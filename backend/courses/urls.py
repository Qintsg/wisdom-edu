"""
课程模块 - URL路由配置
"""
from django.urls import path
from courses.api import (
    admin as admin_views,
    admin_course_class_stats as admin_course_class_stats_views,
    admin_statistics as admin_statistics_views,
    student as student_views,
)
from courses.api.teacher import (
    announcement as teacher_announcement_views,
    classroom as teacher_classroom_views,
    course as teacher_course_views,
    invitation as teacher_invitation_views,
    student as teacher_student_views,
)
from courses.api.teacher import workspace as teacher_workspace_views

app_name = 'courses'

urlpatterns = [
    # 用户课程
    path('api/courses', student_views.course_list, name='course_list'),
    path('api/courses/select', student_views.course_select, name='course_select'),
    path('api/courses/search', teacher_course_views.course_search, name='course_search'),
    
    # 学生班级管理
    path('api/student/classes', student_views.student_class_list, name='student_class_list'),
    path('api/student/classes/<int:class_id>', student_views.student_class_detail, name='student_class_detail'),
    path('api/student/classes/join', student_views.student_join_class, name='student_join_class'),
    path('api/student/classes/<int:class_id>/leave', student_views.student_leave_class, name='student_leave_class'),
    
    # 教师课程管理
    path('api/teacher/courses/create', teacher_course_views.course_create, name='course_create'),
    path('api/teacher/courses/my', teacher_course_views.my_created_courses, name='my_created_courses'),
    path('api/teacher/courses/<int:course_id>', teacher_course_views.course_update, name='course_update'),
    path('api/teacher/courses/<int:course_id>/workspace', teacher_workspace_views.course_workspace, name='course_workspace'),
    path('api/teacher/courses/<int:course_id>/delete', teacher_course_views.course_delete, name='course_delete'),
    path('api/teacher/courses/<int:course_id>/cover/upload', teacher_course_views.teacher_course_cover_upload, name='teacher_course_cover_upload'),
    path('api/teacher/courses/<int:course_id>/statistics', teacher_course_views.teacher_course_statistics, name='teacher_course_statistics'),
    path('api/teacher/courses/<int:course_id>/settings', teacher_course_views.get_course_settings, name='get_course_settings'),
    path('api/teacher/courses/<int:course_id>/settings/update', teacher_course_views.update_course_settings, name='update_course_settings'),
    
    # 教师班级管理
    path('api/teacher/classes/create', teacher_workspace_views.class_create, name='class_create'),
    path('api/teacher/classes/my', teacher_workspace_views.my_classes, name='my_classes_list'),
    path('api/teacher/classes/<int:class_id>', teacher_classroom_views.class_update, name='class_update'),
    path('api/teacher/classes/<int:class_id>/delete', teacher_classroom_views.class_delete, name='class_delete'),
    path('api/teacher/classes/<int:class_id>/progress', teacher_classroom_views.teacher_class_progress, name='teacher_class_progress'),
    
    # 班级课程发布
    path('api/teacher/classes/<int:class_id>/courses', teacher_classroom_views.class_courses, name='class_courses'),
    path('api/teacher/classes/<int:class_id>/publish-course', teacher_classroom_views.class_publish_course, name='class_publish_course'),
    path('api/teacher/classes/<int:class_id>/courses/<int:course_id>', teacher_classroom_views.class_unpublish_course, name='class_unpublish_course'),
    
    # 班级邀请码管理（教师）
    path('api/teacher/classes/<int:class_id>/invitations', teacher_invitation_views.list_class_invitations, name='list_class_invitations'),
    path('api/teacher/invitations/generate', teacher_invitation_views.generate_class_invitation, name='generate_class_invitation'),
    path('api/teacher/invitations/<int:invitation_id>', teacher_invitation_views.delete_class_invitation, name='delete_class_invitation'),
    
    # 班级学生管理（教师）
    path('api/teacher/classes/<int:class_id>/students', teacher_student_views.class_students, name='class_students'),
    path('api/teacher/classes/<int:class_id>/students/<int:user_id>', teacher_student_views.remove_student_from_class, name='remove_student'),
    path('api/teacher/classes/<int:class_id>/student-profiles', teacher_student_views.get_class_student_profiles, name='class_student_profiles'),
    
    # 班级公告管理（教师）
    path('api/teacher/classes/<int:class_id>/announcements', teacher_announcement_views.class_announcements, name='class_announcements'),
    path('api/teacher/announcements/<int:announcement_id>', teacher_announcement_views.announcement_detail, name='announcement_detail'),
    
    # 管理端 - 课程管理
    path('api/admin/courses', admin_views.admin_course_list, name='admin_course_list'),
    path('api/admin/courses/create', admin_views.admin_course_create, name='admin_course_create'),
    path('api/admin/courses/<int:course_id>', admin_views.admin_course_detail, name='admin_course_detail'),
    path('api/admin/courses/<int:course_id>/assign-teacher', admin_views.admin_course_assign_teacher, name='admin_course_assign_teacher'),
    path('api/admin/courses/<int:course_id>/statistics', admin_course_class_stats_views.admin_course_statistics, name='admin_course_statistics'),
    
    # 管理端 - 班级管理
    path('api/admin/classes', admin_views.admin_class_list, name='admin_class_list'),
    path('api/admin/classes/create', admin_views.admin_class_create, name='admin_class_create'),
    path('api/admin/classes/<int:class_id>', admin_views.admin_class_detail, name='admin_class_detail'),
    path('api/admin/classes/<int:class_id>/students', admin_views.admin_class_students, name='admin_class_students'),
    path('api/admin/classes/<int:class_id>/students/add', admin_views.admin_class_add_students, name='admin_class_add_students'),
    path('api/admin/classes/<int:class_id>/students/<int:student_id>', admin_views.admin_class_remove_student, name='admin_class_remove_student'),
    path('api/admin/classes/<int:class_id>/assign-teacher', admin_views.admin_class_assign_teacher, name='admin_class_assign_teacher'),
    path('api/admin/classes/<int:class_id>/statistics', admin_course_class_stats_views.admin_class_statistics, name='admin_class_statistics'),
    
    # 管理端 - 统计
    path('api/admin/statistics/overview', admin_statistics_views.admin_statistics_overview, name='admin_statistics_overview'),
    path('api/admin/statistics/users', admin_statistics_views.admin_statistics_users, name='admin_statistics_users'),
    path('api/admin/statistics/courses', admin_statistics_views.admin_statistics_courses, name='admin_statistics_courses'),
    path('api/admin/statistics/learning', admin_statistics_views.admin_statistics_learning, name='admin_statistics_learning'),
    path('api/admin/statistics/exams', admin_statistics_views.admin_statistics_exams, name='admin_statistics_exams'),
    path('api/admin/statistics/active-users', admin_statistics_views.admin_statistics_active_users, name='admin_statistics_active_users'),
    path('api/admin/statistics/report', admin_statistics_views.admin_statistics_report, name='admin_statistics_report'),
    path('api/admin/statistics/export', admin_statistics_views.admin_statistics_export, name='admin_statistics_export'),
]
