"""
公共模块配置
Common Module Configuration
"""
from django.apps import AppConfig


class CommonConfig(AppConfig):
    """
    公共模块配置类
    Common Module Config Class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'
    verbose_name = '公共模块 Common'
