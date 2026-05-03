"""
学习路径规则。

负责：
- 读取课程前置关系
- 对掌握度执行前置约束
- 按掌握度 + 拓扑约束排序知识点
- 判定高掌握知识点是否自动完成
"""
from __future__ import annotations

from collections import defaultdict

from knowledge.models import KnowledgePoint, KnowledgeRelation


AUTO_COMPLETE_THRESHOLD = 0.85
PREREQUISITE_MASTERY_THRESHOLD = 0.6


# 维护意图：load course points
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_course_points(course_id: int):
    return list(
        KnowledgePoint.objects.filter(course_id=course_id, is_published=True).order_by('order', 'id')
    )


# 维护意图：build prerequisite maps
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_prerequisite_maps(course_id: int):
    prereq_map = defaultdict(list)
    dependents_map = defaultdict(list)
    for relation in KnowledgeRelation.objects.filter(course_id=course_id, relation_type='prerequisite'):
        prereq_map[relation.post_point_id].append(relation.pre_point_id)
        dependents_map[relation.pre_point_id].append(relation.post_point_id)
    return prereq_map, dependents_map


# 维护意图：对掌握度施加前置约束。
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_prerequisite_caps(mastery_dict: dict[int, float], course_id: int, buffer: float = 0.0) -> dict[int, float]:
    """
    对掌握度施加前置约束。

    初始评测阶段 buffer=0，保证 post <= min(pre)。
    持续学习阶段可允许少量 buffer，但仍避免明显违例。
    """
    adjusted = {int(point_id): float(value) for point_id, value in (mastery_dict or {}).items()}
    points = load_course_points(course_id)
    prereq_map, _ = build_prerequisite_maps(course_id)

    ordered_ids = [point.id for point in points]
    for point_id in ordered_ids:
        prereqs = [pre_id for pre_id in prereq_map.get(point_id, []) if pre_id in adjusted]
        if not prereqs or point_id not in adjusted:
            continue
        cap = min(adjusted[pre_id] for pre_id in prereqs) + buffer
        adjusted[point_id] = max(0.0, min(adjusted[point_id], min(0.98, cap)))
    return adjusted


# 维护意图：is auto completable
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def is_auto_completable(point_id: int, mastery_dict: dict[int, float], prereq_map: dict[int, list[int]]) -> bool:
    mastery = float(mastery_dict.get(point_id, 0))
    if mastery < AUTO_COMPLETE_THRESHOLD:
        return False
    prereqs = prereq_map.get(point_id, [])
    if not prereqs:
        return True
    return all(float(mastery_dict.get(pre_id, 0)) >= PREREQUISITE_MASTERY_THRESHOLD for pre_id in prereqs)


# 维护意图：在满足前置约束的前提下，优先返回掌握度更低的知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def topological_mastery_order(points, mastery_dict: dict[int, float], prereq_map: dict[int, list[int]], completed_point_ids: set[int] | None = None):
    """
    在满足前置约束的前提下，优先返回掌握度更低的知识点。
    """
    completed_point_ids = completed_point_ids or set()
    point_by_id = {point.id: point for point in points}
    indegree = {}
    dependents_map = defaultdict(list)

    for point in points:
        remaining_prereqs = [pre_id for pre_id in prereq_map.get(point.id, []) if pre_id in point_by_id and pre_id not in completed_point_ids]
        indegree[point.id] = len(remaining_prereqs)
        for pre_id in remaining_prereqs:
            dependents_map[pre_id].append(point.id)

    ready = [point for point in points if indegree[point.id] == 0]
    ordered = []
    used_ids = set()

    while ready:
        ready.sort(key=lambda point: (float(mastery_dict.get(point.id, 0)), point.order, point.id))
        current = ready.pop(0)
        if current.id in used_ids:
            continue
        ordered.append(current)
        used_ids.add(current.id)
        for dependent_id in dependents_map.get(current.id, []):
            indegree[dependent_id] -= 1
            if indegree[dependent_id] == 0 and dependent_id not in used_ids:
                ready.append(point_by_id[dependent_id])

    for point in points:
        if point.id not in used_ids:
            ordered.append(point)
    return ordered


# 维护意图：返回自动完成与待学习知识点集合。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def partition_points_for_path(course_id: int, mastery_dict: dict[int, float], excluded_point_ids: set[int] | None = None):
    """
    返回自动完成与待学习知识点集合。

    excluded_point_ids 用于刷新路径时排除已保留节点对应的知识点。
    """
    excluded_point_ids = excluded_point_ids or set()
    points = [point for point in load_course_points(course_id) if point.id not in excluded_point_ids]
    prereq_map, _ = build_prerequisite_maps(course_id)
    auto_completed = []
    pending = []
    for point in topological_mastery_order(points, mastery_dict, prereq_map):
        if is_auto_completable(point.id, mastery_dict, prereq_map):
            auto_completed.append(point)
        else:
            pending.append(point)
    return auto_completed, pending, prereq_map
