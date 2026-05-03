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

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
TEMP_PREFIX = "[API回归]"


# 维护意图：记录普通 JSON 接口检查结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def record_check(
    checks: List[CheckResult],
    name: str,
    resp,
    err: Optional[str],
    expected: Tuple[int, ...] = (200,),
    detail: Optional[str] = None,
) -> Tuple[Optional[Any], bool]:
    """记录普通 JSON 接口检查结果。"""
    if err:
        checks.append(CheckResult(name, False, err))
        return None, False
    if resp is None:
        checks.append(CheckResult(name, False, "无响应对象"))
        return None, False

    ok = resp.status_code in expected
    payload = _extract_data(resp)
    success_detail = detail or ("ok" if ok else f"unexpected={resp.status_code}")
    checks.append(CheckResult(name, ok, success_detail, status_code=resp.status_code))
    return payload, ok


# 维护意图：记录二进制导出接口检查结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def record_blob_check(
    checks: List[CheckResult],
    name: str,
    resp,
    err: Optional[str],
    expected: Tuple[int, ...] = (200,),
) -> bool:
    """记录二进制导出接口检查结果。"""
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


# 维护意图：提取题目选项中可提交的答案值
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def first_option_value(option: object) -> Any:
    """提取题目选项中可提交的答案值。"""
    if isinstance(option, dict):
        return option.get("answer_value") or option.get("value") or option.get("key")
    return option


# 维护意图：构造单选或多选题的默认答案
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_choice_answer(options: list[object], *, multiple: bool) -> Any:
    """构造单选或多选题的默认答案。"""
    first_value = first_option_value(options[0]) if options else None
    if multiple:
        return [first_value] if first_value is not None else []
    return first_value or ""


# 维护意图：根据单题题型构造默认提交答案
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_question_answer(question: Dict[str, Any]) -> Any:
    """根据单题题型构造默认提交答案。"""
    question_type = question.get("type") or question.get("question_type")
    options = question.get("options") or []
    if question_type == "multiple_choice":
        return build_choice_answer(options, multiple=True)
    if question_type == "true_false":
        return "true"
    if question_type in {"single_choice", "single"}:
        return build_choice_answer(options, multiple=False)
    return "测试答案"


# 维护意图：根据试卷题型构造默认答题载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_exam_answers(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """根据试卷题型构造默认答题载荷。"""
    answers: Dict[str, Any] = {}
    for question in questions:
        question_id = str(question.get("question_id") or question.get("id"))
        answers[question_id] = build_question_answer(question)
    return answers


# 维护意图：读取 OpenAPI 文档中声明的路径列表
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_documented_paths() -> List[str]:
    """读取 OpenAPI 文档中声明的路径列表。"""
    api_doc = Path(__file__).resolve().parents[2] / "docs" / "api.yaml"
    if not api_doc.exists():
        return []
    try:
        text = api_doc.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    return [line.strip().rstrip(":") for line in text.splitlines() if re.match(r"^  /", line)]


# 维护意图：将登录 token 转换为 Bearer 认证头
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_auth_headers(token: Optional[str]) -> Dict[str, str]:
    """将登录 token 转换为 Bearer 认证头。"""
    return {"Authorization": f"Bearer {token}"} if token else {}


# 维护意图：从列表型接口返回中提取首个对象主键
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def pick_first_id(
    payload: Optional[Dict[str, Any]], list_key: str, *candidate_keys: str
) -> Optional[Any]:
    """从列表型接口返回中提取首个对象主键。"""
    if not isinstance(payload, dict):
        return None
    items = payload.get(list_key) or []
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


# 维护意图：执行健康检查与文档端点检查
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def run_document_checks(checks: List[CheckResult], base_url: str) -> None:
    """执行健康检查与文档端点检查。"""
    documented_paths = load_documented_paths()
    checks.append(CheckResult("API文档路径统计", True, f"documented_paths={len(documented_paths)}"))

    _, ok = record_check(
        checks,
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
        record_check(
            checks,
            f"文档接口-{name}",
            *_request("GET", f"{base_url}{path}"),
            expected=(200,),
        )
