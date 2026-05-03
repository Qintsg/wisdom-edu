"""学生端 GraphRAG 排序与 source 构造 mixin。"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from .corpus import tokenize
from .student_utils import humanize_document_title, sanitize_answer_text, to_float, to_int


# 维护意图：实现实体、文档、社区报告的本地排序与 source 标准化
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class StudentRetrievalMixin:
    """实现实体、文档、社区报告的本地排序与 source 标准化。"""

    # 维护意图：提取适合进入上下文窗口的证据片段
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _document_excerpt(self, document: dict[str, object], limit: int = 180) -> str:
        """提取适合进入上下文窗口的证据片段。"""
        content = str(document.get("content", "")).strip()
        metadata = document.get("metadata")
        answer_hidden = bool(metadata.get("answer_hidden", False)) if isinstance(metadata, dict) else False
        if answer_hidden:
            content = content.split("解析：", 1)[0].strip()
        return sanitize_answer_text(content)[:limit]

    # 维护意图：从实体 ID 集合中提取知识点数字 ID
    # 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
    # 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
    def _extract_point_ids(self, entity_ids: Iterable[str]) -> set[int]:
        """从实体 ID 集合中提取知识点数字 ID。"""
        point_ids: set[int] = set()
        for entity_id in entity_ids:
            if not entity_id.startswith("kp:"):
                continue
            _, _, raw_id = entity_id.partition(":")
            if raw_id.isdigit():
                point_ids.add(int(raw_id))
        return point_ids

    # 维护意图：将索引文档转成统一 source 结构
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _source_from_document(self, document: dict[str, object], query_mode: str, limit: int = 140) -> dict[str, object]:
        """将索引文档转成统一 source 结构。"""
        return {
            "id": str(document.get("id", "")).strip(),
            "title": humanize_document_title(document),
            "kind": str(document.get("kind", "")).strip() or "document",
            "url": str(document.get("url", "")).strip(),
            "excerpt": self._document_excerpt(document, limit=limit),
            "query_mode": query_mode,
        }

    # 维护意图：将社区报告转成统一 source 结构
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _source_from_report(self, report: dict[str, object], query_mode: str) -> dict[str, object]:
        """将社区报告转成统一 source 结构。"""
        community_id = str(report.get("community_id", "")).strip()
        summary = sanitize_answer_text(str(report.get("summary", "")))
        return {
            "id": community_id,
            "title": str(report.get("title", "")).strip() or "社区报告",
            "kind": "community_report",
            "url": "",
            "excerpt": summary[:160],
            "query_mode": query_mode,
        }

    # 维护意图：把官方 GraphRAG 检索命中转换为统一 source 结构
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _source_from_graphrag_hit(self, hit, query_mode: str) -> dict[str, object]:
        """把官方 GraphRAG 检索命中转换为统一 source 结构。"""
        return hit.as_source(query_mode)

    # 维护意图：按来源 ID 去重，保留最先出现的证据
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _merge_sources(self, *source_groups: list[dict[str, object]]) -> list[dict[str, object]]:
        """按来源 ID 去重，保留最先出现的证据。"""
        merged: list[dict[str, object]] = []
        seen_ids: set[str] = set()
        for source_group in source_groups:
            for source in source_group:
                source_id = str(source.get("id", "")).strip()
                if not source_id or source_id in seen_ids:
                    continue
                seen_ids.add(source_id)
                merged.append(source)
        return merged

    # 维护意图：计算实体与查询的相关性分数
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _entity_score(self, entity: dict[str, object], query_tokens: set[str], seed_entity_ids: set[str]) -> float:
        """计算实体与查询的相关性分数。"""
        entity_id = str(entity.get("id", "")).strip()
        if not entity_id:
            return -1.0

        metadata = entity.get("metadata")
        searchable_parts: list[str] = [str(entity.get("title", "")).strip(), str(entity.get("summary", "")).strip()]
        if isinstance(metadata, dict):
            for value in metadata.values():
                if isinstance(value, str):
                    searchable_parts.append(value)
                elif isinstance(value, list):
                    searchable_parts.extend(str(item) for item in value)

        searchable_text = " ".join(part for part in searchable_parts if part).lower()
        token_overlap = len(query_tokens & tokenize(searchable_text))
        substring_bonus = sum(1.0 for token in query_tokens if token and token in searchable_text)
        entity_type = str(entity.get("entity_type", "")).strip()
        type_bonus = {"knowledge_point": 1.2, "resource": 1.0, "chapter": 0.6, "question": 0.2}.get(entity_type, 0.0)
        seed_bonus = 12.0 if entity_id in seed_entity_ids else 0.0
        return token_overlap * 3.0 + substring_bonus + type_bonus + seed_bonus

    # 维护意图：对实体进行局部查询排序
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _rank_entities(self, payload: dict[str, object], query: str, seed_entity_ids: Iterable[str] = (), limit: int = 6) -> list[dict[str, object]]:
        """对实体进行局部查询排序。"""
        seed_ids = {entity_id for entity_id in seed_entity_ids if entity_id}
        query_tokens = tokenize(query)
        ranked: list[tuple[float, str, dict[str, object]]] = []
        for entity in self._entity_list(payload):
            score = self._entity_score(entity, query_tokens, seed_ids)
            if score <= 0 and str(entity.get("id", "")) not in seed_ids:
                continue
            ranked.append((score, str(entity.get("title", "")), entity))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [entity for _, _, entity in ranked[:limit]]

    # 维护意图：从关系表中收集一跳邻居实体
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _collect_neighbor_ids(self, payload: dict[str, object], focus_entity_ids: Iterable[str], limit: int = 8) -> list[str]:
        """从关系表中收集一跳邻居实体。"""
        focus_ids = {entity_id for entity_id in focus_entity_ids if entity_id}
        scores: dict[str, float] = defaultdict(float)
        for relationship in self._relationship_list(payload):
            source_id = str(relationship.get("source", "")).strip()
            target_id = str(relationship.get("target", "")).strip()
            weight = to_float(relationship.get("weight", 0.0))
            if source_id in focus_ids and target_id and target_id not in focus_ids:
                scores[target_id] += 1.0 + weight
            elif target_id in focus_ids and source_id and source_id not in focus_ids:
                scores[source_id] += 1.0 + weight
        ordered_ids = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        return [entity_id for entity_id, _ in ordered_ids[:limit]]

    # 维护意图：将关系边转换为适合 prompt 的短句
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _relationship_lines(self, payload: dict[str, object], focus_entity_ids: Iterable[str], limit: int = 8) -> list[str]:
        """将关系边转换为适合 prompt 的短句。"""
        focus_ids = {entity_id for entity_id in focus_entity_ids if entity_id}
        entity_map = self._entity_map(payload)
        relation_lines: list[str] = []
        for relationship in self._relationship_list(payload):
            source_id = str(relationship.get("source", "")).strip()
            target_id = str(relationship.get("target", "")).strip()
            if source_id not in focus_ids and target_id not in focus_ids:
                continue
            source_title = str(entity_map.get(source_id, {}).get("title", source_id)).strip()
            target_title = str(entity_map.get(target_id, {}).get("title", target_id)).strip()
            relation_type = str(relationship.get("relation_type", "相关")).strip() or "相关"
            relation_lines.append(f"{source_title} -[{relation_type}]-> {target_title}")
            if len(relation_lines) >= limit:
                break
        from .student_utils import dedupe_strings
        return dedupe_strings(relation_lines)

    # 维护意图：按 query 与焦点实体综合排序证据文档
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _rank_documents(self, payload: dict[str, object], query: str, focus_entity_ids: Iterable[str] = (), limit: int = 6, include_questions: bool = False) -> list[dict[str, object]]:
        """按 query 与焦点实体综合排序证据文档。"""
        query_tokens = tokenize(query)
        focus_ids = {entity_id for entity_id in focus_entity_ids if entity_id}
        focus_point_ids = self._extract_point_ids(focus_ids)
        ranked_documents: list[tuple[float, str, dict[str, object]]] = []
        for document in self._document_list(payload):
            kind = str(document.get("kind", "")).strip()
            metadata = document.get("metadata")
            if kind == "question" and not include_questions:
                continue
            document_tokens = tokenize(f"{document.get('title', '')} {document.get('content', '')}".lower())
            score = float(len(query_tokens & document_tokens) * 2)
            document_id = str(document.get("id", "")).strip()
            if document_id in focus_ids:
                score += 8.0
            if isinstance(metadata, dict):
                knowledge_point_ids = metadata.get("knowledge_point_ids")
                if isinstance(knowledge_point_ids, list):
                    overlap = {int(item) for item in knowledge_point_ids if str(item).isdigit()} & focus_point_ids
                    score += float(len(overlap) * 3)
                if to_int(metadata.get("knowledge_point_id"), default=-1) in focus_point_ids:
                    score += 3.0
            if score <= 0:
                continue
            ranked_documents.append((score, humanize_document_title(document), document))
        ranked_documents.sort(key=lambda item: (-item[0], item[1]))
        return [document for _, _, document in ranked_documents[:limit]]

    # 维护意图：按查询与实体焦点排序社区报告
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _rank_community_reports(self, payload: dict[str, object], query: str, focus_entity_ids: Iterable[str] = (), limit: int = 4) -> list[dict[str, object]]:
        """按查询与实体焦点排序社区报告。"""
        query_tokens = tokenize(query)
        focus_ids = {entity_id for entity_id in focus_entity_ids if entity_id}
        community_lookup = self._community_lookup(payload)
        ranked_reports: list[tuple[float, str, dict[str, object]]] = []
        for report in self._community_report_list(payload):
            community_id = str(report.get("community_id", "")).strip()
            community = community_lookup.get(community_id, {})
            searchable_parts = [str(report.get("title", "")).strip(), str(report.get("summary", "")).strip()]
            themes = report.get("themes")
            if isinstance(themes, list):
                searchable_parts.extend(str(theme) for theme in themes)
            top_entities = report.get("top_entities")
            if isinstance(top_entities, list):
                searchable_parts.extend(str(item.get("title", "")) for item in top_entities if isinstance(item, dict))
            searchable_text = " ".join(part for part in searchable_parts if part).lower()
            score = float(len(query_tokens & tokenize(searchable_text)) * 4)
            entity_ids = community.get("entity_ids")
            if isinstance(entity_ids, list):
                score += float(len({str(entity_id) for entity_id in entity_ids} & focus_ids) * 4)
            if score <= 0 and not focus_ids:
                continue
            ranked_reports.append((score, str(report.get("title", "")), report))
        ranked_reports.sort(key=lambda ranked_item: (-ranked_item[0], ranked_item[1]))
        return [report for _, _, report in ranked_reports[:limit]]
