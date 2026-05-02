"""学习路径动态调整服务。"""

from __future__ import annotations

import logging

from django.db import models, transaction

from assessments.models import AnswerHistory
from common.config import AppConfig
from common.logging_utils import build_log_message
from knowledge.models import KnowledgeMastery, KnowledgePoint
from learning.models import LearningPath, PathNode
from users.models import User


logger = logging.getLogger(__name__)

CourseId = int | str


def refresh_learning_path_from_mastery(
    *,
    path: LearningPath,
    user: User,
    course_id: CourseId,
) -> dict[str, object]:
    """基于 KT 掌握度刷新未完成学习路径。"""
    _update_mastery_from_answer_history(user=user, course_id=course_id)
    with transaction.atomic():
        _rebuild_locked_path_nodes(path=path, user=user, course_id=course_id)

    return {
        "path_id": path.id,
        "nodes": _serialize_refreshed_nodes(path),
        "ai_reason": path.ai_reason,
        "dynamic": path.is_dynamic,
    }


def insert_remediation_nodes(path: LearningPath) -> dict[str, object]:
    """对失败节点插入强化练习节点，兼容旧版路径调整逻辑。"""
    with transaction.atomic():
        for failed_node in path.nodes.filter(status="failed"):
            _insert_remediation_node_if_missing(path, failed_node)
        path.is_dynamic = True
        path.ai_reason = "由于你在学习过程中出现困难，我们调整了学习路径以帮助你更好地掌握知识。"
        path.save()

    path.refresh_from_db()
    return {
        "path_id": path.id,
        "nodes": _serialize_legacy_adjusted_nodes(path),
        "ai_reason": path.ai_reason,
        "dynamic": path.is_dynamic,
    }


def _update_mastery_from_answer_history(*, user: User, course_id: CourseId) -> None:
    """用户主动刷新路径时，先用课程历史答题记录更新 KT 掌握度。"""
    try:
        history = _build_kt_history(user=user, course_id=course_id)
        if not history:
            return

        from ai_services.services import kt_service

        kt_result = kt_service.predict_mastery(
            user_id=user.id,
            course_id=course_id,
            answer_history=history,
        )
        kt_predictions = kt_result.get("predictions") or {}
        logger.info(
            build_log_message(
                "kt.path_refresh.success",
                user_id=user.id,
                course_id=course_id,
                answer_count=len(history),
                prediction_count=len(kt_predictions),
            )
        )
        _apply_kt_predictions(user=user, course_id=course_id, predictions=kt_predictions)
    except Exception as exc:
        logger.error(
            build_log_message(
                "kt.path_refresh.fail",
                user_id=user.id,
                course_id=course_id,
                error=exc,
            )
        )


def _build_kt_history(*, user: User, course_id: CourseId) -> list[dict[str, int]]:
    """读取课程答题历史并转换为 KT 服务输入结构。"""
    answer_records = (
        AnswerHistory.objects.filter(user=user, course_id=course_id)
        .order_by("answered_at")
        .values("question_id", "knowledge_point_id", "is_correct")
    )
    if not answer_records.exists():
        return []

    return [
        {
            "question_id": record["question_id"],
            "knowledge_point_id": record["knowledge_point_id"],
            "correct": 1 if record["is_correct"] else 0,
        }
        for record in answer_records
        if record["knowledge_point_id"]
    ]


def _apply_kt_predictions(
    *,
    user: User,
    course_id: CourseId,
    predictions: dict[object, object],
) -> None:
    """把 KT 输出写回课程知识点掌握度。"""
    for knowledge_point_id, mastery_rate in predictions.items():
        try:
            KnowledgeMastery.objects.update_or_create(
                user=user,
                course_id=course_id,
                knowledge_point_id=knowledge_point_id,
                defaults={"mastery_rate": float(mastery_rate)},
            )
        except Exception as exc:
            logger.warning(
                build_log_message(
                    "kt.path_refresh.mastery_update_fail",
                    user_id=user.id,
                    course_id=course_id,
                    knowledge_point_id=knowledge_point_id,
                    error=exc,
                )
            )


def _rebuild_locked_path_nodes(
    *,
    path: LearningPath,
    user: User,
    course_id: CourseId,
) -> None:
    """删除未来 locked 节点，并根据掌握度补齐新的学习/测试节点。"""
    preserved_nodes = _preserved_path_nodes(path)
    preserved_point_ids = {
        node.knowledge_point_id for node in preserved_nodes if node.knowledge_point_id
    }
    path.nodes.filter(status="locked").delete()

    nodes_to_create, node_resource_points = _build_replacement_nodes(
        path=path,
        user=user,
        course_id=course_id,
        preserved_nodes=preserved_nodes,
        preserved_point_ids=preserved_point_ids,
    )
    _create_path_nodes_with_resources(nodes_to_create, node_resource_points)
    _ensure_active_path_node(path)
    path.is_dynamic = True
    path.ai_reason = "已根据KT预测和AI分析，保留你的学习进度并重新规划了未完成部分。"
    path.save()


def _preserved_path_nodes(path: LearningPath) -> list[PathNode]:
    """保留已完成、进行中、跳过和失败节点，避免刷新丢失学习进度。"""
    preserved_statuses = ("completed", "active", "skipped", "failed")
    return list(path.nodes.filter(status__in=preserved_statuses))


def _build_replacement_nodes(
    *,
    path: LearningPath,
    user: User,
    course_id: CourseId,
    preserved_nodes: list[PathNode],
    preserved_point_ids: set[int],
) -> tuple[list[PathNode], list[KnowledgePoint | None]]:
    """根据剩余知识点和配置生成候选节点列表。"""
    mastery_dict = _course_mastery_map(user=user, course_id=course_id)
    remaining_points = _remaining_course_points(course_id, preserved_point_ids)
    sorted_remaining = sorted(
        remaining_points,
        key=lambda point: mastery_dict.get(point.id, 0),
    )
    remaining_quota = max(0, AppConfig.max_path_nodes() - len(preserved_nodes))

    return _make_path_node_batch(
        path=path,
        points=sorted_remaining[:remaining_quota],
        mastery_dict=mastery_dict,
        start_order=_next_order_index(preserved_nodes),
        test_interval=AppConfig.path_test_interval(),
    )


def _course_mastery_map(*, user: User, course_id: CourseId) -> dict[int, float]:
    """读取课程知识点掌握度，用于低掌握度优先排序。"""
    return {
        mastery.knowledge_point_id: float(mastery.mastery_rate)
        for mastery in KnowledgeMastery.objects.filter(user=user, course_id=course_id)
    }


def _remaining_course_points(
    course_id: CourseId,
    preserved_point_ids: set[int],
) -> list[KnowledgePoint]:
    """获取尚未被保留节点覆盖的已发布知识点。"""
    return list(
        KnowledgePoint.objects.filter(course_id=course_id, is_published=True)
        .exclude(id__in=preserved_point_ids)
        .order_by("order")
    )


def _next_order_index(preserved_nodes: list[PathNode]) -> int:
    """计算新节点追加起始顺序。"""
    return max((node.order_index for node in preserved_nodes), default=-1) + 1


def _make_path_node_batch(
    *,
    path: LearningPath,
    points: list[KnowledgePoint],
    mastery_dict: dict[int, float],
    start_order: int,
    test_interval: int,
) -> tuple[list[PathNode], list[KnowledgePoint | None]]:
    """按学习节点和阶段测试间隔构造 bulk_create 输入。"""
    nodes_to_create: list[PathNode] = []
    node_resource_points: list[KnowledgePoint | None] = []
    study_batch: list[KnowledgePoint] = []
    order_index = start_order

    for point in points:
        mastery_rate = mastery_dict.get(point.id, 0)
        nodes_to_create.append(_make_study_node(path, point, mastery_rate, order_index))
        node_resource_points.append(point)
        study_batch.append(point)
        order_index += 1

        if len(study_batch) >= test_interval:
            nodes_to_create.append(_make_test_node(path, study_batch, order_index))
            node_resource_points.append(None)
            study_batch = []
            order_index += 1

    return nodes_to_create, node_resource_points


def _make_study_node(
    path: LearningPath,
    point: KnowledgePoint,
    mastery_rate: float,
    order_index: int,
) -> PathNode:
    """生成单个学习节点。"""
    return PathNode(
        path=path,
        knowledge_point=point,
        title=f"{point.name}" + ("提升" if mastery_rate > 0.5 else "基础"),
        goal=f"掌握{point.name}的核心概念及应用",
        criterion="完成所有学习资源和测验，正确率≥80%",
        suggestion=f"{'巩固' if mastery_rate > 0.5 else '重点学习'}{point.name}相关内容。",
        status="locked",
        order_index=order_index,
        node_type="study",
        estimated_minutes=max(15, min(60, int(30 + (1 - mastery_rate) * 30))),
    )


def _make_test_node(
    path: LearningPath,
    study_batch: list[KnowledgePoint],
    order_index: int,
) -> PathNode:
    """为一组学习节点生成阶段测试节点。"""
    knowledge_point_names = [point.name for point in study_batch]
    test_names = "、".join(knowledge_point_names)
    if len(knowledge_point_names) > 3:
        test_title = f"阶段测试：{'、'.join(knowledge_point_names[:3])}等{len(knowledge_point_names)}个知识点"
    else:
        test_title = f"阶段测试：{test_names}"

    return PathNode(
        path=path,
        knowledge_point=study_batch[-1],
        title=test_title,
        goal=f"检验{test_names}的掌握程度",
        criterion="正确率≥80%视为通过",
        suggestion="综合运用前几个知识点完成测试题。",
        status="locked",
        order_index=order_index,
        node_type="test",
        estimated_minutes=15,
    )


def _create_path_nodes_with_resources(
    nodes_to_create: list[PathNode],
    node_resource_points: list[KnowledgePoint | None],
) -> None:
    """批量创建节点，并为学习节点绑定可见资源。"""
    if not nodes_to_create:
        return

    created_nodes = PathNode.objects.bulk_create(nodes_to_create)
    for node, point in zip(created_nodes, node_resource_points):
        if point is None:
            continue
        resources = point.resources.filter(is_visible=True)[:5]
        if resources:
            node.resources.set(resources)


def _ensure_active_path_node(path: LearningPath) -> None:
    """当全部保留节点已完成时，激活第一个未来节点。"""
    if path.nodes.filter(status="active").exists():
        return
    first_locked = path.nodes.filter(status="locked").order_by("order_index").first()
    if first_locked:
        first_locked.status = "active"
        first_locked.save()


def _serialize_refreshed_nodes(path: LearningPath) -> list[dict[str, object]]:
    """序列化刷新路径后的节点列表。"""
    return [
        {
            "node_id": node.id,
            "title": node.title,
            "goal": node.goal,
            "criterion": node.criterion,
            "status": node.status,
            "suggestion": node.suggestion,
            "node_type": node.node_type,
            "knowledge_point_id": node.knowledge_point_id,
            "knowledge_point_name": node.knowledge_point.name if node.knowledge_point else None,
            "tasks_count": len(node.resources.all()) + (1 if node.exam else 0),
        }
        for node in path.nodes.select_related("knowledge_point")
        .prefetch_related("resources")
        .order_by("order_index")
    ]


def _insert_remediation_node_if_missing(path: LearningPath, failed_node: PathNode) -> None:
    """为失败节点插入一个强化练习节点，并重新激活原节点。"""
    existing = path.nodes.filter(
        title__contains="强化练习",
        order_index__gt=failed_node.order_index,
        is_inserted=True,
    ).exists()
    if existing or not failed_node.knowledge_point:
        return

    path.nodes.filter(order_index__gt=failed_node.order_index).update(
        order_index=models.F("order_index") + 1
    )
    PathNode.objects.create(
        path=path,
        knowledge_point=failed_node.knowledge_point,
        title=f"{failed_node.knowledge_point.name}强化练习",
        goal=f"纠正对{failed_node.knowledge_point.name}的误解并掌握正确用法",
        criterion="完成强化练习及复测",
        suggestion=f"针对你在{failed_node.knowledge_point.name}测试中的错误，请完成以下强化练习。",
        status="active",
        order_index=failed_node.order_index + 1,
        is_inserted=True,
    )
    failed_node.status = "active"
    failed_node.save()


def _serialize_legacy_adjusted_nodes(path: LearningPath) -> list[dict[str, object]]:
    """序列化旧版强化练习路径调整响应。"""
    return [
        {
            "node_id": node.id,
            "title": node.title,
            "goal": node.goal,
            "criterion": node.criterion,
            "status": node.status,
            "suggestion": node.suggestion,
            "tasks_count": len(node.resources.all()) + (1 if node.exam else 0),
        }
        for node in path.nodes.prefetch_related("resources").all()
    ]
