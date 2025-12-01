"""
课程模块视图 - 兼容层

视图已按角色拆分为:
- student_views: 课程列表、选课、班级管理
- teacher_views: 课程CRUD、班级管理、邀请码、课程设置
- admin_views: 课程/班级管理、统计报表
"""
from .student_views import *  # noqa: F401,F403
from .teacher_views import *  # noqa: F401,F403
from .admin_views import *  # noqa: F401,F403
