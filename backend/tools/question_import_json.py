#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
题库 JSON 导入适配工具。

负责 JSON 数据源读取、结构验证以及原始题目对象到标准题目载荷的转换。
"""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from tools.common import clean_nan, load_json, safe_float
from tools.knowledge import validate_json
from tools.question_import_answers import normalize_question_answer
from tools.question_import_knowledge import normalize_knowledge_point_names
from tools.question_import_text import clean_question_options, strip_import_text
from tools.question_import_types import QuestionPayload


# 维护意图：验证题库 JSON 结构
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def validate_question_json_payload(payload: Mapping[str, object]) -> None:
    """验证题库 JSON 结构。"""
    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise ValueError("题库JSON缺少 questions(list)")


# 维护意图：加载题库 JSON 数据源，兼容路径与已解析对象
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_question_json_source(source: object) -> dict[str, object]:
    """加载题库 JSON 数据源，兼容路径与已解析对象。"""
    if isinstance(source, Mapping):
        payload = {str(key): value for key, value in source.items()}
        validate_question_json_payload(payload)
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


# 维护意图：将 JSON 题目对象规整为统一载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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
