"""学习路径生成辅助工具。"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

from common.config import AppConfig


logger = logging.getLogger(__name__)

REMEDIAL_REINSERTION_THRESHOLD = 0.6

if TYPE_CHECKING:
    from courses.models import Course
    from knowledge.models import KnowledgePoint
    from learning.models import LearningPath, PathNode
    from users.models import User


@dataclass
class PathGenerationPlan:
    """批量创建学习路径节点所需的计划结果。"""

    nodes_to_create: list["PathNode"]
    node_resource_points: list["KnowledgePoint | None"]
    linked_points: list["KnowledgePoint"]


def load_course_point_ids(course_id: int) -> list[int]:
    """返回课程内所有已发布知识点 ID。"""
    from knowledge.models import KnowledgePoint

    return list(
        KnowledgePoint.objects.filter(course_id=course_id, is_published=True)
        .order_by("order", "id")
        .values_list("id", flat=True)
    )


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
    pending_ids = set(pending_by_id)
    ordered = sorted(
        pending_points,
        key=lambda point: (
            float(mastery_dict.get(point.id, 0)),
            point.order,
            point.id,
        ),
    )
    seed_point = ordered[0]
    selected_ids: list[int] = [seed_point.id]
    visited_ids: set[int] = {seed_point.id}
    queue_ids: list[int] = [seed_point.id]

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

    if len(selected_ids) < batch_size:
        for point in ordered:
            if point.id in visited_ids:
                continue
            selected_ids.append(point.id)
            visited_ids.add(point.id)
            if len(selected_ids) >= batch_size:
                break

    return [pending_by_id[point_id] for point_id in selected_ids if point_id in pending_by_id]


def sync_course_mastery(
    *,
    user: "User",
    course: "Course",
    course_point_ids: list[int],
) -> dict[int, float]:
    """同步课程全量掌握度，保证路径规划覆盖全部知识点。"""
    from assessments.models import AnswerHistory
    from ai_services.services import kt_service
    from knowledge.models import KnowledgeMastery
    from learning.path_rules import apply_prerequisite_caps

    course_id = course.id
    mastery_dict: dict[int, float] = {}
    answer_records = list(
        AnswerHistory.objects.filter(user=user, course_id=course_id)
        .order_by("answered_at")
        .values("question_id", "knowledge_point_id", "is_correct")
    )
    kt_history = [
        {
            "question_id": record["question_id"],
            "knowledge_point_id": record["knowledge_point_id"],
            "correct": 1 if record["is_correct"] else 0,
        }
        for record in answer_records
        if record["knowledge_point_id"]
    ]

    if kt_history:
        try:
            kt_result = kt_service.predict_mastery(
                user_id=user.id,
                course_id=course_id,
                answer_history=kt_history,
                knowledge_points=course_point_ids,
            )
            raw_predictions = kt_result.get("predictions") or {}
            mastery_dict = {
                int(point_id): float(value)
                for point_id, value in raw_predictions.items()
            }
            logger.info(
                "KT服务调用成功(路径生成): 用户=%s, 答题历史=%d条, 预测结果=%d条",
                user.id,
                len(kt_history),
                len(mastery_dict),
            )
        except Exception as kt_error:
            logger.error(
                "KT预测失败(路径生成): 用户=%s, 错误=%s",
                user.id,
                kt_error,
            )

    existing_mastery = {
        row.knowledge_point_id: float(row.mastery_rate)
        for row in KnowledgeMastery.objects.filter(user=user, course_id=course_id)
    }
    for point_id in course_point_ids:
        if point_id not in mastery_dict:
            mastery_dict[point_id] = existing_mastery.get(point_id, 0.25)

    mastery_dict = apply_prerequisite_caps(
        mastery_dict,
        course_id=course_id,
        buffer=0.05,
    )
    for point_id, mastery_rate in mastery_dict.items():
        KnowledgeMastery.objects.update_or_create(
            user=user,
            course_id=course_id,
            knowledge_point_id=point_id,
            defaults={"mastery_rate": float(mastery_rate)},
        )
    return mastery_dict


def _build_completed_nodes(
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


def _build_pending_nodes(
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
    study_batch: list["KnowledgePoint"] = []
    order_index = start_order
    study_batch_size = max(1, min(AppConfig.path_test_interval(), pending_quota))
    linked_points = build_linked_pending_batch(
        pending_points=pending_points,
        mastery_dict=mastery_dict,
        prereq_map=prereq_map,
        dependents_map=dependents_map,
        batch_size=study_batch_size,
    )
    for point in linked_points:
        mastery_rate = mastery_dict.get(point.id, 0)
        remedial_reinsertion = point.id in remedial_point_ids
        nodes_to_create.append(
            PathNode(
                path=learning_path,
                knowledge_point=point,
                title=(
                    f"{point.name}补强"
                    if remedial_reinsertion
                    else f"{point.name}" + ("提升" if mastery_rate > 0.5 else "基础")
                ),
                goal=f"掌握{point.name}的核心概念及应用",
                criterion="完成所有学习资源和测验，正确率≥80%",
                suggestion=(
                    f"最近一次测试后，{point.name} 掌握度降至 {round(float(mastery_rate) * 100)}%，请优先补强。"
                    if remedial_reinsertion
                    else f"{'巩固' if mastery_rate > 0.5 else '重点学习'}{point.name}相关内容。"
                ),
                status="locked",
                order_index=order_index,
                node_type="study",
                estimated_minutes=max(15, min(60, int(30 + (1 - mastery_rate) * 30))),
                is_inserted=remedial_reinsertion,
            )
        )
        resource_points.append(point)
        study_batch.append(point)
        order_index += 1
    return nodes_to_create, resource_points, linked_points, order_index


def _build_test_node(
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
    if len(knowledge_point_names) > 3:
        title = f"阶段测试：{'、'.join(knowledge_point_names[:3])}等{len(knowledge_point_names)}个知识点"
    else:
        title = f"阶段测试：{'、'.join(knowledge_point_names)}"
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

    completed_nodes, completed_points, next_order = _build_completed_nodes(
        learning_path=learning_path,
        auto_completed_points=auto_completed_points,
        remaining_quota=remaining_quota,
        start_order=max_order + 1,
    )
    pending_quota = max(0, remaining_quota - len(completed_points))
    pending_nodes, pending_resource_points, linked_points, next_order = _build_pending_nodes(
        learning_path=learning_path,
        pending_points=pending_points,
        mastery_dict=mastery_dict,
        prereq_map=prereq_map,
        dependents_map=dependents_map,
        pending_quota=pending_quota,
        start_order=next_order,
        remedial_point_ids=remedial_point_ids,
    )

    nodes_to_create = [*completed_nodes, *pending_nodes]
    node_resource_points: list["KnowledgePoint | None"] = [*completed_points, *pending_resource_points]
    test_node = _build_test_node(
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
