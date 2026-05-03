from __future__ import annotations

from typing import cast

from common.utils import build_normalized_score_map
from knowledge.models import KnowledgeMastery, KnowledgePoint
from learning.models import PathNode
from users.models import User

# 维护意图：将请求中的用户对象收窄为项目内 User 类型。
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def _get_authenticated_user(request) -> User:
    """
    将请求中的用户对象收窄为项目内 User 类型。
    :param request: DRF 请求对象。
    :return: 已认证用户。
    """
    return cast(User, request.user)


# 维护意图：将 JSONField 中的资源 ID 值规整为字符串列表。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _coerce_string_list(raw_value: object) -> list[str]:
    """
    将 JSONField 中的资源 ID 值规整为字符串列表。
    :param raw_value: 原始 JSONField 值。
    :return: 字符串 ID 列表。
    """
    if not isinstance(raw_value, list):
        return []
    return [str(item) for item in raw_value]


# 维护意图：生成仪表盘节点预览的排序键，优先展示未完成节点。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _path_node_sort_key(node: PathNode) -> tuple[int, int, int]:
    """
    生成仪表盘节点预览的排序键，优先展示未完成节点。
    :param node: 路径节点对象。
    :return: 排序键元组。
    """
    completion_rank = 1 if node.status == "completed" else 0
    return (completion_rank, node.order_index, node.id)


# 维护意图：截取题干摘要供 LLM 选题使用。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _clean_text_for_llm(text: str, max_len: int = 80) -> str:
    """
    截取题干摘要供 LLM 选题使用。
    :param text: 原始题干文本。
    :param max_len: 最大截断长度。
    :return: 清洗后的短文本。
    """
    if not text:
        return ""
    import re
    from django.utils.html import strip_tags

    cleaned_text = strip_tags(str(text)).strip()
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    return cleaned_text[:max_len]


# 维护意图：构建试卷题目分值映射。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_exam_score_map(exam, exam_questions):
    """
    构建试卷题目分值映射。
    :param exam: 考试对象。
    :param exam_questions: 试卷题目关联列表。
    :return: 归一化后的分值映射。
    """
    return build_normalized_score_map(
        [
            (eq.question_id, float(eq.score or getattr(eq.question, "score", 0) or 0))
            for eq in exam_questions
        ],
        target_total_score=float(exam.total_score or 0),
    )


# 维护意图：统一序列化学习路径节点。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _serialize_path_nodes(path, max_visible_order: int | None = None) -> list[dict[str, object]]:
    """
    统一序列化学习路径节点。
    :param path: 学习路径对象。
    :return: 节点序列化结果列表。
    """

    query = path.nodes.select_related("knowledge_point").prefetch_related("resources")
    if max_visible_order is not None:
        query = query.filter(order_index__lte=max_visible_order)
    ordered_nodes = list(query.order_by("order_index", "id"))
    return [
        {
            "node_id": node.id,
            "title": node.title,
            "goal": node.goal,
            "criterion": node.criterion,
            "status": node.status,
            "suggestion": node.suggestion,
            "node_type": node.node_type,
            "estimated_minutes": node.estimated_minutes,
            "knowledge_point_id": node.knowledge_point_id,
            "knowledge_point_name": node.knowledge_point.name
            if node.knowledge_point
            else None,
            "tasks_count": len(node.resources.all()) + (1 if node.exam else 0),
            "order_index": node.order_index,
        }
        for node in ordered_nodes
    ]


# 维护意图：读取指定知识点的当前掌握度快照。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _snapshot_mastery_for_points(
    user, course_id: int, point_ids: list[int]
) -> dict[int, float]:
    """
    读取指定知识点的当前掌握度快照。
    :param user: 当前用户对象。
    :param course_id: 课程 ID。
    :param point_ids: 知识点 ID 列表。
    :return: 以知识点 ID 为键的掌握度映射。
    """

    if not point_ids:
        return {}
    return {
        row.knowledge_point_id: float(row.mastery_rate)
        for row in KnowledgeMastery.objects.filter(
            user=user,
            course_id=course_id,
            knowledge_point_id__in=point_ids,
        )
    }


# 维护意图：计算一组知识点掌握度的平均值。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _average_mastery(mastery_snapshot: dict[int, float]) -> float | None:
    """
    计算一组知识点掌握度的平均值。
    :param mastery_snapshot: 掌握度快照。
    :return: 平均掌握度，缺失时返回 None。
    """

    if not mastery_snapshot:
        return None
    values = list(mastery_snapshot.values())
    return round(sum(values) / len(values), 4)


# 维护意图：构建掌握度变化明细。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_mastery_change_payload(
    before_snapshot: dict[int, float], after_snapshot: dict[int, float]
) -> list[dict[str, object]]:
    """
    构建掌握度变化明细。
    :param before_snapshot: 调整前掌握度快照。
    :param after_snapshot: 调整后掌握度快照。
    :return: 掌握度变化列表。
    """

    point_ids = sorted(set(before_snapshot.keys()) | set(after_snapshot.keys()))
    point_name_map = {
        row.id: row.name for row in KnowledgePoint.objects.filter(id__in=point_ids)
    }
    mastery_changes: list[dict[str, object]] = []
    for point_id in point_ids:
        before_rate = round(float(before_snapshot.get(point_id, 0.0)), 4)
        after_rate = round(float(after_snapshot.get(point_id, before_rate)), 4)
        mastery_changes.append(
            {
                "knowledge_point_id": point_id,
                "knowledge_point_name": point_name_map.get(
                    point_id, f"知识点 {point_id}"
                ),
                "mastery_before": before_rate,
                "mastery_after": after_rate,
                "improvement": round(after_rate - before_rate, 4),
            }
        )
    return mastery_changes
