#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 在线运行时数据源加载。"""

from __future__ import annotations

from ai_services.services.mefkt_runtime_types import RuntimeFeatureSources, RuntimeSourceData


def load_runtime_source_data(course_id: int) -> RuntimeSourceData:
    """加载课程题目、资源、关系和答题统计。"""
    from assessments.models import AnswerHistory, Question
    from knowledge.models import KnowledgeRelation, Resource

    questions = list(
        Question.objects.filter(course_id=course_id, is_visible=True)
        .prefetch_related("knowledge_points")
        .order_by("id")
    )
    resources = list(
        Resource.objects.filter(course_id=course_id, is_visible=True)
        .prefetch_related("knowledge_points")
    )

    point_to_resources = collect_point_resource_map(resources)
    prereq_points, dependent_points, related_points = collect_knowledge_relation_maps(course_id)
    answer_stats = collect_question_answer_stats(course_id)
    return RuntimeSourceData(
        questions=questions,
        resources=resources,
        point_to_resources=point_to_resources,
        prereq_points=prereq_points,
        dependent_points=dependent_points,
        related_points=related_points,
        answer_stats=answer_stats,
    )


def collect_point_resource_map(resources: list[object]) -> dict[int, set[int]]:
    """按知识点聚合可见资源，避免后续逐题循环查库。"""
    point_to_resources: dict[int, set[int]] = {}
    for resource in resources:
        for point_id in resource.knowledge_points.values_list("id", flat=True):
            point_to_resources.setdefault(int(point_id), set()).add(int(resource.id))
    return point_to_resources


def collect_knowledge_relation_maps(
    course_id: int,
) -> tuple[dict[int, set[int]], dict[int, set[int]], dict[int, set[int]]]:
    """把 Neo4j 前的 PostgreSQL 关系索引拆成先修、后继与相关关系。"""
    from knowledge.models import KnowledgeRelation

    prereq_points: dict[int, set[int]] = {}
    dependent_points: dict[int, set[int]] = {}
    related_points: dict[int, set[int]] = {}
    relation_rows = KnowledgeRelation.objects.filter(course_id=course_id).values_list(
        "pre_point_id",
        "post_point_id",
        "relation_type",
    )
    for pre_point_id, post_point_id, relation_type in relation_rows:
        register_relation_row(
            prereq_points=prereq_points,
            dependent_points=dependent_points,
            related_points=related_points,
            pre_point_id=int(pre_point_id),
            post_point_id=int(post_point_id),
            relation_type=str(relation_type),
        )
    return prereq_points, dependent_points, related_points


def register_relation_row(
    *,
    prereq_points: dict[int, set[int]],
    dependent_points: dict[int, set[int]],
    related_points: dict[int, set[int]],
    pre_point_id: int,
    post_point_id: int,
    relation_type: str,
) -> None:
    """把单条知识关系写入运行时邻接索引。"""
    if relation_type == "prerequisite":
        prereq_points.setdefault(post_point_id, set()).add(pre_point_id)
        dependent_points.setdefault(pre_point_id, set()).add(post_point_id)
        return
    related_points.setdefault(pre_point_id, set()).add(post_point_id)
    related_points.setdefault(post_point_id, set()).add(pre_point_id)


def collect_question_answer_stats(course_id: int) -> dict[int, dict[str, float]]:
    """聚合历史答题总数与正确数，供题目难度代理特征使用。"""
    from assessments.models import AnswerHistory

    answer_stats: dict[int, dict[str, float]] = {}
    answer_rows = AnswerHistory.objects.filter(course_id=course_id).values_list(
        "question_id",
        "is_correct",
    )
    for question_id_raw, is_correct in answer_rows:
        question_id = int(question_id_raw)
        stats = answer_stats.setdefault(question_id, {"total": 0.0, "correct": 0.0})
        stats["total"] += 1.0
        stats["correct"] += 1.0 if bool(is_correct) else 0.0
    return answer_stats


def build_feature_sources(source_data: RuntimeSourceData) -> RuntimeFeatureSources:
    """将课程源数据收敛为题目特征提取的输入。"""
    return RuntimeFeatureSources(
        point_to_resources=source_data.point_to_resources,
        prereq_points=source_data.prereq_points,
        dependent_points=source_data.dependent_points,
        related_points=source_data.related_points,
        answer_stats=source_data.answer_stats,
    )
