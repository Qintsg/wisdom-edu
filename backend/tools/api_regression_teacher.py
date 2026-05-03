"""教师端公开 API 回归测试阶段实现。"""

from __future__ import annotations

from dataclasses import dataclass, field

from tools.api_regression_helpers import TEMP_PREFIX, record_check
from tools.testing import CheckResult, _request


TempIdMap = dict[str, int | None]


# 维护意图：教师端回归执行上下文
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass
class TeacherRegressionContext:
    """教师端回归执行上下文。"""

    checks: list[CheckResult]
    base_url: str
    teacher_headers: dict[str, str]
    course_id: int
    temp_suffix: str
    temp_ids: TempIdMap = field(
        default_factory=lambda: {
            "course_id": None,
            "class_id": None,
            "question_id": None,
            "exam_id": None,
            "invitation_id": None,
        }
    )


# 维护意图：执行教师端课程、题目、班级与考试相关回归。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _run_teacher_regression(
    checks: list[CheckResult],
    base_url: str,
    teacher_headers: dict[str, str],
    course_id: int,
    include_all: bool,
    temp_suffix: str,
) -> TempIdMap:
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
    context = TeacherRegressionContext(
        checks=checks,
        base_url=base_url,
        teacher_headers=teacher_headers,
        course_id=course_id,
        temp_suffix=temp_suffix,
    )
    _run_teacher_read_checks(context)
    if not include_all:
        return context.temp_ids

    _run_teacher_mutation_checks(context)
    _run_teacher_list_checks(context)
    return context.temp_ids


# 维护意图：执行教师端只读快速检查
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _run_teacher_read_checks(context: TeacherRegressionContext) -> None:
    """执行教师端只读快速检查。"""
    record_check_get(context, "教师-我的课程", "/api/teacher/courses/my")
    record_check_get(context, "教师-我的班级", "/api/teacher/classes/my")


# 维护意图：执行教师端创建、更新、发布和撤销链路
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _run_teacher_mutation_checks(context: TeacherRegressionContext) -> None:
    """执行教师端创建、更新、发布和撤销链路。"""
    _create_course(context)
    if context.temp_ids["course_id"]:
        point_id = _create_knowledge_point(context)
        _create_question(context, point_id)
        _create_class(context)
        _create_exam(context)


# 维护意图：创建临时课程并执行课程统计、更新检查
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _create_course(context: TeacherRegressionContext) -> None:
    """创建临时课程并执行课程统计、更新检查。"""
    temp_course_name = f"{TEMP_PREFIX}课程{context.temp_suffix}"
    response, ok = record_check_request(
        context,
        "教师-创建课程",
        "POST",
        "/api/teacher/courses/create",
        expected=(200, 201),
        data={"name": temp_course_name, "description": "接口回归创建"},
    )
    context.temp_ids["course_id"] = _response_id(response, ok, "course_id", "id")
    if not context.temp_ids["course_id"]:
        return

    course_path = f"/api/teacher/courses/{context.temp_ids['course_id']}"
    record_check_get(context, "教师-课程统计", f"{course_path}/statistics")
    record_check_request(
        context,
        "教师-更新课程",
        "PUT",
        course_path,
        expected=(200,),
        json={"course_name": f"{temp_course_name}-更新"},
    )


# 维护意图：在临时课程下创建知识点
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _create_knowledge_point(context: TeacherRegressionContext) -> int | None:
    """在临时课程下创建知识点。"""
    response, ok = record_check_request(
        context,
        "教师-创建知识点",
        "POST",
        "/api/teacher/knowledge-points/create",
        expected=(200, 201),
        json={
            "course_id": context.temp_ids["course_id"],
            "point_name": f"{TEMP_PREFIX}知识点{context.temp_suffix}",
            "description": "接口回归知识点",
        },
    )
    return _response_id(response, ok, "point_id", "id")


# 维护意图：创建临时单选题并验证详情与更新接口
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _create_question(context: TeacherRegressionContext, point_id: int | None) -> None:
    """创建临时单选题并验证详情与更新接口。"""
    response, ok = record_check_request(
        context,
        "教师-创建题目",
        "POST",
        "/api/teacher/questions/create",
        expected=(200, 201),
        json={
            "course_id": context.temp_ids["course_id"],
            "content": f"{TEMP_PREFIX}单选题{context.temp_suffix}",
            "type": "single_choice",
            "options": [
                {"value": "A", "label": "A", "content": "正确答案"},
                {"value": "B", "label": "B", "content": "错误答案"},
            ],
            "answer": {"answer": "A"},
            "points": [point_id] if point_id else [],
            "analysis": "接口回归题目",
            "score": 10,
        },
    )
    context.temp_ids["question_id"] = _response_id(response, ok, "question_id", "id")
    if not context.temp_ids["question_id"]:
        return

    question_path = f"/api/teacher/questions/{context.temp_ids['question_id']}"
    record_check_get(context, "教师-题目详情", question_path)
    record_check_request(
        context,
        "教师-更新题目",
        "PUT",
        f"{question_path}/update",
        expected=(200,),
        json={"analysis": "更新后的接口回归题目"},
    )


# 维护意图：创建临时班级，并验证详情、学生、进度和邀请码接口
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _create_class(context: TeacherRegressionContext) -> None:
    """创建临时班级，并验证详情、学生、进度和邀请码接口。"""
    response, ok = record_check_request(
        context,
        "教师-创建班级",
        "POST",
        "/api/teacher/classes/create",
        expected=(200, 201),
        json={
            "name": f"{TEMP_PREFIX}班级{context.temp_suffix}",
            "course_id": context.temp_ids["course_id"],
            "description": "接口回归班级",
        },
    )
    context.temp_ids["class_id"] = _response_id(response, ok, "class_id", "id")
    if not context.temp_ids["class_id"]:
        return

    class_path = f"/api/teacher/classes/{context.temp_ids['class_id']}"
    record_check_get(context, "教师-班级详情", class_path)
    record_check_get(context, "教师-班级学生", f"{class_path}/students")
    record_check_get(context, "教师-班级进度", f"{class_path}/progress")
    _create_invitation(context)
    record_check_get(context, "教师-邀请码列表", f"{class_path}/invitations")


# 维护意图：为临时班级生成邀请码
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _create_invitation(context: TeacherRegressionContext) -> None:
    """为临时班级生成邀请码。"""
    response, ok = record_check_request(
        context,
        "教师-生成邀请码",
        "POST",
        "/api/teacher/invitations/generate",
        expected=(200, 201),
        json={"class_id": context.temp_ids["class_id"], "max_uses": 1},
    )
    context.temp_ids["invitation_id"] = _response_id(response, ok, "invitation_id", "id")


# 维护意图：创建临时考试并验证详情、更新、发布、撤销和统计接口
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _create_exam(context: TeacherRegressionContext) -> None:
    """创建临时考试并验证详情、更新、发布、撤销和统计接口。"""
    if not context.temp_ids["question_id"]:
        return

    response, ok = record_check_request(
        context,
        "教师-创建考试",
        "POST",
        "/api/teacher/exams/create",
        expected=(200, 201),
        json={
            "course_id": context.temp_ids["course_id"],
            "title": f"{TEMP_PREFIX}考试{context.temp_suffix}",
            "exam_type": "chapter",
            "questions": [context.temp_ids["question_id"]],
            "duration": 30,
            "total_score": 100,
            "pass_score": 60,
        },
    )
    context.temp_ids["exam_id"] = _response_id(response, ok, "exam_id", "id")
    if not context.temp_ids["exam_id"]:
        return

    exam_path = f"/api/teacher/exams/{context.temp_ids['exam_id']}"
    record_check_get(context, "教师-考试详情", exam_path)
    record_check_request(
        context,
        "教师-更新考试",
        "PUT",
        f"{exam_path}/update",
        expected=(200,),
        json={"description": "接口回归考试"},
    )
    _publish_and_unpublish_exam(context, exam_path)
    record_check_get(context, "教师-考试结果列表", f"{exam_path}/results")
    record_check_get(context, "教师-考试分析", f"{exam_path}/analysis")


# 维护意图：有临时班级时验证考试发布和取消发布
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _publish_and_unpublish_exam(
    context: TeacherRegressionContext,
    exam_path: str,
) -> None:
    """有临时班级时验证考试发布和取消发布。"""
    if not context.temp_ids["class_id"]:
        return
    record_check_request(
        context,
        "教师-发布考试",
        "POST",
        f"{exam_path}/publish",
        expected=(200,),
        json={"class_id": context.temp_ids["class_id"]},
    )
    record_check_request(
        context,
        "教师-取消发布",
        "POST",
        f"{exam_path}/unpublish",
        expected=(200,),
    )


# 维护意图：全量模式收尾时验证教师端列表接口
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _run_teacher_list_checks(context: TeacherRegressionContext) -> None:
    """全量模式收尾时验证教师端列表接口。"""
    target_course_id = context.temp_ids["course_id"] or context.course_id
    record_check_get(context, "教师-课程列表", "/api/teacher/courses/my")
    for label, path in (
        ("教师-题目列表", "/api/teacher/questions"),
        ("教师-知识点列表", "/api/teacher/knowledge-points"),
        ("教师-资源列表", "/api/teacher/resources"),
        ("教师-考试列表", "/api/teacher/exams"),
    ):
        record_check_get(context, label, path, params={"course_id": target_course_id})


# 维护意图：记录教师端 GET 请求检查
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def record_check_get(
    context: TeacherRegressionContext,
    label: str,
    path: str,
    *,
    params: dict[str, object] | None = None,
) -> tuple[object, bool]:
    """记录教师端 GET 请求检查。"""
    return record_check_request(
        context,
        label,
        "GET",
        path,
        expected=(200,),
        params=params,
    )


# 维护意图：封装教师端回归请求和结果记录
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def record_check_request(
    context: TeacherRegressionContext,
    label: str,
    method: str,
    path: str,
    *,
    expected: tuple[int, ...],
    data: dict[str, object] | None = None,
    json: dict[str, object] | None = None,
    params: dict[str, object] | None = None,
) -> tuple[object, bool]:
    """封装教师端回归请求和结果记录。"""
    return record_check(
        context.checks,
        label,
        *_request(
            method,
            f"{context.base_url}{path}",
            headers=context.teacher_headers,
            data=data,
            json=json,
            params=params,
        ),
        expected=expected,
    )


# 维护意图：从成功响应中提取临时资源 ID
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _response_id(
    response: object,
    ok: bool,
    *candidate_keys: str,
) -> int | None:
    """从成功响应中提取临时资源 ID。"""
    if not ok or not isinstance(response, dict):
        return None
    for key in candidate_keys:
        value = response.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    return None
