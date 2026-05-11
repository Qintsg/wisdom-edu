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


# 维护意图：构造面向学生端 WebSocket 的纯文本流式回答 prompt
# 边界说明：流式通道不要求 JSON，避免前端逐字展示结构化包裹文本。
# 风险说明：约束需与 GraphRAG 证据边界一致，避免模型把无依据内容包装为事实。
def build_stream_answer_prompt(
    *,
    question: str,
    focus_text: str,
    combined_context: str,
    candidate_names: Sequence[str] = (),
) -> str:
    """构造面向学生端 WebSocket 的纯文本流式回答 prompt。"""
    candidate_text = "、".join(candidate_names[:6]) if candidate_names else "未命中唯一知识点"
    return f"""# 任务
请基于给定 GraphRAG 证据，用中文直接回答学生问题。

# 学生问题
{question}

# 当前上下文
{focus_text}

# 候选知识点
{candidate_text}

# GraphRAG 证据
{combined_context or '当前证据不足。'}

# 回答约束
1. 只能基于证据回答，不要编造课程外事实。
2. 先直接回答学生问题，再给出下一步学习建议。
3. 如果证据不足，要明确提示“当前证据不足”。
4. 不要输出 JSON、代码块或表格。
"""


# 维护意图：提供知识点级和课程级 GraphRAG 问答
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class StudentAnswerMixin:
    """提供知识点级和课程级 GraphRAG 问答。"""

    # 维护意图：准备知识点级 GraphRAG 流式回答所需证据，不直接调用 LLM
    # 边界说明：WebSocket 层只消费 prompt、fallback 与元数据，不接触图谱查询细节。
    # 风险说明：与 answer_graph_question 共用证据构造，改动时需保持 HTTP 与 WS 语义一致。
    def prepare_graph_answer_stream(
        self,
        *,
        course_id: int,
        point: KnowledgePoint,
        question: str,
    ) -> dict[str, object]:
        """准备知识点级 GraphRAG 流式回答所需证据，不直接调用 LLM。"""
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
        prompt = build_stream_answer_prompt(
            question=question,
            focus_text=f"知识点：{point.name}；章节：{point.chapter or '未分章'}",
            combined_context=evidence.combined_context,
            candidate_names=[point.name],
        )
        return {
            "prompt": prompt,
            "call_type": "graph_rag_answer_stream",
            "fallback_payload": graph_answer_without_llm(evidence),
            "candidate_names": [point.name],
        }

    # 维护意图：准备课程级 GraphRAG 流式回答所需证据，不直接调用 LLM
    # 边界说明：保留候选知识点 ID，便于学生端展示命中上下文。
    # 风险说明：结构类问题和未指定知识点问题都依赖此方法的元数据完整性。
    def prepare_course_answer_stream(
        self,
        *,
        course_id: int,
        question: str,
        seed_point_ids: Sequence[int] = (),
    ) -> dict[str, object]:
        """准备课程级 GraphRAG 流式回答所需证据，不直接调用 LLM。"""
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
        prompt = build_stream_answer_prompt(
            question=question,
            focus_text="课程级 GraphRAG 问答",
            combined_context=evidence.combined_context,
            candidate_names=candidates.candidate_names,
        )
        fallback_payload = course_answer_without_llm(evidence, candidates)
        return {
            "prompt": prompt,
            "call_type": "graph_rag_course_answer_stream",
            "fallback_payload": fallback_payload,
            "candidate_names": candidates.candidate_names,
            "matched_point_ids": candidates.matched_point_ids,
        }

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
