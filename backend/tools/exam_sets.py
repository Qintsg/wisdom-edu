#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
套题导入工具。
@Project : wisdom-edu
@File : exam_sets.py
@Author : Qintsg
@Date : 2026-03-23
"""

from __future__ import annotations

import re
from pathlib import Path

from courses.models import Course
from exams.models import Exam
from tools.common import COURSE_RESOURCES_DIR, get_course, resolve_path
from tools.exam_sets_support import (
    ExamSetImportContext,
    ExamSetImportResult,
    build_import_context,
    collect_question_knowledge_point_names,
    create_exam_set,
    load_matched_questions,
    load_pandas_module,
    open_excel_file,
    question_set_exists,
)
from tools.testing import _status_flag


def resolve_homework_path(homework_dir: str | None) -> Path:
    """
    解析作业库目录。
    :param homework_dir: 用户显式传入的作业库目录。
    :return: 最终用于扫描 Excel 文件的目录路径。
    """
    if homework_dir:
        return resolve_path(homework_dir)
    return COURSE_RESOURCES_DIR / "作业库(excel)"


def collect_excel_files(homework_path: Path) -> list[Path]:
    """
    收集目录下全部 Excel 文件。
    :param homework_path: 作业库目录。
    :return: 按文件名排序后的 Excel 文件列表。
    """
    return sorted(list(homework_path.glob("*.xlsx")) + list(homework_path.glob("*.xls")))


def collect_import_files(homework_dir: str | None) -> list[Path]:
    """
    校验并收集本次要导入的作业库文件。
    :param homework_dir: 作业库目录路径，留空使用默认课程资源目录。
    :return: 可导入 Excel 文件列表。
    """
    homework_path = resolve_homework_path(homework_dir)
    if not homework_path.exists():
        print(f"作业库目录不存在: {homework_path}")
        return []

    files = collect_excel_files(homework_path)
    if not files:
        print(f"作业库目录中没有Excel文件: {homework_path}")
    return files


def build_exam_title(set_name: str) -> str:
    """
    根据文件名推导章节标题。
    :param set_name: Excel 文件名去后缀后的文本。
    :return: 统一格式的套题标题。
    """
    chapter_match = re.match(r"^(\d+)(.*)", set_name)
    chapter_number = chapter_match.group(1) if chapter_match else ""
    chapter_name = chapter_match.group(2).strip() if chapter_match else set_name
    return f"第{chapter_number}章 {chapter_name}" if chapter_number else chapter_name


def import_single_exam_file(
    file_path: Path,
    context: ExamSetImportContext,
    replace: bool,
) -> ExamSetImportResult:
    """
    导入单个 Excel 文件。
    :param file_path: Excel 文件路径。
    :param context: 套题导入上下文。
    :param replace: 是否已处于覆盖重建模式。
    :return: 单文件导入结果。
    """
    set_name = file_path.stem
    exam_title = build_exam_title(set_name)
    if not replace and question_set_exists(context.course, exam_title):
        print(f"  跳过已存在的套题: {exam_title}")
        return ExamSetImportResult(created=False, question_count=0)

    excel_file = open_excel_file(file_path, context.pandas_module)
    if excel_file is None:
        return ExamSetImportResult(created=False, question_count=0)

    matched_questions = load_matched_questions(file_path, excel_file, context)
    if not matched_questions:
        print(f"  {_status_flag(False)} {set_name}: 未匹配到任何题目，跳过")
        return ExamSetImportResult(created=False, question_count=0)

    create_exam_set(context.course, exam_title, file_path, matched_questions)
    kp_names = collect_question_knowledge_point_names(matched_questions)
    kp_info = f", 知识点: {', '.join(kp_names)}" if kp_names else ""
    print(f"  {_status_flag(True)} {exam_title}: {len(matched_questions)} 题{kp_info}")
    return ExamSetImportResult(created=True, question_count=len(matched_questions))


def print_dry_run(files: list[Path]) -> None:
    """
    打印 dry-run 预览结果。
    :param files: 将被导入的 Excel 文件列表。
    :return: None。
    """
    print(f"[DRY-RUN] 将从 {len(files)} 个文件创建套题")
    for file_path in files:
        print(f"  - {file_path.name}")


def clear_existing_question_sets(course: Course) -> None:
    """
    清理目标课程既有套题。
    :param course: 目标课程。
    :return: None。
    """
    deleted = Exam.objects.filter(course=course, exam_type="question_set").delete()
    print(f"已清除旧套题: {deleted[0]} 条")


def import_exam_sets(
    course_id: int,
    homework_dir: str | None = None,
    replace: bool = False,
    dry_run: bool = False,
) -> None:
    """
    从作业库 Excel 目录导入套题。
    :param course_id: 课程 ID。
    :param homework_dir: 作业库目录路径，留空时使用默认目录。
    :param replace: 是否先删除已有套题再重建。
    :param dry_run: 是否仅预览导入目标而不执行写入。
    :return: None。
    """
    pandas_module = load_pandas_module()
    if pandas_module is None:
        return

    course = get_course(course_id)
    files = collect_import_files(homework_dir)
    if not files:
        return

    if dry_run:
        print_dry_run(files)
        return

    context = build_import_context(course, pandas_module)
    if replace:
        clear_existing_question_sets(course)

    total_sets = 0
    total_questions = 0
    for file_path in files:
        result = import_single_exam_file(file_path, context, replace)
        if result.created:
            total_sets += 1
            total_questions += result.question_count

    print(f"\n套题导入完成: {total_sets} 个套题, {total_questions} 道题目")
