"""
知识图谱模块配置
Knowledge Module Configuration
"""
from django.apps import AppConfig


# 维护意图：知识图谱模块配置类 Knowledge Module Config Class
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgeConfig(AppConfig):
    """
    知识图谱模块配置类
    Knowledge Module Config Class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knowledge'
    verbose_name = '知识图谱 Knowledge'
