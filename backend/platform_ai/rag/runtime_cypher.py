"""GraphRAG Text2Cypher fallback query builders."""

from __future__ import annotations

import re

from platform_ai.rag.runtime_models import _coerce_int, _coerce_string, _escape_cypher_string


GRAPH_INTENT_KEYWORDS = {
    "prerequisite": ["前置", "先修", "先学", "基础"],
    "postrequisite": ["后续", "下一步", "之后", "延伸", "进阶"],
    "path": ["路径", "顺序", "链路", "关系", "联系", "关联"],
}


# 维护意图：从结构化提示中提取单行键值
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_line_value(prompt_text: str, key: str) -> str:
    """从结构化提示中提取单行键值。"""
    matched = re.search(rf"{re.escape(key)}\s*:\s*(.+)", prompt_text)
    return _coerce_string(matched.group(1)) if matched else ""


# 维护意图：从 Text2Cypher 自定义提示中提取用户问题
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def extract_user_question(prompt_text: str) -> str:
    """从 Text2Cypher 自定义提示中提取用户问题。"""
    matched = re.search(r"User question:\s*(.*?)\n\nRules:", prompt_text, re.S)
    if matched:
        return _coerce_string(matched.group(1))
    return _coerce_string(prompt_text)


# 维护意图：为启发式 Cypher 生成稳定的目标知识点匹配子句
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_target_match(
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


# 维护意图：构造前置知识点查询
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_prerequisite_query(target_match: str, course_id: int) -> str:
    """构造前置知识点查询。"""
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


# 维护意图：构造后续知识点查询
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_postrequisite_query(target_match: str, course_id: int) -> str:
    """构造后续知识点查询。"""
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


# 维护意图：构造局部知识链路查询
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_path_query(target_match: str, course_id: int) -> str:
    """构造局部知识链路查询。"""
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


# 维护意图：构造课程证据资源查询
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_resource_query(target_match: str, course_id: int) -> str:
    """构造课程证据资源查询。"""
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


# 维护意图：在无可用模型时，为 Text2CypherRetriever 生成启发式 Cypher
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def fallback_cypher_from_prompt(prompt_text: str) -> str:
    """在无可用模型时，为 Text2CypherRetriever 生成启发式 Cypher。"""
    course_id = _coerce_int(extract_line_value(prompt_text, "course_id"), default=0)
    focus_point_id = _coerce_int(extract_line_value(prompt_text, "focus_point_id"), default=0)
    focus_point_name = extract_line_value(prompt_text, "focus_point_name")
    question = extract_user_question(prompt_text)
    normalized_question = question.lower()
    target_match = build_target_match(
        course_id=course_id,
        focus_point_id=focus_point_id,
        focus_point_name=focus_point_name,
        question=question,
    )

    # Text2Cypher 不可用时仍保持“图谱优先、证据可追溯”的降级路径。
    if any(keyword in normalized_question for keyword in GRAPH_INTENT_KEYWORDS["prerequisite"]):
        return build_prerequisite_query(target_match, course_id)
    if any(keyword in normalized_question for keyword in GRAPH_INTENT_KEYWORDS["postrequisite"]):
        return build_postrequisite_query(target_match, course_id)
    if any(keyword in normalized_question for keyword in GRAPH_INTENT_KEYWORDS["path"]):
        return build_path_query(target_match, course_id)
    return build_resource_query(target_match, course_id)


__all__ = [
    "fallback_cypher_from_prompt",
]
