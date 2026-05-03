"""题目选项、答案 token 与答案展示工具。"""

from __future__ import annotations

import math
import re
from typing import Any

from django.utils.html import strip_tags

from .grading import _normalize_boolean_answer, extract_answer_value


# 维护意图：将可能的空值、NaN 或 HTML 文本转为安全显示文本。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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


# 维护意图：提取答案匹配时使用的 token 集合。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def answer_tokens(answer: Any, question_type: str | None = None) -> set[str]:
    """
    提取答案匹配时使用的 token 集合。

    :param answer: 原始答案。
    :param question_type: 可选题型，用于真假题别名扩展。
    :return: 可用于选项匹配的 token 集合。
    """
    tokens: set[str] = set()
    for value in answer_values(answer):
        cleaned = clean_display_text(value)
        if cleaned:
            tokens.update(display_token_variants(cleaned))
            tokens.update(true_false_alias_tokens(cleaned, question_type))
    return tokens


# 维护意图：将原始答案规整为可迭代值列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def answer_values(answer: Any) -> list[Any]:
    """将原始答案规整为可迭代值列表。"""
    payload = extract_answer_value(answer)
    if isinstance(payload, (list, tuple, set)):
        return list(payload)
    if payload is None:
        return []
    return [payload]


# 维护意图：生成大小写兼容的展示 token
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def display_token_variants(cleaned: str) -> set[str]:
    """生成大小写兼容的展示 token。"""
    return {cleaned, cleaned.lower(), cleaned.upper()}


# 维护意图：为真假题补充中英文布尔别名
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def true_false_alias_tokens(cleaned: str, question_type: str | None) -> set[str]:
    """为真假题补充中英文布尔别名。"""
    if question_type != "true_false":
        return set()
    lower = cleaned.lower()
    if lower in {"正确", "true", "1", "yes", "对", "是", "t", "√"}:
        return {"true", "TRUE", "正确"}
    if lower in {"错误", "false", "0", "no", "错", "否", "f", "×"}:
        return {"false", "FALSE", "错误"}
    return set()


# 维护意图：将题目选项归一化为统一的 value/label/content/letter 结构。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
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
    raw_options = default_true_false_options(raw_options, question_type)

    for index, option in enumerate(raw_options or []):
        normalized_option = normalize_single_option(option, index)
        if normalized_option is None:
            continue
        normalized.append(normalized_option)
    return normalized


# 维护意图：真假题缺少选项时补充默认选项
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def default_true_false_options(raw_options: Any, question_type: str | None) -> Any:
    """真假题缺少选项时补充默认选项。"""
    if raw_options or question_type != "true_false":
        return raw_options
    return [
        {"value": "true", "label": "正确"},
        {"value": "false", "label": "错误"},
    ]


# 维护意图：归一化单个选项
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_single_option(option: Any, index: int) -> dict[str, str] | None:
    """归一化单个选项。"""
    letter = chr(ord("A") + index)
    if isinstance(option, dict):
        return normalize_dict_option(option, index, letter)
    if isinstance(option, str):
        return normalize_text_option(option, index, letter)
    return None


# 维护意图：归一化字典选项
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_dict_option(option: dict[str, Any], index: int, letter: str) -> dict[str, str]:
    """归一化字典选项。"""
    raw_value = first_truthy_option_field(
        option,
        ["value", "key", "option_id", "letter", "label", "content", "text", "id"],
    )
    raw_label = first_truthy_option_field(option, ["content", "text", "label"]) or raw_value
    value = clean_display_text(raw_value) or f"opt_{index + 1}"
    label = clean_display_text(raw_label) or f"选项{letter}"
    resolved_letter = clean_display_text(option.get("letter") or option.get("key")) or letter
    return option_payload(value=value, label=label, letter=resolved_letter)


# 维护意图：归一化纯文本选项
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_text_option(option: str, index: int, letter: str) -> dict[str, str]:
    """归一化纯文本选项。"""
    cleaned = clean_display_text(option)
    value = cleaned or f"opt_{index + 1}"
    label = cleaned or f"选项{letter}"
    return option_payload(value=value, label=label, letter=letter)


# 维护意图：按旧逻辑读取第一个 truthy 选项字段
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def first_truthy_option_field(option: dict[str, Any], field_names: list[str]) -> Any:
    """按旧逻辑读取第一个 truthy 选项字段。"""
    for field_name in field_names:
        value = option.get(field_name)
        if value:
            return value
    return None


# 维护意图：构造统一选项载荷
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def option_payload(*, value: Any, label: str, letter: str) -> dict[str, str]:
    """构造统一选项载荷。"""
    return {
        "value": str(value),
        "label": label,
        "content": label,
        "letter": letter,
    }


# 维护意图：提取选项匹配 token。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def option_tokens(option: dict[str, Any]) -> set[str]:
    """
    提取选项匹配 token。

    :param option: 标准化后的选项结构。
    :return: 可匹配 token 集合。
    """
    tokens: set[str] = set()
    for value in option_token_values(option):
        cleaned = clean_display_text(value)
        if cleaned:
            tokens.update(display_token_variants(cleaned))
    return tokens


# 维护意图：返回选项中参与匹配的字段值
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def option_token_values(option: dict[str, Any]) -> tuple[Any, Any, Any, Any]:
    """返回选项中参与匹配的字段值。"""
    return (
        option.get("value"),
        option.get("letter"),
        option.get("label"),
        option.get("content"),
    )


# 维护意图：为选项补充学生选择和正确答案标记。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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


# 维护意图：格式化单个选项展示文本。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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


# 维护意图：构建题目答案展示文本。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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
        matched = matched_option_displays(options, token_set)
        if matched:
            return "；".join(matched)

    payload = extract_answer_value(answer)
    if isinstance(payload, (list, tuple, set)):
        return joined_answer_values(payload)
    if isinstance(payload, bool):
        return "正确" if payload else "错误"

    bool_value = _normalize_boolean_answer(payload)
    if question_type == "true_false" and bool_value is not None:
        return "正确" if bool_value else "错误"

    cleaned = clean_display_text(payload)
    return cleaned or "未作答"


# 维护意图：返回与答案 token 命中的选项展示文本
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def matched_option_displays(options: list[dict[str, Any]], token_set: set[str]) -> list[str]:
    """返回与答案 token 命中的选项展示文本。"""
    return [
        format_option_display(option)
        for option in options
        if option_tokens(option) & token_set
    ]


# 维护意图：展示多选或集合答案
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def joined_answer_values(payload: Any) -> str:
    """展示多选或集合答案。"""
    values = []
    for item in payload:
        cleaned = clean_display_text(item)
        if cleaned:
            values.append(cleaned)
    return "；".join(values) if values else "未作答"


# 维护意图：将答案序列化为统一 JSON 结构，便于持久化。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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
