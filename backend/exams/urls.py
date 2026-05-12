"""
考试模块 - URL路由配置

API命名规范：
- /api/student/* - 学生专用接口（如考试提交）
- /api/teacher/* - 教师专用接口（如考试管理）
"""
from django.urls import path
from exams.api.student import artifact as student_artifact_views
from exams.api.student import classroom as student_classroom_views
from exams.api.student import exam as student_exam_views
from exams.api.student import feedback as student_feedback_views
from exams.api.student import initial_assessment as initial_assessment_views
from exams.api.student import submission as student_submission_views
from exams.api.teacher import exam_management as teacher_exam_views
from exams.api.teacher import question as teacher_question_views
from exams.api.teacher import result as teacher_result_views

app_name = 'exams'

urlpatterns = [
    # ============ 学生端 ============
    # 考试列表和详情
    path('api/student/exams', student_exam_views.exam_list, name='exam_list'),
    path('api/student/exams/<int:exam_id>', student_exam_views.exam_detail, name='exam_detail'),
    path('api/student/exams/<int:exam_id>/submit', student_submission_views.exam_submit, name='exam_submit'),
    path('api/student/exams/<int:exam_id>/result', student_submission_views.exam_result, name='exam_result'),
    path('api/student/exams/<int:exam_id>/draft', student_submission_views.exam_save_draft, name='exam_save_draft'),
    path('api/student/exams/<int:exam_id>/statistics', student_submission_views.exam_statistics, name='exam_statistics'),
    path('api/student/exams/<int:exam_id>/answer-sheet', student_artifact_views.exam_answer_sheet, name='exam_answer_sheet'),
    path('api/student/exams/<int:exam_id>/retake', student_artifact_views.exam_retake, name='exam_retake'),
    path('api/student/exams/<int:exam_id>/download', student_artifact_views.exam_download, name='exam_download'),
    
    # 班级相关
    path('api/student/classes/<int:class_id>/members', student_classroom_views.student_class_members, name='student_class_members'),
    path('api/student/classes/<int:class_id>/ranking', student_classroom_views.student_class_ranking, name='student_class_ranking'),
    path('api/student/classes/<int:class_id>/notifications', student_classroom_views.student_class_notifications, name='student_class_notifications'),
    path('api/student/classes/<int:class_id>/assignments', student_classroom_views.student_class_assignments, name='student_class_assignments'),
    
    # 反馈报告
    path('api/student/feedback/generate', student_feedback_views.generate_feedback_report, name='generate_feedback_report'),
    path('api/student/feedback/<int:exam_id>', student_feedback_views.get_feedback_report, name='get_feedback_report'),
    
    # 初始评测
    path('api/student/assessments/initial/start', initial_assessment_views.initial_assessment_start, name='initial_assessment_start'),
    path('api/student/assessments/initial/submit', initial_assessment_views.initial_assessment_submit, name='initial_assessment_submit'),
    
    # ============ 教师端 ============
    # 考试管理
    path('api/teacher/exams', teacher_exam_views.exam_manage_list, name='teacher_exam_list'),
    path('api/teacher/exams/create', teacher_exam_views.exam_create, name='teacher_exam_create'),
    path('api/teacher/exams/<int:exam_id>', teacher_exam_views.exam_teacher_detail, name='teacher_exam_detail'),
    path('api/teacher/exams/<int:exam_id>/update', teacher_exam_views.exam_update, name='teacher_exam_update'),
    path('api/teacher/exams/<int:exam_id>/delete', teacher_exam_views.exam_delete, name='teacher_exam_delete'),
    path('api/teacher/exams/<int:exam_id>/publish', teacher_exam_views.exam_publish, name='teacher_exam_publish'),
    path('api/teacher/exams/<int:exam_id>/unpublish', teacher_exam_views.exam_unpublish, name='teacher_exam_unpublish'),
    path('api/teacher/exams/<int:exam_id>/results', teacher_result_views.exam_results, name='teacher_exam_results'),
    path('api/teacher/exams/<int:exam_id>/export', teacher_result_views.teacher_exam_export, name='teacher_exam_export'),
    path('api/teacher/exams/<int:exam_id>/questions/add', teacher_exam_views.teacher_exam_add_questions, name='teacher_exam_add_questions'),
    path('api/teacher/exams/<int:exam_id>/questions/remove', teacher_exam_views.teacher_exam_remove_questions, name='teacher_exam_remove_questions'),
    path('api/teacher/exams/<int:exam_id>/students/<int:student_id>', teacher_result_views.exam_student_detail, name='teacher_exam_student'),
    path('api/teacher/exams/<int:exam_id>/analysis', teacher_result_views.exam_analysis, name='teacher_exam_analysis'),
]
