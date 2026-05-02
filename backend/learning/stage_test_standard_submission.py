"""常规阶段测试提交流程。"""

from __future__ import annotations

import logging

from django.db import transaction

from assessments.models import AnswerHistory
from common.logging_utils import build_log_message
from knowledge.models import KnowledgeMastery
from learning.models import NodeProgress, PathNode
from learning.stage_test_feedback import build_feedback_report
from learning.stage_test_models import StageTestEvaluation
from learning.stage_test_results import persist_stage_progress, stage_response_payload
from users.models import User


logger = logging.getLogger(__name__)


def submit_standard_stage_test(
    *,
    node: PathNode,
    user: User,
    progress: NodeProgress,
    evaluation: StageTestEvaluation,
    mastery_before_snapshot: dict[int, float],
    tracked_point_ids: list[int],
) -> dict[str, object]:
    """处理常规阶段测试提交。"""
    with transaction.atomic():
        update_standard_node_status(node, evaluation.passed)
        update_mastery_from_kt_or_fallback(user, node, evaluation.point_stats)
        feedback_report = build_feedback_report(node, user, evaluation)
        mastery_changes = persist_stage_progress(
            user=user,
            node=node,
            progress=progress,
            evaluation=evaluation,
            feedback_report=feedback_report,
            mastery_before_snapshot=mastery_before_snapshot,
            tracked_point_ids=tracked_point_ids,
            path_refreshed=False,
            update_fields=None,
        )

    if evaluation.passed:
        refresh_learning_path(user, node)

    return stage_response_payload(
        evaluation=evaluation,
        mastery_changes=mastery_changes,
        feedback_report=feedback_report,
        node_status=node.status,
        path_refreshed=evaluation.passed,
    )


def update_standard_node_status(node: PathNode, passed: bool) -> None:
    """更新常规阶段测试状态并在通过后解锁下一个节点。"""
    node.status = "completed" if passed else "failed"
    node.save()
    if not passed:
        return
    next_node = (
        PathNode.objects.filter(path=node.path, order_index__gt=node.order_index)
        .order_by("order_index")
        .first()
    )
    if next_node and next_node.status == "locked":
        next_node.status = "active"
        next_node.save()


def update_mastery_from_kt_or_fallback(
    user: User,
    node: PathNode,
    point_stats: dict[int, dict[str, object]],
) -> None:
    """优先用 KT 预测更新掌握度，失败时使用原简单算法兜底。"""
    try:
        kt_predictions = predict_stage_mastery(user, node, point_stats)
        apply_stage_kt_predictions(user, node, kt_predictions)
    except Exception as exc:
        logger.error(
            build_log_message(
                "kt.stage_test.fail",
                user_id=user.id,
                node_id=node.id,
                error=exc,
            )
        )
        fallback_mastery_update(user, node, point_stats)


def predict_stage_mastery(
    user: User,
    node: PathNode,
    point_stats: dict[int, dict[str, object]],
) -> dict[object, object]:
    """汇总课程作答历史并调用 KT 服务。"""
    from ai_services.services.kt_service import kt_service

    kt_history = [
        {
            "question_id": history["question_id"],
            "knowledge_point_id": history["knowledge_point_id"],
            "correct": 1 if history["is_correct"] else 0,
        }
        for history in AnswerHistory.objects.filter(user=user, course=node.path.course)
        .order_by("answered_at")
        .values("question_id", "knowledge_point_id", "is_correct")
    ]
    kt_result = kt_service.predict_mastery(
        user_id=user.id,
        course_id=node.path.course_id,
        answer_history=kt_history,
        knowledge_points=list(point_stats.keys()),
    )
    kt_predictions = kt_result.get("predictions", {})
    logger.info(
        build_log_message(
            "kt.stage_test.success",
            user_id=user.id,
            node_id=node.id,
            answer_count=len(kt_history),
            prediction_count=len(kt_predictions),
        )
    )
    return kt_predictions


def apply_stage_kt_predictions(
    user: User,
    node: PathNode,
    kt_predictions: dict[object, object],
) -> None:
    """写入 KT 预测掌握度。"""
    for knowledge_point_id, mastery_value in kt_predictions.items():
        try:
            mastery, _ = KnowledgeMastery.objects.get_or_create(
                user=user,
                course=node.path.course,
                knowledge_point_id=knowledge_point_id,
            )
            mastery.mastery_rate = max(0, min(1, round(float(mastery_value), 4)))
            mastery.save()
        except Exception as exc:
            logger.warning(
                build_log_message(
                    "kt.stage_test.mastery_update_fail",
                    user_id=user.id,
                    node_id=node.id,
                    knowledge_point_id=knowledge_point_id,
                    error=exc,
                )
            )


def fallback_mastery_update(
    user: User,
    node: PathNode,
    point_stats: dict[int, dict[str, object]],
) -> None:
    """KT 不可用时按当前阶段测试正确率微调掌握度。"""
    for knowledge_point_id, stats in point_stats.items():
        try:
            if stats["total"] <= 0:
                continue
            mastery_delta = 0.1 if stats["correct"] / stats["total"] >= 0.8 else -0.05
            mastery, _ = KnowledgeMastery.objects.get_or_create(
                user=user,
                course=node.path.course,
                knowledge_point_id=knowledge_point_id,
            )
            mastery.mastery_rate = max(0, min(1, float(mastery.mastery_rate) + mastery_delta))
            mastery.save()
        except Exception as exc:
            logger.warning(
                build_log_message(
                    "kt.stage_test.fallback_mastery_update_fail",
                    user_id=user.id,
                    node_id=node.id,
                    knowledge_point_id=knowledge_point_id,
                    error=exc,
                )
            )


def refresh_learning_path(user: User, node: PathNode) -> None:
    """阶段测试通过后触发路径刷新。"""
    from ai_services.services.path_service import PathService

    PathService().generate_path(user, node.path.course)
