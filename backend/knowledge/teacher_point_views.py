"""教师端知识点管理视图。"""
from __future__ import annotations

import logging

from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.neo4j_service import neo4j_service
from common.permissions import IsTeacherOrAdmin
from common.responses import error_response, success_response
from common.utils import resolve_course_id as _resolve_course_id

from .models import KnowledgePoint, KnowledgeRelation
from .teacher_helpers import bad_request, refresh_course_rag_index


logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_point_list(request: Request) -> Response:
    """获取知识点列表，优先 Neo4j，不可用时降级 PostgreSQL。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    neo4j_points = neo4j_service.get_knowledge_points_neo4j(course_id)
    if neo4j_points is not None:
        return success_response(data={
            "points": [{
                "point_id": point.get("id"),
                "point_name": point.get("name", ""),
                "description": point.get("description", ""),
                "chapter": point.get("chapter", ""),
                "order": point.get("order_index", 0),
                "is_published": point.get("is_published", True),
            } for point in neo4j_points],
            "data_source": "neo4j",
        })

    logger.warning("[knowledge_point_list] Neo4j不可用，降级使用PostgreSQL查询课程 %s 的知识点", course_id)
    points = KnowledgePoint.objects.filter(course_id=course_id).order_by("order")
    return success_response(data={
        "points": [{
            "point_id": getattr(point, "id", None) or getattr(point, "pk", None),
            "point_name": point.name,
            "description": point.description,
            "chapter": point.chapter,
            "order": point.order,
            "is_published": point.is_published,
        } for point in points],
        "data_source": "postgresql",
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_point_create(request: Request) -> Response:
    """创建知识点。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    point_name = request.data.get("point_name")
    description = request.data.get("description", "")
    prerequisites = request.data.get("prerequisites", [])
    chapter = request.data.get("chapter", "")

    if not point_name:
        return bad_request("缺少必要参数")
    if isinstance(prerequisites, str):
        prerequisites = [point_id.strip() for point_id in prerequisites.split(",") if point_id.strip()]

    max_order = KnowledgePoint.objects.filter(course_id=course_id).count()
    with transaction.atomic():
        point = KnowledgePoint.objects.create(
            course_id=course_id,
            name=point_name,
            description=description,
            chapter=chapter,
            order=max_order,
        )
        for pre_id in prerequisites:
            try:
                pre_id_int = int(pre_id)
            except (TypeError, ValueError):
                continue
            try:
                pre_point = KnowledgePoint.objects.get(id=pre_id_int, course_id=course_id)
                KnowledgeRelation.objects.create(
                    course_id=course_id,
                    pre_point=pre_point,
                    post_point=point,
                    relation_type="prerequisite",
                )
            except KnowledgePoint.DoesNotExist:
                continue

    neo4j_service.sync_single_point(point)
    for relation in KnowledgeRelation.objects.filter(post_point=point):
        neo4j_service.sync_single_relation(relation)
    refresh_course_rag_index(course_id)
    return success_response(
        data={"point_id": getattr(point, "id", None) or getattr(point, "pk", None), "point_name": point.name},
        msg="知识点创建成功",
    )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_point_update(request: Request, point_id: int) -> Response:
    """获取或更新知识点。"""
    try:
        point = KnowledgePoint.objects.get(id=point_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    if request.method == "GET":
        return success_response(data={
            "point_id": point.id,
            "point_name": point.name,
            "description": point.description or "",
            "chapter": point.chapter or "",
            "order": point.order,
            "is_published": point.is_published,
            "course_id": point.course_id,
        })

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
    neo4j_service.sync_single_point(point)
    refresh_course_rag_index(point.course_id)
    return success_response(
        data={"point_id": getattr(point, "id", None) or getattr(point, "pk", None), "point_name": point.name},
        msg="知识点更新成功",
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_point_delete(request: Request, point_id: int) -> Response:
    """删除知识点。"""
    try:
        point = KnowledgePoint.objects.get(id=point_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    neo4j_service.delete_point_neo4j(point_id)
    KnowledgeRelation.objects.filter(pre_point=point).delete()
    KnowledgeRelation.objects.filter(post_point=point).delete()
    course_id = point.course_id
    point.delete()
    refresh_course_rag_index(course_id)
    return success_response(msg="知识点删除成功")
