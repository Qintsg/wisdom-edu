"""
课程模块 - Admin配置
"""
from django.contrib import admin
from .models import Course, Class, Enrollment, Announcement


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """课程管理"""
    list_display = ['name', 'term', 'created_by', 'created_at']
    search_fields = ['name']
    list_filter = ['term']


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    """班级管理"""
    list_display = ['name', 'course', 'teacher', 'semester', 'created_at']
    list_filter = ['course', 'semester']
    search_fields = ['name']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """选课记录管理"""
    list_display = ['user', 'class_obj', 'role', 'enrolled_at']
    list_filter = ['role']
    search_fields = ['user__username']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """班级公告管理"""
    list_display = ['title', 'class_obj', 'created_by', 'created_at']
    list_filter = ['class_obj']
    search_fields = ['title', 'content']
