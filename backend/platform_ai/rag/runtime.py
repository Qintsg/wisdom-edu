#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""GraphRAG 运行时。

@Project : wisdom-edu
@File : runtime.py
@Author : Qintsg
@Date : 2026-04-04

该模块负责三件事：
1. 把现有课程语料抽取为 GraphRAG 文档投影；
2. 将文档向量写入 Qdrant，本地持久化为课程级向量集合；
3. 使用 `neo4j-graphrag-python` 官方检索器把向量命中重新接回 Neo4j 图谱。

这样可以在不推翻现有课程知识图谱的前提下，把 AI 助手与知识图谱详情
统一升级到“图 + 向量 + 自定义抽取/检索”的混合 GraphRAG 体系。
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from hashlib import md5, sha256
from math import sqrt
from pathlib import Path
from typing import cast
import asyncio
import json
import logging
import os
import re
from uuid import NAMESPACE_URL, uuid5

from django.conf import settings
from neo4j import Driver
from neo4j_graphrag.embeddings import SentenceTransformerEmbeddings
from neo4j_graphrag.embeddings.base import Embedder
from neo4j_graphrag.experimental.components.entity_relation_extractor import EntityRelationExtractor
from neo4j_graphrag.experimental.components.types import (
    Neo4jGraph,
    Neo4jNode,
    Neo4jRelationship,
    TextChunk,
    TextChunks,
)
from neo4j_graphrag.llm import LLMInterfaceV2, LLMResponse
from neo4j_graphrag.llm.types import ToolCall, ToolCallResponse
from neo4j_graphrag.message_history import MessageHistory
from neo4j_graphrag.retrievers import QdrantNeo4jRetriever
from neo4j_graphrag.retrievers import Text2CypherRetriever, ToolsRetriever
from neo4j_graphrag.tool import ObjectParameter, StringParameter, Tool
from neo4j_graphrag.types import LLMMessage, RetrieverResult, RetrieverResultItem
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

from common.neo4j_service import neo4j_service
from platform_ai.llm import llm_facade

from .corpus import tokenize


logger = logging.getLogger(__name__)


DocumentPayload = dict[str, object]
SourcePayload = dict[str, object]

DEFAULT_VECTOR_DIMENSION = 256
DEFAULT_SENTENCE_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_QDRANT_DIRECTORY = Path("runtime_logs") / "rag" / "qdrant"
COURSE_DOCUMENT_LABEL = "CourseDocument"
COURSE_RETRIEVAL_MODE = "neo4j_graphrag_qdrant"
GRAPH_TOOL_QUERY_MODE = "graph_tools"
GRAPH_QUERY_RETRIEVAL_MODE = "neo4j_graphrag_tools"


@dataclass(frozen=True)
class GraphRAGArtifactReport:
    """描述一次课程级 GraphRAG 物化的主要产物。"""

    collection_name: str
    qdrant_path: str
    vector_points: int
    embedder_provider: str
    neo4j_projection_ready: bool
    projected_documents: int
    projected_relations: int

    def as_dict(self) -> dict[str, object]:
        """转换为适合持久化到课程索引的 JSON 结构。"""
        return {
            "collection_name": self.collection_name,
            "qdrant_path": self.qdrant_path,
            "vector_points": self.vector_points,
            "embedder_provider": self.embedder_provider,
            "neo4j_projection_ready": self.neo4j_projection_ready,
            "projected_documents": self.projected_documents,
            "projected_relations": self.projected_relations,
        }


@dataclass(frozen=True)
class GraphRAGSearchHit:
    """承载一次混合检索返回的单条证据。"""

    external_id: str
    doc_id: str
    title: str
    kind: str
    excerpt: str
    url: str
    score: float
    point_ids: list[int]
    matched_points: list[SourcePayload]
    prerequisites: list[SourcePayload]
    postrequisites: list[SourcePayload]
    source_label: str = COURSE_RETRIEVAL_MODE

    def as_source(self, query_mode: str) -> dict[str, object]:
        """转换为前端可直接消费的证据 source。"""
        return {
            "id": self.external_id,
            "title": self.title,
            "kind": self.kind,
            "url": self.url,
            "excerpt": self.excerpt,
            "query_mode": query_mode,
            "score": round(self.score, 6),
            "retrieval_source": self.source_label,
        }


@dataclass(frozen=True)
class GraphQueryContext:
    """承载官方 ToolsRetriever / Text2Cypher 生成的结构化图查询上下文。"""

    context: str
    sources: list[dict[str, object]]
    tools_selected: list[str]
    generated_cypher: str
    query_modes: list[str]
    matched_point_ids: list[int]
    mode: str = GRAPH_QUERY_RETRIEVAL_MODE

    def as_dict(self) -> dict[str, object]:
        """转换为稳定的业务层载荷。"""
        return {
            "context": self.context,
            "sources": self.sources,
            "tools_selected": self.tools_selected,
            "generated_cypher": self.generated_cypher,
            "query_modes": self.query_modes,
            "matched_point_ids": self.matched_point_ids,
            "mode": self.mode,
        }


def _coerce_string(value: object) -> str:
    """把任意输入收敛为稳定字符串，避免外部数据结构污染。"""
    return str(value).strip() if value is not None else ""


def _coerce_int(value: object, default: int = 0) -> int:
    """把弱类型输入稳定转换为整数。"""
    normalized_text = _coerce_string(value)
    if normalized_text.lstrip("-").isdigit():
        return int(normalized_text)
    return default


def _coerce_int_list(value: object) -> list[int]:
    """提取 payload 中的整型列表，过滤空值与非法值。"""
    normalized_ids: list[int] = []
    if isinstance(value, list):
        raw_values = value
    else:
        raw_values = [value]

    for raw_value in raw_values:
        normalized_text = _coerce_string(raw_value)
        if not normalized_text or not normalized_text.lstrip("-").isdigit():
            continue
        normalized_ids.append(int(normalized_text))
    return normalized_ids


def _escape_cypher_string(value: str) -> str:
    """转义 Cypher 单引号字符串，避免模板化查询被截断。"""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _message_history_text(
    message_history: list[LLMMessage] | MessageHistory | None,
) -> str:
    """将消息历史压缩为可读文本，供路由与提示生成复用。"""
    if message_history is None:
        return ""

    raw_messages = getattr(message_history, "messages", message_history)
    if not isinstance(raw_messages, list):
        return ""

    normalized_lines: list[str] = []
    for raw_message in raw_messages[:8]:
        if isinstance(raw_message, dict):
            role = _coerce_string(raw_message.get("role")) or "user"
            content = _coerce_string(raw_message.get("content"))
        else:
            role = _coerce_string(getattr(raw_message, "role", "")) or "user"
            content = _coerce_string(getattr(raw_message, "content", ""))
        if content:
            normalized_lines.append(f"{role}: {content}")
    return "\n".join(normalized_lines)


def _query_tool_parameters(description: str) -> ObjectParameter:
    """为 ToolsRetriever 生成极简参数模式，降低工具路由复杂度。"""
    return ObjectParameter(
        description="课程图查询参数",
        properties={
            "query_text": StringParameter(
                description=description,
                required=True,
            )
        },
        required_properties=["query_text"],
        additional_properties=False,
    )


def _dedupe_strings(items: Sequence[str]) -> list[str]:
    """保持原顺序去重字符串列表。"""
    seen_items: set[str] = set()
    ordered_items: list[str] = []
    for item in items:
        normalized_item = item.strip()
        if not normalized_item or normalized_item in seen_items:
            continue
        seen_items.add(normalized_item)
        ordered_items.append(normalized_item)
    return ordered_items


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


def _compact_excerpt(text: str, limit: int = 220) -> str:
    """压缩文本片段，便于进入聊天窗口与知识点详情。"""
    normalized = " ".join(segment.strip() for segment in text.splitlines() if segment.strip())
    return normalized[:limit]


def _vector_point_ids(document: DocumentPayload) -> list[int]:
    """从课程文档 payload 中提取关联知识点 ID 列表。"""
    metadata = document.get("metadata")
    point_ids: list[int] = []
    if isinstance(metadata, dict):
        point_ids.extend(_coerce_int_list(metadata.get("knowledge_point_ids", [])))
        point_ids.extend(_coerce_int_list(metadata.get("knowledge_point_id")))
        entity_ids = metadata.get("entity_ids")
        if isinstance(entity_ids, list):
            for entity_id in entity_ids:
                normalized = _coerce_string(entity_id)
                if normalized.startswith("kp:"):
                    point_ids.extend(_coerce_int_list(normalized.partition(":")[2]))
    document_id = _coerce_string(document.get("id"))
    if document_id.startswith("kp:"):
        point_ids.extend(_coerce_int_list(document_id.partition(":")[2]))
    return sorted(set(point_ids))


def _qdrant_point_id(external_id: str) -> str:
    """为 Qdrant 本地模式生成稳定 UUID。"""
    normalized_external_id = _coerce_string(external_id)
    if not normalized_external_id:
        normalized_external_id = "empty-document"
    return str(uuid5(NAMESPACE_URL, f"wisdom-edu:{normalized_external_id}"))


class TokenHashEmbedder(Embedder):
    """离线可用的哈希向量器。

    这里不依赖外部模型下载，适合测试与本地开发。
    真正部署时可以通过环境变量切换到 `SentenceTransformerEmbeddings`。
    """

    def __init__(self, dimensions: int = DEFAULT_VECTOR_DIMENSION) -> None:
        super().__init__()
        self.dimensions = max(64, int(dimensions))

    def embed_query(self, text: str) -> list[float]:
        """把查询文本编码为稠密向量。

        做法是对 token 做双哈希投影：
        - 一个哈希决定落桶位置；
        - 另一个哈希决定正负符号；
        - 最后进行 $L_2$ 归一化，便于余弦检索。
        """
        tokens = list(tokenize(text))
        if not tokens:
            tokens = [text.strip() or "empty"]

        vector = [0.0] * self.dimensions
        for token in tokens:
            digest = sha256(token.encode("utf-8")).hexdigest()
            bucket = int(digest[:8], 16) % self.dimensions
            sign = 1.0 if int(digest[8:16], 16) % 2 == 0 else -1.0
            weight = 1.0 + min(len(token), 12) / 12.0
            vector[bucket] += sign * weight

        norm = sqrt(sum(component * component for component in vector))
        if norm <= 0:
            return vector
        return [component / norm for component in vector]


class SafeSentenceTransformerEmbedder(Embedder):
    """对官方 SentenceTransformer 向量器做安全包装。

    这样即使本地没有模型缓存、网络不可用或运行时初始化失败，
    也会自动回退到哈希向量器，而不会让索引构建整体中断。
    """

    def __init__(self, model_name: str, fallback_embedder: TokenHashEmbedder) -> None:
        super().__init__()
        self.model_name = model_name
        self.fallback_embedder = fallback_embedder
        self._delegate: SentenceTransformerEmbeddings | None = None
        self._delegate_unavailable = False

    def _resolve_delegate(self) -> SentenceTransformerEmbeddings | None:
        """延迟初始化真实 embedding 模型，避免模块导入即触发下载。"""
        if self._delegate_unavailable:
            return None
        if self._delegate is not None:
            return self._delegate
        try:
            self._delegate = SentenceTransformerEmbeddings(model=self.model_name)
            return self._delegate
        except Exception as error:  # pragma: no cover - 仅在模型不可用时触发
            logger.warning("SentenceTransformer 初始化失败，回退哈希向量器: model=%s error=%s", self.model_name, error)
            self._delegate_unavailable = True
            return None

    def embed_query(self, text: str) -> list[float]:
        """优先使用 SentenceTransformer，失败时自动回退。"""
        delegate = self._resolve_delegate()
        if delegate is None:
            return self.fallback_embedder.embed_query(text)
        try:
            return delegate.embed_query(text)
        except Exception as error:  # pragma: no cover - 仅在模型运行失败时触发
            logger.warning("SentenceTransformer 编码失败，回退哈希向量器: model=%s error=%s", self.model_name, error)
            self._delegate_unavailable = True
            return self.fallback_embedder.embed_query(text)


class StructuredCourseGraphExtractor(EntityRelationExtractor):
    """把课程已有结构化文档投影成 GraphRAG 图对象。

    这里并不重新“猜测”知识点关系，而是显式复用课程现成事实：
    - 每条课程文档都会生成一个 `CourseDocument` 节点；
    - 文档与知识点之间会生成 `ABOUT` 关系；
    - 这些节点稍后会被同步到 Neo4j，供官方 Qdrant 检索器回查图谱。
    """

    def __init__(self, course_id: int) -> None:
        super().__init__()
        self.course_id = int(course_id)

    async def run(
        self,
        chunks: TextChunks,
        document_info: object | None = None,
        lexical_graph_config: object | None = None,
        **kwargs: object,
    ) -> Neo4jGraph:
        del document_info, lexical_graph_config, kwargs

        graph_nodes: list[Neo4jNode] = []
        graph_relationships: list[Neo4jRelationship] = []

        for chunk in chunks.chunks:
            metadata = chunk.metadata if isinstance(chunk.metadata, dict) else {}
            external_id = _coerce_string(metadata.get("external_id") or chunk.uid or f"chunk:{chunk.index}")
            title = _coerce_string(metadata.get("title")) or external_id
            kind = _coerce_string(metadata.get("kind")) or "document"
            url = _coerce_string(metadata.get("url"))
            chapter = _coerce_string(metadata.get("chapter"))
            point_ids = _coerce_int_list(metadata.get("point_ids", []))
            point_id_strings = [str(point_id) for point_id in point_ids]

            graph_nodes.append(
                Neo4jNode(
                    id=external_id,
                    label=COURSE_DOCUMENT_LABEL,
                    properties={
                        "external_id": external_id,
                        "doc_id": _coerce_string(metadata.get("doc_id") or external_id),
                        "course_id": self.course_id,
                        "title": title,
                        "kind": kind,
                        "content": chunk.text,
                        "url": url,
                        "chapter": chapter,
                        "point_ids_csv": ",".join(point_id_strings),
                        "excerpt": _compact_excerpt(chunk.text),
                    },
                )
            )

            for point_id in point_ids:
                graph_relationships.append(
                    Neo4jRelationship(
                        start_node_id=external_id,
                        end_node_id=f"kp:{point_id}",
                        type="ABOUT",
                        properties={
                            "course_id": self.course_id,
                            "point_id": point_id,
                        },
                    )
                )

        return Neo4jGraph(nodes=graph_nodes, relationships=graph_relationships)


class CourseGraphRAGRuntime:
    """统一管理课程级 GraphRAG 物化与检索。"""

    def __init__(self) -> None:
        self._qdrant_client: QdrantClient | None = None
        self._hash_embedder = TokenHashEmbedder(self._vector_dimension())
        self._configured_embedder: Embedder | None = None
        self._configured_provider: str | None = None

    def _vector_dimension(self) -> int:
        """读取向量维度配置；对哈希向量器直接决定桶数量。"""
        raw_value = str(getattr(settings, "GRAPHRAG_VECTOR_DIMENSION", DEFAULT_VECTOR_DIMENSION)).strip()
        if raw_value.isdigit():
            return max(64, int(raw_value))
        return DEFAULT_VECTOR_DIMENSION

    def qdrant_directory(self) -> Path:
        """返回本地 Qdrant 持久化目录。"""
        configured_path = str(getattr(settings, "GRAPHRAG_QDRANT_PATH", "")).strip()
        if configured_path:
            return Path(configured_path)
        return Path(settings.BASE_DIR) / DEFAULT_QDRANT_DIRECTORY

    def collection_name(self, course_id: int) -> str:
        """为每门课程生成稳定的向量集合名称。"""
        return f"course_{int(course_id)}_documents_v2"

    def _qdrant(self) -> QdrantClient:
        """按需初始化本地 Qdrant 客户端。"""
        if self._qdrant_client is None:
            storage_path = self.qdrant_directory()
            storage_path.mkdir(parents=True, exist_ok=True)
            self._qdrant_client = QdrantClient(path=str(storage_path))
        return self._qdrant_client

    def _embedder(self) -> tuple[str, Embedder]:
        """根据配置解析实际使用的 embedder。"""
        configured_provider = str(getattr(settings, "GRAPHRAG_EMBEDDER_PROVIDER", "hash")).strip().lower() or "hash"
        if self._configured_embedder is not None and self._configured_provider == configured_provider:
            return configured_provider, self._configured_embedder

        if configured_provider == "sentence_transformer":
            model_name = str(getattr(settings, "GRAPHRAG_SENTENCE_MODEL", DEFAULT_SENTENCE_MODEL)).strip() or DEFAULT_SENTENCE_MODEL
            self._configured_embedder = SafeSentenceTransformerEmbedder(model_name=model_name, fallback_embedder=self._hash_embedder)
        else:
            configured_provider = "hash"
            self._configured_embedder = self._hash_embedder

        self._configured_provider = configured_provider
        return configured_provider, self._configured_embedder

    def _collection_exists(self, collection_name: str) -> bool:
        """安全检查向量集合是否存在。"""
        try:
            return self._qdrant().collection_exists(collection_name)
        except Exception as error:
            logger.warning("检查 Qdrant 集合失败: collection=%s error=%s", collection_name, error)
            return False

    def _build_chunks(self, documents: list[DocumentPayload]) -> TextChunks:
        """把课程文档转换为 GraphRAG extractor 所需的 TextChunks。"""
        chunks: list[TextChunk] = []
        for index, document in enumerate(documents):
            metadata = document.get("metadata")
            metadata_dict = metadata if isinstance(metadata, dict) else {}
            external_id = _coerce_string(document.get("id")) or f"doc:{index}"
            chunks.append(
                TextChunk(
                    text=_coerce_string(document.get("content")),
                    index=index,
                    metadata={
                        "external_id": external_id,
                        "doc_id": external_id,
                        "title": _coerce_string(document.get("title")),
                        "kind": _coerce_string(document.get("kind")),
                        "url": _coerce_string(document.get("url")),
                        "chapter": _coerce_string(metadata_dict.get("chapter")),
                        "point_ids": _vector_point_ids(document),
                    },
                    uid=external_id,
                )
            )
        return TextChunks(chunks=chunks)

    def _projection_from_graph(self, graph: Neo4jGraph) -> tuple[list[DocumentPayload], list[DocumentPayload]]:
        """把 extractor 输出拆成 Neo4j 可直接写入的节点与关系投影。"""
        projected_documents: list[DocumentPayload] = []
        projected_links: list[DocumentPayload] = []

        for graph_node in graph.nodes:
            if graph_node.label != COURSE_DOCUMENT_LABEL:
                continue
            node_properties = graph_node.properties or {}
            projected_documents.append(
                {
                    "external_id": _coerce_string(node_properties.get("external_id") or graph_node.id),
                    "doc_id": _coerce_string(node_properties.get("doc_id") or graph_node.id),
                    "title": _coerce_string(node_properties.get("title")),
                    "kind": _coerce_string(node_properties.get("kind")),
                    "content": _coerce_string(node_properties.get("content")),
                    "url": _coerce_string(node_properties.get("url")),
                    "chapter": _coerce_string(node_properties.get("chapter")),
					"point_ids": _coerce_int_list(
						_coerce_string(node_properties.get("point_ids_csv")).split(",")
					),
                    "excerpt": _coerce_string(node_properties.get("excerpt")),
                }
            )

        for graph_relationship in graph.relationships:
            if graph_relationship.type != "ABOUT":
                continue
            point_token = _coerce_string(graph_relationship.end_node_id)
            if not point_token.startswith("kp:"):
                continue
            point_text = point_token.partition(":")[2]
            if not point_text.isdigit():
                continue
            projected_links.append(
                {
                    "external_id": _coerce_string(graph_relationship.start_node_id),
                    "point_id": int(point_text),
                }
            )

        return projected_documents, projected_links

    def _vector_points(self, documents: list[DocumentPayload], embedder: Embedder) -> tuple[int, list[PointStruct]]:
        """为课程文档生成 Qdrant Point 列表，并返回向量维度。"""
        vector_points: list[PointStruct] = []
        vector_size = 0
        for document in documents:
            external_id = _coerce_string(document.get("id"))
            if not external_id:
                continue
            content = _coerce_string(document.get("content"))
            vector = embedder.embed_query(content)
            if not vector:
                continue
            vector_size = max(vector_size, len(vector))
            metadata = document.get("metadata")
            metadata_dict = metadata if isinstance(metadata, dict) else {}
            payload = {
                "external_id": external_id,
                "doc_id": external_id,
                "course_id": _coerce_int(metadata_dict.get("course_id"), default=0),
                "title": _coerce_string(document.get("title")),
                "kind": _coerce_string(document.get("kind")),
                "url": _coerce_string(document.get("url")),
                "chapter": _coerce_string(metadata_dict.get("chapter")),
                "point_ids": _vector_point_ids(document),
                "excerpt": _compact_excerpt(content),
            }
            vector_points.append(
                PointStruct(
                    id=_qdrant_point_id(external_id),
                    vector=vector,
                    payload=payload,
                )
            )
        return vector_size, vector_points

    def materialize_course_payload(self, course_id: int, payload: DocumentPayload) -> dict[str, object]:
        """将课程索引物化到 Qdrant 与 Neo4j GraphRAG 投影。"""
        raw_documents = payload.get("documents")
        documents = [item for item in raw_documents if isinstance(item, dict)] if isinstance(raw_documents, list) else []
        provider_name, embedder = self._embedder()
        collection_name = self.collection_name(course_id)

        if self._collection_exists(collection_name):
            self._qdrant().delete_collection(collection_name)

        vector_size, vector_points = self._vector_points(documents, embedder)
        self._qdrant().create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size or self._vector_dimension(), distance=Distance.COSINE),
            on_disk_payload=True,
        )
        if vector_points:
            self._qdrant().upsert(collection_name=collection_name, points=vector_points, wait=True)

        extractor = StructuredCourseGraphExtractor(course_id=course_id)
        extracted_graph = asyncio.run(extractor.run(self._build_chunks(documents)))
        projected_documents, projected_links = self._projection_from_graph(extracted_graph)
        neo4j_report = neo4j_service.sync_course_graphrag_projection(
            course_id=course_id,
            documents=projected_documents,
            about_links=projected_links,
        )
        artifact_report = GraphRAGArtifactReport(
            collection_name=collection_name,
            qdrant_path=str(self.qdrant_directory()),
            vector_points=len(vector_points),
            embedder_provider=provider_name,
            neo4j_projection_ready=bool(neo4j_report.get("status") == "success"),
            projected_documents=_coerce_int(neo4j_report.get("documents", 0), default=0),
            projected_relations=_coerce_int(neo4j_report.get("relations", 0), default=0),
        )
        payload["graph_rag_artifacts"] = artifact_report.as_dict()
        return artifact_report.as_dict()

    def ensure_materialized(self, course_id: int, payload: DocumentPayload) -> dict[str, object]:
        """确保课程索引的向量集合与 Neo4j 投影同时存在。"""
        collection_name = self.collection_name(course_id)
        has_collection = self._collection_exists(collection_name)
        has_projection = neo4j_service.has_course_graphrag_projection(course_id)
        artifact_payload = payload.get("graph_rag_artifacts")
        if has_collection and (has_projection or not neo4j_service.is_available) and isinstance(artifact_payload, dict):
            return artifact_payload
        return self.materialize_course_payload(course_id, payload)

    def clear_course_payload(self, course_id: int) -> bool:
        """删除课程级 Qdrant 向量集合，避免删课后残留僵尸索引。"""
        collection_name = self.collection_name(course_id)
        if not self._collection_exists(collection_name):
            return False
        try:
            self._qdrant().delete_collection(collection_name)
        except Exception as error:
            logger.warning("清理课程 Qdrant 集合失败: course=%s error=%s", course_id, error)
            return False
        return True

    def _retrieval_query(self) -> str:
        """定义官方检索器回查 Neo4j 时的课程级取图语句。"""
        return """
        WITH node, score
        OPTIONAL MATCH (node)-[:ABOUT]->(point:KnowledgePoint)
        OPTIONAL MATCH (pre:KnowledgePoint)-[:PREREQUISITE]->(point)
        OPTIONAL MATCH (point)-[:PREREQUISITE]->(post:KnowledgePoint)
        RETURN node.external_id AS external_id,
               node.doc_id AS doc_id,
               node.title AS title,
               node.kind AS kind,
               node.url AS url,
               node.excerpt AS excerpt,
               node.point_ids AS point_ids,
               score,
               collect(DISTINCT CASE WHEN point.id IS NULL THEN NULL ELSE {point_id: point.id, point_name: point.name} END) AS matched_points,
               collect(DISTINCT CASE WHEN pre.id IS NULL THEN NULL ELSE {point_id: pre.id, point_name: pre.name} END) AS prerequisites,
               collect(DISTINCT CASE WHEN post.id IS NULL THEN NULL ELSE {point_id: post.id, point_name: post.name} END) AS postrequisites
        """

    def _format_retriever_record(self, record: object) -> RetrieverResultItem:
        """把官方检索器返回的 Neo4j 记录收敛为统一元数据。"""
        get_value = getattr(record, "get")
        metadata = {
            "external_id": _coerce_string(get_value("external_id")),
            "doc_id": _coerce_string(get_value("doc_id")),
            "title": _coerce_string(get_value("title")) or "课程证据",
            "kind": _coerce_string(get_value("kind")) or "document",
            "url": _coerce_string(get_value("url")),
            "excerpt": _coerce_string(get_value("excerpt")),
            "score": float(get_value("score") or 0.0),
            "point_ids": _coerce_int_list(get_value("point_ids") or []),
            "matched_points": [item for item in (get_value("matched_points") or []) if isinstance(item, dict)],
            "prerequisites": [item for item in (get_value("prerequisites") or []) if isinstance(item, dict)],
            "postrequisites": [item for item in (get_value("postrequisites") or []) if isinstance(item, dict)],
            "retrieval_source": COURSE_RETRIEVAL_MODE,
        }
        return RetrieverResultItem(content=metadata["excerpt"] or metadata["title"], metadata=metadata)

    def _parse_items(self, items: list[object]) -> list[GraphRAGSearchHit]:
        """将 RetrieverResult items 解析成业务层更易处理的 dataclass。"""
        parsed_hits: list[GraphRAGSearchHit] = []
        for item in items:
            metadata = getattr(item, "metadata", None)
            if not isinstance(metadata, dict):
                continue
            parsed_hits.append(
                GraphRAGSearchHit(
                    external_id=_coerce_string(metadata.get("external_id")),
                    doc_id=_coerce_string(metadata.get("doc_id") or metadata.get("external_id")),
                    title=_coerce_string(metadata.get("title")) or "课程证据",
                    kind=_coerce_string(metadata.get("kind")) or "document",
                    excerpt=_coerce_string(metadata.get("excerpt")),
                    url=_coerce_string(metadata.get("url")),
                    score=float(metadata.get("score") or 0.0),
                    point_ids=_coerce_int_list(metadata.get("point_ids") or []),
                    matched_points=[entry for entry in metadata.get("matched_points", []) if isinstance(entry, dict)],
                    prerequisites=[entry for entry in metadata.get("prerequisites", []) if isinstance(entry, dict)],
                    postrequisites=[entry for entry in metadata.get("postrequisites", []) if isinstance(entry, dict)],
                    source_label=_coerce_string(metadata.get("retrieval_source")) or COURSE_RETRIEVAL_MODE,
                )
            )
        return parsed_hits

    def _search_qdrant_only(self, course_id: int, query: str, limit: int) -> list[GraphRAGSearchHit]:
        """Neo4j 不可用时，仅凭向量库返回基础证据。"""
        collection_name = self.collection_name(course_id)
        if not self._collection_exists(collection_name):
            return []
        _, embedder = self._embedder()
        response = self._qdrant().query_points(
            collection_name=collection_name,
            query=embedder.embed_query(query),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        fallback_hits: list[GraphRAGSearchHit] = []
        for point in response.points:
            payload = point.payload if isinstance(point.payload, dict) else {}
            fallback_hits.append(
                GraphRAGSearchHit(
                    external_id=_coerce_string(payload.get("external_id") or point.id),
                    doc_id=_coerce_string(payload.get("doc_id") or point.id),
                    title=_coerce_string(payload.get("title")) or "课程证据",
                    kind=_coerce_string(payload.get("kind")) or "document",
                    excerpt=_coerce_string(payload.get("excerpt")),
                    url=_coerce_string(payload.get("url")),
                    score=float(getattr(point, "score", 0.0) or 0.0),
                    point_ids=_coerce_int_list(payload.get("point_ids") or []),
                    matched_points=[],
                    prerequisites=[],
                    postrequisites=[],
                    source_label="qdrant_local_only",
                )
            )
        return fallback_hits

    def search_documents(
        self,
        *,
        course_id: int,
        query: str,
        limit: int = 6,
        seed_point_ids: list[int] | None = None,
    ) -> list[GraphRAGSearchHit]:
        """执行课程级混合检索，并对种子知识点做轻量重排。"""
        normalized_query = query.strip()
        if not normalized_query:
            return []

        if not neo4j_service.is_available:
            return self._search_qdrant_only(course_id=course_id, query=normalized_query, limit=limit)

        collection_name = self.collection_name(course_id)
        if not self._collection_exists(collection_name):
            return []

        provider_name, embedder = self._embedder()
        del provider_name
        graph_driver = neo4j_service.get_driver()
        if graph_driver is None:
            return self._search_qdrant_only(course_id=course_id, query=normalized_query, limit=limit)
        retriever = QdrantNeo4jRetriever(
            driver=graph_driver,
            client=self._qdrant(),
            collection_name=collection_name,
            embedder=embedder,
            id_property_neo4j="external_id",
            id_property_external="external_id",
            node_label_neo4j=COURSE_DOCUMENT_LABEL,
            result_formatter=self._format_retriever_record,
            retrieval_query=self._retrieval_query(),
        )
        try:
            retriever_result = retriever.search(query_text=normalized_query, top_k=max(limit * 2, 8))
            parsed_hits = self._parse_items(list(retriever_result.items))
        except Exception as error:
            logger.warning("官方 GraphRAG 检索失败，回退 Qdrant 本地检索: course=%s error=%s", course_id, error)
            parsed_hits = self._search_qdrant_only(course_id=course_id, query=normalized_query, limit=max(limit * 2, 8))

        boosted_seed_ids = set(seed_point_ids or [])
        reranked_hits = sorted(
            parsed_hits,
            key=lambda hit: (
                -(
                    hit.score
                    + (2.5 if boosted_seed_ids & set(hit.point_ids) else 0.0)
                    + (0.4 if hit.kind == "knowledge_point" else 0.0)
                ),
                hit.title,
            ),
        )
        return reranked_hits[:limit]

    def search_points(self, *, course_id: int, query: str, limit: int = 8) -> list[dict[str, object]]:
        """将文档级命中聚合成知识点级候选集合。"""
        aggregated_scores: defaultdict[int, float] = defaultdict(float)
        source_titles: defaultdict[int, list[str]] = defaultdict(list)
        prerequisite_map: dict[int, list[SourcePayload]] = defaultdict(list)
        postrequisite_map: dict[int, list[SourcePayload]] = defaultdict(list)

        for rank, hit in enumerate(self.search_documents(course_id=course_id, query=query, limit=max(limit * 2, 8)), start=1):
            point_entries = [entry for entry in hit.matched_points if isinstance(entry.get("point_id"), int)]
            if not point_entries:
                point_entries = [
                    {"point_id": point_id, "point_name": ""}
                    for point_id in hit.point_ids
                ]

            rank_bonus = 1.0 / rank
            for point_entry in point_entries:
                point_id = point_entry.get("point_id")
                if not isinstance(point_id, int):
                    continue
                aggregated_scores[point_id] += hit.score + rank_bonus
                if hit.title and hit.title not in source_titles[point_id]:
                    source_titles[point_id].append(hit.title)
                prerequisite_map.setdefault(point_id, [])
                postrequisite_map.setdefault(point_id, [])
                for prerequisite in hit.prerequisites:
                    if prerequisite not in prerequisite_map[point_id]:
                        prerequisite_map[point_id].append(prerequisite)
                for postrequisite in hit.postrequisites:
                    if postrequisite not in postrequisite_map[point_id]:
                        postrequisite_map[point_id].append(postrequisite)

        ordered_point_ids = [
            point_id
            for point_id, _ in sorted(aggregated_scores.items(), key=lambda item: (-item[1], item[0]))[:limit]
        ]
        return [
            {
                "point_id": point_id,
                "graph_rag_score": round(aggregated_scores[point_id], 6),
                "source_titles": source_titles.get(point_id, [])[:4],
                "prerequisites": prerequisite_map.get(point_id, [])[:4],
                "postrequisites": postrequisite_map.get(point_id, [])[:4],
            }
            for point_id in ordered_point_ids
        ]

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

    def _graph_record_formatter(self, record: object) -> RetrieverResultItem:
        """把结构化 Cypher 结果转换为统一的检索条目。"""
        get_value = getattr(record, "get")
        item_type = _coerce_string(get_value("item_type")) or "graph_query"
        point_id = _coerce_int(get_value("point_id"), default=0)
        point_name = _coerce_string(get_value("point_name")) or "当前知识点"
        relation_type = _coerce_string(get_value("relation_type")) or item_type.upper()
        related_point_id = _coerce_int(get_value("related_point_id"), default=0)
        related_point_name = _coerce_string(get_value("related_point_name"))
        source_title = _coerce_string(get_value("source_title"))
        source_excerpt = _coerce_string(get_value("source_excerpt"))
        reasoning = _coerce_string(get_value("reasoning"))

        if item_type == "prerequisite" and related_point_name:
            content = f"{point_name} 的前置知识包括：{related_point_name}。"
        elif item_type == "postrequisite" and related_point_name:
            content = f"学完 {point_name} 后可继续学习：{related_point_name}。"
        elif item_type == "resource" and source_title:
            content = f"{point_name} 的课程证据：{source_title}。{source_excerpt}"
        elif related_point_name:
            content = f"{point_name} 与 {related_point_name} 存在 {relation_type} 关系。"
        else:
            content = reasoning or point_name

        return RetrieverResultItem(
            content=_compact_excerpt(content),
            metadata={
                "item_type": item_type,
                "point_id": point_id,
                "point_name": point_name,
                "relation_type": relation_type,
                "related_point_id": related_point_id,
                "related_point_name": related_point_name,
                "source_title": source_title,
                "source_excerpt": source_excerpt,
                "reasoning": reasoning,
                "retrieval_source": "text2cypher",
            },
        )

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

    def _graph_tools_system_instruction(self) -> str:
        """定义 ToolsRetriever 的系统路由指令。"""
        return (
            "你负责为课程 GraphRAG 选择检索工具。"
            "涉及前置知识、后续知识、依赖关系、学习顺序、图谱链路的问题优先选择 graph_structure_query。"
            "涉及概念解释、资源、证据补充、例题、学习建议的问题优先选择 semantic_course_search。"
            "如果问题同时包含结构关系与解释需求，可以同时选择两个工具。"
        )

    def _tool_line(self, item: RetrieverResultItem) -> str:
        """把工具检索条目转换为简洁的上下文短句。"""
        metadata = item.metadata if isinstance(item.metadata, dict) else {}
        tool_name = _coerce_string(metadata.get("tool"))
        if tool_name == "graph_structure_query" or _coerce_string(metadata.get("retrieval_source")) == "text2cypher":
            item_type = _coerce_string(metadata.get("item_type"))
            point_name = _coerce_string(metadata.get("point_name")) or "当前知识点"
            related_point_name = _coerce_string(metadata.get("related_point_name"))
            source_title = _coerce_string(metadata.get("source_title"))
            source_excerpt = _coerce_string(metadata.get("source_excerpt"))
            if item_type == "prerequisite" and related_point_name:
                return f"{point_name} 的前置知识：{related_point_name}"
            if item_type == "postrequisite" and related_point_name:
                return f"{point_name} 的后续知识：{related_point_name}"
            if item_type == "resource" and source_title:
                return f"{point_name} 的课程证据：{source_title}：{source_excerpt}"
            if related_point_name:
                return f"{point_name} 与 {related_point_name} 存在图关系。"
        title = _coerce_string(metadata.get("title")) or "课程证据"
        excerpt = _coerce_string(metadata.get("excerpt")) or _coerce_string(item.content)
        return f"{title}：{excerpt}"

    def _tool_source(self, item: RetrieverResultItem) -> dict[str, object]:
        """将 ToolsRetriever item 收敛为统一证据结构。"""
        metadata = item.metadata if isinstance(item.metadata, dict) else {}
        tool_name = _coerce_string(metadata.get("tool"))
        retrieval_source = _coerce_string(metadata.get("retrieval_source"))
        if tool_name == "graph_structure_query" or retrieval_source == "text2cypher":
            point_id = _coerce_int(metadata.get("point_id"), default=0)
            related_point_id = _coerce_int(metadata.get("related_point_id"), default=0)
            source_title = _coerce_string(metadata.get("source_title"))
            point_name = _coerce_string(metadata.get("point_name")) or "图关系查询"
            return {
                "id": f"cypher:{point_id}:{related_point_id}:{_coerce_string(metadata.get('item_type')) or 'graph'}",
                "title": source_title or f"{point_name} · 图关系",
                "kind": "graph_query",
                "url": "",
                "excerpt": _compact_excerpt(self._tool_line(item)),
                "query_mode": GRAPH_TOOL_QUERY_MODE,
                "retrieval_source": retrieval_source or "text2cypher",
            }
        return {
            "id": _coerce_string(metadata.get("external_id")) or _coerce_string(metadata.get("doc_id")) or md5(str(item.content).encode("utf-8")).hexdigest(),
            "title": _coerce_string(metadata.get("title")) or "课程证据",
            "kind": _coerce_string(metadata.get("kind")) or "document",
            "url": _coerce_string(metadata.get("url")),
            "excerpt": _coerce_string(metadata.get("excerpt")) or _compact_excerpt(_coerce_string(item.content)),
            "query_mode": GRAPH_TOOL_QUERY_MODE,
            "retrieval_source": retrieval_source or COURSE_RETRIEVAL_MODE,
        }

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
            return GraphQueryContext(
                context="",
                sources=[],
                tools_selected=[],
                generated_cypher="",
                query_modes=[],
                matched_point_ids=[],
                mode=COURSE_RETRIEVAL_MODE,
            ).as_dict()

        seed_point_ids = [focus_point_id] if isinstance(focus_point_id, int) and focus_point_id > 0 else []
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

        if graph_driver is None:
            semantic_only = self._semantic_tool_result(
                course_id=course_id,
                query_text=normalized_query,
                seed_point_ids=seed_point_ids,
                limit=limit,
            )
            semantic_sources = [
                self._tool_source(item)
                for item in semantic_only.items
            ]
            semantic_lines = _dedupe_strings(
                [self._tool_line(item) for item in semantic_only.items if self._tool_line(item)]
            )
            return GraphQueryContext(
                context=("语义证据：\n- " + "\n- ".join(semantic_lines[:5])) if semantic_lines else "",
                sources=semantic_sources[:6],
                tools_selected=["semantic_course_search"] if semantic_sources else [],
                generated_cypher="",
                query_modes=[GRAPH_TOOL_QUERY_MODE] if semantic_sources else [],
                matched_point_ids=seed_point_ids,
                mode=COURSE_RETRIEVAL_MODE,
            ).as_dict()

        resolved_graph_driver = cast(Driver, graph_driver)
        tools_retriever = ToolsRetriever(
            driver=resolved_graph_driver,
            llm=FacadeGraphRAGLLM(),
            tools=available_tools,
            system_instruction=self._graph_tools_system_instruction(),
        )
        tool_result = tools_retriever.search(query_text=normalized_query)

        generated_cypher = ""
        semantic_lines: list[str] = []
        graph_lines: list[str] = []
        sources: list[dict[str, object]] = []
        matched_point_ids: list[int] = []
        seen_source_ids: set[str] = set()
        for item in tool_result.items:
            metadata = item.metadata if isinstance(item.metadata, dict) else {}
            generated_cypher = generated_cypher or _coerce_string(metadata.get("generated_cypher"))
            source = self._tool_source(item)
            source_id = _coerce_string(source.get("id"))
            if source_id and source_id not in seen_source_ids:
                seen_source_ids.add(source_id)
                sources.append(source)

            line = self._tool_line(item)
            if not line:
                continue
            if _coerce_string(metadata.get("retrieval_source")) == "text2cypher" or _coerce_string(metadata.get("tool")) == "graph_structure_query":
                graph_lines.append(line)
            else:
                semantic_lines.append(line)

            matched_point_ids.extend(_coerce_int_list(metadata.get("point_ids") or []))
            matched_point_ids.append(_coerce_int(metadata.get("point_id"), default=0))
            matched_point_ids.append(_coerce_int(metadata.get("related_point_id"), default=0))

        context_sections: list[str] = []
        deduped_graph_lines = _dedupe_strings(graph_lines)
        deduped_semantic_lines = _dedupe_strings(semantic_lines)
        if deduped_graph_lines:
            context_sections.append("结构化图查询：\n- " + "\n- ".join(deduped_graph_lines[:6]))
        if deduped_semantic_lines:
            context_sections.append("语义证据补充：\n- " + "\n- ".join(deduped_semantic_lines[:5]))

        tools_selected = []
        raw_tools_selected = tool_result.metadata.get("tools_selected") if isinstance(tool_result.metadata, dict) else None
        if isinstance(raw_tools_selected, list):
            tools_selected = [
                _coerce_string(tool_name)
                for tool_name in raw_tools_selected
                if _coerce_string(tool_name)
            ]

        return GraphQueryContext(
            context="\n\n".join(context_sections),
            sources=sources[:8],
            tools_selected=tools_selected,
            generated_cypher=generated_cypher,
            query_modes=[GRAPH_TOOL_QUERY_MODE] if sources else [],
            matched_point_ids=sorted({point_id for point_id in matched_point_ids if point_id > 0}),
            mode=GRAPH_QUERY_RETRIEVAL_MODE if sources else COURSE_RETRIEVAL_MODE,
        ).as_dict()


student_graphrag_runtime = CourseGraphRAGRuntime()
