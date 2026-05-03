"""
用户模块 - 学生画像接口

包含：画像查看、习惯偏好更新、画像刷新、历史对比、导出
"""

from __future__ import annotations

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.responses import error_response, success_response
from knowledge.models import ProfileSummary
from .models import HabitPreference
from .serializers import HabitPreferenceSerializer
from .student_profile_support import (
    build_profile_export_response,
    build_profile_history_payload,
    build_profile_refresh_payload,
    build_student_profile_payload,
    parse_profile_history_limit,
    snapshot_profile_summary,
)


# 维护意图：获取学习者画像 GET /api/profile
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request: Request) -> Response:
    """
    获取学习者画像
    GET /api/profile
    """
    return success_response(
        data=build_student_profile_payload(
            user=request.user,
            course_id=request.query_params.get('course_id'),
        )
    )


# 维护意图：更新学习习惯偏好 PUT /api/profile/habit
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_habit_preference(request: Request) -> Response:
    """
    更新学习习惯偏好
    PUT /api/profile/habit
    """
    habit_preference, _ = HabitPreference.objects.get_or_create(user=request.user)
    serializer = HabitPreferenceSerializer(habit_preference, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return success_response(
            data=serializer.data,
            msg='学习偏好已更新',
        )
    return error_response(msg=str(serializer.errors), code=400)


# 维护意图：手动更新学生画像（主动刷新） PUT /api/student/profile/update 调用KT服务细化掌握度 + LLM服务生成AI画像分析 请求参数： - course_id: 课程。
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_student_profile(request: Request) -> Response:
    """
    手动更新学生画像（主动刷新）
    PUT /api/student/profile/update

    调用KT服务细化掌握度 + LLM服务生成AI画像分析

    请求参数：
    - course_id: 课程ID（必填）
    """
    course_id = request.data.get('course_id')
    if not course_id:
        return error_response(msg='缺少课程ID', code=400)

    payload, error = build_profile_refresh_payload(request.user, course_id)
    if error:
        return error_response(
            msg=f'画像刷新失败: {error}',
            code=500,
        )
    return success_response(data=payload, msg='画像刷新成功（已调用AI分析）')


# 维护意图：获取画像历史（趋势对比） GET /api/profile/history 查询参数： - course_id: 课程ID（必填） - limit: 返回记录数（默认10）
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_history(request: Request) -> Response:
    """
    获取画像历史（趋势对比）
    GET /api/profile/history

    查询参数：
    - course_id: 课程ID（必填）
    - limit: 返回记录数（默认10）
    """
    course_id = request.query_params.get('course_id')
    if not course_id:
        return error_response(msg='缺少课程ID', code=400)

    return success_response(data={
        'course_id': course_id,
        'history': build_profile_history_payload(
            request.user,
            course_id,
            parse_profile_history_limit(request.query_params.get('limit', 10)),
        ),
    })


# 维护意图：对比不同时间的学习画像 GET /api/student/profile/compare 查询参数： - date1: 第一个时间点 (YYYY-MM-DD) - date2: 第二个时间点。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_compare(request: Request) -> Response:
    """
    对比不同时间的学习画像
    GET /api/student/profile/compare

    查询参数：
    - date1: 第一个时间点 (YYYY-MM-DD)
    - date2: 第二个时间点 (YYYY-MM-DD)
    """
    date1 = request.query_params.get('date1')
    date2 = request.query_params.get('date2')
    if not date1 or not date2:
        return error_response(msg='请提供两个比较日期', code=400)

    history = ProfileSummary.objects.filter(user=request.user).order_by('generated_at')
    snapshot1 = history.filter(generated_at__date__lte=date1).last()
    snapshot2 = history.filter(generated_at__date__lte=date2).last()
    return success_response(
        data={
            'date1': date1,
            'date2': date2,
            'snapshot1': snapshot_profile_summary(snapshot1),
            'snapshot2': snapshot_profile_summary(snapshot2),
        }
    )


# 维护意图：导出学习画像为 JSON（简版，PDF 需集成额外库） POST /api/student/profile/export
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def profile_export(request: Request) -> HttpResponse:
    """
    导出学习画像为 JSON（简版，PDF 需集成额外库）
    POST /api/student/profile/export
    """
    return build_profile_export_response(request.user)
