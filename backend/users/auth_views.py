"""用户模块 - 认证与公共接口。"""

from __future__ import annotations

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from common.responses import created_response, error_response, success_response
from .auth_password_views import password_reset, password_reset_send
from .auth_support import (
    authenticate_user_login,
    blacklist_refresh_token,
    build_userinfo_payload,
    change_user_password,
    get_authenticated_user,
    refresh_access_token,
    register_user,
    update_userinfo_payload,
)
from .serializers import CustomTokenObtainPairSerializer


# 维护意图：自定义登录视图 已审查
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义登录视图 已审查。"""

    serializer_class = CustomTokenObtainPairSerializer


# 维护意图：用户注册
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def register(request: Request) -> Response:
    """用户注册。"""
    payload, error_message, status_code = register_user(request.data)
    if error_message:
        return error_response(msg=error_message, code=status_code)
    return created_response(data=payload, msg="注册成功")


# 维护意图：用户登录，支持用户名、邮箱或手机号
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request: Request) -> Response:
    """用户登录，支持用户名、邮箱或手机号。"""
    payload, error_message, status_code = authenticate_user_login(request, request.data)
    if error_message:
        return error_response(msg=error_message, code=status_code)
    return success_response(data=payload, msg="登录成功")


# 维护意图：获取当前用户信息
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def userinfo(request: Request) -> Response:
    """获取当前用户信息。"""
    user = get_authenticated_user(request)
    return success_response(data=build_userinfo_payload(user))


# 维护意图：更新当前用户信息
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_userinfo(request: Request) -> Response:
    """更新当前用户信息。"""
    user = get_authenticated_user(request)
    payload, error_message = update_userinfo_payload(user, request.data, request.FILES)
    if error_message:
        return error_response(msg=error_message)
    return success_response(data=payload, msg="用户信息已更新")


# 维护意图：刷新 JWT 访问令牌
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def token_refresh(request: Request) -> Response:
    """刷新 JWT 访问令牌。"""
    payload, error_message, status_code = refresh_access_token(request.data.get("refresh"))
    if error_message:
        return error_response(msg=error_message, code=status_code)
    return success_response(data=payload, msg="令牌已刷新")


# 维护意图：修改当前用户密码
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request: Request) -> Response:
    """修改当前用户密码。"""
    error_message = change_user_password(get_authenticated_user(request), request.data)
    if error_message:
        return error_response(msg=error_message)
    return success_response(msg="密码修改成功")


# 维护意图：退出登录，并尽力拉黑 refresh token
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request: Request) -> Response:
    """退出登录，并尽力拉黑 refresh token。"""
    blacklist_refresh_token(request.data.get("refresh"))
    return success_response(msg="退出成功")


# 维护意图：健康检查端点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def health(_request: Request) -> Response:
    """健康检查端点。"""
    return success_response(data={"status": "healthy"})
