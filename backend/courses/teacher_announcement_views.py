"""教师端班级公告管理视图。"""
from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsTeacherOrAdmin
from common.responses import created_response, error_response, forbidden_response, success_response

from .models import Announcement, Class


# 维护意图：班级公告列表 / 创建公告
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_announcements(request, class_id):
    """班级公告列表 / 创建公告。"""
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    if class_obj.teacher != request.user:
        return forbidden_response(msg="无权操作该班级")

    if request.method == "GET":
        announcements = Announcement.objects.filter(class_obj=class_obj)
        return success_response(data={"announcements": [{
            "id": announcement.id,
            "title": announcement.title,
            "content": announcement.content,
            "created_by": announcement.created_by.username if announcement.created_by else None,
            "created_at": announcement.created_at.strftime("%Y-%m-%d %H:%M") if announcement.created_at else None,
            "updated_at": announcement.updated_at.strftime("%Y-%m-%d %H:%M") if announcement.updated_at else None,
        } for announcement in announcements]})

    title = request.data.get("title", "").strip()
    content = request.data.get("content", "").strip()
    if not title:
        return error_response(msg="公告标题不能为空", code=400)
    if not content:
        return error_response(msg="公告内容不能为空", code=400)
    announcement = Announcement.objects.create(class_obj=class_obj, title=title, content=content, created_by=request.user)
    return created_response(data={"id": announcement.id, "title": announcement.title, "content": announcement.content, "created_at": announcement.created_at.strftime("%Y-%m-%d %H:%M")}, msg="公告发布成功")


# 维护意图：编辑 / 删除公告
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def announcement_detail(request, announcement_id):
    """编辑 / 删除公告。"""
    try:
        announcement = Announcement.objects.select_related("class_obj").get(id=announcement_id)
    except Announcement.DoesNotExist:
        return error_response(msg="公告不存在", code=404)
    if announcement.class_obj.teacher != request.user:
        return forbidden_response(msg="无权操作该公告")

    if request.method == "DELETE":
        announcement.delete()
        return success_response(msg="公告已删除")

    title = request.data.get("title", "").strip()
    content = request.data.get("content", "").strip()
    if title:
        announcement.title = title
    if content:
        announcement.content = content
    announcement.save()
    return success_response(data={"id": announcement.id, "title": announcement.title, "content": announcement.content, "updated_at": announcement.updated_at.strftime("%Y-%m-%d %H:%M")}, msg="公告已更新")
