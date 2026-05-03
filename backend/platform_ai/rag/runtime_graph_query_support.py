from __future__ import annotations

from hashlib import md5

from neo4j_graphrag.types import RetrieverResultItem

from platform_ai.rag.runtime_models import (
    COURSE_RETRIEVAL_MODE,
    GRAPH_QUERY_RETRIEVAL_MODE,
    GRAPH_TOOL_QUERY_MODE,
    GraphQueryContext,
    _coerce_int,
    _coerce_int_list,
    _coerce_string,
    _compact_excerpt,
    _dedupe_strings,
)


# 维护意图：把结构化 Cypher 结果转换为统一的检索条目
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_graph_record_item(record: object) -> RetrieverResultItem:
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


# 维护意图：把工具检索条目转换为简洁的上下文短句
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_tool_line(item: RetrieverResultItem) -> str:
    """把工具检索条目转换为简洁的上下文短句。"""
    metadata = item.metadata if isinstance(item.metadata, dict) else {}
    tool_name = _coerce_string(metadata.get("tool"))
    retrieval_source = _coerce_string(metadata.get("retrieval_source"))
    if tool_name == "graph_structure_query" or retrieval_source == "text2cypher":
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


# 维护意图：将 ToolsRetriever item 收敛为统一证据结构
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_tool_source(item: RetrieverResultItem) -> dict[str, object]:
    """将 ToolsRetriever item 收敛为统一证据结构。"""
    metadata = item.metadata if isinstance(item.metadata, dict) else {}
    tool_name = _coerce_string(metadata.get("tool"))
    retrieval_source = _coerce_string(metadata.get("retrieval_source"))
    if tool_name == "graph_structure_query" or retrieval_source == "text2cypher":
        point_id = _coerce_int(metadata.get("point_id"), default=0)
        related_point_id = _coerce_int(metadata.get("related_point_id"), default=0)
        source_title = _coerce_string(metadata.get("source_title"))
        point_name = _coerce_string(metadata.get("point_name")) or "图关系查询"
        item_type = _coerce_string(metadata.get("item_type")) or "graph"
        return {
            "id": f"cypher:{point_id}:{related_point_id}:{item_type}",
            "title": source_title or f"{point_name} · 图关系",
            "kind": "graph_query",
            "url": "",
            "excerpt": _compact_excerpt(build_tool_line(item)),
            "query_mode": GRAPH_TOOL_QUERY_MODE,
            "retrieval_source": retrieval_source or "text2cypher",
        }
    external_id = _coerce_string(metadata.get("external_id"))
    doc_id = _coerce_string(metadata.get("doc_id"))
    title = _coerce_string(metadata.get("title")) or "课程证据"
    kind = _coerce_string(metadata.get("kind")) or "document"
    url = _coerce_string(metadata.get("url"))
    excerpt = _coerce_string(metadata.get("excerpt")) or _compact_excerpt(_coerce_string(item.content))
    fallback_id = md5(str(item.content).encode("utf-8")).hexdigest()
    return {
        "id": external_id or doc_id or fallback_id,
        "title": title,
        "kind": kind,
        "url": url,
        "excerpt": excerpt,
        "query_mode": GRAPH_TOOL_QUERY_MODE,
        "retrieval_source": retrieval_source or COURSE_RETRIEVAL_MODE,
    }


# 维护意图：返回空查询上下文
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_empty_query_context() -> dict[str, object]:
    """返回空查询上下文。"""
    return GraphQueryContext(
        context="",
        sources=[],
        tools_selected=[],
        generated_cypher="",
        query_modes=[],
        matched_point_ids=[],
        mode=COURSE_RETRIEVAL_MODE,
    ).as_dict()


# 维护意图：将纯语义检索结果转换为稳定业务载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_semantic_only_query_context(semantic_only, seed_point_ids: list[int]) -> dict[str, object]:
    """将纯语义检索结果转换为稳定业务载荷。"""
    semantic_sources = [build_tool_source(item) for item in semantic_only.items]
    semantic_lines = _dedupe_strings(
        [build_tool_line(item) for item in semantic_only.items if build_tool_line(item)]
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


# 维护意图：将 ToolsRetriever 返回聚合成统一 GraphQueryContext 业务结构
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_tools_query_context(tool_result) -> dict[str, object]:
    """将 ToolsRetriever 返回聚合成统一 GraphQueryContext 业务结构。"""
    generated_cypher = ""
    semantic_lines: list[str] = []
    graph_lines: list[str] = []
    sources: list[dict[str, object]] = []
    matched_point_ids: list[int] = []
    seen_source_ids: set[str] = set()

    for item in tool_result.items:
        metadata = item.metadata if isinstance(item.metadata, dict) else {}
        generated_cypher = generated_cypher or _coerce_string(metadata.get("generated_cypher"))
        source = build_tool_source(item)
        source_id = _coerce_string(source.get("id"))
        if source_id and source_id not in seen_source_ids:
            seen_source_ids.add(source_id)
            sources.append(source)

        line = build_tool_line(item)
        if not line:
            continue
        if _coerce_string(metadata.get("retrieval_source")) == "text2cypher" or _coerce_string(metadata.get("tool")) == "graph_structure_query":
            graph_lines.append(line)
        else:
            semantic_lines.append(line)

        item_point_ids = _coerce_int_list(metadata.get("point_ids") or [])
        item_point_id = _coerce_int(metadata.get("point_id"), default=0)
        related_point_id = _coerce_int(metadata.get("related_point_id"), default=0)
        matched_point_ids.extend(item_point_ids)
        matched_point_ids.append(item_point_id)
        matched_point_ids.append(related_point_id)

    context_sections: list[str] = []
    deduped_graph_lines = _dedupe_strings(graph_lines)
    deduped_semantic_lines = _dedupe_strings(semantic_lines)
    if deduped_graph_lines:
        context_sections.append("结构化图查询：\n- " + "\n- ".join(deduped_graph_lines[:6]))
    if deduped_semantic_lines:
        context_sections.append("语义证据补充：\n- " + "\n- ".join(deduped_semantic_lines[:5]))

    raw_tools_selected = tool_result.metadata.get("tools_selected") if isinstance(tool_result.metadata, dict) else None
    tools_selected = []
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
