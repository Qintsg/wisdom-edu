"""学生端 GraphRAG 索引与载荷读取 mixin。"""
from __future__ import annotations

import logging
from collections import defaultdict

from .corpus import build_course_graph_index, load_course_index, save_course_index


logger = logging.getLogger(__name__)


# 维护意图：提供课程索引构建、物化校验与安全载荷读取
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class StudentIndexMixin:
    """提供课程索引构建、物化校验与安全载荷读取。"""

    # 维护意图：构建课程 GraphRAG 索引
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    def build_index(self, course_id: int, persist: bool = True, force_rebuild: bool = False) -> dict[str, object]:
        """构建课程 GraphRAG 索引。"""
        if not force_rebuild:
            payload = load_course_index(course_id)
            if payload.get("index_type") == self.INDEX_VERSION and payload.get("entities"):
                return payload

        payload = build_course_graph_index(course_id)
        payload["index_type"] = self.INDEX_VERSION
        try:
            payload["graph_rag_artifacts"] = self._runtime().materialize_course_payload(course_id, payload)
        except Exception as error:
            logger.warning("课程 GraphRAG 物化失败，保留本地索引回退: course=%s error=%s", course_id, error)
            payload["graph_rag_artifacts"] = {
                "collection_name": self._runtime().collection_name(course_id),
                "qdrant_path": str(self._runtime().qdrant_directory()),
                "vector_points": 0,
                "embedder_provider": "degraded",
                "neo4j_projection_ready": False,
                "projected_documents": 0,
                "projected_relations": 0,
            }
        if persist:
            save_course_index(course_id, payload)
        return payload

    # 维护意图：确保课程索引已可用，必要时自动重建
    # 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
    # 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
    def _ensure_index(self, course_id: int, persist: bool = True) -> dict[str, object]:
        """确保课程索引已可用，必要时自动重建。"""
        payload = load_course_index(course_id)
        if payload.get("index_type") == self.INDEX_VERSION and payload.get("entities"):
            try:
                payload["graph_rag_artifacts"] = self._runtime().ensure_materialized(course_id, payload)
            except Exception as error:
                logger.warning("课程 GraphRAG 物化校验失败，继续使用本地索引: course=%s error=%s", course_id, error)
            return payload
        return self.build_index(course_id, persist=persist, force_rebuild=True)

    # 维护意图：安全读取实体列表
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _entity_list(self, payload: dict[str, object]) -> list[dict[str, object]]:
        """安全读取实体列表。"""
        raw_entities = payload.get("entities")
        if not isinstance(raw_entities, list):
            return []
        return [item for item in raw_entities if isinstance(item, dict)]

    # 维护意图：安全读取关系列表
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _relationship_list(self, payload: dict[str, object]) -> list[dict[str, object]]:
        """安全读取关系列表。"""
        raw_relationships = payload.get("relationships")
        if not isinstance(raw_relationships, list):
            return []
        return [item for item in raw_relationships if isinstance(item, dict)]

    # 维护意图：安全读取文档列表
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _document_list(self, payload: dict[str, object]) -> list[dict[str, object]]:
        """安全读取文档列表。"""
        raw_documents = payload.get("documents")
        if not isinstance(raw_documents, list):
            return []
        return [item for item in raw_documents if isinstance(item, dict)]

    # 维护意图：安全读取社区列表
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _community_list(self, payload: dict[str, object]) -> list[dict[str, object]]:
        """安全读取社区列表。"""
        raw_communities = payload.get("communities")
        if not isinstance(raw_communities, list):
            return []
        return [item for item in raw_communities if isinstance(item, dict)]

    # 维护意图：安全读取社区报告列表
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _community_report_list(self, payload: dict[str, object]) -> list[dict[str, object]]:
        """安全读取社区报告列表。"""
        raw_reports = payload.get("community_reports")
        if not isinstance(raw_reports, list):
            return []
        return [item for item in raw_reports if isinstance(item, dict)]

    # 维护意图：将实体列表转换为按实体 ID 索引的映射
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _entity_map(self, payload: dict[str, object]) -> dict[str, dict[str, object]]:
        """将实体列表转换为按实体 ID 索引的映射。"""
        entity_map: dict[str, dict[str, object]] = {}
        for entity in self._entity_list(payload):
            entity_id = str(entity.get("id", "")).strip()
            if entity_id:
                entity_map[entity_id] = entity
        return entity_map

    # 维护意图：构建社区 ID 到社区描述的映射
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _community_lookup(self, payload: dict[str, object]) -> dict[str, dict[str, object]]:
        """构建社区 ID 到社区描述的映射。"""
        community_lookup: dict[str, dict[str, object]] = {}
        for community in self._community_list(payload):
            community_id = str(community.get("id", "")).strip()
            if community_id:
                community_lookup[community_id] = community
        return community_lookup

    # 维护意图：构建实体到社区的反向索引
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _entity_to_communities(self, payload: dict[str, object]) -> dict[str, list[str]]:
        """构建实体到社区的反向索引。"""
        membership: dict[str, list[str]] = defaultdict(list)
        for community in self._community_list(payload):
            community_id = str(community.get("id", "")).strip()
            if not community_id:
                continue
            entity_ids = community.get("entity_ids")
            if not isinstance(entity_ids, list):
                continue
            for entity_id in entity_ids:
                normalized = str(entity_id).strip()
                if normalized:
                    membership[normalized].append(community_id)
        return dict(membership)
