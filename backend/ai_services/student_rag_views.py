"""学生主链路的 RAG 视图。"""

from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.responses import error_response, success_response
from .student_rag_support import (
    build_node_intro_payload,
    build_path_constraints,
    cache_node_intro,
    cached_node_intro,
    demo_intro_payload,
    node_intro_cache_key,
    plan_student_path,
    resolve_course,
    resolve_intro_point,
)


# 维护意图：Generate a personalized path proposal using mastery and RAG evidence
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_path_planning(request: Request) -> Response:
    """Generate a personalized path proposal using mastery and RAG evidence."""
    course_id = request.data.get("course_id")
    if not course_id:
        return error_response(msg="缺少课程ID", code=400)

    course = resolve_course(course_id)
    if course is None:
        return error_response(msg="课程不存在", code=404)

    payload, error = plan_student_path(
        user=request.user,
        course=course,
        course_id=course_id,
        target=request.data.get("target", ""),
        constraints=build_path_constraints(
            request.user,
            course_id,
            request.data.get("constraints", {}),
        ),
    )
    if error:
        return error_response(msg=error, code=500)
    return success_response(data=payload, msg="路径规划完成")


# 维护意图：Explain a knowledge point with cached graph-backed and corpus-backed content
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_node_intro(request: Request) -> Response:
    """Explain a knowledge point with cached graph-backed and corpus-backed content."""
    course_id = request.data.get("course_id")
    point_id = request.data.get("point_id")
    point_name = (request.data.get("point_name") or "").strip()
    if not course_id:
        return error_response(msg="缺少课程ID", code=400)
    if not point_name and not point_id:
        return error_response(msg="缺少知识点名称或 point_id", code=400)

    point = resolve_intro_point(course_id=course_id, point_id=point_id, point_name=point_name)
    if point is None:
        return error_response(msg="知识点不存在", code=404)

    preset_payload = demo_intro_payload(request.user, point)
    if preset_payload:
        return success_response(data=preset_payload)

    resolved_point_name = point.name
    cache_key = node_intro_cache_key(
        user_id=request.user.id,
        course_id=course_id,
        point_id=point.id,
        point_name=resolved_point_name,
    )
    cached = cached_node_intro(cache_key)
    if cached:
        return success_response(data=cached)

    payload, cacheable = build_node_intro_payload(
        user=request.user,
        course_id=course_id,
        point=point,
        course_name=request.data.get("course_name", "") or point.course.name,
        point_name=resolved_point_name,
    )
    if cacheable:
        cache_node_intro(cache_key, payload)
    return success_response(data=payload)
