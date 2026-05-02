#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""公开 API 回归测试工具入口。"""

from __future__ import annotations

import time
from typing import List

from tools.api_regression_admin import _run_admin_regression
from tools.api_regression_helpers import (
    DEFAULT_BASE_URL,
    _build_auth_headers,
    _run_document_checks,
)
from tools.api_regression_student import _run_student_regression
from tools.api_regression_teacher import _run_teacher_regression
from tools.testing import CheckResult, _login, _print_checks, _resolve_course_id


def api_regression(
    base_url: str = DEFAULT_BASE_URL,
    include_all: bool = False,
    as_json: bool = False,
) -> None:
    """执行公开 API 回归测试。"""
    checks: List[CheckResult] = []
    temp_suffix = str(int(time.time()))

    _run_document_checks(checks, base_url)
    if not checks or not checks[1].ok:
        _print_checks(checks, as_json=as_json)
        return

    student_token, _ = _login(base_url, "student1", "Test123456")
    teacher_token, _ = _login(base_url, "teacher1", "Test123456")
    admin_token, _ = _login(base_url, "admin", "Admin123456")

    student_headers = _build_auth_headers(student_token)
    teacher_headers = _build_auth_headers(teacher_token)
    admin_headers = _build_auth_headers(admin_token)

    checks.append(CheckResult("学生登录", bool(student_token), "student1"))
    checks.append(CheckResult("教师登录", bool(teacher_token), "teacher1"))
    checks.append(CheckResult("管理员登录", bool(admin_token), "admin"))
    if not all([student_token, teacher_token, admin_token]):
        _print_checks(checks, as_json=as_json)
        return

    course_id = _resolve_course_id(base_url, student_headers, None)
    checks.append(
        CheckResult(
            "课程上下文解析",
            bool(course_id),
            f"course_id={course_id}" if course_id else "未解析到课程",
        )
    )

    if course_id:
        _run_student_regression(
            checks=checks,
            base_url=base_url,
            student_headers=student_headers,
            course_id=course_id,
            include_all=include_all,
        )
        _run_teacher_regression(
            checks=checks,
            base_url=base_url,
            teacher_headers=teacher_headers,
            course_id=course_id,
            include_all=include_all,
            temp_suffix=temp_suffix,
        )

    _run_admin_regression(
        checks=checks,
        base_url=base_url,
        admin_headers=admin_headers,
        include_all=include_all,
        temp_suffix=temp_suffix,
    )

    _print_checks(checks, as_json=as_json)