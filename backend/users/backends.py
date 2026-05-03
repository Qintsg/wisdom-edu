"""
用户模块 - 自定义认证后端

支持使用用户名、邮箱或手机号登录
"""
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User


# 维护意图：多字段认证后端 支持使用以下方式登录： - 用户名 (username) - 邮箱 (email) - 手机号 (phone) 认证逻辑： 1. 将输入值同时与 username、email、。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class MultiFieldAuthBackend(ModelBackend):
    """
    多字段认证后端
    
    支持使用以下方式登录：
    - 用户名 (username)
    - 邮箱 (email)
    - 手机号 (phone)
    
    认证逻辑：
    1. 将输入值同时与 username、email、phone 匹配
    2. 匹配到用户后验证密码
    3. 检查用户是否激活
    """
    
    # 维护意图：认证用户
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        认证用户
        
        Args:
            request: HTTP请求对象
            username: 登录凭证（可以是用户名、邮箱或手机号）
            password: 密码
        
        Returns:
            User对象（认证成功）或 None（认证失败）
        """
        if username is None or password is None:
            return None
        
        try:
            user = User.objects.get(
                Q(username=username) | 
                Q(email=username) | 
                Q(phone=username)
            )
        except User.DoesNotExist:
            # 用户不存在 - 仍然运行密码哈希以防止timing attack
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # 理论上不应发生（因为三个字段都有唯一约束）
            # 但作为安全措施，取第一个匹配
            user = User.objects.filter(
                Q(username=username) | 
                Q(email=username) | 
                Q(phone=username)
            ).first()
        
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
