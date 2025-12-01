#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
套题导入工具。
@Project : wisdom-edu
@File : exam_sets.py
@Author : Qintsg
@Date : 2026-03-23
"""

"""从作业库 Excel 导入阶段测试套题，并绑定已有题库记录。"""

import re
from pathlib import Path
from typing import Optional

from django.db import transaction

from assessments.models import Question
from courses.models import Course
from exams.models import Exam, ExamQuestion
from exams.score_policy import sync_exam_totals
from knowledge.models import KnowledgePoint
from tools.common import (
    COURSE_RESOURCES_DIR,
    clean_nan,
    get_course,
    resolve_path,
    split_multi_values,
)
from tools.questions import _strip_html
from tools.testing import _status_flag


def _resolve_homework_path(homework_dir: Optional[str]) -> Path:
    """
    解析作业库目录。
    :param homework_dir: 用户显式传入的作业库目录。
    :return: 最终用于扫描 Excel 文件的目录路径。
    """
    if homework_dir:
        return resolve_path(homework_dir)
    return COURSE_RESOURCES_DIR / "作业库(excel)"


def _collect_excel_files(homework_path: Path) -> list[Path]:
    """
    收集目录下全部 Excel 文件。
    :param homework_path: 作业库目录。
    :return: 按文件名排序后的 Excel 文件列表。
    """
    return sorted(list(homework_path.glob("*.xlsx")) + list(homework_path.glob("*.xls")))


def _build_exam_title(set_name: str) -> str:
    """
    根据文件名推导章节标题。
    :param set_name: Excel 文件名去后缀后的文本。
    :return: 统一格式的套题标题。
    """
    chapter_match = re.match(r"^(\d+)(.*)", set_name)
    chapter_number = chapter_match.group(1) if chapter_match else ""
    chapter_name = chapter_match.group(2).strip() if chapter_match else set_name
    return f"第{chapter_number}章 {chapter_name}" if chapter_number else chapter_name


def _extract_row_content(row, columns: list[str]) -> str:
    """
    从单行 Excel 数据中提取题干。
    :param row: pandas 行对象。
    :param columns: 当前 sheet 的列名列表。
    :return: 清洗后的题干文本，未命中时返回空字符串。
    """
    if "大题题干" in columns:
        return clean_nan(row.get("小题题干")) or clean_nan(row.get("大题题干")) or ""

    if "题干" in columns:
        return clean_nan(row.get("题干") or "")

    for column_name in columns:
        if any(keyword in str(column_name) for keyword in ["题目", "content", "内容"]):
            return clean_nan(row.get(column_name) or "")

    return ""


def _resolve_knowledge_point(
    knowledge_point_name: str,
    course: Course,
    knowledge_point_map: dict[str, KnowledgePoint],
) -> Optional[KnowledgePoint]:
    """
    解析知识点名称对应的知识点对象。
    :param knowledge_point_name: Excel 中读取到的知识点名称。
    :param course: 所属课程。
    :param knowledge_point_map: 已预加载的知识点映射。
    :return: 匹配到的知识点对象，未匹配时返回 None。
    """
    matched_point = knowledge_point_map.get(knowledge_point_name)
    if matched_point:
        return matched_point

    return KnowledgePoint.objects.filter(
        course=course,
        name__icontains=knowledge_point_name,
    ).first()


def _bind_question_knowledge_points(
    question: Question,
    knowledge_point_cell: str,
    course: Course,
    knowledge_point_map: dict[str, KnowledgePoint],
) -> None:
    """
    根据 Excel 知识点列补齐题目知识点关联。
    :param question: 已匹配到的题目对象。
    :param knowledge_point_cell: Excel 单元格中的知识点文本。
    :param course: 所属课程。
    :param knowledge_point_map: 已预加载的知识点映射。
    :return: None。
    """
    if not knowledge_point_cell or question.knowledge_points.exists():
        return

    for knowledge_point_name in split_multi_values(knowledge_point_cell):
        matched_point = _resolve_knowledge_point(
            knowledge_point_name,
            course,
            knowledge_point_map,
        )
        if matched_point:
            question.knowledge_points.add(matched_point)


def _load_matched_questions(
    file_path: Path,
    excel_file,
    course: Course,
    knowledge_point_map: dict[str, KnowledgePoint],
    pandas_module,
) -> list[Question]:
    """
    读取单个 Excel 套题文件并匹配题目。
    :param file_path: 当前导入的 Excel 文件路径。
    :param excel_file: pandas ExcelFile 对象。
    :param course: 所属课程。
    :param knowledge_point_map: 已预加载的知识点映射。
    :param pandas_module: pandas 模块引用。
    :return: 当前文件匹配到的题目列表。
    """
    matched_questions: list[Question] = []

    for sheet_name in excel_file.sheet_names:
        try:
            dataframe = pandas_module.read_excel(file_path, sheet_name=sheet_name)
        except ValueError:
            continue
        if dataframe.empty:
            continue

        columns = list(dataframe.columns)
        for _, row in dataframe.iterrows():
            question_content = _strip_html(_extract_row_content(row, columns))
            if not question_content:
                continue

            matched_question = _match_question(question_content, course)
            if not matched_question:
                continue

            _bind_question_knowledge_points(
                matched_question,
                clean_nan(row.get("知识点") or ""),
                course,
                knowledge_point_map,
            )
            matched_questions.append(matched_question)

    return matched_questions


def _collect_question_knowledge_point_names(questions: list[Question]) -> list[str]:
    """
    收集套题关联的知识点名称。
    :param questions: 已匹配的题目列表。
    :return: 排序后的知识点名称列表。
    """
    knowledge_point_names: set[str] = set()
    for question in questions:
        for knowledge_point in question.knowledge_points.all():
            knowledge_point_names.add(knowledge_point.name)
    return sorted(knowledge_point_names)


def _match_question(content: str, course: Course) -> Optional[Question]:
    """通过内容匹配已导入的题目

    Args:
        content: 题目内容文本
        course: 所属课程

    Returns:
        匹配到的 Question 对象，或 None
    """
    if not content:
        return None

    question = Question.objects.filter(course=course, content=content).first()
    if question:
        return question

    normalized = re.sub(r"\s+", "", content)
    for candidate in Question.objects.filter(course=course):
        if re.sub(r"\s+", "", candidate.content) == normalized:
            return candidate

    return None


def import_exam_sets(
    course_id: int,
    homework_dir: Optional[str] = None,
    replace: bool = False,
    dry_run: bool = False,
):
    """
    从作业库 Excel 目录导入套题。
    :param course_id: 课程 ID。
    :param homework_dir: 作业库目录路径，留空时使用默认目录。
    :param replace: 是否先删除已有套题再重建。
    :param dry_run: 是否仅预览导入目标而不执行写入。
    :return: None。
    """
    try:
        import pandas as pd
    except ImportError:
        print("请先安装 pandas openpyxl xlrd")
        return

    course: Course = get_course(course_id)

    hw_path = _resolve_homework_path(homework_dir)
    if not hw_path.exists():
        print(f"作业库目录不存在: {hw_path}")
        return

    files = _collect_excel_files(hw_path)
    if not files:
        print(f"作业库目录中没有Excel文件: {hw_path}")
        return

    if dry_run:
        print(f"[DRY-RUN] 将从 {len(files)} 个文件创建套题")
        for file_path in files:
            print(f"  - {file_path.name}")
        return

    kp_map = {point.name: point for point in KnowledgePoint.objects.filter(course=course)}

    if replace:
        deleted = Exam.objects.filter(course=course, exam_type="question_set").delete()
        print(f"已清除旧套题: {deleted[0]} 条")

    total_sets = 0
    total_questions = 0

    for file_path in files:
        set_name = file_path.stem
        exam_title = _build_exam_title(set_name)

        if (
            not replace
            and Exam.objects.filter(
                course=course,
                exam_type="question_set",
                title=exam_title,
            ).exists()
        ):
            print(f"  跳过已存在的套题: {exam_title}")
            continue

        try:
            xls = pd.ExcelFile(file_path)
        except Exception as exc:
            print(f"  {_status_flag(False)} 读取失败 {file_path.name}: {exc}")
            continue

        matched_questions = _load_matched_questions(
            file_path,
            xls,
            course,
            kp_map,
            pd,
        )
        if not matched_questions:
            print(f"  {_status_flag(False)} {set_name}: 未匹配到任何题目，跳过")
            continue

        with transaction.atomic():
            exam = Exam.objects.create(
                course=course,
                title=exam_title,
                description=f"来自作业库 {file_path.name} 的套题",
                exam_type="question_set",
                total_score=0,
                pass_score=0,
                status="published",
            )

            for order, question in enumerate(matched_questions):
                ExamQuestion.objects.create(
                    exam=exam,
                    question=question,
                    score=question.score or 1,
                    order=order,
                )

            sync_exam_totals(exam)

        kp_names = _collect_question_knowledge_point_names(matched_questions)
        total_sets += 1
        total_questions += len(matched_questions)
        kp_info = f", 知识点: {', '.join(kp_names)}" if kp_names else ""
        print(f"  {_status_flag(True)} {exam_title}: {len(matched_questions)} 题{kp_info}")

    print(f"\n套题导入完成: {total_sets} 个套题, {total_questions} 道题目")
