"""教师端课程 CRUD、封面、统计和配置视图。"""
from __future__ import annotations

import os
import shutil
import zipfile

from django.conf import settings as django_settings
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from application.teacher.contracts import normalize_course_payload
from common.permissions import IsTeacherOrAdmin
from common.responses import created_response, error_response, forbidden_response, success_response

from .models import Class, ClassCourse, Course, Enrollment
from .teacher_course_helpers import COURSE_CONFIG_DEFAULTS, extract_course_archive, resolve_archive_root


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def course_search(request):
    """搜索公开课程。"""
    keyword = request.query_params.get("keyword", "")
    try:
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = min(max(1, int(request.query_params.get("page_size", 20))), 100)
    except (ValueError, TypeError):
        page, page_size = 1, 20

    queryset = Course.objects.filter(is_public=True)
    if keyword:
        queryset = queryset.filter(name__icontains=keyword)
    total = queryset.count()
    courses = queryset[(page - 1) * page_size : page * page_size]
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "courses": [{
            "course_id": course.id,
            "name": course.name,
            "description": course.description,
            "cover": course.cover.url if course.cover else None,
            "created_by": course.created_by.username if course.created_by else None,
            "created_at": course.created_at.isoformat(),
        } for course in courses],
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def course_create(request):
    """创建课程。"""
    payload = normalize_course_payload(request.data)
    name = payload["name"]
    if not name:
        return error_response(msg="课程名称不能为空", code=400)

    archive_file = request.FILES.get("archive") or request.FILES.get("course_archive")
    publish_class_id = request.data.get("publish_class_id")
    target_class = None
    if publish_class_id not in (None, ""):
        try:
            target_class = Class.objects.get(id=int(publish_class_id))
        except (TypeError, ValueError, Class.DoesNotExist):
            return error_response(msg="发布班级不存在", code=400)
        if target_class.teacher != request.user and not request.user.is_admin:
            return forbidden_response(msg="无权发布到该班级")

    temp_dir = None
    try:
        with transaction.atomic():
            course = Course.objects.create(
                name=name,
                description=payload["description"],
                term=payload["term"],
                is_public=payload["is_public"],
                initial_assessment_count=payload["initial_assessment_count"],
                created_by=request.user,
            )
            if archive_file:
                from common.neo4j_service import neo4j_service
                from tools.bootstrap import bootstrap_course_assets
                archive_temp_dir = extract_course_archive(archive_file)
                if archive_temp_dir is None:
                    raise ValueError("课程资源压缩包解析失败")
                temp_dir = archive_temp_dir
                bootstrap_course_assets(
                    course_name=course.name,
                    teacher=request.user.username,
                    replace=True,
                    sync_graph=neo4j_service.is_available,
                    dry_run=False,
                    resources_root=resolve_archive_root(archive_temp_dir),
                )
            if target_class:
                class_course, _ = ClassCourse.objects.get_or_create(class_obj=target_class, course=course, defaults={"published_by": request.user, "is_active": True})
                if not class_course.is_active:
                    class_course.is_active = True
                    class_course.published_by = request.user
                    class_course.save(update_fields=["is_active", "published_by"])
                if target_class.course_id != course.id:
                    target_class.course = course
                    target_class.save(update_fields=["course", "updated_at"])
    except zipfile.BadZipFile:
        return error_response(msg="上传文件不是有效的 ZIP 压缩包", code=400)
    except Exception as exc:
        return error_response(msg=f"课程创建失败: {exc}", code=400)
    finally:
        if temp_dir:
            try:
                temp_dir.cleanup()
            except PermissionError:
                shutil.rmtree(temp_dir.name, ignore_errors=True)

    return created_response(data={"course_id": course.id, "name": course.name, "published_class_id": target_class.id if target_class else None}, msg="课程创建成功")


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def course_update(request, course_id):
    """获取或更新课程。"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)

    if request.method == "GET":
        return success_response(data={
            "course_id": course.id,
            "name": course.name,
            "description": course.description or "",
            "term": course.term or "",
            "is_public": course.is_public,
            "initial_assessment_count": course.initial_assessment_count,
            "created_at": course.created_at.isoformat(),
            "updated_at": course.updated_at.isoformat(),
            "created_by": course.created_by.username if course.created_by else None,
        })
    if not course.can_edit(request.user):
        return forbidden_response(msg="无权编辑此课程")

    field_mapping = {"course_name": "name", "course_description": "description"}
    allowed_fields = ["name", "description", "term", "is_public", "initial_assessment_count"]
    mapped_fields = set()
    for frontend_key, model_field in field_mapping.items():
        if frontend_key in request.data:
            setattr(course, model_field, request.data[frontend_key])
            mapped_fields.add(model_field)
    for field in allowed_fields:
        if field in request.data and field not in mapped_fields:
            setattr(course, field, request.data[field])
    course.save()
    return success_response(data={"course_id": course.id, "name": course.name}, msg="课程更新成功")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def my_created_courses(request):
    """获取我创建的课程。"""
    courses = Course.get_manageable_courses(request.user)
    return success_response(data={"courses": [{"course_id": course.id, "name": course.name, "description": course.description, "is_public": course.is_public, "created_at": course.created_at.isoformat()} for course in courses]})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def course_delete(request, course_id):
    """教师端删除课程。"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)
    if course.created_by != request.user and request.user.role != "admin" and not request.user.is_superuser:
        return error_response(msg="无权删除此课程", code=403)
    course.delete()
    return success_response(msg="课程已删除")


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_course_cover_upload(request, course_id):
    """上传课程封面图。"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)
    if course.created_by != request.user and request.user.role != "admin":
        return forbidden_response(msg="无权修改此课程")
    cover = request.FILES.get("cover") or request.FILES.get("file")
    if not cover:
        return error_response(msg="请上传封面图片", code=400)

    cover_dir = os.path.join(django_settings.MEDIA_ROOT, "covers")
    os.makedirs(cover_dir, exist_ok=True)
    filename = f"course_{course_id}_{cover.name}"
    filepath = os.path.join(cover_dir, filename)
    with open(filepath, "wb+") as file_handle:
        for chunk in cover.chunks():
            file_handle.write(chunk)
    cover_url = f"/media/covers/{filename}"
    course.cover_url = cover_url
    course.save()
    return success_response(data={"cover_url": cover_url}, msg="封面上传成功")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_course_statistics(request, course_id):
    """获取课程统计数据。"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)
    if course.created_by != request.user and request.user.role != "admin":
        return forbidden_response(msg="无权查看此课程统计")
    class_count = ClassCourse.objects.filter(course=course).count()
    student_ids = Enrollment.objects.filter(class_obj__in=ClassCourse.objects.filter(course=course).values_list("class_obj_id", flat=True)).values_list("user_id", flat=True).distinct()
    return success_response(data={"course_id": course.id, "course_name": course.name, "class_count": class_count, "student_count": len(student_ids)})


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def get_course_settings(request, course_id):
    """获取课程配置。"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)
    if course.created_by != request.user and request.user.role != "admin":
        return forbidden_response(msg="无权修改此课程配置")
    config = {**COURSE_CONFIG_DEFAULTS}
    if isinstance(course.config, dict):
        config.update(course.config)
    config["initial_assessment_count"] = course.initial_assessment_count
    return success_response(data={"course_id": course.id, "course_name": course.name, "config": config})


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def update_course_settings(request, course_id):
    """更新课程配置。"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)
    if course.created_by != request.user and request.user.role != "admin":
        return forbidden_response(msg="无权修改此课程配置")
    new_config = request.data.get("config", {})
    if not isinstance(new_config, dict):
        return error_response(msg="config参数应为字典格式", code=400)
    invalid_keys = set(new_config.keys()) - set(COURSE_CONFIG_DEFAULTS.keys())
    if invalid_keys:
        return error_response(msg=f"不允许的配置项: {', '.join(invalid_keys)}", code=400)
    current_config = course.config if isinstance(course.config, dict) else {}
    current_config.update(new_config)
    if "initial_assessment_count" in new_config:
        course.initial_assessment_count = int(new_config["initial_assessment_count"])
    course.config = current_config
    course.save()
    merged = dict(COURSE_CONFIG_DEFAULTS)
    merged.update(current_config)
    merged["initial_assessment_count"] = course.initial_assessment_count
    return success_response(data={"course_id": course.id, "config": merged}, msg="课程配置已更新")
