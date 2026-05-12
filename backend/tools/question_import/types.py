#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
题库导入数据结构。

集中定义跨 JSON、Excel 与数据库绑定流程共享的轻量载荷，避免解析模块彼此耦合。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from courses.models import Course
from knowledge.models import KnowledgePoint


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
