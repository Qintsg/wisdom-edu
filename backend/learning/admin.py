"""
学习路径模块 - Admin配置
"""
from django.contrib import admin
from .models import LearningPath, PathNode, NodeProgress


# 维护意图：学习路径管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    """学习路径管理"""
    list_display = ['user', 'course', 'is_dynamic', 'generated_at']
    list_filter = ['course', 'is_dynamic']
    search_fields = ['user__username']


# 维护意图：路径节点管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(PathNode)
class PathNodeAdmin(admin.ModelAdmin):
    """路径节点管理"""
    list_display = ['title', 'path', 'status', 'order_index']
    list_filter = ['status']
    search_fields = ['title']


# 维护意图：节点进度管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(NodeProgress)
class NodeProgressAdmin(admin.ModelAdmin):
    """节点进度管理"""
    list_display = ['user', 'node', 'updated_at']
    search_fields = ['user__username']
