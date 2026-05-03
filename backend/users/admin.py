"""
用户模块 - Admin配置
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, HabitPreference, UserCourseContext


# 维护意图：用户管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理"""
    list_display = ['username', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'email']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('role', 'avatar', 'phone')}),
    )


# 维护意图：学习习惯偏好管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(HabitPreference)
class HabitPreferenceAdmin(admin.ModelAdmin):
    """学习习惯偏好管理"""
    list_display = ['user', 'preferred_resource', 'preferred_study_time', 'updated_at']
    list_filter = ['preferred_resource', 'preferred_study_time']
    search_fields = ['user__username']


# 维护意图：用户课程上下文管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(UserCourseContext)
class UserCourseContextAdmin(admin.ModelAdmin):
    """用户课程上下文管理"""
    list_display = ['user', 'current_course', 'current_class', 'updated_at']
    list_filter = ['current_course']
    search_fields = ['user__username']
