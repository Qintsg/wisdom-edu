"""教师课程工作台新视图。"""

from __future__ import annotations

from django.db import transaction
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from application.teacher.workspace import build_course_workspace
from common.permissions import IsTeacherOrAdmin
from common.responses import created_response, error_response, forbidden_response, success_response
from .models import Class, ClassCourse, Course


# 维护意图：返回教师课程工作台聚合数据
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def course_workspace(request, course_id: int):
    """返回教师课程工作台聚合数据。"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)

    if not course.can_edit(request.user) and request.user.role != "admin" and not request.user.is_superuser:
        return forbidden_response(msg="无权查看此课程工作台")

    return success_response(data=build_course_workspace(course, request.user))


# 维护意图：标准化班级创建，兼容 `name` 和 `class_name`
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_create(request):
    """标准化班级创建，兼容 `name` 和 `class_name`。"""
    name = (request.data.get("name") or request.data.get("class_name") or "").strip()
    description = request.data.get("description", "")
    semester = request.data.get("semester", "")
    course_id = request.data.get("course_id")

    if not name:
        return error_response(msg="班级名称不能为空")

    try:
        with transaction.atomic():
            class_obj = Class.objects.create(
                name=name,
                description=description,
                semester=semester,
                teacher=request.user,
            )
            if course_id:
                course = Course.objects.filter(id=course_id).first()
                if course:
                    class_obj.course = course
                    class_obj.save(update_fields=["course"])
                    ClassCourse.objects.get_or_create(
                        class_obj=class_obj,
                        course=course,
                        defaults={"published_by": request.user, "is_active": True},
                    )
            return created_response(
                data={
                    "class_id": getattr(class_obj, "id", None) or getattr(class_obj, "pk", None),
                    "name": class_obj.name,
                    "class_name": class_obj.name,
                },
                msg="班级创建成功",
            )
    except Exception as exc:
        return error_response(msg=f"创建失败: {exc}", code=500)


# 维护意图：标准化班级列表，支持按课程上下文筛选
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def my_classes(request):
    """标准化班级列表，支持按课程上下文筛选。"""
    course_id = request.query_params.get("course_id")
    classes = Class.objects.filter(teacher=request.user).order_by("-created_at")
    if course_id:
        classes = classes.filter(
            Q(course_id=course_id) | Q(class_courses__course_id=course_id, class_courses__is_active=True)
        ).distinct()

    return success_response(
        data={
            "classes": [
                {
                    "class_id": getattr(item, "id", None) or getattr(item, "pk", None),
                    "name": item.name,
                    "class_name": item.name,
                    "description": item.description or "",
                    "semester": item.semester or "",
                    "student_count": item.get_student_count(),
                    "is_active": item.is_active,
                    "course_id": getattr(item, "course_id", None),
                    "created_at": item.created_at.isoformat(),
                }
                for item in classes
            ]
        }
    )
