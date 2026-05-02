#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""GraphRAG 运行时兼容入口。

@Project : wisdom-edu
@File : runtime.py
@Author : Qintsg
@Date : 2026-04-04
"""

from __future__ import annotations

from collections.abc import Sequence
import json
import re

from neo4j_graphrag.llm import LLMInterfaceV2, LLMResponse
from neo4j_graphrag.llm.types import ToolCall, ToolCallResponse
from neo4j_graphrag.message_history import MessageHistory
from neo4j_graphrag.tool import Tool
from neo4j_graphrag.types import LLMMessage

from common.neo4j_service import neo4j_service
from platform_ai.llm import llm_facade
from platform_ai.rag.runtime_course import CourseGraphRAGRuntime
from platform_ai.rag.runtime_models import (
    COURSE_DOCUMENT_LABEL,
    COURSE_RETRIEVAL_MODE,
    DEFAULT_QDRANT_DIRECTORY,
    DEFAULT_SENTENCE_MODEL,
    DEFAULT_VECTOR_DIMENSION,
    GRAPH_QUERY_RETRIEVAL_MODE,
    GRAPH_TOOL_QUERY_MODE,
    DocumentPayload,
    GraphQueryContext,
    GraphRAGArtifactReport,
    GraphRAGSearchHit,
    SafeSentenceTransformerEmbedder,
    SourcePayload,
    StructuredCourseGraphExtractor,
    TokenHashEmbedder,
    _coerce_int,
    _coerce_string,
    _dedupe_strings,
    _escape_cypher_string,
    _message_history_text,
)
class FacadeGraphRAGLLM(LLMInterfaceV2):
    """让官方 GraphRAG 检索器复用仓库内现有的 LLM 门面。"""

    def __init__(self) -> None:
        super().__init__(
            model_name=getattr(llm_facade.service, "model_name", "wisdom-edu-graph-router"),
            model_params={"temperature": 0},
        )

    @staticmethod
    def _extract_line_value(prompt_text: str, key: str) -> str:
        """从结构化提示中提取单行键值。"""
        matched = re.search(rf"{re.escape(key)}\s*:\s*(.+)", prompt_text)
        return _coerce_string(matched.group(1)) if matched else ""

    @staticmethod
    def _extract_user_question(prompt_text: str) -> str:
        """从 Text2Cypher 自定义提示中提取用户问题。"""
        matched = re.search(r"User question:\s*(.*?)\n\nRules:", prompt_text, re.S)
        if matched:
            return _coerce_string(matched.group(1))
        return _coerce_string(prompt_text)

    @staticmethod
    def _normalize_invoke_input(
        raw_input: list[LLMMessage] | str,
    ) -> tuple[str, list[LLMMessage]]:
        """兼容 V2 message list 与仓库内旧式字符串 prompt 调用。"""
        if isinstance(raw_input, str):
            prompt_text = _coerce_string(raw_input)
            return prompt_text, [{"role": "user", "content": prompt_text}]

        normalized_messages: list[LLMMessage] = []
        prompt_lines: list[str] = []
        for raw_message in raw_input:
            if not isinstance(raw_message, dict):
                continue
            role = _coerce_string(raw_message.get("role")) or "user"
            content = raw_message.get("content")
            if isinstance(content, str):
                content_text = content
            elif content is None:
                content_text = ""
            else:
                content_text = json.dumps(content, ensure_ascii=False)
            normalized_messages.append({"role": role, "content": content_text})
            if content_text:
                prompt_lines.append(f"{role}: {content_text}")

        prompt_text = "\n".join(prompt_lines).strip()
        if not normalized_messages:
            normalized_messages = [{"role": "user", "content": prompt_text}]
        return prompt_text, normalized_messages

    @staticmethod
    def _response_format_hint(response_format: object | None) -> str:
        """为 V2 structured output 参数生成可读提示。"""
        if response_format is None:
            return "无"
        if isinstance(response_format, dict):
            return json.dumps(response_format, ensure_ascii=False)
        return _coerce_string(getattr(response_format, "__name__", response_format)) or "无"

    @classmethod
    def _build_target_match(
        cls,
        *,
        course_id: int,
        focus_point_id: int,
        focus_point_name: str,
        question: str,
    ) -> str:
        """为启发式 Cypher 生成稳定的目标知识点匹配子句。"""
        if focus_point_id > 0:
            return (
                f"MATCH (target:KnowledgePoint {{course_id: {course_id}}})\n"
                f"WHERE target.id = {focus_point_id} AND coalesce(target.is_published, true) = true"
            )

        lookup_name = _escape_cypher_string(focus_point_name or question)
        return (
            f"MATCH (target:KnowledgePoint {{course_id: {course_id}}})\n"
            "WHERE coalesce(target.is_published, true) = true "
            f"AND toLower(target.name) CONTAINS toLower('{lookup_name}')"
        )

    @classmethod
    def _fallback_cypher_from_prompt(cls, prompt_text: str) -> str:
        """在无可用模型时，为 Text2CypherRetriever 生成启发式 Cypher。"""
        course_id = _coerce_int(cls._extract_line_value(prompt_text, "course_id"), default=0)
        focus_point_id = _coerce_int(
            cls._extract_line_value(prompt_text, "focus_point_id"),
            default=0,
        )
        focus_point_name = cls._extract_line_value(prompt_text, "focus_point_name")
        question = cls._extract_user_question(prompt_text)
        normalized_question = question.lower()
        target_match = cls._build_target_match(
            course_id=course_id,
            focus_point_id=focus_point_id,
            focus_point_name=focus_point_name,
            question=question,
        )

        if any(keyword in normalized_question for keyword in ["前置", "先修", "先学", "基础"]):
            return (
                f"{target_match}\n"
                f"OPTIONAL MATCH (pre:KnowledgePoint {{course_id: {course_id}}})-[:PREREQUISITE]->(target)\n"
                f"OPTIONAL MATCH (doc:CourseDocument {{course_id: {course_id}}})-[:ABOUT]->(target)\n"
                "RETURN 'prerequisite' AS item_type,\n"
                "       target.id AS point_id,\n"
                "       target.name AS point_name,\n"
                "       'PREREQUISITE' AS relation_type,\n"
                "       pre.id AS related_point_id,\n"
                "       COALESCE(pre.name, '') AS related_point_name,\n"
                "       COALESCE(doc.title, '') AS source_title,\n"
                "       COALESCE(doc.excerpt, '') AS source_excerpt,\n"
                "       '说明该知识点的前置知识。' AS reasoning\n"
                "LIMIT 8"
            )

        if any(keyword in normalized_question for keyword in ["后续", "下一步", "之后", "延伸", "进阶"]):
            return (
                f"{target_match}\n"
                f"OPTIONAL MATCH (target)-[:PREREQUISITE]->(post:KnowledgePoint {{course_id: {course_id}}})\n"
                f"OPTIONAL MATCH (doc:CourseDocument {{course_id: {course_id}}})-[:ABOUT]->(target)\n"
                "RETURN 'postrequisite' AS item_type,\n"
                "       target.id AS point_id,\n"
                "       target.name AS point_name,\n"
                "       'PREREQUISITE' AS relation_type,\n"
                "       post.id AS related_point_id,\n"
                "       COALESCE(post.name, '') AS related_point_name,\n"
                "       COALESCE(doc.title, '') AS source_title,\n"
                "       COALESCE(doc.excerpt, '') AS source_excerpt,\n"
                "       '说明该知识点的后续知识。' AS reasoning\n"
                "LIMIT 8"
            )

        if any(keyword in normalized_question for keyword in ["路径", "顺序", "链路", "关系", "联系", "关联"]):
            return (
                f"{target_match}\n"
                "CALL {\n"
                "  WITH target\n"
                f"  OPTIONAL MATCH (pre:KnowledgePoint {{course_id: {course_id}}})-[:PREREQUISITE]->(target)\n"
                "  RETURN 'prerequisite' AS item_type, target.id AS point_id, target.name AS point_name,\n"
                "         'PREREQUISITE' AS relation_type, pre.id AS related_point_id, COALESCE(pre.name, '') AS related_point_name\n"
                "  UNION ALL\n"
                "  WITH target\n"
                f"  OPTIONAL MATCH (target)-[:PREREQUISITE]->(post:KnowledgePoint {{course_id: {course_id}}})\n"
                "  RETURN 'postrequisite' AS item_type, target.id AS point_id, target.name AS point_name,\n"
                "         'PREREQUISITE' AS relation_type, post.id AS related_point_id, COALESCE(post.name, '') AS related_point_name\n"
                "}\n"
                f"OPTIONAL MATCH (doc:CourseDocument {{course_id: {course_id}}})-[:ABOUT]->(target)\n"
                "RETURN item_type, point_id, point_name, relation_type, related_point_id, related_point_name,\n"
                "       COALESCE(doc.title, '') AS source_title,\n"
                "       COALESCE(doc.excerpt, '') AS source_excerpt,\n"
                "       '展示该知识点的局部知识链路。' AS reasoning\n"
                "LIMIT 8"
            )

        return (
            f"{target_match}\n"
            f"OPTIONAL MATCH (doc:CourseDocument {{course_id: {course_id}}})-[:ABOUT]->(target)\n"
            "RETURN 'resource' AS item_type,\n"
            "       target.id AS point_id,\n"
            "       target.name AS point_name,\n"
            "       'ABOUT' AS relation_type,\n"
            "       target.id AS related_point_id,\n"
            "       target.name AS related_point_name,\n"
            "       COALESCE(doc.title, '') AS source_title,\n"
            "       COALESCE(doc.excerpt, '') AS source_excerpt,\n"
            "       '展示该知识点的课程证据。' AS reasoning\n"
            "LIMIT 8"
        )

    @staticmethod
    def _heuristic_tool_calls(input_text: str, tools: list[Tool]) -> list[ToolCall]:
        """在无模型或模型路由失败时，基于关键词选择检索工具。"""
        normalized_query = input_text.lower()
        available_names = [tool.get_name() for tool in tools]
        semantic_tool_name = next(
            (
                tool_name
                for tool_name in available_names
                if "semantic" in tool_name or "vector" in tool_name
            ),
            "",
        )
        graph_tool_name = next(
            (
                tool_name
                for tool_name in available_names
                if "graph" in tool_name or "cypher" in tool_name
            ),
            "",
        )
        needs_graph = any(
            keyword in normalized_query
            for keyword in [
                "前置",
                "先修",
                "后续",
                "依赖",
                "路径",
                "顺序",
                "关系",
                "联系",
                "关联",
                "图谱",
            ]
        )
        needs_semantic = any(
            keyword in normalized_query
            for keyword in [
                "解释",
                "是什么",
                "介绍",
                "资源",
                "例题",
                "练习",
                "学习",
                "总结",
                "讲解",
                "怎么",
                "如何",
            ]
        )

        selected_calls: list[ToolCall] = []
        if graph_tool_name and needs_graph:
            selected_calls.append(
                ToolCall(name=graph_tool_name, arguments={"query_text": input_text})
            )
        if semantic_tool_name and (needs_semantic or not selected_calls):
            selected_calls.append(
                ToolCall(name=semantic_tool_name, arguments={"query_text": input_text})
            )
        if not selected_calls and graph_tool_name:
            selected_calls.append(
                ToolCall(name=graph_tool_name, arguments={"query_text": input_text})
            )
        return selected_calls

    def invoke(
        self,
        input: list[LLMMessage] | str,
        response_format: object | None = None,
        message_history: list[LLMMessage] | MessageHistory | None = None,
        system_instruction: str | None = None,
        **_: object,
    ) -> LLMResponse:
        """将官方 Text2Cypher prompt 委托给仓库的 LLM 门面处理。"""
        prompt_text, normalized_messages = self._normalize_invoke_input(input)
        fallback_cypher = self._fallback_cypher_from_prompt(prompt_text)
        if not llm_facade.is_available:
            return LLMResponse(content=fallback_cypher)

        history_text = _message_history_text(message_history)
        result = llm_facade.call_with_fallback(
            prompt=(
                "你是 Neo4j Cypher 生成器。你会收到一段已经包含 schema、课程范围与示例的任务提示。"
                "请严格遵循该提示，并输出 JSON：{\"content\": \"<Cypher语句>\"}。"
                "content 字段只能包含一条可执行 Cypher，不得包含 Markdown、解释或额外文本。"
                f"\n系统指令：{system_instruction or '无'}"
                f"\n历史对话：\n{history_text or '无'}"
                f"\n响应格式：{self._response_format_hint(response_format)}"
                f"\n消息输入：\n{json.dumps(normalized_messages, ensure_ascii=False, indent=2)}"
                f"\n\n原始任务提示：\n{prompt_text}"
            ),
            call_type="graph_rag_text2cypher",
            fallback_response={"content": fallback_cypher},
        )
        generated_cypher = _coerce_string(result.get("content")) or fallback_cypher
        return LLMResponse(content=generated_cypher)

    async def ainvoke(
        self,
        input: list[LLMMessage] | str,
        response_format: object | None = None,
        **kwargs: object,
    ) -> LLMResponse:
        """异步接口直接复用同步实现，保持与官方接口兼容。"""
        return self.invoke(
            input=input,
            response_format=response_format,
            **kwargs,
        )

    def invoke_with_tools(
        self,
        input: str,
        tools: Sequence[Tool],
        message_history: list[LLMMessage] | MessageHistory | None = None,
        system_instruction: str | None = None,
    ) -> ToolCallResponse:
        """用结构化 JSON 路由官方 ToolsRetriever 所需的工具选择。"""
        normalized_tools = list(tools)
        fallback_tool_calls = [
            {"name": tool_call.name, "arguments": tool_call.arguments}
            for tool_call in self._heuristic_tool_calls(input, normalized_tools)
        ]
        if not llm_facade.is_available:
            return ToolCallResponse(
                content="使用启发式规则选择检索工具。",
                tool_calls=self._heuristic_tool_calls(input, normalized_tools),
            )

        history_text = _message_history_text(message_history)
        tool_specs = [
            {
                "name": tool.get_name(),
                "description": tool.get_description(),
                "parameters": tool.get_parameters(),
            }
            for tool in normalized_tools
        ]
        routing_result = llm_facade.call_with_fallback(
            prompt=(
                "你是课程 GraphRAG 的工具路由器，需要为当前问题选择最合适的检索工具。"
                f"\n系统指令：{system_instruction or '无'}"
                f"\n历史对话：\n{history_text or '无'}"
                f"\n可用工具：\n{json.dumps(tool_specs, ensure_ascii=False, indent=2)}"
                f"\n用户问题：\n{input}"
                "\n\n请输出 JSON："
                "{\"content\": \"简短路由理由\", \"tool_calls\": [{\"name\": \"工具名\", \"arguments\": {\"query_text\": \"原问题\"}}]}"
                "\n规则："
                "\n1. 只能使用给定的工具名。"
                "\n2. 结构关系/前置/后续/路径问题优先选图查询工具。"
                "\n3. 概念解释/资源/证据补充问题优先选语义检索工具。"
                "\n4. 如果用户同时询问结构关系与解释，可以同时选择多个工具。"
                "\n5. arguments 中至少保留 query_text，且不要改写用户问题含义。"
            ),
            call_type="graph_rag_tool_router",
            fallback_response={
                "content": "使用启发式规则选择检索工具。",
                "tool_calls": fallback_tool_calls,
            },
        )

        available_names = {tool.get_name() for tool in normalized_tools}
        validated_tool_calls: list[ToolCall] = []
        raw_tool_calls = routing_result.get("tool_calls")
        if isinstance(raw_tool_calls, list):
            for raw_tool_call in raw_tool_calls:
                if not isinstance(raw_tool_call, dict):
                    continue
                tool_name = _coerce_string(raw_tool_call.get("name"))
                if tool_name not in available_names:
                    continue
                raw_arguments = raw_tool_call.get("arguments")
                normalized_arguments = (
                    {str(key): value for key, value in raw_arguments.items()}
                    if isinstance(raw_arguments, dict)
                    else {}
                )
                normalized_arguments.setdefault("query_text", input)
                validated_tool_calls.append(
                    ToolCall(name=tool_name, arguments=normalized_arguments)
                )

        if not validated_tool_calls:
            validated_tool_calls = self._heuristic_tool_calls(input, normalized_tools)

        return ToolCallResponse(
            content=_coerce_string(routing_result.get("content")) or "完成图查询工具选择。",
            tool_calls=validated_tool_calls,
        )


student_graphrag_runtime = CourseGraphRAGRuntime()

__all__ = [
    "COURSE_DOCUMENT_LABEL",
    "COURSE_RETRIEVAL_MODE",
    "DEFAULT_QDRANT_DIRECTORY",
    "DEFAULT_SENTENCE_MODEL",
    "DEFAULT_VECTOR_DIMENSION",
    "GRAPH_QUERY_RETRIEVAL_MODE",
    "GRAPH_TOOL_QUERY_MODE",
    "CourseGraphRAGRuntime",
    "DocumentPayload",
    "FacadeGraphRAGLLM",
    "GraphQueryContext",
    "GraphRAGArtifactReport",
    "GraphRAGSearchHit",
    "SafeSentenceTransformerEmbedder",
    "SourcePayload",
    "StructuredCourseGraphExtractor",
    "TokenHashEmbedder",
    "neo4j_service",
    "student_graphrag_runtime",
]
