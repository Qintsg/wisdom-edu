"""学生端 GraphRAG local/global/drift 上下文组合 mixin。"""
from __future__ import annotations

import logging
from collections.abc import Iterable

from .student_utils import RankedContext, dedupe_strings, sanitize_answer_text


logger = logging.getLogger(__name__)


# 维护意图：组合多种 GraphRAG 查询模式的上下文与证据来源
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class StudentContextMixin:
    """组合多种 GraphRAG 查询模式的上下文与证据来源。"""

    # 维护意图：实现 GraphRAG Local Search
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    def _build_local_context(
        self,
        course_id: int,
        query: str,
        seed_entity_ids: Iterable[str] = (),
        include_questions: bool = False,
    ) -> RankedContext:
        """实现 GraphRAG Local Search。"""
        payload = self._ensure_index(course_id)
        seed_ids = {entity_id for entity_id in seed_entity_ids if entity_id}
        hybrid_hits = []
        try:
            hybrid_hits = self._runtime().search_documents(
                course_id=course_id,
                query=query,
                limit=6,
                seed_point_ids=sorted(self._extract_point_ids(seed_ids)),
            )
        except Exception as error:
            logger.warning("课程 GraphRAG 混合检索失败，回退本地图排序: course=%s error=%s", course_id, error)

        hybrid_entity_ids = {f"kp:{point_id}" for hit in hybrid_hits for point_id in hit.point_ids}
        ranked_entities = self._rank_entities(payload, query, seed_ids | hybrid_entity_ids, limit=5)
        ranked_entity_ids = [str(entity.get("id", "")).strip() for entity in ranked_entities]
        focus_ids = seed_ids | hybrid_entity_ids | set(ranked_entity_ids)
        focus_ids.update(self._collect_neighbor_ids(payload, focus_ids, limit=6))

        entity_map = self._entity_map(payload)
        focus_titles = [str(entity_map[entity_id].get("title", entity_id)).strip() for entity_id in focus_ids if entity_id in entity_map]
        relation_lines = self._relationship_lines(payload, focus_ids)
        documents = self._rank_documents(payload, query, focus_ids, limit=5, include_questions=include_questions)
        reports = self._rank_community_reports(payload, query, focus_ids, limit=2)

        context_lines: list[str] = []
        if focus_titles:
            context_lines.append(f"命中实体：{'、'.join(dedupe_strings(focus_titles)[:6])}")
        if relation_lines:
            context_lines.append("关键关系：\n- " + "\n- ".join(relation_lines[:6]))
        if reports:
            report_summaries = [sanitize_answer_text(str(report.get("summary", ""))) for report in reports if str(report.get("summary", "")).strip()]
            if report_summaries:
                context_lines.append("社区洞察：\n- " + "\n- ".join(report_summaries[:2]))
        if hybrid_hits:
            hybrid_lines = [f"{hit.title}：{hit.excerpt}" for hit in hybrid_hits if hit.excerpt]
            if hybrid_lines:
                context_lines.append("向量证据：\n- " + "\n- ".join(hybrid_lines[:5]))
        if documents:
            evidence_lines = [
                f"{self._humanize_document_title(document)}：{self._document_excerpt(document, limit=120)}"
                for document in documents
                if self._document_excerpt(document, limit=120)
            ]
            if evidence_lines:
                context_lines.append("局部证据：\n- " + "\n- ".join(evidence_lines[:5]))

        sources = self._merge_sources(
            [self._source_from_graphrag_hit(hit, "local") for hit in hybrid_hits],
            [self._source_from_document(document, "local") for document in documents],
            [self._source_from_report(report, "local") for report in reports],
        )
        return RankedContext(context="\n".join(context_lines), sources=sources, matched_entity_ids=[entity_id for entity_id in focus_ids if entity_id])

    # 维护意图：实现 GraphRAG Global Search
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    def _build_global_context(self, course_id: int, query: str) -> RankedContext:
        """实现 GraphRAG Global Search。"""
        payload = self._ensure_index(course_id)
        reports = self._rank_community_reports(payload, query, (), limit=4)
        if not reports:
            return RankedContext(context="", sources=[], matched_entity_ids=[])

        context_lines: list[str] = ["高层主题概览："]
        community_ids: list[str] = []
        for report in reports:
            title = str(report.get("title", "")).strip() or "社区报告"
            summary = sanitize_answer_text(str(report.get("summary", "")))
            context_lines.append(f"- {title}：{summary}")
            community_id = str(report.get("community_id", "")).strip()
            if community_id:
                community_ids.append(community_id)

        return RankedContext(
            context="\n".join(context_lines),
            sources=[self._source_from_report(report, "global") for report in reports],
            matched_entity_ids=community_ids,
        )

    # 维护意图：实现 GraphRAG DRIFT Search
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    def _build_drift_context(self, course_id: int, query: str, seed_entity_ids: Iterable[str] = ()) -> RankedContext:
        """实现 GraphRAG DRIFT Search。"""
        payload = self._ensure_index(course_id)
        local_context = self._build_local_context(course_id, query, seed_entity_ids)
        if not local_context.matched_entity_ids:
            return RankedContext(context="", sources=[], matched_entity_ids=[])

        entity_to_communities = self._entity_to_communities(payload)
        community_lookup = self._community_lookup(payload)
        related_community_ids: set[str] = set()
        for entity_id in local_context.matched_entity_ids:
            related_community_ids.update(entity_to_communities.get(entity_id, []))

        expanded_entity_ids: set[str] = set(local_context.matched_entity_ids)
        expanded_reports: list[dict[str, object]] = []
        for community_id in related_community_ids:
            community = community_lookup.get(community_id, {})
            entity_ids = community.get("entity_ids")
            if isinstance(entity_ids, list):
                expanded_entity_ids.update(str(entity_id) for entity_id in entity_ids)
            for report in self._community_report_list(payload):
                if str(report.get("community_id", "")).strip() == community_id:
                    expanded_reports.append(report)
                    break

        entity_map = self._entity_map(payload)
        expanded_titles = [str(entity_map[entity_id].get("title", entity_id)).strip() for entity_id in expanded_entity_ids if entity_id in entity_map]
        documents = self._rank_documents(payload, query, expanded_entity_ids, limit=5)

        context_lines: list[str] = []
        if expanded_titles:
            context_lines.append("扩展实体：" + "、".join(dedupe_strings(expanded_titles)[:8]))
        if expanded_reports:
            report_summaries = [sanitize_answer_text(str(report.get("summary", ""))) for report in expanded_reports if str(report.get("summary", "")).strip()]
            if report_summaries:
                context_lines.append("社区延展：\n- " + "\n- ".join(report_summaries[:2]))
        if documents:
            drift_lines = [
                f"{self._humanize_document_title(document)}：{self._document_excerpt(document, limit=110)}"
                for document in documents
                if self._document_excerpt(document, limit=110)
            ]
            if drift_lines:
                context_lines.append("扩展事实：\n- " + "\n- ".join(drift_lines[:5]))

        sources = self._merge_sources(
            [self._source_from_document(document, "drift") for document in documents],
            [self._source_from_report(report, "drift") for report in expanded_reports],
        )
        return RankedContext(context="\n".join(context_lines), sources=sources, matched_entity_ids=sorted(expanded_entity_ids))

    # 维护意图：组合 local / global / drift 三类上下文
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _compose_query_context(
        self,
        course_id: int,
        query: str,
        seed_entity_ids: Iterable[str] = (),
        include_questions: bool = False,
    ) -> dict[str, object]:
        """组合 local / global / drift 三类上下文。"""
        local_context = self._build_local_context(course_id, query, seed_entity_ids, include_questions=include_questions)
        global_context = self._build_global_context(course_id, query)
        drift_context = self._build_drift_context(course_id, query, seed_entity_ids)

        context_sections: list[str] = []
        if local_context.context:
            context_sections.append(f"[Local Search]\n{local_context.context}")
        if global_context.context:
            context_sections.append(f"[Global Search]\n{global_context.context}")
        if drift_context.context:
            context_sections.append(f"[DRIFT Search]\n{drift_context.context}")

        merged_sources = self._merge_sources(local_context.sources, global_context.sources, drift_context.sources)
        matched_entity_ids = dedupe_strings(
            list(local_context.matched_entity_ids) + list(global_context.matched_entity_ids) + list(drift_context.matched_entity_ids)
        )
        return {"context": "\n\n".join(section for section in context_sections if section), "sources": merged_sources, "matched_entity_ids": matched_entity_ids}

    # 维护意图：保留旧方法调用形式，委托给共享工具
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _humanize_document_title(self, document: dict[str, object]) -> str:
        """保留旧方法调用形式，委托给共享工具。"""
        from .student_utils import humanize_document_title
        return humanize_document_title(document)
