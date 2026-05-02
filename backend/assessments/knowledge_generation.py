"""
知识测评提交后的异步生成任务。

该模块隔离耗时的学习路径、画像和反馈报告生成，避免主视图文件继续承载跨服务编排细节。
"""
from __future__ import annotations

import logging

from .knowledge_generation_support import (
    build_assessment_mistake_payload,
    load_assessment_result_snapshot,
    refresh_learner_profile_for_assessment,
    refresh_learning_path_for_assessment,
    resolve_async_generation_context,
    update_generation_status,
    upsert_assessment_feedback_report,
)
from .models import Assessment, AssessmentResult, AssessmentStatus


logger = logging.getLogger(__name__)


def async_generate_after_assessment(
    user_id: int,
    course_id: int | str,
    assessment_id: int,
    question_details: list[dict[str, object]],
) -> None:
    """
    在知识测评提交后异步完成耗时操作。

    生成/刷新学习路径、学习者画像和反馈报告，完成后更新 AssessmentStatus.generating。
    """
    import django
    django.setup()

    user, assessment, context_error = resolve_async_generation_context(
        user_id=user_id,
        assessment_id=assessment_id,
    )
    if user is None or assessment is None:
        logger.error(f"异步生成：无法获取用户或测评 user_id={user_id}: {context_error}")
        update_generation_status(
            user_id=user_id,
            course_id=course_id,
            generating=False,
            generation_error=context_error,
        )
        return

    errors: list[str] = []

    try:
        refresh_learning_path_for_assessment(user=user, course_id=course_id)
        logger.info(f"异步生成：学习路径生成成功 user={user_id} course={course_id}")
    except Exception as exc:
        logger.error(f"异步生成：学习路径生成失败 user={user_id}: {exc}")
        errors.append(f"学习路径: {exc}")

    try:
        refresh_learner_profile_for_assessment(user=user, course_id=course_id)
        logger.info(f"异步生成：学习者画像刷新成功 user={user_id} course={course_id}")
    except Exception as exc:
        logger.error(f"异步生成：学习画像刷新失败 user={user_id}: {exc}")
        errors.append(f"学习画像: {exc}")

    try:
        from ai_services.services import llm_service as llm
        assessment_result, assessment_score, assessment_total_score = load_assessment_result_snapshot(
            user_id=user_id,
            assessment=assessment,
        )
        if assessment_result is None:
            raise AssessmentResult.DoesNotExist("未找到知识测评结果")

        report_content = llm.generate_feedback_report(
            exam_info={'title': assessment.title, 'type': '初始知识评测'},
            score=assessment_score,
            total_score=assessment_total_score,
            mistakes=build_assessment_mistake_payload(question_details),
        )
        report_id = upsert_assessment_feedback_report(
            user_id=user_id,
            assessment=assessment,
            question_details=question_details,
            llm_feedback=report_content,
        )
        logger.info(f"异步生成：反馈报告生成成功 user={user_id} report={report_id}")
    except Exception as exc:
        logger.error(f"异步生成：反馈报告生成失败 user={user_id}: {exc}")
        errors.append(f"反馈报告: {exc}")

    update_generation_status(
        user_id=user_id,
        course_id=course_id,
        generating=False,
        generation_error='; '.join(errors) if errors else None,
    )
    logger.info(f"异步生成完成 user={user_id} course={course_id} errors={len(errors)}")
