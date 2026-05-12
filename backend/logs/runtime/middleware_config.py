"""操作日志中间件静态配置。"""

from __future__ import annotations


EXCLUDE_PATTERNS = [
    r"^/static/",
    r"^/media/",
    r"^/health/",
    r"^/__debug__/",
    r"^/admin/jsi18n/",
    r"^/favicon\.ico",
]


PATH_MODULE_MAP = {
    "/api/auth/": "users",
    "/api/users/": "users",
    "/api/student/profile": "users",
    "/api/admin/activation": "users",
    "/api/teacher/invitations": "users",
    "/api/courses/": "courses",
    "/api/classes/": "courses",
    "/api/my-classes": "courses",
    "/api/teacher/classes/": "courses",
    "/api/teacher/courses/": "courses",
    "/api/knowledge": "knowledge",
    "/api/student/knowledge": "knowledge",
    "/api/teacher/knowledge": "knowledge",
    "/api/teacher/resources": "knowledge",
    "/api/teacher/questions": "exams",
    "/api/exams/": "exams",
    "/api/student/exams/": "exams",
    "/api/student/feedback/": "exams",
    "/api/assessments/": "assessments",
    "/api/learning/": "learning",
    "/api/student/learning-path": "learning",
    "/api/student/path-nodes/": "learning",
    "/api/ai/": "ai_services",
    "/api/student/ai/": "ai_services",
    "/api/logs/": "logs",
    "/api/admin/": "system",
    "/admin/": "system",
}


METHOD_ACTION_MAP = {
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
    "DELETE": "delete",
    "GET": "read",
}
