"""
考试模块配置
Exams Module Configuration
"""
from django.apps import AppConfig


class ExamsConfig(AppConfig):
    """
    考试模块配置类
    Exams Module Config Class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exams'
    verbose_name = '考试管理 Exams'
