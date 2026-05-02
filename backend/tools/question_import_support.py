#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
题库导入辅助工具兼容门面。

具体清洗、答案归一化、Excel/JSON 适配、知识点绑定与持久化实现已拆分到
`question_import_*` 模块；本文件保留历史导入路径，避免影响 tools.questions。
"""
from __future__ import annotations

from tools.question_import_answers import (
    ANSWER_SEPARATOR_PATTERN,
    FALSE_OPTION_TEXTS,
    TRUE_OPTION_TEXTS,
    build_excel_answer,
    normalize_question_answer,
    normalize_true_false_options,
)
from tools.question_import_excel import (
    DIFFICULTY_MAP,
    TYPE_MAP,
    build_excel_options,
    build_excel_question_payload,
    extract_question_content,
    iter_excel_question_payloads,
    open_question_bank_workbook,
    row_get,
)
from tools.question_import_json import (
    build_json_question_payload,
    load_question_json_source,
    validate_question_json_payload,
)
from tools.question_import_knowledge import (
    LEADING_DIGITS_PATTERN,
    build_question_import_context,
    link_question_knowledge_points,
    match_knowledge_point_by_topic,
    normalize_knowledge_point_names,
    resolve_filename_knowledge_point,
)
from tools.question_import_records import create_question_from_payload
from tools.question_import_text import (
    clean_question_options,
    strip_import_answer_payload,
    strip_import_text,
)
from tools.question_import_types import (
    QuestionBankWorkbook,
    QuestionImportContext,
    QuestionImportSummary,
    QuestionPayload,
)

_build_excel_answer = build_excel_answer
_build_excel_options = build_excel_options
_normalize_true_false_options = normalize_true_false_options
_row_get = row_get
_validate_question_json_payload = validate_question_json_payload

__all__ = [
    "ANSWER_SEPARATOR_PATTERN",
    "DIFFICULTY_MAP",
    "FALSE_OPTION_TEXTS",
    "LEADING_DIGITS_PATTERN",
    "QuestionBankWorkbook",
    "QuestionImportContext",
    "QuestionImportSummary",
    "QuestionPayload",
    "TRUE_OPTION_TEXTS",
    "TYPE_MAP",
    "_build_excel_answer",
    "_build_excel_options",
    "_normalize_true_false_options",
    "_row_get",
    "_validate_question_json_payload",
    "build_excel_answer",
    "build_excel_options",
    "build_excel_question_payload",
    "build_json_question_payload",
    "build_question_import_context",
    "clean_question_options",
    "create_question_from_payload",
    "extract_question_content",
    "iter_excel_question_payloads",
    "link_question_knowledge_points",
    "load_question_json_source",
    "match_knowledge_point_by_topic",
    "normalize_knowledge_point_names",
    "normalize_question_answer",
    "normalize_true_false_options",
    "open_question_bank_workbook",
    "resolve_filename_knowledge_point",
    "row_get",
    "strip_import_answer_payload",
    "strip_import_text",
    "validate_question_json_payload",
]
