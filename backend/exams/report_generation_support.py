"""考试反馈报告生成的上下文与持久化辅助逻辑。"""

from __future__ import annotations

import logging
from typing import Any

from django.db import DatabaseError

from common.logging_utils import build_log_message


logger = logging.getLogger(__name__)

REPORT_SAVE_FIELDS = [
    "overview",
    "status",
    "analysis",
    "recommendations",
    "next_tasks",
    "conclusion",
    "generated_at",
]


# 维护意图：加载报告及其关键关联对象
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_report_with_dependencies(report_id: int):
    """加载报告及其关键关联对象。"""
    from .models import FeedbackReport

    return (
        FeedbackReport.objects.select_related("exam", "exam_submission", "user")
        .filter(id=report_id)
        .first()
    )


# 维护意图：按题目与知识点展开答题轨迹
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_answer_history_records(
    exam_questions,
    submission_answers: dict[str, Any],
) -> list[dict[str, int]]:
    """按题目与知识点展开答题轨迹。"""
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


# 维护意图：将 KT 预测结果回写到课程知识点掌握度
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def persist_kt_predictions(
    *,
    report,
    exam,
    user,
    kt_predictions: dict[str, Any],
) -> None:
    """将 KT 预测结果回写到课程知识点掌握度。"""
    from knowledge.models import KnowledgeMastery

    for knowledge_point_id, mastery_rate in kt_predictions.items():
        try:
            # 单个知识点写入失败不应终止整份报告生成。
            KnowledgeMastery.objects.update_or_create(
                user=user,
                course_id=exam.course_id,
                knowledge_point_id=knowledge_point_id,
                defaults={"mastery_rate": float(mastery_rate)},
            )
        except (DatabaseError, TypeError, ValueError) as error:
            logger.warning(
                build_log_message(
                    "feedback.kt.mastery_update_fail",
                    report_id=report.id,
                    exam_id=exam.id,
                    user_id=user.id,
                    knowledge_point_id=knowledge_point_id,
                    error=error,
                )
            )


# 维护意图：刷新 KT 预测并回写掌握度
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def refresh_kt_analysis(
    report,
    exam,
    user,
    answer_history_records: list[dict[str, int]],
) -> dict[str, Any]:
    """刷新 KT 预测并回写掌握度。"""
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
            persist_kt_predictions(
                report=report,
                exam=exam,
                user=user,
                kt_predictions=kt_predictions,
            )

        kt_analysis = {
            "predictions": kt_predictions,
            "confidence": mapping_value(kt_result, "confidence", 0),
            "model_type": mapping_value(kt_result, "model_type", "unknown"),
            "answer_count": mapping_value(
                kt_result,
                "answer_count",
                len(answer_history_records),
            ),
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


# 维护意图：将错题结果补全为 LLM 可消费的结构
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_detailed_mistakes(
    exam_questions,
    mistakes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """将错题结果补全为 LLM 可消费的结构。"""
    question_map = {
        exam_question.question_id: exam_question.question
        for exam_question in exam_questions
    }
    detailed_mistakes: list[dict[str, Any]] = []
    for mistake in mistakes:
        question = question_map.get(mistake["question_id"])
        point = question.knowledge_points.first() if question else None
        analysis = mistake.get("analysis") or ""
        if not analysis and question:
            analysis = getattr(question, "analysis", "")
        detailed_mistakes.append(
            {
                "question_id": mistake["question_id"],
                "question_text": mistake["content"],
                "knowledge_point_name": point.name if point else "",
                "student_answer": mapping_value(mistake, "student_answer"),
                "correct_answer": mapping_value(mistake, "correct_answer"),
                "student_answer_display": mapping_value(mistake, "student_answer_display"),
                "correct_answer_display": mapping_value(mistake, "correct_answer_display"),
                "analysis": analysis,
            }
        )
    return detailed_mistakes


# 维护意图：获取用户学习习惯偏好
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_habit_preferences(user) -> dict[str, str] | None:
    """获取用户学习习惯偏好。"""
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


# 维护意图：规范化 LLM 返回的列表字段
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_llm_list(llm_result: dict[str, Any], field_name: str) -> list[Any]:
    """规范化 LLM 返回的列表字段。"""
    field_value = llm_result.get(field_name)
    return field_value if isinstance(field_value, list) else []


# 维护意图：读取 KT/LLM 中间结果字段并统一默认值语义
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def mapping_value(record: dict[str, Any], field_name: str, default_value: object = None) -> object:
    """读取 KT/LLM 中间结果字段并统一默认值语义。"""
    return record.get(field_name, default_value)


# 维护意图：记录反馈报告相关的 LLM 调用摘要
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def save_llm_call_log(
    user,
    exam,
    grading: dict[str, Any],
    mistakes: list[dict[str, Any]],
    summary: str,
) -> None:
    """记录反馈报告相关的 LLM 调用摘要。"""
    from ai_services.models import LLMCallLog

    try:
        # 调用日志失败只影响审计可见性，不影响学生报告主流程。
        LLMCallLog.objects.create(
            user=user,
            call_type="feedback_report",
            input_summary=f"exam:{exam.id}, score:{grading['score']}/{exam.total_score}, mistakes:{len(mistakes)}",
            output_summary=summary[:500],
            is_success=True,
        )
    except DatabaseError as error:
        logger.warning(
            build_log_message(
                "feedback.llm_call_log.fail",
                exam_id=exam.id,
                user_id=user.id,
                error=error,
            )
        )


# 维护意图：统一回写报告失败状态
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def persist_failed_report(report, error_message: str) -> dict[str, Any]:
    """统一回写报告失败状态。"""
    overview = dict(report.overview) if isinstance(report.overview, dict) else {}
    overview["generation_error"] = error_message
    report.overview = overview
    report.status = "failed"
    report.analysis = overview.get("analysis") or ""
    report.recommendations = report.recommendations or []
    report.next_tasks = report.next_tasks or []
    report.conclusion = report.conclusion or "AI 报告生成失败，请稍后重试。"
    report.save(update_fields=REPORT_SAVE_FIELDS)
    return overview


__all__ = [
    "REPORT_SAVE_FIELDS",
    "build_answer_history_records",
    "build_detailed_mistakes",
    "extract_habit_preferences",
    "load_report_with_dependencies",
    "normalize_llm_list",
    "persist_failed_report",
    "refresh_kt_analysis",
    "save_llm_call_log",
]
