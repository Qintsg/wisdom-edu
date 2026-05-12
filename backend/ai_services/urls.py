"""
AI服务模块 - URL路由配置

API命名规范：
- /api/student/* - 学生专用接口（AI分析服务）
- /api/ai/* - 通用AI服务接口
"""

from django.urls import path

from ai_services.api.kt import (
    kt_batch_predict,
    kt_model_info,
    kt_predict,
    kt_recommendations,
)
from ai_services.api.student.chat import (
    ai_chat,
    ai_graph_rag_ask,
    ai_graph_rag_search,
    ai_knowledge_graph_query,
)
from ai_services.api.student.profile import (
    ai_analysis_compare,
    ai_feedback_report,
    ai_key_points_reminder,
    ai_learning_advice,
    ai_profile_analysis,
    ai_refresh_learning_path,
    ai_refresh_profile,
    ai_resource_reason,
    ai_time_scheduling,
)
from ai_services.api.student.rag import ai_node_intro, ai_path_planning

app_name = "ai"

urlpatterns = [
    # ============ 学生端AI服务 ============
    path(
        "api/student/ai/profile-analysis",
        ai_profile_analysis,
        name="ai_profile_analysis",
    ),
    path(
        "api/student/ai/path-planning",
        ai_path_planning,
        name="ai_path_planning",
    ),
    path(
        "api/student/ai/resource-reason",
        ai_resource_reason,
        name="ai_resource_reason",
    ),
    path(
        "api/student/ai/feedback-report",
        ai_feedback_report,
        name="ai_feedback_report",
    ),
    path(
        "api/student/ai/learning-advice",
        ai_learning_advice,
        name="ai_learning_advice",
    ),
    # ============ 主动刷新服务 ============
    path(
        "api/student/ai/refresh-profile",
        ai_refresh_profile,
        name="ai_refresh_profile",
    ),
    path(
        "api/student/ai/refresh-learning-path",
        ai_refresh_learning_path,
        name="ai_refresh_learning_path",
    ),
    path(
        "api/student/ai/key-points-reminder",
        ai_key_points_reminder,
        name="ai_key_points_reminder",
    ),
    path(
        "api/student/ai/time-scheduling",
        ai_time_scheduling,
        name="ai_time_scheduling",
    ),
    path(
        "api/student/ai/analysis-compare",
        ai_analysis_compare,
        name="ai_analysis_compare",
    ),
    # ============ AI对话与知识点介绍 ============
    path("api/student/ai/chat", ai_chat, name="ai_chat"),
    path(
        "api/student/ai/node-intro",
        ai_node_intro,
        name="ai_node_intro",
    ),
    path(
        "api/student/ai/knowledge-query",
        ai_knowledge_graph_query,
        name="ai_knowledge_graph_query",
    ),
    path(
        "api/student/ai/graph-rag/search",
        ai_graph_rag_search,
        name="ai_graph_rag_search",
    ),
    path(
        "api/student/ai/graph-rag/ask",
        ai_graph_rag_ask,
        name="ai_graph_rag_ask",
    ),
    # ============ 知识追踪服务 ============
    path("api/ai/kt/predict", kt_predict, name="kt_predict"),
    path("api/ai/kt/model-info", kt_model_info, name="kt_model_info"),
    path("api/ai/kt/batch-predict", kt_batch_predict, name="kt_batch_predict"),
    path(
        "api/ai/kt/recommendations",
        kt_recommendations,
        name="kt_recommendations",
    ),
]
