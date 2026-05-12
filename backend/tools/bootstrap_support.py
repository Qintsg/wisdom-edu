#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""课程资源导入辅助工具。"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Optional

from django.conf import settings

from courses.models import Course
from knowledge.models import Resource
from tools.common import (
    BASE_DIR,
    COURSE_RESOURCES_DIR,
    CourseAssetBundle,
    resolve_path,
)
from tools.testing import _status_flag
from users.models import User


def ensure_teacher(username: str) -> User:
    """校验教师账号是否存在。"""
    teacher = User.objects.filter(username=username).first()
    if not teacher:
        raise ValueError(f"教师不存在: {username}")
    return teacher


def ensure_course_record(course_name: str, teacher_obj: User) -> Course:
    """确保课程记录存在。"""
    course = Course.objects.filter(name=course_name).first()
    if course is not None:
        return course
    return Course.objects.create(
        name=course_name,
        description=f"{course_name} 样例课程（从资源目录导入）",
        created_by=teacher_obj,
        is_public=True,
    )


def copy_to_media(source_path: Path, sub_dir: str = "resources") -> str:
    """将文件复制到 MEDIA_ROOT 下并返回相对路径。"""
    media_root = Path(settings.MEDIA_ROOT)
    dest_dir = media_root / sub_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / source_path.name
    if dest_path.exists():
        stem = source_path.stem
        suffix = source_path.suffix
        counter = 1
        while dest_path.exists():
            dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1

    shutil.copy2(str(source_path), str(dest_path))
    return str(dest_path.relative_to(media_root)).replace("\\", "/")


def bundle_has_importable_assets(bundle: CourseAssetBundle) -> bool:
    """判断课程资源包是否包含可导入资源。"""
    return any(
        [
            bundle.knowledge_file,
            bundle.initial_assessment_file,
            bundle.homework_files,
            bundle.resources_file,
            bundle.ppt_files,
            bundle.video_files,
            bundle.textbook_files,
        ]
    )


def import_media_resources(
    *,
    course: Course,
    teacher_obj: User,
    file_paths: list[Path],
    resource_type: str,
    sub_dir: str,
    description_prefix: str,
    chapter_from_parent: bool = False,
) -> int:
    """导入文件型课程资源并返回实际新增条数。"""
    if not file_paths:
        return 0

    created_count = 0
    sort_order = Resource.objects.filter(course=course).count()
    for file_path in file_paths:
        chapter_num = None
        title = file_path.stem
        if chapter_from_parent:
            parent_name = file_path.parent.name
            chapter_num = parent_name if parent_name.isdigit() else None
            chapter_label = f"第{chapter_num}章" if chapter_num else ""
            title = f"{chapter_label} {file_path.stem}".strip()

        if Resource.objects.filter(
            course=course,
            title=title,
            resource_type=resource_type,
        ).exists():
            continue

        relative_path = copy_to_media(file_path, sub_dir=sub_dir)
        Resource.objects.create(
            course=course,
            title=title,
            resource_type=resource_type,
            file=relative_path,
            description=f"{description_prefix} - {file_path.name}",
            chapter_number=chapter_num,
            sort_order=sort_order,
            is_visible=True,
            uploaded_by=teacher_obj,
        )
        created_count += 1
        sort_order += 1
    return created_count


def import_bundle_knowledge_assets(
    *,
    bundle: CourseAssetBundle,
    course: Course,
    replace: bool,
    dry_run: bool,
) -> None:
    """导入课程知识图谱资源。"""
    from tools.knowledge import import_knowledge, import_knowledge_map

    if not bundle.knowledge_file:
        return
    suffix = bundle.knowledge_file.suffix.lower()
    if suffix == ".json":
        import_knowledge(
            str(bundle.knowledge_file),
            int(course.pk),
            replace=replace,
            dry_run=dry_run,
        )
        return
    if suffix in [".xlsx", ".xls"]:
        if dry_run:
            print(f"[DRY-RUN] 将导入知识图谱Excel: {bundle.knowledge_file}")
        else:
            import_knowledge_map(str(bundle.knowledge_file), course_id=int(course.pk))


def import_bundle_question_assets(
    *,
    bundle: CourseAssetBundle,
    course: Course,
    replace: bool,
    dry_run: bool,
) -> None:
    """导入初始评测、作业题库与套题。"""
    from assessments.models import Question
    from tools.exam_sets import import_exam_sets
    from tools.questions import import_question_bank

    if replace and not dry_run and (bundle.initial_assessment_file or bundle.homework_files):
        Question.objects.filter(course=course).delete()

    if bundle.initial_assessment_file:
        if dry_run:
            print(f"[DRY-RUN] 将导入初始评测: {bundle.initial_assessment_file}")
        else:
            import_question_bank(
                str(bundle.initial_assessment_file),
                int(course.pk),
                for_initial_assessment=True,
            )
            initial_question_count = Question.objects.filter(
                course=course,
                for_initial_assessment=True,
            ).count()
            if initial_question_count:
                course.initial_assessment_count = initial_question_count
                course.save(update_fields=["initial_assessment_count", "updated_at"])

    for homework_path in bundle.homework_files:
        if dry_run:
            print(f"[DRY-RUN] 将导入作业库: {homework_path}")
        else:
            import_question_bank(
                str(homework_path),
                int(course.pk),
                for_initial_assessment=False,
            )

    if not bundle.homework_files:
        return
    if dry_run:
        print("[DRY-RUN] 将从作业库创建套题")
        return
    homework_dir = bundle.homework_files[0].parent
    import_exam_sets(int(course.pk), str(homework_dir), replace=replace)


def import_bundle_resource_assets(
    *,
    bundle: CourseAssetBundle,
    course: Course,
    replace: bool,
    dry_run: bool,
) -> None:
    """导入资源 JSON。"""
    from tools.resources import import_resources_json

    if bundle.resources_file and bundle.resources_file.suffix.lower() == ".json":
        import_resources_json(
            str(bundle.resources_file),
            int(course.pk),
            replace=replace,
            dry_run=dry_run,
        )


def import_bundle_media_assets(
    *,
    bundle: CourseAssetBundle,
    course: Course,
    teacher_obj: User,
    dry_run: bool,
) -> None:
    """导入课程媒体资源。"""
    media_specs = [
        ("PPT", bundle.ppt_files, "document", "resources/ppt", "课程PPT", True),
        ("视频", bundle.video_files, "video", "resources/video", "教学视频", False),
        ("电子教材", bundle.textbook_files, "document", "resources/textbook", "电子教材", False),
    ]
    for label, file_paths, resource_type, sub_dir, description_prefix, chapter_from_parent in media_specs:
        if not file_paths:
            continue
        if dry_run:
            print(f"[DRY-RUN] 将导入 {len(file_paths)} 个{label}文件")
            continue
        imported_count = import_media_resources(
            course=course,
            teacher_obj=teacher_obj,
            file_paths=file_paths,
            resource_type=resource_type,
            sub_dir=sub_dir,
            description_prefix=description_prefix,
            chapter_from_parent=chapter_from_parent,
        )
        print(f"  {label}资源导入: {imported_count} 个文件")


def finalize_bootstrap_course(
    *,
    course: Course,
    sync_graph: bool,
    dry_run: bool,
) -> None:
    """执行图谱同步与 RAG 刷新收尾动作。"""
    from tools.neo4j_tools import sync_neo4j
    from tools.rag_index import refresh_rag_corpus

    if sync_graph and not dry_run:
        result = sync_neo4j(int(course.pk))
        if not result or result.get("nodes", 0) <= 0:
            raise RuntimeError(f"课程 {course.name} 的 Neo4j 图数据同步失败或为空")

    if not dry_run:
        refresh_rag_corpus(course_id=int(course.pk))


def resolve_resources_root(resources_root: Optional[str]) -> Path:
    """解析课程资源导入根目录。"""
    if not resources_root:
        return COURSE_RESOURCES_DIR
    return resolve_path(resources_root)


def resolve_batch_resource_root() -> Path:
    """读取批量导入时的资源目录，并处理环境变量回退。"""
    try:
        from dotenv import load_dotenv as dotenv_loader
    except ImportError:
        dotenv_loader = None

    if dotenv_loader is not None:
        dotenv_loader(BASE_DIR / ".env")

    resource_dir = os.getenv("COURSE_RESOURCES_DIR", str(COURSE_RESOURCES_DIR))
    resource_path = Path(resource_dir)
    if not resource_path.is_absolute():
        resource_path = BASE_DIR / resource_path
    if not resource_path.exists() and resource_path != COURSE_RESOURCES_DIR:
        print(
            f"  {_status_flag(False)} 环境变量资源目录不可用，回退到内置目录: {resource_path}"
        )
        return COURSE_RESOURCES_DIR
    return resource_path


def collect_batch_candidates(
    *,
    resource_path: Path,
    course_name: Optional[str],
) -> list[tuple[str, Path]]:
    """构造批量课程导入候选列表。"""
    if not resource_path.exists():
        print(f"  {_status_flag(False)} 资源目录不存在: {resource_path}")
        return []

    candidates: list[tuple[str, Path]] = []
    seen: set[str] = set()

    def enqueue(name: str, base_dir: Path) -> None:
        normalized_name = name.strip()
        if not normalized_name or normalized_name in seen:
            return
        seen.add(normalized_name)
        candidates.append((normalized_name, base_dir))

    if course_name:
        preferred_dir = resource_path / course_name
        base_dir = preferred_dir if preferred_dir.exists() else resource_path
        enqueue(course_name, base_dir)
        return candidates

    enqueue("大数据技术与应用", resource_path)
    ignore_dirs = {"PPT", "教学视频", "电子教材", "作业库(excel)", "作业库"}
    for directory in resource_path.iterdir():
        if not directory.is_dir() or directory.name in ignore_dirs:
            continue
        enqueue(directory.name, directory)
    return candidates
