from __future__ import annotations

from typing import cast
import logging

from neo4j import Driver
from neo4j_graphrag.retrievers import Text2CypherRetriever, ToolsRetriever
from neo4j_graphrag.tool import Tool
from neo4j_graphrag.types import RetrieverResult, RetrieverResultItem

from platform_ai.rag.runtime_models import (
    COURSE_RETRIEVAL_MODE,
    _coerce_int,
    _coerce_string,
    _escape_cypher_string,
    _query_tool_parameters,
)
from platform_ai.rag.runtime_graph_query_support import (
    build_empty_query_context,
    build_graph_record_item,
    build_semantic_only_query_context,
    build_tool_line,
    build_tool_source,
    build_tools_query_context,
)
from platform_ai.rag.runtime_proxies import FacadeGraphRAGLLM, neo4j_service

logger = logging.getLogger(__name__)


# 维护意图：ToolsRetriever 与 Text2Cypher 图查询能力
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class CourseGraphRAGQueryMixin:
    """ToolsRetriever 与 Text2Cypher 图查询能力。"""

    # 维护意图：定义面向课程知识图谱的受控 Neo4j schema 文本
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _graph_query_schema(self) -> str:
        """定义面向课程知识图谱的受控 Neo4j schema 文本。"""
        return """
Node properties:
KnowledgePoint {id: INTEGER, course_id: INTEGER, name: STRING, chapter: STRING, description: STRING, is_published: BOOLEAN}
CourseDocument {external_id: STRING, doc_id: STRING, course_id: INTEGER, title: STRING, kind: STRING, content: STRING, url: STRING, chapter: STRING, excerpt: STRING}

Relationship properties:
PREREQUISITE {type: STRING}
ABOUT {course_id: INTEGER}

The relationships:
(:KnowledgePoint)-[:PREREQUISITE]->(:KnowledgePoint)
(:CourseDocument)-[:ABOUT]->(:KnowledgePoint)
"""

    # 维护意图：为 Text2Cypher 生成贴合课程图谱的 few-shot 样例
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _graph_query_examples(
        self,
        *,
        course_id: int,
        focus_point_id: int | None,
        focus_point_name: str,
    ) -> list[str]:
        """为 Text2Cypher 生成贴合课程图谱的 few-shot 样例。"""
        resolved_point_id = focus_point_id or 0
        resolved_point_name = focus_point_name or "当前知识点"
        escaped_point_name = _escape_cypher_string(resolved_point_name)
        return [
            (
                "USER INPUT: '这个知识点的前置知识是什么？' QUERY: "
                f"MATCH (target:KnowledgePoint {{course_id: {course_id}}}) "
                f"WHERE target.id = {resolved_point_id} OR toLower(target.name) CONTAINS toLower('{escaped_point_name}') "
                f"OPTIONAL MATCH (pre:KnowledgePoint {{course_id: {course_id}}})-[:PREREQUISITE]->(target) "
                f"OPTIONAL MATCH (doc:CourseDocument {{course_id: {course_id}}})-[:ABOUT]->(target) "
                "RETURN 'prerequisite' AS item_type, target.id AS point_id, target.name AS point_name, 'PREREQUISITE' AS relation_type, "
                "pre.id AS related_point_id, COALESCE(pre.name, '') AS related_point_name, COALESCE(doc.title, '') AS source_title, "
                "COALESCE(doc.excerpt, '') AS source_excerpt, '说明该知识点的前置知识。' AS reasoning LIMIT 8"
            ),
            (
                "USER INPUT: '学完这个知识点之后可以继续学什么？' QUERY: "
                f"MATCH (target:KnowledgePoint {{course_id: {course_id}}}) "
                f"WHERE target.id = {resolved_point_id} OR toLower(target.name) CONTAINS toLower('{escaped_point_name}') "
                f"OPTIONAL MATCH (target)-[:PREREQUISITE]->(post:KnowledgePoint {{course_id: {course_id}}}) "
                f"OPTIONAL MATCH (doc:CourseDocument {{course_id: {course_id}}})-[:ABOUT]->(target) "
                "RETURN 'postrequisite' AS item_type, target.id AS point_id, target.name AS point_name, 'PREREQUISITE' AS relation_type, "
                "post.id AS related_point_id, COALESCE(post.name, '') AS related_point_name, COALESCE(doc.title, '') AS source_title, "
                "COALESCE(doc.excerpt, '') AS source_excerpt, '说明该知识点的后续知识。' AS reasoning LIMIT 8"
            ),
            (
                "USER INPUT: '这个知识点有哪些课程资源或证据？' QUERY: "
                f"MATCH (target:KnowledgePoint {{course_id: {course_id}}}) "
                f"WHERE target.id = {resolved_point_id} OR toLower(target.name) CONTAINS toLower('{escaped_point_name}') "
                f"OPTIONAL MATCH (doc:CourseDocument {{course_id: {course_id}}})-[:ABOUT]->(target) "
                "RETURN 'resource' AS item_type, target.id AS point_id, target.name AS point_name, 'ABOUT' AS relation_type, "
                "target.id AS related_point_id, target.name AS related_point_name, COALESCE(doc.title, '') AS source_title, "
                "COALESCE(doc.excerpt, '') AS source_excerpt, '展示该知识点的课程证据。' AS reasoning LIMIT 8"
            ),
        ]

    # 维护意图：自定义 Text2Cypher prompt，强制课程内查询和固定返回列
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _text2cypher_prompt(self) -> str:
        """自定义 Text2Cypher prompt，强制课程内查询和固定返回列。"""
        return """
Task: Generate a Cypher statement for querying the course knowledge graph.

course_id: {course_id}
focus_point_id: {focus_point_id}
focus_point_name: {focus_point_name}

Schema:
{schema}

Examples (optional):
{examples}

User question:
{query_text}

Rules:
1. You MUST restrict every KnowledgePoint and CourseDocument node to course_id = {course_id}.
2. Prefer the focus point when focus_point_id is provided.
3. Only use labels KnowledgePoint and CourseDocument.
4. Only use relationships PREREQUISITE and ABOUT.
5. The query must return these columns exactly: item_type, point_id, point_name, relation_type, related_point_id, related_point_name, source_title, source_excerpt, reasoning.
6. Use COALESCE for nullable string fields and keep the result limit within 8 rows.
7. Do not use properties or relationships not included in the schema.
8. Return only the Cypher statement without Markdown fences or explanations.

Cypher query:
"""

    # 维护意图：把结构化 Cypher 结果转换为统一的检索条目
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _graph_record_formatter(self, record: object) -> RetrieverResultItem:
        """把结构化 Cypher 结果转换为统一的检索条目。"""
        return build_graph_record_item(record)

    # 维护意图：将现有混合检索包装成可供 ToolsRetriever 调用的 Tool 结果
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _semantic_tool_result(
        self,
        *,
        course_id: int,
        query_text: str,
        seed_point_ids: list[int],
        limit: int,
    ) -> RetrieverResult:
        """将现有混合检索包装成可供 ToolsRetriever 调用的 Tool 结果。"""
        hits = self.search_documents(
            course_id=course_id,
            query=query_text,
            limit=limit,
            seed_point_ids=seed_point_ids,
        )
        items = [
            RetrieverResultItem(
                content=hit.excerpt or hit.title,
                metadata={
                    "external_id": hit.external_id,
                    "doc_id": hit.doc_id,
                    "title": hit.title,
                    "kind": hit.kind,
                    "url": hit.url,
                    "excerpt": hit.excerpt,
                    "score": hit.score,
                    "point_ids": hit.point_ids,
                    "matched_points": hit.matched_points,
                    "prerequisites": hit.prerequisites,
                    "postrequisites": hit.postrequisites,
                    "retrieval_source": hit.source_label,
                },
            )
            for hit in hits
        ]
        return RetrieverResult(
            items=items,
            metadata={"retrieval_mode": COURSE_RETRIEVAL_MODE},
        )

    # 维护意图：执行官方 Text2CypherRetriever，并把生成的 Cypher 注入 item metadata
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _text2cypher_tool_result(
        self,
        *,
        course_id: int,
        query_text: str,
        focus_point_id: int | None,
        focus_point_name: str,
    ) -> RetrieverResult:
        """执行官方 Text2CypherRetriever，并把生成的 Cypher 注入 item metadata。"""
        graph_driver = neo4j_service.get_driver()
        if graph_driver is None:
            return RetrieverResult(items=[], metadata={"retrieval_mode": GRAPH_QUERY_RETRIEVAL_MODE})
        retriever = Text2CypherRetriever(
            driver=graph_driver,
            llm=FacadeGraphRAGLLM(),
            neo4j_schema=self._graph_query_schema(),
            examples=self._graph_query_examples(
                course_id=course_id,
                focus_point_id=focus_point_id,
                focus_point_name=focus_point_name,
            ),
            result_formatter=self._graph_record_formatter,
            custom_prompt=self._text2cypher_prompt(),
        )
        search_result = retriever.search(
            query_text=query_text,
            prompt_params={
                "course_id": course_id,
                "focus_point_id": focus_point_id or 0,
                "focus_point_name": focus_point_name,
                "examples": "\n".join(
                    self._graph_query_examples(
                        course_id=course_id,
                        focus_point_id=focus_point_id,
                        focus_point_name=focus_point_name,
                    )
                ),
            },
        )
        generated_cypher = _coerce_string(search_result.metadata.get("cypher") if search_result.metadata else "")
        enriched_items = [
            RetrieverResultItem(
                content=item.content,
                metadata={
                    **(item.metadata or {}),
                    "generated_cypher": generated_cypher,
                },
            )
            for item in search_result.items
        ]
        return RetrieverResult(
            items=enriched_items,
            metadata={
                "generated_cypher": generated_cypher,
                "retrieval_mode": GRAPH_QUERY_RETRIEVAL_MODE,
            },
        )

    # 维护意图：定义 ToolsRetriever 的系统路由指令
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _graph_tools_system_instruction(self) -> str:
        """定义 ToolsRetriever 的系统路由指令。"""
        return (
            "你负责为课程 GraphRAG 选择检索工具。"
            "涉及前置知识、后续知识、依赖关系、学习顺序、图谱链路的问题优先选择 graph_structure_query。"
            "涉及概念解释、资源、证据补充、例题、学习建议的问题优先选择 semantic_course_search。"
            "如果问题同时包含结构关系与解释需求，可以同时选择两个工具。"
        )

    # 维护意图：把工具检索条目转换为简洁的上下文短句
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _tool_line(self, item: RetrieverResultItem) -> str:
        """把工具检索条目转换为简洁的上下文短句。"""
        return build_tool_line(item)

    # 维护意图：将 ToolsRetriever item 收敛为统一证据结构
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _tool_source(self, item: RetrieverResultItem) -> dict[str, object]:
        """将 ToolsRetriever item 收敛为统一证据结构。"""
        return build_tool_source(item)

    # 维护意图：构造图查询所需工具集合，并尽量获取可用图驱动
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    def _build_available_tools(
        self,
        *,
        course_id: int,
        normalized_query: str,
        seed_point_ids: list[int],
        focus_point_id: int | None,
        focus_point_name: str,
        limit: int,
    ) -> tuple[list[Tool], Driver | None]:
        """构造图查询所需工具集合，并尽量获取可用图驱动。"""
        semantic_tool = Tool(
            name="semantic_course_search",
            description="检索与当前问题语义最相关的课程证据、资源和图谱文档，适合概念解释、课程资源、例题和学习建议问题。",
            execute_func=lambda query_text: self._semantic_tool_result(
                course_id=course_id,
                query_text=_coerce_string(query_text) or normalized_query,
                seed_point_ids=seed_point_ids,
                limit=limit,
            ),
            parameters=_query_tool_parameters("学生原始问题文本。"),
        )
        available_tools = [semantic_tool]
        graph_driver = None
        if neo4j_service.is_available:
            try:
                graph_driver = neo4j_service.get_driver()
            except Exception as error:
                logger.warning("Graph 查询驱动不可用，回退语义证据工具: course=%s error=%s", course_id, error)
                graph_driver = None
        if graph_driver is not None:
            available_tools.append(
                Tool(
                    name="graph_structure_query",
                    description="生成并执行课程图 Cypher 查询，适合回答前置知识、后续知识、依赖关系、学习顺序、路径与结构型事实问题。",
                    execute_func=lambda query_text: self._text2cypher_tool_result(
                        course_id=course_id,
                        query_text=_coerce_string(query_text) or normalized_query,
                        focus_point_id=focus_point_id,
                        focus_point_name=focus_point_name,
                    ),
                    parameters=_query_tool_parameters("学生的结构化图查询问题。"),
                )
            )
        return available_tools, graph_driver

    # 维护意图：在图驱动不可用时，仅用语义检索返回图查询上下文
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def _query_graph_semantic_only(
        self,
        *,
        course_id: int,
        normalized_query: str,
        seed_point_ids: list[int],
        limit: int,
    ) -> dict[str, object]:
        """在图驱动不可用时，仅用语义检索返回图查询上下文。"""
        semantic_only = self._semantic_tool_result(
            course_id=course_id,
            query_text=normalized_query,
            seed_point_ids=seed_point_ids,
            limit=limit,
        )
        return build_semantic_only_query_context(semantic_only, seed_point_ids)

    # 维护意图：在图驱动可用时，执行 ToolsRetriever 并聚合结果
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def _query_graph_with_tools(
        self,
        *,
        graph_driver: Driver,
        available_tools: list[Tool],
        normalized_query: str,
    ) -> dict[str, object]:
        """在图驱动可用时，执行 ToolsRetriever 并聚合结果。"""
        tools_retriever = ToolsRetriever(
            driver=graph_driver,
            llm=FacadeGraphRAGLLM(),
            tools=available_tools,
            system_instruction=self._graph_tools_system_instruction(),
        )
        tool_result = tools_retriever.search(query_text=normalized_query)
        return build_tools_query_context(tool_result)

    # 维护意图：通过官方 ToolsRetriever 组合语义检索与 Text2Cypher 图查询
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def query_graph(
        self,
        *,
        course_id: int,
        query: str,
        focus_point_id: int | None = None,
        focus_point_name: str = "",
        limit: int = 6,
    ) -> dict[str, object]:
        """通过官方 ToolsRetriever 组合语义检索与 Text2Cypher 图查询。"""
        normalized_query = query.strip()
        if not normalized_query:
            return build_empty_query_context()

        seed_point_ids = [focus_point_id] if isinstance(focus_point_id, int) and focus_point_id > 0 else []
        available_tools, graph_driver = self._build_available_tools(
            course_id=course_id,
            normalized_query=normalized_query,
            seed_point_ids=seed_point_ids,
            focus_point_id=focus_point_id,
            focus_point_name=focus_point_name,
            limit=limit,
        )

        if graph_driver is None:
            return self._query_graph_semantic_only(
                course_id=course_id,
                seed_point_ids=seed_point_ids,
                limit=limit,
                normalized_query=normalized_query,
            )
        return self._query_graph_with_tools(
            graph_driver=cast(Driver, graph_driver),
            available_tools=available_tools,
            normalized_query=normalized_query,
        )
