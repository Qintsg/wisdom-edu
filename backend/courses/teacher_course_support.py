"""教师端课程视图的查询、写入与响应支撑逻辑。"""

from __future__ import annotations

import os
import shutil
import tempfile
import zipfile
from collections.abc import Mapping
from typing import Protocol

from django.conf import settings as django_settings
from django.db import transaction
from django.db.models import QuerySet

from application.teacher.contracts import normalize_course_payload
from .models import Class, ClassCourse, Course, Enrollment
from .teacher_course_helpers import COURSE_CONFIG_DEFAULTS, extract_course_archive, resolve_archive_root


# 维护意图：上传文件只依赖原始文件名和分块读取能力
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class UploadedChunkFile(Protocol):
    """上传文件只依赖原始文件名和分块读取能力。"""

    name: str

    # 维护意图：返回可迭代的文件分块
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def chunks(self) -> object:
        """返回可迭代的文件分块。"""


# 维护意图：搜索公开课程并返回分页响应
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_search_payload(query_params: Mapping[str, object]) -> dict[str, object]:
    """搜索公开课程并返回分页响应。"""
    keyword = query_params.get("keyword", "")
    page, page_size = parse_course_pagination(query_params)
    queryset = Course.objects.filter(is_public=True)
    if keyword:
        queryset = queryset.filter(name__icontains=keyword)

    total = queryset.count()
    courses = queryset[(page - 1) * page_size : page * page_size]
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "courses": [build_course_search_item(course) for course in courses],
    }


# 维护意图：解析课程搜索分页参数并兜底非法输入
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_course_pagination(query_params: Mapping[str, object]) -> tuple[int, int]:
    """解析课程搜索分页参数并兜底非法输入。"""
    try:
        page = max(1, int(query_params.get("page", 1)))
        page_size = min(max(1, int(query_params.get("page_size", 20))), 100)
    except (ValueError, TypeError):
        page, page_size = 1, 20
    return page, page_size


# 维护意图：序列化公开课程搜索项
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_search_item(course: Course) -> dict[str, object]:
    """序列化公开课程搜索项。"""
    return {
        "course_id": course.id,
        "name": course.name,
        "description": course.description,
        "cover": course.cover.url if course.cover else None,
        "created_by": course.created_by.username if course.created_by else None,
        "created_at": course.created_at.isoformat(),
    }


# 维护意图：创建课程，按需导入资源压缩包并发布到指定班级
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def create_teacher_course(
    data: Mapping[str, object],
    files: Mapping[str, object],
    user: object,
) -> tuple[dict[str, object] | None, str | None, int]:
    """创建课程，按需导入资源压缩包并发布到指定班级。"""
    payload = normalize_course_payload(data)
    name = payload["name"]
    if not name:
        return None, "课程名称不能为空", 400

    target_class, target_error, target_status = resolve_publish_class(data.get("publish_class_id"), user)
    if target_error:
        return None, target_error, target_status

    temp_dir: tempfile.TemporaryDirectory | None = None
    try:
        with transaction.atomic():
            course = Course.objects.create(
                name=name,
                description=payload["description"],
                term=payload["term"],
                is_public=payload["is_public"],
                initial_assessment_count=payload["initial_assessment_count"],
                created_by=user,
            )
            temp_dir = bootstrap_course_archive(files.get("archive") or files.get("course_archive"), course, user)
            if target_class:
                publish_course_to_class(course, target_class, user)
    except zipfile.BadZipFile:
        return None, "上传文件不是有效的 ZIP 压缩包", 400
    except Exception as exc:
        return None, f"课程创建失败: {exc}", 400
    finally:
        cleanup_course_archive(temp_dir)

    return {
        "course_id": course.id,
        "name": course.name,
        "published_class_id": target_class.id if target_class else None,
    }, None, 201


# 维护意图：解析创建课程时的可选发布班级，并执行教师权限校验
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_publish_class(
    publish_class_id: object,
    user: object,
) -> tuple[Class | None, str | None, int]:
    """解析创建课程时的可选发布班级，并执行教师权限校验。"""
    if publish_class_id in (None, ""):
        return None, None, 200
    try:
        target_class = Class.objects.get(id=int(publish_class_id))
    except (TypeError, ValueError, Class.DoesNotExist):
        return None, "发布班级不存在", 400
    if target_class.teacher != user and not getattr(user, "is_admin", False):
        return None, "无权发布到该班级", 403
    return target_class, None, 200


# 维护意图：解析课程资源包并调用既有 bootstrap 流程导入课程资产
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def bootstrap_course_archive(
    archive_file: object,
    course: Course,
    user: object,
) -> tempfile.TemporaryDirectory | None:
    """解析课程资源包并调用既有 bootstrap 流程导入课程资产。"""
    if not archive_file:
        return None

    from common.neo4j_service import neo4j_service
    from tools.bootstrap import bootstrap_course_assets

    archive_temp_dir = extract_course_archive(archive_file)
    if archive_temp_dir is None:
        raise ValueError("课程资源压缩包解析失败")
    bootstrap_course_assets(
        course_name=course.name,
        teacher=user.username,
        replace=True,
        sync_graph=neo4j_service.is_available,
        dry_run=False,
        resources_root=resolve_archive_root(archive_temp_dir),
    )
    return archive_temp_dir


# 维护意图：将新建课程发布到指定班级，并同步班级默认课程
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def publish_course_to_class(course: Course, target_class: Class, user: object) -> None:
    """将新建课程发布到指定班级，并同步班级默认课程。"""
    class_course, _ = ClassCourse.objects.get_or_create(
        class_obj=target_class,
        course=course,
        defaults={"published_by": user, "is_active": True},
    )
    if not class_course.is_active:
        class_course.is_active = True
        class_course.published_by = user
        class_course.save(update_fields=["is_active", "published_by"])
    if target_class.course_id != course.id:
        target_class.course = course
        target_class.save(update_fields=["course", "updated_at"])


# 维护意图：清理课程资源包临时目录，兼容 Windows 文件句柄延迟释放
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def cleanup_course_archive(temp_dir: tempfile.TemporaryDirectory | None) -> None:
    """清理课程资源包临时目录，兼容 Windows 文件句柄延迟释放。"""
    if temp_dir is None:
        return
    try:
        temp_dir.cleanup()
    except PermissionError:
        shutil.rmtree(temp_dir.name, ignore_errors=True)


# 维护意图：按主键读取教师端课程对象
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def get_teacher_course(course_id: int) -> Course | None:
    """按主键读取教师端课程对象。"""
    return Course.objects.filter(id=course_id).first()


# 维护意图：序列化教师端课程详情
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_detail_payload(course: Course) -> dict[str, object]:
    """序列化教师端课程详情。"""
    return {
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


# 维护意图：按兼容字段名更新课程基础信息
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_teacher_course(course: Course, data: Mapping[str, object]) -> dict[str, object]:
    """按兼容字段名更新课程基础信息。"""
    mapped_fields = apply_legacy_course_fields(course, data)
    for field in ["name", "description", "term", "is_public", "initial_assessment_count"]:
        if field in data and field not in mapped_fields:
            setattr(course, field, data[field])
    course.save()
    return {"course_id": course.id, "name": course.name}


# 维护意图：应用前端旧字段名到模型字段名的映射
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_legacy_course_fields(course: Course, data: Mapping[str, object]) -> set[str]:
    """应用前端旧字段名到模型字段名的映射。"""
    field_mapping = {"course_name": "name", "course_description": "description"}
    mapped_fields: set[str] = set()
    for frontend_key, model_field in field_mapping.items():
        if frontend_key in data:
            setattr(course, model_field, data[frontend_key])
            mapped_fields.add(model_field)
    return mapped_fields


# 维护意图：读取当前教师或管理员可管理课程
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_my_created_courses_payload(user: object) -> dict[str, object]:
    """读取当前教师或管理员可管理课程。"""
    courses = Course.get_manageable_courses(user)
    return {"courses": [build_my_course_item(course) for course in courses]}


# 维护意图：序列化我的课程列表项
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_my_course_item(course: Course) -> dict[str, object]:
    """序列化我的课程列表项。"""
    return {
        "course_id": course.id,
        "name": course.name,
        "description": course.description,
        "is_public": course.is_public,
        "created_at": course.created_at.isoformat(),
    }


# 维护意图：保持原删除权限：创建者、管理员角色或超级用户
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def can_delete_course(course: Course, user: object) -> bool:
    """保持原删除权限：创建者、管理员角色或超级用户。"""
    return course.created_by == user or getattr(user, "role", None) == "admin" or getattr(user, "is_superuser", False)


# 维护意图：保持原封面、统计和配置权限：创建者或管理员角色
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def can_access_owned_course(course: Course, user: object) -> bool:
    """保持原封面、统计和配置权限：创建者或管理员角色。"""
    return course.created_by == user or getattr(user, "role", None) == "admin"


# 维护意图：删除教师端课程并返回用户可读结果
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def delete_teacher_course(course_id: int, user: object) -> tuple[str | None, str | None, int]:
    """删除教师端课程并返回用户可读结果。"""
    course = get_teacher_course(course_id)
    if course is None:
        return None, "课程不存在", 404
    if not can_delete_course(course, user):
        return None, "无权删除此课程", 403
    try:
        course.delete()
    except Exception as exc:
        return None, f"课程删除失败: {exc}", 400
    return "课程已删除", None, 200


# 维护意图：读取需要创建者或管理员权限的课程
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def get_owned_course(course_id: int, user: object, permission_message: str) -> tuple[Course | None, str | None, int]:
    """读取需要创建者或管理员权限的课程。"""
    course = get_teacher_course(course_id)
    if course is None:
        return None, "课程不存在", 404
    if not can_access_owned_course(course, user):
        return None, permission_message, 403
    return course, None, 200


# 维护意图：校验课程权限后保存封面
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def upload_teacher_course_cover(
    course_id: int,
    files: Mapping[str, object],
    user: object,
) -> tuple[dict[str, object] | None, str | None, int]:
    """校验课程权限后保存封面。"""
    course, error_message, status_code = get_owned_course(course_id, user, "无权修改此课程")
    if error_message or course is None:
        return None, error_message, status_code
    return save_course_cover(course, files, course_id)


# 维护意图：保存课程封面文件并返回旧接口使用的 cover_url
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def save_course_cover(course: Course, files: Mapping[str, object], course_id: int) -> tuple[dict[str, object] | None, str | None, int]:
    """保存课程封面文件并返回旧接口使用的 cover_url。"""
    cover = files.get("cover") or files.get("file")
    if not cover:
        return None, "请上传封面图片", 400

    cover_url = write_course_cover_file(course_id, cover)
    course.cover_url = cover_url
    course.save()
    return {"cover_url": cover_url}, None, 200


# 维护意图：写入课程封面文件到 media/covers
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def write_course_cover_file(course_id: int, cover: UploadedChunkFile) -> str:
    """写入课程封面文件到 media/covers。"""
    cover_dir = os.path.join(django_settings.MEDIA_ROOT, "covers")
    os.makedirs(cover_dir, exist_ok=True)
    filename = f"course_{course_id}_{cover.name}"
    filepath = os.path.join(cover_dir, filename)
    with open(filepath, "wb+") as file_handle:
        for chunk in cover.chunks():
            file_handle.write(chunk)
    return f"/media/covers/{filename}"


# 维护意图：统计课程发布班级数量和去重学生数量
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_statistics_payload(course: Course) -> dict[str, object]:
    """统计课程发布班级数量和去重学生数量。"""
    class_course_queryset = ClassCourse.objects.filter(course=course)
    student_ids = course_student_ids(class_course_queryset)
    return {
        "course_id": course.id,
        "course_name": course.name,
        "class_count": class_course_queryset.count(),
        "student_count": len(student_ids),
    }


# 维护意图：读取课程关联班级内的去重学生 ID
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def course_student_ids(class_course_queryset: QuerySet[ClassCourse]) -> QuerySet[int]:
    """读取课程关联班级内的去重学生 ID。"""
    class_ids = class_course_queryset.values_list("class_obj_id", flat=True)
    return Enrollment.objects.filter(class_obj__in=class_ids).values_list("user_id", flat=True).distinct()


# 维护意图：校验课程权限后返回统计数据
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_statistics_for_user(course_id: int, user: object) -> tuple[dict[str, object] | None, str | None, int]:
    """校验课程权限后返回统计数据。"""
    course, error_message, status_code = get_owned_course(course_id, user, "无权查看此课程统计")
    if error_message or course is None:
        return None, error_message, status_code
    return build_course_statistics_payload(course), None, 200


# 维护意图：合并默认课程配置与课程自定义配置
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_settings_payload(course: Course) -> dict[str, object]:
    """合并默认课程配置与课程自定义配置。"""
    config = merged_course_config(course)
    return {"course_id": course.id, "course_name": course.name, "config": config}


# 维护意图：返回课程配置的默认值合并结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def merged_course_config(course: Course) -> dict[str, object]:
    """返回课程配置的默认值合并结果。"""
    config = {**COURSE_CONFIG_DEFAULTS}
    if isinstance(course.config, dict):
        config.update(course.config)
    config["initial_assessment_count"] = course.initial_assessment_count
    return config


# 维护意图：校验并更新课程配置
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_course_config(course: Course, new_config: object) -> tuple[dict[str, object] | None, str | None]:
    """校验并更新课程配置。"""
    if not isinstance(new_config, dict):
        return None, "config参数应为字典格式"
    invalid_keys = set(new_config.keys()) - set(COURSE_CONFIG_DEFAULTS.keys())
    if invalid_keys:
        return None, f"不允许的配置项: {', '.join(invalid_keys)}"

    current_config = course.config if isinstance(course.config, dict) else {}
    current_config.update(new_config)
    if "initial_assessment_count" in new_config:
        course.initial_assessment_count = int(new_config["initial_assessment_count"])
    course.config = current_config
    course.save()
    return {"course_id": course.id, "config": merged_course_config(course)}, None


# 维护意图：校验课程权限后返回课程配置
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_settings_for_user(course_id: int, user: object) -> tuple[dict[str, object] | None, str | None, int]:
    """校验课程权限后返回课程配置。"""
    course, error_message, status_code = get_owned_course(course_id, user, "无权修改此课程配置")
    if error_message or course is None:
        return None, error_message, status_code
    return build_course_settings_payload(course), None, 200


# 维护意图：校验课程权限后更新课程配置
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_course_settings_for_user(
    course_id: int,
    user: object,
    new_config: object,
) -> tuple[dict[str, object] | None, str | None, int]:
    """校验课程权限后更新课程配置。"""
    course, error_message, status_code = get_owned_course(course_id, user, "无权修改此课程配置")
    if error_message or course is None:
        return None, error_message, status_code
    payload, config_error = update_course_config(course, new_config)
    return payload, config_error, 400 if config_error else 200
