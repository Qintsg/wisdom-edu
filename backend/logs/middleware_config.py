"""操作日志中间件静态配置。"""

from __future__ import annotations


# 维护意图：集中维护不进入操作日志的路径模式
# 边界说明：只存放静态配置，不访问 Django request 或数据库。
# 风险说明：调整排除规则时，需要同步中间件行为测试与运维日志预期。
EXCLUDE_PATTERNS = [
    r"^/static/",
    r"^/media/",
    r"^/health/",
    r"^/__debug__/",
    r"^/admin/jsi18n/",
    r"^/favicon\.ico",
]


# 维护意图：集中维护 API 路径到业务模块的归属映射
# 边界说明：旧 `/api/profile*` 不在这里保留，学生画像统一使用 `/api/student/profile*`。
# 风险说明：新增模块入口时需补齐映射，否则操作日志会归入 system。
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


# 维护意图：集中维护 HTTP 方法到操作类型的默认映射
# 边界说明：登录、导入、导出等语义化动作仍由中间件按路径特判。
# 风险说明：新增非标准写操作方法时需同步这里和日志展示文案。
METHOD_ACTION_MAP = {
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
    "DELETE": "delete",
    "GET": "read",
}
