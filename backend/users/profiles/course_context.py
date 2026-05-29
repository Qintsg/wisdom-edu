#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
学习者画像课程上下文校验工具。
@Project : wisdom-edu
@File : course_context.py
@Author : Qintsg
@Date : 2026-05-29 00:00
'''

from __future__ import annotations

from rest_framework.response import Response

from common.domain.utils import validate_course_exists
from common.http.responses import error_response


def resolve_existing_profile_course_id(raw_course_id: object) -> tuple[int | None, Response | None]:
    """
    解析并验证画像刷新使用的课程 ID。

    :param raw_course_id: 请求体或查询参数中的课程 ID。
    :return: `(course_id, error_response)`；校验失败时 `course_id` 为 None。
    """
    if raw_course_id in (None, ""):
        return None, error_response(msg="缺少课程ID", code=400)

    try:
        course_id = int(str(raw_course_id).strip())
    except (TypeError, ValueError):
        return None, error_response(msg="课程ID格式错误", code=400)

    if validate_course_exists(course_id) is None:
        return None, error_response(msg="课程不存在", code=400)

    return course_id, None
