"""
AI服务模块 - 序列化器

提供AI服务相关的序列化器
"""
from rest_framework import serializers


class AIProfileAnalysisSerializer(serializers.Serializer):
    """画像诊断序列化器"""
    refresh = serializers.BooleanField(required=False, default=False)


class AIPathPlanningSerializer(serializers.Serializer):
    """路径规划序列化器"""
    target = serializers.CharField(required=False)
    constraints = serializers.DictField(required=False)


class AIResourceReasonSerializer(serializers.Serializer):
    """资源推荐理由序列化器"""
    resource_id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    point_id = serializers.IntegerField(required=False)


class AIFeedbackReportSerializer(serializers.Serializer):
    """反馈报告生成序列化器"""
    exam_id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    include_next_tasks = serializers.BooleanField(required=False, default=True)
