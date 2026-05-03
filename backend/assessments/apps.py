"""
测评模块配置
Assessments Module Configuration
"""
from django.apps import AppConfig


# 维护意图：测评模块配置类 Assessments Module Config Class
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class AssessmentsConfig(AppConfig):
    """
    测评模块配置类
    Assessments Module Config Class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assessments'
    verbose_name = '测评管理 Assessments'
