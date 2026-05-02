#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
题库导入辅助工具。

集中处理 HTML 清洗、题型/答案归一化、Excel/JSON 输入适配以及知识点绑定，
让 questions.py 只保留导入命令的事务编排。
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from html import unescape as html_unescape
from pathlib import Path
import re

from django.utils.html import strip_tags

from assessments.models import Question
from courses.models import Course
from knowledge.models import KnowledgePoint
from tools.common import clean_nan, load_json, resolve_path, safe_float, split_multi_values
from tools.knowledge import validate_json


ANSWER_SEPARATOR_PATTERN = re.compile(r"[,;，；\s]+")
LEADING_DIGITS_PATTERN = re.compile(r"^\d+")
WHITESPACE_PATTERN = re.compile(r"\s+")
TRUE_OPTION_TEXTS = {"正确", "对", "True", "true", "T"}
FALSE_OPTION_TEXTS = {"错误", "错", "False", "false", "F"}

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


@dataclass
class QuestionImportContext:
    """缓存课程知识点，避免导入过程重复查库。"""

    course: Course
    knowledge_points: list[KnowledgePoint]
    knowledge_point_map: dict[str, KnowledgePoint]


@dataclass
class QuestionImportSummary:
    """记录导入统计信息。"""

    imported_count: int = 0
    linked_count: int = 0
    skipped_duplicates: int = 0
    unmatched_names: set[str] = field(default_factory=set)

    def record_import(self, linked: bool) -> None:
        """记录单题导入结果。"""
        self.imported_count += 1
        if linked:
            self.linked_count += 1


@dataclass
class QuestionPayload:
    """标准化后的题目载荷。"""

    content: str
    question_type: str
    options: list[object]
    answer: dict[str, object]
    analysis: str
    difficulty: str
    score: float
    chapter: str | None
    knowledge_point_names: list[str] = field(default_factory=list)
    for_initial_assessment: bool = False
    is_visible: bool = True


@dataclass
class QuestionBankWorkbook:
    """Excel 题库数据源适配结果。"""

    display_name: str
    stem: str
    excel_file: object


def _validate_question_json_payload(payload: Mapping[str, object]) -> None:
    """验证题库 JSON 结构。"""
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise ValueError("题库JSON缺少 questions(list)")


def _row_get(row: object, key: str) -> object:
    """安全读取 pandas Series 风格对象的字段。"""
    getter = getattr(row, "get", None)
    if callable(getter):
        return getter(key)
    return None


def strip_import_text(value: object) -> object:
    """去除 HTML 标签并清理多余空白。"""
    if not value:
        return value
    text = strip_tags(str(value))
    text = html_unescape(text)
    text = text.replace("\xa0", " ")
    return WHITESPACE_PATTERN.sub(" ", text).strip()


def strip_import_answer_payload(answer: object) -> object:
    """清洗答案字段中的 HTML。"""
    if isinstance(answer, str):
        return strip_import_text(answer)
    if isinstance(answer, Mapping):
        cleaned_payload: dict[str, object] = {}
        for key, value in answer.items():
            if isinstance(value, str):
                cleaned_payload[str(key)] = strip_import_text(value)
                continue
            if isinstance(value, list):
                cleaned_payload[str(key)] = [
                    strip_import_text(item) if isinstance(item, str) else item
                    for item in value
                ]
                continue
            cleaned_payload[str(key)] = value
        return cleaned_payload
    return answer


def normalize_question_answer(answer: object) -> dict[str, object]:
    """将题目答案规整为 Question 模型使用的统一 JSON 结构。"""
    cleaned_answer = strip_import_answer_payload(answer)
    if isinstance(cleaned_answer, Mapping):
        return {str(key): value for key, value in cleaned_answer.items()}
    if isinstance(cleaned_answer, Sequence) and not isinstance(cleaned_answer, (str, bytes, bytearray)):
        return {"answers": list(cleaned_answer)}
    return {"answer": cleaned_answer}


def clean_question_options(raw_options: object) -> list[object]:
    """清洗 JSON 题目中的选项内容。"""
    if not isinstance(raw_options, list):
        return []

    cleaned_options: list[object] = []
    for option in raw_options:
        if isinstance(option, Mapping):
            cleaned_option = {
                str(key): (strip_import_text(value) if isinstance(value, str) else value)
                for key, value in option.items()
            }
            cleaned_options.append(cleaned_option)
            continue
        if isinstance(option, str):
            cleaned_options.append(strip_import_text(option))
            continue
        cleaned_options.append(option)
    return cleaned_options


def extract_question_content(row: object, columns: list[str]) -> str:
    """从 Excel 行数据中提取题干文本。"""
    if "大题题干" in columns:
        return clean_nan(_row_get(row, "小题题干")) or clean_nan(_row_get(row, "大题题干")) or ""
    if "题干" in columns:
        return clean_nan(_row_get(row, "题干") or "")
    for column_name in columns:
        if any(keyword in str(column_name) for keyword in ["题目", "content", "内容"]):
            return clean_nan(_row_get(row, column_name) or "")
    return ""


def normalize_knowledge_point_names(value: object) -> list[str]:
    """统一规整题目关联知识点名称。"""
    if isinstance(value, str):
        items = split_multi_values(value)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        items = [str(item).strip() for item in value]
    else:
        items = []
    return [item for item in items if item]


def match_knowledge_point_by_topic(
    topic: str,
    knowledge_points: Sequence[KnowledgePoint],
) -> KnowledgePoint | None:
    """尝试将一个话题名称匹配到课程知识点。"""
    if not topic or not knowledge_points:
        return None
    topic_lower = topic.lower().strip()
    for knowledge_point in knowledge_points:
        if knowledge_point.name.strip() == topic.strip():
            return knowledge_point

    best_match: KnowledgePoint | None = None
    best_name_length = 0
    for knowledge_point in knowledge_points:
        point_name = knowledge_point.name.lower().strip()
        if topic_lower in point_name or point_name in topic_lower:
            if len(knowledge_point.name) > best_name_length:
                best_match = knowledge_point
                best_name_length = len(knowledge_point.name)
    return best_match


def build_question_import_context(course: Course) -> QuestionImportContext:
    """预加载课程知识点上下文。"""
    knowledge_points = list(KnowledgePoint.objects.filter(course=course))
    return QuestionImportContext(
        course=course,
        knowledge_points=knowledge_points,
        knowledge_point_map={knowledge_point.name: knowledge_point for knowledge_point in knowledge_points},
    )


def link_question_knowledge_points(
    question: Question,
    knowledge_point_names: Sequence[str],
    context: QuestionImportContext,
    unmatched_names: set[str],
) -> bool:
    """按知识点名称为题目绑定知识点。"""
    linked = False
    for knowledge_point_name in knowledge_point_names:
        knowledge_point = context.knowledge_point_map.get(knowledge_point_name)
        if knowledge_point is None:
            knowledge_point = match_knowledge_point_by_topic(
                knowledge_point_name,
                context.knowledge_points,
            )
        if knowledge_point is None:
            unmatched_names.add(knowledge_point_name)
            continue
        question.knowledge_points.add(knowledge_point)
        linked = True
    return linked


def load_question_json_source(source: object) -> dict[str, object]:
    """加载题库 JSON 数据源，兼容路径与已解析对象。"""
    if isinstance(source, Mapping):
        payload = {str(key): value for key, value in source.items()}
        _validate_question_json_payload(payload)
        return payload
    if isinstance(source, Path):
        source = str(source)
    if isinstance(source, str):
        validate_json(source, "questions")
        payload = load_json(source)
        if not isinstance(payload, dict):
            raise ValueError("题库JSON必须是对象")
        return {str(key): value for key, value in payload.items()}
    raise TypeError("题库 JSON 仅支持文件路径、Path 对象或已解析的 dict")


def build_json_question_payload(raw_question: Mapping[str, object]) -> QuestionPayload | None:
    """将 JSON 题目对象规整为统一载荷。"""
    content = str(strip_import_text(clean_nan(raw_question.get("content", ""))) or "")
    if not content:
        return None
    return QuestionPayload(
        content=content,
        question_type=str(raw_question.get("question_type") or "single_choice"),
        options=clean_question_options(raw_question.get("options") or []),
        answer=normalize_question_answer(raw_question.get("answer") or {}),
        analysis=str(strip_import_text(clean_nan(raw_question.get("analysis", ""))) or ""),
        difficulty=str(raw_question.get("difficulty") or "medium"),
        score=safe_float(raw_question.get("score"), 1.0),
        chapter=clean_nan(raw_question.get("chapter", "")) or None,
        knowledge_point_names=normalize_knowledge_point_names(raw_question.get("knowledge_points", [])),
        for_initial_assessment=bool(raw_question.get("for_initial_assessment", False)),
        is_visible=bool(raw_question.get("is_visible", True)),
    )


def _build_excel_options(row: object, columns: list[str]) -> list[dict[str, str]]:
    """从 Excel 行中提取选项列表。"""
    options: list[dict[str, str]] = []
    for index in range(26):
        label = chr(ord("A") + index)
        option_key = f"选项{label}" if f"选项{label}" in columns else label
        raw_option = _row_get(row, option_key)
        if raw_option is None:
            continue
        option_text = str(strip_import_text(clean_nan(raw_option)) or "")
        if option_text:
            options.append({"label": label, "content": option_text})
    return options


def _build_excel_answer(question_type: str, answer_text: str) -> dict[str, object]:
    """根据题型规整 Excel 中的答案字段。"""
    if question_type == "multiple_choice":
        answers = [item.strip() for item in ANSWER_SEPARATOR_PATTERN.split(answer_text) if item.strip()]
        if len(answers) == 1 and len(answers[0]) > 1:
            answers = list(answers[0])
        return {"answers": answers}

    if question_type == "true_false":
        if answer_text.upper() == "A" or answer_text in TRUE_OPTION_TEXTS:
            return {"answer": "true"}
        if answer_text.upper() == "B" or answer_text in FALSE_OPTION_TEXTS:
            return {"answer": "false"}
    return {"answer": answer_text}


def _normalize_true_false_options(
    question_type: str,
    options: list[dict[str, str]],
) -> list[dict[str, str]]:
    """为判断题选项补齐 true/false 值。"""
    if question_type != "true_false" or not options:
        return options
    normalized_options: list[dict[str, str]] = []
    for option in options:
        option_text = option["content"].strip()
        if option_text in TRUE_OPTION_TEXTS:
            normalized_options.append({**option, "value": "true"})
            continue
        if option_text in FALSE_OPTION_TEXTS:
            normalized_options.append({**option, "value": "false"})
            continue
        normalized_options.append(option)
    return normalized_options


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
        clean_nan(_row_get(row, "小题题型"))
        or clean_nan(_row_get(row, "题型"))
        or clean_nan(_row_get(row, "题目类型"))
        or ""
    )
    question_type = TYPE_MAP.get(question_type_text, "single_choice")
    difficulty_text = clean_nan(_row_get(row, "难易度")) or clean_nan(_row_get(row, "难度")) or ""
    difficulty = DIFFICULTY_MAP.get(difficulty_text, "medium")
    raw_options = _build_excel_options(row, columns)
    answer_text = str(
        strip_import_text(clean_nan(_row_get(row, "正确答案")) or clean_nan(_row_get(row, "答案")) or "") or ""
    )
    return QuestionPayload(
        content=content,
        question_type=question_type,
        options=_normalize_true_false_options(question_type, raw_options),
        answer=_build_excel_answer(question_type, answer_text),
        analysis=str(
            strip_import_text(clean_nan(_row_get(row, "答案解析")) or clean_nan(_row_get(row, "解析")) or "") or ""
        ),
        difficulty=difficulty,
        score=safe_float(
            clean_nan(_row_get(row, "分值"))
            or clean_nan(_row_get(row, "建议分数"))
            or clean_nan(_row_get(row, "得分"))
            or clean_nan(_row_get(row, "分数")),
            default=1.0,
        ),
        chapter=clean_nan(_row_get(row, "目录")) or clean_nan(_row_get(row, "章节")) or None,
        knowledge_point_names=normalize_knowledge_point_names(clean_nan(_row_get(row, "知识点") or "")),
        for_initial_assessment=for_initial_assessment,
    )


def create_question_from_payload(course: Course, payload: QuestionPayload) -> Question:
    """根据标准化载荷创建题目。"""
    return Question.objects.create(
        course=course,
        content=payload.content,
        question_type=payload.question_type,
        options=payload.options,
        answer=payload.answer,
        analysis=payload.analysis,
        difficulty=payload.difficulty,
        score=payload.score,
        chapter=payload.chapter,
        for_initial_assessment=payload.for_initial_assessment,
        is_visible=payload.is_visible,
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


def resolve_filename_knowledge_point(
    filename_stem: str,
    context: QuestionImportContext,
) -> KnowledgePoint | None:
    """尝试根据文件名推导默认知识点。"""
    topic = LEADING_DIGITS_PATTERN.sub("", filename_stem).strip()
    if not topic:
        return None
    return match_knowledge_point_by_topic(topic, context.knowledge_points)
