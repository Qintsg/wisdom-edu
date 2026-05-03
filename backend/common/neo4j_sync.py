"""Neo4j 课程图谱同步与测试数据导入。"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


# 维护意图：课程图谱批量同步、清理、导入和统计能力
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class Neo4jSyncMixin:
    """课程图谱批量同步、清理、导入和统计能力。"""

    # 维护意图：同步课程的知识图谱到 Neo4j
    # 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
    # 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
    def sync_knowledge_graph(self, course_id: int) -> Dict[str, int | str]:
        """同步课程的知识图谱到 Neo4j。"""
        self._ensure_available()

        from knowledge.models import KnowledgePoint, KnowledgeRelation

        points = list(KnowledgePoint.objects.filter(course_id=course_id))
        relations = list(KnowledgeRelation.objects.filter(course_id=course_id))
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

        with driver.session() as session:

            # 维护意图：sync tx
            # 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
            # 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
            def _sync_tx(tx):
                tx.run(
                    "MATCH (n:KnowledgePoint {course_id: $course_id}) DETACH DELETE n",
                    course_id=course_id,
                )
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
                rel_type_map = {
                    "prerequisite": "PREREQUISITE",
                    "includes": "INCLUDES",
                    "related": "RELATED",
                }
                for neo4j_rel_type, cypher_rel_type in rel_type_map.items():
                    typed_rels = [
                        rel for rel in rel_data if rel["rel_type"] == neo4j_rel_type
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
            "课程 %s 知识图谱同步完成: %s 节点, %s 关系",
            course_id,
            node_count,
            rel_count,
        )
        return {"nodes": node_count, "relations": rel_count, "status": "success"}

    # 维护意图：清除 Neo4j 中的所有数据
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def clear_all(self) -> Dict[str, int]:
        """清除 Neo4j 中的所有数据。"""
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
            session.run("MATCH (n) DETACH DELETE n")

        logger.info(
            "Neo4j数据已清除: %s 节点, %s 关系",
            stats["nodes_deleted"],
            stats["relations_deleted"],
        )
        return stats

    # 维护意图：导入测试数据到 Neo4j
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def import_test_data(self, knowledge_data: Dict) -> Dict[str, int | str]:
        """导入测试数据到 Neo4j。"""
        self._ensure_available()
        course_id = knowledge_data.get("course_id", 0)
        course_name = knowledge_data.get("course_name", "")
        points = knowledge_data.get("points", [])
        relations = knowledge_data.get("relations", [])
        driver = self._get_driver()

        with driver.session() as session:
            session.run(
                "MATCH (n:KnowledgePoint {course_id: $course_id}) DETACH DELETE n",
                course_id=course_id,
            )
            session.run(
                """
                MERGE (c:Course {id: $course_id})
                SET c.name = $course_name
                """,
                course_id=course_id,
                course_name=course_name,
            )
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
            "Neo4j测试数据导入完成: 课程 %s, %s 节点, %s 关系",
            course_id,
            len(points),
            len(relations),
        )
        return {
            "course_id": course_id,
            "nodes": len(points),
            "relations": len(relations),
            "status": "success",
        }

    # 维护意图：获取 Neo4j 中所有课程的知识图谱统计
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_all_courses(self) -> List[Dict]:
        """获取 Neo4j 中所有课程的知识图谱统计。"""
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
