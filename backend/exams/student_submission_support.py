"""学生端考试提交流程辅助工具。"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import InvalidOperation
from typing import Any

from django.db import DatabaseError, IntegrityError
from django.utils import timezone

from common.logging_utils import build_log_message
from common.utils import extract_answer_value, score_questions, serialize_answer_payload

from .models import Exam, ExamQuestion, ExamSubmission, FeedbackReport
from .student_helpers import (
    build_exam_question_details,
    build_feedback_overview,
    build_mastery_change_payload,
    resolve_pass_threshold,
    snapshot_mastery_for_points,
)


logger = logging.getLogger(__name__)


class DuplicateExamSubmissionError(RuntimeError):
    """表示考试已经完成提交，不应重复写入。"""


@dataclass
class ExamSubmissionContext:
    """考试提交前的评分和回显上下文。"""

    exam_questions: list[ExamQuestion]
    questions: list[Any]
    grading: dict[str, Any]
    question_result_map: dict[str, dict[str, Any]]
    question_details: list[dict[str, Any]]
    score: float
    pass_threshold: float
    passed: bool
    correct_count: int
    accuracy: float


def build_exam_submission_context(exam: Exam, answers: dict[str, Any]) -> ExamSubmissionContext:
    """构建考试提交所需的批改与回显上下文。"""
    exam_questions = list(
        ExamQuestion.objects.filter(exam=exam)
        .select_related("question")
        .prefetch_related("question__knowledge_points")
    )
    questions = [exam_question.question for exam_question in exam_questions]
    from .student_helpers import build_exam_score_map

    score_map = build_exam_score_map(exam, exam_questions)
    grading = score_questions(answers, questions, score_map=score_map)
    question_result_map = {
        str(item["question_id"]): item for item in grading["question_results"]
    }
    question_details = build_exam_question_details(
        exam_questions,
        answers,
        question_result_map,
    )
    score = float(grading["score"])
    pass_threshold = resolve_pass_threshold(exam)
    passed = score >= pass_threshold
    correct_count = sum(
        1 for item in grading["question_results"] if item["is_correct"]
    )
    accuracy = round(correct_count / len(questions) * 100, 1) if questions else 0
    return ExamSubmissionContext(
        exam_questions=exam_questions,
        questions=questions,
        grading=grading,
        question_result_map=question_result_map,
        question_details=question_details,
        score=score,
        pass_threshold=pass_threshold,
        passed=passed,
        correct_count=correct_count,
        accuracy=accuracy,
    )


def upsert_exam_submission_record(
    *,
    exam: Exam,
    user,
    answers: dict[str, Any],
    context: ExamSubmissionContext,
) -> ExamSubmission:
    """创建或更新考试提交记录。"""
    existing_submission = (
        ExamSubmission.objects.select_for_update()
        .filter(exam=exam, user=user)
        .first()
    )
    if existing_submission and existing_submission.score is not None and float(existing_submission.score) >= 0:
        raise DuplicateExamSubmissionError("already_submitted")

    if existing_submission:
        existing_submission.answers = answers
        existing_submission.score = context.score
        existing_submission.is_passed = context.passed
        existing_submission.graded_at = timezone.now()
        existing_submission.save(
            update_fields=["answers", "score", "is_passed", "graded_at"]
        )
        return existing_submission

    try:
        return ExamSubmission.objects.create(
            exam=exam,
            user=user,
            answers=answers,
            score=context.score,
            is_passed=context.passed,
            graded_at=timezone.now(),
        )
    except IntegrityError as error:
        raise DuplicateExamSubmissionError("already_submitted") from error


def build_answer_history_batch(
    *,
    exam: Exam,
    user,
    answers: dict[str, Any],
    context: ExamSubmissionContext,
) -> tuple[list[Any], list[dict[str, int]]]:
    """构建考试答题历史批量写入对象和 KT 输入记录。"""
    from assessments.models import AnswerHistory

    mistake_question_ids = {
        str(mistake["question_id"]) for mistake in context.grading["mistakes"]
    }
    history_models: list[AnswerHistory] = []
    answer_history_records: list[dict[str, int]] = []
    for question in context.questions:
        question_id = str(question.id)
        result = context.question_result_map.get(question_id, {})
        student_answer = answers.get(question_id)
        correct_value = result.get(
            "correct_answer",
            extract_answer_value(question.answer),
        )
        is_correct = result.get("is_correct", question_id not in mistake_question_ids)
        knowledge_point = question.knowledge_points.first()
        history_models.append(
            AnswerHistory(
                user=user,
                course=exam.course,
                question=question,
                knowledge_point=knowledge_point,
                student_answer=serialize_answer_payload(
                    question.question_type,
                    student_answer,
                ),
                correct_answer=serialize_answer_payload(
                    question.question_type,
                    correct_value,
                ),
                is_correct=is_correct,
                score=result.get("earned_score", 0),
                source="exam",
                exam_id=exam.id,
            )
        )
        if knowledge_point:
            answer_history_records.append(
                {
                    "question_id": question.id,
                    "knowledge_point_id": knowledge_point.id,
                    "correct": 1 if is_correct else 0,
                }
            )
    return history_models, answer_history_records


def persist_answer_histories(history_models: list[Any]) -> None:
    """批量持久化考试答题历史。"""
    if history_models:
        from assessments.models import AnswerHistory

        AnswerHistory.objects.bulk_create(history_models, batch_size=100)


def capture_mastery_snapshot_from_records(
    *,
    user,
    course_id: int,
    answer_history_records: list[dict[str, int]],
) -> dict[int, float]:
    """基于本次考试涉及的知识点读取掌握度快照。"""
    tracked_point_ids = sorted(
        {
            int(item["knowledge_point_id"])
            for item in answer_history_records
            if item.get("knowledge_point_id")
        }
    )
    return snapshot_mastery_for_points(user, course_id, tracked_point_ids)


def refresh_exam_kt_analysis(
    *,
    user,
    exam: Exam,
    answer_history_records: list[dict[str, int]],
) -> dict[str, Any]:
    """刷新考试后的 KT 预测并回写掌握度。"""
    kt_analysis: dict[str, Any] = {}
    try:
        from ai_services.services import kt_service
        from knowledge.models import KnowledgeMastery

        if not answer_history_records:
            return kt_analysis

        kt_result = kt_service.predict_mastery(
            user_id=user.id,
            course_id=exam.course_id,
            answer_history=answer_history_records,
        )
        kt_predictions = kt_result.get("predictions") or {}
        if kt_predictions:
            for knowledge_point_id, mastery_rate in kt_predictions.items():
                try:
                    KnowledgeMastery.objects.update_or_create(
                        user=user,
                        course_id=exam.course_id,
                        knowledge_point_id=knowledge_point_id,
                        defaults={"mastery_rate": float(mastery_rate)},
                    )
                except (
                    DatabaseError,
                    InvalidOperation,
                    OverflowError,
                    TypeError,
                    ValueError,
                ) as error:
                    logger.warning(
                        build_log_message(
                            "kt.exam_submit.mastery_skip",
                            user_id=user.id,
                            exam_id=exam.id,
                            knowledge_point_id=knowledge_point_id,
                            error=error,
                        )
                    )
            kt_analysis = {
                "predictions": kt_predictions,
                "confidence": kt_result.get("confidence", 0),
                "model_type": kt_result.get("model_type", "unknown"),
            }
            logger.info(
                build_log_message(
                    "kt.exam_submit.success",
                    user_id=user.id,
                    exam_id=exam.id,
                    answer_count=len(answer_history_records),
                    prediction_count=len(kt_predictions),
                )
            )
    except Exception as error:
        logger.error(
            build_log_message(
                "kt.exam_submit.fail",
                user_id=user.id,
                exam_id=exam.id,
                error=error,
            )
        )
    return kt_analysis


def build_submission_feedback_state(
    *,
    user,
    exam: Exam,
    submission: ExamSubmission,
    context: ExamSubmissionContext,
    kt_analysis: dict[str, Any],
    mastery_before_snapshot: dict[int, float],
) -> tuple[FeedbackReport, list[dict[str, Any]]]:
    """生成反馈报告预置状态和掌握度变化明细。"""
    mastery_after_snapshot = snapshot_mastery_for_points(
        user,
        exam.course_id,
        sorted(mastery_before_snapshot.keys()),
    )
    mastery_changes = build_mastery_change_payload(
        mastery_before_snapshot,
        mastery_after_snapshot,
    )
    overview = build_feedback_overview(
        score=context.score,
        total_score=exam.total_score,
        passed=context.passed,
        correct_count=context.correct_count,
        total_count=len(context.questions),
        accuracy=context.accuracy,
        kt_analysis=kt_analysis,
        mastery_changes=mastery_changes,
    )
    report, _ = FeedbackReport.objects.update_or_create(
        user=user,
        exam=exam,
        defaults={
            "exam_submission": submission,
            "status": "pending",
            "overview": overview,
            "analysis": "",
            "recommendations": [],
            "next_tasks": [],
            "conclusion": "",
        },
    )
    return report, mastery_changes


def sync_result_submission_snapshot(submission: ExamSubmission, snapshot: dict[str, Any]) -> tuple[float, bool]:
    """确保结果页回显分数与通过状态与当前快照一致。"""
    display_score = float(snapshot["grading"]["score"])
    passed = bool(snapshot["passed"])
    if submission.score is None or float(submission.score) != display_score or submission.is_passed != passed:
        submission.score = display_score
        submission.is_passed = passed
        submission.graded_at = submission.graded_at or timezone.now()
        submission.save(update_fields=["score", "is_passed", "graded_at"])
    return display_score, passed
