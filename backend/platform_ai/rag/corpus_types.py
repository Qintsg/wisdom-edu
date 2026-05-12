"""GraphRAG corpus serializable data types。"""

from __future__ import annotations

from dataclasses import dataclass


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
