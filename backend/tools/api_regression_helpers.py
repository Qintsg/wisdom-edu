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
