"""学生端考试反馈报告视图。"""
from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.responses import error_response, success_response

from .models import ExamSubmission, FeedbackReport
from .student_helpers import (
    FeedbackOverviewInput,
    build_feedback_overview,
    build_submission_feedback_snapshot,
    normalize_feedback_payload,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_feedback_report(request):
    """生成反馈报告。"""
    exam_id = request.data.get("exam_id")
    force = request.data.get("force", False)
    if not exam_id:
        return error_response(msg="缺少作业ID")

    user = request.user
    try:
        submission = ExamSubmission.objects.get(exam_id=exam_id, user=user)
    except ExamSubmission.DoesNotExist:
        return error_response(msg="您尚未完成该作业", code=404)

    report = FeedbackReport.objects.filter(exam_id=exam_id, user=user).first()
    snapshot = build_submission_feedback_snapshot(submission)
    question_details = snapshot["question_details"]
    if report and report.status == "completed" and not force:
        return success_response(data=normalize_feedback_payload(report, question_details))

    overview = dict(report.overview) if report and isinstance(report.overview, dict) else {}
    overview.update(build_feedback_overview(
        FeedbackOverviewInput(
            score=snapshot["grading"]["score"],
            total_score=submission.exam.total_score,
            passed=snapshot["passed"],
            correct_count=snapshot["correct_count"],
            total_count=snapshot["total_count"],
            accuracy=snapshot["accuracy"],
            kt_analysis=overview.get("kt_analysis", {}),
            summary=str(overview.get("summary", "")),
            knowledge_gaps=overview.get("knowledge_gaps", []),
        )
    ))
    report, _ = FeedbackReport.objects.update_or_create(
        exam_id=exam_id,
        user=user,
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

    from .report_service import enqueue_feedback_report_on_commit
    enqueue_feedback_report_on_commit(report.id, force=bool(force))

    msg = "AI 反馈报告已重新排队生成" if force else "AI 反馈报告生成中"
    return success_response(data=normalize_feedback_payload(report, question_details), msg=msg)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_feedback_report(request, exam_id):
    """获取反馈报告。"""
    report = FeedbackReport.objects.filter(exam_id=exam_id, user=request.user).first()
    if not report:
        return error_response(msg="报告不存在", code=404)

    question_details = []
    if report.exam_submission and report.exam:
        snapshot = build_submission_feedback_snapshot(report.exam_submission)
        question_details = snapshot["question_details"]
    return success_response(data=normalize_feedback_payload(report, question_details))
