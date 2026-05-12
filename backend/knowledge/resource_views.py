"""学生端知识资源与知识点搜索接口。"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.responses import error_response, success_response
from common.utils import resolve_course_id as _resolve_course_id
from .models import KnowledgePoint, Resource


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_student_resources(request):
    """获取课程学习资源列表（学生端）。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    queryset = Resource.objects.filter(course_id=course_id, is_visible=True)
    sort = request.query_params.get("sort", "default")
    if sort == "title":
        queryset = queryset.order_by("title", "id")
    elif sort == "type":
        queryset = queryset.order_by("resource_type", "title", "id")
    elif sort == "newest":
        queryset = queryset.order_by("-created_at", "-id")
    else:
        queryset = queryset.order_by("chapter_number", "sort_order", "resource_type", "title", "id")

    resource_type = request.query_params.get("type")
    keyword = request.query_params.get("keyword")
    point_id = request.query_params.get("point_id")
    if resource_type:
        queryset = queryset.filter(resource_type=resource_type)
    if keyword:
        queryset = queryset.filter(title__icontains=keyword)
    if point_id:
        queryset = queryset.filter(knowledge_points__id=point_id)

    try:
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
    except (ValueError, TypeError):
        page, page_size = 1, 20
    page = max(page, 1)
    page_size = max(1, min(page_size, 100))
    total = queryset.count()
    resources = queryset[(page - 1) * page_size : page * page_size]

    return success_response(data={
        "resources": [
            {
                "id": resource.id,
                "title": resource.title,
                "resource_type": resource.resource_type,
                "description": resource.description or "",
                "url": resource.url or "",
                "file": resource.file.url if resource.file else "",
                "duration": resource.duration,
                "chapter_number": resource.chapter_number or "",
                "sort_order": resource.sort_order,
                "knowledge_points": [
                    {"id": getattr(point, "id", None) or getattr(point, "pk", None), "name": getattr(point, "name", "")}
                    for point in resource.knowledge_points.all()
                ],
                "created_at": resource.created_at.isoformat() if resource.created_at else "",
            }
            for resource in resources.prefetch_related("knowledge_points")
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def knowledge_point_resources(request, point_id):
    """获取知识点相关资源。"""
    try:
        point = KnowledgePoint.objects.get(id=point_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    resources = Resource.objects.filter(knowledge_points=point, is_visible=True).order_by("sort_order")
    return success_response(data=[
        {
            "id": resource.id,
            "title": resource.title,
            "resource_type": resource.resource_type,
            "url": resource.url or "",
            "file": resource.file.url if resource.file else "",
            "duration": resource.duration,
        }
        for resource in resources
    ])


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def knowledge_search(request):
    """搜索知识点。"""
    keyword = request.query_params.get("keyword", "")
    course_id = request.query_params.get("course_id")
    if not keyword:
        return error_response(msg="请提供搜索关键字")

    queryset = KnowledgePoint.objects.filter(name__icontains=keyword)
    if course_id:
        queryset = queryset.filter(course_id=course_id)
    return success_response(data=[
        {
            "id": point.id,
            "name": point.name,
            "description": point.description or "",
            "course_id": point.course_id,
        }
        for point in queryset[:50]
    ])
