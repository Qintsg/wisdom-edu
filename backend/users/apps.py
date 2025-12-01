"""
用户模块配置
Users Module Configuration
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    用户模块配置类
    Users Module Config Class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = '用户管理 Users'
