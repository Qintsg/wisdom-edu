"""学习路径节点计划构建。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from common.config import AppConfig

if TYPE_CHECKING:
    from knowledge.models import KnowledgePoint
    from learning.models import LearningPath, PathNode


# 维护意图：批量创建学习路径节点所需的计划结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass
class PathGenerationPlan:
    """批量创建学习路径节点所需的计划结果。"""

    nodes_to_create: list["PathNode"]
    node_resource_points: list["KnowledgePoint | None"]
    linked_points: list["KnowledgePoint"]


# 维护意图：从待学习知识点中选取最低掌握度且尽量互相关联的小批次
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_linked_pending_batch(
    *,
    pending_points: list["KnowledgePoint"],
    mastery_dict: dict[int, float],
    prereq_map: dict[int, list[int]],
    dependents_map: dict[int, list[int]],
    batch_size: int,
) -> list["KnowledgePoint"]:
    """从待学习知识点中选取最低掌握度且尽量互相关联的小批次。"""
    if not pending_points or batch_size <= 0:
        return []
    pending_by_id = {point.id: point for point in pending_points}
    ordered = order_pending_points(pending_points, mastery_dict)
    selected_ids = expand_linked_point_ids(
        seed_point_id=ordered[0].id,
        pending_ids=set(pending_by_id),
        prereq_map=prereq_map,
        dependents_map=dependents_map,
        batch_size=batch_size,
    )
    selected_ids = fill_unlinked_point_ids(
        ordered_points=ordered,
        selected_ids=selected_ids,
        batch_size=batch_size,
    )
    return [pending_by_id[point_id] for point_id in selected_ids if point_id in pending_by_id]


# 维护意图：按掌握度、课程顺序和 ID 生成稳定候选顺序
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def order_pending_points(
    pending_points: list["KnowledgePoint"],
    mastery_dict: dict[int, float],
) -> list["KnowledgePoint"]:
    """按掌握度、课程顺序和 ID 生成稳定候选顺序。"""
    return sorted(
        pending_points,
        key=lambda point: (
            float(mastery_dict.get(point.id, 0)),
            point.order,
            point.id,
        ),
    )


# 维护意图：从最低掌握度知识点出发，沿先修和后继关系扩展学习批次
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def expand_linked_point_ids(
    *,
    seed_point_id: int,
    pending_ids: set[int],
    prereq_map: dict[int, list[int]],
    dependents_map: dict[int, list[int]],
    batch_size: int,
) -> list[int]:
    """从最低掌握度知识点出发，沿先修和后继关系扩展学习批次。"""
    selected_ids: list[int] = [seed_point_id]
    visited_ids: set[int] = {seed_point_id}
    queue_ids: list[int] = [seed_point_id]
    while queue_ids and len(selected_ids) < batch_size:
        current_id = queue_ids.pop(0)
        neighbor_ids = prereq_map.get(current_id, []) + dependents_map.get(current_id, [])
        for neighbor_id in neighbor_ids:
            if neighbor_id in visited_ids or neighbor_id not in pending_ids:
                continue
            visited_ids.add(neighbor_id)
            selected_ids.append(neighbor_id)
            queue_ids.append(neighbor_id)
            if len(selected_ids) >= batch_size:
                break
    return selected_ids


# 维护意图：关系邻居不足时，用剩余低掌握度知识点补足批次
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def fill_unlinked_point_ids(
    *,
    ordered_points: list["KnowledgePoint"],
    selected_ids: list[int],
    batch_size: int,
) -> list[int]:
    """关系邻居不足时，用剩余低掌握度知识点补足批次。"""
    visited_ids = set(selected_ids)
    for point in ordered_points:
        if len(selected_ids) >= batch_size:
            break
        if point.id in visited_ids:
            continue
        selected_ids.append(point.id)
        visited_ids.add(point.id)
    return selected_ids


# 维护意图：构造可直接标记为完成的学习节点
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_completed_nodes(
    *,
    learning_path: "LearningPath",
    auto_completed_points: list["KnowledgePoint"],
    remaining_quota: int,
    start_order: int,
) -> tuple[list["PathNode"], list["KnowledgePoint"], int]:
    """构造可直接标记为完成的学习节点。"""
    from learning.models import PathNode

    nodes_to_create: list[PathNode] = []
    completed_points: list["KnowledgePoint"] = []
    order_index = start_order
    completed_quota = min(len(auto_completed_points), remaining_quota)
    for point in auto_completed_points[:completed_quota]:
        nodes_to_create.append(
            PathNode(
                path=learning_path,
                knowledge_point=point,
                title=f"{point.name}巩固",
                goal=f"你已达到 {point.name} 的默认完成标准",
                criterion="掌握度已达默认完成阈值",
                suggestion="系统已将该知识点标记为默认完成，可按需回顾相关资源。",
                status="completed",
                order_index=order_index,
                node_type="study",
                estimated_minutes=15,
            )
        )
        completed_points.append(point)
        order_index += 1
    return nodes_to_create, completed_points, order_index


# 维护意图：构造当前一轮需要学习的节点
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_pending_nodes(
    *,
    learning_path: "LearningPath",
    pending_points: list["KnowledgePoint"],
    mastery_dict: dict[int, float],
    prereq_map: dict[int, list[int]],
    dependents_map: dict[int, list[int]],
    pending_quota: int,
    start_order: int,
    remedial_point_ids: set[int],
) -> tuple[list["PathNode"], list["KnowledgePoint"], list["KnowledgePoint"], int]:
    """构造当前一轮需要学习的节点。"""
    from learning.models import PathNode

    nodes_to_create: list[PathNode] = []
    resource_points: list["KnowledgePoint"] = []
    order_index = start_order
    if pending_quota <= 0:
        return nodes_to_create, resource_points, [], order_index

    study_batch_size = max(1, min(AppConfig.path_test_interval(), pending_quota))
    linked_points = build_linked_pending_batch(
        pending_points=pending_points,
        mastery_dict=mastery_dict,
        prereq_map=prereq_map,
        dependents_map=dependents_map,
        batch_size=study_batch_size,
    )
    for point in linked_points:
        nodes_to_create.append(
            build_study_node(
                learning_path=learning_path,
                point=point,
                mastery_rate=mastery_dict.get(point.id, 0),
                remedial_reinsertion=point.id in remedial_point_ids,
                order_index=order_index,
            )
        )
        resource_points.append(point)
        order_index += 1
    return nodes_to_create, resource_points, linked_points, order_index


# 维护意图：构造单个学习节点，集中维护补强与基础学习文案
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_study_node(
    *,
    learning_path: "LearningPath",
    point: "KnowledgePoint",
    mastery_rate: float,
    remedial_reinsertion: bool,
    order_index: int,
) -> "PathNode":
    """构造单个学习节点，集中维护补强与基础学习文案。"""
    from learning.models import PathNode

    return PathNode(
        path=learning_path,
        knowledge_point=point,
        title=build_study_title(point.name, mastery_rate, remedial_reinsertion),
        goal=f"掌握{point.name}的核心概念及应用",
        criterion="完成所有学习资源和测验，正确率≥80%",
        suggestion=build_study_suggestion(point.name, mastery_rate, remedial_reinsertion),
        status="locked",
        order_index=order_index,
        node_type="study",
        estimated_minutes=max(15, min(60, int(30 + (1 - mastery_rate) * 30))),
        is_inserted=remedial_reinsertion,
    )


# 维护意图：生成学习节点标题
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_study_title(point_name: str, mastery_rate: float, remedial_reinsertion: bool) -> str:
    """生成学习节点标题。"""
    if remedial_reinsertion:
        return f"{point_name}补强"
    return f"{point_name}" + ("提升" if mastery_rate > 0.5 else "基础")


# 维护意图：生成学习节点建议
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_study_suggestion(point_name: str, mastery_rate: float, remedial_reinsertion: bool) -> str:
    """生成学习节点建议。"""
    if remedial_reinsertion:
        return f"最近一次测试后，{point_name} 掌握度降至 {round(float(mastery_rate) * 100)}%，请优先补强。"
    return f"{'巩固' if mastery_rate > 0.5 else '重点学习'}{point_name}相关内容。"


# 维护意图：基于当前学习批次补一个阶段测试节点
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_test_node(
    *,
    learning_path: "LearningPath",
    study_batch: list["KnowledgePoint"],
    order_index: int,
) -> "PathNode | None":
    """基于当前学习批次补一个阶段测试节点。"""
    from learning.models import PathNode

    if not study_batch:
        return None
    knowledge_point_names = [point.name for point in study_batch]
    title = build_test_title(knowledge_point_names)
    return PathNode(
        path=learning_path,
        knowledge_point=study_batch[-1],
        title=title,
        goal=f"检验{'、'.join(knowledge_point_names)}的掌握程度",
        criterion="正确率≥80%视为通过",
        suggestion="综合运用前几个知识点完成测试题。",
        status="locked",
        order_index=order_index,
        node_type="test",
        estimated_minutes=15,
    )


# 维护意图：生成阶段测试节点标题
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_test_title(knowledge_point_names: list[str]) -> str:
    """生成阶段测试节点标题。"""
    if len(knowledge_point_names) > 3:
        return f"阶段测试：{'、'.join(knowledge_point_names[:3])}等{len(knowledge_point_names)}个知识点"
    return f"阶段测试：{'、'.join(knowledge_point_names)}"


# 维护意图：根据保留节点和掌握度生成新一轮路径节点计划
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_generation_plan(
    *,
    learning_path: "LearningPath",
    preserved_nodes: list["PathNode"],
    auto_completed_points: list["KnowledgePoint"],
    pending_points: list["KnowledgePoint"],
    mastery_dict: dict[int, float],
    prereq_map: dict[int, list[int]],
    dependents_map: dict[int, list[int]],
    remedial_point_ids: set[int],
) -> PathGenerationPlan:
    """根据保留节点和掌握度生成新一轮路径节点计划。"""
    max_order = max((node.order_index for node in preserved_nodes), default=-1)
    remaining_quota = max(0, AppConfig.max_path_nodes() - len(preserved_nodes))
    completed_nodes, completed_points, next_order = build_completed_nodes(
        learning_path=learning_path,
        auto_completed_points=auto_completed_points,
        remaining_quota=remaining_quota,
        start_order=max_order + 1,
    )
    pending_nodes, pending_resource_points, linked_points, next_order = build_pending_nodes(
        learning_path=learning_path,
        pending_points=pending_points,
        mastery_dict=mastery_dict,
        prereq_map=prereq_map,
        dependents_map=dependents_map,
        pending_quota=max(0, remaining_quota - len(completed_points)),
        start_order=next_order,
        remedial_point_ids=remedial_point_ids,
    )
    return assemble_generation_plan(
        learning_path=learning_path,
        completed_nodes=completed_nodes,
        completed_points=completed_points,
        pending_nodes=pending_nodes,
        pending_resource_points=pending_resource_points,
        linked_points=linked_points,
        next_order=next_order,
    )


# 维护意图：合并学习节点、资源映射和阶段测试节点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def assemble_generation_plan(
    *,
    learning_path: "LearningPath",
    completed_nodes: list["PathNode"],
    completed_points: list["KnowledgePoint"],
    pending_nodes: list["PathNode"],
    pending_resource_points: list["KnowledgePoint"],
    linked_points: list["KnowledgePoint"],
    next_order: int,
) -> PathGenerationPlan:
    """合并学习节点、资源映射和阶段测试节点。"""
    nodes_to_create = [*completed_nodes, *pending_nodes]
    node_resource_points: list["KnowledgePoint | None"] = [*completed_points, *pending_resource_points]
    test_node = build_test_node(
        learning_path=learning_path,
        study_batch=linked_points,
        order_index=next_order,
    )
    if test_node is not None:
        nodes_to_create.append(test_node)
        node_resource_points.append(None)
    return PathGenerationPlan(
        nodes_to_create=nodes_to_create,
        node_resource_points=node_resource_points,
        linked_points=linked_points,
    )


# 维护意图：为新建学习节点回填最多 5 个可见资源
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def attach_resources_to_created_nodes(
    created_nodes: list["PathNode"],
    node_resource_points: list["KnowledgePoint | None"],
) -> None:
    """为新建学习节点回填最多 5 个可见资源。"""
    for node, point in zip(created_nodes, node_resource_points):
        if point is None:
            continue
        resources = point.resources.filter(is_visible=True)[:5]
        if resources:
            node.resources.add(*list(resources))
