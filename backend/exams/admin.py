"""
考试模块 - Admin配置
"""
from django.contrib import admin
from .models import Exam, ExamQuestion, ExamSubmission, FeedbackReport


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """考试管理"""
    list_display = ['title', 'exam_type', 'course', 'status', 'created_at']
    list_filter = ['exam_type', 'status', 'course']
    search_fields = ['title']


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    """考试题目关联管理"""
    list_display = ['exam', 'question', 'score', 'order']


@admin.register(ExamSubmission)
class ExamSubmissionAdmin(admin.ModelAdmin):
    """考试提交管理"""
    list_display = ['exam', 'user', 'score', 'is_passed', 'submitted_at']
    list_filter = ['is_passed', 'exam']
    search_fields = ['user__username']


@admin.register(FeedbackReport)
class FeedbackReportAdmin(admin.ModelAdmin):
    """反馈报告管理"""
    list_display = ['user', 'exam', 'status', 'generated_at']
    list_filter = ['status']
    search_fields = ['user__username']
