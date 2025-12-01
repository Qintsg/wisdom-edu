"""
知识图谱模块配置
Knowledge Module Configuration
"""
from django.apps import AppConfig


class KnowledgeConfig(AppConfig):
    """
    知识图谱模块配置类
    Knowledge Module Config Class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knowledge'
    verbose_name = '知识图谱 Knowledge'
