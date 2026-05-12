"""
用户模块 - Admin配置
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, HabitPreference, UserCourseContext


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    list_display = ['username', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('role', 'avatar', 'phone')}),
    )


@admin.register(HabitPreference)
class HabitPreferenceAdmin(admin.ModelAdmin):
    """学习习惯偏好管理"""
    list_display = ['user', 'preferred_resource', 'preferred_study_time', 'updated_at']
    list_filter = ['preferred_resource', 'preferred_study_time']
    search_fields = ['user__username']


@admin.register(UserCourseContext)
class UserCourseContextAdmin(admin.ModelAdmin):
    """用户课程上下文管理"""
    list_display = ['user', 'current_course', 'current_class', 'updated_at']
    list_filter = ['current_course']
    search_fields = ['user__username']
