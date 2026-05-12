"""
操作日志模块 - 序列化器
Operation Logs Module - Serializers
"""
from rest_framework import serializers

from .models import OperationLog


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""

    username = serializers.CharField(
        source='user.username', read_only=True, default=None, allow_null=True
    )
    action_type_display = serializers.CharField(
        source='get_action_type_display',
        read_only=True
    )
    module_display = serializers.CharField(
        source='get_module_display',
        read_only=True
    )

    class Meta:
        """声明操作日志序列化器暴露的字段集合。"""

        model = OperationLog
        fields = [
            'id', 'user', 'username', 'action_type', 'action_type_display',
            'module', 'module_display', 'description', 'request_path',
            'request_method', 'request_params', 'response_status',
            'is_success', 'error_message', 'ip_address', 'user_agent',
            'created_at'
        ]
        read_only_fields = fields
