"""阶段测试提交评分、掌握度更新与反馈生成逻辑。"""

from __future__ import annotations

import logging

from django.db import transaction

from assessments.models import AnswerHistory, Question
from common.defense_demo import (
    complete_defense_demo_stage_test,
    get_defense_demo_stage_test_payload,
    is_defense_demo_student,
)
from common.logging_utils import build_log_message
from common.utils import (
    build_answer_display,
    build_normalized_score_map,
    check_answer,
    decorate_question_options,
    extract_answer_value,
    score_questions,
    serialize_answer_payload,
)
from knowledge.models import KnowledgeMastery, KnowledgePoint
from learning.models import NodeProgress, PathNode
from learning.stage_test_feedback import build_feedback_report
from learning.stage_test_models import PASS_THRESHOLD, TOTAL_SCORE, StageTestEvaluation
from learning.stage_test_results import (
    persist_stage_progress,
    stage_response_payload,
)
from learning.view_helpers import _snapshot_mastery_for_points
from users.models import User


logger = logging.getLogger(__name__)


def submit_stage_test_answers(
    *,
    node: PathNode,
    user: User,
    answers: dict[str, object],
) -> dict[str, object]:
    """提交阶段测试答案并返回兼容前端的结果 payload。"""
    evaluation = _evaluate_stage_test(node=node, user=user, answers=answers)
    progress, _ = NodeProgress.objects.get_or_create(node=node, user=user)
    tracked_point_ids = sorted(evaluation.point_stats.keys())
    mastery_before_snapshot = _snapshot_mastery_for_points(
        user,
        node.path.course_id,
        tracked_point_ids,
    )
    demo_stage_payload = get_defense_demo_stage_test_payload(progress)

    if demo_stage_payload and is_defense_demo_student(user, node.path.course):
        return _submit_demo_stage_test(
            node=node,
            user=user,
            progress=progress,
            evaluation=evaluation,
            demo_stage_payload=demo_stage_payload,
            mastery_before_snapshot=mastery_before_snapshot,
            tracked_point_ids=tracked_point_ids,
        )

    return _submit_standard_stage_test(
        node=node,
        user=user,
        progress=progress,
        evaluation=evaluation,
        mastery_before_snapshot=mastery_before_snapshot,
        tracked_point_ids=tracked_point_ids,
    )


def _evaluate_stage_test(
    *,
    node: PathNode,
    user: User,
    answers: dict[str, object],
) -> StageTestEvaluation:
    """读取题目、评分并记录每题作答历史。"""
    question_ids = _question_ids_from_answers(answers)
    question_map = _question_map(node, question_ids)
    questions = [question_map[question_id] for question_id in question_ids if question_id in question_map]
    grading = _grade_questions(answers, questions)
    question_result_map = {
        str(item["question_id"]): item
        for item in grading["question_results"]
    }
    question_details = _build_question_details(
        node=node,
        user=user,
        answers=answers,
        questions=questions,
        question_result_map=question_result_map,
    )
    detailed_mistakes = _build_detailed_mistakes(question_details, question_map)
    score = float(grading["score"])
    correct_count = sum(1 for item in grading["question_results"] if item["is_correct"])
    total_count = len(questions)

    return StageTestEvaluation(
        answers=answers,
        questions=questions,
        question_map=question_map,
        point_stats=grading["point_stats"],
        question_details=question_details,
        detailed_mistakes=detailed_mistakes,
        score=score,
        passed=score >= PASS_THRESHOLD,
        correct_count=correct_count,
        total_count=total_count,
        accuracy=round(correct_count / total_count * 100, 1) if total_count else 0,
    )


def _question_ids_from_answers(answers: dict[str, object]) -> list[int]:
    """将前端答案 key 转成题目 ID，忽略无法解析的异常 key。"""
    question_ids: list[int] = []
    for question_id_text in answers:
        try:
            question_ids.append(int(question_id_text))
        except (TypeError, ValueError):
            logger.warning("阶段测试答案包含非法题目ID: %s", question_id_text)
    return question_ids


def _question_map(node: PathNode, question_ids: list[int]) -> dict[int, Question]:
    """按课程约束读取可评分题目。"""
    return {
        question.id: question
        for question in Question.objects.filter(
            id__in=question_ids,
            course=node.path.course,
        ).prefetch_related("knowledge_points")
    }


def _grade_questions(
    answers: dict[str, object],
    questions: list[Question],
) -> dict[str, object]:
    """使用统一评分工具按 100 分制计算阶段测试成绩。"""
    stage_score_map = build_normalized_score_map(
        [(question.id, 1) for question in questions],
        target_total_score=TOTAL_SCORE,
        equal_weight=True,
    )
    return score_questions(answers, questions, score_map=stage_score_map)


def _build_question_details(
    *,
    node: PathNode,
    user: User,
    answers: dict[str, object],
    questions: list[Question],
    question_result_map: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    """生成每题详情并写入 AnswerHistory。"""
    question_details: list[dict[str, object]] = []
    for question in questions:
        result = question_result_map.get(str(question.id), {})
        question_detail = _build_single_question_detail(
            node=node,
            user=user,
            answers=answers,
            question=question,
            result=result,
        )
        question_details.append(question_detail)
    return question_details


def _build_single_question_detail(
    *,
    node: PathNode,
    user: User,
    answers: dict[str, object],
    question: Question,
    result: dict[str, object],
) -> dict[str, object]:
    """构造单题反馈详情并记录作答历史。"""
    student_answer = answers.get(str(question.id))
    correct_value = result.get("correct_answer", extract_answer_value(question.answer))
    is_correct = result.get(
        "is_correct",
        check_answer(question.question_type, student_answer, question.answer),
    )
    decorated_options = decorate_question_options(
        question.options,
        question.question_type,
        student_answer=student_answer,
        correct_answer=correct_value,
    )
    question_points: list[KnowledgePoint] = list(question.knowledge_points.all())
    primary_point = question_points[0] if question_points else None
    AnswerHistory.objects.create(
        user=user,
        course=node.path.course,
        question=question,
        knowledge_point=primary_point,
        student_answer=serialize_answer_payload(question.question_type, student_answer),
        correct_answer=serialize_answer_payload(question.question_type, correct_value),
        is_correct=is_correct,
        score=result.get("earned_score", 0),
    )
    return {
        "question_id": question.id,
        "content": question.content,
        "question_type": question.question_type,
        "student_answer": student_answer,
        "correct_answer": correct_value,
        "student_answer_display": build_answer_display(
            student_answer,
            question.question_type,
            decorated_options,
        ),
        "correct_answer_display": build_answer_display(
            correct_value,
            question.question_type,
            decorated_options,
        ),
        "is_correct": is_correct,
        "analysis": result.get("analysis") or question.analysis or "",
        "options": decorated_options,
        "knowledge_points": [
            {"id": point.id, "name": point.name}
            for point in question_points
        ],
        "score": result.get("earned_score", 0),
        "full_score": result.get("assigned_score", 0),
    }


def _build_detailed_mistakes(
    question_details: list[dict[str, object]],
    question_map: dict[int, Question],
) -> list[dict[str, object]]:
    """从题目详情中提取错题报告输入。"""
    return [
        _mistake_detail(item, question_map.get(item["question_id"]))
        for item in question_details
        if not item["is_correct"]
    ]


def _mistake_detail(
    item: dict[str, object],
    question: Question | None,
) -> dict[str, object]:
    """构造单道错题详情。"""
    related_points = list(question.knowledge_points.all()) if question else []
    primary_point = related_points[0] if related_points else None
    return {
        "question_id": item["question_id"],
        "question_text": question.content if question else "",
        "knowledge_point_name": primary_point.name if primary_point else "",
        "student_answer": item.get("student_answer"),
        "correct_answer": item.get("correct_answer"),
        "student_answer_display": item.get("student_answer_display"),
        "correct_answer_display": item.get("correct_answer_display"),
        "analysis": item.get("analysis") or (question.analysis if question else ""),
        "options": item.get("options", []),
    }


def _submit_demo_stage_test(
    *,
    node: PathNode,
    user: User,
    progress: NodeProgress,
    evaluation: StageTestEvaluation,
    demo_stage_payload: dict[str, object],
    mastery_before_snapshot: dict[int, float],
    tracked_point_ids: list[int],
) -> dict[str, object]:
    """答辩预置阶段测试使用固定掌握度和固定反馈。"""
    with transaction.atomic():
        _update_demo_node_status(node, user, progress, evaluation.passed)
        _apply_demo_mastery(user, node, demo_stage_payload)
        mastery_changes = persist_stage_progress(
            user=user,
            node=node,
            progress=progress,
            evaluation=evaluation,
            feedback_report=_demo_feedback_report(demo_stage_payload),
            mastery_before_snapshot=mastery_before_snapshot,
            tracked_point_ids=tracked_point_ids,
            path_refreshed=evaluation.passed,
            update_fields=["mastery_before", "mastery_after", "extra_data", "updated_at"],
        )

    return stage_response_payload(
        evaluation=evaluation,
        mastery_changes=mastery_changes,
        feedback_report=_demo_feedback_report(demo_stage_payload),
        node_status=node.status,
        path_refreshed=evaluation.passed,
    )


def _update_demo_node_status(
    node: PathNode,
    user: User,
    progress: NodeProgress,
    passed: bool,
) -> None:
    """更新答辩预置阶段测试节点状态。"""
    if passed:
        complete_defense_demo_stage_test(node, user, progress)
        return
    node.status = "failed"
    node.save(update_fields=["status"])


def _apply_demo_mastery(
    user: User,
    node: PathNode,
    demo_stage_payload: dict[str, object],
) -> None:
    """按答辩预置 payload 写入固定掌握度。"""
    mastery_after_map = demo_stage_payload.get("mastery_after", {})
    if not isinstance(mastery_after_map, dict):
        return
    for point_id_text, mastery_value in mastery_after_map.items():
        try:
            point_id = int(point_id_text)
            mastery_rate = round(float(mastery_value), 4)
        except (TypeError, ValueError):
            continue
        KnowledgeMastery.objects.update_or_create(
            user=user,
            course=node.path.course,
            knowledge_point_id=point_id,
            defaults={"mastery_rate": mastery_rate},
        )


def _demo_feedback_report(demo_stage_payload: dict[str, object]) -> dict[str, object]:
    """读取答辩预置反馈报告。"""
    feedback_report = demo_stage_payload.get("feedback_report")
    return feedback_report if isinstance(feedback_report, dict) else {}


def _submit_standard_stage_test(
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
        _update_standard_node_status(node, evaluation.passed)
        _update_mastery_from_kt_or_fallback(user, node, evaluation.point_stats)
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
        _refresh_learning_path(user, node)

    return stage_response_payload(
        evaluation=evaluation,
        mastery_changes=mastery_changes,
        feedback_report=feedback_report,
        node_status=node.status,
        path_refreshed=evaluation.passed,
    )


def _update_standard_node_status(node: PathNode, passed: bool) -> None:
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


def _update_mastery_from_kt_or_fallback(
    user: User,
    node: PathNode,
    point_stats: dict[int, dict[str, object]],
) -> None:
    """优先用 KT 预测更新掌握度，失败时使用原简单算法兜底。"""
    try:
        kt_predictions = _predict_stage_mastery(user, node, point_stats)
        _apply_stage_kt_predictions(user, node, kt_predictions)
    except Exception as exc:
        logger.error(
            build_log_message(
                "kt.stage_test.fail",
                user_id=user.id,
                node_id=node.id,
                error=exc,
            )
        )
        _fallback_mastery_update(user, node, point_stats)


def _predict_stage_mastery(
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


def _apply_stage_kt_predictions(
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


def _fallback_mastery_update(
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


def _refresh_learning_path(user: User, node: PathNode) -> None:
    """阶段测试通过后触发路径刷新。"""
    from ai_services.services.path_service import PathService

    PathService().generate_path(user, node.path.course)
