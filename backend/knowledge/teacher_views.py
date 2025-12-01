"""
知识图谱模块 - 教师端视图

提供资源库、知识点管理相关的API端点。
CRUD操作同时写入PostgreSQL和Neo4j，确保数据一致性。
"""

import codecs
import json
import logging
from collections.abc import Iterable
from typing import Protocol, cast

from django.db import transaction
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from application.teacher.contracts import first_present, normalize_question_point_ids
from assessments.models import Question
from common.neo4j_service import neo4j_service
from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, success_response
from common.utils import resolve_course_id as _resolve_course_id
from .models import KnowledgePoint, KnowledgeRelation, Resource


logger = logging.getLogger(__name__)
UTF8_BOM = codecs.BOM_UTF8.decode("utf-8")
KnowledgePointReference = int | str | KnowledgePoint


class _KnowledgePointRelationSetter(Protocol):
    """支持 set 的知识点关系管理器协议。"""

    def set(self, points: Iterable[KnowledgePointReference]) -> None:
        """替换知识点关联。"""


class _KnowledgePointRelationAdder(Protocol):
    """支持 add 的知识点关系管理器协议。"""

    def add(self, *points: KnowledgePoint) -> None:
        """追加知识点关联。"""


def _bad_request(msg: str) -> Response:
    """返回 400 错误响应。"""
    return error_response(msg=msg)


def _parse_pagination(
    request: Request,
    *,
    size_keys: tuple[str, ...] = ("page_size", "size"),
    default_size: int = 20,
    max_size: int = 100,
) -> tuple[int, int]:
    """解析分页参数。"""
    try:
        page = max(1, int(request.query_params.get("page", 1)))
        size = default_size
        for size_key in size_keys:
            size_value = request.query_params.get(size_key)
            if size_value not in (None, ""):
                size = int(size_value)
                break
        size = min(max(1, size), max_size)
    except (ValueError, TypeError):
        page = 1
        size = default_size
    return page, size


def _replace_knowledge_points(
    relation_manager: _KnowledgePointRelationSetter,
    point_values: Iterable[KnowledgePointReference],
) -> None:
    """统一替换多对多知识点关联。"""
    relation_manager.set(point_values)


def _require_point_ids(request: Request) -> tuple[list[int | str], Response | None]:
    """从请求中提取必填知识点 ID 列表。"""
    raw_point_ids = request.data.get("knowledge_point_ids", [])
    if isinstance(raw_point_ids, list):
        point_ids = raw_point_ids
    elif raw_point_ids in (None, ""):
        point_ids = []
    else:
        point_ids = [raw_point_ids]

    if not point_ids:
        return [], _bad_request("请提供知识点ID列表")
    return point_ids, None


def _link_knowledge_points(target: Resource | Question, point_ids: list[int | str]) -> int:
    """为资源或题目补充知识点关联并刷新 RAG 索引。"""
    points = list(
        KnowledgePoint.objects.filter(id__in=point_ids, course_id=target.course_id)
    )
    cast(_KnowledgePointRelationAdder, target.knowledge_points).add(*points)
    _refresh_course_rag_index(target.course_id)
    return len(points)


def _extract_question_answer_text(question: Question) -> str:
    """提取题目的导出答案文本。"""
    answer_payload = question.answer if isinstance(question.answer, dict) else {}
    answer_value = answer_payload.get("answer")
    if answer_value not in (None, ""):
        return str(answer_value)
    answers = answer_payload.get("answers")
    if isinstance(answers, list):
        return ",".join(str(answer) for answer in answers if answer is not None)
    return ""


def _build_csv_download_response(filename: str) -> HttpResponse:
    """构造带 BOM 的 CSV 下载响应。"""
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write(UTF8_BOM)
    return response


def _refresh_course_rag_index(course_id: int) -> None:
    """在知识图谱、题库、资源变更后刷新课程级 RAG 索引。"""
    try:
        from tools.rag_index import refresh_rag_corpus

        refresh_rag_corpus(course_id=course_id)
        logger.info("课程 RAG 索引刷新成功: course=%s", course_id)
    except Exception as error:
        logger.warning("课程 RAG 索引刷新失败: course=%s error=%s", course_id, error)


# ========== 资源库管理 ==========


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_list(request):
    """
    获取资源列表
    GET /api/teacher/resources
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    resource_type = request.query_params.get("type")
    keyword = request.query_params.get("keyword") or request.query_params.get(
        "title", ""
    )
    point_id = request.query_params.get("point_id")
    page, size = _parse_pagination(request)

    resources = (
        Resource.objects.filter(course_id=course_id)
        .prefetch_related("knowledge_points")
        .order_by("sort_order", "id")
    )

    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    if keyword:
        resources = resources.filter(title__icontains=keyword)
    if point_id:
        resources = resources.filter(knowledge_points__id=point_id)

    total = resources.count()
    start = (page - 1) * size
    resources = resources[start : start + size]

    data = []
    for r in resources:
        file_url = None
        file_format = ""
        try:
            if r.file:
                file_url = r.file.url
                file_name = getattr(r.file, "name", "") or ""
                file_format = file_name.split(".")[-1] if "." in file_name else ""
        except (ValueError, AttributeError):
            pass

        kp_list = cast(list[KnowledgePoint], list(r.knowledge_points.all()))
        first_point = kp_list[0] if kp_list else None

        item = {
            "resource_id": getattr(r, "id", None) or getattr(r, "pk", None),
            "title": r.title,
            "type": r.resource_type,
            "url": r.url or file_url,
            "format": file_format,
            "point_id": first_point.id if first_point else None,
            "point_name": ", ".join(point.name for point in kp_list) if kp_list else "",
            "points": [{"id": point.id, "name": point.name} for point in kp_list],
            "description": getattr(r, "description", "") or "",
            "visible": r.is_visible,
            "created_at": r.created_at.isoformat(),
            "duration": r.duration,
            "duration_display": f"{r.duration // 60:02d}:{r.duration % 60:02d}"
            if r.duration
            else None,
            "chapter_number": r.chapter_number,
            "sort_order": r.sort_order,
        }

        data.append(item)

    return success_response(data={"total": total, "resources": data})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_create(request):
    """
    上传/创建资源
    POST /api/teacher/resources
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    title = first_present(request.data, "title", "resource_name")
    resource_type = first_present(request.data, "type", "resource_type")
    url = first_present(request.data, "url", "resource_url")
    file = request.FILES.get("file")
    # 兼容前端 point_id (单个) 和 points (数组) 两种传参方式
    points = request.data.get("points", request.data.get("knowledge_point_ids", []))
    point_id = request.data.get("point_id") or request.data.get("knowledge_point_id")
    duration = request.data.get("duration")
    chapter_number = request.data.get("chapter_number")
    sort_order = request.data.get("sort_order", 0)
    description = request.data.get("description", "")

    if not title or not resource_type:
        return _bad_request("缺少必要参数")

    if isinstance(points, str):
        try:
            points = json.loads(points)
        except json.JSONDecodeError:
            points = []

    # 若前端传了 point_id 而 points 为空，则将 point_id 作为 points
    if not points and point_id:
        points = [point_id]

    # 处理视频时长
    duration_val = None
    if duration is not None:
        try:
            duration_val = int(duration)
        except (ValueError, TypeError):
            pass

    # 解析排序序号
    sort_order_val = 0
    if sort_order:
        try:
            sort_order_val = int(sort_order)
        except (ValueError, TypeError):
            sort_order_val = 0

    resource = Resource.objects.create(
        course_id=course_id,
        title=title,
        resource_type=resource_type,
        url=url,
        file=file,
        description=description,
        duration=duration_val,
        chapter_number=chapter_number if chapter_number else None,
        sort_order=sort_order_val,
        uploaded_by=request.user,
    )

    if points:
        _replace_knowledge_points(
            cast(_KnowledgePointRelationSetter, resource.knowledge_points), points
        )

    _refresh_course_rag_index(course_id)

    return success_response(
        data={
            "resource_id": getattr(resource, "id", None)
            or getattr(resource, "pk", None),
            "title": resource.title,
            "url": resource.url or (resource.file.url if resource.file else None),
        },
        msg="资源创建成功",
    )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_update(request, resource_id):
    """
    获取或更新资源
    GET /api/teacher/resources/{resource_id} - 获取详情
    PUT /api/teacher/resources/{resource_id} - 更新
    """
    try:
        resource = Resource.objects.get(id=resource_id)
    except Resource.DoesNotExist:
        return error_response(msg="资源不存在", code=404)

    if request.method == "GET":
        return success_response(
            data={
                "resource_id": resource.id,
                "title": resource.title,
                "type": resource.resource_type,
                "url": resource.url or "",
                "file": resource.file.url if resource.file else None,
                "description": resource.description or "",
                "duration": resource.duration,
                "chapter_number": resource.chapter_number or "",
                "sort_order": resource.sort_order,
                "is_visible": resource.is_visible,
                "knowledge_points": list(
                    resource.knowledge_points.values_list("id", flat=True)
                ),
                "course_id": resource.course_id,
            }
        )

    # PUT - 更新

    title = first_present(request.data, "title", "resource_name")
    resource_type = first_present(request.data, "type", "resource_type")
    url = first_present(request.data, "url", "resource_url")
    points = request.data.get("points", request.data.get("knowledge_point_ids", []))
    point_id = request.data.get("point_id") or request.data.get("knowledge_point_id")
    is_visible = first_present(request.data, "visible", "is_visible")
    duration = request.data.get("duration")
    chapter_number = request.data.get("chapter_number")
    sort_order = request.data.get("sort_order")
    description = request.data.get("description")

    if title:
        resource.title = title
    if resource_type:
        resource.resource_type = resource_type
    if url:
        resource.url = url
    if is_visible is not None:
        resource.is_visible = is_visible
    if description is not None:
        resource.description = description
    if duration is not None:
        try:
            resource.duration = int(duration)
        except (ValueError, TypeError):
            pass
    if chapter_number is not None:
        resource.chapter_number = chapter_number
    if sort_order is not None:
        try:
            resource.sort_order = int(sort_order)
        except (ValueError, TypeError):
            pass

    resource.save()

    if isinstance(points, str):
        try:
            points = json.loads(points)
        except json.JSONDecodeError:
            points = []
    if not points and point_id:
        points = [point_id]
    if points:
        _replace_knowledge_points(
            cast(_KnowledgePointRelationSetter, resource.knowledge_points), points
        )

    _refresh_course_rag_index(resource.course_id)

    return success_response(
        data={
            "resource_id": getattr(resource, "id", None)
            or getattr(resource, "pk", None)
        },
        msg="资源更新成功",
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_delete(request, resource_id):
    """
    删除资源
    DELETE /api/teacher/resources/{resource_id}
    """
    try:
        resource = Resource.objects.get(id=resource_id)
        course_id = resource.course_id
        resource.delete()
        _refresh_course_rag_index(course_id)
        return success_response(msg="资源删除成功")
    except Resource.DoesNotExist:
        return error_response(msg="资源不存在", code=404)


# ========== 题库管理 ==========


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_list(request):
    """
    获取题目列表
    GET /api/teacher/questions
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    question_type = request.query_params.get("type")
    difficulty = request.query_params.get("difficulty")
    point_id = request.query_params.get("point_id")
    keyword = request.query_params.get("keyword", "")
    page, size = _parse_pagination(request, size_keys=("size",))

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
    questions = questions.prefetch_related("knowledge_points")[start : start + size]

    data = []
    for q in questions:
        data.append(
            {
                "question_id": getattr(q, "id", None) or getattr(q, "pk", None),
                "content": q.content[:100] + "..."
                if len(q.content) > 100
                else q.content,
                "type": q.question_type,
                "difficulty": q.difficulty,
                "points": list(q.knowledge_points.values_list("id", flat=True)),
                "created_at": q.created_at.isoformat(),
            }
        )

    return success_response(data={"total": total, "questions": data})


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_detail(request, question_id):
    """
    获取/更新题目
    GET /api/teacher/questions/{question_id} - 获取题目详情
    PUT /api/teacher/questions/{question_id} - 更新题目
    """
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(msg="题目不存在", code=404)

    if request.method == "PUT":
        # 更新题目（复用question_update的逻辑）
        fields = ["content", "options", "analysis", "difficulty", "score"]
        for field in request.data:
            if field in fields:
                setattr(question, field, request.data[field])

        if "answer" in request.data:
            answer = request.data["answer"]
            question.answer = (
                {"answer": answer} if not isinstance(answer, dict) else answer
            )

        if "type" in request.data or "question_type" in request.data:
            question.question_type = first_present(
                request.data, "type", "question_type"
            )
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
            kps = KnowledgePoint.objects.filter(
                id__in=request.data["knowledge_point_ids"], course=question.course
            )
            _replace_knowledge_points(
                cast(_KnowledgePointRelationSetter, question.knowledge_points), kps
            )
        elif "points" in request.data:
            _replace_knowledge_points(
                cast(_KnowledgePointRelationSetter, question.knowledge_points),
                normalize_question_point_ids(request.data),
            )

        return success_response(
            data={
                "question_id": getattr(question, "id", None)
                or getattr(question, "pk", None)
            },
            msg="题目更新成功",
        )

    question_points = cast(list[KnowledgePoint], list(question.knowledge_points.all()))
    return success_response(
        data={
            "question_id": getattr(question, "id", None)
            or getattr(question, "pk", None),
            "content": question.content,
            "type": question.question_type,
            "question_type": question.question_type,
            "options": question.options,
            "answer": question.answer,
            "analysis": question.analysis,
            "difficulty": question.difficulty,
            "score": float(question.score),
            "suggested_score": float(question.suggested_score)
            if question.suggested_score
            else None,
            "chapter": question.chapter,
            "is_visible": question.is_visible,
            "for_initial_assessment": question.for_initial_assessment,
            "points": [
                {"point_id": point.id, "point_name": point.name}
                for point in question_points
            ],
            "knowledge_points": [
                {"id": point.id, "name": point.name} for point in question_points
            ],
            "creator": question.created_by.username if question.created_by else None,
            "created_at": question.created_at.isoformat(),
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_create(request):
    """
    创建题目
    POST /api/teacher/questions
    """
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
        return _bad_request("缺少必要参数")

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
        _replace_knowledge_points(
            cast(_KnowledgePointRelationSetter, question.knowledge_points), points
        )

    _refresh_course_rag_index(course_id)

    return success_response(
        data={
            "question_id": getattr(question, "id", None)
            or getattr(question, "pk", None)
        },
        msg="题目创建成功",
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_update(request, question_id):
    """
    更新题目
    PUT /api/teacher/questions/{question_id}
    """
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(msg="题目不存在", code=404)

    fields = ["content", "options", "analysis", "difficulty", "score"]
    for field in fields:
        if field in request.data:
            setattr(question, field, request.data[field])

    if "answer" in request.data:
        answer = request.data["answer"]
        question.answer = {"answer": answer} if not isinstance(answer, dict) else answer

    if "type" in request.data or "question_type" in request.data:
        question.question_type = first_present(request.data, "type", "question_type")

    question.save()

    if "points" in request.data or "knowledge_point_ids" in request.data:
        _replace_knowledge_points(
            cast(_KnowledgePointRelationSetter, question.knowledge_points),
            normalize_question_point_ids(request.data),
        )

    _refresh_course_rag_index(question.course_id)

    return success_response(
        data={
            "question_id": getattr(question, "id", None)
            or getattr(question, "pk", None)
        },
        msg="题目更新成功",
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_delete(request, question_id):
    """
    删除题目
    DELETE /api/teacher/questions/{question_id}
    """
    try:
        question = Question.objects.get(id=question_id)
        course_id = question.course_id
        question.delete()
        _refresh_course_rag_index(course_id)
        return success_response(msg="题目删除成功")
    except Question.DoesNotExist:
        return error_response(msg="题目不存在", code=404)


# ========== 知识图谱管理 ==========


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_relation_list(request):
    """
    获取知识点关系列表（教师端）
    GET /api/teacher/knowledge-relations

    优先从Neo4j查询，不可用时降级到PostgreSQL。
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    # 尝试Neo4j
    neo4j_relations = neo4j_service.get_knowledge_relations_neo4j(course_id)

    if neo4j_relations is not None:
        return success_response(
            data={
                "relations": [
                    {
                        "relation_id": r.get("relation_id"),
                        "from_point_id": r.get("pre_point_id"),
                        "from_point_name": r.get("pre_point_name", ""),
                        "to_point_id": r.get("post_point_id"),
                        "to_point_name": r.get("post_point_name", ""),
                        "relation_type": r.get("relation_type", "prerequisite"),
                    }
                    for r in neo4j_relations
                ],
                "count": len(neo4j_relations),
                "data_source": "neo4j",
            }
        )

    # PostgreSQL降级
    logger.warning(
        f"[knowledge_relation_list] Neo4j不可用，降级使用PostgreSQL查询课程 {course_id} 的关系"
    )

    relations = KnowledgeRelation.objects.filter(course_id=course_id).select_related(
        "pre_point", "post_point"
    )
    return success_response(
        data={
            "relations": [
                {
                    "relation_id": getattr(r, "id", None) or getattr(r, "pk", None),
                    "from_point_id": getattr(r, "pre_point_id", None),
                    "from_point_name": r.pre_point.name,
                    "to_point_id": getattr(r, "post_point_id", None),
                    "to_point_name": r.post_point.name,
                    "relation_type": r.relation_type,
                }
                for r in relations
            ],
            "count": relations.count(),
            "data_source": "postgresql",
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_relation_create(request):
    """
    创建知识点关系
    POST /api/teacher/knowledge-relations/create
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    data = request.data
    from_point_id = data.get("from_point_id")
    to_point_id = data.get("to_point_id")
    relation_type = data.get("relation_type", "prerequisite")

    if not from_point_id or not to_point_id:
        return _bad_request("缺少 from_point_id 或 to_point_id")

    if str(from_point_id) == str(to_point_id):
        return _bad_request("不能创建自引用关系")

    # 检查知识点是否存在
    try:
        pre = KnowledgePoint.objects.get(pk=from_point_id, course_id=course_id)
        post = KnowledgePoint.objects.get(pk=to_point_id, course_id=course_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    rel, created = KnowledgeRelation.objects.get_or_create(
        course_id=course_id,
        pre_point=pre,
        post_point=post,
        defaults={"relation_type": relation_type},
    )

    # 同步到Neo4j
    if created:
        neo4j_service.sync_single_relation(rel)
        _refresh_course_rag_index(course_id)

    return success_response(
        data={
            "relation_id": getattr(rel, "id", None) or getattr(rel, "pk", None),
            "created": created,
        },
        msg="关系创建成功" if created else "关系已存在",
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_relation_delete(request, relation_id):
    """
    删除知识点关系
    DELETE /api/teacher/knowledge-relations/<relation_id>
    """
    try:
        rel = KnowledgeRelation.objects.get(pk=relation_id)
    except KnowledgeRelation.DoesNotExist:
        return error_response(msg="关系不存在", code=404)

    # 同步删除Neo4j中的关系
    neo4j_service.delete_relation_neo4j(rel.pre_point_id, rel.post_point_id)

    course_id = rel.course_id
    rel.delete()
    _refresh_course_rag_index(course_id)
    return success_response(msg="关系删除成功")


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_graph_save(request):
    """
    批量保存知识图谱（来自可视化编辑器）
    POST /api/teacher/knowledge-map/save
    接收 { nodes: [...], edges: [...] } 并同步到数据库
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    payload = request.data
    nodes = payload.get("nodes", [])
    edges = payload.get("edges", [])

    if not nodes:
        return _bad_request("节点数据为空")

    with transaction.atomic():
        existing_points = {
            str(getattr(point, "id", point.pk)): point
            for point in KnowledgePoint.objects.filter(course_id=course_id)
        }
        existing_ids = set(existing_points.keys())
        submitted_ids = set()

        for node in nodes:
            node_id = str(node.get("id", ""))
            name = str(node.get("name", node.get("point_name", "")))[:200]
            if node_id in existing_ids:
                point = existing_points[node_id]
                if point.name != name:
                    point.name = name
                    point.description = str(node.get("description", ""))[:1000]
                    point.save(update_fields=["name", "description"])
                submitted_ids.add(node_id)

        removed = existing_ids - submitted_ids
        if removed:
            KnowledgePoint.objects.filter(pk__in=removed, course_id=course_id).delete()

        KnowledgeRelation.objects.filter(course_id=course_id).delete()
        point_map = {
            str(getattr(point, "id", point.pk)): point
            for point in KnowledgePoint.objects.filter(course_id=course_id)
        }
        for edge in edges:
            source = str(edge.get("source", ""))
            target = str(edge.get("target", ""))
            if source in point_map and target in point_map and source != target:
                KnowledgeRelation.objects.get_or_create(
                    course_id=course_id,
                    pre_point=point_map[source],
                    post_point=point_map[target],
                    defaults={"relation_type": edge.get("label", "prerequisite")},
                )

    # 批量保存后同步整个课程图谱到Neo4j
    try:
        neo4j_service.sync_knowledge_graph(course_id)
        logger.info(f"知识图谱保存后Neo4j同步成功: course={course_id}")
    except Exception as exc:
        logger.warning(f"知识图谱保存成功但Neo4j同步失败: {exc}")

    _refresh_course_rag_index(course_id)
    return success_response(msg="知识图谱保存成功")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_point_list(request):
    """
    获取知识点列表
    GET /api/teacher/knowledge-points

    优先从Neo4j查询，不可用时降级到PostgreSQL。
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    # 尝试Neo4j
    neo4j_points = neo4j_service.get_knowledge_points_neo4j(course_id)

    if neo4j_points is not None:
        return success_response(
            data={
                "points": [
                    {
                        "point_id": p.get("id"),
                        "point_name": p.get("name", ""),
                        "description": p.get("description", ""),
                        "chapter": p.get("chapter", ""),
                        "order": p.get("order_index", 0),
                        "is_published": p.get("is_published", True),
                    }
                    for p in neo4j_points
                ],
                "data_source": "neo4j",
            }
        )

    # PostgreSQL降级
    logger.warning(
        f"[knowledge_point_list] Neo4j不可用，降级使用PostgreSQL查询课程 {course_id} 的知识点"
    )

    points = KnowledgePoint.objects.filter(course_id=course_id).order_by("order")

    return success_response(
        data={
            "points": [
                {
                    "point_id": getattr(p, "id", None) or getattr(p, "pk", None),
                    "point_name": p.name,
                    "description": p.description,
                    "chapter": p.chapter,
                    "order": p.order,
                    "is_published": p.is_published,
                }
                for p in points
            ],
            "data_source": "postgresql",
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_point_create(request):
    """
    创建知识点
    POST /api/teacher/knowledge-points
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    point_name = request.data.get("point_name")
    description = request.data.get("description", "")
    prerequisites = request.data.get("prerequisites", [])
    chapter = request.data.get("chapter", "")

    if not point_name:
        return _bad_request("缺少必要参数")

    if isinstance(prerequisites, str):
        prerequisites = [pid.strip() for pid in prerequisites.split(",") if pid.strip()]

    max_order = KnowledgePoint.objects.filter(course_id=course_id).count()

    with transaction.atomic():
        point = KnowledgePoint.objects.create(
            course_id=course_id,
            name=point_name,
            description=description,
            chapter=chapter,
            order=max_order,
        )

        # 创建先修关系
        for pre_id in prerequisites:
            try:
                pre_id_int = int(pre_id)
            except (TypeError, ValueError):
                continue

            try:
                pre_point = KnowledgePoint.objects.get(
                    id=pre_id_int, course_id=course_id
                )
                KnowledgeRelation.objects.create(
                    course_id=course_id,
                    pre_point=pre_point,
                    post_point=point,
                    relation_type="prerequisite",
                )
            except KnowledgePoint.DoesNotExist:
                continue

    # 同步新知识点到Neo4j
    neo4j_service.sync_single_point(point)
    # 同步先修关系到Neo4j
    for rel in KnowledgeRelation.objects.filter(post_point=point):
        neo4j_service.sync_single_relation(rel)

    _refresh_course_rag_index(course_id)

    return success_response(
        data={
            "point_id": getattr(point, "id", None) or getattr(point, "pk", None),
            "point_name": point.name,
        },
        msg="知识点创建成功",
    )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_point_update(request, point_id):
    """
    获取或更新知识点
    GET /api/teacher/knowledge-points/{point_id} - 获取详情
    PUT /api/teacher/knowledge-points/{point_id} - 更新
    """
    try:
        point = KnowledgePoint.objects.get(id=point_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    if request.method == "GET":
        return success_response(
            data={
                "point_id": point.id,
                "point_name": point.name,
                "description": point.description or "",
                "chapter": point.chapter or "",
                "order": point.order,
                "is_published": point.is_published,
                "course_id": point.course_id,
            }
        )

    # PUT - 更新

    # 更新允许的字段
    if "point_name" in request.data:
        point.name = request.data["point_name"]
    if "name" in request.data:
        point.name = request.data["name"]
    if "description" in request.data:
        point.description = request.data["description"]
    if "chapter" in request.data:
        point.chapter = request.data["chapter"]
    if "order" in request.data:
        point.order = request.data["order"]
    if "is_published" in request.data:
        point.is_published = request.data["is_published"]

    point.save()

    # 同步更新到Neo4j
    neo4j_service.sync_single_point(point)

    _refresh_course_rag_index(point.course_id)

    return success_response(
        data={
            "point_id": getattr(point, "id", None) or getattr(point, "pk", None),
            "point_name": point.name,
        },
        msg="知识点更新成功",
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_point_delete(request, point_id):
    """
    删除知识点
    DELETE /api/teacher/knowledge-points/{point_id}/delete
    """
    try:
        point = KnowledgePoint.objects.get(id=point_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    # 同步删除Neo4j中的节点及其关系
    neo4j_service.delete_point_neo4j(point_id)

    # 删除PostgreSQL中相关的关系
    KnowledgeRelation.objects.filter(pre_point=point).delete()
    KnowledgeRelation.objects.filter(post_point=point).delete()

    course_id = point.course_id
    point.delete()
    _refresh_course_rag_index(course_id)

    return success_response(msg="知识点删除成功")


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_map_import(request):
    """
    导入知识图谱
    POST /api/teacher/knowledge-map/import
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    file = request.FILES.get("file")

    if not file:
        return _bad_request("缺少必要参数")

    # 验证文件大小（最大10MB）
    max_size = 10 * 1024 * 1024
    if file.size > max_size:
        return _bad_request("文件大小超过限制(最大10MB)")

    # 验证文件类型
    allowed_extensions = [".json", ".xlsx", ".xls"]
    file_ext = file.name.lower().split(".")[-1] if "." in file.name else ""
    if f".{file_ext}" not in allowed_extensions:
        return _bad_request("仅支持JSON或Excel格式文件")

    try:
        if file_ext == "json":
            content = file.read().decode("utf-8")
            data = json.loads(content)
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])
        else:
            import pandas as pd

            df = pd.read_excel(file, sheet_name=0)
            nodes = []
            edges = []

            for idx, row in df.iterrows():
                node = {
                    "id": str(idx),
                    "name": str(row.get("知识点名称", row.get("name", f"知识点{idx}"))),
                    "description": str(row.get("描述", row.get("description", ""))),
                    "chapter": str(row.get("章节", row.get("chapter", ""))),
                }
                nodes.append(node)

                # 处理先修关系
                prereq = row.get("先修知识点", row.get("prerequisites", ""))
                if prereq and str(prereq) != "nan":
                    for pre_name in str(prereq).split(","):
                        pre_name = pre_name.strip()
                        if pre_name:
                            edges.append(
                                {
                                    "source": pre_name,
                                    "target": node["name"],
                                    "relation": "prerequisite",
                                }
                            )

    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return _bad_request(f"文件格式错误: {str(exc)}")
    except Exception as exc:
        return _bad_request(f"文件读取失败: {str(exc)}")

    if not nodes:
        return _bad_request("知识点数据为空")

    # 验证节点数量限制
    if len(nodes) > 1000:
        return _bad_request("知识点数量超过限制(最多1000个)")

    id_map = {}  # 原始ID或名称到新ID的映射

    with transaction.atomic():
        for idx, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            name = str(node.get("name", node.get("point_name", f"知识点{idx}")))[:200]
            point = KnowledgePoint.objects.create(
                course_id=course_id,
                name=name,
                description=str(node.get("description", ""))[:1000],
                chapter=str(node.get("chapter", ""))[:100],
                order=idx,
            )
            point_id = getattr(point, "id", None) or getattr(point, "pk", None)
            id_map[str(node.get("id", str(idx)))] = point_id
            id_map[name] = point_id  # 也用名称作为key

        for edge in edges:
            if not isinstance(edge, dict):
                continue
            source = str(edge.get("source"))
            target = str(edge.get("target"))
            source_id = id_map.get(source)
            target_id = id_map.get(target)

            if source_id and target_id:
                KnowledgeRelation.objects.get_or_create(
                    course_id=course_id,
                    pre_point_id=source_id,
                    post_point_id=target_id,
                    defaults={"relation_type": edge.get("relation", "prerequisite")},
                )

    # 保持 PostgreSQL 与 Neo4j 图副本一致。
    try:
        neo4j_service.sync_knowledge_graph(course_id)
        logger.info(f"知识图谱导入后Neo4j同步成功: course={course_id}")
    except Exception as exc:
        logger.warning(f"知识图谱导入成功但Neo4j同步失败: {exc}")

    return success_response(
        data={"imported_nodes": len(nodes), "imported_edges": len(edges)},
        msg="知识图谱导入成功",
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_map_publish(request):
    """
    发布知识图谱
    POST /api/teacher/knowledge-map/publish
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    confirm = request.data.get("confirm", False)

    if not confirm:
        # 预览模式
        points = KnowledgePoint.objects.filter(course_id=course_id, is_published=False)
        pending_count = points.count()
        return success_response(
            data={
                "pending_count": pending_count,
                "message": f"有 {pending_count} 个知识点待发布",
            }
        )

    updated = KnowledgePoint.objects.filter(course_id=course_id).update(is_published=True)

    # 发布后同步到Neo4j（更新is_published状态）
    try:
        neo4j_service.sync_knowledge_graph(course_id)
    except Exception as exc:
        logger.warning(f"知识图谱发布成功但Neo4j同步失败: {exc}")

    _refresh_course_rag_index(course_id)
    return success_response(data={"published_count": updated}, msg="知识图谱发布成功")


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_map_build_rag_index(request):
    """
    构建课程 GraphRAG 索引。
    POST /api/teacher/knowledge-map/build-rag-index
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    from tools.rag_index import refresh_rag_corpus

    built_paths = refresh_rag_corpus(course_id=course_id)
    return success_response(
        data={
            "course_id": course_id,
            "index_paths": built_paths,
        },
        msg="课程 GraphRAG 索引构建完成",
    )


# ============ 知识图谱导出 / 模板 ============


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_map_export(request):
    """
    导出知识图谱为 JSON 文件
    GET /api/teacher/knowledge-map/export
    """
    import json as json_mod
    from django.http import HttpResponse

    course_id, err = _resolve_course_id(request)
    if err:
        return err

    points = KnowledgePoint.objects.filter(course_id=course_id)
    relations = KnowledgeRelation.objects.filter(course_id=course_id)

    payload = {
        "course_id": course_id,
        "knowledge_points": [
            {
                "id": kp.id,
                "name": kp.name,
                "description": kp.description or "",
                "difficulty": getattr(kp, "difficulty", None),
                "parent_id": getattr(kp, "parent_id", None),
            }
            for kp in points
        ],
        "relations": [
            {
                "from_point_id": getattr(r, "pre_point_id", None),
                "to_point_id": getattr(r, "post_point_id", None),
                "relation_type": r.relation_type,
            }
            for r in relations
        ],
    }

    response = HttpResponse(
        json_mod.dumps(payload, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="knowledge_map_{course_id}.json"'
    )
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_map_template(request):
    """
    获取知识图谱导入模板
    GET /api/teacher/knowledge-map/template
    """
    import json as json_mod
    from django.http import HttpResponse

    template = {
        "knowledge_points": [
            {
                "name": "示例知识点1",
                "description": "描述",
                "difficulty": 3,
                "parent_id": None,
            },
            {
                "name": "示例知识点2",
                "description": "描述",
                "difficulty": 2,
                "parent_id": None,
            },
        ],
        "relations": [
            {
                "from_point_name": "示例知识点1",
                "to_point_name": "示例知识点2",
                "relation_type": "prerequisite",
            },
        ],
    }

    response = HttpResponse(
        json_mod.dumps(template, ensure_ascii=False, indent=2),
        content_type="application/json; charset=utf-8",
    )
    response["Content-Disposition"] = (
        'attachment; filename="knowledge_map_template.json"'
    )
    return response


# ============ 资源上传 / 关联知识点 ============


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_upload(request):
    """
    上传资源文件
    POST /api/teacher/resources/upload
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return _bad_request("请上传文件")

    title = request.data.get("title", uploaded_file.name)
    resource_type = request.data.get("resource_type", "document")
    description = request.data.get("description", "")

    resource = Resource.objects.create(
        course_id=course_id,
        title=title,
        resource_type=resource_type,
        description=description,
        file=uploaded_file,
        uploaded_by=request.user,
    )

    return success_response(
        data={
            "id": resource.id,
            "title": resource.title,
            "file": resource.file.url if resource.file else "",
        },
        msg="资源上传成功",
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def resource_link_knowledge(request, resource_id):
    """
    资源关联知识点
    POST /api/teacher/resources/{resource_id}/link-knowledge
    """
    try:
        resource = Resource.objects.get(id=resource_id)
    except Resource.DoesNotExist:
        return error_response(msg="资源不存在", code=404)

    point_ids, err = _require_point_ids(request)
    if err:
        return err

    linked_count = _link_knowledge_points(resource, point_ids)
    return success_response(msg=f"已关联 {linked_count} 个知识点")


# ============ 题目批量操作 / 关联知识点 ============


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_batch_delete(request):
    """
    批量删除题目
    POST /api/teacher/questions/batch-delete
    """
    from assessments.models import Question

    question_ids = request.data.get("question_ids", [])
    if not question_ids:
        return _bad_request("请提供题目ID列表")

    questions = Question.objects.filter(id__in=question_ids)
    course_ids = list(questions.values_list("course_id", flat=True).distinct())
    deleted_count, _ = questions.delete()
    for course_id in course_ids:
        if course_id:
            _refresh_course_rag_index(int(course_id))
    return success_response(
        data={"deleted_count": deleted_count}, msg=f"已删除 {deleted_count} 道题目"
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_import(request):
    """
    批量导入题目
    POST /api/teacher/questions/import

    支持 JSON 和 Excel 文件导入
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return _bad_request("请上传文件")

    filename = uploaded_file.name.lower()

    try:
        if filename.endswith(".json"):
            import json as json_mod

            data = json_mod.loads(uploaded_file.read().decode("utf-8"))
            from tools.questions import import_questions_json

            result = import_questions_json(data, course_id)
        elif filename.endswith((".xlsx", ".xls")):
            from tools.questions import import_question_bank

            result = import_question_bank(uploaded_file, course_id)
        else:
            return _bad_request("仅支持 .json / .xlsx 文件")
    except Exception as exc:
        return _bad_request(f"导入失败: {exc}")

    _refresh_course_rag_index(course_id)
    return success_response(data=result, msg="题目导入完成")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_export(request):
    """
    导出题目
    GET /api/teacher/questions/export
    """
    import csv
    from assessments.models import Question

    course_id, err = _resolve_course_id(request)
    if err:
        return err

    questions = Question.objects.filter(course_id=course_id)
    response = _build_csv_download_response("questions.csv")
    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "题型",
            "题目内容",
            "选项A",
            "选项B",
            "选项C",
            "选项D",
            "正确答案",
            "解析",
            "难度",
        ]
    )

    for question in questions:
        options = question.options if isinstance(question.options, list) else []
        writer.writerow(
            [
                question.id,
                question.question_type,
                question.content,
                options[0] if len(options) > 0 else "",
                options[1] if len(options) > 1 else "",
                options[2] if len(options) > 2 else "",
                options[3] if len(options) > 3 else "",
                _extract_question_answer_text(question),
                question.analysis or "",
                question.difficulty,
            ]
        )
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_template(request):
    """
    获取题目导入模板
    GET /api/teacher/questions/template
    """
    import csv

    response = _build_csv_download_response("question_template.csv")
    writer = csv.writer(response)
    writer.writerow(
        [
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
        ]
    )
    writer.writerow(
        [
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
        ]
    )
    writer.writerow(
        ["true_false", "Python是动态类型语言", "正确", "错误", "", "", "A", "", 1, ""]
    )
    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def question_link_knowledge(request, question_id):
    """
    题目关联知识点
    POST /api/teacher/questions/{question_id}/link-knowledge
    """
    from assessments.models import Question

    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return error_response(msg="题目不存在", code=404)

    point_ids, err = _require_point_ids(request)
    if err:
        return err

    linked_count = _link_knowledge_points(question, point_ids)
    return success_response(msg=f"已关联 {linked_count} 个知识点")
