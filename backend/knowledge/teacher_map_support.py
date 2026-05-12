"""教师端知识图谱视图辅助工具。"""
from __future__ import annotations

import json
from typing import Any

from django.db import transaction

from .models import KnowledgePoint, KnowledgeRelation


def update_existing_graph_nodes(*, course_id: int, nodes: list[dict[str, Any]]) -> None:
    """根据前端提交节点更新现有知识点。"""
    existing_points = {
        str(getattr(point, "id", point.pk)): point
        for point in KnowledgePoint.objects.filter(course_id=course_id)
    }
    existing_ids = set(existing_points)
    submitted_ids: set[str] = set()

    for node in nodes:
        node_id = str(node.get("id", ""))
        name = str(node.get("name", node.get("point_name", "")))[:200]
        if node_id not in existing_ids:
            continue
        point = existing_points[node_id]
        if point.name != name:
            point.name = name
            point.description = str(node.get("description", ""))[:1000]
            point.save(update_fields=["name", "description"])
        submitted_ids.add(node_id)

    removed_ids = existing_ids - submitted_ids
    if removed_ids:
        KnowledgePoint.objects.filter(pk__in=removed_ids, course_id=course_id).delete()


def rebuild_graph_relations(*, course_id: int, edges: list[dict[str, Any]]) -> None:
    """按前端提交关系重建课程知识点边。"""
    KnowledgeRelation.objects.filter(course_id=course_id).delete()
    point_map = {
        str(getattr(point, "id", point.pk)): point
        for point in KnowledgePoint.objects.filter(course_id=course_id)
    }
    for edge in edges:
        source = str(edge.get("source", ""))
        target = str(edge.get("target", ""))
        if source not in point_map or target not in point_map or source == target:
            continue
        KnowledgeRelation.objects.get_or_create(
            course_id=course_id,
            pre_point=point_map[source],
            post_point=point_map[target],
            defaults={"relation_type": edge.get("label", "prerequisite")},
        )


def parse_imported_knowledge_map(file) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """解析教师上传的 JSON 或 Excel 知识图谱文件。"""
    file_ext = file.name.lower().split(".")[-1] if "." in file.name else ""
    if file_ext == "json":
        content = file.read().decode("utf-8")
        payload = json.loads(content)
        return payload.get("nodes", []), payload.get("edges", [])

    import pandas as pd

    dataframe = pd.read_excel(file, sheet_name=0)
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    for index, row in dataframe.iterrows():
        node = {
            "id": str(index),
            "name": str(row.get("知识点名称", row.get("name", f"知识点{index}"))),
            "description": str(row.get("描述", row.get("description", ""))),
            "chapter": str(row.get("章节", row.get("chapter", ""))),
        }
        nodes.append(node)
        prerequisites = row.get("先修知识点", row.get("prerequisites", ""))
        if prerequisites and str(prerequisites) != "nan":
            for prerequisite_name in str(prerequisites).split(","):
                prerequisite_name = prerequisite_name.strip()
                if prerequisite_name:
                    edges.append(
                        {
                            "source": prerequisite_name,
                            "target": node["name"],
                            "relation": "prerequisite",
                        }
                    )
    return nodes, edges


def persist_imported_knowledge_map(*, course_id: int, nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> tuple[int, int]:
    """写入教师端导入的知识图谱节点和关系。"""
    id_map: dict[str, int] = {}
    with transaction.atomic():
        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            name = str(node.get("name", node.get("point_name", f"知识点{index}")))[:200]
            point = KnowledgePoint.objects.create(
                course_id=course_id,
                name=name,
                description=str(node.get("description", ""))[:1000],
                chapter=str(node.get("chapter", ""))[:100],
                order=index,
            )
            point_id = getattr(point, "id", None) or getattr(point, "pk", None)
            id_map[str(node.get("id", str(index)))] = point_id
            id_map[name] = point_id

        for edge in edges:
            if not isinstance(edge, dict):
                continue
            source_id = id_map.get(str(edge.get("source")))
            target_id = id_map.get(str(edge.get("target")))
            if source_id and target_id:
                KnowledgeRelation.objects.get_or_create(
                    course_id=course_id,
                    pre_point_id=source_id,
                    post_point_id=target_id,
                    defaults={"relation_type": edge.get("relation", "prerequisite")},
                )
    return len(nodes), len(edges)
