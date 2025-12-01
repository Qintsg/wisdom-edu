"""
考试模块 - URL路由配置

API命名规范：
- /api/student/* - 学生专用接口（如考试提交）
- /api/teacher/* - 教师专用接口（如考试管理）
"""
from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    # ============ 学生端 ============
    # 考试列表和详情
    path('api/student/exams', views.exam_list, name='exam_list'),
    path('api/student/exams/<int:exam_id>', views.exam_detail, name='exam_detail'),
    path('api/student/exams/<int:exam_id>/submit', views.exam_submit, name='exam_submit'),
    path('api/student/exams/<int:exam_id>/result', views.exam_result, name='exam_result'),
    path('api/student/exams/<int:exam_id>/draft', views.exam_save_draft, name='exam_save_draft'),
    path('api/student/exams/<int:exam_id>/statistics', views.exam_statistics, name='exam_statistics'),
    path('api/student/exams/<int:exam_id>/answer-sheet', views.exam_answer_sheet, name='exam_answer_sheet'),
    path('api/student/exams/<int:exam_id>/retake', views.exam_retake, name='exam_retake'),
    path('api/student/exams/<int:exam_id>/download', views.exam_download, name='exam_download'),
    
    # 班级相关
    path('api/student/classes/<int:class_id>/members', views.student_class_members, name='student_class_members'),
    path('api/student/classes/<int:class_id>/ranking', views.student_class_ranking, name='student_class_ranking'),
    path('api/student/classes/<int:class_id>/notifications', views.student_class_notifications, name='student_class_notifications'),
    path('api/student/classes/<int:class_id>/assignments', views.student_class_assignments, name='student_class_assignments'),
    
    # 反馈报告
    path('api/student/feedback/generate', views.generate_feedback_report, name='generate_feedback_report'),
    path('api/student/feedback/<int:exam_id>', views.get_feedback_report, name='get_feedback_report'),
    
    # 初始评测
    path('api/student/assessments/initial/start', views.initial_assessment_start, name='initial_assessment_start'),
    path('api/student/assessments/initial/submit', views.initial_assessment_submit, name='initial_assessment_submit'),
    
    # ============ 教师端 ============
    # 考试管理
    path('api/teacher/exams', views.exam_manage_list, name='teacher_exam_list'),
    path('api/teacher/exams/create', views.exam_create, name='teacher_exam_create'),
    path('api/teacher/exams/<int:exam_id>', views.exam_teacher_detail, name='teacher_exam_detail'),
    path('api/teacher/exams/<int:exam_id>/update', views.exam_update, name='teacher_exam_update'),
    path('api/teacher/exams/<int:exam_id>/delete', views.exam_delete, name='teacher_exam_delete'),
    path('api/teacher/exams/<int:exam_id>/publish', views.exam_publish, name='teacher_exam_publish'),
    path('api/teacher/exams/<int:exam_id>/unpublish', views.exam_unpublish, name='teacher_exam_unpublish'),
    path('api/teacher/exams/<int:exam_id>/results', views.exam_results, name='teacher_exam_results'),
    path('api/teacher/exams/<int:exam_id>/export', views.teacher_exam_export, name='teacher_exam_export'),
    path('api/teacher/exams/<int:exam_id>/questions/add', views.teacher_exam_add_questions, name='teacher_exam_add_questions'),
    path('api/teacher/exams/<int:exam_id>/questions/remove', views.teacher_exam_remove_questions, name='teacher_exam_remove_questions'),
    path('api/teacher/exams/<int:exam_id>/students/<int:student_id>', views.exam_student_detail, name='teacher_exam_student'),
    path('api/teacher/exams/<int:exam_id>/analysis', views.exam_analysis, name='teacher_exam_analysis'),
]
