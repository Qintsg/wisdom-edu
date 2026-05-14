#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
student1 大数据学习状态内置预置数据。
@Project : wisdom-edu
@File : demo_student1_snapshot_parse.py
@Author : Qintsg
@Date : 2026-05-13 13:36
'''

from __future__ import annotations

from tools.demo_student1_snapshot_types import DesktopSnapshot, QuestionSnapshot


INLINE_SNAPSHOT_QUESTIONS = [
    QuestionSnapshot(
        order=index,
        content=f"大数据技术与应用初始评测题 {index}",
        student_answer=True if index <= 40 else False,
        correct_answer=True,
        is_correct=index <= 40,
        analysis="需要结合课程资源复习相关知识点。",
    )
    for index in range(1, 51)
]


INLINE_REPORT_MASTERY = {
    "大数据存储与管理": 0.98,
    "基于潜在因子的推荐方法": 0.97,
    "Spark定义与特征": 0.87,
    "大数据技术基础": 0.72,
    "大数据基本概念": 0.64,
    "Spark SQL原理与特征": 0.24,
    "大数据系统实践": 0.24,
    "综合实践": 0.29,
}


INLINE_PATH_TITLES = [
    "大数据概念基础复盘",
    "Spark定义与特征巩固",
    "大数据智能分析挖掘巩固",
    "基于潜在因子的推荐方法巩固",
    "大数据存储与管理巩固",
    "Spark SQL原理与特征基础",
    "阶段测试：Spark SQL原理与特征、大数据系统实践、综合实践",
]


def load_inline_snapshot() -> DesktopSnapshot:
    """
    返回内置的 student1 大数据课程业务快照。
    :return: 归一化快照。
    """
    return DesktopSnapshot(
        score=80.0,
        correct_count=40,
        total_count=50,
        question_details=list(INLINE_SNAPSHOT_QUESTIONS),
        report_mastery=dict(INLINE_REPORT_MASTERY),
        profile_summary="整体掌握度 57.3%，高掌握知识点集中在大数据存储与管理、推荐方法等内容。",
        profile_weakness="薄弱环节包括 Spark SQL原理与特征、综合实践和大数据系统实践，需要结合课程任务继续巩固。",
        profile_suggestion="优先巩固 Spark SQL 原理与特征，再推进大数据系统实践和综合实践任务。",
        ability_scores={"处理速度": 60, "工作记忆": 60, "知觉推理": 60, "言语理解": 60},
        learner_tags=["高效型学习者", "视觉型", "晚间学习", "自适应"],
        path_titles=list(INLINE_PATH_TITLES),
        selected_path_title="Spark SQL原理与特征基础",
        selected_minutes=52,
        selected_goal="掌握Spark SQL原理与特征的核心概念及应用",
        selected_suggestion="重点学习Spark SQL原理与特征相关内容。",
    )
