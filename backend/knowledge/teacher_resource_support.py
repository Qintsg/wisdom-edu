"""教师端资源库视图支持逻辑。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import cast

from application.teacher.contracts import first_present
from .models import KnowledgePoint, Resource
from .teacher_helpers import KnowledgePointRelationSetter, replace_knowledge_points


# 维护意图：资源创建或更新的标准化输入
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class ResourceWritePayload:
    """资源创建或更新的标准化输入。"""

    title: object
    resource_type: object
    url: object
    points: object
    duration: int | None
    chapter_number: object
    sort_order: int | None
    description: object
    is_visible: object | None = None


# 维护意图：按课程和查询参数过滤资源
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def filtered_teacher_resources(course_id: object, query_params: object):
    """按课程和查询参数过滤资源。"""
    resources = Resource.objects.filter(course_id=course_id).prefetch_related("knowledge_points").order_by("sort_order", "id")
    resource_type = query_params.get("type")
    keyword = query_params.get("keyword") or query_params.get("title", "")
    point_id = query_params.get("point_id")
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    if keyword:
        resources = resources.filter(title__icontains=keyword)
    if point_id:
        resources = resources.filter(knowledge_points__id=point_id)
    return resources


# 维护意图：序列化资源列表项
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def resource_list_payload(resource: Resource) -> dict[str, object]:
    """序列化资源列表项。"""
    file_url, file_format = resource_file_display(resource)
    knowledge_points = cast(list[KnowledgePoint], list(resource.knowledge_points.all()))
    first_point = knowledge_points[0] if knowledge_points else None
    return {
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
        "duration_display": resource_duration_display(resource.duration),
        "chapter_number": resource.chapter_number,
        "sort_order": resource.sort_order,
    }


# 维护意图：安全读取资源文件 URL 和格式
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def resource_file_display(resource: Resource) -> tuple[str | None, str]:
    """安全读取资源文件 URL 和格式。"""
    try:
        if not resource.file:
            return None, ""
        file_url = resource.file.url
        file_name = getattr(resource.file, "name", "") or ""
        return file_url, file_name.split(".")[-1] if "." in file_name else ""
    except (ValueError, AttributeError):
        return None, ""


# 维护意图：格式化资源时长
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def resource_duration_display(duration: int | None) -> str | None:
    """格式化资源时长。"""
    if not duration:
        return None
    return f"{duration // 60:02d}:{duration % 60:02d}"


# 维护意图：序列化资源详情
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def resource_detail_payload(resource: Resource) -> dict[str, object]:
    """序列化资源详情。"""
    return {
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
    }


# 维护意图：解析资源创建或更新字段
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_resource_write_payload(data: object, *, partial: bool) -> ResourceWritePayload:
    """解析资源创建或更新字段。"""
    default_sort = data.get("sort_order") if partial else data.get("sort_order", 0)
    return ResourceWritePayload(
        title=first_present(data, "title", "resource_name"),
        resource_type=first_present(data, "type", "resource_type"),
        url=first_present(data, "url", "resource_url"),
        points=parse_resource_points(data),
        duration=parse_optional_int(data.get("duration")),
        chapter_number=data.get("chapter_number"),
        sort_order=parse_optional_int(default_sort),
        description=data.get("description", "" if not partial else None),
        is_visible=first_present(data, "visible", "is_visible") if partial else None,
    )


# 维护意图：解析 points / knowledge_point_ids / point_id 入参
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_resource_points(data: object) -> object:
    """解析 points / knowledge_point_ids / point_id 入参。"""
    points = data.get("points", data.get("knowledge_point_ids", []))
    point_id = data.get("point_id") or data.get("knowledge_point_id")
    if isinstance(points, str):
        try:
            points = json.loads(points)
        except json.JSONDecodeError:
            points = []
    if not points and point_id:
        return [point_id]
    return points


# 维护意图：解析可选整数
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_optional_int(value: object) -> int | None:
    """解析可选整数。"""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


# 维护意图：创建资源并按需关联知识点
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def create_resource_from_payload(
    *,
    course_id: object,
    payload: ResourceWritePayload,
    file: object,
    user: object,
) -> Resource:
    """创建资源并按需关联知识点。"""
    resource = Resource.objects.create(
        course_id=course_id,
        title=payload.title,
        resource_type=payload.resource_type,
        url=payload.url,
        file=file,
        description=payload.description,
        duration=payload.duration,
        chapter_number=payload.chapter_number if payload.chapter_number else None,
        sort_order=payload.sort_order or 0,
        uploaded_by=user,
    )
    replace_resource_points(resource, payload.points)
    return resource


# 维护意图：按部分字段更新资源
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_resource_from_payload(resource: Resource, payload: ResourceWritePayload) -> None:
    """按部分字段更新资源。"""
    if payload.title:
        resource.title = payload.title
    if payload.resource_type:
        resource.resource_type = payload.resource_type
    if payload.url:
        resource.url = payload.url
    if payload.is_visible is not None:
        resource.is_visible = payload.is_visible
    if payload.description is not None:
        resource.description = payload.description
    if payload.duration is not None:
        resource.duration = payload.duration
    if payload.chapter_number is not None:
        resource.chapter_number = payload.chapter_number
    if payload.sort_order is not None:
        resource.sort_order = payload.sort_order
    resource.save()
    replace_resource_points(resource, payload.points)


# 维护意图：替换资源知识点关联
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def replace_resource_points(resource: Resource, points: object) -> None:
    """替换资源知识点关联。"""
    if points:
        replace_knowledge_points(cast(KnowledgePointRelationSetter, resource.knowledge_points), points)


# 维护意图：构造创建成功响应
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def resource_create_result(resource: Resource) -> dict[str, object]:
    """构造创建成功响应。"""
    return {
        "resource_id": getattr(resource, "id", None) or getattr(resource, "pk", None),
        "title": resource.title,
        "url": resource.url or (resource.file.url if resource.file else None),
    }
