"""Neo4j 服务基础连接与通用异常。"""

from __future__ import annotations

import logging
import time
import warnings
from typing import TYPE_CHECKING, Optional

from django.conf import settings

from common.logging_utils import build_log_message

if TYPE_CHECKING:
    from neo4j import Driver, Query

try:
    from neo4j.exceptions import DriverError
except ImportError:

    # 维护意图：neo4j 未安装时使用的兼容驱动异常占位
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class DriverError(Exception):
        """neo4j 未安装时使用的兼容驱动异常占位。"""


logger = logging.getLogger(__name__)

FALLBACK_WARNING = (
    "Neo4j不可用，已降级到PostgreSQL查询知识图谱数据。图遍历等高级功能不可用。"
)


# 维护意图：Neo4j 数据库不可用异常
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Neo4jUnavailableError(Exception):
    """Neo4j 数据库不可用异常。"""


# 维护意图：Neo4j 降级到 PostgreSQL 时的警告
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Neo4jFallbackWarning(UserWarning):
    """Neo4j 降级到 PostgreSQL 时的警告。"""


# 维护意图：封装 Neo4j 驱动连接、可用性检查与通用辅助方法
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Neo4jBaseMixin:
    """封装 Neo4j 驱动连接、可用性检查与通用辅助方法。"""

    def __init__(self):
        """初始化 Neo4j 连接缓存。"""
        self._driver: Optional["Driver"] = None
        self._is_available: Optional[bool] = None

    # 维护意图：重置连接缓存，供同步前强制重试
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def reset_connection_state(self):
        """重置连接缓存，供同步前强制重试。"""
        driver = self._driver
        if driver is not None:
            try:
                driver.close()
            except (AttributeError, DriverError, OSError, RuntimeError, TypeError):
                pass
        self._driver = None
        self._is_available = None

    # 维护意图：输出 PostgreSQL 降级警告
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _warn_fallback(self, operation: str = ""):
        """输出 PostgreSQL 降级警告。"""
        msg = FALLBACK_WARNING
        if operation:
            msg = f"[{operation}] {msg}"
        logger.warning(
            build_log_message("neo4j.fallback", operation=operation, detail=msg)
        )
        warnings.warn(msg, Neo4jFallbackWarning, stacklevel=3)

    # 维护意图：检查 Neo4j 是否可用
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @property
    def is_available(self) -> bool:
        """检查 Neo4j 是否可用。"""
        if self._is_available is None:
            self._is_available = self._check_connection()
        return self._is_available

    # 维护意图：检查 Neo4j 连接
    # 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
    # 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
    def _check_connection(self) -> bool:
        """检查 Neo4j 连接。"""
        try:
            from neo4j import GraphDatabase
        except ImportError:
            logger.error("neo4j包未安装，知识图谱功能不可用")
            return False

        uri = getattr(settings, "NEO4J_BOLT_URL", "bolt://localhost:7687")
        username = getattr(settings, "NEO4J_USERNAME", "neo4j")
        password = getattr(settings, "NEO4J_PASSWORD", "password")

        last_error = None
        for attempt in range(3):
            driver = None
            try:
                driver = GraphDatabase.driver(uri, auth=(username, password))
                driver.verify_connectivity()
                self._driver = driver
                logger.debug("Neo4j连接成功")
                return True
            except Exception as error:
                last_error = error
                if driver:
                    driver.close()
                if attempt < 2:
                    time.sleep(1)
        logger.error("Neo4j连接失败: %s，知识图谱功能不可用", last_error)
        return False

    # 维护意图：确保 Neo4j 可用，否则抛出异常
    # 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
    # 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
    def _ensure_available(self):
        """确保 Neo4j 可用，否则抛出异常。"""
        if not self.is_available:
            raise Neo4jUnavailableError(
                "Neo4j数据库不可用。请检查Neo4j服务是否启动，以及连接配置是否正确。"
            )

    # 维护意图：将动态 Cypher 文本封装为 Neo4j Query 对象
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    @staticmethod
    def _build_query(query_text: str) -> "Query":
        """将动态 Cypher 文本封装为 Neo4j Query 对象。"""
        from neo4j import Query

        return Query(query_text)

    # 维护意图：获取 Neo4j 驱动
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def _get_driver(self) -> "Driver":
        """获取 Neo4j 驱动。"""
        if self._driver is None:
            self._ensure_available()
            from neo4j import GraphDatabase

            uri = getattr(settings, "NEO4J_BOLT_URL", "bolt://localhost:7687")
            username = getattr(settings, "NEO4J_USERNAME", "neo4j")
            password = getattr(settings, "NEO4J_PASSWORD", "password")
            self._driver = GraphDatabase.driver(uri, auth=(username, password))

        driver = self._driver
        if driver is None:
            raise Neo4jUnavailableError("Neo4j驱动初始化失败，无法创建会话。")
        return driver

    # 维护意图：对外暴露当前可复用的 Neo4j 驱动
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_driver(self) -> "Driver":
        """对外暴露当前可复用的 Neo4j 驱动。"""
        return self._get_driver()

    # 维护意图：解析知识点所属课程，避免多课程图谱查询串课
    # 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
    # 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
    @staticmethod
    def _resolve_point_course_id(point_id: int) -> Optional[int]:
        """解析知识点所属课程，避免多课程图谱查询串课。"""
        from knowledge.models import KnowledgePoint

        return (
            KnowledgePoint.objects.filter(id=point_id)
            .values_list("course_id", flat=True)
            .first()
        )

    # 维护意图：关闭 Neo4j 连接
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def close(self):
        """关闭 Neo4j 连接。"""
        driver = self._driver
        if driver is not None:
            driver.close()
            self._driver = None
