"""学生端考试列表与详情视图。"""
from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.responses import error_response, success_response

from .student_exam_support import (
    build_exam_detail_payload,
    build_exam_list_payload,
    get_published_exam,
    resolve_exam_detail_access_error,
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_list(request: Request) -> Response:
    """获取考试列表。"""
    return success_response(data=build_exam_list_payload(request.query_params, request.user))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_detail(request: Request, exam_id: int) -> Response:
    """获取考试详情（含题目，不含答案）。"""
    exam = get_published_exam(exam_id)
    if exam is None:
        return error_response(msg="作业不存在", code=404)

    access_error = resolve_exam_detail_access_error(exam, request.user)
    if access_error:
        return error_response(msg=access_error, code=403)

    return success_response(data=build_exam_detail_payload(exam))
