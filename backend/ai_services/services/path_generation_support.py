"""学习路径生成辅助工具。"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ai_services.services.path_generation_nodes import (
    PathGenerationPlan,
    attach_resources_to_created_nodes,
    build_generation_plan,
    build_linked_pending_batch,
)


logger = logging.getLogger(__name__)

REMEDIAL_REINSERTION_THRESHOLD = 0.6

if TYPE_CHECKING:
    from courses.models import Course
    from users.models import User


# 维护意图：返回课程内所有已发布知识点 ID
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_course_point_ids(course_id: int) -> list[int]:
    """返回课程内所有已发布知识点 ID。"""
    from knowledge.models import KnowledgePoint

    return list(
        KnowledgePoint.objects.filter(course_id=course_id, is_published=True)
        .order_by("order", "id")
        .values_list("id", flat=True)
    )


# 维护意图：同步课程全量掌握度，保证路径规划覆盖全部知识点
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def sync_course_mastery(
    *,
    user: "User",
    course: "Course",
    course_point_ids: list[int],
) -> dict[int, float]:
    """同步课程全量掌握度，保证路径规划覆盖全部知识点。"""
    from assessments.models import AnswerHistory
    from ai_services.services import kt_service
    from knowledge.models import KnowledgeMastery
    from learning.path_rules import apply_prerequisite_caps

    course_id = course.id
    answer_records = list(
        AnswerHistory.objects.filter(user=user, course_id=course_id)
        .order_by("answered_at")
        .values("question_id", "knowledge_point_id", "is_correct")
    )
    kt_history = [
        {
            "question_id": record["question_id"],
            "knowledge_point_id": record["knowledge_point_id"],
            "correct": 1 if record["is_correct"] else 0,
        }
        for record in answer_records
        if record["knowledge_point_id"]
    ]
    mastery_dict = predict_course_mastery(
        user=user,
        course_id=course_id,
        course_point_ids=course_point_ids,
        kt_history=kt_history,
    )
    existing_mastery = {
        row.knowledge_point_id: float(row.mastery_rate)
        for row in KnowledgeMastery.objects.filter(user=user, course_id=course_id)
    }
    for point_id in course_point_ids:
        if point_id not in mastery_dict:
            mastery_dict[point_id] = existing_mastery.get(point_id, 0.25)

    mastery_dict = apply_prerequisite_caps(
        mastery_dict,
        course_id=course_id,
        buffer=0.05,
    )
    persist_course_mastery(
        user=user,
        course_id=course_id,
        mastery_dict=mastery_dict,
    )
    return mastery_dict


# 维护意图：调用 KT 服务预测课程知识点掌握度
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def predict_course_mastery(
    *,
    user: "User",
    course_id: int,
    course_point_ids: list[int],
    kt_history: list[dict[str, int]],
) -> dict[int, float]:
    """调用 KT 服务预测课程知识点掌握度。"""
    from ai_services.services import kt_service

    if not kt_history:
        return {}
    try:
        kt_result = kt_service.predict_mastery(
            user_id=user.id,
            course_id=course_id,
            answer_history=kt_history,
            knowledge_points=course_point_ids,
        )
        raw_predictions = kt_result.get("predictions") or {}
        mastery_dict = {
            int(point_id): float(value)
            for point_id, value in raw_predictions.items()
        }
        logger.info(
            "KT服务调用成功(路径生成): 用户=%s, 答题历史=%d条, 预测结果=%d条",
            user.id,
            len(kt_history),
            len(mastery_dict),
        )
        return mastery_dict
    except Exception as kt_error:
        logger.error(
            "KT预测失败(路径生成): 用户=%s, 错误=%s",
            user.id,
            kt_error,
        )
        return {}


# 维护意图：持久化本轮课程掌握度预测结果
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def persist_course_mastery(
    *,
    user: "User",
    course_id: int,
    mastery_dict: dict[int, float],
) -> None:
    """持久化本轮课程掌握度预测结果。"""
    from knowledge.models import KnowledgeMastery

    for point_id, mastery_rate in mastery_dict.items():
        KnowledgeMastery.objects.update_or_create(
            user=user,
            course_id=course_id,
            knowledge_point_id=point_id,
            defaults={"mastery_rate": float(mastery_rate)},
        )


__all__ = [
    "PathGenerationPlan",
    "REMEDIAL_REINSERTION_THRESHOLD",
    "attach_resources_to_created_nodes",
    "build_generation_plan",
    "build_linked_pending_batch",
    "load_course_point_ids",
    "sync_course_mastery",
]
