"""
课程模块配置
Courses Module Configuration
"""
from django.apps import AppConfig


class CoursesConfig(AppConfig):
    """
    课程模块配置类
    Courses Module Config Class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'
    verbose_name = '课程管理 Courses'

    def ready(self) -> None:
        """注册课程删除后的外部资产清理信号。"""
        # 确保应用启动时注册 signal receiver。
        from . import signals  # noqa: F401
