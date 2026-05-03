"""
操作日志模块应用配置
Operation Logs Module Application Configuration
"""
from django.apps import AppConfig


# 维护意图：操作日志模块配置 Operation Logs Module Config
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class LogsConfig(AppConfig):
    """
    操作日志模块配置
    Operation Logs Module Config
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logs'
    verbose_name = '操作日志 Operation Logs'
