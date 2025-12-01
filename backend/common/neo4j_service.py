"""
Neo4j图数据库服务模块

提供知识图谱的图数据库操作，支持：
- 知识点节点的CRUD操作
- 知识关系的创建和查询
- 图遍历和路径查询
- 知识图谱查询（Neo4j优先，PostgreSQL降级）
- 测试数据导入

知识图谱优先存储在Neo4j中。当Neo4j不可用时，降级到PostgreSQL并输出警告。

使用示例:
    from common.neo4j_service import neo4j_service

    # 检查Neo4j是否可用
    if not neo4j_service.is_available:
        logger.warning("Neo4j不可用，将降级使用PostgreSQL")

    # 同步知识图谱到Neo4j
    neo4j_service.sync_knowledge_graph(course_id=1)

    # 查询知识图谱（Neo4j优先，PostgreSQL降级）
    result = neo4j_service.get_knowledge_map(course_id=1)

    # 查询前置知识点
    prerequisites = neo4j_service.get_prerequisites(point_id=10)
"""

import logging
import time
import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from django.conf import settings
from common.logging_utils import build_log_message

if TYPE_CHECKING:
    from neo4j import Driver, Query

try:
    from neo4j.exceptions import DriverError
except ImportError:

    class DriverError(Exception):
        """neo4j 未安装时使用的兼容驱动异常占位。"""

        pass

logger = logging.getLogger(__name__)

FALLBACK_WARNING = (
    "Neo4j不可用，已降级到PostgreSQL查询知识图谱数据。图遍历等高级功能不可用。"
)


class Neo4jUnavailableError(Exception):
    """Neo4j数据库不可用异常"""

    pass


class Neo4jFallbackWarning(UserWarning):
    """Neo4j降级到PostgreSQL时的警告"""

    pass


class Neo4jService:
    """
    Neo4j图数据库服务类

    封装Neo4j数据库操作，提供知识图谱相关的图查询功能。
    知识图谱优先存储在Neo4j中，当Neo4j不可用时降级到PostgreSQL并输出警告。
    """

    def __init__(self):
        """初始化Neo4j连接"""
        self._driver: Optional["Driver"] = None
        self._is_available: Optional[bool] = None

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

    def _warn_fallback(self, operation: str = ""):
        """输出PostgreSQL降级警告"""
        msg = FALLBACK_WARNING
        if operation:
            msg = f"[{operation}] {msg}"
        logger.warning(
            build_log_message("neo4j.fallback", operation=operation, detail=msg)
        )
        warnings.warn(msg, Neo4jFallbackWarning, stacklevel=3)

    @property
    def is_available(self) -> bool:
        """检查Neo4j是否可用"""
        if self._is_available is None:
            self._is_available = self._check_connection()
        return self._is_available

    def _check_connection(self) -> bool:
        """检查Neo4j连接"""
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
            except Exception as e:
                last_error = e
                if driver:
                    driver.close()
                if attempt < 2:
                    time.sleep(1)
        logger.error(f"Neo4j连接失败: {last_error}，知识图谱功能不可用")
        return False

    def _ensure_available(self):
        """确保Neo4j可用，否则抛出异常"""
        if not self.is_available:
            raise Neo4jUnavailableError(
                "Neo4j数据库不可用。请检查Neo4j服务是否启动，以及连接配置是否正确。"
            )

    @staticmethod
    def _build_query(query_text: str) -> "Query":
        """将动态 Cypher 文本封装为 Neo4j Query 对象。"""
        from neo4j import Query

        return Query(query_text)

    def _get_driver(self) -> "Driver":
        """获取Neo4j驱动"""
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

    def get_driver(self) -> "Driver":
        """对外暴露当前可复用的 Neo4j 驱动。

        GraphRAG 运行时需要在已有知识点图之上补充课程文档投影，
        因此这里提供一个受控入口，避免其他模块直接感知连接细节。
        """
        return self._get_driver()

    @staticmethod
    def _resolve_point_course_id(point_id: int) -> Optional[int]:
        """解析知识点所属课程，避免多课程图谱查询串课。"""

        from knowledge.models import KnowledgePoint

        return (
            KnowledgePoint.objects.filter(id=point_id)
            .values_list("course_id", flat=True)
            .first()
        )

    def close(self):
        """关闭Neo4j连接"""
        driver = self._driver
        if driver is not None:
            driver.close()
            self._driver = None

    def sync_knowledge_graph(self, course_id: int) -> Dict[str, int | str]:
        """
        同步课程的知识图谱到Neo4j（使用批量UNWIND操作确保可靠性）

        从PostgreSQL读取知识点和关系，同步到Neo4j图数据库。
        使用事务和UNWIND批量操作替代逐条CREATE以确保原子性和可靠性。

        Args:
            course_id: 课程ID

        Returns:
            同步结果统计 {nodes: x, relations: y}

        Raises:
            Neo4jUnavailableError: Neo4j不可用时抛出
        """
        self._ensure_available()

        from knowledge.models import KnowledgePoint, KnowledgeRelation

        points = list(KnowledgePoint.objects.filter(course_id=course_id))
        relations = list(KnowledgeRelation.objects.filter(course_id=course_id))

        # 准备批量数据
        point_data = [
            {
                "id": point.id,
                "course_id": course_id,
                "name": point.name or "",
                "chapter": point.chapter or "",
                "point_type": point.point_type or "knowledge",
                "level": point.level or 1,
                "description": point.description or "",
                "tags": point.tags or "",
                "cognitive_dimension": point.cognitive_dimension or "",
                "category": point.category or "",
                "teaching_goal": point.teaching_goal or "",
                "is_published": getattr(point, "is_published", True),
                "order": getattr(point, "order", 0) or 0,
            }
            for point in points
        ]

        rel_data = [
            {
                "pre_id": rel.pre_point_id,
                "post_id": rel.post_point_id,
                "rel_type": rel.relation_type or "prerequisite",
            }
            for rel in relations
        ]

        driver = self._get_driver()

        # 使用显式事务确保原子性
        with driver.session() as session:

            def _sync_tx(tx):
                # 1. 清除该课程的旧数据
                tx.run(
                    "MATCH (n:KnowledgePoint {course_id: $course_id}) DETACH DELETE n",
                    course_id=course_id,
                )

                # 2. 批量创建知识点节点（UNWIND）
                if point_data:
                    tx.run(
                        """
                        UNWIND $points AS p
                        CREATE (n:KnowledgePoint {
                            id: p.id,
                            course_id: p.course_id,
                            name: p.name,
                            chapter: p.chapter,
                            point_type: p.point_type,
                            level: p.level,
                            description: p.description,
                            tags: p.tags,
                            cognitive_dimension: p.cognitive_dimension,
                            category: p.category,
                            teaching_goal: p.teaching_goal,
                            is_published: p.is_published,
                            order_index: p.order
                        })
                        """,
                        points=point_data,
                    )

                # 3. 批量创建关系（UNWIND + 动态关系类型）
                _REL_TYPE_MAP = {
                    "prerequisite": "PREREQUISITE",
                    "includes": "INCLUDES",
                    "related": "RELATED",
                }
                for neo4j_rel_type, cypher_rel_type in _REL_TYPE_MAP.items():
                    typed_rels = [
                        r for r in rel_data if r["rel_type"] == neo4j_rel_type
                    ]
                    if typed_rels:
                        tx.run(
                            f"""
                            UNWIND $rels AS r
                            MATCH (a:KnowledgePoint {{id: r.pre_id, course_id: $course_id}})
                            MATCH (b:KnowledgePoint {{id: r.post_id, course_id: $course_id}})
                            CREATE (a)-[:{cypher_rel_type} {{type: r.rel_type}}]->(b)
                            """,
                            rels=typed_rels,
                            course_id=course_id,
                        )

            session.execute_write(_sync_tx)

        node_count = len(point_data)
        rel_count = len(rel_data)
        logger.debug(
            f"课程 {course_id} 知识图谱同步完成: {node_count} 节点, {rel_count} 关系"
        )

        return {"nodes": node_count, "relations": rel_count, "status": "success"}

    def get_prerequisites(self, point_id: int, depth: int = 1) -> List[Dict]:
        """
        获取知识点的前置知识点

        Args:
            point_id: 知识点ID
            depth: 递归深度（默认1层）

        Returns:
            前置知识点列表

        Raises:
            Neo4jUnavailableError: Neo4j不可用时抛出
        """
        self._ensure_available()

        driver = self._get_driver()
        course_id = self._resolve_point_course_id(point_id)

        with driver.session() as session:
            result = session.run(
                self._build_query(
                    f"""
                MATCH (target:KnowledgePoint {{id: $point_id, course_id: $course_id}})
                MATCH path = (pre:KnowledgePoint {{course_id: $course_id}})-[:PREREQUISITE*1..{depth}]->(target)
                RETURN DISTINCT pre.id as id, pre.name as name, 
                       pre.chapter as chapter, length(path) as distance
                ORDER BY distance
                """,
                ),
                point_id=point_id,
                course_id=course_id,
            )

            return [dict(record) for record in result]

    def get_dependents(self, point_id: int, depth: int = 1) -> List[Dict]:
        """
        获取依赖于该知识点的后续知识点

        Args:
            point_id: 知识点ID
            depth: 递归深度

        Returns:
            后续知识点列表

        Raises:
            Neo4jUnavailableError: Neo4j不可用时抛出
        """
        self._ensure_available()

        driver = self._get_driver()
        course_id = self._resolve_point_course_id(point_id)

        with driver.session() as session:
            result = session.run(
                self._build_query(
                    f"""
                MATCH (source:KnowledgePoint {{id: $point_id, course_id: $course_id}})
                MATCH path = (source)-[:PREREQUISITE*1..{depth}]->(dep:KnowledgePoint {{course_id: $course_id}})
                RETURN DISTINCT dep.id as id, dep.name as name,
                       dep.chapter as chapter, length(path) as distance
                ORDER BY distance
                """,
                ),
                point_id=point_id,
                course_id=course_id,
            )

            return [dict(record) for record in result]

    def find_learning_path(
        self,
        start_point_id: int,
        end_point_id: int,
    ) -> Optional[List[Dict]]:
        """
        查找两个知识点之间的学习路径

        Args:
            start_point_id: 起始知识点ID
            end_point_id: 目标知识点ID

        Returns:
            最短学习路径，None表示不存在

        Raises:
            Neo4jUnavailableError: Neo4j不可用时抛出
        """
        self._ensure_available()

        driver = self._get_driver()
        start_course_id = self._resolve_point_course_id(start_point_id)
        end_course_id = self._resolve_point_course_id(end_point_id)
        if (
            start_course_id is None
            or end_course_id is None
            or start_course_id != end_course_id
        ):
            return None

        with driver.session() as session:
            result = session.run(
                """
                MATCH path = shortestPath(
                    (start:KnowledgePoint {id: $start_id, course_id: $course_id})-[:PREREQUISITE*]->(end:KnowledgePoint {id: $end_id, course_id: $course_id})
                )
                RETURN [n in nodes(path) | {id: n.id, name: n.name, chapter: n.chapter}] as path
                """,
                start_id=start_point_id,
                end_id=end_point_id,
                course_id=start_course_id,
            )

            record = result.single()
            if record:
                return record["path"]
            return None

    def get_graph_stats(self, course_id: int) -> Dict[str, Any]:
        """
        获取课程知识图谱的统计信息

        Args:
            course_id: 课程ID

        Returns:
            统计信息

        Raises:
            Neo4jUnavailableError: Neo4j不可用时抛出
        """
        self._ensure_available()

        driver = self._get_driver()

        with driver.session() as session:
            result = session.run(
                """
                MATCH (n:KnowledgePoint {course_id: $course_id})
                OPTIONAL MATCH (n)-[r]->()
                RETURN count(DISTINCT n) as node_count, count(r) as relation_count
                """,
                course_id=course_id,
            )

            record = result.single()
            if record is None:
                # 无记录时提供零值统计，便于调用方统一处理。
                return {
                    "node_count": 0,
                    "relation_count": 0,
                    "source": "neo4j",
                }
            return {
                "node_count": record["node_count"],
                "relation_count": record["relation_count"],
                "source": "neo4j",
            }

    def clear_all(self) -> Dict[str, int]:
        """
        清除Neo4j中的所有数据

        Returns:
            删除的节点和关系数量

        Raises:
            Neo4jUnavailableError: Neo4j不可用时抛出
        """
        self._ensure_available()

        driver = self._get_driver()

        with driver.session() as session:
            result = session.run(
                self._build_query(
                    "MATCH (n) OPTIONAL MATCH (n)-[r]-() "
                    "RETURN count(DISTINCT n) as nodes, count(DISTINCT r) as relations"
                )
            )
            record = result.single()
            stats = {
                "nodes_deleted": int(record["nodes"]) if record is not None else 0,
                "relations_deleted": int(record["relations"]) if record is not None else 0,
            }

            # 删除所有数据
            session.run("MATCH (n) DETACH DELETE n")

        # 写入日志记录
        logger.info(
            f"Neo4j数据已清除: {stats['nodes_deleted']} 节点, {stats['relations_deleted']} 关系"
        )
        return stats

    def import_test_data(self, knowledge_data: Dict) -> Dict[str, int | str]:
        """
        导入测试数据到Neo4j（仅用于测试）

        直接将知识图谱数据导入Neo4j，不经过PostgreSQL。

        Args:
            knowledge_data: 知识图谱数据，格式：
                {
                    'course_id': 1,
                    'course_name': '课程名称',
                    'points': [
                        {'id': 1, 'name': '知识点1', 'chapter': '第一章', 'point_type': 'knowledge'},
                        ...
                    ],
                    'relations': [
                        {'pre_id': 1, 'post_id': 2, 'type': 'prerequisite'},
                        ...
                    ]
                }

        Returns:
            导入统计 {nodes: x, relations: y}

        Raises:
            Neo4jUnavailableError: Neo4j不可用时抛出
        """
        self._ensure_available()

        course_id = knowledge_data.get("course_id", 0)
        course_name = knowledge_data.get("course_name", "")
        points = knowledge_data.get("points", [])
        relations = knowledge_data.get("relations", [])

        driver = self._get_driver()

        with driver.session() as session:
            # 清除该课程的旧数据
            session.run(
                "MATCH (n:KnowledgePoint {course_id: $course_id}) DETACH DELETE n",
                course_id=course_id,
            )

            # 创建课程节点（可选）
            session.run(
                """
                MERGE (c:Course {id: $course_id})
                SET c.name = $course_name
                """,
                course_id=course_id,
                course_name=course_name,
            )

            # 创建知识点节点
            for point in points:
                session.run(
                    """
                    CREATE (n:KnowledgePoint {
                        id: $id,
                        course_id: $course_id,
                        name: $name,
                        chapter: $chapter,
                        point_type: $point_type,
                        level: $level,
                        description: $description
                    })
                    """,
                    id=point.get("id", 0),
                    course_id=course_id,
                    name=point.get("name", ""),
                    chapter=point.get("chapter", ""),
                    point_type=point.get("point_type", "knowledge"),
                    level=point.get("level", 1),
                    description=point.get("description", ""),
                )

            # 创建关系
            for rel in relations:
                session.run(
                    """
                    MATCH (a:KnowledgePoint {id: $pre_id, course_id: $course_id})
                    MATCH (b:KnowledgePoint {id: $post_id, course_id: $course_id})
                    CREATE (a)-[r:PREREQUISITE {type: $rel_type}]->(b)
                    """,
                    pre_id=rel.get("pre_id"),
                    post_id=rel.get("post_id"),
                    course_id=course_id,
                    rel_type=rel.get("type", "prerequisite"),
                )

        logger.info(
            f"Neo4j测试数据导入完成: 课程 {course_id}, {len(points)} 节点, {len(relations)} 关系"
        )

        return {
            "course_id": course_id,
            "nodes": len(points),
            "relations": len(relations),
            "status": "success",
        }

    def get_all_courses(self) -> List[Dict]:
        """
        获取Neo4j中所有课程的知识图谱统计

        Returns:
            课程列表及其知识图谱统计
        """
        self._ensure_available()

        driver = self._get_driver()

        with driver.session() as session:
            result = session.run(
                """
                MATCH (n:KnowledgePoint)
                WITH n.course_id as course_id, count(n) as node_count
                OPTIONAL MATCH (n2:KnowledgePoint {course_id: course_id})-[r:PREREQUISITE]->()
                RETURN course_id, node_count, count(r) as relation_count
                ORDER BY course_id
                """
            )

            return [dict(record) for record in result]

    # ========== 知识图谱查询（Neo4j优先，PostgreSQL降级） ==========

    def get_knowledge_map(
        self, course_id: int, published_only: bool = True
    ) -> Optional[Dict]:
        """
        从Neo4j获取课程的知识图谱

        Args:
            course_id: 课程ID
            published_only: 是否只返回已发布的知识点

        Returns:
            {'nodes': [...], 'edges': [...]} 或 None（Neo4j不可用时）
        """
        if not self.is_available:
            self._warn_fallback("get_knowledge_map")
            return None

        try:
            driver = self._get_driver()
            with driver.session() as session:
                # 查询节点
                published_filter = (
                    " AND n.is_published = true" if published_only else ""
                )
                result = session.run(
                    self._build_query(
                        f"""
                    MATCH (n:KnowledgePoint {{course_id: $course_id}})
                    WHERE true{published_filter}
                    RETURN n.id as point_id, n.name as point_name,
                           n.chapter as chapter, n.point_type as type,
                           n.level as level, n.description as description,
                           n.tags as tags, n.cognitive_dimension as cognitive_dimension,
                           n.category as category, n.teaching_goal as teaching_goal,
                           n.is_published as is_published, n.order_index as order_index
                    ORDER BY n.order_index
                    """,
                    ),
                    course_id=course_id,
                )
                nodes = [dict(record) for record in result]

                # 查询边
                result = session.run(
                    """
                    MATCH (a:KnowledgePoint {course_id: $course_id})-[r]->(b:KnowledgePoint {course_id: $course_id})
                    RETURN a.id as source, b.id as target, r.type as relation_type, type(r) as neo4j_type
                    """,
                    course_id=course_id,
                )
                edges = [dict(record) for record in result]

            logger.debug(
                f"Neo4j知识图谱查询: course={course_id}, nodes={len(nodes)}, edges={len(edges)}"
            )
            return {"nodes": nodes, "edges": edges, "source": "neo4j"}
        except Exception as e:
            logger.error(f"Neo4j知识图谱查询失败: {e}")
            self._warn_fallback("get_knowledge_map")
            return None

    def get_knowledge_point_neo4j(self, point_id: int) -> Optional[Dict]:
        """
        从Neo4j获取知识点详情及其关系

        Args:
            point_id: 知识点ID

        Returns:
            知识点信息及关系，或 None
        """
        if not self.is_available:
            self._warn_fallback("get_knowledge_point")
            return None

        try:
            driver = self._get_driver()
            course_id = self._resolve_point_course_id(point_id)
            with driver.session() as session:
                result = session.run(
                    """
                    MATCH (n:KnowledgePoint {id: $point_id, course_id: $course_id})
                    RETURN n.id as point_id, n.name as point_name, n.course_id as course_id,
                           n.chapter as chapter, n.point_type as type,
                           n.level as level, n.description as description,
                           n.tags as tags, n.cognitive_dimension as cognitive_dimension,
                           n.category as category, n.teaching_goal as teaching_goal
                    """,
                    point_id=point_id,
                    course_id=course_id,
                )
                record = result.single()
                if not record:
                    return None

                point_data = dict(record)

                result = session.run(
                    """
                    MATCH (pre:KnowledgePoint {course_id: $course_id})-[:PREREQUISITE]->(n:KnowledgePoint {id: $point_id, course_id: $course_id})
                    RETURN pre.id as point_id, pre.name as point_name
                    """,
                    point_id=point_id,
                    course_id=course_id,
                )
                point_data["prerequisites"] = [dict(r) for r in result]

                result = session.run(
                    """
                    MATCH (n:KnowledgePoint {id: $point_id, course_id: $course_id})-[:PREREQUISITE]->(post:KnowledgePoint {course_id: $course_id})
                    RETURN post.id as point_id, post.name as point_name
                    """,
                    point_id=point_id,
                    course_id=course_id,
                )
                point_data["postrequisites"] = [dict(r) for r in result]

                point_data["source"] = "neo4j"
                return point_data
        except Exception as e:
            logger.error(f"Neo4j知识点查询失败: {e}")
            self._warn_fallback("get_knowledge_point")
            return None

    def get_knowledge_points_neo4j(self, course_id: int) -> Optional[List[Dict]]:
        """
        从Neo4j获取课程的所有知识点列表

        Args:
            course_id: 课程ID

        Returns:
            知识点列表，或 None（Neo4j不可用时）
        """
        if not self.is_available:
            self._warn_fallback("get_knowledge_points")
            return None

        try:
            driver = self._get_driver()
            with driver.session() as session:
                result = session.run(
                    """
                    MATCH (n:KnowledgePoint {course_id: $course_id})
                    RETURN n.id as id, n.name as name, n.chapter as chapter,
                           n.point_type as type, n.description as description,
                           n.is_published as is_published, n.order_index as order_index,
                           n.level as level
                    ORDER BY n.order_index
                    """,
                    course_id=course_id,
                )
                points = [dict(record) for record in result]

            logger.debug(
                f"Neo4j知识点列表查询: course={course_id}, count={len(points)}"
            )
            return points
        except Exception as e:
            logger.error(f"Neo4j知识点列表查询失败: {e}")
            self._warn_fallback("get_knowledge_points")
            return None

    def get_knowledge_relations_neo4j(self, course_id: int) -> Optional[List[Dict]]:
        """
        从Neo4j获取课程的所有知识点关系

        Args:
            course_id: 课程ID

        Returns:
            关系列表，或 None（Neo4j不可用时）
        """
        if not self.is_available:
            self._warn_fallback("get_knowledge_relations")
            return None

        try:
            driver = self._get_driver()
            with driver.session() as session:
                result = session.run(
                    """
                    MATCH (a:KnowledgePoint {course_id: $course_id})-[r]->(b:KnowledgePoint {course_id: $course_id})
                    RETURN id(r) as relation_id, a.id as pre_point_id, a.name as pre_point_name,
                           b.id as post_point_id, b.name as post_point_name,
                           r.type as relation_type
                    """,
                    course_id=course_id,
                )
                relations = [dict(record) for record in result]

            logger.debug(
                f"Neo4j关系列表查询: course={course_id}, count={len(relations)}"
            )
            return relations
        except Exception as e:
            logger.error(f"Neo4j关系列表查询失败: {e}")
            self._warn_fallback("get_knowledge_relations")
            return None

    # ========== CRUD同步到Neo4j ==========

    def sync_single_point(self, point) -> bool:
        """
        同步单个知识点到Neo4j（创建或更新）

        Args:
            point: KnowledgePoint实例

        Returns:
            是否成功
        """
        if not self.is_available:
            self._warn_fallback("sync_single_point")
            return False

        try:
            driver = self._get_driver()
            with driver.session() as session:
                session.run(
                    """
                    MERGE (n:KnowledgePoint {id: $id, course_id: $course_id})
                    SET n.name = $name,
                        n.chapter = $chapter,
                        n.point_type = $point_type,
                        n.level = $level,
                        n.description = $description,
                        n.tags = $tags,
                        n.cognitive_dimension = $cognitive_dimension,
                        n.category = $category,
                        n.teaching_goal = $teaching_goal,
                        n.is_published = $is_published,
                        n.order_index = $order_index
                    """,
                    id=point.id,
                    course_id=point.course_id,
                    name=point.name or "",
                    chapter=point.chapter or "",
                    point_type=point.point_type or "knowledge",
                    level=point.level or 1,
                    description=point.description or "",
                    tags=point.tags or "",
                    cognitive_dimension=point.cognitive_dimension or "",
                    category=point.category or "",
                    teaching_goal=point.teaching_goal or "",
                    is_published=getattr(point, "is_published", True),
                    order_index=getattr(point, "order", 0) or 0,
                )
            logger.debug(f"Neo4j同步知识点: id={point.id}, name={point.name}")
            return True
        except Exception as e:
            logger.error(f"Neo4j同步知识点失败: {e}")
            return False

    def delete_point_neo4j(self, point_id: int) -> bool:
        """
        从Neo4j删除知识点及其关系

        Args:
            point_id: 知识点ID

        Returns:
            是否成功
        """
        if not self.is_available:
            self._warn_fallback("delete_point")
            return False

        try:
            driver = self._get_driver()
            with driver.session() as session:
                session.run(
                    "MATCH (n:KnowledgePoint {id: $point_id}) DETACH DELETE n",
                    point_id=point_id,
                )
            logger.debug(f"Neo4j删除知识点: id={point_id}")
            return True
        except Exception as e:
            logger.error(f"Neo4j删除知识点失败: {e}")
            return False

    def sync_single_relation(self, relation) -> bool:
        """
        同步单个知识关系到Neo4j

        Args:
            relation: KnowledgeRelation实例

        Returns:
            是否成功
        """
        if not self.is_available:
            self._warn_fallback("sync_single_relation")
            return False

        try:
            _REL_TYPE_MAP = {
                "prerequisite": "PREREQUISITE",
                "includes": "INCLUDES",
                "related": "RELATED",
            }
            neo4j_rel = _REL_TYPE_MAP.get(relation.relation_type, "PREREQUISITE")

            driver = self._get_driver()
            with driver.session() as session:
                session.run(
                    self._build_query(
                        f"""
                    MATCH (a:KnowledgePoint {{id: $pre_id}})
                    MATCH (b:KnowledgePoint {{id: $post_id}})
                    CREATE (a)-[:{neo4j_rel} {{type: $rel_type}}]->(b)
                    """,
                    ),
                    pre_id=relation.pre_point_id,
                    post_id=relation.post_point_id,
                    rel_type=relation.relation_type,
                )
            logger.debug(
                f"Neo4j同步关系: {relation.pre_point_id} -> {relation.post_point_id}"
            )
            return True
        except Exception as e:
            logger.error(f"Neo4j同步关系失败: {e}")
            return False

    def delete_relation_neo4j(self, pre_point_id: int, post_point_id: int) -> bool:
        """
        从Neo4j删除知识关系

        Args:
            pre_point_id: 前置知识点ID
            post_point_id: 后续知识点ID

        Returns:
            是否成功
        """
        if not self.is_available:
            self._warn_fallback("delete_relation")
            return False

        try:
            driver = self._get_driver()
            with driver.session() as session:
                session.run(
                    """
                    MATCH (a:KnowledgePoint {id: $pre_id})-[r]->(b:KnowledgePoint {id: $post_id})
                    DELETE r
                    """,
                    pre_id=pre_point_id,
                    post_id=post_point_id,
                )
            logger.debug(f"Neo4j删除关系: {pre_point_id} -> {post_point_id}")
            return True
        except Exception as e:
            logger.error(f"Neo4j删除关系失败: {e}")
            return False

    def clear_course_graph(self, course_id: int) -> bool:
        """
        清除指定课程的Neo4j图数据与 GraphRAG 文档投影

        Args:
            course_id: 课程ID

        Returns:
            是否成功
        """
        if not self.is_available:
            self._warn_fallback("clear_course_graph")
            return False

        try:
            driver = self._get_driver()
            with driver.session() as session:
                session.run(
                    "MATCH (d:CourseDocument {course_id: $course_id}) DETACH DELETE d",
                    course_id=course_id,
                )
                session.run(
                    "MATCH (n:KnowledgePoint {course_id: $course_id}) DETACH DELETE n",
                    course_id=course_id,
                )
                session.run(
                    "MATCH (c:Course {id: $course_id}) DETACH DELETE c",
                    course_id=course_id,
                )
            logger.debug(f"Neo4j清除课程 {course_id} 图数据与文档投影")
            return True
        except Exception as e:
            logger.error(f"Neo4j清除课程图数据失败: {e}")
            return False

    def has_course_graphrag_projection(self, course_id: int) -> bool:
        """检查课程级 GraphRAG 文档投影是否已存在。"""
        if not self.is_available:
            return False

        try:
            driver = self._get_driver()
            with driver.session() as session:
                result = session.run(
                    """
                    MATCH (d:CourseDocument {course_id: $course_id})
                    RETURN count(d) as document_count
                    """,
                    course_id=course_id,
                )
                record = result.single()
                return bool(record and record["document_count"] > 0)
        except Exception as e:
            logger.error(f"Neo4j检查 GraphRAG 投影失败: {e}")
            return False

    def sync_course_graphrag_projection(
        self,
        course_id: int,
        documents: List[Dict[str, object]],
        about_links: List[Dict[str, object]],
    ) -> Dict[str, object]:
        """同步课程级 GraphRAG 文档投影。

        这里不会改写既有 `KnowledgePoint` 主图，只新增 `CourseDocument`
        节点以及它们到知识点的 `ABOUT` 关系，从而把向量检索命中
        回接到真实课程图谱。
        """
        if not self.is_available:
            self._warn_fallback("sync_course_graphrag_projection")
            return {
                "documents": 0,
                "relations": 0,
                "status": "fallback",
            }

        driver = self._get_driver()

        with driver.session() as session:

            def _sync_projection_tx(tx):
                # 先清理课程旧投影，保证重建后的文档视图一致。
                tx.run(
                    """
                    MATCH (d:CourseDocument {course_id: $course_id})
                    DETACH DELETE d
                    """,
                    course_id=course_id,
                )

                if documents:
                    tx.run(
                        """
                        UNWIND $documents AS doc
                        MERGE (d:CourseDocument {course_id: $course_id, external_id: doc.external_id})
                        SET d.doc_id = doc.doc_id,
                            d.title = doc.title,
                            d.kind = doc.kind,
                            d.content = doc.content,
                            d.url = doc.url,
                            d.chapter = doc.chapter,
                            d.point_ids = doc.point_ids,
                            d.excerpt = doc.excerpt
                        """,
                        course_id=course_id,
                        documents=documents,
                    )

                if about_links:
                    tx.run(
                        """
                        UNWIND $links AS link
                        MATCH (d:CourseDocument {course_id: $course_id, external_id: link.external_id})
                        MATCH (p:KnowledgePoint {course_id: $course_id, id: link.point_id})
                        MERGE (d)-[:ABOUT {course_id: $course_id}]->(p)
                        """,
                        course_id=course_id,
                        links=about_links,
                    )

            session.execute_write(_sync_projection_tx)

        return {
            "documents": len(documents),
            "relations": len(about_links),
            "status": "success",
        }


# 创建默认实例
neo4j_service = Neo4jService()
