"""学生主链路的 RAG 视图。"""

from __future__ import annotations

import logging

from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from assessments.models import AbilityScore
from common.defense_demo import get_defense_demo_intro_payload, is_defense_demo_student
from common.logging_utils import build_log_message
from common.responses import error_response, success_response
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint
from knowledge.services import get_or_generate_point_intro
from platform_ai.rag import student_learning_rag

from .models import LLMCallLog

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_path_planning(request):
    """Generate a personalized path proposal using mastery and RAG evidence."""
    course_id = request.data.get("course_id")
    target = request.data.get("target", "")
    constraints = request.data.get("constraints", {})
    if not course_id:
        return error_response(msg="缺少课程ID", code=400)

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)

    user = request.user
    mastery_records = KnowledgeMastery.objects.filter(
        user=user,
        course_id=course_id,
    ).select_related("knowledge_point")
    mastery_data = [
        {
            "point_id": record.knowledge_point_id,
            "point_name": record.knowledge_point.name,
            "mastery_rate": float(record.mastery_rate),
        }
        for record in mastery_records
        if record.knowledge_point_id
    ]

    ability = AbilityScore.objects.filter(user=user, course_id=course_id).first()
    if ability:
        # Keep caller constraints intact while attaching teacher-generated ability
        # scores as additional planning signals.
        constraints = dict(constraints or {})
        constraints["ability_scores"] = ability.scores

    # 规划服务异常时返回降级响应，避免接口直接失败。
    try:
        result = student_learning_rag.plan_learning_path(
            course=course,
            mastery_data=mastery_data,
            target=target,
            constraints=constraints,
            max_nodes=constraints.get("max_nodes", 6)
            if isinstance(constraints, dict)
            else 6,
        )
    except Exception as exc:
        logger.error(
            build_log_message(
                "rag.path_planning.fail", user_id=user.id,
                course_id=course_id, error=exc,
            )
        )
        return error_response(msg="路径规划服务暂时不可用", code=500)

    LLMCallLog.objects.create(
        user=user,
        call_type="path_planning",
        input_summary=f"course={course_id}, target={target or 'default'}, mastery_points={len(mastery_data)}",
        output_summary=str(result)[:500],
        is_success=True,
    )
    return success_response(
        data={
            "reason": result.get("reason", ""),
            "suggested_nodes": result.get("nodes", []),
        },
        msg="路径规划完成",
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_node_intro(request):
    """Explain a knowledge point with cached graph-backed and corpus-backed content."""
    point_name = (request.data.get("point_name") or "").strip()
    point_id = request.data.get("point_id")
    course_name = request.data.get("course_name", "")
    course_id = request.data.get("course_id")

    if not course_id:
        return error_response(msg="缺少课程ID", code=400)

    if not point_name and not point_id:
        return error_response(msg="缺少知识点名称或 point_id", code=400)

    point_queryset = KnowledgePoint.objects.select_related("course").filter(
        course_id=course_id
    )
    if point_id:
        point = point_queryset.filter(id=point_id).first()
    else:
        point = point_queryset.filter(name=point_name).order_by("order", "id").first()
    if not point:
        return error_response(msg="知识点不存在", code=404)

    course_name = course_name or point.course.name
    point_name = point.name
    point_id = point.id

    # DEFENSE_DEMO_PRESET: 答辩演示节点介绍直接读取课程配置中的固定内容，
    # 这样可以保留真实页面的等待动画，但不会被现场 LLM 波动影响。
    preset_payload = get_defense_demo_intro_payload(point.course, point_id)
    if preset_payload and is_defense_demo_student(request.user, point.course):
        return success_response(data=preset_payload)

    # Cache at user scope so repeated visits reuse the same composed answer
    # without mixing course-specific explanations across students.
    cache_key = f"rag_node_intro:{request.user.id}:{course_id}:{point_id or point_name}"
    cached = cache.get(cache_key)
    if cached:
        return success_response(data=cached)

    # 异常保护块
    try:
        intro_payload = get_or_generate_point_intro(point)
        result = student_learning_rag.explain_knowledge_point(
            course_id=int(course_id),
            point_name=point_name,
            point_id=int(point_id) if point_id else None,
            question=f"{course_name} 课程中，{point_name} 是什么？与哪些知识相关？该如何学习？",
        )
        result["introduction"] = (
            result.get("introduction") or intro_payload["introduction"]
        )
        result["key_concepts"] = (
            result.get("key_concepts") or intro_payload["key_concepts"]
        )
        result["learning_tips"] = (
            result.get("learning_tips") or intro_payload["learning_tips"]
        )
        result["difficulty"] = result.get("difficulty") or intro_payload["difficulty"]
        result["sources"] = result.get("sources") or intro_payload["sources"]
        cache.set(cache_key, result, 3600)
        return success_response(data=result)
    except Exception as exc:
        # The local intro generator is the safe degradation path because it uses
        # persisted course data instead of returning an opaque LLM failure.
        logger.error(
            build_log_message(
                "rag.node_intro.fail",
                user_id=request.user.id,
                course_id=course_id,
                point_name=point_name,
                error=exc,
            )
        )
        return success_response(data=get_or_generate_point_intro(point))
