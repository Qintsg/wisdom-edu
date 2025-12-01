"""
测评模块 - Admin配置
"""
from django.contrib import admin
from .models import (
    Question, Assessment, AssessmentQuestion, SurveyQuestion, 
    AbilityScore, AssessmentStatus, AssessmentResult
)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """题目管理"""
    list_display = ['id', 'question_type', 'difficulty', 'course', 'created_at']
    list_filter = ['question_type', 'difficulty', 'course']
    search_fields = ['content']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """测评管理"""
    list_display = ['title', 'assessment_type', 'course', 'is_active']
    list_filter = ['assessment_type', 'is_active', 'course']


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    """测评题目关联管理"""
    list_display = ['assessment', 'question', 'order']


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    """问卷题目管理"""
    list_display = ['id', 'question_type', 'order', 'is_global', 'course']
    list_filter = ['question_type', 'is_global', 'course']


@admin.register(AbilityScore)
class AbilityScoreAdmin(admin.ModelAdmin):
    """能力评分管理"""
    list_display = ['user', 'course', 'created_at']
    list_filter = ['course']
    search_fields = ['user__username']


@admin.register(AssessmentStatus)
class AssessmentStatusAdmin(admin.ModelAdmin):
    """测评状态管理"""
    list_display = ['user', 'course', 'knowledge_done', 'ability_done', 'habit_done']
    list_filter = ['course', 'knowledge_done', 'ability_done', 'habit_done']
    search_fields = ['user__username']


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    """测评结果管理"""
    list_display = ['user', 'assessment', 'score', 'completed_at']
    list_filter = ['assessment', 'course']
    search_fields = ['user__username']
