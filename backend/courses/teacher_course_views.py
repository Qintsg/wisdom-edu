"""教师端课程 CRUD、封面、统计和配置视图。"""

from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.permissions import IsTeacherOrAdmin
from common.responses import created_response, error_response, forbidden_response, success_response
from .teacher_course_support import (
    build_course_detail_payload,
    build_course_search_payload,
    build_course_settings_for_user,
    build_course_statistics_for_user,
    build_my_created_courses_payload,
    create_teacher_course,
    delete_teacher_course,
    get_teacher_course,
    update_teacher_course,
    update_course_settings_for_user,
    upload_teacher_course_cover,
)


# 维护意图：搜索公开课程
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def course_search(request: Request) -> Response:
    """搜索公开课程。"""
    return success_response(data=build_course_search_payload(request.query_params))


# 维护意图：统一教师课程接口错误响应，避免各端点重复权限分支
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def teacher_course_error_response(error_message: str, status_code: int) -> Response:
    """统一教师课程接口错误响应，避免各端点重复权限分支。"""
    if status_code == 403:
        return forbidden_response(msg=error_message)
    return error_response(msg=error_message, code=status_code)


# 维护意图：创建课程
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def course_create(request: Request) -> Response:
    """创建课程。"""
    payload, error_message, status_code = create_teacher_course(request.data, request.FILES, request.user)
    if error_message:
        return teacher_course_error_response(error_message, status_code)
    return created_response(data=payload, msg="课程创建成功")


# 维护意图：获取或更新课程
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def course_update(request: Request, course_id: int) -> Response:
    """获取或更新课程。"""
    course = get_teacher_course(course_id)
    if course is None:
        return error_response(msg="课程不存在", code=404)
    if request.method == "GET":
        return success_response(data=build_course_detail_payload(course))
    if not course.can_edit(request.user):
        return forbidden_response(msg="无权编辑此课程")

    payload = update_teacher_course(course, request.data)
    return success_response(data=payload, msg="课程更新成功")


# 维护意图：获取我创建的课程
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def my_created_courses(request: Request) -> Response:
    """获取我创建的课程。"""
    return success_response(data=build_my_created_courses_payload(request.user))


# 维护意图：教师端删除课程
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def course_delete(request: Request, course_id: int) -> Response:
    """教师端删除课程。"""
    success_message, error_message, status_code = delete_teacher_course(course_id, request.user)
    if error_message:
        return teacher_course_error_response(error_message, status_code)
    return success_response(msg=success_message)


# 维护意图：上传课程封面图
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_course_cover_upload(request: Request, course_id: int) -> Response:
    """上传课程封面图。"""
    payload, error_message, status_code = upload_teacher_course_cover(course_id, request.FILES, request.user)
    if error_message:
        return teacher_course_error_response(error_message, status_code)
    return success_response(data=payload, msg="封面上传成功")


# 维护意图：获取课程统计数据
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_course_statistics(request: Request, course_id: int) -> Response:
    """获取课程统计数据。"""
    payload, error_message, status_code = build_course_statistics_for_user(course_id, request.user)
    if error_message:
        return teacher_course_error_response(error_message, status_code)
    return success_response(data=payload)


# 维护意图：获取课程配置
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def get_course_settings(request: Request, course_id: int) -> Response:
    """获取课程配置。"""
    payload, error_message, status_code = build_course_settings_for_user(course_id, request.user)
    if error_message:
        return teacher_course_error_response(error_message, status_code)
    return success_response(data=payload)


# 维护意图：更新课程配置
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def update_course_settings(request: Request, course_id: int) -> Response:
    """更新课程配置。"""
    payload, error_message, status_code = update_course_settings_for_user(
        course_id,
        request.user,
        request.data.get("config", {}),
    )
    if error_message:
        return teacher_course_error_response(error_message, status_code)
    return success_response(data=payload, msg="课程配置已更新")
