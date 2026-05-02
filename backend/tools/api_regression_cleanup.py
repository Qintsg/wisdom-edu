"""公开 API 回归测试阶段实现。"""

from __future__ import annotations

from typing import Dict, List, Optional

from tools.testing import CheckResult, _request
from tools.api_regression_helpers import (
    TEMP_PREFIX,
    _blob,
    _build_exam_answers,
    _pick_first_id,
    _record,
)
def _cleanup_regression_entities(
    checks: List[CheckResult],
    base_url: str,
    teacher_headers: Dict[str, str],
    admin_headers: Dict[str, str],
    teacher_temp_ids: Dict[str, Optional[int]],
    admin_temp_ids: Dict[str, Optional[int]],
    include_all: bool,
) -> None:
    """
    清理全量回归中创建的临时数据。
    :param checks: 检查结果列表。
    :param base_url: 服务基础地址。
    :param teacher_headers: 教师端认证请求头。
    :param admin_headers: 管理端认证请求头。
    :param teacher_temp_ids: 教师端临时资源主键集合。
    :param admin_temp_ids: 管理端临时资源主键集合。
    :param include_all: 是否处于全量回归模式。
    :return: None。
    """
    if not include_all:
        return

    if teacher_temp_ids.get("invitation_id"):
        _record(
            checks,
    # ── 清理教师端临时资源（邀请码→考试→题目→班级→课程）──
            "教师-删除邀请码",
            *_request(
                "DELETE",
                f"{base_url}/api/teacher/invitations/{teacher_temp_ids['invitation_id']}",
                headers=teacher_headers,
            ),
            expected=(200, 204),
        )
    if teacher_temp_ids.get("exam_id"):
        _record(
            checks,
            "教师-删除考试",
            *_request(
                "DELETE",
                f"{base_url}/api/teacher/exams/{teacher_temp_ids['exam_id']}/delete",
                headers=teacher_headers,
            ),
            expected=(200, 204),
        )
    if teacher_temp_ids.get("question_id"):
        _record(
            checks,
            "教师-删除题目",
            *_request(
                "DELETE",
                f"{base_url}/api/teacher/questions/{teacher_temp_ids['question_id']}/delete",
                headers=teacher_headers,
            ),
            expected=(200, 204),
        )
    if teacher_temp_ids.get("class_id"):
        _record(
            checks,
            "教师-删除班级",
            *_request(
                "DELETE",
                f"{base_url}/api/teacher/classes/{teacher_temp_ids['class_id']}/delete",
                headers=teacher_headers,
            ),
            expected=(200, 204),
        )
    if teacher_temp_ids.get("course_id"):
    # ── 清理管理端临时资源（激活码→班级→课程→用户）──
        _record(
            checks,
            "教师-删除课程",
            *_request(
                "DELETE",
                f"{base_url}/api/teacher/courses/{teacher_temp_ids['course_id']}/delete",
                headers=teacher_headers,
            ),
            expected=(200, 204),
        )

    if admin_temp_ids.get("activation_code_id"):
        _record(
            checks,
            "管理员-删除激活码",
            *_request(
                "DELETE",
                f"{base_url}/api/admin/activation-codes/{admin_temp_ids['activation_code_id']}",
                headers=admin_headers,
            ),
            expected=(200, 204),
        )
    if admin_temp_ids.get("class_id"):
        _record(
            checks,
            "管理员-删除班级",
            *_request(
                "DELETE",
                f"{base_url}/api/admin/classes/{admin_temp_ids['class_id']}",
                headers=admin_headers,
            ),
            expected=(200, 204),
        )
    if admin_temp_ids.get("course_id"):
        _record(
            checks,
            "管理员-删除课程",
            *_request(
                "DELETE",
                f"{base_url}/api/admin/courses/{admin_temp_ids['course_id']}",
                headers=admin_headers,

# ─────────────────────────────────────────────────
# 主入口：按阶段串联全部回归流程
# ─────────────────────────────────────────────────
            ),
            expected=(200, 204),
        )
    if admin_temp_ids.get("user_id"):
        _record(
            checks,
            "管理员-删除用户",
            *_request(
                "DELETE",
                f"{base_url}/api/admin/users/{admin_temp_ids['user_id']}/delete",
                headers=admin_headers,
            ),
            expected=(200, 204),
        )
