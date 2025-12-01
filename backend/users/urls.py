"""
用户模块 - URL路由配置
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 健康检查
    path('health/', views.health, name='health'),

    # 认证
    path('api/auth/register', views.register, name='register'),
    path('api/auth/login', views.login, name='login'),
    path('api/auth/logout', views.logout, name='logout'),
    path('api/auth/userinfo', views.userinfo, name='userinfo'),
    path('api/auth/userinfo/update', views.update_userinfo, name='update_userinfo'),
    path('api/auth/token/refresh', views.token_refresh, name='token_refresh'),
    path('api/auth/password/change', views.change_password, name='change_password'),
    path('api/auth/password/reset/send', views.password_reset_send, name='password_reset_send'),
    path('api/auth/password/reset', views.password_reset, name='password_reset'),

    # 画像
    path('api/student/profile', views.get_profile, name='get_profile'),
    path('api/student/profile/habit', views.update_habit_preference, name='update_habit_preference'),
    path('api/student/profile/update', views.update_student_profile, name='update_student_profile'),
    path('api/student/profile/history', views.get_profile_history, name='get_profile_history'),
    path('api/student/profile/compare', views.profile_compare, name='profile_compare'),
    path('api/student/profile/export', views.profile_export, name='profile_export'),
    
    # 激活码管理（管理员）
    path('api/admin/activation-codes', views.list_activation_codes, name='list_activation_codes'),
    path('api/admin/activation-codes/generate', views.generate_activation_code, name='generate_activation_code'),
    path('api/admin/activation-codes/batch-delete', views.activation_code_batch_delete, name='activation_code_batch_delete'),
    path('api/admin/activation-codes/validate', views.activation_code_validate, name='activation_code_validate'),
    path('api/admin/activation-codes/export', views.activation_code_export, name='activation_code_export'),
    path('api/admin/activation-codes/<int:code_id>', views.delete_activation_code, name='activation_code_detail'),
    
    # 用户管理（管理员）
    path('api/admin/users', views.admin_user_list, name='admin_user_list'),
    path('api/admin/users/create', views.admin_user_create, name='admin_user_create'),
    path('api/admin/users/batch-delete', views.admin_user_batch_delete, name='admin_user_batch_delete'),
    path('api/admin/users/import', views.admin_user_import, name='admin_user_import'),
    path('api/admin/users/export', views.admin_user_export, name='admin_user_export'),
    path('api/admin/users/template', views.admin_user_template, name='admin_user_template'),
    path('api/admin/users/<int:user_id>', views.admin_user_detail, name='admin_user_detail'),
    path('api/admin/users/<int:user_id>/update', views.admin_user_update, name='admin_user_update'),
    path('api/admin/users/<int:user_id>/delete', views.admin_user_delete, name='admin_user_delete'),
    path('api/admin/users/<int:user_id>/reset-password', views.admin_user_reset_password, name='admin_user_reset_password'),
    path('api/admin/users/<int:user_id>/disable', views.admin_user_disable, name='admin_user_disable'),
    path('api/admin/users/<int:user_id>/enable', views.admin_user_enable, name='admin_user_enable'),
    
    # 管理员学生画像查看
    path('api/admin/student-profiles', views.admin_get_all_student_profiles, name='admin_student_profiles'),
    path('api/admin/student-profiles/<int:student_id>', views.admin_student_profile_detail, name='admin_student_profile_detail'),
    
    # 教师查看学生画像
    path('api/teacher/students/<int:user_id>/profile', views.get_student_profile_detail, name='student_profile_detail'),
    path('api/teacher/students/<int:user_id>/refresh-profile', views.teacher_refresh_student_profile, name='teacher_refresh_student_profile'),
]
