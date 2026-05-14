#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
student1 大数据学习状态预置数据类型。
@Project : wisdom-edu
@File : demo_student1_snapshot_types.py
@Author : Qintsg
@Date : 2026-05-13 13:35
'''

from __future__ import annotations

from dataclasses import dataclass


DEMO_COURSE_NAME = "大数据技术与应用"
DEMO_STUDENT_USERNAME = "student1"


@dataclass(frozen=True)
class QuestionSnapshot:
    """初始评测单题快照。"""

    order: int
    content: str
    student_answer: object
    correct_answer: object
    is_correct: bool
    analysis: str = ""


@dataclass(frozen=True)
class DesktopSnapshot:
    """内置预置内容的归一化快照。"""

    score: float
    correct_count: int
    total_count: int
    question_details: list[QuestionSnapshot]
    report_mastery: dict[str, float]
    profile_summary: str
    profile_weakness: str
    profile_suggestion: str
    ability_scores: dict[str, int]
    learner_tags: list[str]
    path_titles: list[str]
    selected_path_title: str
    selected_minutes: int
    selected_goal: str
    selected_suggestion: str


@dataclass(frozen=True)
class StudentDemoPresetResult:
    """student1 大数据学习状态写入结果。"""

    applied: bool
    skipped_reason: str | None
    course_id: int | None = None
    mastery_count: int = 0
    question_count: int = 0
    path_node_count: int = 0
