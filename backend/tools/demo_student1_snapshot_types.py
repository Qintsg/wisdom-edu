#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
student1 桌面快照预置数据类型。
@Project : wisdom-edu
@File : demo_student1_snapshot_types.py
@Author : Qintsg
@Date : 2026-05-13 13:35
'''

from __future__ import annotations

from dataclasses import dataclass, field


DESKTOP_HTML_NAMES = {
    "report": "测评报告 - 自适应学习系统.html",
    "profile": "学习画像 - 自适应学习系统.html",
    "path": "学习路径 - 自适应学习系统.html",
}
DEMO_COURSE_NAME = "大数据技术与应用"
DEMO_STUDENT_USERNAME = "student1"


@dataclass(frozen=True)
class DesktopAsset:
    """桌面导出资源文件摘要。"""

    relative_path: str
    size: int


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
    """桌面三页导出内容的归一化快照。"""

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
    assets: list[DesktopAsset] = field(default_factory=list)


@dataclass(frozen=True)
class StudentDemoPresetResult:
    """student1 演示快照写入结果。"""

    applied: bool
    skipped_reason: str | None
    course_id: int | None = None
    mastery_count: int = 0
    question_count: int = 0
    path_node_count: int = 0
    asset_count: int = 0
