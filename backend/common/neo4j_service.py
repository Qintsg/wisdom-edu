"""Neo4j 图数据库服务兼容入口。"""

from __future__ import annotations

from .neo4j_base import (
    FALLBACK_WARNING,
    Neo4jBaseMixin,
    Neo4jFallbackWarning,
    Neo4jUnavailableError,
)
from .neo4j_crud import Neo4jCrudMixin
from .neo4j_queries import Neo4jQueryMixin
from .neo4j_sync import Neo4jSyncMixin


# 维护意图：Neo4j 图数据库服务类，保留原公共方法与单例入口
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Neo4jService(Neo4jSyncMixin, Neo4jQueryMixin, Neo4jCrudMixin, Neo4jBaseMixin):
    """Neo4j 图数据库服务类，保留原公共方法与单例入口。"""


neo4j_service = Neo4jService()
