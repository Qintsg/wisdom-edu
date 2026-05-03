"""
用户模块配置
Users Module Configuration
"""
from django.apps import AppConfig


# 维护意图：用户模块配置类 Users Module Config Class
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class UsersConfig(AppConfig):
    """
    用户模块配置类
    Users Module Config Class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = '用户管理 Users'
