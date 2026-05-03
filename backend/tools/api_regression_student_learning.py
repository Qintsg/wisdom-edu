"""学生端知识图谱、评测与学习路径回归检查。"""

from __future__ import annotations

from typing import Dict, List, Optional

from tools.api_regression_helpers import pick_first_id, record_check
from tools.testing import CheckResult, _request


# 维护意图：执行知识、评测、看板与路径接口检查，并返回首个知识点 ID
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _run_student_learning_checks(
    checks: List[CheckResult],
    base_url: str,
    student_headers: Dict[str, str],
    course_id: int,
    include_all: bool,
) -> Optional[int]:
    """执行知识、评测、看板与路径接口检查，并返回首个知识点 ID。"""
    point_id = _run_student_knowledge_checks(
        checks=checks,
        base_url=base_url,
        student_headers=student_headers,
        course_id=course_id,
    )
    _run_student_assessment_checks(
        checks=checks,
        base_url=base_url,
        student_headers=student_headers,
        course_id=course_id,
    )
    _run_student_path_checks(
        checks=checks,
        base_url=base_url,
        student_headers=student_headers,
        course_id=course_id,
        include_all=include_all,
    )
    return point_id


# 维护意图：执行学生端知识图谱、知识点、掌握度和资源检查
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _run_student_knowledge_checks(
    checks: List[CheckResult],
    base_url: str,
    student_headers: Dict[str, str],
    course_id: int,
) -> Optional[int]:
    """执行学生端知识图谱、知识点、掌握度和资源检查。"""
    knowledge_map, _ = record_check(
        checks,
        "学生-知识图谱",
        *_request(
            "GET",
            f"{base_url}/api/student/knowledge-map",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    point_id = pick_first_id(knowledge_map, "nodes", "point_id", "id")
    record_check(
        checks,
        "学生-知识点列表",
        *_request(
            "GET",
            f"{base_url}/api/student/knowledge/points",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-知识关系",
        *_request(
            "GET",
            f"{base_url}/api/student/knowledge/relations",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-知识掌握度",
        *_request(
            "GET",
            f"{base_url}/api/student/knowledge/mastery",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-课程资源",
        *_request(
            "GET",
            f"{base_url}/api/student/resources",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    if point_id:
        record_check(
            checks,
            "学生-知识点详情",
            *_request(
                "GET",
                f"{base_url}/api/student/knowledge-points/{point_id}",
                headers=student_headers,
                params={"course_id": course_id},
            ),
            expected=(200,),
        )
        record_check(
            checks,
            "学生-知识点资源",
            *_request(
                "GET",
                f"{base_url}/api/student/knowledge-points/{point_id}/resources",
                headers=student_headers,
                params={"course_id": course_id},
            ),
            expected=(200,),
        )
    return point_id


# 维护意图：执行学生初始评测、看板和学习进度接口检查
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _run_student_assessment_checks(
    checks: List[CheckResult],
    base_url: str,
    student_headers: Dict[str, str],
    course_id: int,
) -> None:
    """执行学生初始评测、看板和学习进度接口检查。"""
    for name, path, expected in (
        ("学生-能力测评题目", "/api/student/assessments/initial/ability", (200,)),
        ("学生-习惯问卷题目", "/api/student/assessments/initial/habit", (200,)),
        ("学生-知识测评题目", "/api/student/assessments/initial/knowledge", (200,)),
        ("学生-知识测评结果", "/api/student/assessments/initial/knowledge/result", (200, 404)),
        ("学生-学习看板聚合", "/api/student/dashboard", (200,)),
        ("学生-学习进度", "/api/student/learning-progress", (200,)),
    ):
        record_check(
            checks,
            name,
            *_request(
                "GET",
                f"{base_url}{path}",
                headers=student_headers,
                params={"course_id": course_id},
            ),
            expected=expected,
        )


# 维护意图：执行学生学习路径、路径节点和节点资源接口检查
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _run_student_path_checks(
    checks: List[CheckResult],
    base_url: str,
    student_headers: Dict[str, str],
    course_id: int,
    include_all: bool,
) -> None:
    """执行学生学习路径、路径节点和节点资源接口检查。"""
    path_data, _ = record_check(
        checks,
        "学生-学习路径",
        *_request(
            "GET",
            f"{base_url}/api/student/learning-path",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-刷新学习路径",
        *_request(
            "POST",
            f"{base_url}/api/student/learning-path/adjust",
            headers=student_headers,
            json={"course_id": course_id, "reason": "manual_refresh"},
        ),
        expected=(200, 404),
    )

    node_id = pick_first_id(path_data, "nodes", "node_id", "id")
    if not node_id:
        return

    record_check(
        checks,
        "学生-节点详情",
        *_request(
            "GET",
            f"{base_url}/api/student/path-nodes/{node_id}",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-节点开始",
        *_request(
            "POST",
            f"{base_url}/api/student/path-nodes/{node_id}/start",
            headers=student_headers,
            json={"course_id": course_id},
        ),
        expected=(200, 409),
    )
    record_check(
        checks,
        "学生-节点资源",
        *_request(
            "GET",
            f"{base_url}/api/student/path-nodes/{node_id}/resources",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    ai_resources, _ = record_check(
        checks,
        "学生-AI资源",
        *_request(
            "GET",
            f"{base_url}/api/student/path-nodes/{node_id}/ai-resources",
            headers=student_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-节点考试",
        *_request(
            "GET",
            f"{base_url}/api/student/path-nodes/{node_id}/exams",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-阶段测试题目",
        *_request(
            "GET",
            f"{base_url}/api/student/path-nodes/{node_id}/stage-test",
            headers=student_headers,
        ),
        expected=(200, 400, 404),
    )
    if include_all and isinstance(ai_resources, dict):
        external_resources = ai_resources.get("external_resources") or []
        if external_resources:
            external_resource_id = external_resources[0].get("resource_id")
            if external_resource_id:
                record_check(
                    checks,
                    "学生-外部资源完成",
                    *_request(
                        "POST",
                        f"{base_url}/api/student/path-nodes/{node_id}/resources/{external_resource_id}/complete",
                        headers=student_headers,
                        json={"course_id": course_id},
                    ),
                    expected=(200,),
                )
