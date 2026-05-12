"""
学习路径模块 - URL路由配置

API命名规范：
- /api/student/* - 学生专用接口
- /api/path-nodes/* - 学习路径节点相关（兼容旧路由）
"""
from django.urls import path
from learning.api import dashboard as dashboard_views
from learning.api import paths as path_views
from learning.api.nodes import detail as node_detail_views
from learning.api.nodes import progress as node_progress_views
from learning.api.rag import views as student_rag_views
from learning.stage_test import get_views as stage_test_get_views
from learning.stage_test import submit_views as stage_test_submit_views

app_name = 'learning'

urlpatterns = [
    # ============ 学生端 ============
    path('api/student/learning-path', path_views.get_learning_path, name='get_learning_path'),
    path('api/student/learning-path/adjust', path_views.adjust_learning_path, name='adjust_learning_path'),
    path('api/student/learning-progress', node_progress_views.get_learning_progress, name='get_learning_progress'),
    path('api/student/path-nodes/<int:node_id>', node_detail_views.get_path_node_detail, name='get_path_node_detail'),
    path('api/student/path-nodes/<int:node_id>/start', node_progress_views.start_learning_node, name='start_learning_node'),
    path('api/student/path-nodes/<int:node_id>/complete', node_progress_views.complete_path_node, name='complete_path_node'),
    path('api/student/path-nodes/<int:node_id>/skip', node_progress_views.skip_path_node, name='skip_path_node'),
    path('api/student/path-nodes/<int:node_id>/resources', node_progress_views.get_node_resources, name='get_node_resources'),
    path('api/student/path-nodes/<int:node_id>/ai-resources', student_rag_views.get_ai_resources, name='get_ai_resources'),
    path('api/student/path-nodes/<int:node_id>/resources/<str:resource_id>/complete', node_detail_views.complete_node_resource, name='complete_node_resource'),
    path('api/student/path-nodes/<int:node_id>/resources/<str:resource_id>/pause', node_progress_views.pause_node_resource, name='pause_node_resource'),
    path('api/student/path-nodes/<int:node_id>/exams', node_progress_views.get_node_exams, name='get_node_exams'),
    path('api/student/path-nodes/<int:node_id>/exams/<int:exam_id>/submit', node_detail_views.submit_node_exam, name='submit_node_exam'),
    # 阶段测试（内嵌做题）
    path('api/student/path-nodes/<int:node_id>/stage-test', stage_test_get_views.get_stage_test, name='get_stage_test'),
    path('api/student/path-nodes/<int:node_id>/stage-test/submit', stage_test_submit_views.submit_stage_test, name='submit_stage_test'),

    # Dashboard
    path('api/student/dashboard', dashboard_views.student_dashboard, name='student_dashboard'),
]
