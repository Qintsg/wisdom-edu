"""GraphRAG corpus serializable data types。"""

from __future__ import annotations

from dataclasses import dataclass


# 维护意图：Serializable retrieval unit persisted into the on-disk GraphRAG index
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass
class CorpusDocument:
    """Serializable retrieval unit persisted into the on-disk GraphRAG index."""

    id: str
    kind: str
    title: str
    content: str
    url: str
    metadata: dict

    # 维护意图：Convert the dataclass to a JSON payload
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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


# 维护意图：GraphRAG entity node
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass
class GraphEntity:
    """GraphRAG entity node."""

    id: str
    entity_type: str
    title: str
    summary: str
    url: str
    metadata: dict

    # 维护意图：Serialize the entity for JSON persistence
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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


# 维护意图：GraphRAG relationship edge
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass
class GraphRelationship:
    """GraphRAG relationship edge."""

    source: str
    target: str
    relation_type: str
    weight: float
    metadata: dict

    # 维护意图：Serialize the graph edge for JSON persistence
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def as_dict(self) -> dict:
        """Serialize the graph edge for JSON persistence."""
        return {
            "source": self.source,
            "target": self.target,
            "relation_type": self.relation_type,
            "weight": self.weight,
            "metadata": self.metadata,
        }
