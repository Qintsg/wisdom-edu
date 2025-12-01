"""
测评模块 - 序列化器

提供题目、测评、问卷相关的序列化器
"""
import re
from django.utils.html import strip_tags
from rest_framework import serializers
from .models import Question, Assessment, SurveyQuestion


def _clean_html(value):
    """去除字符串中的HTML标签并清理多余空白。"""
    if not value or not isinstance(value, str):
        return value
    cleaned = strip_tags(value)
    return re.sub(r'\s+', ' ', cleaned).strip()


def _clean_options(options):
    """清洗选项列表中的HTML标签。"""
    if not options or not isinstance(options, list):
        return options
    cleaned = []
    for opt in options:
        if isinstance(opt, dict):
            opt = {k: (_clean_html(v) if isinstance(v, str) else v) for k, v in opt.items()}
        elif isinstance(opt, str):
            opt = _clean_html(opt)
        cleaned.append(opt)
    return cleaned


class QuestionSerializer(serializers.ModelSerializer):
    """题目序列化器"""
    points = serializers.SerializerMethodField()
    
    class Meta:
        """声明题目管理接口的完整字段集合。"""
        model = Question
        fields = ['id', 'course', 'content', 'question_type', 'options',
                  'answer', 'analysis', 'knowledge_points', 'difficulty',
                  'score', 'points', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    @staticmethod
    def get_points(obj):
        """返回题目绑定的知识点 ID 列表。"""
        return list(obj.knowledge_points.values_list('id', flat=True))

    def to_representation(self, instance):
        """输出时清洗HTML标签。"""
        data = super().to_representation(instance)
        data['content'] = _clean_html(data.get('content', ''))
        data['analysis'] = _clean_html(data.get('analysis', ''))
        data['options'] = _clean_options(data.get('options', []))
        return data


class QuestionListSerializer(serializers.ModelSerializer):
    """题目列表序列化器（简化版）"""
    points = serializers.SerializerMethodField()
    
    class Meta:
        """声明题目列表页的精简展示字段。"""
        model = Question
        fields = ['id', 'content', 'question_type', 'points', 'difficulty',
                  'created_at', 'updated_at']
    
    @staticmethod
    def get_points(obj):
        """返回题目列表项绑定的知识点 ID 列表。"""
        return list(obj.knowledge_points.values_list('id', flat=True))


class QuestionDetailSerializer(serializers.ModelSerializer):
    """题目详情序列化器（含知识点名称）"""
    points = serializers.SerializerMethodField()
    creator = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        """声明题目详情页需要输出的字段。"""
        model = Question
        fields = ['id', 'content', 'question_type', 'options', 'answer',
                  'analysis', 'points', 'difficulty', 'score', 'creator']
    
    @staticmethod
    def get_points(obj):
        """返回题目详情页使用的知识点名称列表。"""
        return [{'point_id': p.id, 'point_name': p.name} 
                for p in obj.knowledge_points.all()]


class AssessmentSerializer(serializers.ModelSerializer):
    """测评序列化器"""
    
    class Meta:
        """声明测评记录的基础输出字段。"""
        model = Assessment
        fields = ['id', 'course', 'title', 'assessment_type', 'description',
                  'is_active', 'created_at']


class AssessmentQuestionSerializer(serializers.ModelSerializer):
    """测评题目序列化器（学生端，不含答案）"""
    points = serializers.SerializerMethodField()
    
    class Meta:
        """声明学生端测评题目需要暴露的字段。"""
        model = Question
        fields = ['id', 'content', 'options', 'question_type', 'points']
    
    @staticmethod
    def get_points(obj):
        """返回测评题目绑定的知识点 ID 列表。"""
        return list(obj.knowledge_points.values_list('id', flat=True))

    def to_representation(self, instance):
        """输出时清洗HTML标签。"""
        data = super().to_representation(instance)
        data['content'] = _clean_html(data.get('content', ''))
        data['options'] = _clean_options(data.get('options', []))
        return data


class SurveyQuestionSerializer(serializers.ModelSerializer):
    """问卷题目序列化器"""
    
    class Meta:
        """声明问卷题目的基础输出字段。"""
        model = SurveyQuestion
        fields = ['id', 'text', 'question_type', 'options', 'order']


class AssessmentSubmitSerializer(serializers.Serializer):
    """测评提交序列化器"""
    answers = serializers.ListField(child=serializers.DictField())


class SurveySubmitSerializer(serializers.Serializer):
    """问卷提交序列化器"""
    survey_id = serializers.IntegerField()
    responses = serializers.ListField(child=serializers.DictField())
