"""
课程模块 - Admin配置
"""
from django.contrib import admin
from .models import Course, Class, Enrollment, Announcement


# 维护意图：课程管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """课程管理"""
    list_display = ['name', 'term', 'created_by', 'created_at']
    search_fields = ['name']
    list_filter = ['term']


# 维护意图：班级管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    """班级管理"""
    list_display = ['name', 'course', 'teacher', 'semester', 'created_at']
    list_filter = ['course', 'semester']
    search_fields = ['name']


# 维护意图：选课记录管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """选课记录管理"""
    list_display = ['user', 'class_obj', 'role', 'enrolled_at']
    list_filter = ['role']
    search_fields = ['user__username']


# 维护意图：班级公告管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """班级公告管理"""
    list_display = ['title', 'class_obj', 'created_by', 'created_at']
    list_filter = ['class_obj']
    search_fields = ['title', 'content']
