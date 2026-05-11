"""学生端 AI 助手流式问答编排服务。"""

from __future__ import annotations

import logging
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass

from common.logging_utils import build_log_message

from platform_ai.llm import llm_facade
from platform_ai.rag import student_learning_rag

from .student_graph_rag_support import (
    build_graph_answer_payload,
    has_course_rag_result,
    is_graph_structure_question,
    match_points_by_query_text,
    point_from_explicit_id,
    point_from_search,
    resolve_point_from_ids,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class StudentAIStreamPlan:
    """学生端 AI 流式回答计划。"""

    prompt: str
    call_type: str
    fallback_reply: str
    metadata: dict[str, object]


# 维护意图：为没有可用课程图谱证据的场景构造通用流式回答计划
# 边界说明：不触发完整 LLM 调用，仅准备 prompt 与降级文本。
# 风险说明：该路径缺少 GraphRAG 证据，回答必须明确上下文限制。
def build_generic_stream_plan(
    *,
    question: str,
    course_id: int | None = None,
    knowledge_point: str = "",
    course_name: str = "",
    error_message: str = "",
    history: Sequence[Mapping[str, object]] | None = None,
) -> StudentAIStreamPlan:
    """为没有可用课程图谱证据的场景构造通用流式回答计划。"""
    fallback_reply = error_message or (
        f"当前问题是“{question}”。系统暂未在当前课程知识图谱中命中明确证据，"
        "我会先给出通用学习建议；建议继续补充课程、知识点或具体例题后追问。"
    )
    context_lines = [
        f"课程ID：{course_id or '未提供'}",
        f"课程名称：{course_name or '未提供'}",
        f"知识点：{knowledge_point or '未提供'}",
    ]
    history_context = _format_history_context(history)
    prompt = "\n".join(
        [
            "# 任务",
            "请用中文回答学生的学习问题。若缺少课程图谱证据，请明确说明上下文限制。",
            "",
            "# 学生问题",
            question,
            "",
            "# 上下文",
            *context_lines,
            "",
            "# 最近对话",
            history_context or "无",
            "",
            "# 回答约束",
            "1. 先直接回答，再给出下一步学习建议。",
            "2. 不要把没有证据的判断包装成事实。",
            "3. 不要输出 JSON。",
        ]
    )
    metadata = {
        "reply": fallback_reply,
        "sources": [],
        "mode": "llm_fallback" if not error_message else "error",
        "query_modes": [],
        "key_points": [],
        "matched_point": None,
        "related_points": {"prerequisites": [], "postrequisites": []},
    }
    return StudentAIStreamPlan(
        prompt=prompt,
        call_type="chat",
        fallback_reply=fallback_reply,
        metadata=metadata,
    )


# 维护意图：构造带课程 GraphRAG 证据的流式回答计划
# 边界说明：证据准备仍为同步数据库/图谱流程，最终答案生成交给 LLM 流式入口。
# 风险说明：如果证据准备失败，上层需回退到普通完整回答链路。
def build_course_stream_plan(
    *,
    user,
    course_id: int,
    question: str,
    point_id: int | None = None,
    history: Sequence[Mapping[str, object]] | None = None,
) -> StudentAIStreamPlan:
    """构造带课程 GraphRAG 证据的流式回答计划。"""
    matched_point = point_from_explicit_id(course_id=course_id, point_id=point_id)

    if matched_point is None:
        explicit_points = match_points_by_query_text(course_id=course_id, query=question, limit=3)
        if len(explicit_points) >= 2 or is_graph_structure_question(question):
            seed_point_ids = [int(point.id) for point in explicit_points]
            course_plan = student_learning_rag.prepare_course_answer_stream(
                course_id=course_id,
                question=question,
                seed_point_ids=seed_point_ids,
            )
            matched_point = explicit_points[0] if explicit_points else resolve_point_from_ids(
                course_id=course_id,
                point_ids=_extract_int_list(course_plan.get("matched_point_ids")),
            )
            return _attach_history_context(_build_plan_from_rag_result(
                user=user,
                matched_point=matched_point,
                raw_plan=course_plan,
            ), history)
        matched_point = explicit_points[0] if explicit_points else None

    if matched_point is None:
        matched_point = point_from_search(user=user, course_id=course_id, question=question)

    if matched_point is not None:
        point_plan = student_learning_rag.prepare_graph_answer_stream(
            course_id=course_id,
            point=matched_point,
            question=question,
        )
        return _attach_history_context(_build_plan_from_rag_result(
            user=user,
            matched_point=matched_point,
            raw_plan=point_plan,
        ), history)

    course_plan = student_learning_rag.prepare_course_answer_stream(
        course_id=course_id,
        question=question,
        seed_point_ids=(),
    )
    fallback_payload = _payload_mapping(course_plan.get("fallback_payload"))
    if not has_course_rag_result(fallback_payload):
        return build_generic_stream_plan(question=question, course_id=course_id, history=history)

    matched_point = resolve_point_from_ids(
        course_id=course_id,
        point_ids=_extract_int_list(course_plan.get("matched_point_ids")),
    )
    return _attach_history_context(_build_plan_from_rag_result(
        user=user,
        matched_point=matched_point,
        raw_plan=course_plan,
    ), history)


# 维护意图：构造学生端 AI 助手统一流式回答计划
# 边界说明：保留无 course_id 的旧聊天场景，前端可统一走 WebSocket。
# 风险说明：调整入参兼容字段时，需要同步 HTTP 与 WS 调用方。
def build_student_ai_stream_plan(
    *,
    user,
    question: str,
    course_id: int | str | None = None,
    point_id: int | str | None = None,
    knowledge_point: str = "",
    course_name: str = "",
    history: Sequence[Mapping[str, object]] | None = None,
) -> StudentAIStreamPlan:
    """构造学生端 AI 助手统一流式回答计划。"""
    normalized_question = question.strip()
    if not normalized_question:
        return build_generic_stream_plan(
            question="请输入问题",
            error_message="请输入问题",
            history=history,
        )

    normalized_course_id = _coerce_optional_int(course_id)
    if normalized_course_id is None:
        return build_generic_stream_plan(
            question=normalized_question,
            knowledge_point=knowledge_point,
            course_name=course_name,
            history=history,
        )

    return build_course_stream_plan(
        user=user,
        course_id=normalized_course_id,
        question=normalized_question,
        point_id=_coerce_optional_int(point_id),
        history=history,
    )


# 维护意图：执行 LLM 文本流式生成
# 边界说明：这里不输出 fallback，调用方在没有真实 chunk 时统一回退。
# 风险说明：保持生成器懒执行，避免 WebSocket 层拿不到首个 token 前被阻塞为完整响应。
def iter_student_ai_stream_chunks(plan: StudentAIStreamPlan) -> Iterator[str]:
    """执行 LLM 文本流式生成。"""
    if not llm_facade.is_available:
        yield from ()
        return
    try:
        yield from llm_facade.stream_text_with_fallback(
            prompt=plan.prompt,
            call_type=plan.call_type,
            fallback_text="",
        )
    except Exception as error:  # noqa: BLE001
        logger.error(build_log_message("student_ai.stream.init_fail", error=error))


# 维护意图：合成 WebSocket done 事件载荷
# 边界说明：保留旧元数据字段，并新增 reply / streamed。
# 风险说明：前端依赖 reply 作为最终完整内容时，必须与 chunk 累积结果一致。
def build_stream_done_payload(
    *,
    plan: StudentAIStreamPlan,
    reply: str,
    streamed: bool,
) -> dict[str, object]:
    """合成 WebSocket done 事件载荷。"""
    payload = dict(plan.metadata)
    payload["reply"] = reply or plan.fallback_reply
    payload["streamed"] = streamed
    return payload


def _build_plan_from_rag_result(
    *,
    user,
    matched_point,
    raw_plan: Mapping[str, object],
) -> StudentAIStreamPlan:
    """将 GraphRAG 证据计划转换为学生端流式计划。"""
    fallback_payload = _payload_mapping(raw_plan.get("fallback_payload"))
    metadata = build_graph_answer_payload(
        user=user,
        matched_point=matched_point,
        rag_result=dict(fallback_payload),
    )
    fallback_reply = str(metadata.get("reply", "")).strip() or "当前证据不足，请补充更具体的问题后重试。"
    return StudentAIStreamPlan(
        prompt=str(raw_plan.get("prompt", "")).strip(),
        call_type=str(raw_plan.get("call_type", "graph_rag_answer_stream")).strip(),
        fallback_reply=fallback_reply,
        metadata=metadata,
    )


def _coerce_optional_int(value: int | str | None) -> int | None:
    """将可选 ID 规整为正整数。"""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    value_text = str(value).strip()
    return int(value_text) if value_text.isdigit() and int(value_text) > 0 else None


def _payload_mapping(value: object) -> Mapping[str, object]:
    """将未知载荷收敛为只读映射。"""
    return value if isinstance(value, Mapping) else {}


def _extract_int_list(value: object) -> list[int]:
    """从未知列表中提取正整数。"""
    if not isinstance(value, list):
        return []
    normalized_values: list[int] = []
    for item in value:
        normalized_item = _coerce_optional_int(item)
        if normalized_item is not None:
            normalized_values.append(normalized_item)
    return normalized_values


def _format_history_context(history: Sequence[Mapping[str, object]] | None) -> str:
    """将最近对话压缩为 prompt 可用的短上下文。"""
    if not history:
        return ""
    formatted_lines: list[str] = []
    for item in history[-8:]:
        if not isinstance(item, Mapping):
            continue
        role_text = str(item.get("role") or "").strip()
        content_text = str(item.get("content") or "").strip()
        if not content_text:
            continue
        role_label = "学生" if role_text == "user" else "助手"
        formatted_lines.append(f"{role_label}：{content_text[:240]}")
    return "\n".join(formatted_lines)


def _attach_history_context(
    plan: StudentAIStreamPlan,
    history: Sequence[Mapping[str, object]] | None,
) -> StudentAIStreamPlan:
    """将最近对话补入 GraphRAG 流式 prompt。"""
    history_context = _format_history_context(history)
    if not history_context:
        return plan
    prompt = "\n".join(
        [
            plan.prompt,
            "",
            "# 最近对话",
            history_context,
            "",
            "回答时优先解决最新问题，必要时结合最近对话消解指代。",
        ]
    )
    return StudentAIStreamPlan(
        prompt=prompt,
        call_type=plan.call_type,
        fallback_reply=plan.fallback_reply,
        metadata=plan.metadata,
    )
