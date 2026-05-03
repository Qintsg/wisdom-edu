"""AI 服务 WebSocket 认证中间件。"""

from __future__ import annotations

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


# 维护意图：通过 JWT token 解析 WebSocket 用户
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
@database_sync_to_async
def _resolve_user_from_token(raw_token: str):
    """通过 JWT token 解析 WebSocket 用户。"""
    authentication = JWTAuthentication()
    validated_token = authentication.get_validated_token(raw_token)
    return authentication.get_user(validated_token)


# 维护意图：从查询参数 `token` 中解析 JWT 并注入 scope.user
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
class QueryStringJWTAuthMiddleware(BaseMiddleware):
    """从查询参数 `token` 中解析 JWT 并注入 scope.user。"""

    async def __call__(self, scope, receive, send):
        close_old_connections()
        scope["user"] = AnonymousUser()
        try:
            # 仅在 query_string 为 bytes 时执行解析，避免错误类型直接进入 decode。
            raw_query_string = scope.get("query_string", b"")
            if not isinstance(raw_query_string, bytes):
                return await super().__call__(scope, receive, send)

            query_params = parse_qs(raw_query_string.decode())
            token = (query_params.get("token") or [None])[0]
            if token:
                scope["user"] = await _resolve_user_from_token(token)
        # 鉴权失败时回落为匿名用户，避免 WebSocket 握手直接中断。
        except (AuthenticationFailed, InvalidToken, TokenError, TypeError, ValueError):
            scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)


# 维护意图：包装 channels 路由，提供 query string JWT 认证能力
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def query_string_jwt_auth_middleware_stack(inner):
    """包装 channels 路由，提供 query string JWT 认证能力。"""
    return QueryStringJWTAuthMiddleware(inner)


# 向后兼容 channels 路由中既有的导入名称。
QueryStringJWTAuthMiddlewareStack = query_string_jwt_auth_middleware_stack
