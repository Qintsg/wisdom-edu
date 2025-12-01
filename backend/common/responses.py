"""
统一API响应格式

提供标准化的API响应函数
"""
from rest_framework.response import Response
from rest_framework import status


def api_response(data=None, msg='OK', code=200, status_code=None):
    """
    统一API响应格式
    
    Args:
        data: 响应数据
        msg: 响应消息
        code: 业务状态码
        status_code: HTTP状态码
    
    Returns:
        Response: DRF响应对象
    """
    if status_code is None:
        status_code = code if code < 600 else 200

    return Response({
        'code': code,
        'msg': msg,
        'data': data
    }, status=status_code)


def success_response(data=None, msg='OK'):
    """成功响应 (HTTP 200)"""
    return api_response(data=data, msg=msg, code=200)


def created_response(data=None, msg='创建成功'):
    """创建成功响应 (HTTP 201)"""
    return api_response(data=data, msg=msg, code=201, status_code=201)


def error_response(msg='请求失败', code=400, data=None):
    """错误响应"""
    return api_response(data=data, msg=msg, code=code, status_code=code)


def not_found_response(msg='资源不存在'):
    """资源不存在响应 (HTTP 404)"""
    return error_response(msg=msg, code=404)


def unauthorized_response(msg='未授权，请先登录'):
    """未授权响应 (HTTP 401)"""
    return error_response(msg=msg, code=401)


def forbidden_response(msg='权限不足'):
    """权限不足响应 (HTTP 403)"""
    return error_response(msg=msg, code=403)


__all__ = [
    'api_response',
    'success_response',
    'created_response',
    'error_response',
    'not_found_response',
    'unauthorized_response',
    'forbidden_response',
]
