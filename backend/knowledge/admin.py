"""
知识图谱模块 - Admin配置
"""
from django.contrib import admin
from .models import KnowledgePoint, KnowledgeRelation, Resource, KnowledgeMastery, ProfileSummary


# 维护意图：知识点管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    """知识点管理"""
    list_display = ['name', 'course', 'chapter', 'order', 'is_published']
    list_filter = ['course', 'is_published']
    search_fields = ['name']


# 维护意图：知识点关系管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(KnowledgeRelation)
class KnowledgeRelationAdmin(admin.ModelAdmin):
    """知识点关系管理"""
    list_display = ['pre_point', 'post_point', 'relation_type']
    list_filter = ['relation_type', 'course']


# 维护意图：学习资源管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """学习资源管理"""
    list_display = ['title', 'course', 'resource_type', 'is_visible', 'created_at']
    list_filter = ['resource_type', 'is_visible', 'course']
    search_fields = ['title']


# 维护意图：知识掌握度管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(KnowledgeMastery)
class KnowledgeMasteryAdmin(admin.ModelAdmin):
    """知识掌握度管理"""
    list_display = ['user', 'knowledge_point', 'mastery_rate', 'updated_at']
    list_filter = ['course']
    search_fields = ['user__username', 'knowledge_point__name']


# 维护意图：画像摘要管理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@admin.register(ProfileSummary)
class ProfileSummaryAdmin(admin.ModelAdmin):
    """画像摘要管理"""
    list_display = ['user', 'course', 'generated_at']
    list_filter = ['course']
    search_fields = ['user__username']
