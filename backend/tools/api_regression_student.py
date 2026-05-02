"""学生端公开 API 回归测试编排。"""

from __future__ import annotations

from typing import Dict, List

from tools.api_regression_student_basics import _run_student_basic_checks
from tools.api_regression_student_exam_ai import (
    _run_student_ai_kt_checks,
    _run_student_exam_checks,
)
from tools.api_regression_student_learning import _run_student_learning_checks
from tools.testing import CheckResult


def _run_student_regression(
    checks: List[CheckResult],
    base_url: str,
    student_headers: Dict[str, str],
    course_id: int,
    include_all: bool,
) -> None:
    """执行学生端主要学习链路与 AI 能力回归。"""
    _run_student_basic_checks(
        checks=checks,
        base_url=base_url,
        student_headers=student_headers,
        course_id=course_id,
    )
    point_id = _run_student_learning_checks(
        checks=checks,
        base_url=base_url,
        student_headers=student_headers,
        course_id=course_id,
        include_all=include_all,
    )
    _run_student_exam_checks(
        checks=checks,
        base_url=base_url,
        student_headers=student_headers,
        course_id=course_id,
    )
    _run_student_ai_kt_checks(
        checks=checks,
        base_url=base_url,
        student_headers=student_headers,
        course_id=course_id,
        point_id=point_id,
    )
