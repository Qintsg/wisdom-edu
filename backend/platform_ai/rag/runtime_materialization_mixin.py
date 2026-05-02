from __future__ import annotations

from pathlib import Path
import asyncio
import logging

from django.conf import settings
from neo4j_graphrag.embeddings.base import Embedder
from neo4j_graphrag.experimental.components.types import Neo4jGraph, TextChunk, TextChunks
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from platform_ai.rag.runtime_models import (
    COURSE_DOCUMENT_LABEL,
    DEFAULT_QDRANT_DIRECTORY,
    DEFAULT_SENTENCE_MODEL,
    DEFAULT_VECTOR_DIMENSION,
    DocumentPayload,
    GraphRAGArtifactReport,
    SafeSentenceTransformerEmbedder,
    StructuredCourseGraphExtractor,
    TokenHashEmbedder,
    _coerce_int,
    _coerce_int_list,
    _coerce_string,
    _compact_excerpt,
    _qdrant_point_id,
    _vector_point_ids,
)
from platform_ai.rag.runtime_proxies import neo4j_service

logger = logging.getLogger(__name__)


class CourseGraphRAGMaterializationMixin:
    """课程 GraphRAG 索引物化与清理能力。"""

    def __init__(self) -> None:
        self._qdrant_client: QdrantClient | None = None
        self._hash_embedder = TokenHashEmbedder(self._vector_dimension())
        self._configured_embedder: Embedder | None = None
        self._configured_provider: str | None = None

    def _vector_dimension(self) -> int:
        """读取向量维度配置；对哈希向量器直接决定桶数量。"""
        raw_value = str(getattr(settings, "GRAPHRAG_VECTOR_DIMENSION", DEFAULT_VECTOR_DIMENSION)).strip()
        if raw_value.isdigit():
            return max(64, int(raw_value))
        return DEFAULT_VECTOR_DIMENSION

    def qdrant_directory(self) -> Path:
        """返回本地 Qdrant 持久化目录。"""
        configured_path = str(getattr(settings, "GRAPHRAG_QDRANT_PATH", "")).strip()
        if configured_path:
            return Path(configured_path)
        return Path(settings.BASE_DIR) / DEFAULT_QDRANT_DIRECTORY

    def collection_name(self, course_id: int) -> str:
        """为每门课程生成稳定的向量集合名称。"""
        return f"course_{int(course_id)}_documents_v2"

    def _qdrant(self) -> QdrantClient:
        """按需初始化本地 Qdrant 客户端。"""
        if self._qdrant_client is None:
            storage_path = self.qdrant_directory()
            storage_path.mkdir(parents=True, exist_ok=True)
            self._qdrant_client = QdrantClient(path=str(storage_path))
        return self._qdrant_client

    def _embedder(self) -> tuple[str, Embedder]:
        """根据配置解析实际使用的 embedder。"""
        configured_provider = str(getattr(settings, "GRAPHRAG_EMBEDDER_PROVIDER", "hash")).strip().lower() or "hash"
        if self._configured_embedder is not None and self._configured_provider == configured_provider:
            return configured_provider, self._configured_embedder

        if configured_provider == "sentence_transformer":
            model_name = str(getattr(settings, "GRAPHRAG_SENTENCE_MODEL", DEFAULT_SENTENCE_MODEL)).strip() or DEFAULT_SENTENCE_MODEL
            self._configured_embedder = SafeSentenceTransformerEmbedder(model_name=model_name, fallback_embedder=self._hash_embedder)
        else:
            configured_provider = "hash"
            self._configured_embedder = self._hash_embedder

        self._configured_provider = configured_provider
        return configured_provider, self._configured_embedder

    def _collection_exists(self, collection_name: str) -> bool:
        """安全检查向量集合是否存在。"""
        try:
            return self._qdrant().collection_exists(collection_name)
        except Exception as error:
            logger.warning("检查 Qdrant 集合失败: collection=%s error=%s", collection_name, error)
            return False

    def _build_chunks(self, documents: list[DocumentPayload]) -> TextChunks:
        """把课程文档转换为 GraphRAG extractor 所需的 TextChunks。"""
        chunks: list[TextChunk] = []
        for index, document in enumerate(documents):
            metadata = document.get("metadata")
            metadata_dict = metadata if isinstance(metadata, dict) else {}
            external_id = _coerce_string(document.get("id")) or f"doc:{index}"
            chunks.append(
                TextChunk(
                    text=_coerce_string(document.get("content")),
                    index=index,
                    metadata={
                        "external_id": external_id,
                        "doc_id": external_id,
                        "title": _coerce_string(document.get("title")),
                        "kind": _coerce_string(document.get("kind")),
                        "url": _coerce_string(document.get("url")),
                        "chapter": _coerce_string(metadata_dict.get("chapter")),
                        "point_ids": _vector_point_ids(document),
                    },
                    uid=external_id,
                )
            )
        return TextChunks(chunks=chunks)

    def _projection_from_graph(self, graph: Neo4jGraph) -> tuple[list[DocumentPayload], list[DocumentPayload]]:
        """把 extractor 输出拆成 Neo4j 可直接写入的节点与关系投影。"""
        projected_documents: list[DocumentPayload] = []
        projected_links: list[DocumentPayload] = []

        for graph_node in graph.nodes:
            if graph_node.label != COURSE_DOCUMENT_LABEL:
                continue
            node_properties = graph_node.properties or {}
            projected_documents.append(
                {
                    "external_id": _coerce_string(node_properties.get("external_id") or graph_node.id),
                    "doc_id": _coerce_string(node_properties.get("doc_id") or graph_node.id),
                    "title": _coerce_string(node_properties.get("title")),
                    "kind": _coerce_string(node_properties.get("kind")),
                    "content": _coerce_string(node_properties.get("content")),
                    "url": _coerce_string(node_properties.get("url")),
                    "chapter": _coerce_string(node_properties.get("chapter")),
					"point_ids": _coerce_int_list(
						_coerce_string(node_properties.get("point_ids_csv")).split(",")
					),
                    "excerpt": _coerce_string(node_properties.get("excerpt")),
                }
            )

        for graph_relationship in graph.relationships:
            if graph_relationship.type != "ABOUT":
                continue
            point_token = _coerce_string(graph_relationship.end_node_id)
            if not point_token.startswith("kp:"):
                continue
            point_text = point_token.partition(":")[2]
            if not point_text.isdigit():
                continue
            projected_links.append(
                {
                    "external_id": _coerce_string(graph_relationship.start_node_id),
                    "point_id": int(point_text),
                }
            )

        return projected_documents, projected_links

    def _vector_points(self, documents: list[DocumentPayload], embedder: Embedder) -> tuple[int, list[PointStruct]]:
        """为课程文档生成 Qdrant Point 列表，并返回向量维度。"""
        vector_points: list[PointStruct] = []
        vector_size = 0
        for document in documents:
            external_id = _coerce_string(document.get("id"))
            if not external_id:
                continue
            content = _coerce_string(document.get("content"))
            vector = embedder.embed_query(content)
            if not vector:
                continue
            vector_size = max(vector_size, len(vector))
            metadata = document.get("metadata")
            metadata_dict = metadata if isinstance(metadata, dict) else {}
            payload = {
                "external_id": external_id,
                "doc_id": external_id,
                "course_id": _coerce_int(metadata_dict.get("course_id"), default=0),
                "title": _coerce_string(document.get("title")),
                "kind": _coerce_string(document.get("kind")),
                "url": _coerce_string(document.get("url")),
                "chapter": _coerce_string(metadata_dict.get("chapter")),
                "point_ids": _vector_point_ids(document),
                "excerpt": _compact_excerpt(content),
            }
            vector_points.append(
                PointStruct(
                    id=_qdrant_point_id(external_id),
                    vector=vector,
                    payload=payload,
                )
            )
        return vector_size, vector_points

    def materialize_course_payload(self, course_id: int, payload: DocumentPayload) -> dict[str, object]:
        """将课程索引物化到 Qdrant 与 Neo4j GraphRAG 投影。"""
        raw_documents = payload.get("documents")
        documents = [item for item in raw_documents if isinstance(item, dict)] if isinstance(raw_documents, list) else []
        provider_name, embedder = self._embedder()
        collection_name = self.collection_name(course_id)

        if self._collection_exists(collection_name):
            self._qdrant().delete_collection(collection_name)

        vector_size, vector_points = self._vector_points(documents, embedder)
        self._qdrant().create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size or self._vector_dimension(), distance=Distance.COSINE),
            on_disk_payload=True,
        )
        if vector_points:
            self._qdrant().upsert(collection_name=collection_name, points=vector_points, wait=True)

        extractor = StructuredCourseGraphExtractor(course_id=course_id)
        extracted_graph = asyncio.run(extractor.run(self._build_chunks(documents)))
        projected_documents, projected_links = self._projection_from_graph(extracted_graph)
        neo4j_report = neo4j_service.sync_course_graphrag_projection(
            course_id=course_id,
            documents=projected_documents,
            about_links=projected_links,
        )
        artifact_report = GraphRAGArtifactReport(
            collection_name=collection_name,
            qdrant_path=str(self.qdrant_directory()),
            vector_points=len(vector_points),
            embedder_provider=provider_name,
            neo4j_projection_ready=bool(neo4j_report.get("status") == "success"),
            projected_documents=_coerce_int(neo4j_report.get("documents", 0), default=0),
            projected_relations=_coerce_int(neo4j_report.get("relations", 0), default=0),
        )
        payload["graph_rag_artifacts"] = artifact_report.as_dict()
        return artifact_report.as_dict()

    def ensure_materialized(self, course_id: int, payload: DocumentPayload) -> dict[str, object]:
        """确保课程索引的向量集合与 Neo4j 投影同时存在。"""
        collection_name = self.collection_name(course_id)
        has_collection = self._collection_exists(collection_name)
        has_projection = neo4j_service.has_course_graphrag_projection(course_id)
        artifact_payload = payload.get("graph_rag_artifacts")
        if has_collection and (has_projection or not neo4j_service.is_available) and isinstance(artifact_payload, dict):
            return artifact_payload
        return self.materialize_course_payload(course_id, payload)

    def clear_course_payload(self, course_id: int) -> bool:
        """删除课程级 Qdrant 向量集合，避免删课后残留僵尸索引。"""
        collection_name = self.collection_name(course_id)
        if not self._collection_exists(collection_name):
            return False
        try:
            self._qdrant().delete_collection(collection_name)
        except Exception as error:
            logger.warning("清理课程 Qdrant 集合失败: course=%s error=%s", course_id, error)
            return False
        return True
