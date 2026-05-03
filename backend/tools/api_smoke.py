"""API 烟雾测试和业务流程回归测试。

包含基础API端点验证、学生关键学习链路专项回归、业务逻辑组合测试。
从原 tests/api_smoke.py 迁移而来。
"""

from typing import List, Optional

from tools.testing import (
    CheckResult,
    _extract_data,
    _login,
    _print_checks,
    _request,
    _resolve_course_id,
)


# 维护意图：执行 API 烟雾测试
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def api_smoke(
    base_url: str,
    username: str,
    password: str,
    strict: bool = False,
    as_json: bool = False,
):
    """执行 API 烟雾测试。"""
    checks: List[CheckResult] = []

    # 健康检查
    resp, err = _request('GET', f'{base_url}/health/')
    if err:
        checks.append(CheckResult('健康检查', False, err))
        _print_checks(checks, as_json=as_json)
        return
    if resp is None:
        checks.append(CheckResult('健康检查', False, '无响应对象'))
        _print_checks(checks, as_json=as_json)
        return

    ok = resp.status_code == 200
    checks.append(
        CheckResult(
            '健康检查',
            ok,
            'ok' if ok else 'unexpected',
            status_code=resp.status_code,
        )
    )

    # 登录认证
    token, login_check = _login(base_url, username, password)
    checks.append(login_check)
    headers = {'Authorization': f'Bearer {token}'} if token else {}

    # 用户信息接口
    resp, err = _request('GET', f'{base_url}/api/auth/userinfo', headers=headers)
    if err:
        checks.append(CheckResult('用户信息接口', False, err))
    elif resp is not None:
        ok = resp.status_code == 200
        checks.append(
            CheckResult(
                '用户信息接口',
                ok,
                'ok' if ok else 'unexpected',
                status_code=resp.status_code,
            )
        )
    else:
        checks.append(CheckResult('用户信息接口', False, '无响应对象'))

    # 测评状态接口
    resp, err = _request('GET', f'{base_url}/api/student/assessments/status', headers=headers)
    if err:
        checks.append(CheckResult('测评状态接口', False, err))
    elif resp is not None:
        ok = resp.status_code == 200
        checks.append(
            CheckResult(
                '测评状态接口',
                ok,
                'ok' if ok else 'unexpected',
                status_code=resp.status_code,
            )
        )
    else:
        checks.append(CheckResult('测评状态接口', False, '无响应对象'))

    # 严格模式：学习路径接口
    if strict:
        resp, err = _request('GET', f'{base_url}/api/student/learning-path', headers=headers)
        if err:
            checks.append(CheckResult('学习路径接口(严格)', False, err))
        elif resp is not None:
            ok = resp.status_code in [200, 400]
            checks.append(
                CheckResult(
                    '学习路径接口(严格)',
                    ok,
                    '允许200/400',
                    status_code=resp.status_code,
                )
            )
        else:
            checks.append(CheckResult('学习路径接口(严格)', False, '无响应对象'))

    _print_checks(checks, as_json=as_json)


# 维护意图：执行学生关键业务流程回归测试
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def student_flow_smoke(
    base_url: str,
    username: str,
    password: str,
    course_id: Optional[int],
    as_json: bool = False,
):
    """执行学生关键业务流程回归测试。"""
    checks: List[CheckResult] = []

    # 登录认证
    token, login_check = _login(base_url, username, password)
    checks.append(login_check)
    headers = {'Authorization': f'Bearer {token}'} if token else {}

    resolved_course_id = _resolve_course_id(base_url, headers, course_id)
    if not resolved_course_id:
        checks.append(
            CheckResult(
                '课程ID解析',
                False,
                '无法解析课程ID，请显式传 --course-id',
            )
        )
        _print_checks(checks, as_json=as_json)
        return

    checks.append(CheckResult('课程ID解析', True, f'course_id={resolved_course_id}'))

    # 初始知识测评接口
    resp, err = _request(
        'GET',
        f'{base_url}/api/student/assessments/initial/knowledge',
        headers=headers,
        params={'course_id': resolved_course_id},
    )
    if err:
        checks.append(CheckResult('初始知识测评接口', False, err))
    elif resp is not None:
        ok = resp.status_code in [200, 400]
        checks.append(
            CheckResult(
                '初始知识测评接口',
                ok,
                '允许200/400（关键是不能500）',
                status_code=resp.status_code,
            )
        )
    else:
        checks.append(CheckResult('初始知识测评接口', False, '无响应对象'))

    # 学习路径接口
    resp, err = _request(
        'GET',
        f'{base_url}/api/student/learning-path',
        headers=headers,
        params={'course_id': resolved_course_id},
    )
    node_id = None
    if err:
        checks.append(CheckResult('学习路径接口', False, err))
    elif resp is not None:
        ok = resp.status_code in [200, 400]
        checks.append(
            CheckResult(
                '学习路径接口',
                ok,
                '允许200/400（关键是不能500）',
                status_code=resp.status_code,
            )
        )
        data = _extract_data(resp)
        if isinstance(data, dict):
            nodes = data.get('nodes', [])
            if isinstance(nodes, list) and nodes and isinstance(nodes[0], dict):
                node_id = nodes[0].get('node_id') or nodes[0].get('id')
    else:
        checks.append(CheckResult('学习路径接口', False, '无响应对象'))

    # 节点详情接口
    if node_id:
        resp, err = _request('GET', f'{base_url}/api/student/path-nodes/{node_id}', headers=headers)
        if err:
            checks.append(CheckResult('节点详情接口(无course_id)', False, err))
        elif resp is not None:
            ok = resp.status_code in [200, 400, 404]
            checks.append(
                CheckResult(
                    '节点详情接口(无course_id)',
                    ok,
                    '允许200/400/404（关键是不能500）',
                    status_code=resp.status_code,
                )
            )
        else:
            checks.append(CheckResult('节点详情接口(无course_id)', False, '无响应对象'))
    else:
        checks.append(CheckResult('节点详情接口(无course_id)', True, '无可用节点，跳过'))

    _print_checks(checks, as_json=as_json)


# 维护意图：执行完整业务逻辑测试（api-smoke + student-flow-smoke 的快捷方式）
# 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
# 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
def test_business_logic():
    """执行完整业务逻辑测试（api-smoke + student-flow-smoke 的快捷方式）。"""
    print('说明：完整业务逻辑测试建议使用 api-smoke + student-flow-smoke 组合。')
    api_smoke('http://127.0.0.1:8000', 'student1', 'Test123456', strict=True, as_json=False)
