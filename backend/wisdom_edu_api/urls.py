"""
URL configuration for wisdom_edu_api project.
自适应学习系统 - URL路由配置

API命名规范：
- /api/auth/* - 认证相关（登录、注册、token）
- /api/student/* - 学生专用接口
- /api/teacher/* - 教师专用接口
- /api/admin/* - 管理员专用接口
- /api/courses - 公共课程查询接口
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # 首页和文档页面
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("docs/", TemplateView.as_view(template_name="docs.html"), name="docs"),
    # 管理后台
    path("admin/", admin.site.urls),
    # 各模块API路由
    path("api/common/", include("common.urls")),  # 公共服务（菜单等）
    path("", include("users.urls")),  # 用户认证和画像
    path("", include("courses.urls")),  # 课程管理
    path("", include("knowledge.urls")),  # 知识图谱
    path("", include("assessments.urls")),  # 测评
    path("", include("learning.urls")),  # 学习路径
    path("", include("exams.urls")),  # 考试和反馈
    path("", include("ai_services.urls")),  # AI服务
    path("", include("logs.urls")),  # 操作日志
    # API文档
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# 开发环境下提供媒体文件服务
if settings.DEBUG:
    # 为静态分析提供确定的字符串类型，同时保留缺省 URL 的兜底行为。
    media_url = settings.MEDIA_URL or "/media/"
    static_url = settings.STATIC_URL or "/static/"

    urlpatterns += static(media_url, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(static_url, document_root=settings.STATIC_ROOT)
