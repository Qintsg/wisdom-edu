"""操作日志中文描述生成规则。"""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest

from .logging_setup import ACTION_TYPE_DISPLAY, MODULE_DISPLAY


PathRule = tuple[Callable[[str, str], bool], str]


# 维护意图：构造仅判断路径片段的日志描述规则
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _contains(keyword: str) -> Callable[[str, str], bool]:
    """构造仅判断路径片段的日志描述规则。"""
    return lambda path, method: keyword in path


# 维护意图：构造同时匹配路径片段和请求方法的日志描述规则
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _contains_with_method(keyword: str, expected_method: str) -> Callable[[str, str], bool]:
    """构造同时匹配路径片段和请求方法的日志描述规则。"""
    return lambda path, method: keyword in path and method == expected_method


FIXED_DESCRIPTION_RULES: tuple[PathRule, ...] = (
    (_contains("register"), "用户注册"),
    (_contains("login"), "用户登录"),
    (_contains("logout"), "用户登出"),
    (_contains("userinfo/update"), "更新用户信息"),
    (_contains("userinfo"), "查询用户信息"),
    (_contains("profile/habit"), "更新学习偏好"),
    (_contains("profile/update"), "更新学习画像"),
    (_contains("profile/history"), "查询画像历史"),
    (_contains("profile"), "查询学习画像"),
    (_contains("activation-codes/generate"), "生成激活码"),
    (_contains_with_method("activation-codes", "DELETE"), "删除激活码"),
    (_contains("activation-codes"), "管理激活码"),
    (_contains("invitations/generate"), "生成班级邀请码"),
    (_contains_with_method("invitations", "DELETE"), "删除邀请码"),
    (_contains("/courses/create"), "创建课程"),
    (_contains("/courses/select"), "切换当前课程"),
    (_contains("/classes/create"), "创建班级"),
    (_contains("/classes/join"), "加入班级"),
    (_contains("/leave"), "退出班级"),
    (_contains("/publish-course"), "发布课程到班级"),
    (_contains_with_method("students", "DELETE"), "从班级移除学生"),
    (_contains("knowledge-map/import"), "导入知识图谱"),
    (_contains("knowledge-map/publish"), "发布知识图谱"),
    (_contains("knowledge-map/sync-neo4j"), "同步知识图谱到Neo4j"),
    (_contains("questions/import"), "导入题库"),
    (_contains("assessments/start"), "开始测评"),
    (_contains("feedback/generate"), "生成反馈报告"),
    (_contains("learning-record"), "记录学习进度"),
)


# 维护意图：根据请求路径和操作类型生成易读的中文描述。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def generate_operation_description(
    request: HttpRequest,
    action_type: str,
    module: str,
) -> str:
    """
    根据请求路径和操作类型生成易读的中文描述。

    :param request: Django request 对象。
    :param action_type: 标准化操作类型。
    :param module: 标准化模块名。
    :return: 中文操作描述。
    """
    path = request.path
    method = request.method
    action_display = ACTION_TYPE_DISPLAY.get(action_type, action_type)
    module_display = MODULE_DISPLAY.get(module, module)

    fixed_description = _match_fixed_description(path, method)
    if fixed_description:
        return fixed_description
    if "knowledge-points" in path:
        return f"{action_display}知识点"
    if "resources" in path:
        return f"{action_display}学习资源"
    if "questions" in path:
        return f"{action_display}题目"
    if "assessments" in path and "submit" in path:
        return "提交测评答案"
    if "exams" in path and "submit" in path:
        return "提交考试答案"
    if "exams" in path and "create" in path:
        return "创建考试"
    if "learning-path" in path:
        return f"{action_display}学习路径"
    return f"{module_display} - {action_display}操作"


# 维护意图：按声明顺序匹配固定路径描述，避免入口函数堆叠长 if 链
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _match_fixed_description(path: str, method: str) -> str:
    """按声明顺序匹配固定路径描述，避免入口函数堆叠长 if 链。"""
    for predicate, description in FIXED_DESCRIPTION_RULES:
        if predicate(path, method):
            return description
    return ""


__all__ = ["generate_operation_description"]
