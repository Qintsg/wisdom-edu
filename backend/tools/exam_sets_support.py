#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""套题导入的 Excel 读取、题库匹配与建卷辅助逻辑。"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from django.db import transaction

from assessments.models import Question
from courses.models import Course
from exams.models import Exam, ExamQuestion
from exams.score_policy import sync_exam_totals
from knowledge.models import KnowledgePoint
from tools.common import clean_nan, split_multi_values
from tools.questions import _strip_html
from tools.testing import _status_flag


# 维护意图：套题导入过程中可复用的课程、题库和依赖模块
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class ExamSetImportContext:
    """套题导入过程中可复用的课程、题库和依赖模块。"""

    course: Course
    knowledge_point_map: dict[str, KnowledgePoint]
    question_by_content: dict[str, Question]
    question_by_normalized_content: dict[str, Question]
    pandas_module: ModuleType


# 维护意图：单个 Excel 文件的导入结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class ExamSetImportResult:
    """单个 Excel 文件的导入结果。"""

    created: bool
    question_count: int


# 维护意图：加载 pandas 依赖。
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_pandas_module() -> ModuleType | None:
    """
    加载 pandas 依赖。
    :return: pandas 模块对象；依赖缺失时返回 None。
    """
    try:
        import pandas as pandas_module
    except ImportError:
        print("请先安装 pandas openpyxl xlrd")
        return None
    return pandas_module


# 维护意图：归一化题干文本，消除 Excel 与题库中的空白差异。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_question_content(content: str) -> str:
    """
    归一化题干文本，消除 Excel 与题库中的空白差异。
    :param content: 原始题干。
    :return: 删除空白后的题干。
    """
    return re.sub(r"\s+", "", content)


# 维护意图：解析当前 sheet 中可能承载题干的列名。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_content_columns(columns: list[str]) -> list[str]:
    """
    解析当前 sheet 中可能承载题干的列名。
    :param columns: 当前 sheet 的列名列表。
    :return: 按优先级排序的题干列名。
    """
    if "大题题干" in columns:
        return ["小题题干", "大题题干"]

    if "题干" in columns:
        return ["题干"]

    return [
        column_name
        for column_name in columns
        if any(keyword in str(column_name) for keyword in ["题目", "content", "内容"])
    ]


# 维护意图：从单行 Excel 数据中提取题干。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_row_content(row: Any, columns: list[str]) -> str:
    """
    从单行 Excel 数据中提取题干。
    :param row: pandas 行对象。
    :param columns: 当前 sheet 的列名列表。
    :return: 清洗后的题干文本，未命中时返回空字符串。
    """
    for column_name in resolve_content_columns(columns):
        content = clean_nan(row.get(column_name) or "")
        if content:
            return content
    return ""


# 维护意图：解析知识点名称对应的知识点对象。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_knowledge_point(
    knowledge_point_name: str,
    course: Course,
    knowledge_point_map: dict[str, KnowledgePoint],
) -> KnowledgePoint | None:
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


# 维护意图：根据 Excel 知识点列补齐题目知识点关联。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def bind_question_knowledge_points(
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
        matched_point = resolve_knowledge_point(
            knowledge_point_name,
            course,
            knowledge_point_map,
        )
        if matched_point:
            question.knowledge_points.add(matched_point)


# 维护意图：读取单个 sheet，并把无法解析的 sheet 当作可跳过输入。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def read_excel_sheet(file_path: Path, sheet_name: str, pandas_module: ModuleType) -> Any | None:
    """
    读取单个 sheet，并把无法解析的 sheet 当作可跳过输入。
    :param file_path: Excel 文件路径。
    :param sheet_name: sheet 名称。
    :param pandas_module: pandas 模块引用。
    :return: pandas DataFrame；读取失败时返回 None。
    """
    try:
        return pandas_module.read_excel(file_path, sheet_name=sheet_name)
    except ValueError:
        return None


# 维护意图：逐行遍历 Excel 中非空 sheet 的数据行。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def iter_excel_rows(
    file_path: Path,
    excel_file: Any,
    pandas_module: ModuleType,
) -> Iterator[tuple[Any, list[str]]]:
    """
    逐行遍历 Excel 中非空 sheet 的数据行。
    :param file_path: Excel 文件路径。
    :param excel_file: pandas ExcelFile 对象。
    :param pandas_module: pandas 模块引用。
    :return: 迭代生成 `(row, columns)`。
    """
    for sheet_name in excel_file.sheet_names:
        dataframe = read_excel_sheet(file_path, sheet_name, pandas_module)
        if dataframe is None or dataframe.empty:
            continue

        columns = list(dataframe.columns)
        for _, row in dataframe.iterrows():
            yield row, columns


# 维护意图：预加载课程题库，避免每行 Excel 匹配时重复扫描数据库。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_question_lookup(course: Course) -> tuple[dict[str, Question], dict[str, Question]]:
    """
    预加载课程题库，避免每行 Excel 匹配时重复扫描数据库。
    :param course: 目标课程。
    :return: 原始题干映射与归一化题干映射。
    """
    question_by_content: dict[str, Question] = {}
    question_by_normalized_content: dict[str, Question] = {}
    questions = (
        Question.objects.filter(course=course)
        .prefetch_related("knowledge_points")
        .order_by("id")
    )
    for question in questions:
        question_by_content.setdefault(question.content, question)
        question_by_normalized_content.setdefault(
            normalize_question_content(question.content),
            question,
        )
    return question_by_content, question_by_normalized_content


# 维护意图：构建导入上下文，集中预加载后续流程共享的数据。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_import_context(course: Course, pandas_module: ModuleType) -> ExamSetImportContext:
    """
    构建导入上下文，集中预加载后续流程共享的数据。
    :param course: 目标课程。
    :param pandas_module: pandas 模块引用。
    :return: 套题导入上下文。
    """
    question_by_content, question_by_normalized_content = build_question_lookup(course)
    return ExamSetImportContext(
        course=course,
        knowledge_point_map={
            point.name: point
            for point in KnowledgePoint.objects.filter(course=course)
        },
        question_by_content=question_by_content,
        question_by_normalized_content=question_by_normalized_content,
        pandas_module=pandas_module,
    )


# 维护意图：通过内容匹配已导入的题目。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def match_question(content: str, context: ExamSetImportContext) -> Question | None:
    """
    通过内容匹配已导入的题目。
    :param content: 题目内容文本。
    :param context: 套题导入上下文。
    :return: 匹配到的 Question 对象，或 None。
    """
    if not content:
        return None

    matched_question = context.question_by_content.get(content)
    if matched_question:
        return matched_question

    return context.question_by_normalized_content.get(normalize_question_content(content))


# 维护意图：从 Excel 行中提取题干并匹配题库题目。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def match_row_question(row: Any, columns: list[str], context: ExamSetImportContext) -> Question | None:
    """
    从 Excel 行中提取题干并匹配题库题目。
    :param row: pandas 行对象。
    :param columns: 当前 sheet 的列名列表。
    :param context: 套题导入上下文。
    :return: 匹配到的题目；未匹配时返回 None。
    """
    question_content = _strip_html(extract_row_content(row, columns))
    if not question_content:
        return None

    matched_question = match_question(question_content, context)
    if not matched_question:
        return None

    bind_question_knowledge_points(
        matched_question,
        clean_nan(row.get("知识点") or ""),
        context.course,
        context.knowledge_point_map,
    )
    return matched_question


# 维护意图：读取单个 Excel 套题文件并匹配题目。
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_matched_questions(
    file_path: Path,
    excel_file: Any,
    context: ExamSetImportContext,
) -> list[Question]:
    """
    读取单个 Excel 套题文件并匹配题目。
    :param file_path: 当前导入的 Excel 文件路径。
    :param excel_file: pandas ExcelFile 对象。
    :param context: 套题导入上下文。
    :return: 当前文件匹配到的题目列表。
    """
    matched_questions: list[Question] = []
    for row, columns in iter_excel_rows(file_path, excel_file, context.pandas_module):
        matched_question = match_row_question(row, columns, context)
        if matched_question:
            matched_questions.append(matched_question)
    return matched_questions


# 维护意图：收集套题关联的知识点名称。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def collect_question_knowledge_point_names(questions: list[Question]) -> list[str]:
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


# 维护意图：打开 Excel 文件。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def open_excel_file(file_path: Path, pandas_module: ModuleType) -> Any | None:
    """
    打开 Excel 文件。
    :param file_path: Excel 文件路径。
    :param pandas_module: pandas 模块引用。
    :return: pandas ExcelFile 对象；读取失败时返回 None。
    """
    try:
        return pandas_module.ExcelFile(file_path)
    except Exception as exc:
        print(f"  {_status_flag(False)} 读取失败 {file_path.name}: {exc}")
        return None


# 维护意图：判断同名套题是否已存在。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def question_set_exists(course: Course, exam_title: str) -> bool:
    """
    判断同名套题是否已存在。
    :param course: 目标课程。
    :param exam_title: 套题标题。
    :return: 存在返回 True。
    """
    return Exam.objects.filter(
        course=course,
        exam_type="question_set",
        title=exam_title,
    ).exists()


# 维护意图：根据匹配到的题目创建套题。
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def create_exam_set(
    course: Course,
    exam_title: str,
    file_path: Path,
    matched_questions: list[Question],
) -> Exam:
    """
    根据匹配到的题目创建套题。
    :param course: 目标课程。
    :param exam_title: 套题标题。
    :param file_path: 来源 Excel 文件路径。
    :param matched_questions: 已匹配题目。
    :return: 新建的 Exam 对象。
    """
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
        ExamQuestion.objects.bulk_create(
            [
                ExamQuestion(
                    exam=exam,
                    question=question,
                    score=question.score or 1,
                    order=order,
                )
                for order, question in enumerate(matched_questions)
            ]
        )
        sync_exam_totals(exam)
    return exam
