#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
题库导入持久化工具。

将标准题目载荷落库，保持解析、绑定与数据库写入职责分离。
"""
from __future__ import annotations

from assessments.models import Question
from courses.models import Course
from tools.question_import_types import QuestionPayload


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
