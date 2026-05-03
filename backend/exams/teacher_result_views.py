"""教师端考试结果、分析与导出视图。"""

import codecs
import csv

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, success_response

from .models import ExamSubmission, ExamQuestion
from .teacher_result_support import (
    build_question_analysis,
    build_score_distribution,
    build_submission_result,
    build_teacher_question_detail,
)
from .teacher_helpers import (
    _ensure_teacher_exam_access,
    _get_exam_or_404,
    _parse_pagination,
)


UTF8_BOM = codecs.BOM_UTF8.decode('utf-8')


# 维护意图：获取考试成绩列表（教师端）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    results = [build_submission_result(submission) for submission in submissions]

    return success_response(data={
        'exam_id': exam_id,
        'exam_title': exam.title,
        'total': total,
        'page': page,
        'size': size,
        'results': results,
    })


# 维护意图：获取学生考试详情（教师端）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    question_details = [
        build_teacher_question_detail(exam_question, answers)
        for exam_question in exam_questions.order_by('order')
    ]

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


# 维护意图：获取考试统计分析（教师端）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    score_distribution = build_score_distribution(scores)

    exam_questions = ExamQuestion.objects.filter(exam=exam).select_related('question')
    question_analysis = build_question_analysis(exam_questions, list(submissions))

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


# 维护意图：导出考试成绩
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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
