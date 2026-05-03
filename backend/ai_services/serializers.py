"""
AI服务模块 - 序列化器

提供AI服务相关的序列化器
"""
from rest_framework import serializers


# 维护意图：画像诊断序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class AIProfileAnalysisSerializer(serializers.Serializer):
    """画像诊断序列化器"""
    refresh = serializers.BooleanField(required=False, default=False)


# 维护意图：路径规划序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class AIPathPlanningSerializer(serializers.Serializer):
    """路径规划序列化器"""
    target = serializers.CharField(required=False)
    constraints = serializers.DictField(required=False)


# 维护意图：资源推荐理由序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class AIResourceReasonSerializer(serializers.Serializer):
    """资源推荐理由序列化器"""
    resource_id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    point_id = serializers.IntegerField(required=False)


# 维护意图：反馈报告生成序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class AIFeedbackReportSerializer(serializers.Serializer):
    """反馈报告生成序列化器"""
    exam_id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    include_next_tasks = serializers.BooleanField(required=False, default=True)
