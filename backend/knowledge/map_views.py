"""知识图谱、知识点详情与掌握度接口。"""

import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.neo4j_service import neo4j_service
from common.responses import error_response, success_response
from common.utils import resolve_course_id as _resolve_course_id
from platform_ai.rag import student_learning_rag
from .map_support import (
    build_mastery_lookup,
    build_mastery_payload,
    build_neo4j_knowledge_map_payload,
    build_neo4j_points_payload,
    build_neo4j_relations_payload,
    build_point_detail_payload,
    build_postgresql_knowledge_map_payload,
    build_postgresql_points_payload,
    build_postgresql_point_relations,
    build_postgresql_relations_payload,
    normalize_relation_records,
)
from .models import KnowledgeMastery, KnowledgePoint


logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_map(request):
    """获取课程知识图谱数据，优先 Neo4j，空图或不可用时回退 PostgreSQL。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    mastery_lookup = build_mastery_lookup(user=request.user, course_id=course_id)

    if not neo4j_service.is_available:
        logger.warning("[get_knowledge_map] Neo4j不可用，降级使用PostgreSQL查询课程 %s 的图谱", course_id)
        return success_response(
            data=build_postgresql_knowledge_map_payload(
                course_id=course_id,
                mastery_lookup=mastery_lookup,
            )
        )

    neo4j_data = neo4j_service.get_knowledge_map(course_id, published_only=True)
    if not neo4j_data or not neo4j_data.get("nodes"):
        logger.warning("[get_knowledge_map] Neo4j图数据为空，降级使用PostgreSQL查询课程 %s 的图谱", course_id)
        return success_response(
            data=build_postgresql_knowledge_map_payload(
                course_id=course_id,
                mastery_lookup=mastery_lookup,
            )
        )

    return success_response(
        data=build_neo4j_knowledge_map_payload(
            course_id=course_id,
            neo4j_data=neo4j_data,
            mastery_lookup=mastery_lookup,
        )
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_point_detail(request, point_id):
    """获取知识点详情。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    try:
        point = KnowledgePoint.objects.get(id=point_id, course_id=course_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    mastery = KnowledgeMastery.objects.filter(
        user=request.user,
        knowledge_point=point,
    ).first()
    mastery_rate = float(mastery.mastery_rate) if mastery else 0
    if not neo4j_service.is_available:
        prerequisites, postrequisites = build_postgresql_point_relations(point)
        data_source = "postgresql"
    else:
        neo4j_point = neo4j_service.get_knowledge_point_neo4j(point_id)
        if neo4j_point is None:
            prerequisites, postrequisites = build_postgresql_point_relations(point)
            data_source = "postgresql"
        else:
            prerequisites = normalize_relation_records(
                neo4j_point.get("prerequisites", [])
            )
            postrequisites = normalize_relation_records(
                neo4j_point.get("postrequisites", [])
            )
            data_source = "neo4j"

    try:
        graph_rag_support = student_learning_rag.build_point_support_payload(
            course_id=course_id,
            point=point,
        )
    except Exception as error:
        logger.warning("知识点详情 GraphRAG 摘要生成失败: point=%s error=%s", point_id, error)
        graph_rag_support = {"summary": "", "sources": [], "mode": "graph_rag_error"}

    return success_response(
        data=build_point_detail_payload(
            request=request,
            point=point,
            mastery_rate=mastery_rate,
            prerequisites=prerequisites,
            postrequisites=postrequisites,
            data_source=data_source,
            graph_rag_support=graph_rag_support,
        )
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_relations(request):
    """获取课程知识点关系列表。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    neo4j_relations = neo4j_service.get_knowledge_relations_neo4j(course_id)
    if neo4j_relations is not None:
        return success_response(
            data=build_neo4j_relations_payload(
                course_id=course_id,
                neo4j_relations=neo4j_relations,
            )
        )

    logger.warning(
        "[get_knowledge_relations] Neo4j不可用，降级使用PostgreSQL查询课程 %s 的关系",
        course_id,
    )
    return success_response(
        data=build_postgresql_relations_payload(course_id=course_id)
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_points_list(request):
    """获取课程知识点列表。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    chapter = request.query_params.get("chapter")
    point_type = request.query_params.get("type")
    use_neo4j = not chapter and not point_type
    neo4j_points = neo4j_service.get_knowledge_points_neo4j(course_id) if use_neo4j else None

    neo4j_payload = build_neo4j_points_payload(
        course_id=course_id,
        neo4j_points=neo4j_points,
    )
    if neo4j_payload:
        return success_response(data=neo4j_payload)

    if use_neo4j:
        logger.warning(
            "[get_knowledge_points_list] Neo4j不可用，降级使用PostgreSQL查询课程 %s 的知识点",
            course_id,
        )
    return success_response(
        data=build_postgresql_points_payload(
            course_id=course_id,
            chapter=chapter,
            point_type=point_type,
        )
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_mastery(request):
    """获取用户知识掌握度。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    return success_response(
        data=build_mastery_payload(user=request.user, course_id=course_id)
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_knowledge_mastery(request):
    """手动更新知识点掌握度。"""
    point_id = request.data.get("knowledge_point_id") or request.data.get("point_id")
    mastery_rate = request.data.get("mastery_rate")
    if mastery_rate is None:
        mastery_raw = request.data.get("mastery")
        if mastery_raw is not None:
            try:
                mastery_rate = float(mastery_raw) / 100.0
            except (ValueError, TypeError):
                return error_response(msg="mastery 格式错误")

    if point_id is None or mastery_rate is None:
        return error_response(msg="请提供 knowledge_point_id/point_id 和 mastery_rate/mastery")
    try:
        mastery_rate = float(mastery_rate)
        if not 0 <= mastery_rate <= 1:
            return error_response(msg="掌握度范围为 0~1")
    except (ValueError, TypeError):
        return error_response(msg="mastery_rate 格式错误")

    try:
        point = KnowledgePoint.objects.get(id=point_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    mastery, created = KnowledgeMastery.objects.update_or_create(
        user=request.user,
        knowledge_point=point,
        defaults={"mastery_rate": mastery_rate, "course_id": point.course_id},
    )
    return success_response(
        data={
            "knowledge_point_id": point.id,
            "mastery_rate": float(mastery.mastery_rate),
            "created": created,
        }
    )
