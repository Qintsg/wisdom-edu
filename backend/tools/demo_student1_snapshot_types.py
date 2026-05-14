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
    question_type: str
    options: list[dict[str, object]]
    student_answer: object
    correct_answer: object
    student_answer_display: str
    correct_answer_display: str
    is_correct: bool
    analysis: str = ""
    knowledge_point_names: list[str] | None = None
    difficulty: str = "medium"
    score: float = 2.0


@dataclass(frozen=True)
class PathNodeSnapshot:
    """学习路径单节点快照。"""

    order: int
    title: str
    node_type: str
    status: str
    estimated_minutes: int
    goal: str
    criterion: str
    suggestion: str
    knowledge_point_name: str | None = None
    mastery_before: float | None = None
    mastery_after: float | None = None


@dataclass(frozen=True)
class FeedbackReportSnapshot:
    """初始评测反馈报告快照。"""

    summary: str
    knowledge_gaps: list[str]
    recommendations: list[str]
    next_tasks: list[str]
    encouragement: str
    conclusion: str


@dataclass(frozen=True)
class DesktopSnapshot:
    """内置预置内容的归一化快照。"""

    score: float
    correct_count: int
    total_count: int
    question_details: list[QuestionSnapshot]
    report_mastery: dict[str, float]
    feedback_report: FeedbackReportSnapshot
    profile_summary: str
    profile_weakness: str
    profile_suggestion: str
    ability_scores: dict[str, int]
    learner_tags: list[str]
    path_reason: str
    path_nodes: list[PathNodeSnapshot]
    preset_version: str

    @property
    def path_titles(self) -> list[str]:
        """返回学习路径标题列表，兼容旧调用。"""
        return [node.title for node in self.path_nodes]

    @property
    def selected_path_title(self) -> str:
        """返回桌面页面当前选中的路径节点标题。"""
        for node in self.path_nodes:
            if node.title == "Spark SQL原理与特征基础":
                return node.title
        return self.path_nodes[0].title if self.path_nodes else ""

    @property
    def selected_minutes(self) -> int:
        """返回桌面页面当前选中节点预计时长。"""
        for node in self.path_nodes:
            if node.title == self.selected_path_title:
                return node.estimated_minutes
        return 0

    @property
    def selected_goal(self) -> str:
        """返回桌面页面当前选中节点目标。"""
        for node in self.path_nodes:
            if node.title == self.selected_path_title:
                return node.goal
        return ""

    @property
    def selected_suggestion(self) -> str:
        """返回桌面页面当前选中节点建议。"""
        for node in self.path_nodes:
            if node.title == self.selected_path_title:
                return node.suggestion
        return ""


@dataclass(frozen=True)
class StudentDemoPresetResult:
    """student1 大数据学习状态写入结果。"""

    applied: bool
    skipped_reason: str | None
    course_id: int | None = None
    mastery_count: int = 0
    question_count: int = 0
    path_node_count: int = 0
