"""
考试模块 - Admin配置
"""
from django.contrib import admin
from .models import Exam, ExamQuestion, ExamSubmission, FeedbackReport


# 维护意图：考试管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """考试管理"""
    list_display = ['title', 'exam_type', 'course', 'status', 'created_at']
    list_filter = ['exam_type', 'status', 'course']
    search_fields = ['title']


# 维护意图：考试题目关联管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    """考试题目关联管理"""
    list_display = ['exam', 'question', 'score', 'order']


# 维护意图：考试提交管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(ExamSubmission)
class ExamSubmissionAdmin(admin.ModelAdmin):
    """考试提交管理"""
    list_display = ['exam', 'user', 'score', 'is_passed', 'submitted_at']
    list_filter = ['is_passed', 'exam']
    search_fields = ['user__username']


# 维护意图：反馈报告管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(FeedbackReport)
class FeedbackReportAdmin(admin.ModelAdmin):
    """反馈报告管理"""
    list_display = ['user', 'exam', 'status', 'generated_at']
    list_filter = ['status']
    search_fields = ['user__username']
