"""知识测评异步生成辅助工具。"""
from __future__ import annotations

from typing import Any

from assessments.models import Assessment, AssessmentResult, AssessmentStatus
from users.models import User


def resolve_async_generation_context(
    *,
    user_id: int,
    assessment_id: int,
) -> tuple[User | None, Assessment | None, str | None]:
    """加载异步生成所需的用户与评测上下文。"""
    try:
        user = User.objects.get(id=user_id)
        assessment = Assessment.objects.get(id=assessment_id)
        return user, assessment, None
    except Exception as exc:
        return None, None, str(exc)


def update_generation_status(
    *,
    user_id: int,
    course_id: int | str,
    generating: bool,
    generation_error: str | None,
) -> None:
    """统一更新知识测评异步生成状态。"""
    AssessmentStatus.objects.filter(user_id=user_id, course_id=course_id).update(
        generating=generating,
        generation_error=generation_error,
    )


def build_assessment_mistake_payload(question_details: list[dict[str, object]]) -> list[dict[str, object]]:
    """从知识测评题目详情中抽取错题输入。"""
    mistakes = [detail for detail in question_details if not detail["is_correct"]]
    return [
        {
            "question_text": mistake["content"],
            "knowledge_point_name": mistake["knowledge_points"][0]["name"] if mistake["knowledge_points"] else "",
            "student_answer": mistake["student_answer"],
            "correct_answer": mistake["correct_answer"],
            "analysis": mistake["analysis"],
        }
        for mistake in mistakes[:5]
    ]


def load_assessment_result_snapshot(*, user_id: int, assessment) -> tuple[AssessmentResult | None, float, float]:
    """加载知识测评结果及其分数快照。"""
    assessment_result = AssessmentResult.objects.filter(
        user_id=user_id,
        assessment=assessment,
    ).first()
    if assessment_result is None:
        return None, 0.0, 0.0
    result_data = assessment_result.result_data if isinstance(assessment_result.result_data, dict) else {}
    return (
        assessment_result,
        float(assessment_result.score or 0),
        float(result_data.get("total_score", 0)),
    )


def refresh_learning_path_for_assessment(*, user, course_id: int | str) -> None:
    """生成或刷新学习路径。"""
    from ai_services.services import PathService
    from courses.models import Course

    course = Course.objects.get(id=course_id)
    PathService().generate_path(user, course)


def refresh_learner_profile_for_assessment(*, user, course_id: int | str) -> None:
    """刷新课程学习者画像。"""
    from users.services import get_learner_profile_service

    get_learner_profile_service(user).generate_profile_for_course(course_id)


def upsert_assessment_feedback_report(
    *,
    user_id: int,
    assessment,
    question_details: list[dict[str, object]],
    llm_feedback: dict[str, Any] | object,
) -> int:
    """写回知识测评反馈报告，并返回报告 ID。"""
    from exams.models import FeedbackReport

    assessment_result = AssessmentResult.objects.filter(
        user_id=user_id,
        assessment=assessment,
    ).first()
    if assessment_result is None:
        raise AssessmentResult.DoesNotExist("未找到知识测评结果")

    assessment_score = float(assessment_result.score or 0)
    result_data = assessment_result.result_data if isinstance(assessment_result.result_data, dict) else {}
    assessment_total_score = float(result_data.get("total_score", 0))
    report, _ = FeedbackReport.objects.update_or_create(
        user_id=user_id,
        source="assessment",
        assessment_result=assessment_result,
        defaults={
            "exam": None,
            "status": "completed",
            "overview": {
                "score": assessment_score,
                "total_score": assessment_total_score,
                "correct_count": sum(1 for detail in question_details if detail["is_correct"]),
                "total_count": len(question_details),
                "accuracy": round(
                    sum(1 for detail in question_details if detail["is_correct"])
                    / max(len(question_details), 1)
                    * 100,
                    1,
                ),
                "summary": llm_feedback.get("summary", "") if isinstance(llm_feedback, dict) else "",
                "knowledge_gaps": llm_feedback.get("knowledge_gaps", []) if isinstance(llm_feedback, dict) else [],
            },
            "analysis": llm_feedback.get("analysis", "") if isinstance(llm_feedback, dict) else str(llm_feedback),
            "recommendations": llm_feedback.get("recommendations", []) if isinstance(llm_feedback, dict) else [],
            "next_tasks": llm_feedback.get("next_tasks", []) if isinstance(llm_feedback, dict) else [],
            "conclusion": llm_feedback.get("encouragement", "") if isinstance(llm_feedback, dict) else "",
        },
    )
    return int(report.id)
