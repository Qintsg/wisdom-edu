"""学生端知识图谱视图辅助工具。"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework.request import Request

from .models import KnowledgeMastery, KnowledgePoint, KnowledgeRelation, Resource


# 维护意图：读取当前学生在课程内的知识点掌握度索引
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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


# 维护意图：使用 PostgreSQL 构建知识图谱回退载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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
            "mastery_rate": read_mastery_rate(mastery_lookup, point.id),
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


# 维护意图：将 Neo4j 图谱数据规范化为学生端 API 载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_neo4j_knowledge_map_payload(
    *,
    course_id: int,
    neo4j_data: Mapping[str, object],
    mastery_lookup: dict[int, float],
) -> dict[str, object]:
    """将 Neo4j 图谱数据规范化为学生端 API 载荷。"""
    nodes = []
    for node in mapping_records(read_mapping_field(neo4j_data, "nodes", [])):
        point_id = read_mapping_field(node, "point_id")
        mastery_key = point_id if isinstance(point_id, int) else None
        nodes.append(
            {
                "point_id": point_id,
                "point_name": read_mapping_field(node, "point_name", ""),
                "mastery_rate": read_mastery_rate(mastery_lookup, mastery_key),
                "chapter": read_mapping_field(node, "chapter", ""),
                "type": read_mapping_field(node, "type", "knowledge"),
                "level": read_mapping_field(node, "level", 1),
                "tags": read_mapping_field(node, "tags", ""),
                "cognitive_dimension": read_mapping_field(node, "cognitive_dimension", ""),
                "category": read_mapping_field(node, "category", ""),
                "teaching_goal": read_mapping_field(node, "teaching_goal", ""),
                "description": read_mapping_field(node, "description", ""),
            }
        )
    edges = [
        {
            "source": read_mapping_field(edge, "source"),
            "target": read_mapping_field(edge, "target"),
            "relation_type": read_mapping_field(edge, "relation_type", "prerequisite"),
        }
        for edge in mapping_records(read_mapping_field(neo4j_data, "edges", []))
    ]
    return build_knowledge_map_response_payload(
        course_id=course_id,
        nodes=nodes,
        edges=edges,
        data_source="neo4j",
    )


# 维护意图：构建图谱响应公共结构，保持统计字段与旧接口一致
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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
            sum(float(read_mapping_field(node, "mastery_rate", 0) or 0) for node in nodes)
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


# 维护意图：读取 PostgreSQL 中的前置与后继知识点
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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


# 维护意图：构建知识点详情中的资源载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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
        item["url"] = resolve_resource_url(request=request, resource=resource)
        if resource.resource_type == "video" and resource.duration:
            item["duration"] = resource.duration
            item["duration_display"] = (
                f"{resource.duration // 60:02d}:{resource.duration % 60:02d}"
            )
        resource_list.append(item)
    return resource_list


# 维护意图：组装知识点详情响应，避免视图层混入资源与图谱字段细节
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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
        "graph_rag_summary": read_mapping_field(graph_rag_support, "summary", ""),
        "graph_rag_sources": read_mapping_field(graph_rag_support, "sources", []),
        "graph_rag_mode": read_mapping_field(graph_rag_support, "mode", "graph_rag"),
    }


# 维护意图：构建 Neo4j 关系列表响应载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_neo4j_relations_payload(
    *,
    course_id: int,
    neo4j_relations: object,
) -> dict[str, object]:
    """构建 Neo4j 关系列表响应载荷。"""
    relation_list = [
        {
            "id": read_mapping_field(relation, "relation_id"),
            "pre_point_id": read_mapping_field(relation, "pre_point_id"),
            "pre_point_name": read_mapping_field(relation, "pre_point_name", ""),
            "post_point_id": read_mapping_field(relation, "post_point_id"),
            "post_point_name": read_mapping_field(relation, "post_point_name", ""),
            "relation_type": read_mapping_field(relation, "relation_type", "prerequisite"),
        }
        for relation in mapping_records(neo4j_relations)
    ]
    return build_collection_payload(
        course_id=course_id,
        key="relations",
        records=relation_list,
        data_source="neo4j",
    )


# 维护意图：构建 PostgreSQL 关系列表响应载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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
    return build_collection_payload(
        course_id=course_id,
        key="relations",
        records=relation_list,
        data_source="postgresql",
    )


# 维护意图：构建 Neo4j 知识点列表响应载荷，空结果交由视图回退
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_neo4j_points_payload(
    *,
    course_id: int,
    neo4j_points: object,
) -> dict[str, object] | None:
    """构建 Neo4j 知识点列表响应载荷，空结果交由视图回退。"""
    point_records = mapping_records(neo4j_points)
    if not point_records:
        return None

    points_list = [
        {
            "id": read_mapping_field(point, "id"),
            "name": read_mapping_field(point, "name", ""),
            "chapter": read_mapping_field(point, "chapter", ""),
            "type": read_mapping_field(point, "type", "knowledge"),
            "description": read_mapping_field(point, "description", ""),
            "is_published": read_mapping_field(point, "is_published", True),
        }
        for point in point_records
    ]
    return build_collection_payload(
        course_id=course_id,
        key="points",
        records=points_list,
        data_source="neo4j",
    )


# 维护意图：构建 PostgreSQL 知识点列表响应载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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
    return build_collection_payload(
        course_id=course_id,
        key="points",
        records=points_list,
        data_source="postgresql",
    )


# 维护意图：构建用户知识掌握度列表响应载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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


# 维护意图：将 Neo4j 关系字段规范为列表，异常结构按空列表处理
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_relation_records(value: object) -> list[dict[str, object]]:
    """将 Neo4j 关系字段规范为列表，异常结构按空列表处理。"""
    return [dict(item) for item in mapping_records(value)]


# 维护意图：读取外部图服务返回字段，集中表达默认值语义
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def read_mapping_field(record: Mapping[str, object], key: str, default: object = None) -> object:
    """读取外部图服务返回字段，集中表达默认值语义。"""
    return record.get(key, default)


# 维护意图：读取掌握度索引，缺失或空知识点统一按 0 处理
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def read_mastery_rate(mastery_lookup: dict[int, float], point_id: int | None) -> float:
    """读取掌握度索引，缺失或空知识点统一按 0 处理。"""
    return mastery_lookup.get(point_id, 0) if point_id is not None else 0


# 维护意图：筛选图服务返回值中的映射记录，隔离外部数据形态波动
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def mapping_records(value: object) -> list[Mapping[str, object]]:
    """筛选图服务返回值中的映射记录，隔离外部数据形态波动。"""
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


# 维护意图：解析资源 URL，兼容文件字段缺失或存储后端未返回 URL 的情况
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_resource_url(*, request: Request, resource: Resource) -> str:
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


# 维护意图：构建列表类接口通用响应结构
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_collection_payload(
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
