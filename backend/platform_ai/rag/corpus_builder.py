"""GraphRAG 课程索引构建流程。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import networkx as nx

from assessments.models import Question
from knowledge.models import KnowledgePoint, KnowledgeRelation, Resource
from .corpus_communities import build_community_records
from .corpus_types import CorpusDocument, GraphEntity, GraphRelationship
from .corpus_utils import _chapter_entity_id, _safe_resource_url


# 维护意图：Shared mutable state while assembling a course GraphRAG payload
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass
class GraphCorpusBuildState:
    """Shared mutable state while assembling a course GraphRAG payload."""

    course_id: int
    graph: nx.Graph = field(default_factory=nx.Graph)
    documents: list[CorpusDocument] = field(default_factory=list)
    entities: dict[str, GraphEntity] = field(default_factory=dict)
    relationships: list[GraphRelationship] = field(default_factory=list)
    chapter_members: dict[str, list[str]] = field(default_factory=dict)

    # 维护意图：Track which entities belong to a logical chapter bucket
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def remember_chapter_member(self, chapter_name: str, entity_id: str) -> tuple[str, str]:
        """Track which entities belong to a logical chapter bucket."""
        normalized_chapter = str(chapter_name or "").strip() or "未分章"
        chapter_id = _chapter_entity_id(normalized_chapter)
        self.chapter_members.setdefault(chapter_id, []).append(entity_id)
        return chapter_id, normalized_chapter

    # 维护意图：Register an entity/document pair into the in-memory payload
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def add_entity(self, entity: GraphEntity, document: CorpusDocument) -> None:
        """Register an entity/document pair into the in-memory payload."""
        self.entities[entity.id] = entity
        self.documents.append(document)
        self.graph.add_node(entity.id, entity_type=entity.entity_type)

    # 维护意图：Add a graph edge and the serialized relationship payload together
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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


# 维护意图：Join non-empty text fragments into a single multiline summary
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def join_nonempty(parts: list[str]) -> str:
    """Join non-empty text fragments into a single multiline summary."""
    return "\n".join(part for part in parts if part.strip())


# 维护意图：Render the retrievable summary for a knowledge point entity
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def point_summary(point: KnowledgePoint, chapter_name: str) -> str:
    """Render the retrievable summary for a knowledge point entity."""
    tags = point.get_tags_list()
    return join_nonempty(
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


# 维护意图：Render the retrievable summary for a resource entity
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def resource_summary(resource: Resource, chapter_name: str, linked_points: list[KnowledgePoint]) -> str:
    """Render the retrievable summary for a resource entity."""
    return join_nonempty(
        [
            f"资源标题：{resource.title}",
            f"资源类型：{resource.resource_type}",
            f"资源描述：{resource.description or ''}",
            f"所属章节：{chapter_name}",
            f"关联知识点：{'、'.join(point.name for point in linked_points)}" if linked_points else "",
        ]
    )


# 维护意图：Render the retrievable summary for a question entity
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def question_summary(question: Question, linked_points: list[KnowledgePoint]) -> str:
    """Render the retrievable summary for a question entity."""
    return join_nonempty(
        [
            f"题目：{question.content}",
            f"题型：{question.question_type}",
            f"难度：{question.difficulty}",
            f"解析：{question.analysis or ''}",
            f"关联知识点：{'、'.join(point.name for point in linked_points)}" if linked_points else "",
        ]
    )


# 维护意图：Load the published knowledge points that can participate in GraphRAG
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def published_points(course_id: int) -> list[KnowledgePoint]:
    """Load the published knowledge points that can participate in GraphRAG."""
    return list(
        KnowledgePoint.objects.filter(course_id=course_id, is_published=True).order_by("order", "id")
    )


# 维护意图：Load course resources with knowledge-point associations materialized
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def visible_resources(course_id: int) -> list[Resource]:
    """Load course resources with knowledge-point associations materialized."""
    return list(Resource.objects.filter(course_id=course_id, is_visible=True).prefetch_related("knowledge_points"))


# 维护意图：Load recent visible course questions with their linked knowledge points
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def visible_questions(course_id: int) -> list[Question]:
    """Load recent visible course questions with their linked knowledge points."""
    return list(
        Question.objects.filter(course_id=course_id, is_visible=True)
        .prefetch_related("knowledge_points")
        .order_by("-created_at")[:600]
    )


# 维护意图：Create point entities and seed chapter membership information
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def populate_points(state: GraphCorpusBuildState, points: list[KnowledgePoint]) -> None:
    """Create point entities and seed chapter membership information."""
    for point in points:
        point_id = f"kp:{point.id}"
        _, chapter_name = state.remember_chapter_member(point.chapter or "", point_id)
        tags = point.get_tags_list()
        summary = point_summary(point, chapter_name)
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


# 维护意图：Materialize chapter entities after the knowledge-point phase
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def populate_chapters(state: GraphCorpusBuildState) -> None:
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


# 维护意图：Connect prerequisite relationships between published knowledge points
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def populate_knowledge_relations(state: GraphCorpusBuildState) -> None:
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


# 维护意图：Create resource entities and connect them to knowledge points
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def populate_resources(state: GraphCorpusBuildState) -> None:
    """Create resource entities and connect them to knowledge points."""
    for resource in visible_resources(state.course_id):
        resource_id = f"resource:{resource.id}"
        _, chapter_name = state.remember_chapter_member(resource.chapter_number or "", resource_id)
        linked_points = list(resource.knowledge_points.all())
        summary = resource_summary(resource, chapter_name, linked_points)
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


# 维护意图：Create question entities and connect them to assessed knowledge points
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def populate_questions(state: GraphCorpusBuildState) -> None:
    """Create question entities and connect them to assessed knowledge points."""
    for question in visible_questions(state.course_id):
        question_id = f"question:{question.id}"
        _, chapter_name = state.remember_chapter_member(question.chapter or "", question_id)
        linked_points = list(question.knowledge_points.all())
        summary = question_summary(question, linked_points)
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


# 维护意图：Connect each chapter hub to all collected member entities
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def link_chapter_members(state: GraphCorpusBuildState) -> None:
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

# 维护意图：Assemble the full serializable GraphRAG payload for a course
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_graph_payload(course_id: int) -> dict:
    """Assemble the full serializable GraphRAG payload for a course."""
    state = GraphCorpusBuildState(course_id=course_id)
    points = published_points(course_id)
    populate_points(state, points)
    populate_chapters(state)
    populate_knowledge_relations(state)
    populate_resources(state)
    populate_questions(state)
    link_chapter_members(state)
    community_payloads, community_reports = build_community_records(state)
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
