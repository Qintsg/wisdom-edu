"""
学习路径模块配置
Learning Module Configuration
"""
from django.apps import AppConfig


class LearningConfig(AppConfig):
    """
    学习路径模块配置类
    Learning Module Config Class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'learning'
    verbose_name = '学习路径 Learning'
