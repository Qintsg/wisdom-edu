"""教师端知识关系管理视图。"""
from __future__ import annotations

import logging

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


# 维护意图：获取知识点关系列表，优先 Neo4j，不可用时降级 PostgreSQL
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_relation_list(request: Request) -> Response:
    """获取知识点关系列表，优先 Neo4j，不可用时降级 PostgreSQL。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    neo4j_relations = neo4j_service.get_knowledge_relations_neo4j(course_id)
    if neo4j_relations is not None:
        return success_response(data={
            "relations": [{
                "relation_id": relation.get("relation_id"),
                "from_point_id": relation.get("pre_point_id"),
                "from_point_name": relation.get("pre_point_name", ""),
                "to_point_id": relation.get("post_point_id"),
                "to_point_name": relation.get("post_point_name", ""),
                "relation_type": relation.get("relation_type", "prerequisite"),
            } for relation in neo4j_relations],
            "count": len(neo4j_relations),
            "data_source": "neo4j",
        })

    logger.warning("[knowledge_relation_list] Neo4j不可用，降级使用PostgreSQL查询课程 %s 的关系", course_id)
    relations = KnowledgeRelation.objects.filter(course_id=course_id).select_related("pre_point", "post_point")
    return success_response(data={
        "relations": [{
            "relation_id": getattr(relation, "id", None) or getattr(relation, "pk", None),
            "from_point_id": getattr(relation, "pre_point_id", None),
            "from_point_name": relation.pre_point.name,
            "to_point_id": getattr(relation, "post_point_id", None),
            "to_point_name": relation.post_point.name,
            "relation_type": relation.relation_type,
        } for relation in relations],
        "count": relations.count(),
        "data_source": "postgresql",
    })


# 维护意图：创建知识点关系
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_relation_create(request: Request) -> Response:
    """创建知识点关系。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    from_point_id = request.data.get("from_point_id")
    to_point_id = request.data.get("to_point_id")
    relation_type = request.data.get("relation_type", "prerequisite")
    if not from_point_id or not to_point_id:
        return bad_request("缺少 from_point_id 或 to_point_id")
    if str(from_point_id) == str(to_point_id):
        return bad_request("不能创建自引用关系")

    try:
        pre_point = KnowledgePoint.objects.get(pk=from_point_id, course_id=course_id)
        post_point = KnowledgePoint.objects.get(pk=to_point_id, course_id=course_id)
    except KnowledgePoint.DoesNotExist:
        return error_response(msg="知识点不存在", code=404)

    relation, created = KnowledgeRelation.objects.get_or_create(
        course_id=course_id,
        pre_point=pre_point,
        post_point=post_point,
        defaults={"relation_type": relation_type},
    )
    if created:
        neo4j_service.sync_single_relation(relation)
        refresh_course_rag_index(course_id)

    return success_response(
        data={"relation_id": getattr(relation, "id", None) or getattr(relation, "pk", None), "created": created},
        msg="关系创建成功" if created else "关系已存在",
    )


# 维护意图：删除知识点关系
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_relation_delete(request: Request, relation_id: int) -> Response:
    """删除知识点关系。"""
    try:
        relation = KnowledgeRelation.objects.get(pk=relation_id)
    except KnowledgeRelation.DoesNotExist:
        return error_response(msg="关系不存在", code=404)

    neo4j_service.delete_relation_neo4j(relation.pre_point_id, relation.post_point_id)
    course_id = relation.course_id
    relation.delete()
    refresh_course_rag_index(course_id)
    return success_response(msg="关系删除成功")
