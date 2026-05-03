"""LangChain agent 可调用的课程 GraphRAG 上下文工具。"""
from __future__ import annotations

import logging

from courses.models import Course
from knowledge.models import KnowledgePoint


logger = logging.getLogger(__name__)


# 维护意图：将 GraphRAG sources 规范化为紧凑、JSON 安全的工具载荷
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def trim_graph_sources(raw_sources: object, limit: int = 4) -> list[dict[str, object]]:
    """将 GraphRAG sources 规范化为紧凑、JSON 安全的工具载荷。"""
    if not isinstance(raw_sources, list):
        return []

    normalized_sources: list[dict[str, object]] = []
    for item in raw_sources:
        if isinstance(item, dict):
            normalized_sources.append(normalize_graph_source(item))
        if len(normalized_sources) >= limit:
            break
    return normalized_sources


# 维护意图：规范化单条 GraphRAG 证据来源
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_graph_source(item: dict[object, object]) -> dict[str, object]:
    """规范化单条 GraphRAG 证据来源。"""
    return {
        "id": clean_source_field(item, "id"),
        "title": clean_source_field(item, "title") or "课程证据",
        "kind": clean_source_field(item, "kind") or "document",
        "excerpt": clean_source_field(item, "excerpt"),
        "query_mode": clean_source_field(item, "query_mode"),
        "retrieval_source": clean_source_field(item, "retrieval_source"),
    }


# 维护意图：安全读取 source 字段并转为展示字符串
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def clean_source_field(item: dict[object, object], field_name: str) -> str:
    """安全读取 source 字段并转为展示字符串。"""
    return str(item.get(field_name, "")).strip()


# 维护意图：获取单个知识点的 GraphRAG 摘要
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_point_graphrag_payload(course_id: int, point: KnowledgePoint) -> dict[str, object]:
    """获取单个知识点的 GraphRAG 摘要。"""
    payload = fetch_point_support_payload(course_id=course_id, point=point)
    generated_summary = str(payload.get("summary", "")).strip()
    if not generated_summary and not payload.get("sources"):
        return {}
    return {
        "summary": generated_summary,
        "mode": str(payload.get("mode", "")).strip() or "graph_rag",
        "sources": trim_graph_sources(payload.get("sources"), limit=3),
    }


# 维护意图：调用学生学习 RAG 服务读取知识点证据，失败时降级为空载荷
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def fetch_point_support_payload(course_id: int, point: KnowledgePoint) -> dict[str, object]:
    """调用学生学习 RAG 服务读取知识点证据，失败时降级为空载荷。"""
    try:
        from platform_ai.rag.student import student_learning_rag

        payload = student_learning_rag.build_point_support_payload(
            course_id=course_id,
            point=point,
        )
        return payload if isinstance(payload, dict) else {}
    except Exception as exc:
        logger.warning(
            "LangChain agent point GraphRAG support failed: course=%s point=%s error=%s",
            course_id,
            point.id,
            exc,
        )
        return {}


# 维护意图：按需查询课程 GraphRAG，供 agent 基于课程证据生成结构化回答
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_graphrag_payload(
    *,
    course_id: int,
    query: str,
    point_id: int | None = None,
    limit: int = 4,
) -> dict[str, object]:
    """按需查询课程 GraphRAG，供 agent 基于课程证据生成结构化回答。"""
    normalized_query = query.strip()
    point_name = resolve_point_name(course_id, point_id)
    if not normalized_query:
        return empty_course_graphrag_payload(course_id, point_id, point_name)

    payload = query_course_graph(
        course_id=course_id,
        query=normalized_query,
        point_id=point_id,
        point_name=point_name,
        limit=limit,
    )
    return normalize_course_graphrag_payload(
        payload=payload,
        course_id=course_id,
        point_id=point_id,
        point_name=point_name,
        query=normalized_query,
        limit=limit,
    )


# 维护意图：解析当前聚焦知识点名称
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_point_name(course_id: int, point_id: int | None) -> str:
    """解析当前聚焦知识点名称。"""
    if not point_id:
        return ""
    point = KnowledgePoint.objects.filter(id=point_id, course_id=course_id).first()
    return point.name if point else ""


# 维护意图：返回空查询时的稳定响应结构
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def empty_course_graphrag_payload(
    course_id: int,
    point_id: int | None,
    point_name: str,
) -> dict[str, object]:
    """返回空查询时的稳定响应结构。"""
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


# 维护意图：调用课程 GraphRAG runtime，失败时返回空载荷保持 agent 可降级
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def query_course_graph(
    *,
    course_id: int,
    query: str,
    point_id: int | None,
    point_name: str,
    limit: int,
) -> dict[str, object]:
    """调用课程 GraphRAG runtime，失败时返回空载荷保持 agent 可降级。"""
    try:
        from platform_ai.rag.runtime import student_graphrag_runtime

        payload = student_graphrag_runtime.query_graph(
            course_id=course_id,
            query=query,
            focus_point_id=point_id,
            focus_point_name=point_name,
            limit=max(limit, 3),
        )
        return payload if isinstance(payload, dict) else {}
    except Exception as exc:
        logger.warning(
            "LangChain agent course GraphRAG query failed: course=%s point=%s error=%s",
            course_id,
            point_id,
            exc,
        )
        return {}


# 维护意图：将 runtime 返回的 GraphRAG 载荷压缩为 agent 工具响应
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_course_graphrag_payload(
    *,
    payload: dict[str, object],
    course_id: int,
    point_id: int | None,
    point_name: str,
    query: str,
    limit: int,
) -> dict[str, object]:
    """将 runtime 返回的 GraphRAG 载荷压缩为 agent 工具响应。"""
    return {
        "course_id": course_id,
        "point_id": point_id,
        "point_name": point_name,
        "query": query,
        "mode": clean_payload_text(payload, "mode"),
        "query_modes": clean_string_list(payload.get("query_modes")),
        "tools_selected": clean_string_list(payload.get("tools_selected")),
        "generated_cypher": clean_payload_text(payload, "generated_cypher"),
        "context": clean_payload_text(payload, "context"),
        "sources": trim_graph_sources(payload.get("sources"), limit=limit),
        "matched_point_ids": clean_positive_ids(payload.get("matched_point_ids")),
    }


# 维护意图：读取 runtime 文本字段并去除空白
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def clean_payload_text(payload: dict[str, object], field_name: str) -> str:
    """读取 runtime 文本字段并去除空白。"""
    return str(payload.get(field_name, "")).strip()


# 维护意图：规范化 runtime 返回的字符串列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def clean_string_list(raw_items: object) -> list[str]:
    """规范化 runtime 返回的字符串列表。"""
    if not isinstance(raw_items, list):
        return []
    return [cleaned for item in raw_items if (cleaned := str(item).strip())]


# 维护意图：只保留正整数知识点 ID
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def clean_positive_ids(raw_items: object) -> list[int]:
    """只保留正整数知识点 ID。"""
    if not isinstance(raw_items, list):
        return []
    return [item for item in raw_items if isinstance(item, int) and item > 0]


# 维护意图：查询课程和可选知识点上下文
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_lookup_course_context_payload(
    course_id: int,
    point_id: int | None = None,
) -> dict[str, object]:
    """查询课程和可选知识点上下文。"""
    course = Course.objects.filter(id=course_id).first()
    if not course:
        return {"message": "课程不存在"}
    if not point_id:
        return {"course_id": course.id, "course_name": course.name}

    point = KnowledgePoint.objects.filter(id=point_id, course_id=course_id).first()
    if not point:
        return build_missing_point_payload(course)
    return build_point_context_payload(course_id=course_id, course=course, point=point)


# 维护意图：构建课程存在但知识点缺失时的上下文响应
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_missing_point_payload(course: Course) -> dict[str, object]:
    """构建课程存在但知识点缺失时的上下文响应。"""
    return {
        "course_id": course.id,
        "course_name": course.name,
        "point_missing": True,
    }


# 维护意图：构建包含知识点摘要与 GraphRAG 摘要的课程上下文响应
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_point_context_payload(
    *,
    course_id: int,
    course: Course,
    point: KnowledgePoint,
) -> dict[str, object]:
    """构建包含知识点摘要与 GraphRAG 摘要的课程上下文响应。"""
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


__all__ = [
    "build_course_graphrag_payload",
    "build_lookup_course_context_payload",
    "build_point_graphrag_payload",
    "clean_positive_ids",
    "clean_string_list",
    "empty_course_graphrag_payload",
    "normalize_course_graphrag_payload",
    "trim_graph_sources",
]
