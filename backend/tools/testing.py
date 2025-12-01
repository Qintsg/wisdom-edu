"""测试基础设施。

包含 HTTP 请求封装、登录认证、数据提取、测试数据加载等测试用基础设施。
从原 tests/helpers.py 迁移而来。
"""

import json
import re
import sys
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

import requests

from tools.common import BASE_DIR

# ── 常量 ──────────────────────────────────────────────────
TESTDATA_FILE = BASE_DIR / 'tools' / 'testdata.json5'


def _supports_unicode_output() -> bool:
    """判断当前终端是否支持直接输出 Unicode 状态符号。"""
    encoding = (sys.stdout.encoding or '').lower()
    return 'utf' in encoding


def _status_flag(ok: bool) -> str:
    """根据检查结果返回终端友好的状态标记。"""
    if _supports_unicode_output():
        return '✅' if ok else '❌'
    return '[OK]' if ok else '[FAIL]'


# ── 数据类 ────────────────────────────────────────────────
@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str = ''
    status_code: Optional[int] = None


# ── 输出 ──────────────────────────────────────────────────
def _print_checks(checks: List[CheckResult], as_json: bool = False):
    """打印测试检查结果。

    以可读的格式或JSON格式输出测试检查结果列表，包括成功/失败统计。

    Args:
        checks (List[CheckResult]): 检查结果对象列表
        as_json (bool): 是否以JSON格式输出，默认False使用友好格式
    """
    if as_json:
        output = [asdict(check) for check in checks]
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print('\n==== 测试结果 ====')
    fail = 0
    for item in checks:
        flag = _status_flag(item.ok)
        suffix = f' (status={item.status_code})' if item.status_code is not None else ''
        print(f'{flag} {item.name}{suffix}: {item.detail}')
        if not item.ok:
            fail += 1

    print('==================')
    if fail:
        print(f'失败项: {fail}')
    else:
        print('全部通过')


# ── HTTP 请求封装 ─────────────────────────────────────────
def _request(
    method: str,
    url: str,
    **kwargs,
) -> Tuple[Optional[requests.Response], Optional[str]]:
    """执行HTTP请求并捕获异常。

    Args:
        method (str): HTTP方法，如'GET', 'POST', 'PUT', 'DELETE'等
        url (str): 请求的完整URL
        **kwargs: 传递给requests.request的其他参数

    Returns:
        Tuple[Optional[requests.Response], Optional[str]]:
            成功时返回(Response, None)，失败时返回(None, 错误信息)
    """
    try:
        timeout = kwargs.pop('timeout', 12)
        response = requests.request(method, url, timeout=timeout, **kwargs)
        return response, None
    except Exception as exc:
        return None, str(exc)


def _extract_data(resp: requests.Response) -> Any:
    """从响应中提取data字段。

    尝试解析JSON响应，并提取'data'字段，兼容不同的响应格式。

    Args:
        resp (requests.Response): HTTP响应对象

    Returns:
        Any: 提取的数据，可能是字典、列表或None
    """
    try:
        payload = resp.json()
    except ValueError:
        return None

    if isinstance(payload, dict):
        return payload.get('data', payload)
    return payload


# ── 登录认证 ──────────────────────────────────────────────
def _login(
    base_url: str,
    username: str,
    password: str,
) -> Tuple[Optional[str], CheckResult]:
    """执行用户登录并获取认证令牌。

    Args:
        base_url (str): API基础URL
        username (str): 用户名
        password (str): 密码

    Returns:
        Tuple[Optional[str], CheckResult]: (token, 检查结果)
    """
    resp, err = _request(
        'POST',
        f'{base_url}/api/auth/login',
        json={'username': username, 'password': password},
        timeout=15,
    )
    if err:
        return None, CheckResult('登录接口', False, err)
    if resp is None:
        return None, CheckResult('登录接口', False, '无响应对象')

    data = _extract_data(resp) or {}
    token = None
    if isinstance(data, dict):
        token = data.get('token') or data.get('access')

    ok = resp.status_code == 200 and bool(token)
    detail = '登录成功' if ok else '登录失败'
    return token, CheckResult('登录接口', ok, detail, status_code=resp.status_code)


# ── 课程 ID 解析 ─────────────────────────────────────────
def _resolve_course_id(
    base_url: str,
    headers: Dict[str, str],
    fallback: Optional[int],
) -> Optional[int]:
    """解析获取课程ID。

    如果提供了fallback课程ID则直接返回，否则调用课程列表API获取第一个课程ID。

    Args:
        base_url (str): API基础URL
        headers (Dict[str, str]): 请求头（需包含认证信息）
        fallback (Optional[int]): 备用课程ID

    Returns:
        Optional[int]: 课程ID，解析失败返回None
    """
    if fallback:
        return fallback

    resp, err = _request('GET', f'{base_url}/api/courses', headers=headers)
    if err or not resp or resp.status_code != 200:
        return None

    data = _extract_data(resp)
    courses: list[Any] = []
    if isinstance(data, dict):
        courses_data = data.get('courses', [])
        if isinstance(courses_data, list):
            courses = courses_data
    elif isinstance(data, list):
        courses = data

    if not courses:
        return None

    first_course = courses[0]
    if not isinstance(first_course, dict):
        return None

    course_id = first_course.get('course_id') or first_course.get('id')
    if course_id is None:
        return None

    try:
        return int(course_id)
    except (TypeError, ValueError):
        return None


# ── 测试数据加载 ─────────────────────────────────────────
def _load_testdata() -> Optional[dict]:
    """加载并解析testdata.json5测试数据文件。

    支持JSON5格式（允许注释和尾逗号）。

    Returns:
        Optional[dict]: 解析后的测试数据字典，加载失败返回None
    """
    if not TESTDATA_FILE.exists():
        print(f'  {_status_flag(False)} 测试数据文件不存在: {TESTDATA_FILE}')
        return None

    try:
        content = TESTDATA_FILE.read_text(encoding='utf-8')
        lines = []

        for line in content.split('\n'):
            in_string = False
            output_chars = []
            index = 0
            while index < len(line):
                # 只在字符串外剥离 // 注释，避免误伤 URL 或文本内容。
                if line[index] == '"' and (index == 0 or line[index - 1] != '\\'):
                    in_string = not in_string
                if not in_string and line[index:index + 2] == '//':
                    break
                output_chars.append(line[index])
                index += 1
            lines.append(''.join(output_chars))

        clean = re.sub(r',(\s*[}\]])', r'\1', '\n'.join(lines))
        return json.loads(clean)
    except Exception as exc:
        print(f'  {_status_flag(False)} 加载测试数据失败: {exc}')
        return None
