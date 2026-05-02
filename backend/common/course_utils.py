"""课程上下文解析与课程校验工具。"""

from __future__ import annotations

import logging
from typing import Any

from django.db import DatabaseError


logger = logging.getLogger(__name__)


def validate_course_exists(course_id: int | str) -> Any | None:
    """
    验证课程是否存在。

    :param course_id: 课程 ID。
    :return: Course 对象，不存在时返回 None。
    """
    from courses.models import Course

    try:
        return Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return None


def resolve_course_id(request: Any) -> tuple[int | None, Any | None]:
    """
    从请求中提取课程 ID，优先请求参数，其次用户课程上下文。

    :param request: DRF request 对象。
    :return: `(course_id, error_response)`；解析失败时 `course_id` 为 None。
    """
    from common.responses import error_response as _error_response

    course_id = (
        request.query_params.get("course_id")
        if hasattr(request, "query_params")
        else None
    )
    source = "request"
    if not course_id:
        course_id = request.data.get("course_id") if hasattr(request, "data") else None

    if not course_id and request.user and request.user.is_authenticated:
        try:
            from users.models import UserCourseContext

            context = UserCourseContext.objects.filter(user=request.user).first()
            context_course_id = getattr(context, "current_course_id", None)
            if context_course_id:
                course_id = context_course_id
                source = "context"
        except (AttributeError, DatabaseError, ImportError) as error:
            logger.warning("failed to resolve course_id from user context: %s", error)

    if not course_id:
        return None, _error_response(msg="缺少课程ID")

    course_id_text = str(course_id).strip()
    try:
        course_id_int = int(course_id_text)
        if source == "context":
            logger.debug("course_id resolved from user context: %s", course_id_int)
        return course_id_int, None
    except (ValueError, TypeError):
        logger.warning("invalid course_id format: %s", course_id)
        return None, _error_response(msg="课程ID格式错误")


__all__ = ["validate_course_exists", "resolve_course_id"]
