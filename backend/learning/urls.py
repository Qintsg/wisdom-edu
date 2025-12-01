"""
学习路径模块 - URL路由配置

API命名规范：
- /api/student/* - 学生专用接口
- /api/path-nodes/* - 学习路径节点相关（兼容旧路由）
"""
from django.urls import path
from . import views
from . import student_rag_views

app_name = 'learning'

urlpatterns = [
    # ============ 学生端 ============
    path('api/student/learning-path', views.get_learning_path, name='get_learning_path'),
    path('api/student/learning-path/adjust', views.adjust_learning_path, name='adjust_learning_path'),
    path('api/student/learning-progress', views.get_learning_progress, name='get_learning_progress'),
    path('api/student/path-nodes/<int:node_id>', views.get_path_node_detail, name='get_path_node_detail'),
    path('api/student/path-nodes/<int:node_id>/start', views.start_learning_node, name='start_learning_node'),
    path('api/student/path-nodes/<int:node_id>/complete', views.complete_path_node, name='complete_path_node'),
    path('api/student/path-nodes/<int:node_id>/skip', views.skip_path_node, name='skip_path_node'),
    path('api/student/path-nodes/<int:node_id>/resources', views.get_node_resources, name='get_node_resources'),
    path('api/student/path-nodes/<int:node_id>/ai-resources', student_rag_views.get_ai_resources, name='get_ai_resources'),
    path('api/student/path-nodes/<int:node_id>/resources/<str:resource_id>/complete', views.complete_node_resource, name='complete_node_resource'),
    path('api/student/path-nodes/<int:node_id>/resources/<str:resource_id>/pause', views.pause_node_resource, name='pause_node_resource'),
    path('api/student/path-nodes/<int:node_id>/exams', views.get_node_exams, name='get_node_exams'),
    path('api/student/path-nodes/<int:node_id>/exams/<int:exam_id>/submit', views.submit_node_exam, name='submit_node_exam'),
    # 阶段测试（内嵌做题）
    path('api/student/path-nodes/<int:node_id>/stage-test', views.get_stage_test, name='get_stage_test'),
    path('api/student/path-nodes/<int:node_id>/stage-test/submit', views.submit_stage_test, name='submit_stage_test'),

    # Dashboard
    path('api/student/dashboard', views.student_dashboard, name='student_dashboard'),
]
