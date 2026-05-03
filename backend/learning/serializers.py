"""
学习路径模块 - 序列化器

提供学习路径、节点、进度相关的序列化器
"""
from rest_framework import serializers
from .models import LearningPath, PathNode, NodeProgress


# 维护意图：路径节点序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class PathNodeSerializer(serializers.ModelSerializer):
    """路径节点序列化器"""
    tasks_count = serializers.SerializerMethodField()

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        model = PathNode
        fields = ['id', 'title', 'goal', 'criterion', 'suggestion',
                  'status', 'order_index', 'is_inserted', 'tasks_count']

    # 维护意图：get tasks count
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @staticmethod
    def get_tasks_count(obj):
        return obj.resources.count() + (1 if obj.exam else 0)


# 维护意图：学习路径序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class LearningPathSerializer(serializers.ModelSerializer):
    """学习路径序列化器"""
    nodes = PathNodeSerializer(many=True, read_only=True)

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        model = LearningPath
        fields = ['id', 'ai_reason', 'is_dynamic', 'nodes',
                  'generated_at', 'updated_at']


# 维护意图：路径调整序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class PathAdjustSerializer(serializers.Serializer):
    """路径调整序列化器"""
    course_id = serializers.IntegerField()
    reason = serializers.CharField(required=False)


# 维护意图：节点详情序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class NodeDetailSerializer(serializers.ModelSerializer):
    """节点详情序列化器"""
    resources = serializers.SerializerMethodField()
    exercises = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    mastery_before = serializers.SerializerMethodField()
    mastery_after = serializers.SerializerMethodField()

    # 维护意图：Meta
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        model = PathNode
        fields = ['id', 'title', 'goal', 'criterion', 'suggestion',
                  'status', 'resources', 'exercises', 'progress',
                  'mastery_before', 'mastery_after']

    # 维护意图：get resources
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @staticmethod
    def get_resources(obj):
        return [{
            'resource_id': r.id,
            'title': r.title,
            'type': r.resource_type,
            'url': r.url or (r.file.url if r.file else None),
            'required': True,
            'recommended_reason': ''
        } for r in obj.resources.all()]

    # 维护意图：get exercises
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @staticmethod
    def get_exercises(obj):
        if obj.exam:
            return [{
                'exam_id': obj.exam.id,
                'title': obj.exam.title,
                'required': True
            }]
        return []

    # 维护意图：get progress
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            progress = NodeProgress.objects.filter(
                node=obj,
                user=request.user
            ).first()
            if progress:
                return {
                    'resources_completed': len(progress.completed_resources),
                    'resources_total': obj.resources.count(),
                    'exercises_completed': len(progress.completed_exams),
                    'exercises_total': 1 if obj.exam else 0
                }
        return {
            'resources_completed': 0,
            'resources_total': obj.resources.count(),
            'exercises_completed': 0,
            'exercises_total': 1 if obj.exam else 0
        }

    # 维护意图：get mastery before
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_mastery_before(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and obj.knowledge_point:
            progress = NodeProgress.objects.filter(
                node=obj,
                user=request.user
            ).first()
            if progress and progress.mastery_before:
                return float(progress.mastery_before)
        return 0

    # 维护意图：get mastery after
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_mastery_after(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and obj.knowledge_point:
            progress = NodeProgress.objects.filter(
                node=obj,
                user=request.user
            ).first()
            if progress and progress.mastery_after:
                return float(progress.mastery_after)
        return None
