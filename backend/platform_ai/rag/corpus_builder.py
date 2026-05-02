"""GraphRAG 课程索引构建流程。"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime

import networkx as nx
from networkx.algorithms import community as nx_community

from assessments.models import Question
from knowledge.models import KnowledgePoint, KnowledgeRelation, Resource
from .corpus_types import CorpusDocument, GraphEntity, GraphRelationship
from .corpus_utils import _chapter_entity_id, _safe_resource_url, _top_themes


@dataclass
class GraphCorpusBuildState:
    """Shared mutable state while assembling a course GraphRAG payload."""

    course_id: int
    graph: nx.Graph = field(default_factory=nx.Graph)
    documents: list[CorpusDocument] = field(default_factory=list)
    entities: dict[str, GraphEntity] = field(default_factory=dict)
    relationships: list[GraphRelationship] = field(default_factory=list)
    chapter_members: dict[str, list[str]] = field(default_factory=dict)

    def remember_chapter_member(self, chapter_name: str, entity_id: str) -> tuple[str, str]:
        """Track which entities belong to a logical chapter bucket."""
        normalized_chapter = str(chapter_name or "").strip() or "未分章"
        chapter_id = _chapter_entity_id(normalized_chapter)
        self.chapter_members.setdefault(chapter_id, []).append(entity_id)
        return chapter_id, normalized_chapter

    def add_entity(self, entity: GraphEntity, document: CorpusDocument) -> None:
        """Register an entity/document pair into the in-memory payload."""
        self.entities[entity.id] = entity
        self.documents.append(document)
        self.graph.add_node(entity.id, entity_type=entity.entity_type)

    def add_relationship(
        self,
        *,
        source: str,
        target: str,
        relation_type: str,
        weight: float,
        metadata: dict,
    ) -> None:
        """Add a graph edge and the serialized relationship payload together."""
        self.graph.add_edge(source, target, weight=weight, relation_type=relation_type)
        self.relationships.append(
            GraphRelationship(
                source=source,
                target=target,
                relation_type=relation_type,
                weight=weight,
                metadata=metadata,
            )
        )


def _join_nonempty(parts: list[str]) -> str:
    """Join non-empty text fragments into a single multiline summary."""
    return "\n".join(part for part in parts if part.strip())


def _point_summary(point: KnowledgePoint, chapter_name: str) -> str:
    """Render the retrievable summary for a knowledge point entity."""
    tags = point.get_tags_list()
    return _join_nonempty(
        [
            f"知识点：{point.name}",
            f"描述：{point.description or ''}",
            f"简介：{point.introduction or ''}",
            f"章节：{chapter_name}",
            f"认知维度：{point.cognitive_dimension or ''}",
            f"分类：{point.category or ''}",
            f"教学目标：{point.teaching_goal or ''}",
            f"标签：{'、'.join(tags)}" if tags else "",
        ]
    )


def _resource_summary(resource: Resource, chapter_name: str, linked_points: list[KnowledgePoint]) -> str:
    """Render the retrievable summary for a resource entity."""
    return _join_nonempty(
        [
            f"资源标题：{resource.title}",
            f"资源类型：{resource.resource_type}",
            f"资源描述：{resource.description or ''}",
            f"所属章节：{chapter_name}",
            f"关联知识点：{'、'.join(point.name for point in linked_points)}" if linked_points else "",
        ]
    )


def _question_summary(question: Question, linked_points: list[KnowledgePoint]) -> str:
    """Render the retrievable summary for a question entity."""
    return _join_nonempty(
        [
            f"题目：{question.content}",
            f"题型：{question.question_type}",
            f"难度：{question.difficulty}",
            f"解析：{question.analysis or ''}",
            f"关联知识点：{'、'.join(point.name for point in linked_points)}" if linked_points else "",
        ]
    )


def _published_points(course_id: int) -> list[KnowledgePoint]:
    """Load the published knowledge points that can participate in GraphRAG."""
    return list(
        KnowledgePoint.objects.filter(course_id=course_id, is_published=True).order_by("order", "id")
    )


def _visible_resources(course_id: int) -> list[Resource]:
    """Load course resources with knowledge-point associations materialized."""
    return list(Resource.objects.filter(course_id=course_id, is_visible=True).prefetch_related("knowledge_points"))


def _visible_questions(course_id: int) -> list[Question]:
    """Load recent visible course questions with their linked knowledge points."""
    return list(
        Question.objects.filter(course_id=course_id, is_visible=True)
        .prefetch_related("knowledge_points")
        .order_by("-created_at")[:600]
    )


def _populate_points(state: GraphCorpusBuildState, points: list[KnowledgePoint]) -> None:
    """Create point entities and seed chapter membership information."""
    for point in points:
        point_id = f"kp:{point.id}"
        _, chapter_name = state.remember_chapter_member(point.chapter or "", point_id)
        tags = point.get_tags_list()
        summary = _point_summary(point, chapter_name)
        state.add_entity(
            GraphEntity(
                id=point_id,
                entity_type="knowledge_point",
                title=point.name,
                summary=summary,
                url=f"/student/knowledge-map?point={point.id}",
                metadata={
                    "course_id": state.course_id,
                    "knowledge_point_id": point.id,
                    "chapter": chapter_name,
                    "tags": tags,
                },
            ),
            CorpusDocument(
                id=point_id,
                kind="knowledge_point",
                title=point.name,
                content=summary,
                url=f"/student/knowledge-map?point={point.id}",
                metadata={
                    "course_id": state.course_id,
                    "knowledge_point_id": point.id,
                    "chapter": chapter_name,
                },
            ),
        )


def _populate_chapters(state: GraphCorpusBuildState) -> None:
    """Materialize chapter entities after the knowledge-point phase."""
    for chapter_id, member_ids in state.chapter_members.items():
        chapter_name = next(
            (state.entities[member_id].metadata.get("chapter") for member_id in member_ids if member_id in state.entities),
            "未分章",
        )
        chapter_title = str(chapter_name)
        state.add_entity(
            GraphEntity(
                id=chapter_id,
                entity_type="chapter",
                title=chapter_title,
                summary=f"课程章节：{chapter_title}，包含 {len(member_ids)} 个知识相关实体。",
                url="",
                metadata={"course_id": state.course_id, "chapter": chapter_title},
            ),
            CorpusDocument(
                id=chapter_id,
                kind="chapter",
                title=chapter_title,
                content=f"章节：{chapter_title}，包含 {len(member_ids)} 个知识点与资源节点。",
                url="",
                metadata={"course_id": state.course_id, "chapter": chapter_title},
            ),
        )


def _populate_knowledge_relations(state: GraphCorpusBuildState) -> None:
    """Connect prerequisite relationships between published knowledge points."""
    relation_rows = KnowledgeRelation.objects.filter(course_id=state.course_id).values_list(
        "pre_point_id",
        "post_point_id",
        "relation_type",
    )
    for pre_point_id, post_point_id, relation_type in relation_rows:
        source_id = f"kp:{pre_point_id}"
        target_id = f"kp:{post_point_id}"
        if source_id not in state.entities or target_id not in state.entities:
            continue
        state.add_relationship(
            source=source_id,
            target=target_id,
            relation_type=str(relation_type),
            weight=1.0,
            metadata={"course_id": state.course_id},
        )


def _populate_resources(state: GraphCorpusBuildState) -> None:
    """Create resource entities and connect them to knowledge points."""
    for resource in _visible_resources(state.course_id):
        resource_id = f"resource:{resource.id}"
        _, chapter_name = state.remember_chapter_member(resource.chapter_number or "", resource_id)
        linked_points = list(resource.knowledge_points.all())
        summary = _resource_summary(resource, chapter_name, linked_points)
        state.add_entity(
            GraphEntity(
                id=resource_id,
                entity_type="resource",
                title=resource.title,
                summary=summary,
                url=_safe_resource_url(resource),
                metadata={
                    "course_id": state.course_id,
                    "resource_id": resource.id,
                    "resource_type": resource.resource_type,
                    "chapter": chapter_name,
                    "knowledge_point_ids": [point.id for point in linked_points],
                },
            ),
            CorpusDocument(
                id=resource_id,
                kind="resource",
                title=resource.title,
                content=summary,
                url=_safe_resource_url(resource),
                metadata={
                    "course_id": state.course_id,
                    "resource_id": resource.id,
                    "resource_type": resource.resource_type,
                    "knowledge_point_ids": [point.id for point in linked_points],
                },
            ),
        )
        for point in linked_points:
            point_entity_id = f"kp:{point.id}"
            if point_entity_id not in state.entities:
                continue
            state.add_relationship(
                source=point_entity_id,
                target=resource_id,
                relation_type="supported_by",
                weight=0.8,
                metadata={"course_id": state.course_id, "resource_type": resource.resource_type},
            )


def _populate_questions(state: GraphCorpusBuildState) -> None:
    """Create question entities and connect them to assessed knowledge points."""
    for question in _visible_questions(state.course_id):
        question_id = f"question:{question.id}"
        _, chapter_name = state.remember_chapter_member(question.chapter or "", question_id)
        linked_points = list(question.knowledge_points.all())
        summary = _question_summary(question, linked_points)
        state.add_entity(
            GraphEntity(
                id=question_id,
                entity_type="question",
                title=f"题目 {question.id}",
                summary=summary,
                url=f"/student/knowledge-map?question={question.id}",
                metadata={
                    "course_id": state.course_id,
                    "question_id": question.id,
                    "question_type": question.question_type,
                    "difficulty": question.difficulty,
                    "chapter": chapter_name,
                    "knowledge_point_ids": [point.id for point in linked_points],
                },
            ),
            CorpusDocument(
                id=question_id,
                kind="question",
                title=f"题目 {question.id}",
                content=summary,
                url=f"/student/knowledge-map?question={question.id}",
                metadata={
                    "course_id": state.course_id,
                    "question_id": question.id,
                    "knowledge_point_ids": [point.id for point in linked_points],
                    "answer_hidden": True,
                },
            ),
        )
        for point in linked_points:
            point_entity_id = f"kp:{point.id}"
            if point_entity_id not in state.entities:
                continue
            state.add_relationship(
                source=point_entity_id,
                target=question_id,
                relation_type="assessed_by",
                weight=0.9,
                metadata={"course_id": state.course_id, "question_type": question.question_type},
            )


def _link_chapter_members(state: GraphCorpusBuildState) -> None:
    """Connect each chapter hub to all collected member entities."""
    for chapter_id, member_ids in state.chapter_members.items():
        if chapter_id not in state.entities:
            continue
        for member_id in member_ids:
            if member_id not in state.entities:
                continue
            state.add_relationship(
                source=chapter_id,
                target=member_id,
                relation_type="contains",
                weight=0.6,
                metadata={"course_id": state.course_id},
            )


def _detect_communities(graph: nx.Graph) -> list[set[str]]:
    """Return deterministic graph communities for the current course graph."""
    if graph.number_of_nodes() == 0:
        return []
    if graph.number_of_edges() == 0:
        return [{str(node_id)} for node_id in graph.nodes]
    return [set(group) for group in nx_community.greedy_modularity_communities(graph)]


def _build_community_records(state: GraphCorpusBuildState) -> tuple[list[dict], list[dict]]:
    """Build community payloads, reports, and synthetic report documents."""
    community_payloads: list[dict] = []
    community_reports: list[dict] = []
    for community_index, community_nodes in enumerate(_detect_communities(state.graph), start=1):
        subgraph = state.graph.subgraph(community_nodes)
        if subgraph.number_of_nodes() <= 1:
            centrality = {str(node_id): 1.0 for node_id in subgraph.nodes}
        else:
            centrality = {str(node_id): score for node_id, score in nx.degree_centrality(subgraph).items()}
        top_node_ids = [
            node_id for node_id, _ in sorted(centrality.items(), key=lambda item: item[1], reverse=True)[:6]
        ]
        top_titles = [state.entities[node_id].title for node_id in top_node_ids if node_id in state.entities]
        relation_counter = Counter(
            str(edge_data.get("relation_type", "related")) for _, _, edge_data in subgraph.edges(data=True)
        )
        themes = _top_themes(
            [
                f"{state.entities[node_id].title} {state.entities[node_id].summary}"
                for node_id in community_nodes
                if node_id in state.entities
            ]
        )
        community_id = f"community:{community_index}"
        report_summary = (
            f"该社区围绕 {'、'.join(top_titles[:4]) or '课程核心实体'} 组织，"
            f"主要关系为 {'、'.join(relation_type for relation_type, _ in relation_counter.most_common(3)) or '关联'}，"
            f"主题集中在 {'、'.join(themes[:5]) or '课程核心知识'}。"
        )
        community_payloads.append(
            {
                "id": community_id,
                "entity_ids": sorted(community_nodes),
                "entity_count": len(community_nodes),
                "top_entities": top_node_ids,
                "themes": themes,
            }
        )
        community_reports.append(
            {
                "community_id": community_id,
                "title": f"社区报告 {community_index}",
                "summary": report_summary,
                "themes": themes,
                "top_entities": [
                    {
                        "id": node_id,
                        "title": state.entities[node_id].title,
                        "entity_type": state.entities[node_id].entity_type,
                    }
                    for node_id in top_node_ids
                    if node_id in state.entities
                ],
                "relation_breakdown": dict(relation_counter),
            }
        )
        state.documents.append(
            CorpusDocument(
                id=community_id,
                kind="community_report",
                title=f"社区报告 {community_index}",
                content=report_summary,
                url="",
                metadata={
                    "course_id": state.course_id,
                    "community_id": community_id,
                    "themes": themes,
                    "entity_ids": sorted(community_nodes),
                },
            )
        )
    return community_payloads, community_reports


def build_course_graph_payload(course_id: int) -> dict:
    """Assemble the full serializable GraphRAG payload for a course."""
    state = GraphCorpusBuildState(course_id=course_id)
    points = _published_points(course_id)
    _populate_points(state, points)
    _populate_chapters(state)
    _populate_knowledge_relations(state)
    _populate_resources(state)
    _populate_questions(state)
    _link_chapter_members(state)
    community_payloads, community_reports = _build_community_records(state)
    return {
        "course_id": course_id,
        "index_type": "native_graphrag_v1",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "entities": [entity.as_dict() for entity in state.entities.values()],
        "relationships": [relationship.as_dict() for relationship in state.relationships],
        "communities": community_payloads,
        "community_reports": community_reports,
        "documents": [document.as_dict() for document in state.documents],
    }


__all__ = ["build_course_graph_payload"]
