#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
知识测评结果快照刷新服务。
@Project : wisdom-edu
@File : knowledge_result_refresh.py
@Author : Qintsg
@Date : 2026-05-13 11:40
'''

from __future__ import annotations

from dataclasses import dataclass

from django.db import transaction

from assessments.models import AssessmentResult, Question
from assessments.services.assessment_helpers import persist_mastery_snapshot
from assessments.services.knowledge_assessment_logic import (
    blend_mastery_with_kt,
    evaluate_knowledge_answers,
)


@dataclass(frozen=True)
class KnowledgeResultRefreshSummary:
    """一次知识测评结果快照刷新摘要。"""

    result_id: int
    question_count: int
    mastery_count: int


def refresh_knowledge_result_snapshot(result: AssessmentResult) -> KnowledgeResultRefreshSummary | None:
    """
    重新计算既有知识测评结果快照。
    :param result: 需要刷新的知识测评结果。
    :return: 刷新摘要；无可重算答案时返回 None。
    """
    answer_dict = _resolve_answer_dict(result)
    if not answer_dict:
        return None

    questions = _load_answered_questions(result, answer_dict)
    if not questions:
        return None

    evaluation = evaluate_knowledge_answers(
        user=result.user,
        course_id=result.course_id,
        questions=questions,
        answer_dict=answer_dict,
    )
    final_mastery_map = blend_mastery_with_kt(
        user_id=int(result.user_id),
        course_id=int(result.course_id),
        mastery_map=evaluation.mastery_map,
        point_stats=evaluation.point_stats,
        answer_history_records=evaluation.answer_history_records,
    )
    with transaction.atomic():
        mastery_list = persist_mastery_snapshot(
            result.user,
            int(result.course_id),
            final_mastery_map,
            evaluation.point_stats,
        )
        result.answers = answer_dict
        result.score = evaluation.total_score
        result.result_data = {
            "mastery": mastery_list,
            "question_details": evaluation.question_details,
            "total_score": evaluation.total_possible_score,
            "correct_count": evaluation.correct_count,
            "total_count": evaluation.total_question_count,
        }
        result.save(update_fields=["answers", "score", "result_data"])
    return KnowledgeResultRefreshSummary(
        result_id=int(result.id),
        question_count=evaluation.total_question_count,
        mastery_count=len(mastery_list),
    )


def refresh_course_knowledge_result_snapshots(course_id: int) -> tuple[KnowledgeResultRefreshSummary, ...]:
    """
    刷新课程内所有既有知识测评结果快照。
    :param course_id: 课程 ID。
    :return: 刷新摘要列表。
    """
    results = AssessmentResult.objects.filter(
        course_id=course_id,
        assessment__assessment_type="knowledge",
    ).select_related("user", "assessment").order_by("user_id", "completed_at", "id")
    summaries: list[KnowledgeResultRefreshSummary] = []
    for result in results:
        summary = refresh_knowledge_result_snapshot(result)
        if summary is not None:
            summaries.append(summary)
    return tuple(summaries)


def _resolve_answer_dict(result: AssessmentResult) -> dict[str, object]:
    """从结果 answers 或题目详情快照中恢复作答映射。"""
    if isinstance(result.answers, dict) and result.answers:
        return {str(question_id): answer for question_id, answer in result.answers.items()}
    if isinstance(result.answers, list):
        return {
            str(item["question_id"]): item.get("answer")
            for item in result.answers
            if isinstance(item, dict) and item.get("question_id")
        }

    result_data = result.result_data if isinstance(result.result_data, dict) else {}
    details = result_data.get("question_details") if isinstance(result_data, dict) else []
    if not isinstance(details, list):
        return {}
    return {
        str(item["question_id"]): item.get("student_answer")
        for item in details
        if isinstance(item, dict) and item.get("question_id")
    }


def _load_answered_questions(result: AssessmentResult, answer_dict: dict[str, object]) -> list[Question]:
    """按作答顺序读取题目，并带上最新知识点绑定。"""
    question_ids = [int(question_id) for question_id in answer_dict if str(question_id).isdigit()]
    question_lookup = {
        int(question.id): question
        for question in result.assessment.questions.filter(id__in=question_ids).prefetch_related("knowledge_points")
    }
    return [
        question_lookup[question_id]
        for question_id in question_ids
        if question_id in question_lookup
    ]


__all__ = [
    "KnowledgeResultRefreshSummary",
    "refresh_course_knowledge_result_snapshots",
    "refresh_knowledge_result_snapshot",
]
