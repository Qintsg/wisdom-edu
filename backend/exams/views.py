"""
考试模块视图 - 兼容层

视图已按角色拆分为:
- student_views: 考试列表/提交/成绩、反馈报告、初始评测
- teacher_views: 考试管理、试题管理、成绩分析
"""
from .student_views import *  # noqa: F401,F403
from .teacher_views import *  # noqa: F401,F403
