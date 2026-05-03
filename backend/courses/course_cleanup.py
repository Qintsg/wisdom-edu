"""课程删除后的外部图谱资产清理工具。"""

from __future__ import annotations

import logging

from common.neo4j_service import neo4j_service
from platform_ai.rag.corpus import delete_course_index
from platform_ai.rag.runtime import student_graphrag_runtime


logger = logging.getLogger(__name__)


# 维护意图：清理课程对应的 GraphRAG 索引、向量集合和 Neo4j 投影
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def cleanup_course_runtime_artifacts(course_id: int) -> dict[str, object]:
    """清理课程对应的 GraphRAG 索引、向量集合和 Neo4j 投影。"""
    index_removed = delete_course_index(course_id)
    qdrant_removed = student_graphrag_runtime.clear_course_payload(course_id)
    neo4j_cleared = neo4j_service.clear_course_graph(course_id)
    cleanup_report = {
        "course_id": course_id,
        "index_removed": index_removed,
        "qdrant_removed": qdrant_removed,
        "neo4j_cleared": neo4j_cleared,
    }
    logger.info("课程外部图谱资产清理完成: %s", cleanup_report)
    return cleanup_report
