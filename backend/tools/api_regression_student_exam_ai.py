"""学生端考试、反馈与 AI/KT 回归检查。"""

from __future__ import annotations

from typing import Dict, List, Optional

from tools.api_regression_helpers import _blob, _build_exam_answers, _pick_first_id, _record
from tools.testing import CheckResult, _request


def _run_student_exam_checks(
    checks: List[CheckResult],
    base_url: str,
    student_headers: Dict[str, str],
    course_id: int,
) -> None:
    """执行学生考试、答题、反馈生成和报告下载接口检查。"""
    exams_data, _ = _record(
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
    target_exam_id = _pick_first_id(exams_data, "exams", "exam_id", "id")
    if not target_exam_id:
        return

    exam_detail, detail_ok = _record(
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

    answers = _build_exam_answers(exam_detail.get("questions") or [])
    _record(
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
    _record(
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
    _record(
        checks,
        "学生-考试结果",
        *_request(
            "GET",
            f"{base_url}/api/student/exams/{target_exam_id}/result",
            headers=student_headers,
        ),
        expected=(200,),
    )
    _record(
        checks,
        "学生-考试统计",
        *_request(
            "GET",
            f"{base_url}/api/student/exams/{target_exam_id}/statistics",
            headers=student_headers,
        ),
        expected=(200,),
    )
    _record(
        checks,
        "学生-试卷答案",
        *_request(
            "GET",
            f"{base_url}/api/student/exams/{target_exam_id}/answer-sheet",
            headers=student_headers,
        ),
        expected=(200, 400, 404),
    )
    _record(
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
    _record(
        checks,
        "学生-反馈获取",
        *_request(
            "GET",
            f"{base_url}/api/student/feedback/{target_exam_id}",
            headers=student_headers,
        ),
        expected=(200, 404),
    )
    _blob(
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


def _run_student_ai_kt_checks(
    checks: List[CheckResult],
    base_url: str,
    student_headers: Dict[str, str],
    course_id: int,
    point_id: Optional[int],
) -> None:
    """执行学生 AI 服务与 KT 知识追踪接口检查。"""
    if point_id:
        _record(
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
    _record(
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
    _record(
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
    _record(
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
    _record(
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
    _record(
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
    _record(
        checks,
        "KT模型信息",
        *_request("GET", f"{base_url}/api/ai/kt/model-info", headers=student_headers),
        expected=(200,),
    )
    _record(
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
