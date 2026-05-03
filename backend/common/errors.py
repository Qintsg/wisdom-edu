"""统一 DRF 异常处理与错误消息提取。"""

from __future__ import annotations

import logging
from typing import Any

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


logger = logging.getLogger(__name__)


# 维护意图：将 DRF ErrorDetail / 列表 / 字典转为可 JSON 序列化的错误详情。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _normalize_error_detail(detail: Any) -> Any:
    """
    将 DRF ErrorDetail / 列表 / 字典转为可 JSON 序列化的错误详情。

    :param detail: DRF 原始错误数据。
    :return: 仅包含字符串、列表和字典的错误详情。
    """
    if isinstance(detail, dict):
        return {
            str(key): _normalize_error_detail(value)
            for key, value in detail.items()
        }
    if isinstance(detail, (list, tuple)):
        return [_normalize_error_detail(item) for item in detail]
    if detail is None:
        return None
    return str(detail)


# 维护意图：提取可直接展示给用户的错误消息，优先保留字段名上下文。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _flatten_error_messages(detail: Any) -> list[str]:
    """
    提取可直接展示给用户的错误消息，优先保留字段名上下文。

    :param detail: 归一化后的错误详情。
    :return: 消息列表。
    """
    if isinstance(detail, dict):
        messages: list[str] = []
        for key, value in detail.items():
            child_messages = _flatten_error_messages(value)
            if key == "detail":
                messages.extend(child_messages)
            elif child_messages:
                messages.extend(f"{key}: {message}" for message in child_messages)
        return messages
    if isinstance(detail, list):
        messages: list[str] = []
        for item in detail:
            messages.extend(_flatten_error_messages(item))
        return messages
    if detail is None:
        return []
    text = str(detail).strip()
    return [text] if text else []


# 维护意图：自定义异常处理，统一 API 响应格式。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """
    自定义异常处理，统一 API 响应格式。

    :param exc: DRF 捕获到的异常。
    :param context: DRF 异常上下文。
    :return: 统一 envelope 格式的响应。
    """
    response = exception_handler(exc, context)

    if response is not None:
        normalized_errors = _normalize_error_detail(response.data)
        message = get_error_message(response)
        response.data = {
            "code": response.status_code,
            "msg": message,
            "data": {"errors": normalized_errors} if normalized_errors else None,
            "error": {
                "type": exc.__class__.__name__,
                "details": normalized_errors,
            },
        }
    else:
        request = context.get("request") if isinstance(context, dict) else None
        request_method = getattr(request, "method", "-")
        request_path = getattr(request, "path", "-")
        logger.exception(
            "Unhandled exception | method=%s | path=%s | exc=%s",
            request_method,
            request_path,
            exc,
        )
        response = Response(
            {
                "code": 500,
                "msg": "服务器内部错误" if not settings.DEBUG else str(exc),
                "data": None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


# 维护意图：从 DRF 响应中提取错误信息。
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def get_error_message(response: Response) -> str:
    """
    从 DRF 响应中提取错误信息。

    :param response: DRF 响应对象。
    :return: 最适合展示给用户的错误文案。
    """
    if hasattr(response, "data"):
        normalized_errors = _normalize_error_detail(response.data)
        messages = _flatten_error_messages(normalized_errors)
        if messages:
            return messages[0]

    status_messages = {
        400: "请求参数错误",
        401: "未授权，请先登录",
        403: "权限不足",
        404: "资源不存在",
        405: "不允许的请求方法",
        500: "服务器内部错误",
    }
    return status_messages.get(response.status_code, "请求处理失败")


__all__ = ["custom_exception_handler", "get_error_message"]
