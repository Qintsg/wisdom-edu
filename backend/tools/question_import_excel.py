#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
题库 Excel 导入适配工具。

负责工作簿打开、sheet 迭代、列名识别以及 Excel 行到标准题目载荷的转换。
"""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from tools.common import clean_nan, resolve_path, safe_float
from tools.question_import_answers import build_excel_answer, normalize_true_false_options
from tools.question_import_knowledge import normalize_knowledge_point_names
from tools.question_import_text import strip_import_text
from tools.question_import_types import QuestionBankWorkbook, QuestionPayload


TYPE_MAP: dict[str, str] = {
    "单选题": "single_choice",
    "单选": "single_choice",
    "多选题": "multiple_choice",
    "多选": "multiple_choice",
    "判断题": "true_false",
    "判断": "true_false",
    "填空题": "fill_blank",
    "填空": "fill_blank",
    "简答题": "short_answer",
    "简答": "short_answer",
    "编程题": "code",
    "编程": "code",
}
DIFFICULTY_MAP: dict[str, str] = {
    "易": "easy",
    "简单": "easy",
    "中": "medium",
    "中等": "medium",
    "难": "hard",
    "困难": "hard",
}


def row_get(row: object, key: str) -> object:
    """安全读取 pandas Series 风格对象的字段。"""
    getter = getattr(row, "get", None)
    if callable(getter):
        return getter(key)
    return None


def extract_question_content(row: object, columns: list[str]) -> str:
    """从 Excel 行数据中提取题干文本。"""
    if "大题题干" in columns:
        return clean_nan(row_get(row, "小题题干")) or clean_nan(row_get(row, "大题题干")) or ""
    if "题干" in columns:
        return clean_nan(row_get(row, "题干") or "")
    for column_name in columns:
        if any(keyword in str(column_name) for keyword in ["题目", "content", "内容"]):
            return clean_nan(row_get(row, column_name) or "")
    return ""


def build_excel_options(row: object, columns: list[str]) -> list[dict[str, str]]:
    """从 Excel 行中提取选项列表。"""
    options: list[dict[str, str]] = []
    for index in range(26):
        label = chr(ord("A") + index)
        option_key = f"选项{label}" if f"选项{label}" in columns else label
        raw_option = row_get(row, option_key)
        if raw_option is None:
            continue
        option_text = str(strip_import_text(clean_nan(raw_option)) or "")
        if option_text:
            options.append({"label": label, "content": option_text})
    return options


def build_excel_question_payload(
    row: object,
    columns: list[str],
    *,
    for_initial_assessment: bool,
) -> QuestionPayload | None:
    """将 Excel 行数据转换为统一题目载荷。"""
    content = str(strip_import_text(extract_question_content(row, columns)) or "")
    if not content:
        return None

    question_type_text = (
        clean_nan(row_get(row, "小题题型"))
        or clean_nan(row_get(row, "题型"))
        or clean_nan(row_get(row, "题目类型"))
        or ""
    )
    question_type = TYPE_MAP.get(question_type_text, "single_choice")
    difficulty_text = clean_nan(row_get(row, "难易度")) or clean_nan(row_get(row, "难度")) or ""
    difficulty = DIFFICULTY_MAP.get(difficulty_text, "medium")
    raw_options = build_excel_options(row, columns)
    answer_text = str(
        strip_import_text(clean_nan(row_get(row, "正确答案")) or clean_nan(row_get(row, "答案")) or "") or ""
    )
    return QuestionPayload(
        content=content,
        question_type=question_type,
        options=normalize_true_false_options(question_type, raw_options),
        answer=build_excel_answer(question_type, answer_text),
        analysis=str(
            strip_import_text(clean_nan(row_get(row, "答案解析")) or clean_nan(row_get(row, "解析")) or "") or ""
        ),
        difficulty=difficulty,
        score=safe_float(
            clean_nan(row_get(row, "分值"))
            or clean_nan(row_get(row, "建议分数"))
            or clean_nan(row_get(row, "得分"))
            or clean_nan(row_get(row, "分数")),
            default=1.0,
        ),
        chapter=clean_nan(row_get(row, "目录")) or clean_nan(row_get(row, "章节")) or None,
        knowledge_point_names=normalize_knowledge_point_names(clean_nan(row_get(row, "知识点") or "")),
        for_initial_assessment=for_initial_assessment,
    )


def open_question_bank_workbook(file_source: object, pandas_module: object) -> QuestionBankWorkbook:
    """打开 Excel 题库数据源，兼容路径与上传文件对象。"""
    excel_file_factory = getattr(pandas_module, "ExcelFile", None)
    if not callable(excel_file_factory):
        raise TypeError("pandas 模块缺少 ExcelFile")

    if isinstance(file_source, Path):
        file_source = str(file_source)

    if isinstance(file_source, str):
        path = resolve_path(file_source)
        if not path.exists():
            raise FileNotFoundError(f"错误：文件不存在 - {path}")
        return QuestionBankWorkbook(
            display_name=path.name,
            stem=path.stem,
            excel_file=excel_file_factory(path),
        )

    display_name = getattr(file_source, "name", "")
    if display_name:
        return QuestionBankWorkbook(
            display_name=str(display_name),
            stem=Path(str(display_name)).stem,
            excel_file=excel_file_factory(file_source),
        )

    raise TypeError("Excel 题库仅支持文件路径、Path 对象或上传文件对象")


def iter_excel_question_payloads(
    workbook: QuestionBankWorkbook,
    pandas_module: object,
    *,
    for_initial_assessment: bool,
) -> Iterator[QuestionPayload]:
    """迭代 Excel 工作簿中的标准化题目载荷。"""
    read_excel = getattr(pandas_module, "read_excel", None)
    if not callable(read_excel):
        raise TypeError("pandas 模块缺少 read_excel")

    sheet_names = list(getattr(workbook.excel_file, "sheet_names", []))
    for sheet_name in sheet_names:
        dataframe = read_excel(workbook.excel_file, sheet_name=sheet_name)
        if bool(getattr(dataframe, "empty", False)):
            continue

        columns = [str(column) for column in getattr(dataframe, "columns", [])]
        iterrows = getattr(dataframe, "iterrows", None)
        if not callable(iterrows):
            continue
        for _, row in iterrows():
            payload = build_excel_question_payload(
                row,
                columns,
                for_initial_assessment=for_initial_assessment,
            )
            if payload is not None:
                yield payload
