"""
课程模块视图 - 兼容层

视图已按角色拆分为:
- student_views: 课程列表、选课、班级管理
- teacher_views: 课程CRUD、班级管理、邀请码、课程设置
- admin_views: 课程/班级管理、统计报表
"""
from courses.api.student import *  # noqa: F401,F403
from courses.api.teacher import *  # noqa: F401,F403
from courses.api.admin import *  # noqa: F401,F403
from courses.api.admin_statistics import *  # noqa: F401,F403
