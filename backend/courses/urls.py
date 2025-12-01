"""
课程模块 - URL路由配置
"""
from django.urls import path
from . import views
from . import teacher_workspace_views

app_name = 'courses'

urlpatterns = [
    # 用户课程
    path('api/courses', views.course_list, name='course_list'),
    path('api/courses/select', views.course_select, name='course_select'),
    path('api/courses/search', views.course_search, name='course_search'),
    
    # 学生班级管理
    path('api/student/classes', views.student_class_list, name='student_class_list'),
    path('api/student/classes/<int:class_id>', views.student_class_detail, name='student_class_detail'),
    path('api/student/classes/join', views.student_join_class, name='student_join_class'),
    path('api/student/classes/<int:class_id>/leave', views.student_leave_class, name='student_leave_class'),
    
    # 教师课程管理
    path('api/teacher/courses/create', views.course_create, name='course_create'),
    path('api/teacher/courses/my', views.my_created_courses, name='my_created_courses'),
    path('api/teacher/courses/<int:course_id>', views.course_update, name='course_update'),
    path('api/teacher/courses/<int:course_id>/workspace', teacher_workspace_views.course_workspace, name='course_workspace'),
    path('api/teacher/courses/<int:course_id>/delete', views.course_delete, name='course_delete'),
    path('api/teacher/courses/<int:course_id>/cover/upload', views.teacher_course_cover_upload, name='teacher_course_cover_upload'),
    path('api/teacher/courses/<int:course_id>/statistics', views.teacher_course_statistics, name='teacher_course_statistics'),
    path('api/teacher/courses/<int:course_id>/settings', views.get_course_settings, name='get_course_settings'),
    path('api/teacher/courses/<int:course_id>/settings/update', views.update_course_settings, name='update_course_settings'),
    
    # 教师班级管理
    path('api/teacher/classes/create', teacher_workspace_views.class_create, name='class_create'),
    path('api/teacher/classes/my', teacher_workspace_views.my_classes, name='my_classes_list'),
    path('api/teacher/classes/<int:class_id>', views.class_update, name='class_update'),
    path('api/teacher/classes/<int:class_id>/delete', views.class_delete, name='class_delete'),
    path('api/teacher/classes/<int:class_id>/progress', views.teacher_class_progress, name='teacher_class_progress'),
    
    # 班级课程发布
    path('api/teacher/classes/<int:class_id>/courses', views.class_courses, name='class_courses'),
    path('api/teacher/classes/<int:class_id>/publish-course', views.class_publish_course, name='class_publish_course'),
    path('api/teacher/classes/<int:class_id>/courses/<int:course_id>', views.class_unpublish_course, name='class_unpublish_course'),
    
    # 班级邀请码管理（教师）
    path('api/teacher/classes/<int:class_id>/invitations', views.list_class_invitations, name='list_class_invitations'),
    path('api/teacher/invitations/generate', views.generate_class_invitation, name='generate_class_invitation'),
    path('api/teacher/invitations/<int:invitation_id>', views.delete_class_invitation, name='delete_class_invitation'),
    
    # 班级学生管理（教师）
    path('api/teacher/classes/<int:class_id>/students', views.class_students, name='class_students'),
    path('api/teacher/classes/<int:class_id>/students/<int:user_id>', views.remove_student_from_class, name='remove_student'),
    path('api/teacher/classes/<int:class_id>/student-profiles', views.get_class_student_profiles, name='class_student_profiles'),
    
    # 班级公告管理（教师）
    path('api/teacher/classes/<int:class_id>/announcements', views.class_announcements, name='class_announcements'),
    path('api/teacher/announcements/<int:announcement_id>', views.announcement_detail, name='announcement_detail'),
    
    # 管理端 - 课程管理
    path('api/admin/courses', views.admin_course_list, name='admin_course_list'),
    path('api/admin/courses/create', views.admin_course_create, name='admin_course_create'),
    path('api/admin/courses/<int:course_id>', views.admin_course_detail, name='admin_course_detail'),
    path('api/admin/courses/<int:course_id>/assign-teacher', views.admin_course_assign_teacher, name='admin_course_assign_teacher'),
    path('api/admin/courses/<int:course_id>/statistics', views.admin_course_statistics, name='admin_course_statistics'),
    
    # 管理端 - 班级管理
    path('api/admin/classes', views.admin_class_list, name='admin_class_list'),
    path('api/admin/classes/create', views.admin_class_create, name='admin_class_create'),
    path('api/admin/classes/<int:class_id>', views.admin_class_detail, name='admin_class_detail'),
    path('api/admin/classes/<int:class_id>/students', views.admin_class_students, name='admin_class_students'),
    path('api/admin/classes/<int:class_id>/students/add', views.admin_class_add_students, name='admin_class_add_students'),
    path('api/admin/classes/<int:class_id>/students/<int:student_id>', views.admin_class_remove_student, name='admin_class_remove_student'),
    path('api/admin/classes/<int:class_id>/assign-teacher', views.admin_class_assign_teacher, name='admin_class_assign_teacher'),
    path('api/admin/classes/<int:class_id>/statistics', views.admin_class_statistics, name='admin_class_statistics'),
    
    # 管理端 - 统计
    path('api/admin/statistics/overview', views.admin_statistics_overview, name='admin_statistics_overview'),
    path('api/admin/statistics/users', views.admin_statistics_users, name='admin_statistics_users'),
    path('api/admin/statistics/courses', views.admin_statistics_courses, name='admin_statistics_courses'),
    path('api/admin/statistics/learning', views.admin_statistics_learning, name='admin_statistics_learning'),
    path('api/admin/statistics/exams', views.admin_statistics_exams, name='admin_statistics_exams'),
    path('api/admin/statistics/active-users', views.admin_statistics_active_users, name='admin_statistics_active_users'),
    path('api/admin/statistics/report', views.admin_statistics_report, name='admin_statistics_report'),
    path('api/admin/statistics/export', views.admin_statistics_export, name='admin_statistics_export'),
]
