"""
学习路径模块 - Admin配置
"""
from django.contrib import admin
from .models import LearningPath, PathNode, NodeProgress


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    """学习路径管理"""
    list_display = ['user', 'course', 'is_dynamic', 'generated_at']
    list_filter = ['course', 'is_dynamic']
    search_fields = ['user__username']


@admin.register(PathNode)
class PathNodeAdmin(admin.ModelAdmin):
    """路径节点管理"""
    list_display = ['title', 'path', 'status', 'order_index']
    list_filter = ['status']
    search_fields = ['title']


@admin.register(NodeProgress)
class NodeProgressAdmin(admin.ModelAdmin):
    """节点进度管理"""
    list_display = ['user', 'node', 'updated_at']
    search_fields = ['user__username']
