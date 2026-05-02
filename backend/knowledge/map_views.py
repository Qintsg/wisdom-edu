"""知识图谱、知识点详情与掌握度接口。"""

import logging
from collections.abc import Iterable

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.neo4j_service import neo4j_service
from common.responses import error_response, success_response
from common.utils import resolve_course_id as _resolve_course_id
from platform_ai.rag import student_learning_rag
from .models import KnowledgeMastery, KnowledgePoint, KnowledgeRelation, Resource


logger = logging.getLogger(__name__)


def _build_postgresql_knowledge_map_payload(course_id: int, mastery_dict: dict[int, float]) -> dict[str, object]:
    """使用 PostgreSQL 构建知识图谱回退载荷。"""
    points = KnowledgePoint.objects.filter(course_id=course_id, is_published=True).order_by("order", "id")
    relations = KnowledgeRelation.objects.filter(course_id=course_id).order_by("id")
    nodes = [
        {
            "point_id": point.id,
            "point_name": point.name,
            "mastery_rate": mastery_dict.get(point.id, 0),
            "chapter": point.chapter or "",
            "type": point.point_type,
            "level": point.level,
            "tags": point.tags or "",
            "cognitive_dimension": point.cognitive_dimension or "",
            "category": point.category or "",
            "teaching_goal": point.teaching_goal or "",
            "description": point.description or "",
        }
        for point in points
    ]
    edges = [
        {
            "source": relation.pre_point_id,
            "target": relation.post_point_id,
            "relation_type": relation.relation_type or "prerequisite",
        }
        for relation in relations
    ]
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "course_id": course_id,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "avg_mastery": round(sum(float(node.get("mastery_rate", 0) or 0) for node in nodes) / len(nodes), 3) if nodes else 0,
            "data_source": "postgresql",
        },
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_map(request):
    """获取课程知识图谱数据，优先 Neo4j，空图或不可用时回退 PostgreSQL。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    mastery_dict = {}
    if request.user.is_authenticated:
        mastery_records = KnowledgeMastery.objects.filter(user=request.user, course_id=course_id)
        for mastery in mastery_records:
            kp_id = getattr(mastery, "knowledge_point_id", None) or (
                mastery.knowledge_point.id if getattr(mastery, "knowledge_point", None) else None
            )
            if kp_id is not None:
                mastery_dict[kp_id] = float(mastery.mastery_rate)

    if not neo4j_service.is_available:
        logger.warning("[get_knowledge_map] Neo4j不可用，降级使用PostgreSQL查询课程 %s 的图谱", course_id)
        return success_response(data=_build_postgresql_knowledge_map_payload(course_id, mastery_dict))

    neo4j_data = neo4j_service.get_knowledge_map(course_id, published_only=True)
    if not neo4j_data or not neo4j_data.get("nodes"):
        logger.warning("[get_knowledge_map] Neo4j图数据为空，降级使用PostgreSQL查询课程 %s 的图谱", course_id)
        return success_response(data=_build_postgresql_knowledge_map_payload(course_id, mastery_dict))

    nodes = [
        {
            "point_id": node.get("point_id"),
            "point_name": node.get("point_name", ""),
            "mastery_rate": mastery_dict.get(node.get("point_id"), 0),
            "chapter": node.get("chapter", ""),
            "type": node.get("type", "knowledge"),
            "level": node.get("level", 1),
            "tags": node.get("tags", ""),
            "cognitive_dimension": node.get("cognitive_dimension", ""),
            "category": node.get("category", ""),
            "teaching_goal": node.get("teaching_goal", ""),
            "description": node.get("description", ""),
        }
        for node in neo4j_data["nodes"]
    ]
    edges = [
        {
            "source": edge.get("source"),
            "target": edge.get("target"),
            "relation_type": edge.get("relation_type", "prerequisite"),
        }
        for edge in neo4j_data.get("edges", [])
    ]
    return success_response(data={
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "course_id": course_id,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "avg_mastery": round(sum(node.get("mastery_rate", 0) for node in nodes) / len(nodes), 3) if nodes else 0,
            "data_source": "neo4j",
        },
    })


def _postgresql_point_relations(point: KnowledgePoint) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """读取 PostgreSQL 中的前置与后继知识点。"""
    prerequisites = [
        {"point_id": relation.pre_point_id, "point_name": relation.pre_point.name}
        for relation in point.pre_relations.select_related("pre_point")
    ]
    postrequisites = [
        {"point_id": relation.post_point_id, "point_name": relation.post_point.name}
        for relation in point.post_relations.select_related("post_point")
    ]
    return prerequisites, postrequisites


def _build_resource_payload(request, resources) -> list[dict[str, object]]:
    """构建知识点详情中的资源载荷。"""
    resource_list = []
    for resource in resources:
        item = {
            "resource_id": getattr(resource, "id", None) or getattr(resource, "pk", None),
            "title": resource.title,
            "type": resource.resource_type,
            "chapter_number": resource.chapter_number,
            "sort_order": resource.sort_order,
        }
        if resource.file:
            try:
                file_url = resource.file.url
            except (AttributeError, ValueError):
                file_url = ""
            if file_url:
                try:
                    item["url"] = request.build_absolute_uri(file_url)
                except ValueError:
                    item["url"] = file_url
            else:
                item["url"] = ""
        elif resource.url:
            item["url"] = resource.url
        else:
            item["url"] = "#"

        if resource.resource_type == "video" and resource.duration:
            item["duration"] = resource.duration
            item["duration_display"] = f"{resource.duration // 60:02d}:{resource.duration % 60:02d}"
        resource_list.append(item)
    return resource_list


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

    mastery = KnowledgeMastery.objects.filter(user=request.user, knowledge_point=point).first()
    mastery_rate = float(mastery.mastery_rate) if mastery else 0
    if not neo4j_service.is_available:
        prerequisites, postrequisites = _postgresql_point_relations(point)
        data_source = "postgresql"
    else:
        neo4j_point = neo4j_service.get_knowledge_point_neo4j(point_id)
        if neo4j_point is None:
            prerequisites, postrequisites = _postgresql_point_relations(point)
            data_source = "postgresql"
        else:
            prerequisites = neo4j_point.get("prerequisites", [])
            postrequisites = neo4j_point.get("postrequisites", [])
            data_source = "neo4j"

    resources = getattr(point, "resources", Resource.objects.none())
    resources = resources.filter(is_visible=True).order_by("sort_order", "id")
    try:
        graph_rag_support = student_learning_rag.build_point_support_payload(course_id=course_id, point=point)
    except Exception as error:
        logger.warning("知识点详情 GraphRAG 摘要生成失败: point=%s error=%s", point_id, error)
        graph_rag_support = {"summary": "", "sources": [], "mode": "graph_rag_error"}

    return success_response(data={
        "point_id": getattr(point, "id", None) or getattr(point, "pk", None),
        "point_name": point.name,
        "description": point.description,
        "chapter": point.chapter,
        "level": point.level,
        "tags": point.tags or "",
        "cognitive_dimension": point.cognitive_dimension or "",
        "category": point.category or "",
        "teaching_goal": point.teaching_goal or "",
        "mastery_rate": mastery_rate,
        "prerequisites": prerequisites,
        "postrequisites": postrequisites,
        "resources": _build_resource_payload(request, resources),
        "examples": [],
        "data_source": data_source,
        "graph_rag_summary": graph_rag_support.get("summary", ""),
        "graph_rag_sources": graph_rag_support.get("sources", []),
        "graph_rag_mode": graph_rag_support.get("mode", "graph_rag"),
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_relations(request):
    """获取课程知识点关系列表。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    neo4j_relations = neo4j_service.get_knowledge_relations_neo4j(course_id)
    if neo4j_relations is not None:
        relation_list = [
            {
                "id": relation.get("relation_id"),
                "pre_point_id": relation.get("pre_point_id"),
                "pre_point_name": relation.get("pre_point_name", ""),
                "post_point_id": relation.get("post_point_id"),
                "post_point_name": relation.get("post_point_name", ""),
                "relation_type": relation.get("relation_type", "prerequisite"),
            }
            for relation in neo4j_relations
        ]
        data_source = "neo4j"
    else:
        logger.warning("[get_knowledge_relations] Neo4j不可用，降级使用PostgreSQL查询课程 %s 的关系", course_id)
        relations = KnowledgeRelation.objects.filter(course_id=course_id).select_related("pre_point", "post_point")
        relation_list = [
            {
                "id": getattr(relation, "id", None) or getattr(relation, "pk", None),
                "pre_point_id": getattr(relation, "pre_point_id", None),
                "pre_point_name": relation.pre_point.name,
                "post_point_id": getattr(relation, "post_point_id", None),
                "post_point_name": relation.post_point.name,
                "relation_type": relation.relation_type,
            }
            for relation in relations
        ]
        data_source = "postgresql"

    return success_response(data={"course_id": course_id, "relations": relation_list, "count": len(relation_list), "data_source": data_source})


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
    neo4j_point_records = list(neo4j_points) if isinstance(neo4j_points, Iterable) else []

    if neo4j_point_records:
        points_list = [
            {
                "id": point.get("id"),
                "name": point.get("name", ""),
                "chapter": point.get("chapter", ""),
                "type": point.get("type", "knowledge"),
                "description": point.get("description", ""),
                "is_published": point.get("is_published", True),
            }
            for point in neo4j_point_records
        ]
        data_source = "neo4j"
    else:
        if use_neo4j:
            logger.warning("[get_knowledge_points_list] Neo4j不可用，降级使用PostgreSQL查询课程 %s 的知识点", course_id)
        queryset = KnowledgePoint.objects.filter(course_id=course_id)
        if chapter:
            queryset = queryset.filter(chapter=chapter)
        if point_type:
            queryset = queryset.filter(point_type=point_type)
        points_list = [
            {
                "id": getattr(point, "id", None) or getattr(point, "pk", None),
                "name": point.name,
                "chapter": point.chapter,
                "type": point.point_type,
                "description": point.description,
                "is_published": point.is_published,
            }
            for point in queryset
        ]
        data_source = "postgresql"

    return success_response(data={"course_id": course_id, "points": points_list, "count": len(points_list), "data_source": data_source})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_mastery(request):
    """获取用户知识掌握度。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    mastery_records = KnowledgeMastery.objects.filter(user=request.user, course_id=course_id).select_related("knowledge_point")
    mastery_list = [
        {
            "point_id": mastery.knowledge_point.id if mastery.knowledge_point else None,
            "point_name": mastery.knowledge_point.name if mastery.knowledge_point else None,
            "mastery_rate": float(mastery.mastery_rate) if mastery.mastery_rate else 0,
            "updated_at": mastery.updated_at.isoformat() if mastery.updated_at else None,
        }
        for mastery in mastery_records
    ]
    avg_mastery = sum(item["mastery_rate"] for item in mastery_list) / len(mastery_list) if mastery_list else 0
    return success_response(data={
        "course_id": course_id,
        "user_id": request.user.id,
        "average_mastery": round(avg_mastery, 3),
        "mastery": mastery_list,
        "count": len(mastery_list),
    })


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
    return success_response(data={"knowledge_point_id": point.id, "mastery_rate": float(mastery.mastery_rate), "created": created})
