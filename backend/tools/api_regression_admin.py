"""公开 API 回归测试阶段实现。"""

from __future__ import annotations

from typing import Dict, List, Optional

from tools.api_regression_admin_support import (
    run_admin_activation_flow,
    run_admin_class_flow,
    run_admin_course_flow,
    run_admin_read_checks,
    run_admin_user_flow,
)
from tools.testing import CheckResult


# ─────────────────────────────────────────────────
# 第四阶段：管理端回归测试
# 覆盖用户管理、课程管理、班级管理、日志管理、激活码等
# 管理员端 CRUD 全链路与审计接口。
# ─────────────────────────────────────────────────


def _run_admin_regression(
    checks: List[CheckResult],
    base_url: str,
    admin_headers: Dict[str, str],
    include_all: bool,
    temp_suffix: str,
) -> Dict[str, Optional[int]]:
    """
    执行管理端用户、课程、班级与日志回归。
    :param checks: 检查结果列表。
    :param base_url: 服务基础地址。
    :param admin_headers: 管理端认证请求头。
    :param include_all: 是否执行创建与删除链路。
    :param temp_suffix: 临时资源名称后缀。
    :return: 管理端临时资源主键集合。
    """
    temp_ids: Dict[str, Optional[int]] = {
        "user_id": None,
        "course_id": None,
        "class_id": None,
        "activation_code_id": None,
    }
    run_admin_read_checks(
        checks=checks,
        base_url=base_url,
        admin_headers=admin_headers,
    )

    if not include_all:
        return temp_ids

    # ── 以下为全量模式：创建→更新→禁用→启用→删除链路 ──
    temp_ids["user_id"] = run_admin_user_flow(
        checks=checks,
        base_url=base_url,
        admin_headers=admin_headers,
        temp_suffix=temp_suffix,
    )
    temp_ids["activation_code_id"] = run_admin_activation_flow(
        checks=checks,
        base_url=base_url,
        admin_headers=admin_headers,
    )
    temp_ids["course_id"] = run_admin_course_flow(
        checks=checks,
        base_url=base_url,
        admin_headers=admin_headers,
        temp_suffix=temp_suffix,
    )
    temp_ids["class_id"] = run_admin_class_flow(
        checks=checks,
        base_url=base_url,
        admin_headers=admin_headers,
        temp_suffix=temp_suffix,
        course_id=temp_ids["course_id"],
        user_id=temp_ids["user_id"],
    )

    return temp_ids

# ─────────────────────────────────────────────────
# 第五阶段：清理临时资源
# 按创建的反序删除，保证外键依赖不冲突。
# ─────────────────────────────────────────────────
