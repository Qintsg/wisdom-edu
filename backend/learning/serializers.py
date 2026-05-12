"""
学习路径模块 - 序列化器

提供学习路径、节点、进度相关的序列化器
"""
from rest_framework import serializers
from .models import LearningPath, PathNode, NodeProgress


class PathNodeSerializer(serializers.ModelSerializer):
    """路径节点序列化器"""
    tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = PathNode
        fields = ['id', 'title', 'goal', 'criterion', 'suggestion',
                  'status', 'order_index', 'is_inserted', 'tasks_count']

    @staticmethod
    def get_tasks_count(obj):
        return obj.resources.count() + (1 if obj.exam else 0)


class LearningPathSerializer(serializers.ModelSerializer):
    """学习路径序列化器"""
    nodes = PathNodeSerializer(many=True, read_only=True)

    class Meta:
        model = LearningPath
        fields = ['id', 'ai_reason', 'is_dynamic', 'nodes',
                  'generated_at', 'updated_at']


class PathAdjustSerializer(serializers.Serializer):
    """路径调整序列化器"""
    course_id = serializers.IntegerField()
    reason = serializers.CharField(required=False)


class NodeDetailSerializer(serializers.ModelSerializer):
    """节点详情序列化器"""
    resources = serializers.SerializerMethodField()
    exercises = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    mastery_before = serializers.SerializerMethodField()
    mastery_after = serializers.SerializerMethodField()

    class Meta:
        model = PathNode
        fields = ['id', 'title', 'goal', 'criterion', 'suggestion',
                  'status', 'resources', 'exercises', 'progress',
                  'mastery_before', 'mastery_after']

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

    @staticmethod
    def get_exercises(obj):
        if obj.exam:
            return [{
                'exam_id': obj.exam.id,
                'title': obj.exam.title,
                'required': True
            }]
        return []

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
