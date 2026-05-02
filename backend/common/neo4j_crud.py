"""Neo4j 单点 CRUD 同步与 GraphRAG 投影。"""

from __future__ import annotations

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class Neo4jCrudMixin:
    """知识点、关系与课程文档投影的增删同步能力。"""

    def sync_single_point(self, point) -> bool:
        """同步单个知识点到 Neo4j。"""
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
            logger.debug("Neo4j同步知识点: id=%s, name=%s", point.id, point.name)
            return True
        except Exception as error:
            logger.error("Neo4j同步知识点失败: %s", error)
            return False

    def delete_point_neo4j(self, point_id: int) -> bool:
        """从 Neo4j 删除知识点及其关系。"""
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
            logger.debug("Neo4j删除知识点: id=%s", point_id)
            return True
        except Exception as error:
            logger.error("Neo4j删除知识点失败: %s", error)
            return False

    def sync_single_relation(self, relation) -> bool:
        """同步单个知识关系到 Neo4j。"""
        if not self.is_available:
            self._warn_fallback("sync_single_relation")
            return False

        try:
            rel_type_map = {
                "prerequisite": "PREREQUISITE",
                "includes": "INCLUDES",
                "related": "RELATED",
            }
            neo4j_rel = rel_type_map.get(relation.relation_type, "PREREQUISITE")
            driver = self._get_driver()
            with driver.session() as session:
                session.run(
                    self._build_query(
                        f"""
                    MATCH (a:KnowledgePoint {{id: $pre_id}})
                    MATCH (b:KnowledgePoint {{id: $post_id}})
                    CREATE (a)-[:{neo4j_rel} {{type: $rel_type}}]->(b)
                    """
                    ),
                    pre_id=relation.pre_point_id,
                    post_id=relation.post_point_id,
                    rel_type=relation.relation_type,
                )
            logger.debug("Neo4j同步关系: %s -> %s", relation.pre_point_id, relation.post_point_id)
            return True
        except Exception as error:
            logger.error("Neo4j同步关系失败: %s", error)
            return False

    def delete_relation_neo4j(self, pre_point_id: int, post_point_id: int) -> bool:
        """从 Neo4j 删除知识关系。"""
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
            logger.debug("Neo4j删除关系: %s -> %s", pre_point_id, post_point_id)
            return True
        except Exception as error:
            logger.error("Neo4j删除关系失败: %s", error)
            return False

    def clear_course_graph(self, course_id: int) -> bool:
        """清除指定课程的 Neo4j 图数据与 GraphRAG 文档投影。"""
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
            logger.debug("Neo4j清除课程 %s 图数据与文档投影", course_id)
            return True
        except Exception as error:
            logger.error("Neo4j清除课程图数据失败: %s", error)
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
        except Exception as error:
            logger.error("Neo4j检查 GraphRAG 投影失败: %s", error)
            return False

    def sync_course_graphrag_projection(
        self,
        course_id: int,
        documents: List[Dict[str, object]],
        about_links: List[Dict[str, object]],
    ) -> Dict[str, object]:
        """同步课程级 GraphRAG 文档投影。"""
        if not self.is_available:
            self._warn_fallback("sync_course_graphrag_projection")
            return {"documents": 0, "relations": 0, "status": "fallback"}

        driver = self._get_driver()
        with driver.session() as session:

            def _sync_projection_tx(tx):
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
