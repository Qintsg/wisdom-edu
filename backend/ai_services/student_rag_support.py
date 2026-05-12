"""学生主链路 RAG 视图支持逻辑。"""

from __future__ import annotations

import logging

from django.core.cache import cache

from assessments.models import AbilityScore
from common.defense_demo import get_defense_demo_intro_payload, is_defense_demo_student
from common.logging_utils import build_log_message
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint
from knowledge.services import get_or_generate_point_intro
from platform_ai.rag import student_learning_rag

from .models import LLMCallLog


logger = logging.getLogger(__name__)


def resolve_course(course_id: object) -> Course | None:
    """按 ID 读取课程。"""
    try:
        return Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return None


def build_mastery_data(user, course_id: object) -> list[dict[str, object]]:
    """读取路径规划所需的知识点掌握度。"""
    mastery_records = KnowledgeMastery.objects.filter(
        user=user,
        course_id=course_id,
    ).select_related("knowledge_point")
    return [
        {
            "point_id": record.knowledge_point_id,
            "point_name": record.knowledge_point.name,
            "mastery_rate": float(record.mastery_rate),
        }
        for record in mastery_records
        if record.knowledge_point_id
    ]


def build_path_constraints(user, course_id: object, raw_constraints: object) -> dict[str, object]:
    """合并前端约束和课程能力评分。"""
    constraints = dict(raw_constraints or {}) if isinstance(raw_constraints, dict) else {}
    ability = AbilityScore.objects.filter(user=user, course_id=course_id).first()
    if ability:
        constraints["ability_scores"] = ability.scores
    return constraints


def plan_student_path(
    *,
    user,
    course: Course,
    course_id: object,
    target: object,
    constraints: dict[str, object],
) -> tuple[dict[str, object] | None, str | None]:
    """调用学生 GraphRAG 路径规划，失败时返回错误信息。"""
    mastery_data = build_mastery_data(user, course_id)
    try:
        result = student_learning_rag.plan_learning_path(
            course=course,
            mastery_data=mastery_data,
            target=target,
            constraints=constraints,
            max_nodes=constraints.get("max_nodes", 6),
        )
    except Exception as exc:
        logger.error(
            build_log_message(
                "rag.path_planning.fail",
                user_id=user.id,
                course_id=course_id,
                error=exc,
            )
        )
        return None, "路径规划服务暂时不可用"

    log_path_planning_call(
        user=user,
        course_id=course_id,
        target=target,
        mastery_count=len(mastery_data),
        result=result,
    )
    return {
        "reason": result.get("reason", ""),
        "suggested_nodes": result.get("nodes", []),
    }, None


def log_path_planning_call(
    *,
    user,
    course_id: object,
    target: object,
    mastery_count: int,
    result: dict[str, object],
) -> None:
    """记录路径规划 LLM 调用摘要。"""
    LLMCallLog.objects.create(
        user=user,
        call_type="path_planning",
        input_summary=f"course={course_id}, target={target or 'default'}, mastery_points={mastery_count}",
        output_summary=str(result)[:500],
        is_success=True,
    )


def resolve_intro_point(*, course_id: object, point_id: object, point_name: str) -> KnowledgePoint | None:
    """按 point_id 或名称解析课程知识点。"""
    point_queryset = KnowledgePoint.objects.select_related("course").filter(course_id=course_id)
    if point_id:
        return point_queryset.filter(id=point_id).first()
    return point_queryset.filter(name=point_name).order_by("order", "id").first()


def demo_intro_payload(user, point: KnowledgePoint) -> dict[str, object] | None:
    """读取答辩演示固定知识点介绍。"""
    preset_payload = get_defense_demo_intro_payload(point.course, point.id)
    if preset_payload and is_defense_demo_student(user, point.course):
        return preset_payload
    return None


def node_intro_cache_key(*, user_id: int, course_id: object, point_id: object, point_name: str) -> str:
    """构造学生级知识点介绍缓存键。"""
    return f"rag_node_intro:{user_id}:{course_id}:{point_id or point_name}"


def cached_node_intro(cache_key: str) -> dict[str, object] | None:
    """读取缓存中的知识点介绍。"""
    cached = cache.get(cache_key)
    return cached if isinstance(cached, dict) else None


def build_node_intro_payload(
    *,
    user,
    course_id: object,
    point: KnowledgePoint,
    course_name: str,
    point_name: str,
) -> tuple[dict[str, object], bool]:
    """生成知识点介绍，RAG 失败时回退本地介绍。"""
    try:
        intro_payload = get_or_generate_point_intro(point)
        result = student_learning_rag.explain_knowledge_point(
            course_id=int(course_id),
            point_name=point_name,
            point_id=int(point.id),
            question=f"{course_name} 课程中，{point_name} 是什么？与哪些知识相关？该如何学习？",
        )
        return merge_intro_payload(result, intro_payload), True
    except Exception as exc:
        logger.error(
            build_log_message(
                "rag.node_intro.fail",
                user_id=user.id,
                course_id=course_id,
                point_name=point_name,
                error=exc,
            )
        )
        return get_or_generate_point_intro(point), False


def merge_intro_payload(
    result: dict[str, object],
    intro_payload: dict[str, object],
) -> dict[str, object]:
    """用本地介绍补齐 GraphRAG 结果缺失字段。"""
    for field_name in ["introduction", "key_concepts", "learning_tips", "difficulty", "sources"]:
        result[field_name] = result.get(field_name) or intro_payload[field_name]
    return result


def cache_node_intro(cache_key: str, payload: dict[str, object]) -> None:
    """缓存知识点介绍一小时。"""
    cache.set(cache_key, payload, 3600)
