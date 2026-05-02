from __future__ import annotations

from collections import defaultdict
import logging

from neo4j_graphrag.retrievers import QdrantNeo4jRetriever
from neo4j_graphrag.types import RetrieverResultItem

from platform_ai.rag.runtime_models import (
    COURSE_DOCUMENT_LABEL,
    COURSE_RETRIEVAL_MODE,
    GraphRAGSearchHit,
    SourcePayload,
    _coerce_int_list,
    _coerce_string,
)
from platform_ai.rag.runtime_proxies import neo4j_service

logger = logging.getLogger(__name__)


class CourseGraphRAGSearchMixin:
    """课程文档向量检索与知识点聚合能力。"""

    def _retrieval_query(self) -> str:
        """定义官方检索器回查 Neo4j 时的课程级取图语句。"""
        return """
        WITH node, score
        OPTIONAL MATCH (node)-[:ABOUT]->(point:KnowledgePoint)
        OPTIONAL MATCH (pre:KnowledgePoint)-[:PREREQUISITE]->(point)
        OPTIONAL MATCH (point)-[:PREREQUISITE]->(post:KnowledgePoint)
        RETURN node.external_id AS external_id,
               node.doc_id AS doc_id,
               node.title AS title,
               node.kind AS kind,
               node.url AS url,
               node.excerpt AS excerpt,
               node.point_ids AS point_ids,
               score,
               collect(DISTINCT CASE WHEN point.id IS NULL THEN NULL ELSE {point_id: point.id, point_name: point.name} END) AS matched_points,
               collect(DISTINCT CASE WHEN pre.id IS NULL THEN NULL ELSE {point_id: pre.id, point_name: pre.name} END) AS prerequisites,
               collect(DISTINCT CASE WHEN post.id IS NULL THEN NULL ELSE {point_id: post.id, point_name: post.name} END) AS postrequisites
        """

    def _format_retriever_record(self, record: object) -> RetrieverResultItem:
        """把官方检索器返回的 Neo4j 记录收敛为统一元数据。"""
        get_value = getattr(record, "get")
        metadata = {
            "external_id": _coerce_string(get_value("external_id")),
            "doc_id": _coerce_string(get_value("doc_id")),
            "title": _coerce_string(get_value("title")) or "课程证据",
            "kind": _coerce_string(get_value("kind")) or "document",
            "url": _coerce_string(get_value("url")),
            "excerpt": _coerce_string(get_value("excerpt")),
            "score": float(get_value("score") or 0.0),
            "point_ids": _coerce_int_list(get_value("point_ids") or []),
            "matched_points": [item for item in (get_value("matched_points") or []) if isinstance(item, dict)],
            "prerequisites": [item for item in (get_value("prerequisites") or []) if isinstance(item, dict)],
            "postrequisites": [item for item in (get_value("postrequisites") or []) if isinstance(item, dict)],
            "retrieval_source": COURSE_RETRIEVAL_MODE,
        }
        return RetrieverResultItem(content=metadata["excerpt"] or metadata["title"], metadata=metadata)

    def _parse_items(self, items: list[object]) -> list[GraphRAGSearchHit]:
        """将 RetrieverResult items 解析成业务层更易处理的 dataclass。"""
        parsed_hits: list[GraphRAGSearchHit] = []
        for item in items:
            metadata = getattr(item, "metadata", None)
            if not isinstance(metadata, dict):
                continue
            parsed_hits.append(
                GraphRAGSearchHit(
                    external_id=_coerce_string(metadata.get("external_id")),
                    doc_id=_coerce_string(metadata.get("doc_id") or metadata.get("external_id")),
                    title=_coerce_string(metadata.get("title")) or "课程证据",
                    kind=_coerce_string(metadata.get("kind")) or "document",
                    excerpt=_coerce_string(metadata.get("excerpt")),
                    url=_coerce_string(metadata.get("url")),
                    score=float(metadata.get("score") or 0.0),
                    point_ids=_coerce_int_list(metadata.get("point_ids") or []),
                    matched_points=[entry for entry in metadata.get("matched_points", []) if isinstance(entry, dict)],
                    prerequisites=[entry for entry in metadata.get("prerequisites", []) if isinstance(entry, dict)],
                    postrequisites=[entry for entry in metadata.get("postrequisites", []) if isinstance(entry, dict)],
                    source_label=_coerce_string(metadata.get("retrieval_source")) or COURSE_RETRIEVAL_MODE,
                )
            )
        return parsed_hits

    def _search_qdrant_only(self, course_id: int, query: str, limit: int) -> list[GraphRAGSearchHit]:
        """Neo4j 不可用时，仅凭向量库返回基础证据。"""
        collection_name = self.collection_name(course_id)
        if not self._collection_exists(collection_name):
            return []
        _, embedder = self._embedder()
        response = self._qdrant().query_points(
            collection_name=collection_name,
            query=embedder.embed_query(query),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        fallback_hits: list[GraphRAGSearchHit] = []
        for point in response.points:
            payload = point.payload if isinstance(point.payload, dict) else {}
            fallback_hits.append(
                GraphRAGSearchHit(
                    external_id=_coerce_string(payload.get("external_id") or point.id),
                    doc_id=_coerce_string(payload.get("doc_id") or point.id),
                    title=_coerce_string(payload.get("title")) or "课程证据",
                    kind=_coerce_string(payload.get("kind")) or "document",
                    excerpt=_coerce_string(payload.get("excerpt")),
                    url=_coerce_string(payload.get("url")),
                    score=float(getattr(point, "score", 0.0) or 0.0),
                    point_ids=_coerce_int_list(payload.get("point_ids") or []),
                    matched_points=[],
                    prerequisites=[],
                    postrequisites=[],
                    source_label="qdrant_local_only",
                )
            )
        return fallback_hits

    def search_documents(
        self,
        *,
        course_id: int,
        query: str,
        limit: int = 6,
        seed_point_ids: list[int] | None = None,
    ) -> list[GraphRAGSearchHit]:
        """执行课程级混合检索，并对种子知识点做轻量重排。"""
        normalized_query = query.strip()
        if not normalized_query:
            return []

        if not neo4j_service.is_available:
            return self._search_qdrant_only(course_id=course_id, query=normalized_query, limit=limit)

        collection_name = self.collection_name(course_id)
        if not self._collection_exists(collection_name):
            return []

        provider_name, embedder = self._embedder()
        del provider_name
        graph_driver = neo4j_service.get_driver()
        if graph_driver is None:
            return self._search_qdrant_only(course_id=course_id, query=normalized_query, limit=limit)
        retriever = QdrantNeo4jRetriever(
            driver=graph_driver,
            client=self._qdrant(),
            collection_name=collection_name,
            embedder=embedder,
            id_property_neo4j="external_id",
            id_property_external="external_id",
            node_label_neo4j=COURSE_DOCUMENT_LABEL,
            result_formatter=self._format_retriever_record,
            retrieval_query=self._retrieval_query(),
        )
        try:
            retriever_result = retriever.search(query_text=normalized_query, top_k=max(limit * 2, 8))
            parsed_hits = self._parse_items(list(retriever_result.items))
        except Exception as error:
            logger.warning("官方 GraphRAG 检索失败，回退 Qdrant 本地检索: course=%s error=%s", course_id, error)
            parsed_hits = self._search_qdrant_only(course_id=course_id, query=normalized_query, limit=max(limit * 2, 8))

        boosted_seed_ids = set(seed_point_ids or [])
        reranked_hits = sorted(
            parsed_hits,
            key=lambda hit: (
                -(
                    hit.score
                    + (2.5 if boosted_seed_ids & set(hit.point_ids) else 0.0)
                    + (0.4 if hit.kind == "knowledge_point" else 0.0)
                ),
                hit.title,
            ),
        )
        return reranked_hits[:limit]

    def search_points(self, *, course_id: int, query: str, limit: int = 8) -> list[dict[str, object]]:
        """将文档级命中聚合成知识点级候选集合。"""
        aggregated_scores: defaultdict[int, float] = defaultdict(float)
        source_titles: defaultdict[int, list[str]] = defaultdict(list)
        prerequisite_map: dict[int, list[SourcePayload]] = defaultdict(list)
        postrequisite_map: dict[int, list[SourcePayload]] = defaultdict(list)

        for rank, hit in enumerate(self.search_documents(course_id=course_id, query=query, limit=max(limit * 2, 8)), start=1):
            point_entries = [entry for entry in hit.matched_points if isinstance(entry.get("point_id"), int)]
            if not point_entries:
                point_entries = [
                    {"point_id": point_id, "point_name": ""}
                    for point_id in hit.point_ids
                ]

            rank_bonus = 1.0 / rank
            for point_entry in point_entries:
                point_id = point_entry.get("point_id")
                if not isinstance(point_id, int):
                    continue
                aggregated_scores[point_id] += hit.score + rank_bonus
                if hit.title and hit.title not in source_titles[point_id]:
                    source_titles[point_id].append(hit.title)
                prerequisite_map.setdefault(point_id, [])
                postrequisite_map.setdefault(point_id, [])
                for prerequisite in hit.prerequisites:
                    if prerequisite not in prerequisite_map[point_id]:
                        prerequisite_map[point_id].append(prerequisite)
                for postrequisite in hit.postrequisites:
                    if postrequisite not in postrequisite_map[point_id]:
                        postrequisite_map[point_id].append(postrequisite)

        ordered_point_ids = [
            point_id
            for point_id, _ in sorted(aggregated_scores.items(), key=lambda item: (-item[1], item[0]))[:limit]
        ]
        return [
            {
                "point_id": point_id,
                "graph_rag_score": round(aggregated_scores[point_id], 6),
                "source_titles": source_titles.get(point_id, [])[:4],
                "prerequisites": prerequisite_map.get(point_id, [])[:4],
                "postrequisites": postrequisite_map.get(point_id, [])[:4],
            }
            for point_id in ordered_point_ids
        ]
