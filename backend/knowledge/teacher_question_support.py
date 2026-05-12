"""教师端题库视图的序列化与更新辅助逻辑。"""

from __future__ import annotations

from typing import Any, cast

from application.teacher.contracts import first_present, normalize_question_point_ids
from assessments.models import Question

from .models import KnowledgePoint
from .teacher_helpers import KnowledgePointRelationSetter, replace_knowledge_points


BASIC_UPDATE_FIELDS = ["content", "options", "analysis", "difficulty", "score"]
DETAIL_UPDATE_FIELDS = [
    *BASIC_UPDATE_FIELDS,
    "suggested_score",
    "chapter",
    "is_visible",
    "for_initial_assessment",
]


def question_identifier(question: Question) -> int | None:
    """兼容真实模型与轻量测试对象的题目 ID 读取。"""
    return getattr(question, "id", None) or getattr(question, "pk", None)


def build_question_list_item(question: Question) -> dict[str, Any]:
    """构造题库列表中的单题摘要。"""
    content = question.content[:100] + "..." if len(question.content) > 100 else question.content
    return {
        "question_id": question_identifier(question),
        "content": content,
        "type": question.question_type,
        "difficulty": question.difficulty,
        "points": list(question.knowledge_points.values_list("id", flat=True)),
        "created_at": question.created_at.isoformat(),
    }


def build_question_detail(question: Question) -> dict[str, Any]:
    """构造题目详情响应，保持前端历史字段兼容。"""
    question_points = cast(list[KnowledgePoint], list(question.knowledge_points.all()))
    return {
        "question_id": question_identifier(question),
        "content": question.content,
        "type": question.question_type,
        "question_type": question.question_type,
        "options": question.options,
        "answer": question.answer,
        "analysis": question.analysis,
        "difficulty": question.difficulty,
        "score": float(question.score),
        "suggested_score": float(question.suggested_score) if question.suggested_score else None,
        "chapter": question.chapter,
        "is_visible": question.is_visible,
        "for_initial_assessment": question.for_initial_assessment,
        "points": [{"point_id": point.id, "point_name": point.name} for point in question_points],
        "knowledge_points": [{"id": point.id, "name": point.name} for point in question_points],
        "creator": question.created_by.username if question.created_by else None,
        "created_at": question.created_at.isoformat(),
    }


def apply_question_update_fields(
    question: Question,
    payload,
    *,
    include_detail_fields: bool,
) -> None:
    """按白名单更新题目字段，避免 View 中散落字段分支。"""
    allowed_fields = DETAIL_UPDATE_FIELDS if include_detail_fields else BASIC_UPDATE_FIELDS
    for field in allowed_fields:
        if field in payload:
            setattr(question, field, payload[field])
    if "answer" in payload:
        answer = payload["answer"]
        question.answer = {"answer": answer} if not isinstance(answer, dict) else answer
    if "type" in payload or "question_type" in payload:
        question.question_type = first_present(payload, "type", "question_type")


def replace_question_points_from_payload(
    question: Question,
    payload,
    *,
    filter_course_for_ids: bool = True,
) -> None:
    """按兼容字段替换题目知识点关联。"""
    relation_manager = cast(KnowledgePointRelationSetter, question.knowledge_points)
    if "knowledge_point_ids" in payload:
        if filter_course_for_ids:
            # detail 入口历史上按课程过滤，避免跨课程误绑定。
            knowledge_points = KnowledgePoint.objects.filter(
                id__in=payload["knowledge_point_ids"],
                course=question.course,
            )
            replace_knowledge_points(relation_manager, knowledge_points)
        else:
            replace_knowledge_points(relation_manager, normalize_question_point_ids(payload))
    elif "points" in payload:
        replace_knowledge_points(relation_manager, normalize_question_point_ids(payload))


def has_question_point_payload(payload) -> bool:
    """判断请求是否包含任一知识点关联字段。"""
    return "points" in payload or "knowledge_point_ids" in payload


__all__ = [
    "apply_question_update_fields",
    "build_question_detail",
    "build_question_list_item",
    "has_question_point_payload",
    "question_identifier",
    "replace_question_points_from_payload",
]
