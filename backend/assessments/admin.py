"""
测评模块 - Admin配置
"""
from django.contrib import admin
from .models import (
    Question, Assessment, AssessmentQuestion, SurveyQuestion, 
    AbilityScore, AssessmentStatus, AssessmentResult
)


# 维护意图：题目管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """题目管理"""
    list_display = ['id', 'question_type', 'difficulty', 'course', 'created_at']
    list_filter = ['question_type', 'difficulty', 'course']
    search_fields = ['content']


# 维护意图：测评管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    """测评管理"""
    list_display = ['title', 'assessment_type', 'course', 'is_active']
    list_filter = ['assessment_type', 'is_active', 'course']


# 维护意图：测评题目关联管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    """测评题目关联管理"""
    list_display = ['assessment', 'question', 'order']


# 维护意图：问卷题目管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    """问卷题目管理"""
    list_display = ['id', 'question_type', 'order', 'is_global', 'course']
    list_filter = ['question_type', 'is_global', 'course']


# 维护意图：能力评分管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(AbilityScore)
class AbilityScoreAdmin(admin.ModelAdmin):
    """能力评分管理"""
    list_display = ['user', 'course', 'created_at']
    list_filter = ['course']
    search_fields = ['user__username']


# 维护意图：测评状态管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(AssessmentStatus)
class AssessmentStatusAdmin(admin.ModelAdmin):
    """测评状态管理"""
    list_display = ['user', 'course', 'knowledge_done', 'ability_done', 'habit_done']
    list_filter = ['course', 'knowledge_done', 'ability_done', 'habit_done']
    search_fields = ['user__username']


# 维护意图：测评结果管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    """测评结果管理"""
    list_display = ['user', 'assessment', 'score', 'completed_at']
    list_filter = ['assessment', 'course']
    search_fields = ['user__username']
