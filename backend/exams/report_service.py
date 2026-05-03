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

from django.db import close_old_connections, transaction

from common.logging_utils import build_log_message
from exams.report_generation_support import (
    REPORT_SAVE_FIELDS,
    build_answer_history_records,
    build_detailed_mistakes,
    extract_habit_preferences,
    load_report_with_dependencies,
    normalize_llm_list,
    persist_failed_report,
    refresh_kt_analysis,
    save_llm_call_log,
)
from exams.report_service_support import (
    apply_completed_report,
    build_report_generation_context,
    build_report_overview,
    normalize_llm_feedback,
)

logger = logging.getLogger(__name__)

REPORT_EXECUTOR = ThreadPoolExecutor(
    max_workers=2, thread_name_prefix="feedback-report"
)
ENQUEUED_REPORT_IDS: set[int] = set()
QUEUE_LOCK = Lock()


# 维护意图：将报告生成任务加入后台队列。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def enqueue_feedback_report(report_id: int, force: bool = False) -> bool:
    """
    将报告生成任务加入后台队列。
    :param report_id: 反馈报告 ID。
    :param force: 是否强制重跑已完成报告。
    :return: 是否成功进入队列。
    """
    with QUEUE_LOCK:
        if report_id in ENQUEUED_REPORT_IDS:
            return False
        ENQUEUED_REPORT_IDS.add(report_id)

    REPORT_EXECUTOR.submit(run_feedback_generation, report_id, force)
    return True


# 维护意图：在事务提交后调度报告生成。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def enqueue_feedback_report_on_commit(report_id: int, force: bool = False) -> None:
    """
    在事务提交后调度报告生成。
    :param report_id: 反馈报告 ID。
    :param force: 是否强制重跑已完成报告。
    :return: None。
    """
    transaction.on_commit(lambda: enqueue_feedback_report(report_id, force=force))


# 维护意图：在线程池中执行报告生成并回收连接。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def run_feedback_generation(report_id: int, force: bool = False) -> None:
    """
    在线程池中执行报告生成并回收连接。
    :param report_id: 反馈报告 ID。
    :param force: 是否强制重跑已完成报告。
    :return: None。
    """
    close_old_connections()
    try:
        # 后台线程在独立数据库连接生命周期内生成报告，避免影响提交事务。
        generate_feedback_report_sync(report_id, force=force)
    finally:
        with QUEUE_LOCK:
            ENQUEUED_REPORT_IDS.discard(report_id)
        close_old_connections()


# 维护意图：同步生成单份考试反馈报告。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def generate_feedback_report_sync(
    report_id: int, force: bool = False
) -> dict[str, Any] | None:
    """
    同步生成单份考试反馈报告。
    :param report_id: 反馈报告 ID。
    :param force: 是否强制重跑已完成报告。
    :return: 更新后的概要字典，报告不存在时返回 None。
    """
    from ai_services.services import llm_service
    from .student_views import (
        _build_exam_question_details,
        _build_exam_score_map,
        _resolve_pass_threshold,
    )

    report = load_report_with_dependencies(report_id)
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

        # 报告上下文统一从批改结果、KT、能力画像与学习习惯提取，供 LLM 使用。
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
            build_answer_history_records=build_answer_history_records,
            refresh_kt_analysis=refresh_kt_analysis,
            build_detailed_mistakes=build_detailed_mistakes,
            extract_habit_preferences=extract_habit_preferences,
        )

        llm_result = llm_service.generate_feedback_report(
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
            normalize_list=normalize_llm_list,
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
            save_fields=REPORT_SAVE_FIELDS,
        )

        save_llm_call_log(
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
        return persist_failed_report(report, str(exc))
