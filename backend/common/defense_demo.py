#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
演示环境预置能力兼容入口。
@Project : wisdom-edu
@File : defense_demo.py
@Author : Qintsg
@Date : 2026-03-27
"""

from __future__ import annotations

from common.defense_demo_accounts import ensure_defense_demo_accounts
from common.defense_demo_config import (
    DEFENSE_DEMO_CLASS_NAME,
    DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS,
    DEFENSE_DEMO_MARKER,
    DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME,
    DEFENSE_DEMO_SUPPORT_COURSE_NAME,
    DEFENSE_DEMO_TEACHER_USERNAME,
    DEFENSE_DEMO_WARMUP_STUDENT_USERNAME,
    DEMO_ASSESSMENT_PRESETS,
)
from common.defense_demo_environment import ensure_defense_demo_environment
from common.defense_demo_progress import (
    advance_defense_demo_path,
    complete_defense_demo_stage_test,
)
from common.defense_demo_public import (
    get_course_defense_demo_config,
    get_defense_demo_intro_payload,
    get_defense_demo_resource_payload,
    get_defense_demo_stage_test_payload,
    get_defense_demo_visible_order,
    is_defense_demo_primary_course,
    is_defense_demo_student,
)

__all__ = [
    "DEFENSE_DEMO_CLASS_NAME",
    "DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS",
    "DEFENSE_DEMO_MARKER",
    "DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME",
    "DEFENSE_DEMO_SUPPORT_COURSE_NAME",
    "DEFENSE_DEMO_TEACHER_USERNAME",
    "DEFENSE_DEMO_WARMUP_STUDENT_USERNAME",
    "DEMO_ASSESSMENT_PRESETS",
    "advance_defense_demo_path",
    "complete_defense_demo_stage_test",
    "ensure_defense_demo_accounts",
    "ensure_defense_demo_environment",
    "get_course_defense_demo_config",
    "get_defense_demo_intro_payload",
    "get_defense_demo_resource_payload",
    "get_defense_demo_stage_test_payload",
    "get_defense_demo_visible_order",
    "is_defense_demo_primary_course",
    "is_defense_demo_student",
]