"""学生端考试列表与详情视图。"""
from __future__ import annotations

from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.responses import error_response, success_response
from common.utils import safe_int

from .models import Exam, ExamQuestion, ExamSubmission
from .student_helpers import build_exam_score_map, resolve_pass_threshold


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_list(request):
    """获取考试列表。"""
    course_id = request.query_params.get("course_id")
    exam_type = request.query_params.get("type")
    page = max(1, safe_int(request.query_params.get("page"), 1))
    size = min(max(1, safe_int(request.query_params.get("size"), 20)), 100)
    user = request.user
    exams = Exam.objects.filter(status="published")

    if course_id:
        exams = exams.filter(course_id=course_id)
    if exam_type:
        exams = exams.filter(exam_type=exam_type)

    if user.role == "student":
        now = timezone.now()
        exams = exams.filter(Q(start_time__lte=now) | Q(start_time__isnull=True))
        from courses.models import Enrollment
        enrolled_class_infos = (
            Enrollment.objects.filter(user=user).select_related("class_obj").values("class_obj_id", "class_obj__class_courses__course_id")
        )
        enrolled_class_ids = {item["class_obj_id"] for item in enrolled_class_infos}
        enrolled_course_ids = {item["class_obj__class_courses__course_id"] for item in enrolled_class_infos if item["class_obj__class_courses__course_id"]}
        if not course_id:
            exams = exams.filter(course_id__in=enrolled_course_ids)
        exams = exams.filter(Q(target_class_id__in=enrolled_class_ids) | Q(target_class__isnull=True))
    elif user.role == "teacher":
        exams = exams.filter(created_by=user)

    total = exams.count()
    exams = exams[(page - 1) * size : page * size]
    submissions = {submission.exam_id: submission for submission in ExamSubmission.objects.filter(user=user, exam__in=exams)}
    exam_list_data = []
    for exam in exams:
        submission = submissions.get(exam.id)
        submission_score = float(submission.score) if submission and submission.score is not None else None
        is_submitted = submission_score is not None and submission_score >= 0
        passed = submission_score >= resolve_pass_threshold(exam) if is_submitted else None
        exam_list_data.append({
            "exam_id": exam.id,
            "title": exam.title,
            "type": exam.exam_type,
            "status": exam.status,
            "total_score": float(exam.total_score),
            "duration": exam.duration,
            "start_time": exam.start_time.isoformat() if exam.start_time else None,
            "end_time": exam.end_time.isoformat() if exam.end_time else None,
            "created_at": exam.created_at.isoformat() if exam.created_at else None,
            "submitted": is_submitted,
            "score": submission_score if is_submitted else None,
            "passed": passed,
            "submitted_at": submission.submitted_at.isoformat() if submission and submission.submitted_at else None,
        })
    return success_response(data={"total": total, "exams": exam_list_data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_detail(request, exam_id):
    """获取考试详情（含题目，不含答案）。"""
    try:
        exam = Exam.objects.get(id=exam_id, status="published")
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    if request.user.role == "student":
        now = timezone.now()
        if exam.start_time and exam.start_time > now:
            return error_response(msg="作业尚未开始", code=403)
        if exam.end_time and exam.end_time < now:
            return error_response(msg="作业已结束", code=403)

    exam_questions = ExamQuestion.objects.filter(exam=exam).select_related("question").order_by("order")
    score_map = build_exam_score_map(exam, exam_questions)
    questions = [{
        "question_id": exam_question.question.id,
        "content": exam_question.question.content,
        "options": exam_question.question.options,
        "type": exam_question.question.question_type,
        "score": score_map.get(str(exam_question.question.id), 0),
    } for exam_question in exam_questions]

    return success_response(data={
        "exam_id": exam.id,
        "title": exam.title,
        "description": exam.description,
        "total_score": float(exam.total_score),
        "pass_score": resolve_pass_threshold(exam),
        "duration": exam.duration,
        "questions": questions,
    })
