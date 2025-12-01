"""
AI服务模块 - Admin配置
"""
from django.contrib import admin
from .models import LLMCallLog


@admin.register(LLMCallLog)
class LLMCallLogAdmin(admin.ModelAdmin):
    """LLM调用日志管理"""
    list_display = ['call_type', 'user', 'model', 'is_success', 'tokens_used', 'duration_ms', 'created_at']
    list_filter = ['call_type', 'is_success', 'model']
    search_fields = ['user__username']
    readonly_fields = ['call_type', 'user', 'input_summary', 'output_summary', 'model', 
                       'tokens_used', 'duration_ms', 'is_success', 'error_message', 'created_at']
