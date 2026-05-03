#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
题库导入答案归一化工具。

将 JSON 与 Excel 中不稳定的答案表示转换为 Question.answer 使用的统一结构。
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
import re

from tools.question_import_text import strip_import_answer_payload


ANSWER_SEPARATOR_PATTERN = re.compile(r"[,;，；\s]+")
TRUE_OPTION_TEXTS = {"正确", "对", "True", "true", "T"}
FALSE_OPTION_TEXTS = {"错误", "错", "False", "false", "F"}


# 维护意图：将题目答案规整为 Question 模型使用的统一 JSON 结构
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_question_answer(answer: object) -> dict[str, object]:
    """将题目答案规整为 Question 模型使用的统一 JSON 结构。"""
    cleaned_answer = strip_import_answer_payload(answer)
    if isinstance(cleaned_answer, Mapping):
        return {str(key): value for key, value in cleaned_answer.items()}
    if isinstance(cleaned_answer, Sequence) and not isinstance(cleaned_answer, (str, bytes, bytearray)):
        return {"answers": list(cleaned_answer)}
    return {"answer": cleaned_answer}


# 维护意图：根据题型规整 Excel 中的答案字段
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_excel_answer(question_type: str, answer_text: str) -> dict[str, object]:
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


# 维护意图：为判断题选项补齐 true/false 值
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_true_false_options(
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
