"""
操作日志模块 - URL配置

API命名规范：
- /api/admin/* - 管理员专用接口
"""
from django.urls import path

from . import views

app_name = 'logs'

urlpatterns = [
    # ============ 管理员端 ============
    path('api/admin/logs', views.list_operation_logs, name='list_logs'),
    path('api/admin/logs/<int:log_id>', views.get_operation_log_detail, name='log_detail'),
    path('api/admin/logs/statistics', views.get_log_statistics, name='log_statistics'),
    path('api/admin/logs/options', views.get_log_filter_options, name='log_options'),
    path('api/admin/logs/modules', views.get_log_modules, name='log_modules'),
    path('api/admin/logs/actions', views.get_log_actions, name='log_actions'),
    path('api/admin/logs/export', views.export_logs, name='log_export'),
    path('api/admin/logs/clean', views.clean_expired_logs, name='log_clean'),
]
