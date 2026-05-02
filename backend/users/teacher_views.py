"""
用户模块 - 教师接口

包含：教师查看学生画像详情、教师刷新学生画像
"""
from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.responses import success_response, error_response, forbidden_response
from .teacher_profile_support import (
    build_profile_refresh_payload,
    build_student_profile_payload,
    ensure_teacher_can_view_student,
    resolve_profile_course_id,
    resolve_student_for_teacher_profile,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_student_profile_detail(request, user_id):
    """
    获取单个学生的详细画像（教师/管理员）
    GET /api/teacher/students/{user_id}/profile
    
    查询参数：
    - course_id: 课程ID（可选，缺省时自动获取学生第一个课程）
    """
    user = request.user

    if user.role not in ['teacher', 'admin']:
        return forbidden_response(msg='无权查看学生画像')

    student, student_error = resolve_student_for_teacher_profile(user_id)
    if student_error is not None:
        return student_error

    course_id, course_error = resolve_profile_course_id(
        student,
        request.query_params.get('course_id'),
    )
    if course_error is not None:
        return course_error

    permission_error = ensure_teacher_can_view_student(user, student, course_id)
    if permission_error is not None:
        return permission_error

    return success_response(data=build_student_profile_payload(student, course_id))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def teacher_refresh_student_profile(request, user_id):
    """
    教师主动刷新学生画像（调用KT+LLM服务）
    POST /api/teacher/students/{user_id}/refresh-profile
    """
    user = request.user
    if user.role not in ['teacher', 'admin']:
        return forbidden_response(msg='无权操作')

    course_id = request.data.get('course_id')
    if not course_id:
        return error_response(msg='缺少课程ID')

    student, student_error = resolve_student_for_teacher_profile(user_id)
    if student_error is not None:
        return student_error

    payload, refresh_error = build_profile_refresh_payload(student, course_id)
    if refresh_error is not None:
        return refresh_error

    return success_response(data=payload, msg='学生画像已刷新')
