"""GraphRAG 索引构建。"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from hashlib import md5
from pathlib import Path
import json
import re

import networkx as nx
from django.conf import settings
from networkx.algorithms import community as nx_community

from assessments.models import Question
from knowledge.models import KnowledgePoint, KnowledgeRelation, Resource


TOKEN_PATTERN = re.compile(r"[\u4e00-\u9fff]{1,}|[a-zA-Z0-9_]+")
STOP_TOKENS = {
    "知识点",
    "课程",
    "资源",
    "题目",
    "学习",
    "关联",
    "当前",
    "point",
    "resource",
    "question",
}


@dataclass
class CorpusDocument:
    """Serializable retrieval unit persisted into the on-disk GraphRAG index."""

    id: str
    kind: str
    title: str
    content: str
    url: str
    metadata: dict

    def as_dict(self) -> dict:
        """Convert the dataclass to a JSON payload."""
        return {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "metadata": self.metadata,
        }


@dataclass
class GraphEntity:
    """GraphRAG entity node."""

    id: str
    entity_type: str
    title: str
    summary: str
    url: str
    metadata: dict

    def as_dict(self) -> dict:
        """Serialize the entity for JSON persistence."""
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "metadata": self.metadata,
        }


@dataclass
class GraphRelationship:
    """GraphRAG relationship edge."""

    source: str
    target: str
    relation_type: str
    weight: float
    metadata: dict

    def as_dict(self) -> dict:
        """Serialize the graph edge for JSON persistence."""
        return {
            "source": self.source,
            "target": self.target,
            "relation_type": self.relation_type,
            "weight": self.weight,
            "metadata": self.metadata,
        }


def tokenize(text: str) -> set[str]:
    """Extract normalized Chinese and alphanumeric search tokens from text."""
    if not text:
        return set()
    return {token.lower() for token in TOKEN_PATTERN.findall(str(text)) if token.strip()}


def _safe_resource_url(resource: Resource) -> str:
    """Return a stable URL for a resource entity."""
    if resource.url:
        return resource.url
    if resource.file:
        try:
            return resource.file.url
        except ValueError:
            return ""
    return ""


def _top_themes(texts: list[str], limit: int = 6) -> list[str]:
    """Extract a compact list of community themes from entity texts."""
    counter: Counter[str] = Counter()
    for text in texts:
        counter.update(token for token in tokenize(text) if token not in STOP_TOKENS and len(token) > 1)
    return [token for token, _ in counter.most_common(limit)]


def _chapter_entity_id(chapter_name: str) -> str:
    """Build a deterministic chapter entity id."""
    normalized = chapter_name.strip() or "未分章"
    return f"chapter:{md5(normalized.encode('utf-8')).hexdigest()[:16]}"


def build_course_graph_index(course_id: int) -> dict:
    """Build a native GraphRAG index from course graph, resources, and questions."""
    graph = nx.Graph()
    documents: list[CorpusDocument] = []
    entities: dict[str, GraphEntity] = {}
    relationships: list[GraphRelationship] = []
    chapter_members: dict[str, list[str]] = {}

    points = list(
        KnowledgePoint.objects.filter(course_id=course_id, is_published=True)
        .order_by("order", "id")
    )
    point_map = {point.id: point for point in points}
    point_resource_ids: dict[int, list[int]] = {}
    point_question_ids: dict[int, list[int]] = {}

    for point in points:
        point_id = f"kp:{point.id}"
        chapter_name = str(point.chapter or "").strip() or "未分章"
        chapter_id = _chapter_entity_id(chapter_name)
        chapter_members.setdefault(chapter_id, []).append(point_id)
        tags = point.get_tags_list()
        summary = "\n".join(
            part
            for part in [
                f"知识点：{point.name}",
                f"描述：{point.description or ''}",
                f"简介：{point.introduction or ''}",
                f"章节：{chapter_name}",
                f"认知维度：{point.cognitive_dimension or ''}",
                f"分类：{point.category or ''}",
                f"教学目标：{point.teaching_goal or ''}",
                f"标签：{'、'.join(tags)}" if tags else "",
            ]
            if part.strip()
        )
        entities[point_id] = GraphEntity(
            id=point_id,
            entity_type="knowledge_point",
            title=point.name,
            summary=summary,
            url=f"/student/knowledge-map?point={point.id}",
            metadata={
                "course_id": course_id,
                "knowledge_point_id": point.id,
                "chapter": chapter_name,
                "tags": tags,
            },
        )
        documents.append(
            CorpusDocument(
                id=point_id,
                kind="knowledge_point",
                title=point.name,
                content=summary,
                url=f"/student/knowledge-map?point={point.id}",
                metadata={
                    "course_id": course_id,
                    "knowledge_point_id": point.id,
                    "chapter": chapter_name,
                },
            )
        )
        graph.add_node(point_id, entity_type="knowledge_point")

    for chapter_id, member_ids in chapter_members.items():
        chapter_name = next(
            (entities[member_id].metadata.get("chapter") for member_id in member_ids),
            "未分章",
        )
        entities[chapter_id] = GraphEntity(
            id=chapter_id,
            entity_type="chapter",
            title=str(chapter_name),
            summary=f"课程章节：{chapter_name}，包含 {len(member_ids)} 个知识相关实体。",
            url="",
            metadata={"course_id": course_id, "chapter": chapter_name},
        )
        graph.add_node(chapter_id, entity_type="chapter")
        documents.append(
            CorpusDocument(
                id=chapter_id,
                kind="chapter",
                title=str(chapter_name),
                content=f"章节：{chapter_name}，包含 {len(member_ids)} 个知识点与资源节点。",
                url="",
                metadata={"course_id": course_id, "chapter": chapter_name},
            )
        )

    for pre_point_id, post_point_id, relation_type in KnowledgeRelation.objects.filter(course_id=course_id).values_list(
        "pre_point_id",
        "post_point_id",
        "relation_type",
    ):
        source_id = f"kp:{pre_point_id}"
        target_id = f"kp:{post_point_id}"
        if source_id not in entities or target_id not in entities:
            continue
        graph.add_edge(source_id, target_id, weight=1.0, relation_type=relation_type)
        relationships.append(
            GraphRelationship(
                source=source_id,
                target=target_id,
                relation_type=str(relation_type),
                weight=1.0,
                metadata={"course_id": course_id},
            )
        )

    resources = list(
        Resource.objects.filter(course_id=course_id, is_visible=True).prefetch_related("knowledge_points")
    )
    for resource in resources:
        resource_id = f"resource:{resource.id}"
        chapter_name = str(resource.chapter_number or "").strip() or "未分章"
        chapter_id = _chapter_entity_id(chapter_name)
        chapter_members.setdefault(chapter_id, []).append(resource_id)
        linked_points: list[KnowledgePoint] = list(resource.knowledge_points.all())
        summary = "\n".join(
            part
            for part in [
                f"资源标题：{resource.title}",
                f"资源类型：{resource.resource_type}",
                f"资源描述：{resource.description or ''}",
                f"所属章节：{chapter_name}",
                f"关联知识点：{'、'.join(point.name for point in linked_points)}" if linked_points else "",
            ]
            if part.strip()
        )
        entities[resource_id] = GraphEntity(
            id=resource_id,
            entity_type="resource",
            title=resource.title,
            summary=summary,
            url=_safe_resource_url(resource),
            metadata={
                "course_id": course_id,
                "resource_id": resource.id,
                "resource_type": resource.resource_type,
                "chapter": chapter_name,
                "knowledge_point_ids": [point.id for point in linked_points],
            },
        )
        documents.append(
            CorpusDocument(
                id=resource_id,
                kind="resource",
                title=resource.title,
                content=summary,
                url=_safe_resource_url(resource),
                metadata={
                    "course_id": course_id,
                    "resource_id": resource.id,
                    "resource_type": resource.resource_type,
                    "knowledge_point_ids": [point.id for point in linked_points],
                },
            )
        )
        graph.add_node(resource_id, entity_type="resource")
        for point in linked_points:
            point_resource_ids.setdefault(point.id, []).append(resource.id)
            point_entity_id = f"kp:{point.id}"
            if point_entity_id not in entities:
                continue
            graph.add_edge(point_entity_id, resource_id, weight=0.8, relation_type="supported_by")
            relationships.append(
                GraphRelationship(
                    source=point_entity_id,
                    target=resource_id,
                    relation_type="supported_by",
                    weight=0.8,
                    metadata={"course_id": course_id, "resource_type": resource.resource_type},
                )
            )

    questions = list(
        Question.objects.filter(course_id=course_id, is_visible=True)
        .prefetch_related("knowledge_points")
        .order_by("-created_at")[:600]
    )
    for question in questions:
        question_id = f"question:{question.id}"
        chapter_name = str(question.chapter or "").strip() or "未分章"
        chapter_id = _chapter_entity_id(chapter_name)
        chapter_members.setdefault(chapter_id, []).append(question_id)
        linked_points: list[KnowledgePoint] = list(question.knowledge_points.all())
        summary = "\n".join(
            part
            for part in [
                f"题目：{question.content}",
                f"题型：{question.question_type}",
                f"难度：{question.difficulty}",
                f"解析：{question.analysis or ''}",
                f"关联知识点：{'、'.join(point.name for point in linked_points)}" if linked_points else "",
            ]
            if part.strip()
        )
        entities[question_id] = GraphEntity(
            id=question_id,
            entity_type="question",
            title=f"题目 {question.id}",
            summary=summary,
            url=f"/student/knowledge-map?question={question.id}",
            metadata={
                "course_id": course_id,
                "question_id": question.id,
                "question_type": question.question_type,
                "difficulty": question.difficulty,
                "chapter": chapter_name,
                "knowledge_point_ids": [point.id for point in linked_points],
            },
        )
        documents.append(
            CorpusDocument(
                id=question_id,
                kind="question",
                title=f"题目 {question.id}",
                content=summary,
                url=f"/student/knowledge-map?question={question.id}",
                metadata={
                    "course_id": course_id,
                    "question_id": question.id,
                    "knowledge_point_ids": [point.id for point in linked_points],
                    "answer_hidden": True,
                },
            )
        )
        graph.add_node(question_id, entity_type="question")
        for point in linked_points:
            point_question_ids.setdefault(point.id, []).append(question.id)
            point_entity_id = f"kp:{point.id}"
            if point_entity_id not in entities:
                continue
            graph.add_edge(point_entity_id, question_id, weight=0.9, relation_type="assessed_by")
            relationships.append(
                GraphRelationship(
                    source=point_entity_id,
                    target=question_id,
                    relation_type="assessed_by",
                    weight=0.9,
                    metadata={"course_id": course_id, "question_type": question.question_type},
                )
            )

    for chapter_id, member_ids in chapter_members.items():
        if chapter_id not in entities:
            continue
        graph.add_node(chapter_id, entity_type="chapter")
        for member_id in member_ids:
            if member_id not in entities:
                continue
            graph.add_edge(chapter_id, member_id, weight=0.6, relation_type="contains")
            relationships.append(
                GraphRelationship(
                    source=chapter_id,
                    target=member_id,
                    relation_type="contains",
                    weight=0.6,
                    metadata={"course_id": course_id},
                )
            )

    if graph.number_of_nodes() == 0:
        communities: list[set[str]] = []
    elif graph.number_of_edges() == 0:
        communities = [{node_id} for node_id in graph.nodes]
    else:
        communities = [set(group) for group in nx_community.greedy_modularity_communities(graph)]

    community_payloads: list[dict] = []
    community_reports: list[dict] = []
    for community_index, community_nodes in enumerate(communities, start=1):
        subgraph = graph.subgraph(community_nodes)
        if subgraph.number_of_nodes() <= 1:
            centrality = {node_id: 1.0 for node_id in subgraph.nodes}
        else:
            centrality = nx.degree_centrality(subgraph)
        top_node_ids: list[str] = [
            str(node_id)
            for node_id, _ in sorted(centrality.items(), key=lambda item: item[1], reverse=True)[:6]
        ]
        top_titles = [entities[node_id].title for node_id in top_node_ids if node_id in entities]
        relation_counter = Counter(
            str(edge_data.get("relation_type", "related"))
            for _, _, edge_data in subgraph.edges(data=True)
        )
        themes = _top_themes(
            [
                f"{entities[node_id].title} {entities[node_id].summary}"
                for node_id in community_nodes
                if node_id in entities
            ]
        )
        community_id = f"community:{community_index}"
        community_payloads.append(
            {
                "id": community_id,
                "entity_ids": sorted(community_nodes),
                "entity_count": len(community_nodes),
                "top_entities": top_node_ids,
                "themes": themes,
            }
        )
        report_summary = (
            f"该社区围绕 {'、'.join(top_titles[:4]) or '课程核心实体'} 组织，"
            f"主要关系为 {'、'.join(relation_type for relation_type, _ in relation_counter.most_common(3)) or '关联'}，"
            f"主题集中在 {'、'.join(themes[:5]) or '课程核心知识'}。"
        )
        community_reports.append(
            {
                "community_id": community_id,
                "title": f"社区报告 {community_index}",
                "summary": report_summary,
                "themes": themes,
                "top_entities": [
                    {"id": node_id, "title": entities[node_id].title, "entity_type": entities[node_id].entity_type}
                    for node_id in top_node_ids
                    if node_id in entities
                ],
                "relation_breakdown": dict(relation_counter),
            }
        )
        documents.append(
            CorpusDocument(
                id=community_id,
                kind="community_report",
                title=f"社区报告 {community_index}",
                content=report_summary,
                url="",
                metadata={
                    "course_id": course_id,
                    "community_id": community_id,
                    "themes": themes,
                    "entity_ids": sorted(community_nodes),
                },
            )
        )

    return {
        "course_id": course_id,
        "index_type": "native_graphrag_v1",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "entities": [entity.as_dict() for entity in entities.values()],
        "relationships": [relationship.as_dict() for relationship in relationships],
        "communities": community_payloads,
        "community_reports": community_reports,
        "documents": [document.as_dict() for document in documents],
    }


def build_course_corpus(course_id: int) -> list[CorpusDocument]:
    """Build a backwards-compatible corpus list from the GraphRAG index."""
    payload = build_course_graph_index(course_id)
    return [CorpusDocument(**document) for document in payload.get("documents", [])]


def get_index_path(course_id: int) -> Path:
    """Return the runtime path used for the persisted course GraphRAG index."""
    return Path(settings.BASE_DIR) / "runtime_logs" / "rag" / f"course_{course_id}.json"


def save_course_index(course_id: int, payload: dict) -> Path:
    """Persist the generated GraphRAG index."""
    index_path = get_index_path(course_id)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return index_path


def load_course_index(course_id: int) -> dict:
    """Load a previously materialized GraphRAG index, if available."""
    index_path = get_index_path(course_id)
    if not index_path.exists():
        return {}
    return json.loads(index_path.read_text(encoding="utf-8"))


def delete_course_index(course_id: int) -> bool:
    """Delete the persisted GraphRAG index for a single course when present."""
    index_path = get_index_path(course_id)
    if not index_path.exists():
        return False
    index_path.unlink()
    return True
