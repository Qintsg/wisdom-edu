#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
课程资源一键导入模块。
@Project : wisdom-edu
@File : bootstrap.py
@Author : Qintsg
@Date : 2026-03-23
"""

import shutil
from pathlib import Path
from typing import Optional

from django.conf import settings

from users.models import User
from courses.models import Course
from knowledge.models import Resource

from tools.common import (
    BASE_DIR,
    COURSE_RESOURCES_DIR,
    resolve_path,
    build_course_asset_bundle, CourseAssetBundle,
)
from tools.testing import _status_flag
from tools.knowledge import import_knowledge, import_knowledge_map
from tools.questions import import_question_bank
from tools.resources import import_resources_json


def _ensure_teacher(username: str) -> User:
    """
    校验教师账号是否存在。
    :param username: 教师用户名。
    :return: 教师用户对象。
    """
    teacher = User.objects.filter(username=username).first()
    if not teacher:
        raise ValueError(f"教师不存在: {username}")
    return teacher


def _copy_to_media(source_path: Path, sub_dir: str = "resources") -> str:
    """
    将文件复制到 MEDIA_ROOT 下并返回相对路径。
    :param source_path: 源文件路径。
    :param sub_dir: media 下的子目录。
    :return: 相对于 MEDIA_ROOT 的路径字符串。
    """
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
            # 统一使用相对 MEDIA_ROOT 的正斜杠路径，兼容 Windows 上传记录。
    return str(dest_path.relative_to(media_root)).replace("\\", "/")


def _bundle_has_importable_assets(bundle: CourseAssetBundle) -> bool:
    """
    判断课程资源包是否包含可导入资源。
    :param bundle: 课程资源包描述对象。
    :return: True 表示至少存在一种可导入资源。
    """
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


def _import_media_resources(
    course: Course,
    teacher_obj: User,
    file_paths: list[Path],
    resource_type: str,
    sub_dir: str,
    description_prefix: str,
    chapter_from_parent: bool = False,
) -> None:
    """
    导入文件型课程资源。
    :param course: 目标课程对象。
    :param teacher_obj: 上传教师对象。
    :param file_paths: 待导入文件列表。
    :param resource_type: 资源类型。
    :param sub_dir: MEDIA 子目录。
    :param description_prefix: 资源描述前缀。
    :param chapter_from_parent: 是否从父目录提取章节号。
    :return: None。
    """
    if not file_paths:
        return

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
            course=course, title=title, resource_type=resource_type
        ).exists():
            continue

        relative_path = _copy_to_media(file_path, sub_dir=sub_dir)
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
        sort_order += 1


def bootstrap_course_assets(
    course_name: str,
    teacher: str = "teacher1",
    replace: bool = True,
    sync_graph: bool = False,
    dry_run: bool = False,
    resources_root: Optional[str] = None,
):
    """
    一键导入课程资源包。
    :param course_name: 课程名称。
    :param teacher: 教师用户名。
    :param replace: 是否覆盖已有资源。
    :param sync_graph: 是否同步 Neo4j 图谱。
    :param dry_run: 是否仅预览导入动作。
    :param resources_root: 自定义资源根目录。
    :return: None。
    """
    from tools.neo4j_tools import sync_neo4j
    from tools.rag_index import refresh_rag_corpus
    from assessments.models import Question

    if not resources_root:
        root = COURSE_RESOURCES_DIR
    else:
        root = resolve_path(resources_root)

    teacher_obj = _ensure_teacher(teacher)

    course = Course.objects.filter(name=course_name).first()
    if not course:
        course = Course.objects.create(
            name=course_name,
            description=f"{course_name} 样例课程（从资源目录导入）",
            created_by=teacher_obj,
            is_public=True,
        )

    bundle = build_course_asset_bundle(course_name=course_name, base_dir=root)

    if not _bundle_has_importable_assets(bundle):
        raise FileNotFoundError(
            f"未找到课程[{course_name}]的可导入资源，请检查目录: {root}"
        )

    # 知识图谱
    if bundle.knowledge_file:
        suffix = bundle.knowledge_file.suffix.lower()
        if suffix == ".json":
            import_knowledge(
                str(bundle.knowledge_file),
                int(course.pk),
                replace=replace,
                dry_run=dry_run,
            )
        elif suffix in [".xlsx", ".xls"]:
            if dry_run:
                print(f"[DRY-RUN] 将导入知识图谱Excel: {bundle.knowledge_file}")
            else:
                import_knowledge_map(
                    str(bundle.knowledge_file), course_id=int(course.pk)
                )

    # 题库
    if replace and not dry_run:
        if bundle.initial_assessment_file or bundle.homework_files:
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

    for hw_path in bundle.homework_files:
        if dry_run:
            print(f"[DRY-RUN] 将导入作业库: {hw_path}")
        else:
            import_question_bank(
                str(hw_path), int(course.pk), for_initial_assessment=False
            )

    # 套题(ExamSet) —— 基于已导入的题目创建章节套题
    if bundle.homework_files and not dry_run:
        from tools.exam_sets import import_exam_sets

        hw_dir = bundle.homework_files[0].parent
        import_exam_sets(int(course.pk), str(hw_dir), replace=replace)
    elif bundle.homework_files and dry_run:
        print(f"[DRY-RUN] 将从作业库创建套题")

    # 资源 JSON
    if bundle.resources_file:
        if bundle.resources_file.suffix.lower() == ".json":
            import_resources_json(
                str(bundle.resources_file),
                int(course.pk),
                replace=replace,
                dry_run=dry_run,
            )

    # PPT
    if bundle.ppt_files:
        if dry_run:
            print(f"[DRY-RUN] 将导入 {len(bundle.ppt_files)} 个PPT文件")
        else:
            _import_media_resources(
                course=course,
                teacher_obj=teacher_obj,
                file_paths=bundle.ppt_files,
                resource_type="document",
                sub_dir="resources/ppt",
                description_prefix="课程PPT",
                chapter_from_parent=True,
            )
            print(f"  PPT资源导入: {len(bundle.ppt_files)} 个文件")

    # 视频
    if bundle.video_files:
        if dry_run:
            print(f"[DRY-RUN] 将导入 {len(bundle.video_files)} 个视频")
        else:
            _import_media_resources(
                course=course,
                teacher_obj=teacher_obj,
                file_paths=bundle.video_files,
                resource_type="video",
                sub_dir="resources/video",
                description_prefix="教学视频",
            )
            print(f"  视频资源导入: {len(bundle.video_files)} 个文件")

    # 电子教材
    if bundle.textbook_files:
        if dry_run:
            print(f"[DRY-RUN] 将导入 {len(bundle.textbook_files)} 个电子教材")
        else:
            _import_media_resources(
                course=course,
                teacher_obj=teacher_obj,
                file_paths=bundle.textbook_files,
                resource_type="document",
                sub_dir="resources/textbook",
                description_prefix="电子教材",
            )
            print(f"  电子教材导入: {len(bundle.textbook_files)} 个文件")

    # Neo4j 同步
    if sync_graph and not dry_run:
        result = sync_neo4j(int(course.pk))
        if not result or result.get("nodes", 0) <= 0:
            raise RuntimeError(f"课程 {course.name} 的 Neo4j 图数据同步失败或为空")

    if not dry_run:
        refresh_rag_corpus(course_id=int(course.pk))

    print(
        f"课程样例导入完成: teacher={teacher_obj.username}, "
        f"course_id={course.pk}, course={course.name}, root={root}"
    )


# ── 批量导入课程资源 ──


def import_course_resources(course_name: Optional[str] = None):
    """
    从资料目录批量导入课程资源。
    :param course_name: 指定要导入的课程名称，None 表示导入全部课程。
    :return: None。
    """
    import os
    from typing import List, Tuple

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
        print(f"  {_status_flag(False)} 环境变量资源目录不可用，回退到内置目录: {resource_path}")
        resource_path = COURSE_RESOURCES_DIR

    print(f"开始导入课程资源...")
    print(f"  资源根目录: {resource_path}")

    # 构造候选课程列表
    candidates: List[Tuple[str, Path]] = []
    seen: set = set()

    def _enqueue(name: str, base: Path):
        key = name.strip()
        if not key or key in seen:
            return
        seen.add(key)
        candidates.append((key, base))

    if resource_path.exists():
        if course_name:
            preferred_dir = resource_path / course_name
            base_dir = preferred_dir if preferred_dir.exists() else resource_path
            _enqueue(course_name, base_dir)

        if not course_name:
            _enqueue("大数据技术与应用", resource_path)

        ignore_dirs = {"PPT", "教学视频", "电子教材", "作业库(excel)", "作业库"}
        for d in resource_path.iterdir():
            if not d.is_dir() or d.name in ignore_dirs:
                continue
            if course_name and d.name != course_name:
                continue
            _enqueue(d.name, d)
    else:
        print(f"  {_status_flag(False)} 资源目录不存在: {resource_path}")
        return

    # 3. 执行导入
    if not candidates:
        print(
            f"  {_status_flag(False)} 未找到可导入的课程资源，请检查目录结构或课程名。"
        )
        return

    for cand, base_dir in candidates:
        print(f"\n[导入] 课程: {cand} (搜索目录: {base_dir})")
        try:
            bootstrap_course_assets(
                course_name=cand,
                teacher="teacher1",
                replace=True,
                sync_graph=True,
                dry_run=False,
                resources_root=str(base_dir),
            )
            print(f"  {_status_flag(True)} 导入完成")
        except FileNotFoundError as e:
            print(f"  {_status_flag(False)} 课程[{cand}]未找到可导入资源: {e}")
        except Exception as e:
            print(f"  {_status_flag(False)} 课程[{cand}]导入失败或非课程目录: {e}")
