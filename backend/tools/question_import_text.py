#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
题库导入文本清洗工具。

负责 HTML、实体与空白归一化，确保 JSON 与 Excel 解析共享同一套清洗规则。
"""
from __future__ import annotations

from collections.abc import Mapping
from html import unescape as html_unescape
import re

from django.utils.html import strip_tags


WHITESPACE_PATTERN = re.compile(r"\s+")


# 维护意图：去除 HTML 标签并清理多余空白
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def strip_import_text(value: object) -> object:
    """去除 HTML 标签并清理多余空白。"""
    if not value:
        return value
    text = strip_tags(str(value))
    text = html_unescape(text)
    text = text.replace("\xa0", " ")
    return WHITESPACE_PATTERN.sub(" ", text).strip()


# 维护意图：清洗答案字段中的 HTML
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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


# 维护意图：清洗 JSON 题目中的选项内容
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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
