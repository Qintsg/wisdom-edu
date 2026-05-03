"""学生端考试提交、结果与统计视图。"""
from __future__ import annotations

from django.db import models, transaction
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsStudent
from common.responses import error_response, success_response

from .models import Exam, ExamSubmission
from .student_submission_support import (
    capture_mastery_snapshot_from_records,
    DuplicateExamSubmissionError,
    build_answer_history_batch,
    build_exam_submission_context,
    build_submission_feedback_state,
    persist_answer_histories,
    refresh_exam_kt_analysis,
    sync_result_submission_snapshot,
    upsert_exam_submission_record,
)
from .student_helpers import (
    build_feedback_report_ref,
    build_submission_feedback_snapshot,
    resolve_pass_threshold,
)


# 维护意图：提交考试答案
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def exam_submit(request, exam_id):
    """提交考试答案。"""
    answers = request.data.get("answers", {})
    if not answers:
        return error_response(msg="答案不能为空")
    if not isinstance(answers, dict):
        return error_response(msg="答案格式错误，应为字典格式")

    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    user = request.user
    if ExamSubmission.objects.filter(exam=exam, user=user, score__gte=0).exists():
        return error_response(msg="已经提交过该作业")
    if exam.end_time and exam.end_time < timezone.now():
        return error_response(msg="作业已结束，无法提交", code=403)

    submission_context = build_exam_submission_context(exam, answers)
    with transaction.atomic():
        try:
            submission = upsert_exam_submission_record(
                exam=exam,
                user=user,
                answers=answers,
                context=submission_context,
            )
        except DuplicateExamSubmissionError:
            return error_response(msg="已经提交过该作业")
        history_models, answer_history_records = build_answer_history_batch(
            exam=exam,
            user=user,
            answers=answers,
            context=submission_context,
        )
        persist_answer_histories(history_models)
        mastery_before_snapshot = capture_mastery_snapshot_from_records(
            user=user,
            course_id=exam.course_id,
            answer_history_records=answer_history_records,
        )
        kt_analysis = refresh_exam_kt_analysis(
            user=user,
            exam=exam,
            answer_history_records=answer_history_records,
        )
        report, mastery_changes = build_submission_feedback_state(
            user=user,
            exam=exam,
            submission=submission,
            context=submission_context,
            kt_analysis=kt_analysis,
            mastery_before_snapshot=mastery_before_snapshot,
        )
        from .report_service import enqueue_feedback_report_on_commit
        enqueue_feedback_report_on_commit(report.id, force=True)

    return success_response(
        data={
            "submission_id": submission.id,
            "score": submission_context.score,
            "total_score": float(exam.total_score),
            "pass_score": submission_context.pass_threshold,
            "passed": submission_context.passed,
            "correct_count": submission_context.correct_count,
            "total_count": len(submission_context.questions),
            "accuracy": submission_context.accuracy,
            "question_details": submission_context.question_details,
            "mistakes": [
                {
                    "question_id": mistake["question_id"],
                    "correct_answer": mistake["correct_answer"],
                    "your_answer": mistake["student_answer"],
                    "analysis": mistake["analysis"],
                }
                for mistake in submission_context.grading["mistakes"]
            ],
            "mastery_changes": mastery_changes,
            "feedback_report": build_feedback_report_ref(report),
        },
        msg="作业提交成功",
    )


# 维护意图：获取考试结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_result(request, exam_id):
    """获取考试结果。"""
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)
    try:
        submission = ExamSubmission.objects.get(exam=exam, user=request.user)
    except ExamSubmission.DoesNotExist:
        return error_response(msg="您尚未完成该作业", code=404)

    snapshot = build_submission_feedback_snapshot(submission)
    display_score, passed = sync_result_submission_snapshot(submission, snapshot)

    return success_response(data={
        "exam_id": exam.id,
        "exam_title": exam.title,
        "score": display_score,
        "total_score": float(exam.total_score),
        "pass_score": resolve_pass_threshold(exam),
        "passed": passed,
        "submitted_at": submission.submitted_at.isoformat(),
        "correct_count": snapshot["correct_count"],
        "total_count": snapshot["total_count"],
        "accuracy": snapshot["accuracy"],
        "questions": snapshot["question_details"],
        "question_details": snapshot["question_details"],
    })


# 维护意图：保存考试草稿
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def exam_save_draft(request, exam_id):
    """保存考试草稿。"""
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)
    submission, _ = ExamSubmission.objects.update_or_create(exam=exam, user=request.user, defaults={"answers": request.data.get("answers", {}), "score": -1})
    return success_response(data={"submission_id": submission.id, "saved": True}, msg="草稿已保存")


# 维护意图：获取考试统计数据（学生视角）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_statistics(request, exam_id):
    """获取考试统计数据（学生视角）。"""
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)
    my_submission = ExamSubmission.objects.filter(exam=exam, user=request.user, score__gte=0).first()
    all_submissions = ExamSubmission.objects.filter(exam=exam, score__gte=0)
    average_score = all_submissions.aggregate(avg=models.Avg("score"))["avg"] or 0
    rank = all_submissions.filter(score__gt=my_submission.score).count() + 1 if my_submission else 0
    return success_response(data={
        "my_score": float(my_submission.score) if my_submission else None,
        "average_score": round(float(average_score), 1),
        "total_submissions": all_submissions.count(),
        "my_rank": rank,
    })
