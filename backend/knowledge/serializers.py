"""
知识图谱模块 - 序列化器

提供知识点、关系、资源相关的序列化器
"""
from rest_framework import serializers

from .models import KnowledgePoint, KnowledgeRelation, Resource, KnowledgeMastery


# 维护意图：知识点序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgePointSerializer(serializers.ModelSerializer):
    """知识点序列化器"""

    # 维护意图：声明知识点基础信息的读写字段
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """声明知识点基础信息的读写字段。"""
        model = KnowledgePoint
        fields = ['id', 'course', 'name', 'description', 'chapter', 
                  'point_type', 'level', 'tags', 'cognitive_dimension',
                  'category', 'teaching_goal',
                  'order', 'is_published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# 维护意图：知识点详情序列化器（含关联资源）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgePointDetailSerializer(serializers.ModelSerializer):
    """知识点详情序列化器（含关联资源）"""

    mastery_rate = serializers.SerializerMethodField()
    prerequisites = serializers.SerializerMethodField()
    postrequisites = serializers.SerializerMethodField()
    resources = serializers.SerializerMethodField()

    # 维护意图：声明知识点详情页需要输出的聚合字段
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """声明知识点详情页需要输出的聚合字段。"""
        model = KnowledgePoint
        fields = ['id', 'name', 'description', 'chapter', 'point_type',
                  'level', 'tags', 'cognitive_dimension', 'category', 'teaching_goal',
                  'mastery_rate', 'prerequisites', 'postrequisites', 'resources']

    # 维护意图：读取当前请求用户对该知识点的掌握度
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_mastery_rate(self, obj):
        """读取当前请求用户对该知识点的掌握度。"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            mastery = KnowledgeMastery.objects.filter(
                user=request.user,
                knowledge_point=obj
            ).first()
            return float(mastery.mastery_rate) if mastery else 0
        return 0

    # 维护意图：返回该知识点的前置知识点列表
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @staticmethod
    def get_prerequisites(obj):
        """返回该知识点的前置知识点列表。"""
        relations = KnowledgeRelation.objects.filter(
            post_point=obj,
            relation_type='prerequisite'
        ).select_related('pre_point')
        return [
            {'point_id': relation.pre_point_id, 'point_name': relation.pre_point.name}
            for relation in relations
        ]

    # 维护意图：返回该知识点的后续知识点列表
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @staticmethod
    def get_postrequisites(obj):
        """返回该知识点的后续知识点列表。"""
        relations = KnowledgeRelation.objects.filter(
            pre_point=obj,
            relation_type='prerequisite'
        ).select_related('post_point')
        return [
            {'point_id': relation.post_point_id, 'point_name': relation.post_point.name}
            for relation in relations
        ]

    # 维护意图：获取关联资源列表（包含视频时长等信息）
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @staticmethod
    def get_resources(obj):
        """获取关联资源列表（包含视频时长等信息）"""
        try:
            resources = obj.resources.filter(is_visible=True).order_by('sort_order', 'id')
        except Exception:
            # 兼容处理：如果sort_order字段尚未迁移，使用默认排序
            resources = obj.resources.filter(is_visible=True).order_by('id')

        result = []
        for resource in resources:
            item = {
                'resource_id': resource.id,
                'title': resource.title,
                'type': resource.resource_type,
            }
            # 安全访问新字段（兼容未迁移的数据库）
            try:
                item['chapter_number'] = resource.chapter_number
                item['sort_order'] = resource.sort_order
                # 视频资源附加时长信息
                if resource.resource_type == 'video' and resource.duration:
                    item['duration'] = resource.duration
                    minutes = resource.duration // 60
                    seconds = resource.duration % 60
                    item['duration_display'] = f"{minutes:02d}:{seconds:02d}"
            except AttributeError:
                pass
            result.append(item)
        return result


# 维护意图：知识点关系序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgeRelationSerializer(serializers.ModelSerializer):
    """知识点关系序列化器"""

    # 维护意图：声明知识点关系记录的基础输出字段
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """声明知识点关系记录的基础输出字段。"""
        model = KnowledgeRelation
        fields = ['id', 'course', 'pre_point', 'post_point', 'relation_type']


# 维护意图：知识图谱序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgeMapSerializer(serializers.Serializer):
    """知识图谱序列化器"""

    nodes = serializers.ListField()
    edges = serializers.ListField()


# 维护意图：资源序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ResourceSerializer(serializers.ModelSerializer):
    """资源序列化器"""

    knowledge_points = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=KnowledgePoint.objects.all(),
        required=False
    )
    format = serializers.SerializerMethodField()
    duration_display = serializers.SerializerMethodField()

    # 维护意图：声明资源管理接口需要暴露的字段
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """声明资源管理接口需要暴露的字段。"""
        model = Resource
        fields = ['id', 'course', 'title', 'resource_type', 'file', 'url',
                  'description', 'duration', 'duration_display',
                  'chapter_number', 'sort_order',
                  'knowledge_points', 'is_visible', 'format',
                  'uploaded_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'uploaded_by', 'created_at', 'updated_at']

    # 维护意图：获取资源文件格式
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @staticmethod
    def get_format(obj):
        """获取资源文件格式"""
        if obj.file:
            return obj.file.name.split('.')[-1] if '.' in obj.file.name else ''
        elif obj.url:
            return 'url'
        return ''

    # 维护意图：获取格式化的时长显示（如 "05:30"）
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @staticmethod
    def get_duration_display(obj):
        """获取格式化的时长显示（如 "05:30"）"""
        try:
            if obj.duration is None:
                return None
            minutes = obj.duration // 60
            seconds = obj.duration % 60
            return f"{minutes:02d}:{seconds:02d}"
        except AttributeError:
            return None


# 维护意图：知识图谱导入序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgeMapImportSerializer(serializers.Serializer):
    """知识图谱导入序列化器"""

    file = serializers.FileField()


# 维护意图：知识图谱发布序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgeMapPublishSerializer(serializers.Serializer):
    """知识图谱发布序列化器"""

    course_id = serializers.IntegerField()
    confirm = serializers.BooleanField()


# KnowledgePointCreateSerializer 序列化器：数据验证与转换
# 维护意图：知识点创建序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class KnowledgePointCreateSerializer(serializers.Serializer):
    """知识点创建序列化器"""
    course_id = serializers.IntegerField()
    point_name = serializers.CharField(max_length=200)
    prerequisites = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )
    description = serializers.CharField(required=False, allow_blank=True)
