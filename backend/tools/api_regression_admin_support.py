"""管理端 API 回归测试辅助步骤。"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from tools.api_regression_helpers import TEMP_PREFIX, record_blob_check, record_check
from tools.testing import CheckResult, _request


# 维护意图：执行管理端只读列表、日志和导出检查
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def run_admin_read_checks(
    *,
    checks: List[CheckResult],
    base_url: str,
    admin_headers: Dict[str, str],
) -> None:
    """执行管理端只读列表、日志和导出检查。"""
    record_check(
        checks,
        "管理员-用户列表",
        *_request("GET", f"{base_url}/api/admin/users", headers=admin_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-课程列表",
        *_request("GET", f"{base_url}/api/admin/courses", headers=admin_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-班级列表",
        *_request("GET", f"{base_url}/api/admin/classes", headers=admin_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-激活码列表",
        *_request("GET", f"{base_url}/api/admin/activation-codes", headers=admin_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-日志列表",
        *_request("GET", f"{base_url}/api/admin/logs", headers=admin_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-日志统计",
        *_request("GET", f"{base_url}/api/admin/logs/statistics", headers=admin_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-日志筛选项",
        *_request("GET", f"{base_url}/api/admin/logs/options", headers=admin_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-日志模块",
        *_request("GET", f"{base_url}/api/admin/logs/modules", headers=admin_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-日志操作类型",
        *_request("GET", f"{base_url}/api/admin/logs/actions", headers=admin_headers),
        expected=(200,),
    )
    record_blob_check(
        checks,
        "管理员-日志导出",
        *_request("GET", f"{base_url}/api/admin/logs/export", headers=admin_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-日志清理",
        *_request(
            "DELETE",
            f"{base_url}/api/admin/logs/clean",
            headers=admin_headers,
            params={"days": 7},
        ),
        expected=(200,),
    )


# 维护意图：执行管理端临时用户创建和后续操作链路
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def run_admin_user_flow(
    *,
    checks: List[CheckResult],
    base_url: str,
    admin_headers: Dict[str, str],
    temp_suffix: str,
) -> Optional[int]:
    """执行管理端临时用户创建和后续操作链路。"""
    user_resp, user_ok = record_check(
        checks,
        "管理员-创建用户",
        *_request(
            "POST",
            f"{base_url}/api/admin/users/create",
            headers=admin_headers,
            json={
                "username": f"api_user_{temp_suffix}",
                "password": "Test123456",
                "role": "student",
                "real_name": "API回归用户",
            },
        ),
        expected=(200, 201),
    )
    if not user_ok or not isinstance(user_resp, dict):
        return None

    user_id = user_resp.get("user_id") or user_resp.get("id")
    if user_id is None:
        return None
    record_check(
        checks,
        "管理员-用户详情",
        *_request(
            "GET",
            f"{base_url}/api/admin/users/{user_id}",
            headers=admin_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-更新用户",
        *_request(
            "PUT",
            f"{base_url}/api/admin/users/{user_id}/update",
            headers=admin_headers,
            json={"real_name": "API回归用户-更新"},
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-禁用用户",
        *_request(
            "POST",
            f"{base_url}/api/admin/users/{user_id}/disable",
            headers=admin_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-启用用户",
        *_request(
            "POST",
            f"{base_url}/api/admin/users/{user_id}/enable",
            headers=admin_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-重置密码",
        *_request(
            "POST",
            f"{base_url}/api/admin/users/{user_id}/reset-password",
            headers=admin_headers,
            json={"new_password": "Test123456"},
        ),
        expected=(200,),
    )
    return int(user_id)


# 维护意图：执行管理端激活码生成链路
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def run_admin_activation_flow(
    *,
    checks: List[CheckResult],
    base_url: str,
    admin_headers: Dict[str, str],
) -> Optional[int]:
    """执行管理端激活码生成链路。"""
    activation_resp, activation_ok = record_check(
        checks,
        "管理员-生成激活码",
        *_request(
            "POST",
            f"{base_url}/api/admin/activation-codes/generate",
            headers=admin_headers,
            json={"code_type": "teacher", "count": 1, "remark": "API回归"},
        ),
        expected=(200, 201),
    )
    if not activation_ok or not isinstance(activation_resp, dict):
        return None

    codes = activation_resp.get("codes") or []
    if not codes or not isinstance(codes[0], dict):
        return None
    activation_id = codes[0].get("id")
    return int(activation_id) if activation_id is not None else None


# 维护意图：执行管理端课程创建和只读详情链路
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def run_admin_course_flow(
    *,
    checks: List[CheckResult],
    base_url: str,
    admin_headers: Dict[str, str],
    temp_suffix: str,
) -> Optional[int]:
    """执行管理端课程创建和只读详情链路。"""
    course_resp, course_ok = record_check(
        checks,
        "管理员-创建课程",
        *_request(
            "POST",
            f"{base_url}/api/admin/courses/create",
            headers=admin_headers,
            json={"name": f"{TEMP_PREFIX}管理员课程{temp_suffix}", "teacher_id": None},
        ),
        expected=(200, 201),
    )
    if not course_ok or not isinstance(course_resp, dict):
        return None

    course_id = course_resp.get("course_id") or course_resp.get("id")
    if course_id is None:
        return None
    record_check(
        checks,
        "管理员-课程详情",
        *_request(
            "GET",
            f"{base_url}/api/admin/courses/{course_id}",
            headers=admin_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-课程统计",
        *_request(
            "GET",
            f"{base_url}/api/admin/courses/{course_id}/statistics",
            headers=admin_headers,
        ),
        expected=(200,),
    )
    return int(course_id)


# 维护意图：执行管理端班级创建、查详情和学生管理链路
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def run_admin_class_flow(
    *,
    checks: List[CheckResult],
    base_url: str,
    admin_headers: Dict[str, str],
    temp_suffix: str,
    course_id: Optional[int],
    user_id: Optional[int],
) -> Optional[int]:
    """执行管理端班级创建、查详情和学生管理链路。"""
    class_resp, class_ok = record_check(
        checks,
        "管理员-创建班级",
        *_request(
            "POST",
            f"{base_url}/api/admin/classes/create",
            headers=admin_headers,
            json={
                "name": f"{TEMP_PREFIX}管理员班级{temp_suffix}",
                "course_id": course_id,
            },
        ),
        expected=(200, 201),
    )
    if not class_ok or not isinstance(class_resp, dict):
        return None

    class_id = class_resp.get("class_id") or class_resp.get("id")
    if class_id is None:
        return None
    record_check(
        checks,
        "管理员-班级详情",
        *_request(
            "GET",
            f"{base_url}/api/admin/classes/{class_id}",
            headers=admin_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "管理员-班级学生",
        *_request(
            "GET",
            f"{base_url}/api/admin/classes/{class_id}/students",
            headers=admin_headers,
        ),
        expected=(200,),
    )
    if user_id is not None:
        record_check(
            checks,
            "管理员-班级加学生",
            *_request(
                "POST",
                f"{base_url}/api/admin/classes/{class_id}/students/add",
                headers=admin_headers,
                json={"student_ids": [user_id]},
            ),
            expected=(200,),
        )
        record_check(
            checks,
            "管理员-班级移除学生",
            *_request(
                "DELETE",
                f"{base_url}/api/admin/classes/{class_id}/students/{user_id}",
                headers=admin_headers,
            ),
            expected=(200,),
        )
    record_check(
        checks,
        "管理员-班级统计",
        *_request(
            "GET",
            f"{base_url}/api/admin/classes/{class_id}/statistics",
            headers=admin_headers,
        ),
        expected=(200,),
    )
    return int(class_id)
