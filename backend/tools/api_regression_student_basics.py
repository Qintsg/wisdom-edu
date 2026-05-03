"""学生端基础信息、课程与班级回归检查。"""

from __future__ import annotations

from typing import Dict, List

from tools.api_regression_helpers import pick_first_id, record_check
from tools.testing import CheckResult, _request


# 维护意图：执行学生基础信息、课程选择与班级相关接口检查
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _run_student_basic_checks(
    checks: List[CheckResult],
    base_url: str,
    student_headers: Dict[str, str],
    course_id: int,
) -> None:
    """执行学生基础信息、课程选择与班级相关接口检查。"""
    record_check(
        checks,
        "学生-用户信息",
        *_request("GET", f"{base_url}/api/auth/userinfo", headers=student_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-课程列表",
        *_request("GET", f"{base_url}/api/courses", headers=student_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-选择课程",
        *_request(
            "POST",
            f"{base_url}/api/courses/select",
            headers=student_headers,
            json={"course_id": course_id},
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-测评状态",
        *_request(
            "GET",
            f"{base_url}/api/student/assessments/status",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-画像",
        *_request(
            "GET",
            f"{base_url}/api/student/profile",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-更新习惯偏好",
        *_request(
            "PUT",
            f"{base_url}/api/student/profile/habit",
            headers=student_headers,
            json={
                "preferred_resource": "video",
                "preferred_study_time": "evening",
                "study_pace": "moderate",
            },
        ),
        expected=(200,),
    )

    classes_data, _ = record_check(
        checks,
        "学生-班级列表",
        *_request("GET", f"{base_url}/api/student/classes", headers=student_headers),
        expected=(200,),
    )
    class_id = pick_first_id(classes_data, "classes", "class_id", "id")
    if not class_id:
        return

    record_check(
        checks,
        "学生-班级详情",
        *_request(
            "GET",
            f"{base_url}/api/student/classes/{class_id}",
            headers=student_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-班级成员",
        *_request(
            "GET",
            f"{base_url}/api/student/classes/{class_id}/members",
            headers=student_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-班级排名",
        *_request(
            "GET",
            f"{base_url}/api/student/classes/{class_id}/ranking",
            headers=student_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-班级通知",
        *_request(
            "GET",
            f"{base_url}/api/student/classes/{class_id}/notifications",
            headers=student_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-班级作业",
        *_request(
            "GET",
            f"{base_url}/api/student/classes/{class_id}/assignments",
            headers=student_headers,
        ),
        expected=(200,),
    )
