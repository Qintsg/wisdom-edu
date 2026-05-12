#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
课程资源一键导入模块。
@Project : wisdom-edu
@File : bootstrap.py
@Author : Qintsg
@Date : 2026-03-23
"""

from typing import Optional

from courses.models import Course

from tools.common import build_course_asset_bundle
from tools.bootstrap_support import (
    bundle_has_importable_assets,
    collect_batch_candidates,
    ensure_course_record,
    ensure_teacher,
    finalize_bootstrap_course,
    import_bundle_knowledge_assets,
    import_bundle_media_assets,
    import_bundle_question_assets,
    import_bundle_resource_assets,
    import_media_resources,
    resolve_batch_resource_root,
    resolve_resources_root,
)
from tools.testing import _status_flag

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
    root = resolve_resources_root(resources_root)

    teacher_obj = ensure_teacher(teacher)
    course = ensure_course_record(course_name, teacher_obj)

    bundle = build_course_asset_bundle(course_name=course_name, base_dir=root)

    if not bundle_has_importable_assets(bundle):
        raise FileNotFoundError(
            f"未找到课程[{course_name}]的可导入资源，请检查目录: {root}"
        )

    import_bundle_knowledge_assets(
        bundle=bundle,
        course=course,
        replace=replace,
        dry_run=dry_run,
    )
    import_bundle_question_assets(
        bundle=bundle,
        course=course,
        replace=replace,
        dry_run=dry_run,
    )
    import_bundle_resource_assets(
        bundle=bundle,
        course=course,
        replace=replace,
        dry_run=dry_run,
    )
    import_bundle_media_assets(
        bundle=bundle,
        course=course,
        teacher_obj=teacher_obj,
        dry_run=dry_run,
    )
    finalize_bootstrap_course(
        course=course,
        sync_graph=sync_graph,
        dry_run=dry_run,
    )

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
    resource_path = resolve_batch_resource_root()

    print(f"开始导入课程资源...")
    print(f"  资源根目录: {resource_path}")

    candidates = collect_batch_candidates(
        resource_path=resource_path,
        course_name=course_name,
    )

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
