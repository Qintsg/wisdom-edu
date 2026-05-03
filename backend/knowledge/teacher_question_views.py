"""教师端题库管理视图。"""
from __future__ import annotations

import csv
import json

from application.teacher.contracts import first_present, normalize_question_point_ids
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from assessments.models import Question
from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, success_response
from common.utils import resolve_course_id as _resolve_course_id

from .teacher_question_support import (
    apply_question_update_fields,
    build_question_detail,
    build_question_list_item,
    has_question_point_payload,
    question_identifier,
    replace_question_points_from_payload,
)
from .teacher_helpers import (
    bad_request,
    build_csv_download_response,
    extract_question_answer_text,
    link_knowledge_points,
    parse_pagination,
    refresh_course_rag_index,
    require_point_ids,
)


# 维护意图：获取题目列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_list(request: Request) -> Response:
    """获取题目列表。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    question_type = request.query_params.get("type")
    difficulty = request.query_params.get("difficulty")
    point_id = request.query_params.get("point_id")
    keyword = request.query_params.get("keyword", "")
    page, size = parse_pagination(request, size_keys=("size",))

    questions = Question.objects.filter(course_id=course_id)
    if question_type:
        questions = questions.filter(question_type=question_type)
    if difficulty:
        questions = questions.filter(difficulty=difficulty)
    if point_id:
        questions = questions.filter(knowledge_points__id=point_id)
    if keyword:
        questions = questions.filter(content__icontains=keyword)

    questions = questions.distinct()
    total = questions.count()
    start = (page - 1) * size
    page_questions = questions.prefetch_related("knowledge_points")[start : start + size]
    return success_response(data={
        "total": total,
        "questions": [build_question_list_item(question) for question in page_questions],
    })


# 维护意图：获取或更新题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_detail(request: Request, question_id: int) -> Response:
    """获取或更新题目。"""
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(msg="题目不存在", code=404)

    if request.method == "PUT":
        apply_question_update_fields(question, request.data, include_detail_fields=True)
        question.save()
        replace_question_points_from_payload(question, request.data)

        return success_response(
            data={"question_id": question_identifier(question)},
            msg="题目更新成功",
        )

    return success_response(data=build_question_detail(question))


# 维护意图：创建题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_create(request: Request) -> Response:
    """创建题目。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    content = request.data.get("content")
    question_type = first_present(request.data, "type", "question_type")
    options = request.data.get("options", [])
    answer = request.data.get("answer")
    analysis = request.data.get("analysis", "")
    difficulty = request.data.get("difficulty", "medium")
    score = request.data.get("score", 1)
    points = normalize_question_point_ids(request.data)

    if not content or not question_type or not answer:
        return bad_request("缺少必要参数")

    question = Question.objects.create(
        course_id=course_id,
        content=content,
        question_type=question_type,
        options=options,
        answer={"answer": answer} if not isinstance(answer, dict) else answer,
        analysis=analysis,
        difficulty=difficulty,
        score=score,
        created_by=request.user,
    )
    if points:
        replace_question_points_from_payload(question, {"points": points})

    refresh_course_rag_index(course_id)
    return success_response(data={"question_id": question_identifier(question)}, msg="题目创建成功")


# 维护意图：更新题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_update(request: Request, question_id: int) -> Response:
    """更新题目。"""
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(msg="题目不存在", code=404)

    apply_question_update_fields(question, request.data, include_detail_fields=False)
    question.save()

    if has_question_point_payload(request.data):
        replace_question_points_from_payload(
            question,
            request.data,
            filter_course_for_ids=False,
        )

    refresh_course_rag_index(question.course_id)
    return success_response(data={"question_id": question_identifier(question)}, msg="题目更新成功")


# 维护意图：删除题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_delete(request: Request, question_id: int) -> Response:
    """删除题目。"""
    try:
        question = Question.objects.get(id=question_id)
        course_id = question.course_id
        question.delete()
        refresh_course_rag_index(course_id)
        return success_response(msg="题目删除成功")
    except Question.DoesNotExist:
        return error_response(msg="题目不存在", code=404)


# 维护意图：批量删除题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_batch_delete(request: Request) -> Response:
    """批量删除题目。"""
    question_ids = request.data.get("question_ids", [])
    if not question_ids:
        return bad_request("请提供题目ID列表")

    questions = Question.objects.filter(id__in=question_ids)
    course_ids = list(questions.values_list("course_id", flat=True).distinct())
    deleted_count, _ = questions.delete()
    for course_id in course_ids:
        if course_id:
            refresh_course_rag_index(int(course_id))
    return success_response(data={"deleted_count": deleted_count}, msg=f"已删除 {deleted_count} 道题目")


# 维护意图：批量导入题目，支持 JSON 和 Excel 文件
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_import(request: Request) -> Response:
    """批量导入题目，支持 JSON 和 Excel 文件。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return bad_request("请上传文件")

    filename = uploaded_file.name.lower()
    try:
        if filename.endswith(".json"):
            data = json.loads(uploaded_file.read().decode("utf-8"))
            from tools.questions import import_questions_json
            result = import_questions_json(data, course_id)
        elif filename.endswith((".xlsx", ".xls")):
            from tools.questions import import_question_bank
            result = import_question_bank(uploaded_file, course_id)
        else:
            return bad_request("仅支持 .json / .xlsx 文件")
    except (ImportError, json.JSONDecodeError, RuntimeError, TypeError, ValueError) as exc:
        return bad_request(f"导入失败: {exc}")

    refresh_course_rag_index(course_id)
    return success_response(data=result, msg="题目导入完成")


# 维护意图：导出题目 CSV
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_export(request: Request):
    """导出题目 CSV。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    questions = Question.objects.filter(course_id=course_id)
    response = build_csv_download_response("questions.csv")
    writer = csv.writer(response)
    writer.writerow(["ID", "题型", "题目内容", "选项A", "选项B", "选项C", "选项D", "正确答案", "解析", "难度"])
    for question in questions:
        options = question.options if isinstance(question.options, list) else []
        writer.writerow([
            question.id,
            question.question_type,
            question.content,
            options[0] if len(options) > 0 else "",
            options[1] if len(options) > 1 else "",
            options[2] if len(options) > 2 else "",
            options[3] if len(options) > 3 else "",
            extract_question_answer_text(question),
            question.analysis or "",
            question.difficulty,
        ])
    return response


# 维护意图：获取题目导入模板
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_template(request: Request):
    """获取题目导入模板。"""
    response = build_csv_download_response("question_template.csv")
    writer = csv.writer(response)
    writer.writerow([
        "question_type",
        "content",
        "option_a",
        "option_b",
        "option_c",
        "option_d",
        "correct_answer",
        "analysis",
        "difficulty",
        "knowledge_point_name",
    ])
    writer.writerow([
        "single_choice",
        "以下哪个不是Python基本数据类型？",
        "整数",
        "字符串",
        "数组",
        "布尔",
        "C",
        "数组不是Python的基本数据类型",
        3,
        "数据类型",
    ])
    writer.writerow(["true_false", "Python是动态类型语言", "正确", "错误", "", "", "A", "", 1, ""])
    return response


# 维护意图：题目关联知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_link_knowledge(request: Request, question_id: int) -> Response:
    """题目关联知识点。"""
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(msg="题目不存在", code=404)

    point_ids, err = require_point_ids(request)
    if err:
        return err

    linked_count = link_knowledge_points(question, point_ids)
    return success_response(msg=f"已关联 {linked_count} 个知识点")
