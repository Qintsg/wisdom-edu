"""课程模块 - 管理端统计接口。"""

from __future__ import annotations

import csv
from datetime import timedelta

from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.utils import timezone as tz
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from assessments.models import AnswerHistory
from common.permissions import IsAdmin
from common.responses import success_response
from exams.models import Exam, ExamSubmission
from learning.models import NodeProgress
from logs.models import OperationLog
from users.models import User
from .models import Class, ClassCourse, Course, Enrollment


# 维护意图：管理端 - 获取系统统计概览
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_overview(_request):
    """管理端 - 获取系统统计概览。"""
    user_count = User.objects.filter(is_active=True).count()
    course_count = Course.objects.count()
    class_count = Class.objects.count()
    student_count = User.objects.filter(role='student', is_active=True).count()
    teacher_count = User.objects.filter(role='teacher', is_active=True).count()
    admin_count = User.objects.filter(role='admin', is_active=True).count()

    return success_response(data={
        'userCount': user_count,
        'courseCount': course_count,
        'classCount': class_count,
        'studentCount': student_count,
        'teacherCount': teacher_count,
        'onlineRate': '99.9%',
        'roleDistribution': {
            'student': student_count,
            'teacher': teacher_count,
            'admin': admin_count,
        },
    })


# 维护意图：用户增长趋势 / 活跃度统计
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_users(request):
    """用户增长趋势 / 活跃度统计。"""
    days = int(request.query_params.get('days', 30))
    since = tz.now() - timedelta(days=days)

    daily_reg = (
        User.objects.filter(date_joined__gte=since)
        .annotate(date=TruncDate('date_joined'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    role_dist = User.objects.values('role').annotate(count=Count('id'))

    return success_response(data={
        'total_users': User.objects.count(),
        'daily_registrations': list(daily_reg),
        'role_distribution': list(role_dist),
    })


# 维护意图：课程使用情况统计
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_courses(_request):
    """课程使用情况统计。"""
    top_courses = (
        ClassCourse.objects.values('course__name')
        .annotate(
            class_count=Count('class_obj', distinct=True),
            student_count=Count('class_obj__enrollments', distinct=True),
        )
        .order_by('-student_count')[:10]
    )

    return success_response(data={
        'total_courses': Course.objects.count(),
        'total_classes': Class.objects.count(),
        'total_enrollments': Enrollment.objects.count(),
        'top_courses': list(top_courses),
    })


# 维护意图：整体学习统计
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_learning(_request):
    """整体学习统计。"""
    total_records = NodeProgress.objects.count()
    total_answers = AnswerHistory.objects.count()
    correct_answers = AnswerHistory.objects.filter(is_correct=True).count()

    return success_response(data={
        'total_learning_records': total_records,
        'total_answers': total_answers,
        'correct_answers': correct_answers,
        'accuracy': round(correct_answers / total_answers * 100, 1) if total_answers > 0 else 0,
    })


# 维护意图：考试统计
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_exams(_request):
    """考试统计。"""
    total_exams = Exam.objects.count()
    total_submissions = ExamSubmission.objects.count()
    avg_score = ExamSubmission.objects.aggregate(avg=models.Avg('score'))['avg']

    return success_response(data={
        'total_exams': total_exams,
        'total_submissions': total_submissions,
        'average_score': round(float(avg_score), 1) if avg_score else 0,
    })


# 维护意图：活跃用户排行
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_active_users(request):
    """活跃用户排行。"""
    days = int(request.query_params.get('days', 7))
    since = tz.now() - timedelta(days=days)
    active = (
        OperationLog.objects.filter(created_at__gte=since, user__isnull=False)
        .values('user__id', 'user__username', 'user__real_name')
        .annotate(action_count=Count('id'))
        .order_by('-action_count')[:20]
    )

    return success_response(data={'active_users': list(active), 'days': days})


# 维护意图：系统运行综合报告
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_report(_request):
    """系统运行综合报告。"""
    return success_response(data={
        'users': {
            'total': User.objects.count(),
            'students': User.objects.filter(role='student').count(),
            'teachers': User.objects.filter(role='teacher').count(),
            'admins': User.objects.filter(role='admin').count(),
        },
        'courses': {
            'total': Course.objects.count(),
            'classes': Class.objects.count(),
            'enrollments': Enrollment.objects.count(),
        },
        'exams': {
            'total': Exam.objects.count(),
            'submissions': ExamSubmission.objects.count(),
        },
        'answers': {
            'total': AnswerHistory.objects.count(),
        },
        'logs': {
            'total_operations': OperationLog.objects.count(),
        },
    })


# 维护意图：导出统计数据为 CSV
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_export(_request):
    """导出统计数据为 CSV。"""
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="statistics.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['指标', '数值'])
    writer.writerow(['总用户数', User.objects.count()])
    writer.writerow(['学生数', User.objects.filter(role='student').count()])
    writer.writerow(['教师数', User.objects.filter(role='teacher').count()])
    writer.writerow(['课程数', Course.objects.count()])
    writer.writerow(['班级数', Class.objects.count()])
    writer.writerow(['选课人次', Enrollment.objects.count()])

    return response
