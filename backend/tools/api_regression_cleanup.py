"""公开 API 回归测试临时数据清理。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from tools.api_regression_helpers import _record
from tools.testing import CheckResult, _request


Headers: TypeAlias = dict[str, str]
TempIds: TypeAlias = dict[str, int | None]


@dataclass(frozen=True)
class RegressionCleanupContext:
    """回归清理所需上下文。"""

    checks: list[CheckResult]
    base_url: str
    teacher_headers: Headers
    admin_headers: Headers
    teacher_temp_ids: TempIds
    admin_temp_ids: TempIds
    include_all: bool


@dataclass(frozen=True)
class CleanupAction:
    """单个临时实体删除动作。"""

    label: str
    url: str
    headers: Headers


def cleanup_regression_entities(context: RegressionCleanupContext) -> None:
    """清理全量公开 API 回归中创建的临时数据。"""
    if not context.include_all:
        return

    for action in build_cleanup_actions(context):
        record_cleanup_action(context.checks, action)


def build_cleanup_actions(context: RegressionCleanupContext) -> list[CleanupAction]:
    """按依赖顺序生成临时实体删除动作。"""
    return (
        teacher_cleanup_actions(context)
        + admin_cleanup_actions(context)
    )


def teacher_cleanup_actions(context: RegressionCleanupContext) -> list[CleanupAction]:
    """生成教师端临时资源清理动作。"""
    route_templates = [
        ("invitation_id", "教师-删除邀请码", "/api/teacher/invitations/{id}"),
        ("exam_id", "教师-删除考试", "/api/teacher/exams/{id}/delete"),
        ("question_id", "教师-删除题目", "/api/teacher/questions/{id}/delete"),
        ("class_id", "教师-删除班级", "/api/teacher/classes/{id}/delete"),
        ("course_id", "教师-删除课程", "/api/teacher/courses/{id}/delete"),
    ]
    return build_actions_from_templates(
        base_url=context.base_url,
        headers=context.teacher_headers,
        temp_ids=context.teacher_temp_ids,
        route_templates=route_templates,
    )


def admin_cleanup_actions(context: RegressionCleanupContext) -> list[CleanupAction]:
    """生成管理端临时资源清理动作。"""
    route_templates = [
        ("activation_code_id", "管理员-删除激活码", "/api/admin/activation-codes/{id}"),
        ("class_id", "管理员-删除班级", "/api/admin/classes/{id}"),
        ("course_id", "管理员-删除课程", "/api/admin/courses/{id}"),
        ("user_id", "管理员-删除用户", "/api/admin/users/{id}/delete"),
    ]
    return build_actions_from_templates(
        base_url=context.base_url,
        headers=context.admin_headers,
        temp_ids=context.admin_temp_ids,
        route_templates=route_templates,
    )


def build_actions_from_templates(
    *,
    base_url: str,
    headers: Headers,
    temp_ids: TempIds,
    route_templates: list[tuple[str, str, str]],
) -> list[CleanupAction]:
    """从 ID 字典和路由模板生成有效删除动作。"""
    actions: list[CleanupAction] = []
    for id_key, label, route_template in route_templates:
        entity_id = temp_ids.get(id_key)
        if not entity_id:
            continue
        actions.append(
            CleanupAction(
                label=label,
                url=f"{base_url}{route_template.format(id=entity_id)}",
                headers=headers,
            )
        )
    return actions


def record_cleanup_action(checks: list[CheckResult], action: CleanupAction) -> None:
    """执行删除请求并记录回归检查结果。"""
    response, error = _request("DELETE", action.url, headers=action.headers)
    _record(
        checks,
        action.label,
        response,
        error,
        expected=(200, 204),
    )


def _cleanup_regression_entities(
    checks: list[CheckResult],
    base_url: str,
    teacher_headers: Headers,
    admin_headers: Headers,
    teacher_temp_ids: TempIds,
    admin_temp_ids: TempIds,
    include_all: bool,
) -> None:
    """兼容旧导入路径的清理入口。"""
    cleanup_regression_entities(
        RegressionCleanupContext(
            checks=checks,
            base_url=base_url,
            teacher_headers=teacher_headers,
            admin_headers=admin_headers,
            teacher_temp_ids=teacher_temp_ids,
            admin_temp_ids=admin_temp_ids,
            include_all=include_all,
        )
    )
