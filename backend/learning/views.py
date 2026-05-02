#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
学习路径模块视图兼容入口。
提供学习路径、节点、进度相关的 API 端点。
@Project : wisdom-edu
@File : views.py
@Author : Qintsg
@Date : 2026-03-23
"""

from __future__ import annotations

from learning.dashboard_views import student_dashboard
from learning.node_detail_views import complete_node_resource, get_path_node_detail, submit_node_exam
from learning.node_progress_views import (
    complete_path_node,
    get_ai_resources,
    get_learning_progress,
    get_node_exams,
    get_node_resources,
    pause_node_resource,
    skip_path_node,
    start_learning_node,
)
from learning.path_views import adjust_learning_path, generate_initial_path, get_learning_path
from learning.stage_test_get_views import get_stage_test
from learning.stage_test_submit_views import submit_stage_test

__all__ = [
    "adjust_learning_path",
    "complete_node_resource",
    "complete_path_node",
    "generate_initial_path",
    "get_ai_resources",
    "get_learning_path",
    "get_learning_progress",
    "get_node_exams",
    "get_node_resources",
    "get_path_node_detail",
    "get_stage_test",
    "pause_node_resource",
    "skip_path_node",
    "start_learning_node",
    "student_dashboard",
    "submit_node_exam",
    "submit_stage_test",
]