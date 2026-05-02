"""教师端题库管理视图。"""
from __future__ import annotations

import csv
import json
from typing import cast

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from application.teacher.contracts import first_present, normalize_question_point_ids
from assessments.models import Question
from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, success_response
from common.utils import resolve_course_id as _resolve_course_id

from .models import KnowledgePoint
from .teacher_helpers import (
    KnowledgePointRelationSetter,
    bad_request,
    build_csv_download_response,
    extract_question_answer_text,
    link_knowledge_points,
    parse_pagination,
    refresh_course_rag_index,
    replace_knowledge_points,
    require_point_ids,
)


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
        "questions": [{
            "question_id": getattr(question, "id", None) or getattr(question, "pk", None),
            "content": question.content[:100] + "..." if len(question.content) > 100 else question.content,
            "type": question.question_type,
            "difficulty": question.difficulty,
            "points": list(question.knowledge_points.values_list("id", flat=True)),
            "created_at": question.created_at.isoformat(),
        } for question in page_questions],
    })


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_detail(request: Request, question_id: int) -> Response:
    """获取或更新题目。"""
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(msg="题目不存在", code=404)

    if request.method == "PUT":
        fields = ["content", "options", "analysis", "difficulty", "score"]
        for field in request.data:
            if field in fields:
                setattr(question, field, request.data[field])
        if "answer" in request.data:
            answer = request.data["answer"]
            question.answer = {"answer": answer} if not isinstance(answer, dict) else answer
        if "type" in request.data or "question_type" in request.data:
            question.question_type = first_present(request.data, "type", "question_type")
        if "suggested_score" in request.data:
            question.suggested_score = request.data["suggested_score"]
        if "chapter" in request.data:
            question.chapter = request.data["chapter"]
        if "is_visible" in request.data:
            question.is_visible = request.data["is_visible"]
        if "for_initial_assessment" in request.data:
            question.for_initial_assessment = request.data["for_initial_assessment"]

        question.save()
        if "knowledge_point_ids" in request.data:
            knowledge_points = KnowledgePoint.objects.filter(id__in=request.data["knowledge_point_ids"], course=question.course)
            replace_knowledge_points(cast(KnowledgePointRelationSetter, question.knowledge_points), knowledge_points)
        elif "points" in request.data:
            replace_knowledge_points(
                cast(KnowledgePointRelationSetter, question.knowledge_points),
                normalize_question_point_ids(request.data),
            )

        return success_response(
            data={"question_id": getattr(question, "id", None) or getattr(question, "pk", None)},
            msg="题目更新成功",
        )

    question_points = cast(list[KnowledgePoint], list(question.knowledge_points.all()))
    return success_response(data={
        "question_id": getattr(question, "id", None) or getattr(question, "pk", None),
        "content": question.content,
        "type": question.question_type,
        "question_type": question.question_type,
        "options": question.options,
        "answer": question.answer,
        "analysis": question.analysis,
        "difficulty": question.difficulty,
        "score": float(question.score),
        "suggested_score": float(question.suggested_score) if question.suggested_score else None,
        "chapter": question.chapter,
        "is_visible": question.is_visible,
        "for_initial_assessment": question.for_initial_assessment,
        "points": [{"point_id": point.id, "point_name": point.name} for point in question_points],
        "knowledge_points": [{"id": point.id, "name": point.name} for point in question_points],
        "creator": question.created_by.username if question.created_by else None,
        "created_at": question.created_at.isoformat(),
    })


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
        replace_knowledge_points(cast(KnowledgePointRelationSetter, question.knowledge_points), points)

    refresh_course_rag_index(course_id)
    return success_response(data={"question_id": getattr(question, "id", None) or getattr(question, "pk", None)}, msg="题目创建成功")


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_update(request: Request, question_id: int) -> Response:
    """更新题目。"""
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(msg="题目不存在", code=404)

    for field in ["content", "options", "analysis", "difficulty", "score"]:
        if field in request.data:
            setattr(question, field, request.data[field])
    if "answer" in request.data:
        answer = request.data["answer"]
        question.answer = {"answer": answer} if not isinstance(answer, dict) else answer
    if "type" in request.data or "question_type" in request.data:
        question.question_type = first_present(request.data, "type", "question_type")
    question.save()

    if "points" in request.data or "knowledge_point_ids" in request.data:
        replace_knowledge_points(
            cast(KnowledgePointRelationSetter, question.knowledge_points),
            normalize_question_point_ids(request.data),
        )

    refresh_course_rag_index(question.course_id)
    return success_response(data={"question_id": getattr(question, "id", None) or getattr(question, "pk", None)}, msg="题目更新成功")


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
    except Exception as exc:
        return bad_request(f"导入失败: {exc}")

    refresh_course_rag_index(course_id)
    return success_response(data=result, msg="题目导入完成")


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
