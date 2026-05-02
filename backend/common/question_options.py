"""题目选项、答案 token 与答案展示工具。"""

from __future__ import annotations

import math
import re
from typing import Any

from django.utils.html import strip_tags

from .grading import _normalize_boolean_answer, extract_answer_value


def clean_display_text(value: Any) -> str:
    """
    将可能的空值、NaN 或 HTML 文本转为安全显示文本。

    :param value: 原始展示值。
    :return: 安全单行文本。
    """
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return str(value).strip()

    text = strip_tags(str(value)).strip()
    if text.lower() in {"", "nan", "none", "null", "n/a", "na"}:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def answer_tokens(answer: Any, question_type: str | None = None) -> set[str]:
    """
    提取答案匹配时使用的 token 集合。

    :param answer: 原始答案。
    :param question_type: 可选题型，用于真假题别名扩展。
    :return: 可用于选项匹配的 token 集合。
    """
    payload = extract_answer_value(answer)
    tokens: set[str] = set()

    if isinstance(payload, (list, tuple, set)):
        values = payload
    elif payload is None:
        values = []
    else:
        values = [payload]

    for value in values:
        cleaned = clean_display_text(value)
        if not cleaned:
            continue
        tokens.add(cleaned)
        tokens.add(cleaned.lower())
        tokens.add(cleaned.upper())
        if question_type == "true_false":
            lower = cleaned.lower()
            if lower in {"正确", "true", "1", "yes", "对", "是", "t", "√"}:
                tokens.update({"true", "TRUE", "正确"})
            if lower in {"错误", "false", "0", "no", "错", "否", "f", "×"}:
                tokens.update({"false", "FALSE", "错误"})
    return tokens


def normalize_question_options(
    raw_options: Any, question_type: str | None = None
) -> list[dict[str, str]]:
    """
    将题目选项归一化为统一的 value/label/content/letter 结构。

    :param raw_options: 原始选项数据。
    :param question_type: 题型。
    :return: 选项展示结构列表。
    """
    normalized: list[dict[str, str]] = []

    if not raw_options and question_type == "true_false":
        raw_options = [
            {"value": "true", "label": "正确"},
            {"value": "false", "label": "错误"},
        ]

    for index, option in enumerate(raw_options or []):
        letter = chr(ord("A") + index)
        if isinstance(option, dict):
            raw_value = (
                option.get("value")
                or option.get("key")
                or option.get("option_id")
                or option.get("letter")
                or option.get("label")
                or option.get("content")
                or option.get("text")
                or option.get("id")
            )
            raw_label = (
                option.get("content")
                or option.get("text")
                or option.get("label")
                or raw_value
            )
            value = clean_display_text(raw_value) or f"opt_{index + 1}"
            label = clean_display_text(raw_label) or f"选项{letter}"
            letter = clean_display_text(option.get("letter") or option.get("key")) or letter
        elif isinstance(option, str):
            cleaned = clean_display_text(option)
            value = cleaned or f"opt_{index + 1}"
            label = cleaned or f"选项{letter}"
        else:
            continue

        normalized.append(
            {
                "value": str(value),
                "label": label,
                "content": label,
                "letter": letter,
            }
        )

    return normalized


def option_tokens(option: dict[str, Any]) -> set[str]:
    """
    提取选项匹配 token。

    :param option: 标准化后的选项结构。
    :return: 可匹配 token 集合。
    """
    tokens: set[str] = set()
    for value in (
        option.get("value"),
        option.get("letter"),
        option.get("label"),
        option.get("content"),
    ):
        cleaned = clean_display_text(value)
        if cleaned:
            tokens.update({cleaned, cleaned.lower(), cleaned.upper()})
    return tokens


def decorate_question_options(
    raw_options: Any,
    question_type: str | None = None,
    student_answer: Any = None,
    correct_answer: Any = None,
) -> list[dict[str, Any]]:
    """
    为选项补充学生选择和正确答案标记。

    :return: 带 `is_student_selected` 与 `is_correct_option` 的选项列表。
    """
    normalized = normalize_question_options(raw_options, question_type)
    student_token_set = answer_tokens(student_answer, question_type)
    correct_token_set = answer_tokens(correct_answer, question_type)

    return [
        {
            **option,
            "is_student_selected": bool(option_tokens(option) & student_token_set),
            "is_correct_option": bool(option_tokens(option) & correct_token_set),
        }
        for option in normalized
    ]


def format_option_display(option: dict[str, Any]) -> str:
    """
    格式化单个选项展示文本。

    :param option: 标准化后的选项结构。
    :return: 用户可读选项文案。
    """
    prefix = clean_display_text(option.get("letter") or option.get("value"))
    content = clean_display_text(
        option.get("content") or option.get("label") or option.get("value")
    )
    return f"{prefix}. {content}" if prefix and content else content or prefix


def build_answer_display(
    answer: Any,
    question_type: str | None = None,
    options: list[dict[str, Any]] | None = None,
) -> str:
    """
    构建题目答案展示文本。

    :param answer: 原始答案。
    :param question_type: 可选题型。
    :param options: 可选题目选项。
    :return: 用户可读答案文本。
    """
    token_set = answer_tokens(answer, question_type)
    if options:
        matched = [
            format_option_display(option)
            for option in options
            if option_tokens(option) & token_set
        ]
        if matched:
            return "；".join(matched)

    payload = extract_answer_value(answer)
    if isinstance(payload, (list, tuple, set)):
        values = [clean_display_text(item) for item in payload if clean_display_text(item)]
        return "；".join(values) if values else "未作答"
    if isinstance(payload, bool):
        return "正确" if payload else "错误"

    bool_value = _normalize_boolean_answer(payload)
    if question_type == "true_false" and bool_value is not None:
        return "正确" if bool_value else "错误"

    cleaned = clean_display_text(payload)
    return cleaned or "未作答"


def serialize_answer_payload(question_type: str | None, answer: Any) -> dict[str, Any]:
    """
    将答案序列化为统一 JSON 结构，便于持久化。

    :param question_type: 题型。
    :param answer: 原始答案。
    :return: 可持久化答案 payload。
    """
    payload = extract_answer_value(answer)
    if question_type == "multiple_choice":
        if payload is None or payload == "":
            return {"answers": []}
        if isinstance(payload, (list, tuple, set)):
            return {"answers": list(payload)}
        return {"answers": [payload]}

    if question_type == "true_false":
        bool_value = _normalize_boolean_answer(payload)
        return {"answer": bool_value if bool_value is not None else payload}

    return {"answer": payload}


__all__ = [
    "clean_display_text",
    "answer_tokens",
    "normalize_question_options",
    "option_tokens",
    "decorate_question_options",
    "format_option_display",
    "build_answer_display",
    "serialize_answer_payload",
]
