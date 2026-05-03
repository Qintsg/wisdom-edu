#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
题库导入知识点绑定工具。

负责课程知识点缓存、名称归一化、模糊匹配与题目多对多关系绑定。
"""
from __future__ import annotations

from collections.abc import Sequence
import re

from assessments.models import Question
from courses.models import Course
from knowledge.models import KnowledgePoint
from tools.common import split_multi_values
from tools.question_import_types import QuestionImportContext


LEADING_DIGITS_PATTERN = re.compile(r"^\d+")


# 维护意图：统一规整题目关联知识点名称
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_knowledge_point_names(value: object) -> list[str]:
    """统一规整题目关联知识点名称。"""
    if isinstance(value, str):
        items = split_multi_values(value)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        items = [str(item).strip() for item in value]
    else:
        items = []
    return [item for item in items if item]


# 维护意图：尝试将一个话题名称匹配到课程知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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


# 维护意图：预加载课程知识点上下文
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_question_import_context(course: Course) -> QuestionImportContext:
    """预加载课程知识点上下文。"""
    knowledge_points = list(KnowledgePoint.objects.filter(course=course))
    return QuestionImportContext(
        course=course,
        knowledge_points=knowledge_points,
        knowledge_point_map={knowledge_point.name: knowledge_point for knowledge_point in knowledge_points},
    )


# 维护意图：按知识点名称为题目绑定知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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


# 维护意图：尝试根据文件名推导默认知识点
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_filename_knowledge_point(
    filename_stem: str,
    context: QuestionImportContext,
) -> KnowledgePoint | None:
    """尝试根据文件名推导默认知识点。"""
    topic = LEADING_DIGITS_PATTERN.sub("", filename_stem).strip()
    if not topic:
        return None
    return match_knowledge_point_by_topic(topic, context.knowledge_points)
