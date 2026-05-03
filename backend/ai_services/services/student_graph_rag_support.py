"""学生端 GraphRAG 检索和问答支撑逻辑。"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from django.db.models import Q

from common.neo4j_service import neo4j_service
from knowledge.models import KnowledgeMastery, KnowledgePoint
from platform_ai.llm import llm_facade
from platform_ai.rag import student_learning_rag
from platform_ai.rag.runtime import COURSE_RETRIEVAL_MODE, student_graphrag_runtime


logger = logging.getLogger(__name__)

GRAPH_STRUCTURE_KEYWORDS: tuple[str, ...] = (
    "关系",
    "联系",
    "区别",
    "差异",
    "依赖",
    "先修",
    "前置",
    "后续",
    "顺序",
    "路径",
    "链路",
    "关联",
)


# 维护意图：Graph search result item
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class PointSearchItem:
    """Graph search result item."""

    point_id: int
    point_name: str
    chapter: str
    description: str
    mastery_rate: float
    prerequisites: list[str]
    postrequisites: list[str]

    # 维护意图：Convert the search item into a response payload
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def to_dict(self) -> dict[str, object]:
        """Convert the search item into a response payload."""
        return {
            "point_id": self.point_id,
            "point_name": self.point_name,
            "chapter": self.chapter,
            "description": self.description,
            "mastery_rate": self.mastery_rate,
            "prerequisites": self.prerequisites,
            "postrequisites": self.postrequisites,
        }


# 维护意图：Normalize free-form text for stable in-question point-name matching
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_match_text(text: str) -> str:
    """Normalize free-form text for stable in-question point-name matching."""
    lowered_text = text.strip().lower()
    return re.sub(r"[\W_]+", "", lowered_text, flags=re.UNICODE)


# 维护意图：Detect whether the question is mainly about graph structure or relations
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def is_graph_structure_question(question: str) -> bool:
    """Detect whether the question is mainly about graph structure or relations."""
    normalized_question = question.strip()
    return any(keyword in normalized_question for keyword in GRAPH_STRUCTURE_KEYWORDS)


# 维护意图：Resolve explicit course knowledge points directly mentioned in a question
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def match_points_by_query_text(*, course_id: int, query: str, limit: int = 3) -> list[KnowledgePoint]:
    """Resolve explicit course knowledge points directly mentioned in a question."""
    normalized_query = normalize_match_text(query)
    if not normalized_query:
        return []

    ranked_points: list[tuple[int, int, int, KnowledgePoint]] = []
    point_queryset = KnowledgePoint.objects.filter(course_id=course_id, is_published=True).only("id", "name", "order")
    for point in point_queryset:
        normalized_name = normalize_match_text(point.name)
        if len(normalized_name) < 2 or normalized_name not in normalized_query:
            continue
        ranked_points.append((-len(normalized_name), int(getattr(point, "order", 0) or 0), int(point.id), point))

    ranked_points.sort(key=lambda item: (item[0], item[1], item[2]))
    return unique_ranked_points(ranked_points, limit)


# 维护意图：按排序结果去重知识点并限制数量
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def unique_ranked_points(ranked_points: list[tuple[int, int, int, KnowledgePoint]], limit: int) -> list[KnowledgePoint]:
    """按排序结果去重知识点并限制数量。"""
    matched_points: list[KnowledgePoint] = []
    seen_ids: set[int] = set()
    for _, _, point_id, point in ranked_points:
        if point_id in seen_ids:
            continue
        seen_ids.add(point_id)
        matched_points.append(point)
        if len(matched_points) >= limit:
            break
    return matched_points


# 维护意图：Pick the first existing published point from a candidate ID list
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_point_from_ids(*, course_id: int, point_ids: list[int]) -> KnowledgePoint | None:
    """Pick the first existing published point from a candidate ID list."""
    normalized_ids = [point_id for point_id in point_ids if point_id > 0]
    if not normalized_ids:
        return None

    point_map = {
        int(point.id): point
        for point in KnowledgePoint.objects.filter(course_id=course_id, is_published=True, id__in=normalized_ids)
    }
    for point_id in normalized_ids:
        matched_point = point_map.get(point_id)
        if matched_point is not None:
            return matched_point
    return None


# 维护意图：Normalize a response field into a compact string list
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_text_list(payload: Mapping[str, object], field: str) -> list[str]:
    """Normalize a response field into a compact string list."""
    raw_items = payload.get(field)
    if not isinstance(raw_items, list):
        return []
    return [str(item).strip() for item in raw_items if str(item).strip()]


# 维护意图：Normalize matched point IDs from a course-level RAG payload
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_matched_point_ids(rag_result: Mapping[str, object] | None) -> list[int]:
    """Normalize matched point IDs from a course-level RAG payload."""
    if not isinstance(rag_result, Mapping):
        return []
    raw_point_ids = rag_result.get("matched_point_ids", [])
    if not isinstance(raw_point_ids, Iterable) or isinstance(raw_point_ids, (str, bytes, Mapping)):
        return []

    normalized_ids: list[int] = []
    for raw_point_id in raw_point_ids:
        point_id = coerce_positive_int(raw_point_id)
        if point_id is not None:
            normalized_ids.append(point_id)
    return normalized_ids


# 维护意图：将输入转换为正整数，布尔值和非法字符串视为无效
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def coerce_positive_int(value: object) -> int | None:
    """将输入转换为正整数，布尔值和非法字符串视为无效。"""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    value_text = str(value).strip()
    return int(value_text) if value_text.isdigit() else None


# 维护意图：Check whether the course-level RAG payload contains usable evidence
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def has_course_rag_result(rag_result: Mapping[str, object] | None) -> bool:
    """Check whether the course-level RAG payload contains usable evidence."""
    if not isinstance(rag_result, Mapping):
        return False
    raw_sources = rag_result.get("sources", [])
    return bool(raw_sources) or bool(extract_matched_point_ids(rag_result))


# 维护意图：Get the first matched point ID from a search payload when available
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_first_search_point_id(search_result: Mapping[str, object]) -> int | None:
    """Get the first matched point ID from a search payload when available."""
    raw_matches = search_result.get("matched_points", [])
    if not isinstance(raw_matches, list) or not raw_matches:
        return None

    first_match = raw_matches[0]
    if not isinstance(first_match, Mapping):
        return None
    return coerce_positive_int(first_match.get("point_id"))


# 维护意图：Convert RAG service output into the stable API response shape
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_graph_answer_payload(
    *,
    user,
    matched_point: KnowledgePoint | None,
    rag_result: dict[str, object],
) -> dict[str, object]:
    """Convert RAG service output into the stable API response shape."""
    search_item = build_search_item(user, matched_point) if matched_point is not None else None
    related_points = {
        "prerequisites": search_item.prerequisites if search_item is not None else [],
        "postrequisites": search_item.postrequisites if search_item is not None else [],
    }
    return {
        "reply": str(rag_result.get("answer", rag_result.get("reply", ""))).strip(),
        "sources": rag_result.get("sources", []),
        "mode": str(rag_result.get("mode", "")).strip() or "graph_rag",
        "query_modes": extract_text_list(rag_result, "query_modes"),
        "key_points": extract_text_list(rag_result, "key_points"),
        "matched_point": search_item.to_dict() if search_item is not None else None,
        "related_points": related_points,
    }


# 维护意图：Build a graph search item with relation summaries
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_search_item(user, point: KnowledgePoint) -> PointSearchItem:
    """Build a graph search item with relation summaries."""
    mastery_record = KnowledgeMastery.objects.filter(
        user=user,
        course_id=point.course_id,
        knowledge_point_id=point.id,
    ).first()
    mastery_rate = float(mastery_record.mastery_rate) if mastery_record else 0.0
    prerequisites, postrequisites = neo4j_relation_names(point.id)

    return PointSearchItem(
        point_id=point.id,
        point_name=point.name,
        chapter=point.chapter or "未分章",
        description=(point.introduction or point.description or "")[:180],
        mastery_rate=mastery_rate,
        prerequisites=prerequisites,
        postrequisites=postrequisites,
    )


# 维护意图：读取 Neo4j 中的前置和后续知识点名称
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def neo4j_relation_names(point_id: int) -> tuple[list[str], list[str]]:
    """读取 Neo4j 中的前置和后续知识点名称。"""
    if not neo4j_service.is_available:
        return [], []
    neo4j_point = neo4j_service.get_knowledge_point_neo4j(point_id)
    if not neo4j_point:
        return [], []
    return (
        relation_point_names(neo4j_point.get("prerequisites", [])),
        relation_point_names(neo4j_point.get("postrequisites", [])),
    )


# 维护意图：从图关系载荷中提取最多 4 个知识点名称
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def relation_point_names(raw_relations: object) -> list[str]:
    """从图关系载荷中提取最多 4 个知识点名称。"""
    if not isinstance(raw_relations, list):
        return []
    return [
        str(item.get("point_name", "")).strip()
        for item in raw_relations
        if isinstance(item, Mapping) and str(item.get("point_name", "")).strip()
    ][:4]


# 维护意图：Search knowledge points within the current course graph
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def search_graph_points(*, user, course_id: int, query: str, limit: int = 8) -> dict[str, object]:
    """Search knowledge points within the current course graph."""
    normalized_query = query.strip()
    if not normalized_query:
        return {"query": "", "matched_points": [], "retrieval_mode": "empty_query"}

    graph_rag_result = search_with_runtime(user=user, course_id=course_id, query=normalized_query, limit=limit)
    if graph_rag_result is not None:
        return graph_rag_result

    point_name_matches = match_points_by_query_text(course_id=course_id, query=normalized_query, limit=limit)
    if point_name_matches:
        return build_name_match_response(user=user, query=normalized_query, points=point_name_matches)
    return search_with_database_keyword(user=user, course_id=course_id, query=normalized_query, limit=limit)


# 维护意图：优先走 Neo4j GraphRAG + Qdrant 混合检索
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def search_with_runtime(*, user, course_id: int, query: str, limit: int) -> dict[str, object] | None:
    """优先走 Neo4j GraphRAG + Qdrant 混合检索。"""
    try:
        graph_rag_matches = student_graphrag_runtime.search_points(course_id=course_id, query=query, limit=limit)
    except Exception as error:
        logger.warning("GraphRAG 混合检索失败，回退课程内关键字检索: course=%s error=%s", course_id, error)
        graph_rag_matches = []

    if not graph_rag_matches:
        return None
    matched_points = build_runtime_matched_points(user=user, course_id=course_id, graph_rag_matches=graph_rag_matches)
    if not matched_points:
        return None
    return {"query": query, "matched_points": matched_points, "retrieval_mode": COURSE_RETRIEVAL_MODE}


# 维护意图：将运行时 GraphRAG 命中转换为搜索响应项
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_runtime_matched_points(
    *,
    user,
    course_id: int,
    graph_rag_matches: list[dict[str, object]],
) -> list[dict[str, object]]:
    """将运行时 GraphRAG 命中转换为搜索响应项。"""
    point_ids = [point_id for point_id in (coerce_positive_int(item.get("point_id")) for item in graph_rag_matches) if point_id]
    point_map = {
        getattr(point, "id", 0): point
        for point in KnowledgePoint.objects.filter(course_id=course_id, is_published=True, id__in=point_ids)
    }
    matched_points = []
    for match in graph_rag_matches:
        point_id = coerce_positive_int(match.get("point_id"))
        point = point_map.get(point_id) if point_id is not None else None
        if point is None:
            continue
        matched_points.append(build_runtime_match_item(user, point, match))
    return matched_points


# 维护意图：补齐运行时 GraphRAG 命中的分数、来源和图关系
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_runtime_match_item(user, point: KnowledgePoint, match: Mapping[str, object]) -> dict[str, object]:
    """补齐运行时 GraphRAG 命中的分数、来源和图关系。"""
    item = build_search_item(user, point).to_dict()
    item["graph_rag_score"] = float(match.get("graph_rag_score", 0.0))
    item["supporting_sources"] = [str(title).strip() for title in match.get("source_titles", []) if str(title).strip()]
    if not item["prerequisites"]:
        item["prerequisites"] = relation_point_names(match.get("prerequisites", []))
    if not item["postrequisites"]:
        item["postrequisites"] = relation_point_names(match.get("postrequisites", []))
    return item


# 维护意图：组装显式知识点名称命中的搜索响应
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_name_match_response(*, user, query: str, points: list[KnowledgePoint]) -> dict[str, object]:
    """组装显式知识点名称命中的搜索响应。"""
    return {
        "query": query,
        "matched_points": [build_search_item(user, point).to_dict() for point in points],
        "retrieval_mode": "name_match",
    }


# 维护意图：使用课程内数据库关键词匹配兜底搜索
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def search_with_database_keyword(*, user, course_id: int, query: str, limit: int) -> dict[str, object]:
    """使用课程内数据库关键词匹配兜底搜索。"""
    point_queryset = (
        KnowledgePoint.objects.filter(course_id=course_id, is_published=True)
        .filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(introduction__icontains=query)
            | Q(tags__icontains=query)
        )
        .order_by("order", "id")[:limit]
    )
    matched_points = [build_search_item(user, point).to_dict() for point in point_queryset]
    return {
        "query": query,
        "matched_points": matched_points,
        "retrieval_mode": "graph_search" if matched_points else "no_match",
    }


# 维护意图：Run GraphRAG question answering under the current course context
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def answer_graph_question(
    *,
    user,
    course_id: int,
    question: str,
    point_id: int | None = None,
) -> dict[str, object]:
    """Run GraphRAG question answering under the current course context."""
    matched_point = point_from_explicit_id(course_id=course_id, point_id=point_id)
    course_rag_result: dict[str, object] | None = None

    if matched_point is None:
        matched_point, course_rag_result, payload = answer_explicit_or_structure_question(
            user=user,
            course_id=course_id,
            question=question,
        )
        if payload is not None:
            return payload

    if matched_point is None:
        matched_point = point_from_search(user=user, course_id=course_id, question=question)

    if matched_point is not None:
        return answer_focused_point_question(user=user, course_id=course_id, point=matched_point, question=question)
    return answer_course_or_llm_fallback(user=user, course_id=course_id, question=question, course_rag_result=course_rag_result)


# 维护意图：按显式 point_id 查找当前课程内已发布知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def point_from_explicit_id(*, course_id: int, point_id: int | None) -> KnowledgePoint | None:
    """按显式 point_id 查找当前课程内已发布知识点。"""
    if point_id is None:
        return None
    return KnowledgePoint.objects.filter(id=point_id, course_id=course_id, is_published=True).first()


# 维护意图：显式多知识点或结构类问题优先走课程级 GraphRAG
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def answer_explicit_or_structure_question(
    *,
    user,
    course_id: int,
    question: str,
) -> tuple[KnowledgePoint | None, dict[str, object] | None, dict[str, object] | None]:
    """显式多知识点或结构类问题优先走课程级 GraphRAG。"""
    explicit_points = match_points_by_query_text(course_id=course_id, query=question, limit=3)
    if len(explicit_points) < 2 and not is_graph_structure_question(question):
        matched_point = explicit_points[0] if explicit_points else None
        return matched_point, None, None

    course_rag_response = student_learning_rag.answer_course_question(
        course_id=course_id,
        question=question,
        seed_point_ids=[int(point.id) for point in explicit_points],
    )
    matched_point = explicit_points[0] if explicit_points else resolve_point_from_ids(
        course_id=course_id,
        point_ids=extract_matched_point_ids(course_rag_response),
    )
    if has_course_rag_result(course_rag_response):
        return matched_point, course_rag_response, build_graph_answer_payload(
            user=user,
            matched_point=matched_point,
            rag_result=course_rag_response,
        )
    return matched_point, course_rag_response, None


# 维护意图：通过搜索结果选择最可能的知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def point_from_search(*, user, course_id: int, question: str) -> KnowledgePoint | None:
    """通过搜索结果选择最可能的知识点。"""
    search_result = search_graph_points(user=user, course_id=course_id, query=question, limit=1)
    best_point_id = extract_first_search_point_id(search_result)
    if best_point_id is None:
        return None
    return KnowledgePoint.objects.filter(id=best_point_id, course_id=course_id, is_published=True).first()


# 维护意图：围绕已定位知识点执行 GraphRAG 问答
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def answer_focused_point_question(*, user, course_id: int, point: KnowledgePoint, question: str) -> dict[str, object]:
    """围绕已定位知识点执行 GraphRAG 问答。"""
    rag_result = student_learning_rag.answer_graph_question(course_id=course_id, point=point, question=question)
    return build_graph_answer_payload(user=user, matched_point=point, rag_result=rag_result)


# 维护意图：课程级 GraphRAG 无明确知识点时，按证据可用性决定是否 LLM 兜底
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def answer_course_or_llm_fallback(
    *,
    user,
    course_id: int,
    question: str,
    course_rag_result: dict[str, object] | None,
) -> dict[str, object]:
    """课程级 GraphRAG 无明确知识点时，按证据可用性决定是否 LLM 兜底。"""
    if course_rag_result is None:
        course_rag_result = student_learning_rag.answer_course_question(course_id=course_id, question=question)
    matched_point = resolve_point_from_ids(course_id=course_id, point_ids=extract_matched_point_ids(course_rag_result))
    if has_course_rag_result(course_rag_result):
        return build_graph_answer_payload(user=user, matched_point=matched_point, rag_result=course_rag_result)
    return build_llm_fallback(course_id=course_id, question=question)


# 维护意图：构造无图谱证据时的通用回答
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_llm_fallback(*, course_id: int, question: str) -> dict[str, object]:
    """构造无图谱证据时的通用回答。"""
    fallback = {
        "reply": f"当前问题是“{question}”。系统暂未在当前课程知识图谱中命中明确知识点，下面给出课程级通用学习建议。",
        "sources": [],
        "mode": "llm_fallback",
        "matched_point": None,
        "related_points": {"prerequisites": [], "postrequisites": []},
    }
    if not llm_facade.is_available:
        return fallback
    result = llm_facade.call_with_fallback(
        prompt=(
            "请以中文回答学生的问题，回答需要适用于教学场景，尽量给出下一步学习建议。"
            f"\n课程ID：{course_id}"
            f"\n问题：{question}"
        ),
        call_type="graph_rag_chat_fallback",
        fallback_response=fallback,
    )
    return {**fallback, "reply": result.get("reply", result.get("answer", fallback["reply"]))}
