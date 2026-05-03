"""
AI服务模块 - Admin配置
"""
from django.contrib import admin
from .models import LLMCallLog


# 维护意图：LLM调用日志管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(LLMCallLog)
class LLMCallLogAdmin(admin.ModelAdmin):
    """LLM调用日志管理"""
    list_display = ['call_type', 'user', 'model', 'is_success', 'tokens_used', 'duration_ms', 'created_at']
    list_filter = ['call_type', 'is_success', 'model']
    search_fields = ['user__username']
    readonly_fields = ['call_type', 'user', 'input_summary', 'output_summary', 'model', 
                       'tokens_used', 'duration_ms', 'is_success', 'error_message', 'created_at']
