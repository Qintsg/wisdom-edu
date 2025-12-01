"""
用户模块视图 - 兼容层

视图已按角色拆分为:
- auth_views: 认证、JWT、密码管理、用户信息、健康检查
- student_views: 学生画像查看、更新、历史、对比、导出
- teacher_views: 教师查看/刷新学生画像
- admin_views: 用户CRUD、激活码管理、学生画像管理
"""
from .auth_views import *  # noqa: F401,F403
from .student_views import *  # noqa: F401,F403
from .teacher_views import *  # noqa: F401,F403
from .admin_views import *  # noqa: F401,F403
