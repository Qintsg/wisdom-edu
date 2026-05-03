"""教师端资源库管理视图。"""
from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, success_response
from common.utils import resolve_course_id as _resolve_course_id
from .models import Resource
from .teacher_helpers import (
    bad_request,
    link_knowledge_points,
    parse_pagination,
    refresh_course_rag_index,
    require_point_ids,
)
from .teacher_resource_support import (
    create_resource_from_payload,
    filtered_teacher_resources,
    parse_resource_write_payload,
    resource_create_result,
    resource_detail_payload,
    resource_list_payload,
    update_resource_from_payload,
)


# 维护意图：获取资源列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_list(request: Request) -> Response:
    """获取资源列表。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    page, size = parse_pagination(request)
    resources = filtered_teacher_resources(course_id, request.query_params)
    total = resources.count()
    start = (page - 1) * size
    return success_response(data={
        "total": total,
        "resources": [
            resource_list_payload(resource)
            for resource in resources[start : start + size]
        ],
    })


# 维护意图：上传或创建资源
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_create(request: Request) -> Response:
    """上传或创建资源。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    payload = parse_resource_write_payload(request.data, partial=False)
    if not payload.title or not payload.resource_type:
        return bad_request("缺少必要参数")

    resource = create_resource_from_payload(
        course_id=course_id,
        payload=payload,
        file=request.FILES.get("file"),
        user=request.user,
    )
    refresh_course_rag_index(course_id)
    return success_response(
        data=resource_create_result(resource),
        msg="资源创建成功",
    )


# 维护意图：获取或更新资源
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_update(request: Request, resource_id: int) -> Response:
    """获取或更新资源。"""
    try:
        resource = Resource.objects.get(id=resource_id)
    except Resource.DoesNotExist:
        return error_response(msg="资源不存在", code=404)

    if request.method == "GET":
        return success_response(data=resource_detail_payload(resource))

    update_resource_from_payload(
        resource,
        parse_resource_write_payload(request.data, partial=True),
    )
    refresh_course_rag_index(resource.course_id)
    return success_response(
        data={"resource_id": getattr(resource, "id", None) or getattr(resource, "pk", None)},
        msg="资源更新成功",
    )


# 维护意图：删除资源
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_delete(request: Request, resource_id: int) -> Response:
    """删除资源。"""
    try:
        resource = Resource.objects.get(id=resource_id)
        course_id = resource.course_id
        resource.delete()
        refresh_course_rag_index(course_id)
        return success_response(msg="资源删除成功")
    except Resource.DoesNotExist:
        return error_response(msg="资源不存在", code=404)


# 维护意图：上传资源文件
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_upload(request: Request) -> Response:
    """上传资源文件。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return bad_request("请上传文件")

    resource = Resource.objects.create(
        course_id=course_id,
        title=request.data.get("title", uploaded_file.name),
        resource_type=request.data.get("resource_type", "document"),
        description=request.data.get("description", ""),
        file=uploaded_file,
        uploaded_by=request.user,
    )
    return success_response(
        data={"id": resource.id, "title": resource.title, "file": resource.file.url if resource.file else ""},
        msg="资源上传成功",
    )


# 维护意图：资源关联知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_link_knowledge(request: Request, resource_id: int) -> Response:
    """资源关联知识点。"""
    try:
        resource = Resource.objects.get(id=resource_id)
    except Resource.DoesNotExist:
        return error_response(msg="资源不存在", code=404)

    point_ids, err = require_point_ids(request)
    if err:
        return err

    linked_count = link_knowledge_points(resource, point_ids)
    return success_response(msg=f"已关联 {linked_count} 个知识点")
