"""学生端考试答案、重考与下载视图。"""
from __future__ import annotations

import codecs
import csv

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from assessments.models import Question
from common.responses import error_response, success_response
from common.utils import check_answer, extract_answer_value

from .models import Exam, ExamQuestion, ExamSubmission


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_answer_sheet(request, exam_id):
    """查看标准答案。"""
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    submitted = ExamSubmission.objects.filter(exam=exam, user=request.user, score__gte=0).exists()
    if not submitted:
        return error_response(msg="请先完成作业再查看答案")

    questions = Question.objects.filter(id__in=ExamQuestion.objects.filter(exam=exam).values_list("question_id", flat=True))
    return success_response(data=[{
        "question_id": question.id,
        "content": question.content,
        "correct_answer": extract_answer_value(question.answer),
        "analysis": question.analysis or "",
    } for question in questions])


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def exam_retake(request, exam_id):
    """重新参加考试。"""
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    old_submissions = ExamSubmission.objects.filter(exam=exam, user=request.user)
    if not old_submissions.exists():
        return error_response(msg="您尚未完成此作业")
    old_submissions.delete()
    return success_response(msg="已重置，可以重新作答")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_download(request, exam_id):
    """下载考试答案报告。"""
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    submission = ExamSubmission.objects.filter(exam=exam, user=request.user, score__gte=0).first()
    if not submission:
        return error_response(msg="您尚未完成此作业")

    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="homework_{exam_id}_result.csv"'
    response.write(codecs.BOM_UTF8.decode("utf-8"))
    writer = csv.writer(response)
    writer.writerow(["题号", "题目", "您的答案", "正确答案", "是否正确"])

    questions = Question.objects.filter(id__in=ExamQuestion.objects.filter(exam=exam).values_list("question_id", flat=True))
    answers = submission.answers or {}
    for index, question in enumerate(questions, 1):
        my_answer = answers.get(str(question.id), "")
        correct_answer = extract_answer_value(question.answer)
        is_correct = check_answer(question.question_type, my_answer, question.answer)
        writer.writerow([index, question.content, my_answer, correct_answer, "✓" if is_correct else "✗"])
    return response
