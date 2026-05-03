"""统一 API 响应格式。"""

from __future__ import annotations

from typing import Any

from rest_framework.response import Response


# 维护意图：构造统一响应，保持旧版 code/msg/data 契约并附加可选错误详情。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def api_response(
    data: Any = None,
    msg: str = "OK",
    code: int = 200,
    status_code: int | None = None,
    error_code: str = "",
    errors: Any = None,
) -> Response:
    """
    构造统一响应，保持旧版 code/msg/data 契约并附加可选错误详情。

    :param data: 响应数据。
    :param msg: 用户可读消息。
    :param code: 业务状态码。
    :param status_code: HTTP 状态码。
    :param error_code: 稳定错误类型，供前端或日志检索使用。
    :param errors: 字段级或结构化错误详情。
    :return: DRF Response。
    """
    if status_code is None:
        status_code = code if code < 600 else 200
    response_data = data
    if response_data is None and errors is not None:
        response_data = {"errors": errors}

    payload = {
        "code": code,
        "msg": msg,
        "data": response_data,
    }
    if code >= 400 or status_code >= 400:
        payload["error"] = {
            "type": error_code or f"HTTP_{status_code}",
            "details": errors,
        }

    return Response(payload, status=status_code)


# 维护意图：成功响应 (HTTP 200)
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def success_response(data: Any = None, msg: str = "OK") -> Response:
    """成功响应 (HTTP 200)"""
    return api_response(data=data, msg=msg, code=200)


# 维护意图：创建成功响应 (HTTP 201)
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def created_response(data: Any = None, msg: str = "创建成功") -> Response:
    """创建成功响应 (HTTP 201)"""
    return api_response(data=data, msg=msg, code=201, status_code=201)


# 维护意图：错误响应
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def error_response(
    msg: str = "请求失败",
    code: int = 400,
    data: Any = None,
    error_code: str = "",
    errors: Any = None,
) -> Response:
    """错误响应"""
    return api_response(
        data=data,
        msg=msg,
        code=code,
        status_code=code,
        error_code=error_code,
        errors=errors,
    )


# 维护意图：资源不存在响应 (HTTP 404)
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def not_found_response(msg: str = "资源不存在") -> Response:
    """资源不存在响应 (HTTP 404)"""
    return error_response(msg=msg, code=404)


# 维护意图：未授权响应 (HTTP 401)
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def unauthorized_response(msg: str = "未授权，请先登录") -> Response:
    """未授权响应 (HTTP 401)"""
    return error_response(msg=msg, code=401)


# 维护意图：权限不足响应 (HTTP 403)
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def forbidden_response(msg: str = "权限不足") -> Response:
    """权限不足响应 (HTTP 403)"""
    return error_response(msg=msg, code=403)


__all__ = [
    "api_response",
    "success_response",
    "created_response",
    "error_response",
    "not_found_response",
    "unauthorized_response",
    "forbidden_response",
]
