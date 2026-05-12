"""Neo4j 知识图谱查询方法。"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Neo4jQueryMixin:
    """知识图谱遍历、详情和列表查询能力。"""

    def get_prerequisites(self, point_id: int, depth: int = 1) -> List[Dict]:
        """获取知识点的前置知识点。"""
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
                """
                ),
                point_id=point_id,
                course_id=course_id,
            )
            return [dict(record) for record in result]

    def get_dependents(self, point_id: int, depth: int = 1) -> List[Dict]:
        """获取依赖于该知识点的后续知识点。"""
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
                """
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
        """查找两个知识点之间的最短学习路径。"""
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
        """获取课程知识图谱的统计信息。"""
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
                return {"node_count": 0, "relation_count": 0, "source": "neo4j"}
            return {
                "node_count": record["node_count"],
                "relation_count": record["relation_count"],
                "source": "neo4j",
            }

    def get_knowledge_map(
        self, course_id: int, published_only: bool = True
    ) -> Optional[Dict]:
        """从 Neo4j 获取课程的知识图谱。"""
        if not self.is_available:
            self._warn_fallback("get_knowledge_map")
            return None

        try:
            driver = self._get_driver()
            with driver.session() as session:
                published_filter = " AND n.is_published = true" if published_only else ""
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
                    """
                    ),
                    course_id=course_id,
                )
                nodes = [dict(record) for record in result]
                result = session.run(
                    """
                    MATCH (a:KnowledgePoint {course_id: $course_id})-[r]->(b:KnowledgePoint {course_id: $course_id})
                    RETURN a.id as source, b.id as target, r.type as relation_type, type(r) as neo4j_type
                    """,
                    course_id=course_id,
                )
                edges = [dict(record) for record in result]

            logger.debug(
                "Neo4j知识图谱查询: course=%s, nodes=%s, edges=%s",
                course_id,
                len(nodes),
                len(edges),
            )
            return {"nodes": nodes, "edges": edges, "source": "neo4j"}
        except Exception as error:
            logger.error("Neo4j知识图谱查询失败: %s", error)
            self._warn_fallback("get_knowledge_map")
            return None

    def get_knowledge_point_neo4j(self, point_id: int) -> Optional[Dict]:
        """从 Neo4j 获取知识点详情及其关系。"""
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
                point_data["prerequisites"] = [dict(record) for record in result]
                result = session.run(
                    """
                    MATCH (n:KnowledgePoint {id: $point_id, course_id: $course_id})-[:PREREQUISITE]->(post:KnowledgePoint {course_id: $course_id})
                    RETURN post.id as point_id, post.name as point_name
                    """,
                    point_id=point_id,
                    course_id=course_id,
                )
                point_data["postrequisites"] = [dict(record) for record in result]
                point_data["source"] = "neo4j"
                return point_data
        except Exception as error:
            logger.error("Neo4j知识点查询失败: %s", error)
            self._warn_fallback("get_knowledge_point")
            return None

    def get_knowledge_points_neo4j(self, course_id: int) -> Optional[List[Dict]]:
        """从 Neo4j 获取课程的所有知识点列表。"""
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
            logger.debug("Neo4j知识点列表查询: course=%s, count=%s", course_id, len(points))
            return points
        except Exception as error:
            logger.error("Neo4j知识点列表查询失败: %s", error)
            self._warn_fallback("get_knowledge_points")
            return None

    def get_knowledge_relations_neo4j(self, course_id: int) -> Optional[List[Dict]]:
        """从 Neo4j 获取课程的所有知识点关系。"""
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
            logger.debug("Neo4j关系列表查询: course=%s, count=%s", course_id, len(relations))
            return relations
        except Exception as error:
            logger.error("Neo4j关系列表查询失败: %s", error)
            self._warn_fallback("get_knowledge_relations")
            return None
