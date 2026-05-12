"""用户认证模块 - 密码重置公开接口。"""

from __future__ import annotations

import logging
import secrets
import string

from django.core.cache import cache
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from common.responses import error_response, success_response
from .models import User

logger = logging.getLogger(__name__)


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def password_reset_send(request):
    """发送密码重置验证码。"""
    email = request.data.get('email')
    if not email:
        return error_response(msg='请提供邮箱')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # 不泄露邮箱是否已注册，避免被枚举。
        return success_response(msg='如果该邮箱已注册，验证码已发送')

    code = ''.join(secrets.choice(string.digits) for _ in range(6))
    cache_key = f'pwd_reset:{email}'
    cache.set(cache_key, {'code': code, 'user_id': user.id}, timeout=600)

    # TODO: 接入邮件服务 / 短信服务发送验证码；当前保持原有日志行为。
    logger.info('密码重置验证码已生成 email=%s code=%s', email, code)

    return success_response(msg='验证码已发送，请检查邮箱')


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def password_reset(request):
    """使用验证码重置密码。"""
    email = request.data.get('email')
    code = request.data.get('code')
    new_password = request.data.get('new_password')

    if not all([email, code, new_password]):
        return error_response(msg='请提供邮箱、验证码和新密码')

    if len(new_password) < 6:
        return error_response(msg='密码长度不能少于6位')

    cache_key = f'pwd_reset:{email}'
    cached = cache.get(cache_key)

    if not cached or cached['code'] != code:
        return error_response(msg='验证码无效或已过期')

    try:
        user = User.objects.get(id=cached['user_id'])
    except User.DoesNotExist:
        return error_response(msg='用户不存在')

    user.set_password(new_password)
    user.save()
    cache.delete(cache_key)

    return success_response(msg='密码重置成功')
