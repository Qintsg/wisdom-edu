"""教师端班级与课程发布管理视图。"""
from __future__ import annotations

from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from application.teacher.contracts import normalize_class_payload
from common.permissions import IsTeacherOrAdmin
from common.responses import created_response, error_response, forbidden_response, success_response

from .models import Class, ClassCourse, Course, Enrollment


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_create(request):
    """创建班级。"""
    payload = normalize_class_payload(request.data)
    name = payload["name"]
    if not name:
        return error_response(msg="班级名称不能为空", code=400)
    try:
        with transaction.atomic():
            class_obj = Class.objects.create(name=name, description=payload["description"], semester=payload["semester"], teacher=request.user)
            if payload["course_id"]:
                try:
                    course = Course.objects.get(id=payload["course_id"])
                    class_obj.course = course
                    class_obj.save()
                    ClassCourse.objects.create(class_obj=class_obj, course=course, published_by=request.user, is_active=True)
                except (ValueError, TypeError, Course.DoesNotExist):
                    pass
            return created_response(data={"class_id": class_obj.id, "name": class_obj.name}, msg="班级创建成功")
    except Exception as error:
        return error_response(msg=f"创建失败: {str(error)}", code=500)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_delete(request, class_id):
    """删除班级。"""
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    if class_obj.teacher != request.user and not request.user.is_admin:
        return forbidden_response(msg="无权删除此班级")
    class_obj.delete()
    return success_response(msg="班级已删除")


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_update(request, class_id):
    """获取或更新班级信息。"""
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    if request.method == "GET":
        student_count = Enrollment.objects.filter(class_obj=class_obj).count()
        class_courses = ClassCourse.objects.filter(class_obj=class_obj, is_active=True).select_related("course")
        courses = [{"course_id": class_course.course.id, "course_name": class_course.course.name} for class_course in class_courses]
        return success_response(data={
            "class_id": class_obj.id,
            "name": class_obj.name,
            "class_name": class_obj.name,
            "description": class_obj.description or "",
            "semester": class_obj.semester or "",
            "is_active": class_obj.is_active,
            "teacher": {"user_id": class_obj.teacher.id, "username": class_obj.teacher.username, "real_name": class_obj.teacher.real_name or ""} if class_obj.teacher else None,
            "student_count": student_count,
            "courses": courses,
            "created_at": class_obj.created_at.isoformat(),
        })

    if class_obj.teacher != request.user and not request.user.is_admin:
        return forbidden_response(msg="无权编辑此班级")
    for field in ["name", "description", "semester", "is_active"]:
        if field in request.data:
            setattr(class_obj, field, request.data[field])
    class_obj.save()
    return success_response(data={"class_id": class_obj.id, "name": class_obj.name}, msg="班级更新成功")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def my_classes(request):
    """获取我的班级列表。"""
    classes = Class.objects.filter(teacher=request.user).order_by("-created_at")
    course_id = request.query_params.get("course_id")
    if course_id:
        classes = classes.filter(class_courses__course_id=course_id).distinct()
    return success_response(data={"classes": [{"class_id": class_obj.id, "name": class_obj.name, "description": class_obj.description, "semester": class_obj.semester, "student_count": class_obj.get_student_count(), "is_active": class_obj.is_active, "created_at": class_obj.created_at.isoformat()} for class_obj in classes]})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_publish_course(request, class_id):
    """向班级发布课程。"""
    course_id = request.data.get("course_id")
    if not course_id:
        return error_response(msg="缺少课程ID", code=400)
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    if class_obj.teacher != request.user and not request.user.is_admin:
        return forbidden_response(msg="无权操作此班级")
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)
    if not course.is_public and course.created_by != request.user:
        return forbidden_response(msg="无权发布此课程")
    class_course, created = ClassCourse.objects.get_or_create(class_obj=class_obj, course=course, defaults={"published_by": request.user})
    if not created:
        class_course.is_active = True
        class_course.save()
    return success_response(data={"class_id": class_obj.id, "course_id": course.id}, msg="课程发布成功")


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_unpublish_course(request, class_id, course_id):
    """取消班级中的课程发布。"""
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    if class_obj.teacher != request.user and not request.user.is_admin:
        return forbidden_response(msg="无权操作此班级")
    try:
        class_course = ClassCourse.objects.get(class_obj=class_obj, course_id=course_id)
        class_course.is_active = False
        class_course.save()
    except ClassCourse.DoesNotExist:
        return error_response(msg="该课程未在此班级发布", code=404)
    return success_response(msg="课程已取消发布")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_courses(request, class_id):
    """获取班级发布的课程列表。"""
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    published_class_courses = ClassCourse.objects.filter(class_obj=class_obj, is_active=True).select_related("course", "published_by")
    return success_response(data={
        "class_id": class_id,
        "class_name": class_obj.name,
        "courses": [{"course_id": class_course.course.id, "name": class_course.course.name, "description": class_course.course.description, "published_by": class_course.published_by.username if class_course.published_by else None, "published_at": class_course.published_at.isoformat()} for class_course in published_class_courses],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_class_progress(request, class_id):
    """获取班级学习进度统计。"""
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    if class_obj.teacher != request.user and request.user.role != "admin":
        return forbidden_response(msg="无权查看此班级")

    from django.db.models import Avg
    from knowledge.models import KnowledgeMastery
    enrollments = Enrollment.objects.filter(class_obj=class_obj).select_related("user")
    student_ids = [enrollment.user_id for enrollment in enrollments]
    avg_by_user = dict(KnowledgeMastery.objects.filter(user_id__in=student_ids).values("user_id").annotate(avg=Avg("mastery_rate")).values_list("user_id", "avg"))
    progress = []
    for enrollment in enrollments:
        avg_mastery = float(avg_by_user.get(enrollment.user_id, 0) or 0)
        progress.append({"user_id": enrollment.user_id, "username": enrollment.user.username, "real_name": enrollment.user.real_name, "avg_mastery": round(avg_mastery, 2)})
    return success_response(data={"students": progress})
