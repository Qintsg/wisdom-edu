"""学生端画像、反馈、学习建议与路径刷新 AI 接口。"""

from __future__ import annotations

import logging
from typing import Any

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from assessments.models import AbilityScore, AssessmentStatus
from common.logging_utils import build_log_message
from common.responses import error_response, success_response
from courses.models import Course
from exams.models import Exam, ExamQuestion, ExamSubmission, FeedbackReport
from knowledge.models import KnowledgeMastery, KnowledgePoint, ProfileSummary, Resource
from platform_ai.llm import llm_facade
from users.models import HabitPreference
from users.services import get_learner_profile_service
from .models import LLMCallLog
from .services.path_service import PathService

logger = logging.getLogger(__name__)


def _build_habit_data(user) -> dict[str, Any] | None:
    try:
        habit = user.habit_preference
    except HabitPreference.DoesNotExist:
        return None
    return {"preferred_resource": habit.preferred_resource, "preferred_study_time": habit.preferred_study_time}


def _build_mastery_data(user, course_id: int) -> list[dict[str, Any]]:
    mastery_records = KnowledgeMastery.objects.filter(user=user, course_id=course_id).select_related("knowledge_point")
    return [
        {
            "point_id": record.knowledge_point_id,
            "point_name": record.knowledge_point.name if record.knowledge_point else "",
            "mastery_rate": float(record.mastery_rate),
        }
        for record in mastery_records
        if record.knowledge_point_id
    ]


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_profile_analysis(request):
    """Generate a student profile summary for the current course."""
    course_id = request.data.get("course_id")
    refresh = bool(request.data.get("refresh", False))
    if not course_id:
        return error_response(msg="缺少课程ID", code=400)
    if not Course.objects.filter(id=course_id).exists():
        return error_response(msg="课程不存在", code=404)

    status = AssessmentStatus.objects.filter(user=request.user, course_id=course_id).first()
    has_ability = AbilityScore.objects.filter(user=request.user, course_id=course_id).exists()
    if not has_ability or not (status and status.knowledge_done):
        return error_response(msg="请先完成测评后再获取AI分析", code=400)

    service = get_learner_profile_service(request.user)
    try:
        result = service.generate_profile_for_course(int(course_id), force_refresh=refresh)
    except Exception as exc:
        logger.error(build_log_message("ai.profile_analysis.fail", user_id=request.user.id, course_id=course_id, error=exc))
        return error_response(msg="AI 分析服务暂时不可用", code=500)
    if not result.get("success", False):
        return error_response(msg=str(result.get("error") or "AI 分析服务暂时不可用"), code=500)
    return success_response(data=result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_resource_reason(request):
    """Generate a brief reason explaining why a resource is recommended."""
    resource_id = request.data.get("resource_id")
    course_id = request.data.get("course_id")
    point_id = request.data.get("point_id")
    if not resource_id:
        return error_response(msg="缺少 resource_id 参数", code=400)

    try:
        resource = Resource.objects.get(id=resource_id)
    except Resource.DoesNotExist:
        return error_response(msg="资源不存在", code=404)
    if course_id and int(course_id) != resource.course_id:
        return error_response(msg="资源与当前课程不匹配", code=400)

    mastery = None
    point_name = None
    if point_id:
        try:
            point = KnowledgePoint.objects.get(id=point_id)
            if point.course_id != resource.course_id:
                return error_response(msg="知识点与资源不属于同一课程", code=400)
            point_name = point.name
            mastery_record = KnowledgeMastery.objects.filter(user=request.user, knowledge_point=point).first()
            mastery = float(mastery_record.mastery_rate) if mastery_record else None
        except KnowledgePoint.DoesNotExist:
            pass

    resource_info = {"title": resource.title, "type": resource.resource_type, "description": resource.description or ""}
    fallback = {"reason": f"{resource.title} 与当前知识点相关，可用于补强薄弱环节。", "learning_tips": "建议先快速浏览核心内容，再结合练习进行巩固。"}
    result = (
        llm_facade.generate_resource_reason(resource_info, mastery, point_name, resource.course.name if resource.course_id else None)
        if llm_facade.is_available
        else fallback
    )
    LLMCallLog.objects.create(
        user=request.user,
        call_type="resource_reason",
        input_summary=f"resource={resource_id}, point={point_id or 'na'}",
        output_summary=str(result)[:500],
        is_success=True,
    )
    return success_response(data=result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_feedback_report(request):
    """Return an AI feedback report or a generated fallback summary."""
    exam_id = request.data.get("exam_id")
    if not exam_id:
        return error_response(msg="缺少 exam_id 参数", code=400)
    try:
        exam = Exam.objects.get(id=exam_id)
        submission = ExamSubmission.objects.get(exam=exam, user=request.user)
    except (Exam.DoesNotExist, ExamSubmission.DoesNotExist):
        return error_response(msg="作业或提交记录不存在", code=404)

    report = FeedbackReport.objects.filter(exam=exam, user=request.user).first()
    if report and report.status == "completed":
        return success_response(data={
            "status": report.status,
            "overview": report.overview,
            "analysis": report.analysis,
            "recommendations": report.recommendations,
            "next_tasks": report.next_tasks,
            "conclusion": report.conclusion,
        })

    mistakes: list[dict[str, Any]] = []
    answers = submission.answers or {}
    for exam_question in ExamQuestion.objects.filter(exam=exam).select_related("question"):
        question = exam_question.question
        correct_answer = question.answer.get("answer", question.answer) if isinstance(question.answer, dict) else question.answer
        student_answer = answers.get(str(question.id))
        if student_answer == correct_answer:
            continue
        mistakes.append({"question": question.content, "student_answer": student_answer, "correct_answer": correct_answer, "analysis": question.analysis or ""})

    fallback = {
        "status": "completed",
        "overview": {"score": float(submission.score), "total_score": float(exam.total_score), "passed": submission.is_passed},
        "analysis": mistakes,
        "recommendations": ["优先复习错题对应知识点", "完成一轮针对性练习"],
        "next_tasks": ["回看本次错题解析", "完成学习路径中的下一个节点"],
        "conclusion": "已生成基础反馈，请结合知识图谱和学习路径继续巩固。",
    }
    if llm_facade.is_available:
        result = llm_facade.generate_feedback_report(
            exam_info={"title": exam.title, "type": exam.exam_type},
            score=float(submission.score),
            total_score=float(exam.total_score),
            mistakes=mistakes,
            kt_predictions=None,
        )
        fallback["recommendations"] = result.get("recommendations") or fallback["recommendations"]
        fallback["next_tasks"] = result.get("next_tasks") or fallback["next_tasks"]
        fallback["conclusion"] = result.get("conclusion") or fallback["conclusion"]
    return success_response(data=fallback)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_learning_advice(request):
    """Return current-course advice grounded in profile and mastery data."""
    course_id = request.data.get("course_id")
    if not course_id:
        return error_response(msg="缺少课程ID", code=400)
    mastery_data = _build_mastery_data(request.user, int(course_id))
    ability = AbilityScore.objects.filter(user=request.user, course_id=course_id).first()
    habit_data = _build_habit_data(request.user)
    profile_result = (
        llm_facade.analyze_profile(mastery_data=mastery_data, ability_data=ability.scores if ability else None, habit_data=habit_data)
        if llm_facade.is_available
        else {}
    )
    return success_response(data={
        "summary": profile_result.get("summary", ""),
        "weakness": profile_result.get("weakness", []),
        "strength": profile_result.get("strength", []),
        "suggestion": profile_result.get("suggestion", ""),
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_refresh_profile(request):
    """Force-refresh the student profile for a course."""
    course_id = request.data.get("course_id")
    if not course_id:
        return error_response(msg="缺少课程ID", code=400)
    service = get_learner_profile_service(request.user)
    try:
        result = service.generate_profile_for_course(int(course_id), force_refresh=True)
    except Exception as exc:
        logger.error(build_log_message("ai.refresh_profile.fail", user_id=request.user.id, course_id=course_id, error=exc))
        return error_response(msg="AI 分析服务暂时不可用", code=500)
    if not result.get("success", False):
        return error_response(msg=str(result.get("error") or "AI 分析服务暂时不可用"), code=500)
    return success_response(data=result)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_refresh_learning_path(request):
    """Rebuild the student's learning path for the given course."""
    course_id = request.data.get("course_id")
    if not course_id:
        return error_response(msg="缺少课程ID", code=400)
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)

    existing_path = getattr(request.user, "learning_paths", None)
    existing_path = existing_path.filter(course=course).first() if existing_path else None
    preserved_count = 0
    removed_count = 0
    if existing_path:
        preserved_count = existing_path.nodes.filter(status__in=("completed", "active", "skipped", "failed")).count()
        removed_count = existing_path.nodes.filter(status="locked").count()

    path = PathService().generate_path(request.user, course)
    ordered_nodes = list(path.nodes.order_by("order_index"))
    nodes = [
        {
            "node_id": node.id,
            "title": node.title,
            "status": node.status,
            "node_type": node.node_type,
            "knowledge_point_id": node.knowledge_point_id,
            "suggestion": node.suggestion,
            "is_inserted": node.is_inserted,
        }
        for node in ordered_nodes
    ]
    return success_response(data={
        "path_id": path.id,
        "nodes": nodes,
        "ai_reason": path.ai_reason,
        "dynamic": path.is_dynamic,
        "preserved_count": preserved_count,
        "new_count": max(0, len(ordered_nodes) - preserved_count),
        "change_summary": {"preserved_context": preserved_count, "removed_count": removed_count},
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_key_points_reminder(request):
    """Return weak knowledge points that should be reviewed next."""
    course_id = request.data.get("course_id")
    if not course_id:
        return error_response(msg="缺少 course_id", code=400)
    weak_points = KnowledgeMastery.objects.filter(user=request.user, course_id=course_id, mastery_rate__lt=0.6).select_related("knowledge_point").order_by("mastery_rate")[:10]
    reminders = [
        {
            "knowledge_point_id": record.knowledge_point_id,
            "name": record.knowledge_point.name if record.knowledge_point else "",
            "mastery_rate": float(record.mastery_rate),
            "suggestion": f"建议优先复习 {record.knowledge_point.name if record.knowledge_point else '当前知识点'}。",
        }
        for record in weak_points
    ]
    return success_response(data={"reminders": reminders})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_time_scheduling(request):
    """Distribute available study hours across weak knowledge points."""
    course_id = request.data.get("course_id")
    available_hours = float(request.data.get("available_hours", 2))
    if not course_id:
        return error_response(msg="缺少 course_id", code=400)

    weak_points = KnowledgeMastery.objects.filter(user=request.user, course_id=course_id, mastery_rate__lt=0.7).select_related("knowledge_point").order_by("mastery_rate")
    total_weight = sum(1 - float(record.mastery_rate) for record in weak_points) or 1.0
    schedule = []
    for record in weak_points[:8]:
        hours = round(available_hours * (1 - float(record.mastery_rate)) / total_weight, 1)
        schedule.append({
            "knowledge_point": record.knowledge_point.name if record.knowledge_point else "",
            "mastery_rate": float(record.mastery_rate),
            "suggested_hours": hours,
        })
    return success_response(data={"total_hours": available_hours, "schedule": schedule})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ai_analysis_compare(request):
    """Compare two profile snapshots by date."""
    date1 = request.query_params.get("date1")
    date2 = request.query_params.get("date2")
    if not date1 or not date2:
        return error_response(msg="请提供 date1 和 date2 参数", code=400)

    history = ProfileSummary.objects.filter(user=request.user).order_by("generated_at")
    snapshot1 = history.filter(generated_at__date__lte=date1).last()
    snapshot2 = history.filter(generated_at__date__lte=date2).last()
    return success_response(data={
        "date1": date1,
        "snapshot1": {"summary": snapshot1.summary, "weakness": snapshot1.weakness, "suggestion": snapshot1.suggestion} if snapshot1 else None,
        "date2": date2,
        "snapshot2": {"summary": snapshot2.summary, "weakness": snapshot2.weakness, "suggestion": snapshot2.suggestion} if snapshot2 else None,
    })
