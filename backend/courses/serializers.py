"""
课程模块 - 序列化器

提供课程、班级、选课相关的序列化器
"""
from rest_framework import serializers
from .models import Course, Class, Enrollment, Announcement


# 维护意图：课程序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class CourseSerializer(serializers.ModelSerializer):
    """课程序列化器"""
    course_cover = serializers.ImageField(source='cover', required=False)
    
    # 维护意图：定义课程实体的序列化输出字段
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """定义课程实体的序列化输出字段。"""

        model = Course
        fields = ['id', 'name', 'description', 'course_cover', 'term', 
                  'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


# 维护意图：班级序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ClassSerializer(serializers.ModelSerializer):
    """班级序列化器"""
    course_name = serializers.CharField(
        source='course.name', read_only=True, default=None, allow_null=True
    )
    teacher_name = serializers.CharField(
        source='teacher.username', read_only=True, default=None, allow_null=True
    )
    
    # 维护意图：定义班级实体的序列化输出字段
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """定义班级实体的序列化输出字段。"""

        model = Class
        fields = ['id', 'course', 'name', 'teacher', 'semester', 
                  'course_name', 'teacher_name', 'created_at']
        read_only_fields = ['id', 'created_at']


# 维护意图：选课记录序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class EnrollmentSerializer(serializers.ModelSerializer):
    """选课记录序列化器"""
    course_id = serializers.IntegerField(source='class_obj.course_id', read_only=True)
    course_name = serializers.CharField(
        source='class_obj.course.name', read_only=True, default=None, allow_null=True
    )
    course_cover = serializers.ImageField(
        source='class_obj.course.cover', read_only=True, default=None, allow_null=True
    )
    class_id = serializers.IntegerField(source='class_obj.id', read_only=True)
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    
    # 维护意图：定义选课记录的展示字段集合
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """定义选课记录的展示字段集合。"""

        model = Enrollment
        fields = ['id', 'course_id', 'course_name', 'course_cover', 
                  'class_id', 'class_name', 'role', 'enrolled_at']


# 维护意图：课程选择序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class CourseSelectSerializer(serializers.Serializer):
    """课程选择序列化器"""
    course_id = serializers.IntegerField(required=True)
    class_id = serializers.IntegerField(required=False)


# 维护意图：班级公告序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class AnnouncementSerializer(serializers.ModelSerializer):
    """班级公告序列化器"""
    created_by_name = serializers.CharField(
        source='created_by.username', read_only=True, default=None
    )

    # 维护意图：定义班级公告的序列化字段与只读限制
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """定义班级公告的序列化字段与只读限制。"""

        model = Announcement
        fields = ['id', 'class_obj', 'title', 'content', 'created_by',
                  'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_by_name', 'created_at', 'updated_at']
