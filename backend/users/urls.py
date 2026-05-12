"""
用户模块 - URL路由配置
"""
from django.urls import path
from users.api.admin import activation as activation_views
from users.api.admin import profile as admin_profile_views
from users.api.admin import user_management as user_management_views
from users.api.auth import password as password_views
from users.api.auth import views as auth_views
from users.api import student as student_views
from users.api import teacher as teacher_views

app_name = 'users'

urlpatterns = [
    # 健康检查
    path('health/', auth_views.health, name='health'),

    # 认证
    path('api/auth/register', auth_views.register, name='register'),
    path('api/auth/login', auth_views.login, name='login'),
    path('api/auth/logout', auth_views.logout, name='logout'),
    path('api/auth/userinfo', auth_views.userinfo, name='userinfo'),
    path('api/auth/userinfo/update', auth_views.update_userinfo, name='update_userinfo'),
    path('api/auth/token/refresh', auth_views.token_refresh, name='token_refresh'),
    path('api/auth/password/change', auth_views.change_password, name='change_password'),
    path('api/auth/password/reset/send', password_views.password_reset_send, name='password_reset_send'),
    path('api/auth/password/reset', password_views.password_reset, name='password_reset'),

    # 画像
    path('api/student/profile', student_views.get_profile, name='get_profile'),
    path('api/student/profile/habit', student_views.update_habit_preference, name='update_habit_preference'),
    path('api/student/profile/update', student_views.update_student_profile, name='update_student_profile'),
    path('api/student/profile/history', student_views.get_profile_history, name='get_profile_history'),
    path('api/student/profile/compare', student_views.profile_compare, name='profile_compare'),
    path('api/student/profile/export', student_views.profile_export, name='profile_export'),
    
    # 激活码管理（管理员）
    path('api/admin/activation-codes', activation_views.list_activation_codes, name='list_activation_codes'),
    path('api/admin/activation-codes/generate', activation_views.generate_activation_code, name='generate_activation_code'),
    path('api/admin/activation-codes/batch-delete', activation_views.activation_code_batch_delete, name='activation_code_batch_delete'),
    path('api/admin/activation-codes/validate', activation_views.activation_code_validate, name='activation_code_validate'),
    path('api/admin/activation-codes/export', activation_views.activation_code_export, name='activation_code_export'),
    path('api/admin/activation-codes/<int:code_id>', activation_views.delete_activation_code, name='activation_code_detail'),
    
    # 用户管理（管理员）
    path('api/admin/users', user_management_views.admin_user_list, name='admin_user_list'),
    path('api/admin/users/create', user_management_views.admin_user_create, name='admin_user_create'),
    path('api/admin/users/batch-delete', user_management_views.admin_user_batch_delete, name='admin_user_batch_delete'),
    path('api/admin/users/import', user_management_views.admin_user_import, name='admin_user_import'),
    path('api/admin/users/export', user_management_views.admin_user_export, name='admin_user_export'),
    path('api/admin/users/template', user_management_views.admin_user_template, name='admin_user_template'),
    path('api/admin/users/<int:user_id>', user_management_views.admin_user_detail, name='admin_user_detail'),
    path('api/admin/users/<int:user_id>/update', user_management_views.admin_user_update, name='admin_user_update'),
    path('api/admin/users/<int:user_id>/delete', user_management_views.admin_user_delete, name='admin_user_delete'),
    path('api/admin/users/<int:user_id>/reset-password', user_management_views.admin_user_reset_password, name='admin_user_reset_password'),
    path('api/admin/users/<int:user_id>/disable', user_management_views.admin_user_disable, name='admin_user_disable'),
    path('api/admin/users/<int:user_id>/enable', user_management_views.admin_user_enable, name='admin_user_enable'),
    
    # 管理员学生画像查看
    path('api/admin/student-profiles', admin_profile_views.admin_get_all_student_profiles, name='admin_student_profiles'),
    path('api/admin/student-profiles/<int:student_id>', admin_profile_views.admin_student_profile_detail, name='admin_student_profile_detail'),
    
    # 教师查看学生画像
    path('api/teacher/students/<int:user_id>/profile', teacher_views.get_student_profile_detail, name='student_profile_detail'),
    path('api/teacher/students/<int:user_id>/refresh-profile', teacher_views.teacher_refresh_student_profile, name='teacher_refresh_student_profile'),
]
