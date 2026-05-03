"""学生端 GraphRAG 问答 mixin。"""
from __future__ import annotations

from collections.abc import Sequence

from knowledge.models import KnowledgePoint

from .student_answer_support import (
    build_course_answer_evidence,
    build_course_answer_prompt,
    build_course_graph_focus,
    build_graph_answer_evidence,
    build_graph_answer_prompt,
    build_point_name_map,
    call_llm_answer,
    course_answer_with_llm,
    course_answer_without_llm,
    graph_answer_with_llm,
    graph_answer_without_llm,
    normalize_answer_sources,
    query_graph_bundle,
)
from .student_utils import model_pk


# 维护意图：提供知识点级和课程级 GraphRAG 问答
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class StudentAnswerMixin:
    """提供知识点级和课程级 GraphRAG 问答。"""

    # 维护意图：使用三种 GraphRAG 查询模式回答学生问题
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def answer_graph_question(self, *, course_id: int, point: KnowledgePoint, question: str) -> dict[str, object]:
        """使用三种 GraphRAG 查询模式回答学生问题。"""
        point_pk = model_pk(point)
        context_bundle = self._compose_query_context(course_id, question, {f"kp:{point_pk}"})
        graph_query_bundle = query_graph_bundle(
            self._runtime(),
            course_id=course_id,
            question=question,
            focus_point_id=point_pk,
            focus_point_name=point.name,
            warning_label=f"Graph query 增强失败，回退原三段式 GraphRAG: point={point_pk}",
        )
        sources = normalize_answer_sources(graph_query_bundle, context_bundle, self._merge_sources)
        evidence = build_graph_answer_evidence(
            graph_query_bundle=graph_query_bundle,
            context_bundle=context_bundle,
            sources=sources,
            point=point,
        )

        llm = self._llm_facade()
        if not llm.is_available:
            return graph_answer_without_llm(evidence)

        prompt = build_graph_answer_prompt(
            point=point,
            question=question,
            combined_context=evidence.combined_context,
        )
        result = call_llm_answer(
            llm,
            prompt=prompt,
            call_type="graph_rag_answer",
            fallback_response=evidence.fallback_response,
        )
        return graph_answer_with_llm(llm_result=result, evidence=evidence)

    # 维护意图：在未指定知识点时，使用课程级 GraphRAG 证据回答学生问题
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def answer_course_question(self, *, course_id: int, question: str, seed_point_ids: Sequence[int] = ()) -> dict[str, object]:
        """在未指定知识点时，使用课程级 GraphRAG 证据回答学生问题。"""
        payload = self._ensure_index(course_id)
        point_name_map = build_point_name_map(self._entity_list(payload))
        focus = build_course_graph_focus(seed_point_ids=seed_point_ids, point_name_map=point_name_map)
        context_bundle = self._compose_query_context(course_id, question, focus.seed_entity_ids)
        graph_query_bundle = query_graph_bundle(
            self._runtime(),
            course_id=course_id,
            question=question,
            focus_point_id=focus.focus_point_id,
            focus_point_name=focus.focus_point_name,
            warning_label="课程级 Graph query 失败，回退课程证据上下文",
        )
        sources = normalize_answer_sources(graph_query_bundle, context_bundle, self._merge_sources)
        evidence, candidates = build_course_answer_evidence(
            course_id=course_id,
            graph_query_bundle=graph_query_bundle,
            context_bundle=context_bundle,
            sources=sources,
            focus=focus,
            point_name_map=point_name_map,
        )

        llm = self._llm_facade()
        if not llm.is_available:
            return course_answer_without_llm(evidence, candidates)

        prompt = build_course_answer_prompt(
            question=question,
            candidate_names=candidates.candidate_names,
            combined_context=evidence.combined_context,
        )
        result = call_llm_answer(
            llm,
            prompt=prompt,
            call_type="graph_rag_course_answer",
            fallback_response=evidence.fallback_response,
        )
        return course_answer_with_llm(
            llm_result=result,
            evidence=evidence,
            candidates=candidates,
        )
