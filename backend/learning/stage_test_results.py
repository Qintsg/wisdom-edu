"""阶段测试提交结果持久化与 API 响应组装。"""

from __future__ import annotations

from django.utils import timezone

from learning.models import NodeProgress, PathNode
from learning.stage_test_models import PASS_THRESHOLD, TOTAL_SCORE, StageTestEvaluation
from learning.view_helpers import (
    _average_mastery,
    _build_mastery_change_payload,
    _snapshot_mastery_for_points,
)
from users.models import User


def persist_stage_progress(
    *,
    user: User,
    node: PathNode,
    progress: NodeProgress,
    evaluation: StageTestEvaluation,
    feedback_report: dict[str, object],
    mastery_before_snapshot: dict[int, float],
    tracked_point_ids: list[int],
    path_refreshed: bool,
    update_fields: list[str] | None,
) -> list[dict[str, object]]:
    """写入阶段测试结果和掌握度变化快照。"""
    mastery_after_snapshot = _snapshot_mastery_for_points(
        user,
        node.path.course_id,
        tracked_point_ids,
    )
    mastery_changes = _build_mastery_change_payload(
        mastery_before_snapshot,
        mastery_after_snapshot,
    )
    progress.mastery_before = _average_mastery(mastery_before_snapshot)
    progress.mastery_after = _average_mastery(mastery_after_snapshot)
    progress.extra_data = progress.extra_data or {}
    progress.extra_data["stage_test_result"] = _stored_stage_result(
        evaluation=evaluation,
        mastery_changes=mastery_changes,
        feedback_report=feedback_report,
        submitted_at=timezone.now().isoformat(),
        node_status=node.status,
        path_refreshed=path_refreshed,
    )
    if update_fields:
        progress.save(update_fields=update_fields)
    else:
        progress.save()
    return mastery_changes


def stage_response_payload(
    *,
    evaluation: StageTestEvaluation,
    mastery_changes: list[dict[str, object]],
    feedback_report: dict[str, object],
    node_status: str,
    path_refreshed: bool,
) -> dict[str, object]:
    """构造阶段测试提交 API 响应。"""
    return {
        "score": evaluation.score,
        "total_score": TOTAL_SCORE,
        "passed": evaluation.passed,
        "pass_threshold": PASS_THRESHOLD,
        "correct": evaluation.correct_count,
        "correct_count": evaluation.correct_count,
        "total": evaluation.total_count,
        "total_count": evaluation.total_count,
        "accuracy": evaluation.accuracy,
        "mistakes": evaluation.detailed_mistakes,
        "question_details": evaluation.question_details,
        "point_stats": evaluation.point_stats,
        "mastery_changes": mastery_changes,
        "feedback_report": feedback_report,
        "node_status": node_status,
        "path_refreshed": path_refreshed,
    }


def _stored_stage_result(
    *,
    evaluation: StageTestEvaluation,
    mastery_changes: list[dict[str, object]],
    feedback_report: dict[str, object],
    submitted_at: str,
    node_status: str,
    path_refreshed: bool,
) -> dict[str, object]:
    """构造写入 NodeProgress.extra_data 的阶段测试结果。"""
    return {
        "score": evaluation.score,
        "total_score": TOTAL_SCORE,
        "passed": evaluation.passed,
        "pass_threshold": PASS_THRESHOLD,
        "correct": evaluation.correct_count,
        "correct_count": evaluation.correct_count,
        "total": evaluation.total_count,
        "total_count": evaluation.total_count,
        "accuracy": evaluation.accuracy,
        "mistakes": evaluation.detailed_mistakes,
        "question_details": evaluation.question_details,
        "point_stats": evaluation.point_stats,
        "mastery_changes": mastery_changes,
        "feedback_report": feedback_report,
        "submitted_at": submitted_at,
        "node_status": node_status,
        "path_refreshed": path_refreshed,
    }
