"""
操作日志模块应用配置
Operation Logs Module Application Configuration
"""
from django.apps import AppConfig


class LogsConfig(AppConfig):
    """
    操作日志模块配置
    Operation Logs Module Config
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logs'
    verbose_name = '操作日志 Operation Logs'
