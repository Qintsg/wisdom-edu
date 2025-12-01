"""
知识图谱模块 - 视图

提供知识图谱、知识点、资源相关的API端点。
优先使用Neo4j查询知识图谱数据，Neo4j不可用时降级到PostgreSQL并输出警告。
"""

import logging
from collections.abc import Iterable

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.responses import success_response, error_response
from common.permissions import IsTeacherOrAdmin
from common.utils import resolve_course_id as _resolve_course_id
from common.neo4j_service import neo4j_service
from platform_ai.rag import student_learning_rag
from .models import KnowledgePoint, KnowledgeRelation, KnowledgeMastery, Resource
from .serializers import KnowledgePointDetailSerializer


logger = logging.getLogger(__name__)


def _build_postgresql_knowledge_map_payload(course_id: int, mastery_dict: dict[int, float]) -> dict[str, object]:
    """
    使用 PostgreSQL 构建知识图谱回退载荷。
    :param course_id: 课程 ID。
    :param mastery_dict: 掌握度映射。
    :return: 与 Neo4j 版本一致的节点边数据。
    """

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
            # 显式转换掌握度为浮点数，避免混合类型影响平均值计算。
            "avg_mastery": round(
                sum(float(node.get("mastery_rate", 0) or 0) for node in nodes) / len(nodes),
                3,
            )
            if nodes
            else 0,
            "data_source": "postgresql",
        },
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_map(request):
    """
    获取课程知识图谱数据
    GET /api/knowledge-map

    优先从Neo4j查询，不可用时降级到PostgreSQL并输出警告。
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    user = request.user

    mastery_dict = {}
    if user.is_authenticated:
        mastery_records = KnowledgeMastery.objects.filter(
            user=user, course_id=course_id
        )

        for m in mastery_records:
            kp_id = getattr(m, "knowledge_point_id", None) or (
                m.knowledge_point.id if getattr(m, "knowledge_point", None) else None
            )
            if kp_id is not None:
                mastery_dict[kp_id] = float(m.mastery_rate)

    if not neo4j_service.is_available:
        logger.warning("[get_knowledge_map] Neo4j不可用，降级使用PostgreSQL查询课程 %s 的图谱", course_id)
        return success_response(data=_build_postgresql_knowledge_map_payload(course_id, mastery_dict))

    neo4j_data = neo4j_service.get_knowledge_map(course_id, published_only=True)
    # Neo4j 返回空图时回退到 PostgreSQL，避免前端拿到空知识图谱。
    if not neo4j_data or not neo4j_data.get("nodes"):
        logger.warning("[get_knowledge_map] Neo4j图数据为空，降级使用PostgreSQL查询课程 %s 的图谱", course_id)
        return success_response(data=_build_postgresql_knowledge_map_payload(course_id, mastery_dict))

    nodes = []
    for n in neo4j_data["nodes"]:
        pid = n.get("point_id")
        nodes.append(
            {
                "point_id": pid,
                "point_name": n.get("point_name", ""),
                "mastery_rate": mastery_dict.get(pid, 0),
                "chapter": n.get("chapter", ""),
                "type": n.get("type", "knowledge"),
                "level": n.get("level", 1),
                "tags": n.get("tags", ""),
                "cognitive_dimension": n.get("cognitive_dimension", ""),
                "category": n.get("category", ""),
                "teaching_goal": n.get("teaching_goal", ""),
                "description": n.get("description", ""),
            }
        )

    edges = [
        {
            "source": e.get("source"),
            "target": e.get("target"),
            "relation_type": e.get("relation_type", "prerequisite"),
        }
        for e in neo4j_data.get("edges", [])
    ]

    return success_response(
        data={
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "course_id": course_id,
                "node_count": len(nodes),
                "edge_count": len(edges),
                "avg_mastery": round(
                    sum(n.get("mastery_rate", 0) for n in nodes) / len(nodes), 3
                )
                if nodes
                else 0,
                "data_source": "neo4j",
            },
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_point_detail(request, point_id):
    """
    获取知识点详情
    GET /api/knowledge-points/{point_id}

    优先从Neo4j获取关系数据，资源和掌握度始终从PostgreSQL获取。
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    try:
        point = KnowledgePoint.objects.get(id=point_id, course_id=course_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    user = request.user

    mastery = KnowledgeMastery.objects.filter(user=user, knowledge_point=point).first()
    mastery_rate = float(mastery.mastery_rate) if mastery else 0

    if not neo4j_service.is_available:
        prerequisites = [
            {"point_id": relation.pre_point_id, "point_name": relation.pre_point.name}
            for relation in point.pre_relations.select_related("pre_point")
        ]
        postrequisites = [
            {"point_id": relation.post_point_id, "point_name": relation.post_point.name}
            for relation in point.post_relations.select_related("post_point")
        ]
        data_source = "postgresql"
    else:
        neo4j_point = neo4j_service.get_knowledge_point_neo4j(point_id)
        if neo4j_point is None:
            prerequisites = [
                {"point_id": relation.pre_point_id, "point_name": relation.pre_point.name}
                for relation in point.pre_relations.select_related("pre_point")
            ]
            postrequisites = [
                {"point_id": relation.post_point_id, "point_name": relation.post_point.name}
                for relation in point.post_relations.select_related("post_point")
            ]
            data_source = "postgresql"
        else:
            prerequisites = neo4j_point.get("prerequisites", [])
            postrequisites = neo4j_point.get("postrequisites", [])
            data_source = "neo4j"

    resources = getattr(point, "resources", Resource.objects.none())
    resources = resources.filter(is_visible=True).order_by("sort_order", "id")

    resource_list = []
    for r in resources:
        item = {
            "resource_id": getattr(r, "id", None) or getattr(r, "pk", None),
            "title": r.title,
            "type": r.resource_type,
            "chapter_number": r.chapter_number,
            "sort_order": r.sort_order,
        }

        if r.file:
            # 先安全提取文件 URL，再按需补全为绝对地址。
            try:
                file_url = r.file.url
            except (AttributeError, ValueError):
                file_url = ""

            if file_url:
                try:
                    item["url"] = request.build_absolute_uri(file_url)
                except ValueError:
                    item["url"] = file_url
            else:
                item["url"] = ""
        elif r.url:
            item["url"] = r.url
        else:
            item["url"] = "#"

        if r.resource_type == "video" and r.duration:
            item["duration"] = r.duration
            minutes = r.duration // 60
            seconds = r.duration % 60
            item["duration_display"] = f"{minutes:02d}:{seconds:02d}"
        resource_list.append(item)

    # 额外提供 GraphRAG 证据摘要，供知识图谱详情和 AI 助手共享解释依据。
    try:
        graph_rag_support = student_learning_rag.build_point_support_payload(
            course_id=course_id,
            point=point,
        )
    except Exception as error:
        logger.warning("知识点详情 GraphRAG 摘要生成失败: point=%s error=%s", point_id, error)
        graph_rag_support = {
            "summary": "",
            "sources": [],
            "mode": "graph_rag_error",
        }

    return success_response(
        data={
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
            "resources": resource_list,
            "examples": [],
            "data_source": data_source,
            "graph_rag_summary": graph_rag_support.get("summary", ""),
            "graph_rag_sources": graph_rag_support.get("sources", []),
            "graph_rag_mode": graph_rag_support.get("mode", "graph_rag"),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_relations(request):
    """
    获取课程知识点关系列表
    GET /api/knowledge/relations

    优先从Neo4j查询，不可用时降级到PostgreSQL。

    查询参数：
    - course_id: 课程ID（必填）
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    neo4j_relations = neo4j_service.get_knowledge_relations_neo4j(course_id)

    if neo4j_relations is not None:
        relation_list = [
            {
                "id": r.get("relation_id"),
                "pre_point_id": r.get("pre_point_id"),
                "pre_point_name": r.get("pre_point_name", ""),
                "post_point_id": r.get("post_point_id"),
                "post_point_name": r.get("post_point_name", ""),
                "relation_type": r.get("relation_type", "prerequisite"),
            }
            for r in neo4j_relations
        ]
        data_source = "neo4j"
    else:
        # PostgreSQL降级
        logger.warning(
            f"[get_knowledge_relations] Neo4j不可用，降级使用PostgreSQL查询课程 {course_id} 的关系"
        )

        relations = KnowledgeRelation.objects.filter(
            course_id=course_id
        ).select_related("pre_point", "post_point")

        relation_list = [
            {
                "id": getattr(r, "id", None) or getattr(r, "pk", None),
                "pre_point_id": getattr(r, "pre_point_id", None),
                "pre_point_name": r.pre_point.name,
                "post_point_id": getattr(r, "post_point_id", None),
                "post_point_name": r.post_point.name,
                "relation_type": r.relation_type,
            }
            for r in relations
        ]
        data_source = "postgresql"

    return success_response(
        data={
            "course_id": course_id,
            "relations": relation_list,
            "count": len(relation_list),
            "data_source": data_source,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_points_list(request):
    """
    获取课程知识点列表
    GET /api/knowledge/points

    优先从Neo4j查询，不可用时降级到PostgreSQL。
    注意：Neo4j查询不支持chapter/type筛选时降级到PostgreSQL。

    查询参数：
    - course_id: 课程ID（必填）
    - chapter: 章节筛选（可选）
    - type: 知识点类型筛选（可选）
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    chapter = request.query_params.get("chapter")
    point_type = request.query_params.get("type")

    # 有筛选条件时直接用PostgreSQL（Neo4j不适合复杂属性筛选）
    use_neo4j = not chapter and not point_type

    if use_neo4j:
        neo4j_points = neo4j_service.get_knowledge_points_neo4j(course_id)
    else:
        neo4j_points = None

    # 统一转成列表，避免 Optional/Any 影响后续遍历推断。
    neo4j_point_records = list(neo4j_points) if isinstance(neo4j_points, Iterable) else []

    if neo4j_point_records:
        points_list = [
            {
                "id": p.get("id"),
                "name": p.get("name", ""),
                "chapter": p.get("chapter", ""),
                "type": p.get("type", "knowledge"),
                "description": p.get("description", ""),
                "is_published": p.get("is_published", True),
            }
            for p in neo4j_point_records
        ]
        data_source = "neo4j"
    else:
        # PostgreSQL降级
        if use_neo4j:
            logger.warning(
                f"[get_knowledge_points_list] Neo4j不可用，降级使用PostgreSQL查询课程 {course_id} 的知识点"
            )

        queryset = KnowledgePoint.objects.filter(course_id=course_id)

        if chapter:
            queryset = queryset.filter(chapter=chapter)
        if point_type:
            queryset = queryset.filter(point_type=point_type)

        points_list = [
            {
                "id": getattr(p, "id", None) or getattr(p, "pk", None),
                "name": p.name,
                "chapter": p.chapter,
                "type": p.point_type,
                "description": p.description,
                "is_published": p.is_published,
            }
            for p in queryset
        ]
        data_source = "postgresql"

    return success_response(
        data={
            "course_id": course_id,
            "points": points_list,
            "count": len(points_list),
            "data_source": data_source,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_knowledge_mastery(request):
    """
    获取用户知识掌握度
    GET /api/knowledge/mastery

    查询参数：
    - course_id: 课程ID（必填）
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    user = request.user

    mastery_records = KnowledgeMastery.objects.filter(
        user=user, course_id=course_id
    ).select_related("knowledge_point")

    mastery_list = [
        {
            "point_id": m.knowledge_point.id if m.knowledge_point else None,
            "point_name": m.knowledge_point.name if m.knowledge_point else None,
            "mastery_rate": float(m.mastery_rate) if m.mastery_rate else 0,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None,
        }
        for m in mastery_records
    ]

    avg_mastery = 0
    if mastery_list:
        avg_mastery = sum(m["mastery_rate"] for m in mastery_list) / len(mastery_list)

    return success_response(
        data={
            "course_id": course_id,
            "user_id": user.id,
            "average_mastery": round(avg_mastery, 3),
            "mastery": mastery_list,
            "count": len(mastery_list),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_student_resources(request):
    """
    获取课程学习资源列表（学生端）
    GET /api/student/resources
    """
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    qs = Resource.objects.filter(course_id=course_id, is_visible=True)

    # 排序
    sort = request.query_params.get("sort", "default")
    if sort == "title":
        qs = qs.order_by("title", "id")
    elif sort == "type":
        qs = qs.order_by("resource_type", "title", "id")
    elif sort == "newest":
        qs = qs.order_by("-created_at", "-id")
    else:
        qs = qs.order_by("chapter_number", "sort_order", "resource_type", "title", "id")

    # 筛选
    resource_type = request.query_params.get("type")
    keyword = request.query_params.get("keyword")
    point_id = request.query_params.get("point_id")

    if resource_type:
        qs = qs.filter(resource_type=resource_type)
    if keyword:
        qs = qs.filter(title__icontains=keyword)
    if point_id:
        qs = qs.filter(knowledge_points__id=point_id)

    # 分页
    try:
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
    except (ValueError, TypeError):
        page, page_size = 1, 20
    page = max(page, 1)
    page_size = max(1, min(page_size, 100))
    total = qs.count()
    resources = qs[(page - 1) * page_size : page * page_size]

    return success_response(
        data={
            "resources": [
                {
                    "id": r.id,
                    "title": r.title,
                    "resource_type": r.resource_type,
                    "description": r.description or "",
                    "url": r.url or "",
                    "file": r.file.url if r.file else "",
                    "duration": r.duration,
                    "chapter_number": r.chapter_number or "",
                    "sort_order": r.sort_order,
                    "knowledge_points": [
                        {
                            "id": getattr(kp, "id", None) or getattr(kp, "pk", None),
                            "name": getattr(kp, "name", ""),
                        }
                        for kp in r.knowledge_points.all()
                    ],
                    "created_at": r.created_at.isoformat() if r.created_at else "",
                }
                for r in resources.prefetch_related("knowledge_points")
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    )


# ============ 知识点掌握度更新 ============


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_knowledge_mastery(request):
    """
    手动更新知识点掌握度
    PUT /api/student/knowledge/mastery/update
    """
    # 兼容前端两种参数名: point_id / knowledge_point_id, mastery / mastery_rate
    point_id = request.data.get("knowledge_point_id") or request.data.get("point_id")
    mastery_rate = request.data.get("mastery_rate")
    if mastery_rate is None:
        # 前端传 mastery (0-100)，需要转换为 0-1
        mastery_raw = request.data.get("mastery")
        if mastery_raw is not None:
            try:
                mastery_rate = float(mastery_raw) / 100.0
            except (ValueError, TypeError):
                return error_response(msg="mastery 格式错误")

    if point_id is None or mastery_rate is None:
        return error_response(
            msg="请提供 knowledge_point_id/point_id 和 mastery_rate/mastery"
        )

    try:
        mastery_rate = float(mastery_rate)
        if not 0 <= mastery_rate <= 1:
            return error_response(msg="掌握度范围为 0~1")
    except (ValueError, TypeError):
        return error_response(msg="mastery_rate 格式错误")

    try:
        kp = KnowledgePoint.objects.get(id=point_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    mastery, created = KnowledgeMastery.objects.update_or_create(
        user=request.user,
        knowledge_point=kp,
        defaults={"mastery_rate": mastery_rate, "course_id": kp.course_id},
    )

    return success_response(
        data={
            "knowledge_point_id": kp.id,
            "mastery_rate": float(mastery.mastery_rate),
            "created": created,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def knowledge_point_resources(request, point_id):
    """
    获取知识点相关资源
    GET /api/student/knowledge-points/{point_id}/resources
    """
    try:
        kp = KnowledgePoint.objects.get(id=point_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    resources = Resource.objects.filter(knowledge_points=kp, is_visible=True).order_by(
        "sort_order"
    )

    return success_response(
        data=[
            {
                "id": r.id,
                "title": r.title,
                "resource_type": r.resource_type,
                "url": r.url or "",
                "file": r.file.url if r.file else "",
                "duration": r.duration,
            }
            for r in resources
        ]
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def knowledge_search(request):
    """
    搜索知识点
    GET /api/student/knowledge/search
    """
    keyword = request.query_params.get("keyword", "")
    course_id = request.query_params.get("course_id")

    if not keyword:
        return error_response(msg="请提供搜索关键字")

    qs = KnowledgePoint.objects.filter(name__icontains=keyword)
    if course_id:
        qs = qs.filter(course_id=course_id)

    qs = qs[:50]

    return success_response(
        data=[
            {
                "id": kp.id,
                "name": kp.name,
                "description": kp.description or "",
                "course_id": kp.course_id,
            }
            for kp in qs
        ]
    )
