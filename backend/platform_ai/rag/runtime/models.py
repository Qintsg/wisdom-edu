from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import sha256
from math import sqrt
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5
import json
import logging
import re

from neo4j_graphrag.embeddings import SentenceTransformerEmbeddings
from neo4j_graphrag.embeddings.base import Embedder
from neo4j_graphrag.experimental.components.entity_relation_extractor import EntityRelationExtractor
from neo4j_graphrag.experimental.components.types import Neo4jGraph, Neo4jNode, Neo4jRelationship, TextChunks
from neo4j_graphrag.llm.types import ToolCall
from neo4j_graphrag.message_history import MessageHistory
from neo4j_graphrag.tool import ObjectParameter, StringParameter, Tool
from neo4j_graphrag.types import LLMMessage

from platform_ai.rag.corpus import tokenize

logger = logging.getLogger(__name__)

DocumentPayload = dict[str, object]
SourcePayload = dict[str, object]

DEFAULT_VECTOR_DIMENSION = 256
DEFAULT_SENTENCE_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_QDRANT_DIRECTORY = Path("runtime_logs") / "rag" / "qdrant"
COURSE_DOCUMENT_LABEL = "CourseDocument"
COURSE_RETRIEVAL_MODE = "neo4j_graphrag_qdrant"
GRAPH_TOOL_QUERY_MODE = "graph_tools"
GRAPH_QUERY_RETRIEVAL_MODE = "neo4j_graphrag_tools"


@dataclass(frozen=True)
class GraphRAGArtifactReport:
    """描述一次课程级 GraphRAG 物化的主要产物。"""

    collection_name: str
    qdrant_path: str
    vector_points: int
    embedder_provider: str
    neo4j_projection_ready: bool
    projected_documents: int
    projected_relations: int

    def as_dict(self) -> dict[str, object]:
        """转换为适合持久化到课程索引的 JSON 结构。"""
        return {
            "collection_name": self.collection_name,
            "qdrant_path": self.qdrant_path,
            "vector_points": self.vector_points,
            "embedder_provider": self.embedder_provider,
            "neo4j_projection_ready": self.neo4j_projection_ready,
            "projected_documents": self.projected_documents,
            "projected_relations": self.projected_relations,
        }


@dataclass(frozen=True)
class GraphRAGSearchHit:
    """承载一次混合检索返回的单条证据。"""

    external_id: str
    doc_id: str
    title: str
    kind: str
    excerpt: str
    url: str
    score: float
    point_ids: list[int]
    matched_points: list[SourcePayload]
    prerequisites: list[SourcePayload]
    postrequisites: list[SourcePayload]
    source_label: str = COURSE_RETRIEVAL_MODE

    def as_source(self, query_mode: str) -> dict[str, object]:
        """转换为前端可直接消费的证据 source。"""
        return {
            "id": self.external_id,
            "title": self.title,
            "kind": self.kind,
            "url": self.url,
            "excerpt": self.excerpt,
            "query_mode": query_mode,
            "score": round(self.score, 6),
            "retrieval_source": self.source_label,
        }


@dataclass(frozen=True)
class GraphQueryContext:
    """承载官方 ToolsRetriever / Text2Cypher 生成的结构化图查询上下文。"""

    context: str
    sources: list[dict[str, object]]
    tools_selected: list[str]
    generated_cypher: str
    query_modes: list[str]
    matched_point_ids: list[int]
    mode: str = GRAPH_QUERY_RETRIEVAL_MODE

    def as_dict(self) -> dict[str, object]:
        """转换为稳定的业务层载荷。"""
        return {
            "context": self.context,
            "sources": self.sources,
            "tools_selected": self.tools_selected,
            "generated_cypher": self.generated_cypher,
            "query_modes": self.query_modes,
            "matched_point_ids": self.matched_point_ids,
            "mode": self.mode,
        }


def _coerce_string(value: object) -> str:
    """把任意输入收敛为稳定字符串，避免外部数据结构污染。"""
    return str(value).strip() if value is not None else ""


def _coerce_int(value: object, default: int = 0) -> int:
    """把弱类型输入稳定转换为整数。"""
    normalized_text = _coerce_string(value)
    if normalized_text.lstrip("-").isdigit():
        return int(normalized_text)
    return default


def _coerce_int_list(value: object) -> list[int]:
    """提取 payload 中的整型列表，过滤空值与非法值。"""
    normalized_ids: list[int] = []
    if isinstance(value, list):
        raw_values = value
    else:
        raw_values = [value]

    for raw_value in raw_values:
        normalized_text = _coerce_string(raw_value)
        if not normalized_text or not normalized_text.lstrip("-").isdigit():
            continue
        normalized_ids.append(int(normalized_text))
    return normalized_ids


def _escape_cypher_string(value: str) -> str:
    """转义 Cypher 单引号字符串，避免模板化查询被截断。"""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _message_history_text(
    message_history: list[LLMMessage] | MessageHistory | None,
) -> str:
    """将消息历史压缩为可读文本，供路由与提示生成复用。"""
    if message_history is None:
        return ""

    raw_messages = getattr(message_history, "messages", message_history)
    if not isinstance(raw_messages, list):
        return ""

    normalized_lines: list[str] = []
    for raw_message in raw_messages[:8]:
        if isinstance(raw_message, dict):
            role = _coerce_string(raw_message.get("role")) or "user"
            content = _coerce_string(raw_message.get("content"))
        else:
            role = _coerce_string(getattr(raw_message, "role", "")) or "user"
            content = _coerce_string(getattr(raw_message, "content", ""))
        if content:
            normalized_lines.append(f"{role}: {content}")
    return "\n".join(normalized_lines)


def _query_tool_parameters(description: str) -> ObjectParameter:
    """为 ToolsRetriever 生成极简参数模式，降低工具路由复杂度。"""
    return ObjectParameter(
        description="课程图查询参数",
        properties={
            "query_text": StringParameter(
                description=description,
                required=True,
            )
        },
        required_properties=["query_text"],
        additional_properties=False,
    )


def _dedupe_strings(items: Sequence[str]) -> list[str]:
    """保持原顺序去重字符串列表。"""
    seen_items: set[str] = set()
    ordered_items: list[str] = []
    for item in items:
        normalized_item = item.strip()
        if not normalized_item or normalized_item in seen_items:
            continue
        seen_items.add(normalized_item)
        ordered_items.append(normalized_item)
    return ordered_items

def _compact_excerpt(text: str, limit: int = 220) -> str:
    """压缩文本片段，便于进入聊天窗口与知识点详情。"""
    normalized = " ".join(segment.strip() for segment in text.splitlines() if segment.strip())
    return normalized[:limit]


def _vector_point_ids(document: DocumentPayload) -> list[int]:
    """从课程文档 payload 中提取关联知识点 ID 列表。"""
    metadata = document.get("metadata")
    point_ids: list[int] = []
    if isinstance(metadata, dict):
        point_ids.extend(_coerce_int_list(metadata.get("knowledge_point_ids", [])))
        point_ids.extend(_coerce_int_list(metadata.get("knowledge_point_id")))
        entity_ids = metadata.get("entity_ids")
        if isinstance(entity_ids, list):
            for entity_id in entity_ids:
                normalized = _coerce_string(entity_id)
                if normalized.startswith("kp:"):
                    point_ids.extend(_coerce_int_list(normalized.partition(":")[2]))
    document_id = _coerce_string(document.get("id"))
    if document_id.startswith("kp:"):
        point_ids.extend(_coerce_int_list(document_id.partition(":")[2]))
    return sorted(set(point_ids))


def _qdrant_point_id(external_id: str) -> str:
    """为 Qdrant 本地模式生成稳定 UUID。"""
    normalized_external_id = _coerce_string(external_id)
    if not normalized_external_id:
        normalized_external_id = "empty-document"
    return str(uuid5(NAMESPACE_URL, f"wisdom-edu:{normalized_external_id}"))


class TokenHashEmbedder(Embedder):
    """离线可用的哈希向量器。

    这里不依赖外部模型下载，适合测试与本地开发。
    真正部署时可以通过环境变量切换到 `SentenceTransformerEmbeddings`。
    """

    def __init__(self, dimensions: int = DEFAULT_VECTOR_DIMENSION) -> None:
        super().__init__()
        self.dimensions = max(64, int(dimensions))

    def embed_query(self, text: str) -> list[float]:
        """把查询文本编码为稠密向量。

        做法是对 token 做双哈希投影：
        - 一个哈希决定落桶位置；
        - 另一个哈希决定正负符号；
        - 最后进行 $L_2$ 归一化，便于余弦检索。
        """
        tokens = list(tokenize(text))
        if not tokens:
            tokens = [text.strip() or "empty"]

        vector = [0.0] * self.dimensions
        for token in tokens:
            digest = sha256(token.encode("utf-8")).hexdigest()
            bucket = int(digest[:8], 16) % self.dimensions
            sign = 1.0 if int(digest[8:16], 16) % 2 == 0 else -1.0
            weight = 1.0 + min(len(token), 12) / 12.0
            vector[bucket] += sign * weight

        norm = sqrt(sum(component * component for component in vector))
        if norm <= 0:
            return vector
        return [component / norm for component in vector]


class SafeSentenceTransformerEmbedder(Embedder):
    """对官方 SentenceTransformer 向量器做安全包装。

    这样即使本地没有模型缓存、网络不可用或运行时初始化失败，
    也会自动回退到哈希向量器，而不会让索引构建整体中断。
    """

    def __init__(self, model_name: str, fallback_embedder: TokenHashEmbedder) -> None:
        super().__init__()
        self.model_name = model_name
        self.fallback_embedder = fallback_embedder
        self._delegate: SentenceTransformerEmbeddings | None = None
        self._delegate_unavailable = False

    def _resolve_delegate(self) -> SentenceTransformerEmbeddings | None:
        """延迟初始化真实 embedding 模型，避免模块导入即触发下载。"""
        if self._delegate_unavailable:
            return None
        if self._delegate is not None:
            return self._delegate
        try:
            self._delegate = SentenceTransformerEmbeddings(model=self.model_name)
            return self._delegate
        except Exception as error:  # pragma: no cover - 仅在模型不可用时触发
            logger.warning("SentenceTransformer 初始化失败，回退哈希向量器: model=%s error=%s", self.model_name, error)
            self._delegate_unavailable = True
            return None

    def embed_query(self, text: str) -> list[float]:
        """优先使用 SentenceTransformer，失败时自动回退。"""
        delegate = self._resolve_delegate()
        if delegate is None:
            return self.fallback_embedder.embed_query(text)
        try:
            return delegate.embed_query(text)
        except Exception as error:  # pragma: no cover - 仅在模型运行失败时触发
            logger.warning("SentenceTransformer 编码失败，回退哈希向量器: model=%s error=%s", self.model_name, error)
            self._delegate_unavailable = True
            return self.fallback_embedder.embed_query(text)


class StructuredCourseGraphExtractor(EntityRelationExtractor):
    """把课程已有结构化文档投影成 GraphRAG 图对象。

    这里并不重新“猜测”知识点关系，而是显式复用课程现成事实：
    - 每条课程文档都会生成一个 `CourseDocument` 节点；
    - 文档与知识点之间会生成 `ABOUT` 关系；
    - 这些节点稍后会被同步到 Neo4j，供官方 Qdrant 检索器回查图谱。
    """

    def __init__(self, course_id: int) -> None:
        super().__init__()
        self.course_id = int(course_id)

    async def run(
        self,
        chunks: TextChunks,
        document_info: object | None = None,
        lexical_graph_config: object | None = None,
        **kwargs: object,
    ) -> Neo4jGraph:
        del document_info, lexical_graph_config, kwargs

        graph_nodes: list[Neo4jNode] = []
        graph_relationships: list[Neo4jRelationship] = []

        for chunk in chunks.chunks:
            metadata = chunk.metadata if isinstance(chunk.metadata, dict) else {}
            external_id = _coerce_string(metadata.get("external_id") or chunk.uid or f"chunk:{chunk.index}")
            title = _coerce_string(metadata.get("title")) or external_id
            kind = _coerce_string(metadata.get("kind")) or "document"
            url = _coerce_string(metadata.get("url"))
            chapter = _coerce_string(metadata.get("chapter"))
            point_ids = _coerce_int_list(metadata.get("point_ids", []))
            point_id_strings = [str(point_id) for point_id in point_ids]

            graph_nodes.append(
                Neo4jNode(
                    id=external_id,
                    label=COURSE_DOCUMENT_LABEL,
                    properties={
                        "external_id": external_id,
                        "doc_id": _coerce_string(metadata.get("doc_id") or external_id),
                        "course_id": self.course_id,
                        "title": title,
                        "kind": kind,
                        "content": chunk.text,
                        "url": url,
                        "chapter": chapter,
                        "point_ids_csv": ",".join(point_id_strings),
                        "excerpt": _compact_excerpt(chunk.text),
                    },
                )
            )

            for point_id in point_ids:
                graph_relationships.append(
                    Neo4jRelationship(
                        start_node_id=external_id,
                        end_node_id=f"kp:{point_id}",
                        type="ABOUT",
                        properties={
                            "course_id": self.course_id,
                            "point_id": point_id,
                        },
                    )
                )

        return Neo4jGraph(nodes=graph_nodes, relationships=graph_relationships)
