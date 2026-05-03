from __future__ import annotations

from typing import Any, cast

from django.utils import timezone

from assessments.models import Question
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint, Resource
from learning.models import NodeProgress, PathNode
from users.models import User

# 维护意图：激活当前节点之后的下一个锁定节点。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _activate_next_locked_node(node: PathNode) -> None:
    """
    激活当前节点之后的下一个锁定节点。
    :param node: 当前学习路径节点。
    :return: None。
    """
    next_node = (
        PathNode.objects.filter(path=node.path, order_index__gt=node.order_index)
        .order_by("order_index", "id")
        .first()
    )
    if next_node and next_node.status == "locked":
        next_node.status = "active"
        next_node.save(update_fields=["status"])


# 维护意图：统一设置题目或资源的知识点关联，避免 ManyToMany 静态推断噪声。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _set_related_knowledge_points(target: Question | Resource, point: KnowledgePoint) -> None:
    """
    统一设置题目或资源的知识点关联，避免 ManyToMany 静态推断噪声。
    :param target: 题目或资源对象。
    :param point: 关联知识点。
    :return: None。
    """
    relation_manager = cast(Any, target.knowledge_points)
    relation_manager.set([point])


# 维护意图：获取题目关联的知识点列表，并为静态分析提供明确类型。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _question_knowledge_points(question: Question) -> list[KnowledgePoint]:
    """
    获取题目关联的知识点列表，并为静态分析提供明确类型。
    :param question: 题目对象。
    :return: 知识点列表。
    """
    relation_manager = cast(Any, question.knowledge_points)
    return [point for point in relation_manager.all() if isinstance(point, KnowledgePoint)]


# 维护意图：归一化题目选项，避免 JSONField 推断为 Any 时带来的类型噪声。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _question_options(question: Question) -> list[dict[str, object]]:
    """
    归一化题目选项，避免 JSONField 推断为 Any 时带来的类型噪声。
    :param question: 题目对象。
    :return: 仅包含字典项的选项列表。
    """
    if not isinstance(question.options, list):
        return []

    normalized_options: list[dict[str, object]] = []
    for option in question.options:
        if isinstance(option, dict):
            normalized_options.append(option)
    return normalized_options


# 维护意图：将任意对象收窄为字符串键字典。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _as_object_dict(raw_value: object) -> dict[str, object]:
    """
    将任意对象收窄为字符串键字典。
    :param raw_value: 原始值。
    :return: 字典；不满足时返回空字典。
    """
    return raw_value if isinstance(raw_value, dict) else {}


# 维护意图：规整阶段测试反馈中的掌握度映射。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _coerce_mastery_after_map(raw_value: object) -> dict[int, float]:
    """
    规整阶段测试反馈中的掌握度映射。
    :param raw_value: 原始掌握度映射对象。
    :return: 以知识点 ID 为键的浮点数字典。
    """
    mastery_after_map: dict[int, float] = {}
    if not isinstance(raw_value, dict):
        return mastery_after_map

    for raw_key, raw_item in raw_value.items():
        if isinstance(raw_key, int) and isinstance(raw_item, int | float):
            mastery_after_map[raw_key] = float(raw_item)
            continue
        if isinstance(raw_key, str) and raw_key.isdigit() and isinstance(raw_item, int | float):
            mastery_after_map[int(raw_key)] = float(raw_item)
    return mastery_after_map


# 维护意图：计算掌握度快照的平均值。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _average_snapshot(snapshot: dict[int, float]) -> float | None:
    """
    计算掌握度快照的平均值。
    :param snapshot: 掌握度快照。
    :return: 平均值；无数据时返回 None。
    """
    if not snapshot:
        return None
    return round(sum(snapshot.values()) / len(snapshot), 4)


# 维护意图：读取指定知识点的当前掌握度快照。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _capture_mastery_snapshot(
    course: Course,
    student: User,
    points: list[KnowledgePoint],
) -> dict[int, float]:
    """
    读取指定知识点的当前掌握度快照。
    :param course: 所属课程。
    :param student: 学生账号。
    :param points: 需要关注的知识点列表。
    :return: 以知识点 ID 为键的掌握度映射。
    """
    return {
        mastery.knowledge_point_id: float(mastery.mastery_rate)
        for mastery in KnowledgeMastery.objects.filter(
            user=student,
            course=course,
            knowledge_point__in=points,
        )
    }


# 维护意图：构建阶段测试前后的掌握度变化明细。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_mastery_change_payload(
    points: list[KnowledgePoint],
    mastery_before_snapshot: dict[int, float],
    mastery_after_snapshot: dict[int, float],
) -> list[dict[str, object]]:
    """
    构建阶段测试前后的掌握度变化明细。
    :param points: 参与测试的知识点列表。
    :param mastery_before_snapshot: 测试前掌握度快照。
    :param mastery_after_snapshot: 测试后掌握度快照。
    :return: 掌握度变化列表。
    """
    mastery_changes: list[dict[str, object]] = []
    for point in points:
        before_rate = round(float(mastery_before_snapshot.get(point.id, 0.0)), 4)
        after_rate = round(float(mastery_after_snapshot.get(point.id, before_rate)), 4)
        mastery_changes.append(
            {
                "knowledge_point_id": point.id,
                "knowledge_point_name": point.name,
                "mastery_before": before_rate,
                "mastery_after": after_rate,
                "improvement": round(after_rate - before_rate, 4),
            }
        )
    return mastery_changes


# 维护意图：按预置顺序推进学习路径，而不是触发完整重规划。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def advance_defense_demo_path(node: PathNode, user: User, mark_skipped: bool = False) -> None:
    """
    按预置顺序推进学习路径，而不是触发完整重规划。
    :param node: 当前节点对象。
    :param user: 当前用户对象。
    :param mark_skipped: 是否将当前节点标记为跳过。
    :return: None。
    """

    node.status = "skipped" if mark_skipped else "completed"
    node.save(update_fields=["status"])
    _activate_next_locked_node(node)


# 维护意图：完成阶段测试后的固定解锁动作。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def complete_defense_demo_stage_test(
    node: PathNode,
    user: User,
    progress: NodeProgress,
) -> None:
    """
    完成阶段测试后的固定解锁动作。
    :param node: 当前测试节点。
    :param user: 当前用户对象。
    :param progress: 当前节点进度。
    :return: None。
    """
    _ = user
    node.status = "completed"
    node.save(update_fields=["status"])
    _activate_next_locked_node(node)

    progress.updated_at = timezone.now()
    progress.save(update_fields=["updated_at"])
