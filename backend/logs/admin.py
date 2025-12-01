"""
操作日志模块 - Admin配置
Operation Logs Module - Admin Configuration
"""
from django.contrib import admin

from .models import OperationLog


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    """操作日志Admin配置"""

    list_display = ['id', 'user', 'action_type', 'module', 'description', 
                   'is_success', 'ip_address', 'created_at']
    list_filter = ['action_type', 'module', 'is_success', 'created_at']
    search_fields = ['user__username', 'description', 'request_path']
    readonly_fields = ['user', 'action_type', 'module', 'description', 
                      'request_path', 'request_method', 'request_params',
                      'response_status', 'is_success', 'error_message',
                      'ip_address', 'user_agent', 'created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
