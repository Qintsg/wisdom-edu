"""学生端考试、反馈与 AI/KT 回归检查。"""

from __future__ import annotations

from typing import Dict, List, Optional

from tools.api_regression_helpers import record_blob_check, build_exam_answers, pick_first_id, record_check
from tools.testing import CheckResult, _request


# 维护意图：执行学生考试、答题、反馈生成和报告下载接口检查
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _run_student_exam_checks(
    checks: List[CheckResult],
    base_url: str,
    student_headers: Dict[str, str],
    course_id: int,
) -> None:
    """执行学生考试、答题、反馈生成和报告下载接口检查。"""
    exams_data, _ = record_check(
        checks,
        "学生-考试列表",
        *_request(
            "GET",
            f"{base_url}/api/student/exams",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    target_exam_id = pick_first_id(exams_data, "exams", "exam_id", "id")
    if not target_exam_id:
        return

    exam_detail, detail_ok = record_check(
        checks,
        "学生-考试详情",
        *_request(
            "GET",
            f"{base_url}/api/student/exams/{target_exam_id}",
            headers=student_headers,
        ),
        expected=(200,),
    )
    if not detail_ok or not isinstance(exam_detail, dict):
        return

    answers = build_exam_answers(exam_detail.get("questions") or [])
    record_check(
        checks,
        "学生-考试草稿",
        *_request(
            "POST",
            f"{base_url}/api/student/exams/{target_exam_id}/draft",
            headers=student_headers,
            json={"answers": answers, "course_id": course_id},
        ),
        expected=(200, 400, 404),
    )
    record_check(
        checks,
        "学生-考试提交",
        *_request(
            "POST",
            f"{base_url}/api/student/exams/{target_exam_id}/submit",
            headers=student_headers,
            json={"answers": answers, "course_id": course_id},
        ),
        expected=(200, 400),
    )
    record_check(
        checks,
        "学生-考试结果",
        *_request(
            "GET",
            f"{base_url}/api/student/exams/{target_exam_id}/result",
            headers=student_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-考试统计",
        *_request(
            "GET",
            f"{base_url}/api/student/exams/{target_exam_id}/statistics",
            headers=student_headers,
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "学生-试卷答案",
        *_request(
            "GET",
            f"{base_url}/api/student/exams/{target_exam_id}/answer-sheet",
            headers=student_headers,
        ),
        expected=(200, 400, 404),
    )
    record_check(
        checks,
        "学生-反馈生成",
        *_request(
            "POST",
            f"{base_url}/api/student/feedback/generate",
            headers=student_headers,
            json={"exam_id": target_exam_id, "force": True},
            timeout=90,
        ),
        expected=(200, 500),
    )
    record_check(
        checks,
        "学生-反馈获取",
        *_request(
            "GET",
            f"{base_url}/api/student/feedback/{target_exam_id}",
            headers=student_headers,
        ),
        expected=(200, 404),
    )
    record_blob_check(
        checks,
        "学生-报告下载",
        *_request(
            "GET",
            f"{base_url}/api/student/exams/{target_exam_id}/download",
            headers=student_headers,
            params={"format": "xlsx"},
        ),
        expected=(200, 404),
    )


# 维护意图：执行学生 AI 服务与 KT 知识追踪接口检查
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _run_student_ai_kt_checks(
    checks: List[CheckResult],
    base_url: str,
    student_headers: Dict[str, str],
    course_id: int,
    point_id: Optional[int],
) -> None:
    """执行学生 AI 服务与 KT 知识追踪接口检查。"""
    if point_id:
        record_check(
            checks,
            "学生-AI知识点介绍",
            *_request(
                "POST",
                f"{base_url}/api/student/ai/node-intro",
                headers=student_headers,
                json={"point_name": "测试知识点", "course_name": "大数据技术与应用"},
            ),
            expected=(200,),
        )
    record_check(
        checks,
        "学生-AI画像分析",
        *_request(
            "POST",
            f"{base_url}/api/student/ai/profile-analysis",
            headers=student_headers,
            json={"course_id": course_id},
        ),
        expected=(200, 400, 404, 500),
    )
    record_check(
        checks,
        "学生-AI路径规划",
        *_request(
            "POST",
            f"{base_url}/api/student/ai/path-planning",
            headers=student_headers,
            json={"course_id": course_id},
            timeout=90,
        ),
        expected=(200, 404, 500),
    )
    record_check(
        checks,
        "学生-AI画像刷新",
        *_request(
            "POST",
            f"{base_url}/api/student/ai/refresh-profile",
            headers=student_headers,
            json={"course_id": course_id},
        ),
        expected=(200, 500),
    )
    record_check(
        checks,
        "学生-AI路径刷新",
        *_request(
            "POST",
            f"{base_url}/api/student/ai/refresh-learning-path",
            headers=student_headers,
            json={"course_id": course_id},
        ),
        expected=(200, 404, 500),
    )
    record_check(
        checks,
        "学生-AI对话",
        *_request(
            "POST",
            f"{base_url}/api/student/ai/chat",
            headers=student_headers,
            json={
                "message": "请给我一个学习建议",
                "knowledge_point": "大数据应用",
                "course_name": "大数据技术与应用",
                "history": [],
            },
        ),
        expected=(200,),
    )
    record_check(
        checks,
        "KT模型信息",
        *_request("GET", f"{base_url}/api/ai/kt/model-info", headers=student_headers),
        expected=(200,),
    )
    record_check(
        checks,
        "KT单次预测",
        *_request(
            "POST",
            f"{base_url}/api/ai/kt/predict",
            headers=student_headers,
            json={
                "course_id": course_id,
                "answer_history": [
                    {
                        "question_id": 1,
                        "knowledge_point_id": point_id or 1,
                        "correct": 1,
                    }
                ],
            },
        ),
        expected=(200, 400, 500),
    )
