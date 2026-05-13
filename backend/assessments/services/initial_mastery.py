#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
初始知识测评掌握度融合工具。
@Project : wisdom-edu
@File : initial_mastery.py
@Author : Qintsg
@Date : 2026-05-13 12:15
'''

from __future__ import annotations

from dataclasses import dataclass

from assessments.models import AnswerHistory
from assessments.services.assessment_helpers import (
    INITIAL_MASTERY_MAX,
    calculate_initial_mastery_baseline,
)
from assessments.services.knowledge_assessment_logic import (
    blend_mastery_with_kt,
    load_initial_course_point_ids,
    resolve_initial_kt_weight,
)
from ai_services.services.kt.prediction_support import answered_point_ids
from learning.paths.rules import apply_prerequisite_caps


@dataclass(frozen=True)
class InitialMasteryEvidence:
    """初始知识测评直接作答证据。"""

    answer_history_records: list[dict[str, int | None]]
    point_stats: dict[int, dict[str, object]]
    mastery_map: dict[int, float]


def load_initial_mastery_evidence(*, user_id: int, course_id: int) -> InitialMasteryEvidence:
    """
    读取初始测评作答历史并构造直接掌握度证据。
    :param user_id: 学生用户 ID。
    :param course_id: 课程 ID。
    :return: 初始测评证据对象。
    """
    rows = (
        AnswerHistory.objects.filter(user_id=user_id, course_id=course_id, source="initial")
        .order_by("answered_at", "id")
        .values("question_id", "knowledge_point_id", "knowledge_point__name", "is_correct")
    )
    answer_history_records: list[dict[str, int | None]] = []
    point_stats: dict[int, dict[str, object]] = {}
    for row in rows:
        point_id = int(row["knowledge_point_id"]) if row["knowledge_point_id"] else None
        is_correct = 1 if row["is_correct"] else 0
        answer_history_records.append(
            {
                "question_id": int(row["question_id"]),
                "knowledge_point_id": point_id,
                "correct": is_correct,
            }
        )
        if point_id is None:
            continue
        stats = point_stats.setdefault(
            point_id,
            {
                "correct": 0,
                "total": 0,
                "name": row["knowledge_point__name"] or f"知识点{point_id}",
            },
        )
        stats["total"] = int(stats["total"]) + 1
        stats["correct"] = int(stats["correct"]) + is_correct

    mastery_map = {
        point_id: calculate_initial_mastery_baseline(
            int(stats["correct"]),
            int(stats["total"]),
        )
        for point_id, stats in point_stats.items()
    }
    return InitialMasteryEvidence(
        answer_history_records=answer_history_records,
        point_stats=point_stats,
        mastery_map=mastery_map,
    )


def build_initial_mastery_from_history(*, user_id: int, course_id: int) -> dict[int, float]:
    """
    按知识测评提交时的规则重算初始掌握度。
    :param user_id: 学生用户 ID。
    :param course_id: 课程 ID。
    :return: 初始测评证据与 MEFKT 融合后的掌握度。
    """
    evidence = load_initial_mastery_evidence(user_id=user_id, course_id=course_id)
    if not evidence.answer_history_records:
        return {}
    if not evidence.mastery_map:
        return {}
    return blend_mastery_with_kt(
        user_id=user_id,
        course_id=course_id,
        mastery_map=evidence.mastery_map,
        point_stats=evidence.point_stats,
        answer_history_records=evidence.answer_history_records,
    )


def blend_initial_evidence_with_predictions(
    *,
    course_id: int,
    evidence: InitialMasteryEvidence,
    prediction_map: dict[int, float],
    uses_mefkt: bool,
) -> dict[int, float]:
    """
    将既有 KT 预测与初始测评直接证据融合，避免异步写回覆盖初测差异。
    :param course_id: 课程 ID。
    :param evidence: 初始测评直接证据。
    :param prediction_map: KT/MEFKT 预测掌握度。
    :param uses_mefkt: 预测结果是否来自真实 MEFKT。
    :return: 融合后的掌握度。
    """
    if not evidence.answer_history_records:
        return dict(prediction_map)
    if not evidence.mastery_map:
        return dict(prediction_map)

    normalized_predictions = {
        int(point_id): max(0.0, min(INITIAL_MASTERY_MAX, float(rate)))
        for point_id, rate in prediction_map.items()
    }
    if not uses_mefkt:
        evidence_points = answered_point_ids(evidence.answer_history_records)
        normalized_predictions = {
            point_id: rate
            for point_id, rate in normalized_predictions.items()
            if point_id in evidence_points
        }
    if not normalized_predictions:
        return apply_prerequisite_caps(dict(evidence.mastery_map), course_id)

    course_point_ids = set(
        load_initial_course_point_ids(
            course_id=course_id,
            measured_point_ids=set(evidence.mastery_map),
        )
    )
    blended_mastery = dict(evidence.mastery_map)
    for point_id, predicted_rate in normalized_predictions.items():
        if point_id not in evidence.mastery_map:
            if uses_mefkt and point_id in course_point_ids:
                blended_mastery[point_id] = round(predicted_rate, 4)
            continue
        point_total = max(int(evidence.point_stats.get(point_id, {}).get("total", 0)), 0)
        baseline = float(evidence.mastery_map[point_id])
        kt_weight = resolve_initial_kt_weight(point_total=point_total, uses_mefkt=uses_mefkt)
        blended = baseline * (1 - kt_weight) + predicted_rate * kt_weight
        blended = min(blended, baseline + 0.12)
        blended_mastery[point_id] = round(max(0.0, min(INITIAL_MASTERY_MAX, blended)), 4)
    return apply_prerequisite_caps(blended_mastery, course_id)


__all__ = [
    "InitialMasteryEvidence",
    "blend_initial_evidence_with_predictions",
    "build_initial_mastery_from_history",
    "load_initial_mastery_evidence",
]
