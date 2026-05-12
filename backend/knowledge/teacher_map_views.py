"""教师端知识图谱导入、保存、发布与导出视图。"""
from __future__ import annotations

import json
import logging

from django.db import transaction
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.neo4j_service import neo4j_service
from common.permissions import IsTeacherOrAdmin
from common.responses import success_response
from common.utils import resolve_course_id as _resolve_course_id

from .models import KnowledgePoint, KnowledgeRelation
from .teacher_map_support import (
    parse_imported_knowledge_map,
    persist_imported_knowledge_map,
    rebuild_graph_relations,
    update_existing_graph_nodes,
)
from .teacher_helpers import bad_request, refresh_course_rag_index


logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_graph_save(request: Request) -> Response:
    """批量保存知识图谱并同步数据库副本。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    nodes = request.data.get("nodes", [])
    edges = request.data.get("edges", [])
    if not nodes:
        return bad_request("节点数据为空")

    with transaction.atomic():
        update_existing_graph_nodes(course_id=course_id, nodes=nodes)
        rebuild_graph_relations(course_id=course_id, edges=edges)

    try:
        neo4j_service.sync_knowledge_graph(course_id)
        logger.info(f"知识图谱保存后Neo4j同步成功: course={course_id}")
    except Exception as exc:
        logger.warning(f"知识图谱保存成功但Neo4j同步失败: {exc}")

    refresh_course_rag_index(course_id)
    return success_response(msg="知识图谱保存成功")


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_map_import(request: Request) -> Response:
    """导入知识图谱，支持 JSON / Excel。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    file = request.FILES.get("file")
    if not file:
        return bad_request("缺少必要参数")

    max_size = 10 * 1024 * 1024
    if file.size > max_size:
        return bad_request("文件大小超过限制(最大10MB)")
    file_ext = file.name.lower().split(".")[-1] if "." in file.name else ""
    if f".{file_ext}" not in [".json", ".xlsx", ".xls"]:
        return bad_request("仅支持JSON或Excel格式文件")

    try:
        nodes, edges = parse_imported_knowledge_map(file)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return bad_request(f"文件格式错误: {str(exc)}")
    except Exception as exc:
        return bad_request(f"文件读取失败: {str(exc)}")

    if not nodes:
        return bad_request("知识点数据为空")
    if len(nodes) > 1000:
        return bad_request("知识点数量超过限制(最多1000个)")

    imported_nodes, imported_edges = persist_imported_knowledge_map(
        course_id=course_id,
        nodes=nodes,
        edges=edges,
    )

    try:
        neo4j_service.sync_knowledge_graph(course_id)
        logger.info(f"知识图谱导入后Neo4j同步成功: course={course_id}")
    except Exception as exc:
        logger.warning(f"知识图谱导入成功但Neo4j同步失败: {exc}")

    return success_response(data={"imported_nodes": imported_nodes, "imported_edges": imported_edges}, msg="知识图谱导入成功")


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_map_publish(request: Request) -> Response:
    """发布课程知识图谱。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err
    confirm = request.data.get("confirm", False)
    if not confirm:
        points = KnowledgePoint.objects.filter(course_id=course_id, is_published=False)
        pending_count = points.count()
        return success_response(data={"pending_count": pending_count, "message": f"有 {pending_count} 个知识点待发布"})

    updated = KnowledgePoint.objects.filter(course_id=course_id).update(is_published=True)
    try:
        neo4j_service.sync_knowledge_graph(course_id)
    except Exception as exc:
        logger.warning(f"知识图谱发布成功但Neo4j同步失败: {exc}")

    refresh_course_rag_index(course_id)
    return success_response(data={"published_count": updated}, msg="知识图谱发布成功")


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_map_build_rag_index(request: Request) -> Response:
    """构建课程 GraphRAG 索引。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    from tools.rag_index import refresh_rag_corpus
    built_paths = refresh_rag_corpus(course_id=course_id)
    return success_response(data={"course_id": course_id, "index_paths": built_paths}, msg="课程 GraphRAG 索引构建完成")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_map_export(request: Request) -> HttpResponse | Response:
    """导出知识图谱为 JSON 文件。"""
    course_id, err = _resolve_course_id(request)
    if err:
        return err

    points = KnowledgePoint.objects.filter(course_id=course_id)
    relations = KnowledgeRelation.objects.filter(course_id=course_id)
    payload = {
        "course_id": course_id,
        "knowledge_points": [{
            "id": point.id,
            "name": point.name,
            "description": point.description or "",
            "difficulty": getattr(point, "difficulty", None),
            "parent_id": getattr(point, "parent_id", None),
        } for point in points],
        "relations": [{
            "from_point_id": getattr(relation, "pre_point_id", None),
            "to_point_id": getattr(relation, "post_point_id", None),
            "relation_type": relation.relation_type,
        } for relation in relations],
    }
    response = HttpResponse(json.dumps(payload, ensure_ascii=False, indent=2), content_type="application/json; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="knowledge_map_{course_id}.json"'
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def knowledge_map_template(request: Request) -> HttpResponse:
    """获取知识图谱导入模板。"""
    template = {
        "knowledge_points": [
            {"name": "示例知识点1", "description": "描述", "difficulty": 3, "parent_id": None},
            {"name": "示例知识点2", "description": "描述", "difficulty": 2, "parent_id": None},
        ],
        "relations": [{
            "from_point_name": "示例知识点1",
            "to_point_name": "示例知识点2",
            "relation_type": "prerequisite",
        }],
    }
    response = HttpResponse(json.dumps(template, ensure_ascii=False, indent=2), content_type="application/json; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="knowledge_map_template.json"'
    return response
