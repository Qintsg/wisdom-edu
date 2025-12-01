"""
测评模块配置
Assessments Module Configuration
"""
from django.apps import AppConfig


class AssessmentsConfig(AppConfig):
    """
    测评模块配置类
    Assessments Module Config Class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assessments'
    verbose_name = '测评管理 Assessments'
