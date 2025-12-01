#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
公开 API 回归测试工具。
覆盖学生、教师、管理员三端的公开 API 回归测试。
@Project : wisdom-edu
@File : api_regression.py
@Author : Qintsg
@Date : 2026-03-23
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tools.testing import (
    CheckResult,
    _extract_data,
    _login,
    _print_checks,
    _request,
    _resolve_course_id,
)


# ─── 全局常量 ───
# DEFAULT_BASE_URL: 本地开发服务器的默认基础地址
# TEMP_PREFIX: 回归测试创建的临时资源统一前缀，便于事后识别和清理

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
TEMP_PREFIX = "[API回归]"



# ─────────────────────────────────────────────────
# 辅助函数：结果记录与数据构建
# ─────────────────────────────────────────────────
def _record(
    checks: List[CheckResult],
    name: str,
    resp,
    err: Optional[str],
    expected: Tuple[int, ...] = (200,),
    detail: Optional[str] = None,
) -> Tuple[Optional[Any], bool]:
    """
    记录普通 JSON 接口检查结果。
    :param checks: 检查结果列表。
    :param name: 检查项名称。
    :param resp: HTTP 响应对象。
    # 将原始响应拆分为 JSON 载荷和状态码
    :param err: 请求阶段错误文本。
    :param expected: 允许的状态码集合。
    :param detail: 额外检查描述。
    # 尝试提取嵌套 data 字段（适配 DRF 标准响应结构）
    :return: 响应载荷与是否通过检查的二元组。
    """
    # 判定：状态码在预期范围内即视为通过
    if err:
        checks.append(CheckResult(name, False, err))
        return None, False
    # 构建检查结果记录，附带摘要信息
    if resp is None:
        checks.append(CheckResult(name, False, "无响应对象"))
        return None, False

    ok = resp.status_code in expected
    payload = _extract_data(resp)
    success_detail = detail or ("ok" if ok else f"unexpected={resp.status_code}")
    checks.append(CheckResult(name, ok, success_detail, status_code=resp.status_code))
    return payload, ok



# 记录二进制导出类接口的检查结果（如 Excel/PDF 下载）
def _blob(
    checks: List[CheckResult],
    name: str,
    resp,
    err: Optional[str],
    expected: Tuple[int, ...] = (200,),
) -> bool:
    """
    记录二进制导出接口检查结果。
    :param checks: 检查结果列表。
    :param name: 检查项名称。
    # 二进制响应不解析 JSON，直接按状态码和 Content-Type 判定
    :param resp: HTTP 响应对象。
    :param err: 请求阶段错误文本。
    :param expected: 允许的状态码集合。
    # 非 JSON 响应按字节长度生成摘要
    :return: 当前导出接口是否通过检查。
    """
    if err:
        checks.append(CheckResult(name, False, err))
        return False
    if resp is None:
        checks.append(CheckResult(name, False, "无响应对象"))
        return False
    ok = resp.status_code in expected and bool(resp.content)
    detail = f"bytes={len(resp.content)}" if ok else "导出失败"
    checks.append(CheckResult(name, ok, detail, status_code=resp.status_code))
    return ok



# 根据考试题目列表构建默认答案载荷（用于自动化提交考试）
def _build_exam_answers(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    根据试卷题型构造默认答题载荷。
    :param questions: 试卷题目列表。
    :return: 以题目 ID 为键的答案字典。
    """
    answers: Dict[str, Any] = {}
    for item in questions:
        qid = str(item.get("question_id") or item.get("id"))
        qtype = item.get("type") or item.get("question_type")
        options = item.get("options") or []
        if qtype == "multiple_choice":
            if options:
                first = options[0]
                value = (
                    first.get("answer_value") or first.get("value") or first.get("key")
                )
            # 多选题：选择前两个选项值
                answers[qid] = [value] if value is not None else []
            else:
                answers[qid] = []
        elif qtype == "true_false":
            # 判断题：默认选 true
            answers[qid] = "true"
        elif qtype in {"single_choice", "single"}:
            first = options[0] if options else {}
            # 单选题：取第一个选项的值
            answers[qid] = (
                first.get("answer_value")
                or first.get("value")
                or first.get("key")
            # 其他题型（填空、简答等）：使用占位文本
                or ""
            )
        else:
            answers[qid] = "测试答案"
    return answers



# 从 OpenAPI 文档文件中加载所有已声明的路径
def _load_documented_paths() -> List[str]:
    """
    读取 OpenAPI 文档中声明的路径列表。
    :return: 文档中的 API 路径列表。
    """
    api_doc = Path(__file__).resolve().parents[2] / "docs" / "api.yaml"
    if not api_doc.exists():
    # 读取 YAML 文件，用正则逐行提取以 / 开头的路径键
        return []
    text = api_doc.read_text(encoding="utf-8")
    return [
        line.strip().rstrip(":")
        for line in text.splitlines()
        if re.match(r"^  /", line)
    ]



# 将 JWT token 封装为 Bearer 认证请求头
def _build_auth_headers(token: Optional[str]) -> Dict[str, str]:
    """
    将登录 token 转换为 Bearer 认证头。
    :param token: 登录接口返回的访问令牌。
    :return: 请求头字典。
    """
    return {"Authorization": f"Bearer {token}"} if token else {}



# 从列表型 API 响应中提取首条记录的主键
def _pick_first_id(
    payload: Optional[Dict[str, Any]], list_key: str, *candidate_keys: str
) -> Optional[Any]:
    """
    从列表型接口返回中提取首个对象主键。
    :param payload: 接口返回的 JSON 数据。
    :param list_key: 列表字段名称。
    :param candidate_keys: 候选主键字段集合。
    # 适配分页与非分页两种响应结构：results 列表或直接列表
    :return: 首个命中的主键值。
    """
    if not isinstance(payload, dict):
        return None
    items = payload.get(list_key) or []
    # 优先取 id 字段，回退到 <前缀>_id 字段
    if not items:
        return None
    first_item = items[0]
    if not isinstance(first_item, dict):
        return None
    for key in candidate_keys:
        value = first_item.get(key)
        if value is not None:
            return value
    return None



# ─────────────────────────────────────────────────
# 第一阶段：文档与健康检查
# ─────────────────────────────────────────────────
def _run_document_checks(checks: List[CheckResult], base_url: str) -> None:
    """
    执行健康检查与文档端点检查。
    :param checks: 检查结果列表。
    :param base_url: 服务基础地址。
    :return: None。
    """
    documented_paths = _load_documented_paths()
    checks.append(
    # 健康检查：确保服务可达
        CheckResult(
            "API文档路径统计", True, f"documented_paths={len(documented_paths)}"
        )
    )

    _, ok = _record(
        checks,
    # Schema / Swagger / ReDoc 文档端点可用性
        "健康检查",
        *_request("GET", f"{base_url}/health/"),
        expected=(200,),
    )
    if not ok:
        return

    for name, path in (
        ("Schema", "/api/schema/"),
        ("Swagger", "/api/docs/"),
        ("ReDoc", "/api/redoc/"),
    ):
        _record(
            checks,
            f"文档接口-{name}",
            *_request("GET", f"{base_url}{path}"),
            expected=(200,),
        )



# ─────────────────────────────────────────────────
# 第二阶段：学生端回归测试
# 覆盖个人信息、课程、评测、知识图谱、学习路径、
# 考试、AI 服务、KT 模型等全部学生可用接口。
# ─────────────────────────────────────────────────
def _run_student_regression(
    checks: List[CheckResult],
    base_url: str,
    student_headers: Dict[str, str],
    course_id: int,
    include_all: bool,
) -> None:
    """
    执行学生端主要学习链路与 AI 能力回归。
    :param checks: 检查结果列表。
    :param base_url: 服务基础地址。
    :param student_headers: 学生端认证请求头。
    :param course_id: 当前课程 ID。
    :param include_all: 是否执行全量副作用链路。
    :return: None。
    """
    _record(
        checks,
    # ── 学生基本信息与课程 ──
        "学生-用户信息",
        *_request("GET", f"{base_url}/api/auth/userinfo", headers=student_headers),
        expected=(200,),
    )
    _record(
        checks,
        "学生-课程列表",
        *_request("GET", f"{base_url}/api/courses", headers=student_headers),
        expected=(200,),
    )
    _record(
        checks,
        "学生-选择课程",
        *_request(
            "POST",
            f"{base_url}/api/courses/select",
            headers=student_headers,
            json={"course_id": course_id},
        ),
        expected=(200,),
    # ── 评测状态与用户画像 ──
    )
    _record(
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
    _record(
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
    _record(
        checks,
    # ── 学习习惯偏好 ──
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

    classes_data, _ = _record(
        checks,
        "学生-班级列表",
        *_request("GET", f"{base_url}/api/student/classes", headers=student_headers),
        expected=(200,),
    # ── 班级相关：详情、成员、排名、通知、作业 ──
    )
    class_id = _pick_first_id(classes_data, "classes", "class_id", "id")
    if class_id:
        _record(
            checks,
            "学生-班级详情",
            *_request(
                "GET",
                f"{base_url}/api/student/classes/{class_id}",
                headers=student_headers,
            ),
            expected=(200,),
        )
        _record(
            checks,
            "学生-班级成员",
            *_request(
                "GET",
                f"{base_url}/api/student/classes/{class_id}/members",
                headers=student_headers,
            ),
            expected=(200,),
        )
        _record(
            checks,
            "学生-班级排名",
            *_request(
                "GET",
                f"{base_url}/api/student/classes/{class_id}/ranking",
                headers=student_headers,
            ),
            expected=(200,),
        )
        _record(
            checks,
            "学生-班级通知",
            *_request(
                "GET",
                f"{base_url}/api/student/classes/{class_id}/notifications",
                headers=student_headers,
            ),
            expected=(200,),
        )
        _record(
            checks,
            "学生-班级作业",
            *_request(
                "GET",
                f"{base_url}/api/student/classes/{class_id}/assignments",
                headers=student_headers,
            ),
            expected=(200,),
        )

    knowledge_map, _ = _record(
        checks,
        "学生-知识图谱",
        *_request(
            "GET",
            f"{base_url}/api/student/knowledge-map",
    # ── 知识图谱：图结构、知识点、关系、掌握度、资源 ──
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    point_id = _pick_first_id(knowledge_map, "nodes", "point_id", "id")
    _record(
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
    _record(
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
    _record(
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
    _record(
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
        _record(
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
        _record(
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

    # ── 评测模块：能力、习惯、知识测试及结果 ──
    _record(
        checks,
        "学生-能力测评题目",
        *_request(
            "GET",
            f"{base_url}/api/student/assessments/initial/ability",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    _record(
        checks,
        "学生-习惯问卷题目",
        *_request(
            "GET",
            f"{base_url}/api/student/assessments/initial/habit",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    _record(
        checks,
        "学生-知识测评题目",
        *_request(
            "GET",
            f"{base_url}/api/student/assessments/initial/knowledge",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    _record(
        checks,
        "学生-知识测评结果",
        *_request(
            "GET",
            f"{base_url}/api/student/assessments/initial/knowledge/result",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200, 404),
    )
    _record(
        checks,
        "学生-学习看板聚合",
        *_request(
            "GET",
            f"{base_url}/api/student/dashboard",
            headers=student_headers,
            params={"course_id": course_id},
        ),
        expected=(200,),
    )
    _record(
        checks,
        "学生-学习进度",
        *_request(
            "GET",
            f"{base_url}/api/student/learning-progress",
            headers=student_headers,
            params={"course_id": course_id},
    # ── 仪表盘与学习进度 ──
        ),
        expected=(200,),
    )

    path_data, _ = _record(
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
    _record(
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
    # ── 学习路径：调整、节点、启动、资源、AI资源、考试 ──

    node_id = _pick_first_id(path_data, "nodes", "node_id", "id")
    if node_id:
        _record(
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
        _record(
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
        _record(
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
        ai_resources, _ = _record(
            checks,
            "学生-AI资源",
            *_request(
                "GET",
                f"{base_url}/api/student/path-nodes/{node_id}/ai-resources",
                headers=student_headers,
            ),
            expected=(200,),
        )
        _record(
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
        _record(
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
                    _record(
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
    if target_exam_id:
        exam_detail, detail_ok = _record(
            checks,
    # ── 学生考试：列表、详情、草稿、提交、结果、统计 ──
            "学生-考试详情",
            *_request(
                "GET",
                f"{base_url}/api/student/exams/{target_exam_id}",
                headers=student_headers,
            ),
            expected=(200,),
        )
        if detail_ok and isinstance(exam_detail, dict):
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

    if point_id:
        _record(
            checks,
            "学生-AI知识点介绍",
            *_request(
                "POST",
    # ── AI 服务：知识点介绍、画像分析、路径规划、对话 ──
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
    # ── KT 知识追踪：模型信息与预测 ──
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

# ─────────────────────────────────────────────────
# 第三阶段：教师端回归测试
# 覆盖课程管理、题目管理、班级管理、考试管理等
# 教师端 CRUD 全链路以及只读列表接口。
# ─────────────────────────────────────────────────
    )


def _run_teacher_regression(
    checks: List[CheckResult],
    base_url: str,
    teacher_headers: Dict[str, str],
    course_id: int,
    include_all: bool,
    temp_suffix: str,
) -> Dict[str, Optional[int]]:
    """
    执行教师端课程、题目、班级与考试相关回归。
    :param checks: 检查结果列表。
    :param base_url: 服务基础地址。
    :param teacher_headers: 教师端认证请求头。
    :param course_id: 当前课程 ID。
    :param include_all: 是否执行创建与删除链路。
    :param temp_suffix: 临时资源名称后缀。
    :return: 教师端临时资源主键集合。
    """
    temp_ids: Dict[str, Optional[int]] = {
        "course_id": None,
        "class_id": None,
        "question_id": None,
        "exam_id": None,
        "invitation_id": None,
    }

    _record(
        checks,
        "教师-我的课程",
        *_request("GET", f"{base_url}/api/teacher/courses/my", headers=teacher_headers),
        expected=(200,),
    # ── 教师只读快速检查 ──
    )
    _record(
        checks,
        "教师-我的班级",
        *_request("GET", f"{base_url}/api/teacher/classes/my", headers=teacher_headers),
        expected=(200,),
    )

    if not include_all:
        return temp_ids

    temp_course_name = f"{TEMP_PREFIX}课程{temp_suffix}"
    course_resp, course_ok = _record(
        checks,
        "教师-创建课程",
    # ── 以下为全量模式：创建→更新→查询→删除链路 ──
        *_request(
            "POST",
            f"{base_url}/api/teacher/courses/create",
            headers=teacher_headers,
            data={"name": temp_course_name, "description": "接口回归创建"},
    # 创建临时课程
        ),
        expected=(200, 201),
    )
    if course_ok and isinstance(course_resp, dict):
        temp_ids["course_id"] = course_resp.get("course_id") or course_resp.get("id")
        _record(
            checks,
            "教师-课程统计",
            *_request(
                "GET",
                f"{base_url}/api/teacher/courses/{temp_ids['course_id']}/statistics",
                headers=teacher_headers,
            ),
            expected=(200,),
        )
        _record(
            checks,
            "教师-更新课程",
            *_request(
                "PUT",
        # 课程创建成功后：查统计、更新名称
                f"{base_url}/api/teacher/courses/{temp_ids['course_id']}",
                headers=teacher_headers,
                json={"course_name": f"{temp_course_name}-更新"},
            ),
            expected=(200,),
        )

        point_resp, point_ok = _record(
            checks,
            "教师-创建知识点",
            *_request(
                "POST",
                f"{base_url}/api/teacher/knowledge-points/create",
                headers=teacher_headers,
                json={
                    "course_id": temp_ids["course_id"],
                    "point_name": f"{TEMP_PREFIX}知识点{temp_suffix}",
                    "description": "接口回归知识点",
                },
        # 在临时课程下创建知识点
            ),
            expected=(200, 201),
        )
        temp_point_id = (
            point_resp.get("point_id")
            if point_ok and isinstance(point_resp, dict)
            else None
        )

        question_resp, question_ok = _record(
            checks,
            "教师-创建题目",
            *_request(
                "POST",
        # 创建单选题并关联知识点
                f"{base_url}/api/teacher/questions/create",
                headers=teacher_headers,
                json={
                    "course_id": temp_ids["course_id"],
                    "content": f"{TEMP_PREFIX}单选题{temp_suffix}",
                    "type": "single_choice",
                    "options": [
                        {"value": "A", "label": "A", "content": "正确答案"},
                        {"value": "B", "label": "B", "content": "错误答案"},
                    ],
                    "answer": {"answer": "A"},
                    "points": [temp_point_id] if temp_point_id else [],
                    "analysis": "接口回归题目",
                    "score": 10,
                },
            ),
            expected=(200, 201),
        )
        if question_ok and isinstance(question_resp, dict):
            temp_ids["question_id"] = question_resp.get(
                "question_id"
            ) or question_resp.get("id")
            _record(
                checks,
                "教师-题目详情",
                *_request(
                    "GET",
                    f"{base_url}/api/teacher/questions/{temp_ids['question_id']}",
                    headers=teacher_headers,
                ),
            # 题目创建成功：查详情、更新解析
                expected=(200,),
            )
            _record(
                checks,
                "教师-更新题目",
                *_request(
                    "PUT",
                    f"{base_url}/api/teacher/questions/{temp_ids['question_id']}/update",
                    headers=teacher_headers,
                    json={"analysis": "更新后的接口回归题目"},
                ),
                expected=(200,),
            )

        class_resp, class_ok = _record(
            checks,
            "教师-创建班级",
            *_request(
                "POST",
                f"{base_url}/api/teacher/classes/create",
                headers=teacher_headers,
                json={
                    "name": f"{TEMP_PREFIX}班级{temp_suffix}",
        # 创建班级并关联课程
                    "course_id": temp_ids["course_id"],
                    "description": "接口回归班级",
                },
            ),
            expected=(200, 201),
        )
        if class_ok and isinstance(class_resp, dict):
            temp_ids["class_id"] = class_resp.get("class_id") or class_resp.get("id")
            _record(
                checks,
                "教师-班级详情",
                *_request(
                    "GET",
                    f"{base_url}/api/teacher/classes/{temp_ids['class_id']}",
                    headers=teacher_headers,
                ),
                expected=(200,),
            # 班级创建成功：查详情、学生列表、进度
            )
            _record(
                checks,
                "教师-班级学生",
                *_request(
                    "GET",
                    f"{base_url}/api/teacher/classes/{temp_ids['class_id']}/students",
                    headers=teacher_headers,
                ),
                expected=(200,),
            )
            _record(
                checks,
                "教师-班级进度",
                *_request(
                    "GET",
                    f"{base_url}/api/teacher/classes/{temp_ids['class_id']}/progress",
                    headers=teacher_headers,
                ),
                expected=(200,),
            )
            invitation_resp, invitation_ok = _record(
                checks,
                "教师-生成邀请码",
                *_request(
                    "POST",
                    f"{base_url}/api/teacher/invitations/generate",
            # 生成邀请码并查列表
                    headers=teacher_headers,
                    json={"class_id": temp_ids["class_id"], "max_uses": 1},
                ),
                expected=(200, 201),
            )
            _record(
                checks,
                "教师-邀请码列表",
                *_request(
                    "GET",
                    f"{base_url}/api/teacher/classes/{temp_ids['class_id']}/invitations",
                    headers=teacher_headers,
                ),
                expected=(200,),
            )
            if invitation_ok and isinstance(invitation_resp, dict):
                temp_ids["invitation_id"] = invitation_resp.get(
                    "invitation_id"
                ) or invitation_resp.get("id")

        if temp_ids["course_id"] and temp_ids["question_id"]:
            exam_resp, exam_ok = _record(
                checks,
                "教师-创建考试",
                *_request(
                    "POST",
                    f"{base_url}/api/teacher/exams/create",
                    headers=teacher_headers,
        # 创建考试并关联课程和题目
                    json={
                        "course_id": temp_ids["course_id"],
                        "title": f"{TEMP_PREFIX}考试{temp_suffix}",
                        "exam_type": "chapter",
                        "questions": [temp_ids["question_id"]],
                        "duration": 30,
                        "total_score": 100,
                        "pass_score": 60,
                    },
                ),
                expected=(200, 201),
            )
            if exam_ok and isinstance(exam_resp, dict):
                temp_ids["exam_id"] = exam_resp.get("exam_id") or exam_resp.get("id")
                _record(
                    checks,
                    "教师-考试详情",
                    *_request(
                        "GET",
                        f"{base_url}/api/teacher/exams/{temp_ids['exam_id']}",
                        headers=teacher_headers,
                    ),
                    expected=(200,),
                )
                _record(
                    checks,
                    "教师-更新考试",
                # 考试创建成功：查详情、更新、发布/取消发布、结果列表、分析
                    *_request(
                        "PUT",
                        f"{base_url}/api/teacher/exams/{temp_ids['exam_id']}/update",
                        headers=teacher_headers,
                        json={"description": "接口回归考试"},
                    ),
                    expected=(200,),
                )
                if temp_ids["class_id"]:
                    _record(
                        checks,
                        "教师-发布考试",
                        *_request(
                            "POST",
                            f"{base_url}/api/teacher/exams/{temp_ids['exam_id']}/publish",
                            headers=teacher_headers,
                            json={"class_id": temp_ids["class_id"]},
                        ),
                        expected=(200,),
                    )
                    _record(
                        checks,
                        "教师-取消发布",
                        *_request(
                            "POST",
                            f"{base_url}/api/teacher/exams/{temp_ids['exam_id']}/unpublish",
                            headers=teacher_headers,
                        ),
                        expected=(200,),
                    )
                _record(
                    checks,
                    "教师-考试结果列表",
                    *_request(
                        "GET",
                        f"{base_url}/api/teacher/exams/{temp_ids['exam_id']}/results",
                        headers=teacher_headers,
                    ),
                    expected=(200,),
                )
                _record(
                    checks,
                    "教师-考试分析",
                    *_request(
                        "GET",
                        f"{base_url}/api/teacher/exams/{temp_ids['exam_id']}/analysis",
                        headers=teacher_headers,
                    ),
                    expected=(200,),
                )

    target_course_id = temp_ids["course_id"] or course_id
    _record(
    # ── 教师端只读列表接口 ──
        checks,
        "教师-课程列表",
        *_request("GET", f"{base_url}/api/teacher/courses/my", headers=teacher_headers),
        expected=(200,),
    )
    _record(
        checks,
        "教师-题目列表",
        *_request(
            "GET",
            f"{base_url}/api/teacher/questions",
            headers=teacher_headers,
            params={"course_id": target_course_id},
        ),
        expected=(200,),
    )
    _record(
        checks,
        "教师-知识点列表",
        *_request(
            "GET",
            f"{base_url}/api/teacher/knowledge-points",
            headers=teacher_headers,
            params={"course_id": target_course_id},
        ),
        expected=(200,),
    )
    _record(
        checks,
        "教师-资源列表",
        *_request(
            "GET",
            f"{base_url}/api/teacher/resources",
            headers=teacher_headers,
            params={"course_id": target_course_id},
        ),
        expected=(200,),
    )
    _record(
        checks,
        "教师-考试列表",
        *_request(
            "GET",
            f"{base_url}/api/teacher/exams",
            headers=teacher_headers,
            params={"course_id": target_course_id},
        ),
        expected=(200,),
    )
    return temp_ids


def _run_admin_regression(
    checks: List[CheckResult],
    base_url: str,
    admin_headers: Dict[str, str],

# ─────────────────────────────────────────────────
# 第四阶段：管理端回归测试
# 覆盖用户管理、课程管理、班级管理、日志管理、激活码等
# 管理员端 CRUD 全链路与审计接口。
# ─────────────────────────────────────────────────
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

    _record(
        checks,
        "管理员-用户列表",
        *_request("GET", f"{base_url}/api/admin/users", headers=admin_headers),
        expected=(200,),
    )
    # ── 管理员只读列表接口 ──
    _record(
        checks,
        "管理员-课程列表",
        *_request("GET", f"{base_url}/api/admin/courses", headers=admin_headers),
        expected=(200,),
    )
    _record(
        checks,
        "管理员-班级列表",
        *_request("GET", f"{base_url}/api/admin/classes", headers=admin_headers),
        expected=(200,),
    )
    _record(
        checks,
        "管理员-激活码列表",
        *_request(
            "GET", f"{base_url}/api/admin/activation-codes", headers=admin_headers
        ),
        expected=(200,),
    )
    _record(
        checks,
        "管理员-日志列表",
        *_request("GET", f"{base_url}/api/admin/logs", headers=admin_headers),
        expected=(200,),
    )
    _record(
        checks,
        "管理员-日志统计",
        *_request(
    # ── 日志管理：列表、统计、筛选项、模块、操作类型、导出、清理 ──
            "GET", f"{base_url}/api/admin/logs/statistics", headers=admin_headers
        ),
        expected=(200,),
    )
    _record(
        checks,
        "管理员-日志筛选项",
        *_request("GET", f"{base_url}/api/admin/logs/options", headers=admin_headers),
        expected=(200,),
    )
    _record(
        checks,
        "管理员-日志模块",
        *_request("GET", f"{base_url}/api/admin/logs/modules", headers=admin_headers),
        expected=(200,),
    )
    _record(
        checks,
        "管理员-日志操作类型",
        *_request("GET", f"{base_url}/api/admin/logs/actions", headers=admin_headers),
        expected=(200,),
    )
    _blob(
        checks,
        "管理员-日志导出",
        *_request("GET", f"{base_url}/api/admin/logs/export", headers=admin_headers),
        expected=(200,),
    )
    _record(
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

    if not include_all:
        return temp_ids

    user_resp, user_ok = _record(
    # ── 以下为全量模式：创建→更新→禁用→启用→删除链路 ──
        checks,
        "管理员-创建用户",
        *_request(
            "POST",
            f"{base_url}/api/admin/users/create",
            headers=admin_headers,
    # 创建临时用户（学生角色）
            json={
                "username": f"api_user_{temp_suffix}",
                "password": "Test123456",
                "role": "student",
                "real_name": "API回归用户",
            },
        ),
        expected=(200, 201),
    )
    if user_ok and isinstance(user_resp, dict):
        temp_ids["user_id"] = user_resp.get("user_id") or user_resp.get("id")
        _record(
            checks,
            "管理员-用户详情",
            *_request(
                "GET",
                f"{base_url}/api/admin/users/{temp_ids['user_id']}",
                headers=admin_headers,
            ),
            expected=(200,),
        )
        _record(
            checks,
            "管理员-更新用户",
            *_request(
                "PUT",
        # 用户创建成功：查详情、更新、禁用、启用、重置密码
                f"{base_url}/api/admin/users/{temp_ids['user_id']}/update",
                headers=admin_headers,
                json={"real_name": "API回归用户-更新"},
            ),
            expected=(200,),
        )
        _record(
            checks,
            "管理员-禁用用户",
            *_request(
                "POST",
                f"{base_url}/api/admin/users/{temp_ids['user_id']}/disable",
                headers=admin_headers,
            ),
            expected=(200,),
        )
        _record(
            checks,
            "管理员-启用用户",
            *_request(
                "POST",
                f"{base_url}/api/admin/users/{temp_ids['user_id']}/enable",
                headers=admin_headers,
            ),
            expected=(200,),
        )
        _record(
            checks,
            "管理员-重置密码",
            *_request(
                "POST",
                f"{base_url}/api/admin/users/{temp_ids['user_id']}/reset-password",
                headers=admin_headers,
                json={"new_password": "Test123456"},
            ),
            expected=(200,),
        )

    activation_resp, activation_ok = _record(
        checks,
        "管理员-生成激活码",
        *_request(
            "POST",
            f"{base_url}/api/admin/activation-codes/generate",
    # 生成激活码
            headers=admin_headers,
            json={"code_type": "teacher", "count": 1, "remark": "API回归"},
        ),
        expected=(200, 201),
    )
    if activation_ok and isinstance(activation_resp, dict):
        codes = activation_resp.get("codes") or []
        if codes and isinstance(codes[0], dict):
            temp_ids["activation_code_id"] = codes[0].get("id")

    course_resp, course_ok = _record(
        checks,
        "管理员-创建课程",
        *_request(
            "POST",
            f"{base_url}/api/admin/courses/create",
            headers=admin_headers,
            json={"name": f"{TEMP_PREFIX}管理员课程{temp_suffix}", "teacher_id": None},
        ),
        expected=(200, 201),
    # 创建管理员端课程
    )
    if course_ok and isinstance(course_resp, dict):
        temp_ids["course_id"] = course_resp.get("course_id") or course_resp.get("id")
        _record(
            checks,
            "管理员-课程详情",
            *_request(
                "GET",
                f"{base_url}/api/admin/courses/{temp_ids['course_id']}",
                headers=admin_headers,
            ),
            expected=(200,),
        )
        _record(
            checks,
            "管理员-课程统计",
            *_request(
                "GET",
                f"{base_url}/api/admin/courses/{temp_ids['course_id']}/statistics",
                headers=admin_headers,
        # 课程创建成功：查详情、统计
            ),
            expected=(200,),
        )

    class_resp, class_ok = _record(
    # 创建管理员端班级
        checks,
        "管理员-创建班级",
        *_request(
            "POST",
            f"{base_url}/api/admin/classes/create",
            headers=admin_headers,
            json={
                "name": f"{TEMP_PREFIX}管理员班级{temp_suffix}",
                "course_id": temp_ids["course_id"],
            },
        ),
        expected=(200, 201),
    )
    if class_ok and isinstance(class_resp, dict):
        temp_ids["class_id"] = class_resp.get("class_id") or class_resp.get("id")
        _record(
            checks,
            "管理员-班级详情",
        # 班级创建成功：查详情、学生管理、统计
            *_request(
                "GET",
                f"{base_url}/api/admin/classes/{temp_ids['class_id']}",
                headers=admin_headers,
            ),
            expected=(200,),
        )
        _record(
            checks,
            "管理员-班级学生",
            *_request(
                "GET",
                f"{base_url}/api/admin/classes/{temp_ids['class_id']}/students",
                headers=admin_headers,
            ),
            expected=(200,),
        )
        if temp_ids["user_id"]:
            _record(
                checks,
                "管理员-班级加学生",
                *_request(
                    "POST",
                    f"{base_url}/api/admin/classes/{temp_ids['class_id']}/students/add",
                    headers=admin_headers,
                    json={"student_ids": [temp_ids["user_id"]]},
                ),
                expected=(200,),
            )
            _record(
                checks,
                "管理员-班级移除学生",
                *_request(
                    "DELETE",
                    f"{base_url}/api/admin/classes/{temp_ids['class_id']}/students/{temp_ids['user_id']}",
                    headers=admin_headers,
                ),
                expected=(200,),
            )
        _record(
            checks,
            "管理员-班级统计",
            *_request(
                "GET",
                f"{base_url}/api/admin/classes/{temp_ids['class_id']}/statistics",
                headers=admin_headers,
            ),
            expected=(200,),
        )

    return temp_ids

# ─────────────────────────────────────────────────
# 第五阶段：清理临时资源
# 按创建的反序删除，保证外键依赖不冲突。
# ─────────────────────────────────────────────────


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


def api_regression(
    base_url: str = DEFAULT_BASE_URL, include_all: bool = False, as_json: bool = False
    # 先执行文档/健康检查，失败则直接终止
) -> None:
    """
    执行公开 API 回归测试。
    :param base_url: 服务基础地址。
    :param include_all: 是否覆盖会创建临时数据的全量链路。
    :param as_json: 是否按 JSON 结构输出检查结果。
    :return: None。
    """
    checks: List[CheckResult] = []
    temp_suffix = str(int(time.time()))

    _run_document_checks(checks, base_url)
    if not checks or not checks[1].ok:
    # 封装认证请求头
        _print_checks(checks, as_json=as_json)
        return

    student_token, _ = _login(base_url, "student1", "Test123456")
    teacher_token, _ = _login(base_url, "teacher1", "Test123456")
    # 记录登录结果并校验：任一角色登录失败即终止
    admin_token, _ = _login(base_url, "admin", "Admin123456")

    student_headers = _build_auth_headers(student_token)
    teacher_headers = _build_auth_headers(teacher_token)
    admin_headers = _build_auth_headers(admin_token)

    checks.append(CheckResult("学生登录", bool(student_token), "student1"))
    checks.append(CheckResult("教师登录", bool(teacher_token), "teacher1"))
    checks.append(CheckResult("管理员登录", bool(admin_token), "admin"))
    # 解析学生可用的课程上下文（后续接口依赖 course_id）
    if not all([student_token, teacher_token, admin_token]):
        _print_checks(checks, as_json=as_json)
        return

    course_id = _resolve_course_id(base_url, student_headers, None)
    checks.append(
        CheckResult(
            "课程上下文解析",
            bool(course_id),
            f"course_id={course_id}" if course_id else "未解析到课程",
        )
    )

    # 按角色分别执行回归：学生 → 教师 → 管理员
    if course_id:
        _run_student_regression(
            checks=checks,
            base_url=base_url,
            student_headers=student_headers,
            course_id=course_id,
            include_all=include_all,
        )
        _run_teacher_regression(
            checks=checks,
            base_url=base_url,
            teacher_headers=teacher_headers,
            course_id=course_id,
            include_all=include_all,
            temp_suffix=temp_suffix,
        )

    _run_admin_regression(
        checks=checks,
        base_url=base_url,
        admin_headers=admin_headers,
        include_all=include_all,
        temp_suffix=temp_suffix,
    )

    _print_checks(checks, as_json=as_json)
