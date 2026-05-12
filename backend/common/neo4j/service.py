"""Neo4j 图数据库服务入口。"""

from __future__ import annotations

from common.neo4j.base import (
    FALLBACK_WARNING,
    Neo4jBaseMixin,
    Neo4jFallbackWarning,
    Neo4jUnavailableError,
)
from common.neo4j.crud import Neo4jCrudMixin
from common.neo4j.queries import Neo4jQueryMixin
from common.neo4j.sync import Neo4jSyncMixin


class Neo4jService(Neo4jSyncMixin, Neo4jQueryMixin, Neo4jCrudMixin, Neo4jBaseMixin):
    """Neo4j 图数据库服务类，保留原公共方法与单例入口。"""


neo4j_service = Neo4jService()
