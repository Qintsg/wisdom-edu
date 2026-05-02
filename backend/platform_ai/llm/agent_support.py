from __future__ import annotations

import json
import logging
import re
from typing import Any

from courses.models import Course
from knowledge.models import KnowledgePoint


logger = logging.getLogger(__name__)

JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def parse_json_payload(content: str) -> dict[str, Any]:
    """Best-effort JSON extraction for agent replies that contain extra wrapping."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    for match in JSON_BLOCK_RE.findall(content or ""):
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    start = (content or "").find("{")
    end = (content or "").rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(content[start : end + 1])
        except json.JSONDecodeError:
            pass
    return {}


def trim_graph_sources(raw_sources: object, limit: int = 4) -> list[dict[str, object]]:
    """Normalize GraphRAG sources into a compact JSON-safe payload for agent tools."""
    if not isinstance(raw_sources, list):
        return []

    normalized_sources: list[dict[str, object]] = []
    for item in raw_sources:
        if not isinstance(item, dict):
            continue
        normalized_sources.append(
            {
                "id": str(item.get("id", "")).strip(),
                "title": str(item.get("title", "")).strip() or "课程证据",
                "kind": str(item.get("kind", "")).strip() or "document",
                "excerpt": str(item.get("excerpt", "")).strip(),
                "query_mode": str(item.get("query_mode", "")).strip(),
                "retrieval_source": str(item.get("retrieval_source", "")).strip(),
            }
        )
        if len(normalized_sources) >= limit:
            break
    return normalized_sources


def build_point_graphrag_payload(course_id: int, point: KnowledgePoint) -> dict[str, object]:
    """Fetch a compact GraphRAG summary for a single knowledge point."""
    try:
        from platform_ai.rag.student import student_learning_rag

        payload = student_learning_rag.build_point_support_payload(
            course_id=course_id,
            point=point,
        )
    except Exception as exc:
        logger.warning(
            "LangChain agent point GraphRAG support failed: course=%s point=%s error=%s",
            course_id,
            point.id,
            exc,
        )
        return {}

    generated_summary = str(payload.get("summary", "")).strip()
    if not generated_summary and not payload.get("sources"):
        return {}

    return {
        "summary": generated_summary,
        "mode": str(payload.get("mode", "")).strip() or "graph_rag",
        "sources": trim_graph_sources(payload.get("sources"), limit=3),
    }


def build_course_graphrag_payload(
    *,
    course_id: int,
    query: str,
    point_id: int | None = None,
    limit: int = 4,
) -> dict[str, object]:
    """Query GraphRAG on demand so the agent can ground course-specific answers."""
    normalized_query = query.strip()
    point_name = ""
    if point_id:
        point = KnowledgePoint.objects.filter(id=point_id, course_id=course_id).first()
        if point:
            point_name = point.name

    if not normalized_query:
        return {
            "course_id": course_id,
            "point_id": point_id,
            "point_name": point_name,
            "query": "",
            "mode": "",
            "query_modes": [],
            "tools_selected": [],
            "generated_cypher": "",
            "context": "",
            "sources": [],
            "matched_point_ids": [],
        }

    try:
        from platform_ai.rag.runtime import student_graphrag_runtime

        payload = student_graphrag_runtime.query_graph(
            course_id=course_id,
            query=normalized_query,
            focus_point_id=point_id,
            focus_point_name=point_name,
            limit=max(limit, 3),
        )
    except Exception as exc:
        logger.warning(
            "LangChain agent course GraphRAG query failed: course=%s point=%s error=%s",
            course_id,
            point_id,
            exc,
        )
        payload = {}

    raw_modes = payload.get("query_modes") if isinstance(payload, dict) else []
    raw_tools = payload.get("tools_selected") if isinstance(payload, dict) else []
    raw_points = payload.get("matched_point_ids") if isinstance(payload, dict) else []
    return {
        "course_id": course_id,
        "point_id": point_id,
        "point_name": point_name,
        "query": normalized_query,
        "mode": str(payload.get("mode", "")).strip() if isinstance(payload, dict) else "",
        "query_modes": [str(mode).strip() for mode in raw_modes if str(mode).strip()] if isinstance(raw_modes, list) else [],
        "tools_selected": [str(tool_name).strip() for tool_name in raw_tools if str(tool_name).strip()] if isinstance(raw_tools, list) else [],
        "generated_cypher": str(payload.get("generated_cypher", "")).strip() if isinstance(payload, dict) else "",
        "context": str(payload.get("context", "")).strip() if isinstance(payload, dict) else "",
        "sources": trim_graph_sources(payload.get("sources") if isinstance(payload, dict) else [], limit=limit),
        "matched_point_ids": [point_pk for point_pk in raw_points if isinstance(point_pk, int) and point_pk > 0] if isinstance(raw_points, list) else [],
    }


def build_lookup_course_context_payload(course_id: int, point_id: int | None = None) -> dict[str, object]:
    """Look up course and optional knowledge point context."""
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return {"message": "课程不存在"}
    if not point_id:
        return {"course_id": course.id, "course_name": course.name}

    point = KnowledgePoint.objects.filter(id=point_id, course_id=course_id).first()
    if not point:
        return {
            "course_id": course.id,
            "course_name": course.name,
            "point_missing": True,
        }
    payload: dict[str, object] = {
        "course_id": course.id,
        "course_name": course.name,
        "point_id": point.id,
        "point_name": point.name,
        "description": point.description or "",
        "chapter": point.chapter or "",
    }
    graph_support = build_point_graphrag_payload(course_id=course_id, point=point)
    if graph_support:
        payload["graph_rag"] = graph_support
    return payload


def extract_agent_message_text(messages: object) -> str:
    """从 agent 调用返回中提取最终消息文本。"""
    if not isinstance(messages, list) or not messages:
        return ""
    last_message = messages[-1]
    content = getattr(last_message, "content", "") or ""
    if not isinstance(content, list):
        return str(content)

    parts: list[str] = []
    for item in content:
        if isinstance(item, dict) and item.get("text"):
            parts.append(item["text"])
        elif isinstance(item, str):
            parts.append(item)
    return "\n".join(parts)
