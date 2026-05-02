#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
考试反馈报告生成服务。
复用现有 FeedbackReport.status 字段，将 LLM 报告生成放到进程内后台线程，避免阻塞考试提交主链路。
@Project : wisdom-edu
@File : report_service.py
@Author : Qintsg
@Date : 2026-03-23
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Any

from django.db import DatabaseError, close_old_connections, transaction

from common.logging_utils import build_log_message
from exams.report_service_support import (
    apply_completed_report,
    build_report_generation_context,
    build_report_overview,
    normalize_llm_feedback,
)

logger = logging.getLogger(__name__)

_REPORT_EXECUTOR = ThreadPoolExecutor(
    max_workers=2, thread_name_prefix="feedback-report"
)
_ENQUEUED_REPORT_IDS: set[int] = set()
_QUEUE_LOCK = Lock()
_REPORT_SAVE_FIELDS = [
    "overview",
    "status",
    "analysis",
    "recommendations",
    "next_tasks",
    "conclusion",
    "generated_at",
]


def enqueue_feedback_report(report_id: int, force: bool = False) -> bool:
    """
    将报告生成任务加入后台队列。
    :param report_id: 反馈报告 ID。
    :param force: 是否强制重跑已完成报告。
    :return: 是否成功进入队列。
    """
    with _QUEUE_LOCK:
        if report_id in _ENQUEUED_REPORT_IDS:
            return False
        _ENQUEUED_REPORT_IDS.add(report_id)

    _REPORT_EXECUTOR.submit(_run_feedback_generation, report_id, force)
    return True


def enqueue_feedback_report_on_commit(report_id: int, force: bool = False) -> None:
    """
    在事务提交后调度报告生成。
    :param report_id: 反馈报告 ID。
    :param force: 是否强制重跑已完成报告。
    :return: None。
    """
    transaction.on_commit(lambda: enqueue_feedback_report(report_id, force=force))


def _run_feedback_generation(report_id: int, force: bool = False) -> None:
    """
    在线程池中执行报告生成并回收连接。
    :param report_id: 反馈报告 ID。
    :param force: 是否强制重跑已完成报告。
    :return: None。
    """
    close_old_connections()
    try:
        generate_feedback_report_sync(report_id, force=force)
    finally:
        with _QUEUE_LOCK:
            _ENQUEUED_REPORT_IDS.discard(report_id)
        close_old_connections()


def _load_report_with_dependencies(report_id: int):
    """
    加载报告及其关键关联对象。
    :param report_id: 反馈报告 ID。
    :return: 带关键关联对象的报告实例，未命中时返回 None。
    """
    from .models import FeedbackReport

    return (
        FeedbackReport.objects.select_related("exam", "exam_submission", "user")
        .filter(id=report_id)
        .first()
    )


def _build_answer_history_records(
    exam_questions, submission_answers: dict[str, Any]
) -> list[dict[str, int]]:
    """
    按题目与知识点展开答题轨迹。
    :param exam_questions: 试卷题目关联列表。
    :param submission_answers: 学生提交答案。
    :return: 供 KT 预测使用的答题轨迹列表。
    """
    from common.utils import check_answer

    answer_history_records: list[dict[str, int]] = []
    for exam_question in exam_questions:
        question = exam_question.question
        student_answer = submission_answers.get(str(question.id))
        is_correct = check_answer(
            question.question_type,
            student_answer,
            question.answer,
        )
        for knowledge_point in question.knowledge_points.all():
            answer_history_records.append(
                {
                    "question_id": question.id,
                    "knowledge_point_id": knowledge_point.id,
                    "correct": 1 if is_correct else 0,
                }
            )
    return answer_history_records


def _refresh_kt_analysis(
    report, exam, user, answer_history_records: list[dict[str, int]]
) -> dict[str, Any]:
    """
    刷新 KT 预测并回写掌握度。
    :param report: 当前反馈报告对象。
    :param exam: 当前考试对象。
    :param user: 当前学生对象。
    :param answer_history_records: 答题轨迹列表。
    :return: KT 分析结果字典。
    """
    from knowledge.models import KnowledgeMastery

    kt_analysis: dict[str, Any] = {}
    try:
        from ai_services.services import kt_service

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
                except DatabaseError:
                    continue

        kt_analysis = {
            "predictions": kt_predictions,
            "confidence": kt_result.get("confidence", 0),
            "model_type": kt_result.get("model_type", "unknown"),
            "answer_count": kt_result.get("answer_count", len(answer_history_records)),
        }
    except (DatabaseError, ImportError, RuntimeError, TypeError, ValueError) as exc:
        logger.warning(
            build_log_message(
                "feedback.kt.refresh.fail",
                report_id=report.id,
                exam_id=exam.id,
                user_id=user.id,
                error=exc,
            )
        )
    return kt_analysis


def _build_detailed_mistakes(
    exam_questions, mistakes: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    将错题结果补全为 LLM 可消费的结构。
    :param exam_questions: 试卷题目关联列表。
    :param mistakes: 批改结果中的错题列表。
    :return: 补全后的错题详情列表。
    """
    question_map = {
        exam_question.question_id: exam_question.question
        for exam_question in exam_questions
    }
    detailed_mistakes: list[dict[str, Any]] = []
    for mistake in mistakes:
        question = question_map.get(mistake["question_id"])
        point = question.knowledge_points.first() if question else None
        detailed_mistakes.append(
            {
                "question_id": mistake["question_id"],
                "question_text": mistake["content"],
                "knowledge_point_name": point.name if point else "",
                "student_answer": mistake.get("student_answer"),
                "correct_answer": mistake.get("correct_answer"),
                "student_answer_display": mistake.get("student_answer_display"),
                "correct_answer_display": mistake.get("correct_answer_display"),
                "analysis": mistake.get("analysis") or getattr(question, "analysis", "")
                if question
                else "",
            }
        )
    return detailed_mistakes


def _extract_habit_preferences(user) -> dict[str, str] | None:
    """
    获取用户学习习惯偏好。
    :param user: 当前学生对象。
    :return: 学习习惯偏好字典，缺失时返回 None。
    """
    from users.models import HabitPreference

    try:
        habit = user.habit_preference
        return {
            "preferred_resource": habit.preferred_resource,
            "preferred_study_time": habit.preferred_study_time,
            "study_pace": getattr(habit, "study_pace", ""),
        }
    except HabitPreference.DoesNotExist:
        return None


def _normalize_llm_list(llm_result: dict[str, Any], field_name: str) -> list[Any]:
    """
    规范化 LLM 返回的列表字段。
    :param llm_result: LLM 结构化返回结果。
    :param field_name: 目标字段名称。
    :return: 规范化后的列表结果。
    """
    field_value = llm_result.get(field_name)
    return field_value if isinstance(field_value, list) else []


def _save_llm_call_log(
    user, exam, grading: dict[str, Any], mistakes: list[dict[str, Any]], summary: str
) -> None:
    """
    记录反馈报告相关的 LLM 调用摘要。
    :param user: 当前学生对象。
    :param exam: 当前考试对象。
    :param grading: 批改结果字典。
    :param mistakes: 错题列表。
    :param summary: 报告摘要文本。
    :return: None。
    """
    from ai_services.models import LLMCallLog

    try:
        LLMCallLog.objects.create(
            user=user,
            call_type="feedback_report",
            input_summary=f"exam:{exam.id}, score:{grading['score']}/{exam.total_score}, mistakes:{len(mistakes)}",
            output_summary=summary[:500],
            is_success=True,
        )
    except DatabaseError:
        return


def _persist_failed_report(report, error_message: str) -> dict[str, Any]:
    """
    统一回写报告失败状态。
    :param report: 当前反馈报告对象。
    :param error_message: 失败原因文本。
    :return: 回写后的报告概览字典。
    """
    overview = dict(report.overview) if isinstance(report.overview, dict) else {}
    overview["generation_error"] = error_message
    report.overview = overview
    report.status = "failed"
    report.analysis = overview.get("analysis") or ""
    report.recommendations = report.recommendations or []
    report.next_tasks = report.next_tasks or []
    report.conclusion = report.conclusion or "AI 报告生成失败，请稍后重试。"
    report.save(update_fields=_REPORT_SAVE_FIELDS)
    return overview


def generate_feedback_report_sync(
    report_id: int, force: bool = False
) -> dict[str, Any] | None:
    """
    同步生成单份考试反馈报告。
    :param report_id: 反馈报告 ID。
    :param force: 是否强制重跑已完成报告。
    :return: 更新后的概要字典，报告不存在时返回 None。
    """
    from ai_services.services import llm_service as _llm
    from .student_views import (
        _build_exam_question_details,
        _build_exam_score_map,
        _resolve_pass_threshold,
    )

    report = _load_report_with_dependencies(report_id)
    if not report or not report.exam_submission or not report.exam:
        return None

    if report.status == "completed" and not force:
        return dict(report.overview) if isinstance(report.overview, dict) else {}

    exam = report.exam
    submission = report.exam_submission
    user = report.user

    report.status = "pending"
    report.save(update_fields=["status"])

    try:
        from common.utils import clean_display_text
        from .models import ExamQuestion

        context = build_report_generation_context(
            report=report,
            exam=exam,
            submission=submission,
            load_exam_questions=lambda current_exam: ExamQuestion.objects.filter(exam=current_exam)
            .select_related("question")
            .prefetch_related("question__knowledge_points")
            .order_by("order"),
            build_exam_score_map=_build_exam_score_map,
            build_exam_question_details=_build_exam_question_details,
            build_answer_history_records=_build_answer_history_records,
            refresh_kt_analysis=_refresh_kt_analysis,
            build_detailed_mistakes=_build_detailed_mistakes,
            extract_habit_preferences=_extract_habit_preferences,
        )

        llm_result = _llm.generate_feedback_report(
            exam_info={
                "title": exam.title,
                "type": getattr(exam, "exam_type", "课程作业"),
            },
            score=float(context.grading["score"]),
            total_score=float(exam.total_score),
            mistakes=context.detailed_mistakes,
            kt_predictions=context.kt_analysis.get("predictions") or {},
        )

        normalized_feedback = normalize_llm_feedback(
            llm_result=llm_result,
            clean_text=clean_display_text,
            normalize_list=_normalize_llm_list,
        )
        overview = build_report_overview(
            report=report,
            exam=exam,
            grading=context.grading,
            pass_threshold=_resolve_pass_threshold(exam),
            correct_count=context.correct_count,
            total_count=context.total_count,
            accuracy=context.accuracy,
            kt_analysis=context.kt_analysis,
            ability_data=context.ability_data,
            habit_data=context.habit_data,
            summary=normalized_feedback.summary,
            knowledge_gaps=normalized_feedback.knowledge_gaps,
        )
        apply_completed_report(
            report=report,
            overview=overview,
            normalized_feedback=normalized_feedback,
            detailed_mistakes=context.detailed_mistakes,
            save_fields=_REPORT_SAVE_FIELDS,
        )

        _save_llm_call_log(
            user,
            exam,
            context.grading,
            context.mistakes,
            normalized_feedback.summary,
        )

        logger.info(
            build_log_message(
                "feedback.report.complete",
                report_id=report.id,
                exam_id=exam.id,
                user_id=user.id,
                status=report.status,
            )
        )
        return overview
    except Exception as exc:
        logger.error(
            build_log_message(
                "feedback.report.generate_fail",
                report_id=report.id,
                exam_id=exam.id,
                user_id=user.id,
                error=exc,
            )
        )
        return _persist_failed_report(report, str(exc))
