"""知识测评异步生成辅助工具。"""
from __future__ import annotations

from typing import Any

from assessments.models import Assessment, AssessmentResult, AssessmentStatus
from users.models import User


# 维护意图：加载异步生成所需的用户与评测上下文
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
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


# 维护意图：统一更新知识测评异步生成状态
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
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


# 维护意图：从知识测评题目详情中抽取错题输入
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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


# 维护意图：加载知识测评结果及其分数快照
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
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


# 维护意图：生成或刷新学习路径
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def refresh_learning_path_for_assessment(*, user, course_id: int | str) -> None:
    """生成或刷新学习路径。"""
    from ai_services.services import PathService
    from courses.models import Course

    course = Course.objects.get(id=course_id)
    PathService().generate_path(user, course)


# 维护意图：刷新课程学习者画像
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def refresh_learner_profile_for_assessment(*, user, course_id: int | str) -> None:
    """刷新课程学习者画像。"""
    from users.services import get_learner_profile_service

    get_learner_profile_service(user).generate_profile_for_course(course_id)


# 维护意图：写回知识测评反馈报告，并返回报告 ID
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
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
