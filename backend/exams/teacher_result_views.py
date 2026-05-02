"""教师端考试结果、分析与导出视图。"""

import codecs
import csv

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, success_response

from .models import ExamSubmission, ExamQuestion
from .teacher_helpers import (
    _ensure_teacher_exam_access,
    _get_exam_or_404,
    _normalize_choice_answer_set,
    _parse_pagination,
)


UTF8_BOM = codecs.BOM_UTF8.decode('utf-8')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_results(request, exam_id):
    """获取考试成绩列表（教师端）。"""
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权查看此作业成绩',
    )
    if permission_error is not None:
        return permission_error

    page, size = _parse_pagination(request.query_params, size_key='size')

    submissions = ExamSubmission.objects.filter(exam=exam).select_related('user').order_by('-submitted_at')

    total = submissions.count()
    start = (page - 1) * size
    end = start + size
    submissions = submissions[start:end]

    results = [{
        'submission_id': submission.id,
        'user_id': submission.user.id,
        'username': submission.user.username,
        'real_name': submission.user.real_name or '',
        'score': float(submission.score),
        'is_passed': submission.is_passed,
        'submitted_at': submission.submitted_at.isoformat(),
    } for submission in submissions]

    return success_response(data={
        'exam_id': exam_id,
        'exam_title': exam.title,
        'total': total,
        'page': page,
        'size': size,
        'results': results,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_student_detail(request, exam_id, student_id):
    """获取学生考试详情（教师端）。"""
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权查看此作业',
    )
    if permission_error is not None:
        return permission_error

    try:
        submission = ExamSubmission.objects.get(exam=exam, user_id=student_id)
    except ExamSubmission.DoesNotExist:
        return error_response(msg='学生未提交作业', code=404)

    exam_questions = ExamQuestion.objects.filter(exam=exam).select_related('question')
    answers = submission.answers or {}

    question_details = []
    for exam_question in exam_questions.order_by('order'):
        question = exam_question.question
        student_answer = answers.get(str(question.id), '')
        correct_answer = question.answer.get('answer', question.answer) if isinstance(question.answer, dict) else question.answer

        if question.question_type in ['single_choice', 'true_false']:
            is_correct = student_answer == correct_answer
        elif question.question_type == 'multiple_choice':
            correct_set = _normalize_choice_answer_set(correct_answer)
            student_set = _normalize_choice_answer_set(student_answer)
            is_correct = correct_set == student_set
        else:
            is_correct = str(student_answer).strip().lower() == str(correct_answer).strip().lower()

        question_details.append({
            'question_id': question.id,
            'content': question.content,
            'question_type': question.question_type,
            'options': question.options,
            'correct_answer': correct_answer,
            'student_answer': student_answer,
            'is_correct': is_correct,
            'score': exam_question.score if is_correct else 0,
        })

    return success_response(data={
        'exam_id': exam_id,
        'exam_title': exam.title,
        'student': {
            'user_id': submission.user.id,
            'username': submission.user.username,
            'real_name': submission.user.real_name or '',
        },
        'score': float(submission.score),
        'is_passed': submission.is_passed,
        'submitted_at': submission.submitted_at.isoformat(),
        'questions': question_details,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def exam_analysis(request, exam_id):
    """获取考试统计分析（教师端）。"""
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权查看此作业',
    )
    if permission_error is not None:
        return permission_error

    submissions = ExamSubmission.objects.filter(exam=exam)

    total_submissions = submissions.count()
    if total_submissions == 0:
        return success_response(data={
            'exam_id': exam_id,
            'exam_title': exam.title,
            'total_submissions': 0,
            'message': '暂无提交记录',
        })

    passed_count = submissions.filter(is_passed=True).count()
    scores = list(submissions.values_list('score', flat=True))
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)

    score_distribution = {
        '0-59': 0,
        '60-69': 0,
        '70-79': 0,
        '80-89': 0,
        '90-100': 0,
    }
    for score in scores:
        if score < 60:
            score_distribution['0-59'] += 1
        elif score < 70:
            score_distribution['60-69'] += 1
        elif score < 80:
            score_distribution['70-79'] += 1
        elif score < 90:
            score_distribution['80-89'] += 1
        else:
            score_distribution['90-100'] += 1

    exam_questions = ExamQuestion.objects.filter(exam=exam).select_related('question')
    question_analysis = []

    for exam_question in exam_questions.order_by('order'):
        question = exam_question.question
        correct_count = 0
        correct_answer = question.answer.get('answer', question.answer) if isinstance(question.answer, dict) else question.answer
        for submission in submissions:
            answers = submission.answers or {}
            student_answer = answers.get(str(question.id))

            if question.question_type in ['single_choice', 'true_false']:
                if student_answer == correct_answer:
                    correct_count += 1
            elif question.question_type == 'multiple_choice':
                correct_set = _normalize_choice_answer_set(correct_answer)
                student_set = _normalize_choice_answer_set(student_answer)
                if correct_set == student_set:
                    correct_count += 1
            else:
                if student_answer is not None and str(student_answer).strip().lower() == str(correct_answer).strip().lower():
                    correct_count += 1

        accuracy = correct_count / total_submissions if total_submissions > 0 else 0
        question_analysis.append({
            'question_id': question.id,
            'content': question.content[:50] + '...' if len(question.content) > 50 else question.content,
            'accuracy': round(accuracy, 3),
            'correct_count': correct_count,
            'total_count': total_submissions,
        })

    return success_response(data={
        'exam_id': exam_id,
        'exam_title': exam.title,
        'statistics': {
            'total_submissions': total_submissions,
            'passed_count': passed_count,
            'pass_rate': round(passed_count / total_submissions, 3),
            'avg_score': round(float(avg_score), 2),
            'max_score': float(max_score),
            'min_score': float(min_score),
        },
        'score_distribution': score_distribution,
        'question_analysis': question_analysis,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_exam_export(request, exam_id):
    """导出考试成绩。"""
    exam, exam_error = _get_exam_or_404(exam_id)
    if exam_error is not None:
        return exam_error
    assert exam is not None

    permission_error = _ensure_teacher_exam_access(
        request.user,
        exam,
        deny_message='无权导出此作业成绩',
    )
    if permission_error is not None:
        return permission_error

    submissions = ExamSubmission.objects.filter(exam=exam, score__gte=0).select_related('user')

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="homework_{exam_id}_results.csv"'
    response.write(UTF8_BOM)

    writer = csv.writer(response)
    writer.writerow(['学生ID', '用户名', '姓名', '成绩', '提交时间'])

    for submission in submissions:
        writer.writerow([
            submission.user.id,
            submission.user.username,
            submission.user.real_name or '',
            float(submission.score),
            submission.submitted_at.strftime('%Y-%m-%d %H:%M:%S') if submission.submitted_at else '',
        ])

    return response


__all__ = [
    'UTF8_BOM',
    'exam_analysis',
    'exam_results',
    'exam_student_detail',
    'teacher_exam_export',
]
