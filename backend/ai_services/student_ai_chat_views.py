"""学生端 AI 聊天与 GraphRAG 问答接口。"""

from __future__ import annotations

import logging
from typing import Any

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.logging_utils import build_log_message
from common.responses import error_response, success_response
from platform_ai.llm import llm_facade
from .services.student_graph_rag_service import student_graph_rag_service

logger = logging.getLogger(__name__)


def build_chat_response(
    *,
    user,
    question: str,
    course_id: int | str | None = None,
    point_id: int | str | None = None,
    knowledge_point: str = "",
    course_name: str = "",
) -> dict[str, Any]:
    """统一生成 AI 助手回复，供 HTTP 与 WebSocket 共用。"""
    normalized_question = (question or "").strip()
    if not normalized_question:
        return {"reply": "请输入问题", "sources": [], "mode": "error"}

    if course_id:
        try:
            return student_graph_rag_service.ask(
                user=user,
                course_id=int(course_id),
                question=normalized_question,
                point_id=int(point_id) if point_id else None,
            )
        except Exception as exc:
            logger.error(build_log_message("chat.graph_rag.fail", course_id=course_id, error=exc))
            return {"reply": "服务暂时不可用，请稍后重试。", "sources": [], "mode": "error"}

    fallback = {
        "reply": (
            f"当前问题是“{normalized_question}”。"
            f"{' 你正在学习“' + knowledge_point + '”。' if knowledge_point else ''}"
            f"{' 所属课程为“' + course_name + '”。' if course_name else ''}"
            "当前未提供可定位的课程图谱上下文，我会先给出通用解答，建议在知识图谱或学习路径页面中带上具体知识点继续追问。"
        ),
        "sources": [],
        "mode": "llm_fallback",
    }
    if llm_facade.is_available:
        result = llm_facade.call_with_fallback(
            prompt=(
                "请用中文回答学生的学习问题，保持内容简洁、准确、适合教学场景。"
                f"\n课程：{course_name or '未提供'}"
                f"\n知识点：{knowledge_point or '未提供'}"
                f"\n问题：{normalized_question}"
            ),
            call_type="chat",
            fallback_response=fallback,
        )
        return {"reply": result.get("reply", result.get("answer", "")), "sources": [], "mode": "llm_fallback"}
    return fallback


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    """Course-grounded chat with optional knowledge-point focus."""
    question = (request.data.get("question") or request.data.get("message") or "").strip()
    course_id = request.data.get("course_id")
    point_id = request.data.get("point_id")
    knowledge_point = (request.data.get("knowledge_point") or "").strip()
    course_name = (request.data.get("course_name") or "").strip()
    if not question:
        return error_response(msg="请输入问题", code=400)
    if len(question) > 1000:
        return error_response(msg="问题内容过长，请限制在1000字以内", code=400)

    result = build_chat_response(
        user=request.user,
        question=question,
        course_id=course_id,
        point_id=point_id,
        knowledge_point=knowledge_point,
        course_name=course_name,
    )
    return success_response(data=result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_knowledge_graph_query(request):
    """Dedicated alias for graph-grounded student Q&A."""
    return ai_chat(request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_graph_rag_search(request):
    """Search graph knowledge points under the current course."""
    course_id = request.data.get("course_id")
    query = (request.data.get("query") or request.data.get("keyword") or "").strip()
    limit = int(request.data.get("limit") or 8)
    if not course_id:
        return error_response(msg="缺少课程ID", code=400)
    if not query:
        return error_response(msg="请输入检索内容", code=400)
    result = student_graph_rag_service.search_points(
        user=request.user,
        course_id=int(course_id),
        query=query,
        limit=max(1, min(limit, 20)),
    )
    return success_response(data=result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_graph_rag_ask(request):
    """Ask a graph-grounded question under the current course."""
    course_id = request.data.get("course_id")
    question = (request.data.get("question") or request.data.get("message") or "").strip()
    point_id = request.data.get("point_id")
    if not course_id:
        return error_response(msg="缺少课程ID", code=400)
    if not question:
        return error_response(msg="请输入问题", code=400)
    result = student_graph_rag_service.ask(
        user=request.user,
        course_id=int(course_id),
        question=question,
        point_id=int(point_id) if point_id else None,
    )
    return success_response(data=result)
