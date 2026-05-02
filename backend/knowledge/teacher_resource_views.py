"""教师端资源库管理视图。"""
from __future__ import annotations

import json
from typing import cast

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from application.teacher.contracts import first_present
from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, success_response
from common.utils import resolve_course_id as _resolve_course_id

from .models import KnowledgePoint, Resource
from .teacher_helpers import (
    KnowledgePointRelationSetter,
    bad_request,
    link_knowledge_points,
    parse_pagination,
    refresh_course_rag_index,
    replace_knowledge_points,
    require_point_ids,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_list(request: Request) -> Response:
    """获取资源列表。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    resource_type = request.query_params.get("type")
    keyword = request.query_params.get("keyword") or request.query_params.get("title", "")
    point_id = request.query_params.get("point_id")
    page, size = parse_pagination(request)

    resources = Resource.objects.filter(course_id=course_id).prefetch_related("knowledge_points").order_by("sort_order", "id")
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    if keyword:
        resources = resources.filter(title__icontains=keyword)
    if point_id:
        resources = resources.filter(knowledge_points__id=point_id)

    total = resources.count()
    start = (page - 1) * size
    data = []
    for resource in resources[start : start + size]:
        file_url = None
        file_format = ""
        try:
            if resource.file:
                file_url = resource.file.url
                file_name = getattr(resource.file, "name", "") or ""
                file_format = file_name.split(".")[-1] if "." in file_name else ""
        except (ValueError, AttributeError):
            pass

        knowledge_points = cast(list[KnowledgePoint], list(resource.knowledge_points.all()))
        first_point = knowledge_points[0] if knowledge_points else None
        data.append({
            "resource_id": getattr(resource, "id", None) or getattr(resource, "pk", None),
            "title": resource.title,
            "type": resource.resource_type,
            "url": resource.url or file_url,
            "format": file_format,
            "point_id": first_point.id if first_point else None,
            "point_name": ", ".join(point.name for point in knowledge_points) if knowledge_points else "",
            "points": [{"id": point.id, "name": point.name} for point in knowledge_points],
            "description": getattr(resource, "description", "") or "",
            "visible": resource.is_visible,
            "created_at": resource.created_at.isoformat(),
            "duration": resource.duration,
            "duration_display": f"{resource.duration // 60:02d}:{resource.duration % 60:02d}" if resource.duration else None,
            "chapter_number": resource.chapter_number,
            "sort_order": resource.sort_order,
        })

    return success_response(data={"total": total, "resources": data})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_create(request: Request) -> Response:
    """上传或创建资源。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    title = first_present(request.data, "title", "resource_name")
    resource_type = first_present(request.data, "type", "resource_type")
    url = first_present(request.data, "url", "resource_url")
    file = request.FILES.get("file")
    points = request.data.get("points", request.data.get("knowledge_point_ids", []))
    point_id = request.data.get("point_id") or request.data.get("knowledge_point_id")
    duration = request.data.get("duration")
    chapter_number = request.data.get("chapter_number")
    sort_order = request.data.get("sort_order", 0)
    description = request.data.get("description", "")

    if not title or not resource_type:
        return bad_request("缺少必要参数")

    if isinstance(points, str):
        try:
            points = json.loads(points)
        except json.JSONDecodeError:
            points = []
    if not points and point_id:
        points = [point_id]

    duration_val = None
    if duration is not None:
        try:
            duration_val = int(duration)
        except (ValueError, TypeError):
            pass

    sort_order_val = 0
    if sort_order:
        try:
            sort_order_val = int(sort_order)
        except (ValueError, TypeError):
            sort_order_val = 0

    resource = Resource.objects.create(
        course_id=course_id,
        title=title,
        resource_type=resource_type,
        url=url,
        file=file,
        description=description,
        duration=duration_val,
        chapter_number=chapter_number if chapter_number else None,
        sort_order=sort_order_val,
        uploaded_by=request.user,
    )
    if points:
        replace_knowledge_points(cast(KnowledgePointRelationSetter, resource.knowledge_points), points)

    refresh_course_rag_index(course_id)
    return success_response(
        data={
            "resource_id": getattr(resource, "id", None) or getattr(resource, "pk", None),
            "title": resource.title,
            "url": resource.url or (resource.file.url if resource.file else None),
        },
        msg="资源创建成功",
    )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_update(request: Request, resource_id: int) -> Response:
    """获取或更新资源。"""
    try:
        resource = Resource.objects.get(id=resource_id)
    except Resource.DoesNotExist:
        return error_response(msg="资源不存在", code=404)

    if request.method == "GET":
        return success_response(data={
            "resource_id": resource.id,
            "title": resource.title,
            "type": resource.resource_type,
            "url": resource.url or "",
            "file": resource.file.url if resource.file else None,
            "description": resource.description or "",
            "duration": resource.duration,
            "chapter_number": resource.chapter_number or "",
            "sort_order": resource.sort_order,
            "is_visible": resource.is_visible,
            "knowledge_points": list(resource.knowledge_points.values_list("id", flat=True)),
            "course_id": resource.course_id,
        })

    title = first_present(request.data, "title", "resource_name")
    resource_type = first_present(request.data, "type", "resource_type")
    url = first_present(request.data, "url", "resource_url")
    points = request.data.get("points", request.data.get("knowledge_point_ids", []))
    point_id = request.data.get("point_id") or request.data.get("knowledge_point_id")
    is_visible = first_present(request.data, "visible", "is_visible")
    duration = request.data.get("duration")
    chapter_number = request.data.get("chapter_number")
    sort_order = request.data.get("sort_order")
    description = request.data.get("description")

    if title:
        resource.title = title
    if resource_type:
        resource.resource_type = resource_type
    if url:
        resource.url = url
    if is_visible is not None:
        resource.is_visible = is_visible
    if description is not None:
        resource.description = description
    if duration is not None:
        try:
            resource.duration = int(duration)
        except (ValueError, TypeError):
            pass
    if chapter_number is not None:
        resource.chapter_number = chapter_number
    if sort_order is not None:
        try:
            resource.sort_order = int(sort_order)
        except (ValueError, TypeError):
            pass

    resource.save()
    if isinstance(points, str):
        try:
            points = json.loads(points)
        except json.JSONDecodeError:
            points = []
    if not points and point_id:
        points = [point_id]
    if points:
        replace_knowledge_points(cast(KnowledgePointRelationSetter, resource.knowledge_points), points)

    refresh_course_rag_index(resource.course_id)
    return success_response(data={"resource_id": getattr(resource, "id", None) or getattr(resource, "pk", None)}, msg="资源更新成功")


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
