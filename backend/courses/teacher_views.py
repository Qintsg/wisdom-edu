"""
课程模块 - 教师接口

包含：课程CRUD、班级管理、邀请码、学生管理、课程设置
"""

import shutil
import tempfile
import zipfile
from pathlib import Path

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.db import models, transaction

from common.responses import (
    success_response,
    error_response,
    created_response,
    forbidden_response,
)
from common.permissions import IsTeacherOrAdmin
from application.teacher.contracts import (
    normalize_class_payload,
    normalize_course_payload,
)
from users.models import User
from .models import Course, Class, ClassCourse, Enrollment, Announcement
from .serializers import CourseSerializer


def _extract_course_archive(archive_file) -> tempfile.TemporaryDirectory | None:
    """解压课程资源压缩包并返回临时目录句柄。"""
    if not archive_file:
        return None

    temp_dir = tempfile.TemporaryDirectory(
        prefix="course_archive_",
        ignore_cleanup_errors=True,
    )
    archive_path = Path(temp_dir.name) / archive_file.name
    with archive_path.open("wb+") as destination:
        for chunk in archive_file.chunks():
            destination.write(chunk)

    with zipfile.ZipFile(archive_path, "r") as zip_file:
        zip_file.extractall(temp_dir.name)
    return temp_dir


def _resolve_archive_root(temp_dir: tempfile.TemporaryDirectory) -> str:
    """定位压缩包导入根目录。"""
    root = Path(temp_dir.name)
    children = [
        item
        for item in root.iterdir()
        if item.name != "__MACOSX" and item.suffix.lower() != ".zip"
    ]
    if len(children) == 1 and children[0].is_dir():
        return str(children[0])
    return str(root)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def course_search(request):
    """
    搜索公开课程
    GET /api/courses/search

    查询参数：
    - keyword: 搜索关键词
    - page: 页码
    - page_size: 每页数量
    """
    keyword = request.query_params.get("keyword", "")
    try:
        page = max(1, int(request.query_params.get("page", 1)))
        page_size = min(max(1, int(request.query_params.get("page_size", 20))), 100)
    except (ValueError, TypeError):
        page = 1
        page_size = 20

    queryset = Course.objects.filter(is_public=True)

    if keyword:
        queryset = queryset.filter(name__icontains=keyword)

    total = queryset.count()
    start = (page - 1) * page_size
    courses = queryset[start : start + page_size]

    return success_response(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "courses": [
                {
                    "course_id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "cover": c.cover.url if c.cover else None,
                    "created_by": c.created_by.username if c.created_by else None,
                    "created_at": c.created_at.isoformat(),
                }
                for c in courses
            ],
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def course_create(request):
    """
    创建课程
    POST /api/teacher/courses/create
    """
    payload = normalize_course_payload(request.data)
    name = payload["name"]
    description = payload["description"]
    term = payload["term"]
    is_public = payload["is_public"]
    initial_assessment_count = payload["initial_assessment_count"]
    archive_file = request.FILES.get("archive") or request.FILES.get("course_archive")
    publish_class_id = request.data.get("publish_class_id")

    if not name:
        return error_response(msg="课程名称不能为空", code=400)

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
                description=description,
                term=term,
                is_public=is_public,
                initial_assessment_count=initial_assessment_count,
                created_by=request.user,
            )

            if archive_file:
                from tools.bootstrap import bootstrap_course_assets
                from common.neo4j_service import neo4j_service

                archive_temp_dir = _extract_course_archive(archive_file)
                if archive_temp_dir is None:
                    raise ValueError("课程资源压缩包解析失败")
                temp_dir = archive_temp_dir
                bootstrap_course_assets(
                    course_name=course.name,
                    teacher=request.user.username,
                    replace=True,
                    sync_graph=neo4j_service.is_available,
                    dry_run=False,
                    resources_root=_resolve_archive_root(archive_temp_dir),
                )

            if target_class:
                class_course, _ = ClassCourse.objects.get_or_create(
                    class_obj=target_class,
                    course=course,
                    defaults={"published_by": request.user, "is_active": True},
                )
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

    return created_response(
        data={
            "course_id": course.id,
            "name": course.name,
            "published_class_id": target_class.id if target_class else None,
        },
        msg="课程创建成功",
    )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def course_update(request, course_id):
    """
    获取/更新课程
    GET /api/teacher/courses/{course_id} - 获取课程详情
    PUT /api/teacher/courses/{course_id} - 更新课程信息
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)

    if request.method == "GET":
        return success_response(
            data={
                "course_id": course.id,
                "name": course.name,
                "description": course.description or "",
                "term": course.term or "",
                "is_public": course.is_public,
                "initial_assessment_count": course.initial_assessment_count,
                "created_at": course.created_at.isoformat(),
                "updated_at": course.updated_at.isoformat(),
                "created_by": course.created_by.username if course.created_by else None,
            }
        )

    if not course.can_edit(request.user):
        return forbidden_response(msg="无权编辑此课程")

    # 更新字段（兼容前端传的 course_name/course_description 和 name/description）
    field_mapping = {
        "course_name": "name",
        "course_description": "description",
    }
    allowed_fields = [
        "name",
        "description",
        "term",
        "is_public",
        "initial_assessment_count",
    ]

    # 已通过映射设置的字段，不再重复设置
    mapped_fields = set()
    for frontend_key, model_field in field_mapping.items():
        if frontend_key in request.data:
            setattr(course, model_field, request.data[frontend_key])
            mapped_fields.add(model_field)

    for field in allowed_fields:
        if field in request.data and field not in mapped_fields:
            setattr(course, field, request.data[field])

    course.save()

    return success_response(
        data={"course_id": course.id, "name": course.name}, msg="课程更新成功"
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def my_created_courses(request):
    """
    获取我创建的课程
    GET /api/teacher/courses/my
    """
    courses = Course.get_manageable_courses(request.user)

    return success_response(
        data={
            "courses": [
                {
                    "course_id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "is_public": c.is_public,
                    "created_at": c.created_at.isoformat(),
                }
                for c in courses
            ]
        }
    )


# ========== 班级管理（教师/管理员） ==========


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_create(request):
    """
    创建班级
    POST /api/teacher/classes/create

    请求参数：
    - name: 班级名称 (必填)
    - description: 描述
    - semester: 学期
    - course_id: 关联的课程ID (可选)
    """
    payload = normalize_class_payload(request.data)
    name = payload["name"]
    description = payload["description"]
    semester = payload["semester"]
    course_id = payload["course_id"]

    if not name:
        return error_response(msg="班级名称不能为空", code=400)

    try:
        with transaction.atomic():
            class_obj = Class.objects.create(
                name=name,
                description=description,
                semester=semester,
                teacher=request.user,
            )

            # 如果提供了 course_id，自动发布该课程到班级
            if course_id:
                try:
                    from .models import Course, ClassCourse

                    course = Course.objects.get(id=course_id)
                    # 检查课程是否属于该教师（可选，视业务需求而定，这里暂不强制要求是本人创建的课程，只要存在即可）
                    # 给班级关联课程
                    class_obj.course = course  # 设置为默认课程
                    class_obj.save()

                    ClassCourse.objects.create(
                        class_obj=class_obj,
                        course=course,
                        published_by=request.user,
                        is_active=True,
                    )
                except (ValueError, TypeError):
                    pass  # course_id 非法，忽略
                except Course.DoesNotExist:
                    pass  # 课程不存在，仅创建班级

            return created_response(
                data={"class_id": class_obj.id, "name": class_obj.name},
                msg="班级创建成功",
            )

    except Exception as e:
        return error_response(msg=f"创建失败: {str(e)}", code=500)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_delete(request, class_id):
    """
    删除班级
    DELETE /api/teacher/classes/{class_id}
    """
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
    """
    获取/更新班级信息
    GET /api/teacher/classes/{class_id} - 获取班级详情
    PUT /api/teacher/classes/{class_id} - 更新班级信息
    """
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    if request.method == "GET":
        student_count = Enrollment.objects.filter(class_obj=class_obj).count()
        published_class_courses = ClassCourse.objects.filter(
            class_obj=class_obj, is_active=True
        ).select_related("course")
        courses = [
            {
                "course_id": cc.course.id,
                "course_name": cc.course.name,
            }
            for cc in published_class_courses
        ]

        return success_response(
            data={
                "class_id": class_obj.id,
                "name": class_obj.name,
                "class_name": class_obj.name,
                "description": class_obj.description or "",
                "semester": class_obj.semester or "",
                "is_active": class_obj.is_active,
                "teacher": {
                    "user_id": class_obj.teacher.id,
                    "username": class_obj.teacher.username,
                    "real_name": class_obj.teacher.real_name or "",
                }
                if class_obj.teacher
                else None,
                "student_count": student_count,
                "courses": courses,
                "created_at": class_obj.created_at.isoformat(),
            }
        )

    if class_obj.teacher != request.user and not request.user.is_admin:
        return forbidden_response(msg="无权编辑此班级")

    allowed_fields = ["name", "description", "semester", "is_active"]
    for field in allowed_fields:
        if field in request.data:
            setattr(class_obj, field, request.data[field])

    class_obj.save()

    return success_response(
        data={"class_id": class_obj.id, "name": class_obj.name}, msg="班级更新成功"
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def my_classes(request):
    """
    获取我的班级列表
    GET /api/teacher/classes/my
    """
    classes = Class.objects.filter(teacher=request.user).order_by("-created_at")
    course_id = request.query_params.get("course_id")
    if course_id:
        classes = classes.filter(class_courses__course_id=course_id).distinct()

    return success_response(
        data={
            "classes": [
                {
                    "class_id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "semester": c.semester,
                    "student_count": c.get_student_count(),
                    "is_active": c.is_active,
                    "created_at": c.created_at.isoformat(),
                }
                for c in classes
            ]
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_publish_course(request, class_id):
    """
    向班级发布课程
    POST /api/teacher/classes/{class_id}/publish-course
    """
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

    class_course, created = ClassCourse.objects.get_or_create(
        class_obj=class_obj, course=course, defaults={"published_by": request.user}
    )

    if not created:
        class_course.is_active = True
        class_course.save()

    return success_response(
        data={"class_id": class_obj.id, "course_id": course.id}, msg="课程发布成功"
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_unpublish_course(request, class_id, course_id):
    """
    取消班级中的课程发布
    DELETE /api/teacher/classes/{class_id}/courses/{course_id}
    """
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
    """
    获取班级发布的课程列表
    GET /api/teacher/classes/{class_id}/courses
    """
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    published_class_courses = ClassCourse.objects.filter(
        class_obj=class_obj, is_active=True
    ).select_related("course", "published_by")

    return success_response(
        data={
            "class_id": class_id,
            "class_name": class_obj.name,
            "courses": [
                {
                    "course_id": cc.course.id,
                    "name": cc.course.name,
                    "description": cc.course.description,
                    "published_by": cc.published_by.username
                    if cc.published_by
                    else None,
                    "published_at": cc.published_at.isoformat(),
                }
                for cc in published_class_courses
            ],
        }
    )


# ============ 学生班级管理 ============


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def generate_class_invitation(request):
    """
    生成班级邀请码
    POST /api/teacher/invitations/generate

    请求参数：
    - class_id: 班级ID（必填）
    - max_uses: 最大使用次数（可选，默认100）
    - expires_days: 有效天数（可选，默认30天）
    """
    from users.models import ClassInvitation
    from datetime import timedelta
    from django.utils import timezone
    import random
    import string

    user = request.user
    class_id = request.data.get("class_id")
    max_uses = request.data.get("max_uses", 100)
    expires_days = request.data.get("expires_days", 30)

    if not class_id:
        return error_response(msg="请提供班级ID", code=400)

    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    if user.role == "teacher" and class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权为此班级生成邀请码")

    code = None
    for _ in range(10):
        candidate = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not ClassInvitation.objects.filter(code=candidate).exists():
            code = candidate
            break

    if code is None:
        return error_response(msg="邀请码生成失败，请重试", code=500)

    invitation = ClassInvitation.objects.create(
        code=code,
        class_obj=class_obj,
        created_by=user,
        max_uses=max_uses,
        expires_at=timezone.now() + timedelta(days=expires_days),
    )

    course_name = class_obj.course.name if class_obj.course else None

    return created_response(
        data={
            "invitation_id": invitation.id,
            "code": invitation.code,
            "class_id": class_obj.id,
            "class_name": class_obj.name,
            "course_name": course_name,
            "max_uses": invitation.max_uses,
            "expires_at": invitation.expires_at.isoformat()
            if invitation.expires_at
            else None,
        },
        msg="邀请码生成成功",
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def list_class_invitations(request, class_id):
    """
    获取班级邀请码列表
    GET /api/teacher/classes/{class_id}/invitations
    """
    from users.models import ClassInvitation

    user = request.user

    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    if user.role == "teacher" and class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权查看此班级的邀请码")

    invitations = ClassInvitation.objects.filter(class_obj=class_obj)

    return success_response(
        data={
            "class_id": class_id,
            "class_name": class_obj.name,
            "invitations": [
                {
                    "id": inv.id,
                    "code": inv.code,
                    "max_uses": inv.max_uses,
                    "use_count": inv.use_count,
                    "expires_at": inv.expires_at.isoformat()
                    if inv.expires_at
                    else None,
                    "is_active": inv.is_active,
                    "is_valid": inv.is_valid(),
                    "created_at": inv.created_at.isoformat(),
                }
                for inv in invitations
            ],
        }
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def delete_class_invitation(request, invitation_id):
    """
    删除班级邀请码
    DELETE /api/teacher/invitations/{invitation_id}
    """
    from users.models import ClassInvitation

    user = request.user

    try:
        invitation = ClassInvitation.objects.get(id=invitation_id)
    except ClassInvitation.DoesNotExist:
        return error_response(msg="邀请码不存在", code=404)

    if user.role == "teacher" and invitation.class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权删除此邀请码")

    invitation.delete()
    return success_response(msg="邀请码已删除")


# ============ 班级学生管理（教师）============


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_students(request, class_id):
    """
    获取班级学生列表
    GET /api/teacher/classes/{class_id}/students
    """
    user = request.user

    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    if user.role == "teacher" and class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权查看此班级的学生")

    enrollments = Enrollment.objects.filter(class_obj=class_obj).select_related("user")

    students = []
    for e in enrollments:
        students.append(
            {
                "user_id": e.user.id,
                "username": e.user.username,
                "real_name": e.user.real_name,
                "student_id": e.user.student_id,
                "email": e.user.email,
                "role": e.role,
                "enrolled_at": e.enrolled_at.isoformat(),
            }
        )

    course_name = class_obj.course.name if class_obj.course else None

    return success_response(
        data={
            "class_id": class_id,
            "class_name": class_obj.name,
            "course_name": course_name,
            "total": len(students),
            "students": students,
        }
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def remove_student_from_class(request, class_id, user_id):
    """
    从班级中移除学生
    DELETE /api/teacher/classes/{class_id}/students/{user_id}
    """
    user = request.user

    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    if user.role == "teacher" and class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权管理此班级")

    try:
        enrollment = Enrollment.objects.get(class_obj=class_obj, user_id=user_id)
    except Enrollment.DoesNotExist:
        return error_response(msg="该学生不在此班级中", code=404)

    enrollment.delete()
    return success_response(msg="学生已从班级中移除")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def get_class_student_profiles(request, class_id):
    """
    获取班级学生画像列表
    GET /api/teacher/classes/{class_id}/student-profiles
    """
    from knowledge.models import KnowledgeMastery, ProfileSummary
    from assessments.models import AbilityScore
    from users.models import HabitPreference

    user = request.user

    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    if user.role == "teacher" and class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权查看此班级的学生画像")

    enrollments = Enrollment.objects.filter(class_obj=class_obj).select_related("user")

    course = class_obj.course

    # 批量预查询，避免N+1
    student_ids = [e.user_id for e in enrollments]

    ability_by_user = {}
    for a in AbilityScore.objects.filter(user_id__in=student_ids):
        if a.user_id not in ability_by_user:
            ability_by_user[a.user_id] = a

    habit_by_user = {}
    for h in HabitPreference.objects.filter(user_id__in=student_ids):
        if h.user_id not in habit_by_user:
            habit_by_user[h.user_id] = h

    mastery_by_user = {}
    if course:
        for m in KnowledgeMastery.objects.filter(
            user_id__in=student_ids, course=course
        ).select_related("knowledge_point"):
            mastery_by_user.setdefault(m.user_id, []).append(
                {
                    "point_name": m.knowledge_point.name,
                    "mastery_rate": float(m.mastery_rate),
                }
            )

    profiles = []
    for e in enrollments:
        student = e.user
        ability_score = ability_by_user.get(student.id)
        habit = habit_by_user.get(student.id)
        mastery_data = mastery_by_user.get(student.id, [])[:10]
        ability_score_payload = None
        if ability_score is not None:
            ability_score_payload = {
                "logical_reasoning": ability_score.logical_reasoning,
                "memory": ability_score.memory,
                "innovation": ability_score.innovation,
            }
        habit_preference_payload = None
        if habit is not None:
            habit_preference_payload = {
                "preferred_resource": habit.preferred_resource,
                "preferred_study_time": habit.preferred_study_time,
                "study_pace": habit.study_pace,
            }

        profiles.append(
            {
                "user_id": student.id,
                "username": student.username,
                "real_name": student.real_name,
                "ability_score": ability_score_payload,
                "habit_preference": habit_preference_payload,
                "knowledge_mastery": mastery_data,
            }
        )

    return success_response(
        data={"class_id": class_id, "class_name": class_obj.name, "profiles": profiles}
    )


# ========== 管理端 ==========


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def course_delete(request, course_id):
    """
    教师端 - 删除课程
    DELETE /api/teacher/courses/{course_id}/delete
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)

    if (
        course.created_by != request.user
        and request.user.role != "admin"
        and not request.user.is_superuser
    ):
        return error_response(msg="无权删除此课程", code=403)

    course.delete()
    return success_response(msg="课程已删除")


# ============ 管理端统计 ============


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_course_cover_upload(request, course_id):
    """
    上传课程封面图
    POST /api/teacher/courses/{course_id}/cover/upload
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)

    if course.created_by != request.user and request.user.role != "admin":
        return forbidden_response(msg="无权修改此课程")

    cover = request.FILES.get("cover") or request.FILES.get("file")
    if not cover:
        return error_response(msg="请上传封面图片", code=400)

    # 保存到 media/covers/
    import os
    from django.conf import settings as django_settings

    cover_dir = os.path.join(django_settings.MEDIA_ROOT, "covers")
    os.makedirs(cover_dir, exist_ok=True)

    filename = f"course_{course_id}_{cover.name}"
    filepath = os.path.join(cover_dir, filename)

    with open(filepath, "wb+") as f:
        for chunk in cover.chunks():
            f.write(chunk)

    cover_url = f"/media/covers/{filename}"
    course.cover_url = cover_url
    course.save()

    return success_response(data={"cover_url": cover_url}, msg="封面上传成功")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_course_statistics(request, course_id):
    """
    获取课程统计数据
    GET /api/teacher/courses/{course_id}/statistics
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)

    if course.created_by != request.user and request.user.role != "admin":
        return forbidden_response(msg="无权查看此课程统计")

    class_count = ClassCourse.objects.filter(course=course).count()
    student_ids = (
        Enrollment.objects.filter(
            class_obj__in=ClassCourse.objects.filter(course=course).values_list(
                "class_obj_id", flat=True
            )
        )
        .values_list("user_id", flat=True)
        .distinct()
    )

    return success_response(
        data={
            "course_id": course.id,
            "course_name": course.name,
            "class_count": class_count,
            "student_count": len(student_ids),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def teacher_class_progress(request, class_id):
    """
    获取班级学习进度统计
    GET /api/teacher/classes/{class_id}/progress
    """
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    if class_obj.teacher != request.user and request.user.role != "admin":
        return forbidden_response(msg="无权查看此班级")

    enrollments = Enrollment.objects.filter(class_obj=class_obj).select_related("user")

    from knowledge.models import KnowledgeMastery
    from django.db.models import Avg

    student_ids = [e.user_id for e in enrollments]
    avg_by_user = dict(
        KnowledgeMastery.objects.filter(user_id__in=student_ids)
        .values("user_id")
        .annotate(avg=Avg("mastery_rate"))
        .values_list("user_id", "avg")
    )

    progress = []
    for e in enrollments:
        avg = float(avg_by_user.get(e.user_id, 0) or 0)
        progress.append(
            {
                "user_id": e.user_id,
                "username": e.user.username,
                "real_name": e.user.real_name,
                "avg_mastery": round(avg, 2),
            }
        )

    return success_response(data={"students": progress})


# ============ 教师课程配置API ============

# 课程配置默认值
COURSE_CONFIG_DEFAULTS = {
    "exam_pass_score": 60,  # 考试及格分
    "exam_duration": 90,  # 考试默认时长（分钟）
    "allow_retake": True,  # 允许重考
    "max_retake_times": 3,  # 最大重考次数
    "resource_approval": False,  # 资源需要审核
    "auto_publish_exam": False,  # 考试自动发布
    "show_answer_after_exam": True,  # 考试后显示答案
    "allow_late_submission": False,  # 允许迟交
    "initial_assessment_count": 10,  # 初始评测题数
}


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def get_course_settings(request, course_id):
    """
    获取课程配置
    GET /api/teacher/courses/{course_id}/settings
    """
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

    return success_response(
        data={"course_id": course.id, "course_name": course.name, "config": config}
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def update_course_settings(request, course_id):
    """
    更新课程配置
    PUT /api/teacher/courses/{course_id}/settings

    请求体: {"config": {"exam_pass_score": 70, ...}}
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg="课程不存在", code=404)

    if course.created_by != request.user and request.user.role != "admin":
        return forbidden_response(msg="无权修改此课程配置")

    new_config = request.data.get("config", {})
    if not isinstance(new_config, dict):
        return error_response(msg="config参数应为字典格式", code=400)

    allowed_keys = set(COURSE_CONFIG_DEFAULTS.keys())
    invalid_keys = set(new_config.keys()) - allowed_keys
    if invalid_keys:
        return error_response(
            msg=f"不允许的配置项: {', '.join(invalid_keys)}", code=400
        )

    current_config = course.config if isinstance(course.config, dict) else {}
    current_config.update(new_config)

    if "initial_assessment_count" in new_config:
        course.initial_assessment_count = int(new_config["initial_assessment_count"])

    course.config = current_config
    course.save()

    merged = dict(COURSE_CONFIG_DEFAULTS)
    merged.update(current_config)
    merged["initial_assessment_count"] = course.initial_assessment_count

    return success_response(
        data={"course_id": course.id, "config": merged}, msg="课程配置已更新"
    )


# ============================================================
# 班级公告管理
# ============================================================


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def class_announcements(request, class_id):
    """
    班级公告列表 / 创建公告
    GET  /api/teacher/classes/<class_id>/announcements
    POST /api/teacher/classes/<class_id>/announcements
    """
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    if class_obj.teacher != request.user:
        return forbidden_response(msg="无权操作该班级")

    if request.method == "GET":
        announcements = Announcement.objects.filter(class_obj=class_obj)
        data = [
            {
                "id": a.id,
                "title": a.title,
                "content": a.content,
                "created_by": a.created_by.username if a.created_by else None,
                "created_at": a.created_at.strftime("%Y-%m-%d %H:%M")
                if a.created_at
                else None,
                "updated_at": a.updated_at.strftime("%Y-%m-%d %H:%M")
                if a.updated_at
                else None,
            }
            for a in announcements
        ]
        return success_response(data={"announcements": data})

    title = request.data.get("title", "").strip()
    content = request.data.get("content", "").strip()
    if not title:
        return error_response(msg="公告标题不能为空", code=400)
    if not content:
        return error_response(msg="公告内容不能为空", code=400)

    announcement = Announcement.objects.create(
        class_obj=class_obj, title=title, content=content, created_by=request.user
    )
    return created_response(
        data={
            "id": announcement.id,
            "title": announcement.title,
            "content": announcement.content,
            "created_at": announcement.created_at.strftime("%Y-%m-%d %H:%M"),
        },
        msg="公告发布成功",
    )


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def announcement_detail(request, announcement_id):
    """
    编辑 / 删除公告
    PUT    /api/teacher/announcements/<announcement_id>
    DELETE /api/teacher/announcements/<announcement_id>
    """
    try:
        announcement = Announcement.objects.select_related("class_obj").get(
            id=announcement_id
        )
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
    return success_response(
        data={
            "id": announcement.id,
            "title": announcement.title,
            "content": announcement.content,
            "updated_at": announcement.updated_at.strftime("%Y-%m-%d %H:%M"),
        },
        msg="公告已更新",
    )
