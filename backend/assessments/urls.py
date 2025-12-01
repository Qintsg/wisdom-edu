"""
测评模块 - URL路由配置

初始测评流程：
1. 新用户注册后：完成能力评测和习惯问卷（全局，不绑定课程）
2. 加入新课程后：完成该课程的知识评测
3. 评测完成后：生成该课程的学习者画像

API命名规范：
- /api/student/* - 学生专用接口
- /api/teacher/* - 教师专用接口
- /api/admin/* - 管理员专用接口
"""
from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    # ============ 学生端 ============
    # 评测状态查询
    path('api/student/assessments/status', views.get_assessment_status, name='get_assessment_status'),
    
    # 知识评测（加入课程后进行）
    path('api/student/assessments/initial/knowledge', views.get_knowledge_assessment, name='get_knowledge_assessment'),
    path('api/student/assessments/initial/knowledge/submit', views.submit_knowledge_assessment, name='submit_knowledge_assessment'),
    path('api/student/assessments/initial/knowledge/result', views.get_knowledge_result, name='get_knowledge_result'),
    
    # 能力评测（新用户注册后进行，全局）
    path('api/student/assessments/initial/ability', views.get_ability_assessment, name='get_ability_assessment'),
    path('api/student/assessments/initial/ability/retake', views.retake_ability_assessment, name='retake_ability_assessment'),
    path('api/student/assessments/initial/ability/submit', views.submit_ability_assessment, name='submit_ability_assessment'),
    
    # 习惯问卷（新用户注册后进行，全局）
    path('api/student/assessments/initial/habit', views.get_habit_survey, name='get_habit_survey'),
    path('api/student/assessments/initial/habit/submit', views.submit_habit_survey, name='submit_habit_survey'),
    
    # 画像生成（知识评测完成后）
    path('api/student/assessments/profile/generate', views.generate_course_profile, name='generate_course_profile'),
]
