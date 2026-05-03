"""通用接口视图。"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from common.responses import success_response


# 维护意图：根据用户角色获取动态菜单 GET /api/common/menu 返回: {menu: [...], role: 'student'|'teacher'|'admin'}
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_menu(request):
    """
    根据用户角色获取动态菜单
    GET /api/common/menu
    返回: {menu: [...], role: 'student'|'teacher'|'admin'}
    """
    user = request.user
    role = "student"

    # 先显式收窄动态认证用户属性，避免静态分析把 request.user 视为不完整基类。
    is_superuser = bool(getattr(user, "is_superuser", False))
    user_role = getattr(user, "role", None)

    if is_superuser:
        role = "admin"
    elif user_role is not None:
        role = str(user_role)

    menu = []

    if role == "student":
        menu = [
            {"index": "/student/dashboard", "title": "学习仪表盘", "icon": "Odometer"},
            {"index": "/student/learning-path", "title": "学习路径", "icon": "Guide"},
            {
                "index": "/student/ai-assistant",
                "title": "AI助手",
                "icon": "ChatDotRound",
            },
            {
                "index": "/student/knowledge-map",
                "title": "知识图谱",
                "icon": "Connection",
            },
            {"index": "/student/resources", "title": "课程资源", "icon": "Collection"},
            {
                "index": "assessment-group",
                "title": "在线测评",
                "icon": "EditPen",
                "children": [
                    {
                        "index": "/student/exams",
                        "title": "在线作业",
                        "icon": "Document",
                    },
                    {
                        "index": "/student/assessment",
                        "title": "初始评测",
                        "icon": "DataAnalysis",
                    },
                ],
            },
            {"index": "/student/profile", "title": "学习画像", "icon": "Avatar"},
            {"index": "/student/settings", "title": "个人设置", "icon": "Setting"},
        ]
    elif role == "teacher":
        menu = [
            {"index": "/teacher/dashboard", "title": "教学概览", "icon": "DataBoard"},
            {"index": "/teacher/courses", "title": "课程管理", "icon": "Reading"},
            {"index": "/teacher/classes", "title": "班级管理", "icon": "UserFilled"},
            {
                "index": "/teacher/knowledge",
                "title": "知识图谱管理",
                "icon": "Connection",
            },
            {
                "index": "/teacher/resources",
                "title": "资源管理",
                "icon": "FolderOpened",
            },
            {"index": "/teacher/questions", "title": "题库管理", "icon": "Notebook"},
            {"index": "/teacher/exams", "title": "作业管理", "icon": "DocumentCopy"},
            {"index": "/teacher/settings", "title": "个人设置", "icon": "Setting"},
        ]
    elif role == "admin":
        menu = [
            {"index": "/admin/dashboard", "title": "管理概览", "icon": "DataBoard"},
            {"index": "/admin/users", "title": "用户管理", "icon": "User"},
            {"index": "/admin/courses", "title": "课程管理", "icon": "Reading"},
            {"index": "/admin/classes", "title": "班级管理", "icon": "UserFilled"},
            {"index": "/admin/activation-codes", "title": "激活码管理", "icon": "Key"},
            {"index": "/admin/logs", "title": "系统日志", "icon": "Tickets"},
            {"index": "/admin/settings", "title": "系统设置", "icon": "Setting"},
        ]

    return success_response(data={"menu": menu, "role": role})
