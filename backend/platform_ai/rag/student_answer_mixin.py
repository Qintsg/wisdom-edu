"""学生端 GraphRAG 问答 mixin。"""
from __future__ import annotations

import logging
from collections.abc import Sequence

from knowledge.models import KnowledgePoint

from .student_utils import (
    bundle_mode,
    bundle_positive_ints,
    bundle_query_modes,
    bundle_sources,
    dedupe_ints,
    dedupe_strings,
    model_pk,
    sanitize_answer_text,
    to_int,
)


logger = logging.getLogger(__name__)


class StudentAnswerMixin:
    """提供知识点级和课程级 GraphRAG 问答。"""

    def answer_graph_question(self, *, course_id: int, point: KnowledgePoint, question: str) -> dict[str, object]:
        """使用三种 GraphRAG 查询模式回答学生问题。"""
        point_pk = model_pk(point)
        context_bundle = self._compose_query_context(course_id, question, {f"kp:{point_pk}"})
        graph_query_bundle: dict[str, object] = {}
        try:
            graph_query_bundle = self._runtime().query_graph(
                course_id=course_id,
                query=question,
                focus_point_id=point_pk,
                focus_point_name=point.name,
                limit=6,
            )
        except Exception as error:
            logger.warning("Graph query 增强失败，回退原三段式 GraphRAG: course=%s point=%s error=%s", course_id, point_pk, error)
            graph_query_bundle = {}

        combined_context = "\n\n".join(
            section
            for section in [str(graph_query_bundle.get("context", "")).strip(), str(context_bundle.get("context", "")).strip()]
            if section
        )
        sources = self._merge_sources(bundle_sources(graph_query_bundle), bundle_sources(context_bundle))[:8]
        source_titles = dedupe_strings(str(source.get("title", "")).strip() for source in sources)[:4]
        fallback_answer = sanitize_answer_text(
            "\n".join(
                section
                for section in [
                    f"围绕“{point.name}”，当前课程图谱显示：{point.introduction or point.description or point.name}",
                    f"建议优先结合这些证据继续学习：{'、'.join(source_titles)}。" if source_titles else "建议优先查看课程内与该知识点直接关联的资源。",
                    "如果你想追问先修关系、典型题型或资源推荐，也可以继续细化问题。",
                ]
                if section
            )
        )
        fallback = {"answer": fallback_answer, "key_points": dedupe_strings(source_titles)}
        query_modes = bundle_query_modes(graph_query_bundle)
        resolved_mode = bundle_mode(graph_query_bundle, "graph_rag")
        llm = self._llm_facade()
        if not llm.is_available:
            return {"answer": fallback_answer, "sources": sources, "mode": resolved_mode or "graph_rag", "query_modes": query_modes}

        prompt = f"""# 任务
请基于给定 GraphRAG 证据，用中文回答学生问题。

# 学生问题
{question}

# 当前知识点
- 名称：{point.name}
- 章节：{point.chapter or '未分章'}
- 描述：{point.description or ''}

# GraphRAG 上下文
{combined_context}

# JSON输出格式
{{
  "answer": "80-200字回答",
  "key_points": ["要点1", "要点2"]
}}

# 回答约束
1. 只能基于证据回答，不要编造课程外事实。
2. 回答需先直接答题，再补充学习建议。
3. 若证据不足，要明确说“当前证据不足”。
4. 输出必须是合法 JSON。
"""
        result = llm.call_with_fallback(prompt=prompt, call_type="graph_rag_answer", fallback_response=fallback)
        return {
            "answer": sanitize_answer_text(str(result.get("answer", fallback_answer))),
            "sources": sources,
            "mode": resolved_mode or "graph_rag",
            "query_modes": query_modes,
            "key_points": result.get("key_points", fallback.get("key_points", [])),
        }

    def answer_course_question(self, *, course_id: int, question: str, seed_point_ids: Sequence[int] = ()) -> dict[str, object]:
        """在未指定知识点时，使用课程级 GraphRAG 证据回答学生问题。"""
        payload = self._ensure_index(course_id)
        point_name_map: dict[int, str] = {}
        for entity in self._entity_list(payload):
            if str(entity.get("entity_type", "")).strip() != "knowledge_point":
                continue
            metadata = entity.get("metadata")
            point_id = to_int(metadata.get("knowledge_point_id"), default=0) if isinstance(metadata, dict) else 0
            if point_id <= 0:
                entity_id = str(entity.get("id", "")).strip()
                if entity_id.startswith("kp:"):
                    point_id = to_int(entity_id.partition(":")[2], default=0)
            point_name = str(entity.get("title", "")).strip()
            if point_id > 0 and point_name:
                point_name_map[point_id] = point_name

        resolved_seed_ids = [point_id for point_id in seed_point_ids if point_id > 0]
        seed_entity_ids = {f"kp:{point_id}" for point_id in resolved_seed_ids}
        focus_point_id = resolved_seed_ids[0] if resolved_seed_ids else None
        focus_point_name = point_name_map.get(focus_point_id or 0, "")
        context_bundle = self._compose_query_context(course_id, question, seed_entity_ids)
        graph_query_bundle: dict[str, object] = {}
        try:
            graph_query_bundle = self._runtime().query_graph(
                course_id=course_id,
                query=question,
                focus_point_id=focus_point_id,
                focus_point_name=focus_point_name,
                limit=6,
            )
        except Exception as error:
            logger.warning("课程级 Graph query 失败，回退课程证据上下文: course=%s error=%s", course_id, error)
            graph_query_bundle = {}

        combined_context = "\n\n".join(
            section
            for section in [str(graph_query_bundle.get("context", "")).strip(), str(context_bundle.get("context", "")).strip()]
            if section
        )
        sources = self._merge_sources(bundle_sources(graph_query_bundle), bundle_sources(context_bundle))[:8]
        matched_point_ids = dedupe_ints(list(resolved_seed_ids) + bundle_positive_ints(graph_query_bundle, "matched_point_ids"))
        candidate_names = dedupe_strings(point_name_map.get(point_id, "") for point_id in matched_point_ids)
        missing_point_ids = [point_id for point_id in matched_point_ids if point_id not in point_name_map]
        if missing_point_ids:
            candidate_names = dedupe_strings(
                candidate_names
                + list(
                    KnowledgePoint.objects.filter(course_id=course_id, is_published=True, id__in=missing_point_ids)
                    .order_by("order", "id")
                    .values_list("name", flat=True)
                )
            )
        source_titles = dedupe_strings(str(source.get("title", "")).strip() for source in sources)[:5]
        fallback_answer = sanitize_answer_text(
            "\n".join(
                section
                for section in [
                    f"围绕当前课程问题，系统命中了这些候选知识点：{'、'.join(candidate_names[:4])}。" if candidate_names else "系统已结合当前课程知识图谱与课程证据进行回答。",
                    f"可优先查看这些证据：{'、'.join(source_titles[:4])}。" if source_titles else "如果你希望继续深挖，可追问更具体的知识点、先修关系或资源名称。",
                ]
                if section
            )
        )
        fallback = {"answer": fallback_answer, "key_points": dedupe_strings(candidate_names + source_titles)[:5]}
        query_modes = bundle_query_modes(graph_query_bundle)
        resolved_mode = bundle_mode(graph_query_bundle, "graph_rag_course")
        llm = self._llm_facade()
        if not llm.is_available:
            return {
                "answer": fallback_answer,
                "sources": sources,
                "mode": resolved_mode,
                "query_modes": query_modes,
                "key_points": fallback["key_points"],
                "matched_point_ids": matched_point_ids,
            }

        prompt = f"""# 任务
请基于给定课程的 GraphRAG 证据，用中文直接回答学生问题。

# 学生问题
{question}

# 候选知识点
{'、'.join(candidate_names[:6]) if candidate_names else '当前问题未命中唯一知识点，请以课程级证据回答。'}

# GraphRAG 上下文
{combined_context}

# JSON输出格式
{{
  "answer": "80-220字回答",
  "key_points": ["要点1", "要点2"]
}}

# 回答约束
1. 只能基于证据回答，不要编造课程外事实。
2. 先直接回答学生问题，再补充下一步学习建议。
3. 如果证据不足，要明确提示“当前证据不足”。
4. 输出必须是合法 JSON。
"""
        result = llm.call_with_fallback(prompt=prompt, call_type="graph_rag_course_answer", fallback_response=fallback)
        return {
            "answer": sanitize_answer_text(str(result.get("answer", fallback_answer))),
            "sources": sources,
            "mode": resolved_mode,
            "query_modes": query_modes,
            "key_points": result.get("key_points", fallback["key_points"]),
            "matched_point_ids": matched_point_ids,
        }
