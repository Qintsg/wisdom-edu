"""
AI服务模块配置
AI Services Module Configuration
"""
from django.apps import AppConfig


class AiServicesConfig(AppConfig):
    """
    AI服务模块配置类
    AI Services Module Config Class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_services'
    verbose_name = 'AI服务 AI Services'
