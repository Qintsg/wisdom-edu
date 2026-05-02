"""学生端知识图谱视图辅助工具。"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework.request import Request

from .models import KnowledgeMastery, KnowledgePoint, KnowledgeRelation, Resource


def build_mastery_lookup(*, user: AbstractBaseUser, course_id: int) -> dict[int, float]:
    """读取当前学生在课程内的知识点掌握度索引。"""
    if not user.is_authenticated:
        return {}

    mastery_lookup: dict[int, float] = {}
    mastery_records = KnowledgeMastery.objects.filter(user=user, course_id=course_id)
    for mastery in mastery_records:
        point_id = mastery.knowledge_point_id
        if point_id is not None:
            mastery_lookup[point_id] = float(mastery.mastery_rate)
    return mastery_lookup


def build_postgresql_knowledge_map_payload(
    *,
    course_id: int,
    mastery_lookup: dict[int, float],
) -> dict[str, object]:
    """使用 PostgreSQL 构建知识图谱回退载荷。"""
    points = KnowledgePoint.objects.filter(
        course_id=course_id,
        is_published=True,
    ).order_by("order", "id")
    relations = KnowledgeRelation.objects.filter(course_id=course_id).order_by("id")
    nodes = [
        {
            "point_id": point.id,
            "point_name": point.name,
            "mastery_rate": mastery_lookup.get(point.id, 0),
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
    return build_knowledge_map_response_payload(
        course_id=course_id,
        nodes=nodes,
        edges=edges,
        data_source="postgresql",
    )


def build_neo4j_knowledge_map_payload(
    *,
    course_id: int,
    neo4j_data: Mapping[str, object],
    mastery_lookup: dict[int, float],
) -> dict[str, object]:
    """将 Neo4j 图谱数据规范化为学生端 API 载荷。"""
    nodes = []
    for node in _mapping_records(neo4j_data.get("nodes", [])):
        point_id = node.get("point_id")
        mastery_key = point_id if isinstance(point_id, int) else None
        nodes.append(
            {
                "point_id": point_id,
                "point_name": node.get("point_name", ""),
                "mastery_rate": mastery_lookup.get(mastery_key, 0),
                "chapter": node.get("chapter", ""),
                "type": node.get("type", "knowledge"),
                "level": node.get("level", 1),
                "tags": node.get("tags", ""),
                "cognitive_dimension": node.get("cognitive_dimension", ""),
                "category": node.get("category", ""),
                "teaching_goal": node.get("teaching_goal", ""),
                "description": node.get("description", ""),
            }
        )
    edges = [
        {
            "source": edge.get("source"),
            "target": edge.get("target"),
            "relation_type": edge.get("relation_type", "prerequisite"),
        }
        for edge in _mapping_records(neo4j_data.get("edges", []))
    ]
    return build_knowledge_map_response_payload(
        course_id=course_id,
        nodes=nodes,
        edges=edges,
        data_source="neo4j",
    )


def build_knowledge_map_response_payload(
    *,
    course_id: int,
    nodes: list[dict[str, object]],
    edges: list[dict[str, object]],
    data_source: str,
) -> dict[str, object]:
    """构建图谱响应公共结构，保持统计字段与旧接口一致。"""
    avg_mastery = (
        round(
            sum(float(node.get("mastery_rate", 0) or 0) for node in nodes)
            / len(nodes),
            3,
        )
        if nodes
        else 0
    )
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "course_id": course_id,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "avg_mastery": avg_mastery,
            "data_source": data_source,
        },
    }


def build_postgresql_point_relations(
    point: KnowledgePoint,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
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


def build_resource_payload(
    *,
    request: Request,
    resources: Iterable[Resource],
) -> list[dict[str, object]]:
    """构建知识点详情中的资源载荷。"""
    resource_list = []
    for resource in resources:
        item: dict[str, object] = {
            "resource_id": resource.id,
            "title": resource.title,
            "type": resource.resource_type,
            "chapter_number": resource.chapter_number,
            "sort_order": resource.sort_order,
        }
        item["url"] = _resolve_resource_url(request=request, resource=resource)
        if resource.resource_type == "video" and resource.duration:
            item["duration"] = resource.duration
            item["duration_display"] = (
                f"{resource.duration // 60:02d}:{resource.duration % 60:02d}"
            )
        resource_list.append(item)
    return resource_list


def build_point_detail_payload(
    *,
    request: Request,
    point: KnowledgePoint,
    mastery_rate: float,
    prerequisites: list[dict[str, object]],
    postrequisites: list[dict[str, object]],
    data_source: str,
    graph_rag_support: Mapping[str, object],
) -> dict[str, object]:
    """组装知识点详情响应，避免视图层混入资源与图谱字段细节。"""
    resources = point.resources.filter(is_visible=True).order_by("sort_order", "id")
    return {
        "point_id": point.id,
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
        "resources": build_resource_payload(request=request, resources=resources),
        "examples": [],
        "data_source": data_source,
        "graph_rag_summary": graph_rag_support.get("summary", ""),
        "graph_rag_sources": graph_rag_support.get("sources", []),
        "graph_rag_mode": graph_rag_support.get("mode", "graph_rag"),
    }


def build_neo4j_relations_payload(
    *,
    course_id: int,
    neo4j_relations: object,
) -> dict[str, object]:
    """构建 Neo4j 关系列表响应载荷。"""
    relation_list = [
        {
            "id": relation.get("relation_id"),
            "pre_point_id": relation.get("pre_point_id"),
            "pre_point_name": relation.get("pre_point_name", ""),
            "post_point_id": relation.get("post_point_id"),
            "post_point_name": relation.get("post_point_name", ""),
            "relation_type": relation.get("relation_type", "prerequisite"),
        }
        for relation in _mapping_records(neo4j_relations)
    ]
    return _build_collection_payload(
        course_id=course_id,
        key="relations",
        records=relation_list,
        data_source="neo4j",
    )


def build_postgresql_relations_payload(*, course_id: int) -> dict[str, object]:
    """构建 PostgreSQL 关系列表响应载荷。"""
    relations = KnowledgeRelation.objects.filter(course_id=course_id).select_related(
        "pre_point",
        "post_point",
    )
    relation_list = [
        {
            "id": relation.id,
            "pre_point_id": relation.pre_point_id,
            "pre_point_name": relation.pre_point.name,
            "post_point_id": relation.post_point_id,
            "post_point_name": relation.post_point.name,
            "relation_type": relation.relation_type,
        }
        for relation in relations
    ]
    return _build_collection_payload(
        course_id=course_id,
        key="relations",
        records=relation_list,
        data_source="postgresql",
    )


def build_neo4j_points_payload(
    *,
    course_id: int,
    neo4j_points: object,
) -> dict[str, object] | None:
    """构建 Neo4j 知识点列表响应载荷，空结果交由视图回退。"""
    point_records = _mapping_records(neo4j_points)
    if not point_records:
        return None

    points_list = [
        {
            "id": point.get("id"),
            "name": point.get("name", ""),
            "chapter": point.get("chapter", ""),
            "type": point.get("type", "knowledge"),
            "description": point.get("description", ""),
            "is_published": point.get("is_published", True),
        }
        for point in point_records
    ]
    return _build_collection_payload(
        course_id=course_id,
        key="points",
        records=points_list,
        data_source="neo4j",
    )


def build_postgresql_points_payload(
    *,
    course_id: int,
    chapter: str | None,
    point_type: str | None,
) -> dict[str, object]:
    """构建 PostgreSQL 知识点列表响应载荷。"""
    queryset = KnowledgePoint.objects.filter(course_id=course_id)
    if chapter:
        queryset = queryset.filter(chapter=chapter)
    if point_type:
        queryset = queryset.filter(point_type=point_type)
    points_list = [
        {
            "id": point.id,
            "name": point.name,
            "chapter": point.chapter,
            "type": point.point_type,
            "description": point.description,
            "is_published": point.is_published,
        }
        for point in queryset
    ]
    return _build_collection_payload(
        course_id=course_id,
        key="points",
        records=points_list,
        data_source="postgresql",
    )


def build_mastery_payload(
    *,
    user: AbstractBaseUser,
    course_id: int,
) -> dict[str, object]:
    """构建用户知识掌握度列表响应载荷。"""
    mastery_records = KnowledgeMastery.objects.filter(
        user=user,
        course_id=course_id,
    ).select_related("knowledge_point")
    mastery_list = [
        {
            "point_id": (
                mastery.knowledge_point.id if mastery.knowledge_point else None
            ),
            "point_name": (
                mastery.knowledge_point.name if mastery.knowledge_point else None
            ),
            "mastery_rate": float(mastery.mastery_rate)
            if mastery.mastery_rate
            else 0,
            "updated_at": mastery.updated_at.isoformat()
            if mastery.updated_at
            else None,
        }
        for mastery in mastery_records
    ]
    average_mastery = (
        sum(item["mastery_rate"] for item in mastery_list) / len(mastery_list)
        if mastery_list
        else 0
    )
    return {
        "course_id": course_id,
        "user_id": user.id,
        "average_mastery": round(average_mastery, 3),
        "mastery": mastery_list,
        "count": len(mastery_list),
    }


def normalize_relation_records(value: object) -> list[dict[str, object]]:
    """将 Neo4j 关系字段规范为列表，异常结构按空列表处理。"""
    return [dict(item) for item in _mapping_records(value)]


def _mapping_records(value: object) -> list[Mapping[str, object]]:
    """筛选图服务返回值中的映射记录，隔离外部数据形态波动。"""
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _resolve_resource_url(*, request: Request, resource: Resource) -> str:
    """解析资源 URL，兼容文件字段缺失或存储后端未返回 URL 的情况。"""
    if resource.file:
        try:
            file_url = resource.file.url
        except (AttributeError, ValueError):
            file_url = ""
        if not file_url:
            return ""
        try:
            return request.build_absolute_uri(file_url)
        except ValueError:
            return file_url
    if resource.url:
        return resource.url
    return "#"


def _build_collection_payload(
    *,
    course_id: int,
    key: str,
    records: list[dict[str, object]],
    data_source: str,
) -> dict[str, object]:
    """构建列表类接口通用响应结构。"""
    return {
        "course_id": course_id,
        key: records,
        "count": len(records),
        "data_source": data_source,
    }
