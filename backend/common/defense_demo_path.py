from __future__ import annotations

from courses.models import Course
from exams.models import Exam
from knowledge.models import KnowledgePoint
from learning.models import LearningPath, NodeProgress, PathNode
from users.models import User

from common.defense_demo_progress import _average_snapshot
from common.defense_demo_stage import build_stage_feedback_payload


DemoNodeSpec = dict[str, object]


# 维护意图：创建固定学习路径与节点进度预置。
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _ensure_demo_learning_path(
    course: Course,
    student: User,
    points: list[KnowledgePoint],
    resource_payloads: dict[str, list[dict[str, object]]],
    stage_exam: Exam,
    completed_stage_result: dict[str, object] | None = None,
) -> None:
    """
    创建固定学习路径与节点进度预置。
    :param course: 主课程。
    :param student: 学生账号。
    :param points: 知识点列表。
    :param resource_payloads: 固定资源展示载荷。
    :param stage_exam: 阶段测试试卷。
    :return: None。
    """
    path = _upsert_demo_path(course, student)
    node_specs = _demo_node_specs(points)
    stage_feedback = build_stage_feedback_payload(points)
    node_map, progress_map = _sync_demo_nodes(
        path=path,
        student=student,
        node_specs=node_specs,
        resource_payloads=resource_payloads,
        stage_exam=stage_exam,
        stage_feedback=stage_feedback,
    )

    if isinstance(completed_stage_result, dict):
        _apply_completed_stage_result(
            node_map=node_map,
            progress_map=progress_map,
            resource_payloads=resource_payloads,
            stage_exam=stage_exam,
            completed_stage_result=completed_stage_result,
        )


# 维护意图：创建或更新答辩演示专用学习路径
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _upsert_demo_path(course: Course, student: User) -> LearningPath:
    """创建或更新答辩演示专用学习路径。"""
    path, _ = LearningPath.objects.update_or_create(
        user=student,
        course=course,
        defaults={
            "ai_reason": "先强化基础概念，再进入生态架构理解，最后串联计算模型，通过阶段测试触发后续节点。",
            "is_dynamic": True,
        },
    )
    return path


# 维护意图：返回答辩演示固定路径节点定义
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _demo_node_specs(points: list[KnowledgePoint]) -> list[DemoNodeSpec]:
    """返回答辩演示固定路径节点定义。"""
    return [
        {
            "title": "学习节点 1：大数据概念与特征",
            "goal": "理解 4V 特征和大数据在教学场景中的实际价值。",
            "criterion": "能用自己的话概括大数据的核心特征。",
            "suggestion": "先理解为什么数据规模与速度变化会推动架构升级。",
            "status": "active",
            "order_index": 1,
            "estimated_minutes": 6,
            "knowledge_point": points[0],
            "node_type": "study",
        },
        {
            "title": "学习节点 2：Hadoop 生态组成",
            "goal": "掌握 HDFS、MapReduce、YARN 之间的协作关系。",
            "criterion": "能说明存储、计算、调度三者各自负责什么。",
            "suggestion": "建议先看结构图，再结合组件职责做对照理解。",
            "status": "locked",
            "order_index": 2,
            "estimated_minutes": 5,
            "knowledge_point": points[1],
            "node_type": "study",
        },
        {
            "title": "学习节点 3：Spark 核心计算模型",
            "goal": "理解 Spark 与 MapReduce 在执行机制上的差异。",
            "criterion": "能解释为什么 Spark 更适合迭代与内存计算场景。",
            "suggestion": "重点关注执行模型差异，而不是只背诵框架名称。",
            "status": "locked",
            "order_index": 3,
            "estimated_minutes": 5,
            "knowledge_point": points[2],
            "node_type": "study",
        },
        {
            "title": "阶段测试：大数据基础综合",
            "goal": "验证前三个学习节点的核心概念是否已经连成完整链路。",
            "criterion": "通过阶段测试并触发后续学习节点。",
            "suggestion": "完成测试后注意观察掌握度变化与路径节点的刷新。",
            "status": "locked",
            "order_index": 4,
            "estimated_minutes": 4,
            "knowledge_point": points[2],
            "node_type": "test",
        },
        {
            "title": "进阶节点 1：批处理与内存计算巩固",
            "goal": "基于测试结果继续强化分布式与内存计算的比较理解。",
            "criterion": "完成后续资源浏览与概念对照。",
            "suggestion": "通过资源对比批处理和内存计算的实际差异。",
            "status": "locked",
            "order_index": 5,
            "estimated_minutes": 4,
            "knowledge_point": points[2],
            "node_type": "study",
        },
        {
            "title": "进阶节点 2：课程资源拓展学习",
            "goal": "进入下一阶段资源拓展与知识图谱联动学习。",
            "criterion": "进入资源页与知识图谱页继续学习。",
            "suggestion": "结合知识图谱中的前置关系定位薄弱环节。",
            "status": "locked",
            "order_index": 6,
            "estimated_minutes": 4,
            "knowledge_point": points[1],
            "node_type": "study",
        },
    ]


# 维护意图：同步固定路径节点，并为每个节点设置预置进度数据
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _sync_demo_nodes(
    *,
    path: LearningPath,
    student: User,
    node_specs: list[DemoNodeSpec],
    resource_payloads: dict[str, list[dict[str, object]]],
    stage_exam: Exam,
    stage_feedback: dict[str, object],
) -> tuple[dict[int, PathNode], dict[int, NodeProgress]]:
    """同步固定路径节点，并为每个节点设置预置进度数据。"""
    kept_titles = {str(spec["title"]) for spec in node_specs}
    path.nodes.exclude(title__in=kept_titles).delete()

    node_map: dict[int, PathNode] = {}
    progress_map: dict[int, NodeProgress] = {}
    for spec in node_specs:
        node, progress = _upsert_demo_node(
            path=path,
            student=student,
            spec=spec,
            resource_payloads=resource_payloads,
            stage_exam=stage_exam,
            stage_feedback=stage_feedback,
        )
        node_map[int(spec["order_index"])] = node
        progress_map[int(spec["order_index"])] = progress
    return node_map, progress_map


# 维护意图：创建或更新单个演示节点及其 NodeProgress
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _upsert_demo_node(
    *,
    path: LearningPath,
    student: User,
    spec: DemoNodeSpec,
    resource_payloads: dict[str, list[dict[str, object]]],
    stage_exam: Exam,
    stage_feedback: dict[str, object],
) -> tuple[PathNode, NodeProgress]:
    """创建或更新单个演示节点及其 NodeProgress。"""
    node, _ = PathNode.objects.update_or_create(
        path=path,
        title=spec["title"],
        defaults={
            "goal": spec["goal"],
            "criterion": spec["criterion"],
            "suggestion": spec["suggestion"],
            "status": spec["status"],
            "order_index": spec["order_index"],
            "estimated_minutes": spec["estimated_minutes"],
            "knowledge_point": spec["knowledge_point"],
            "node_type": spec["node_type"],
            "exam": stage_exam if spec["node_type"] == "test" else None,
        },
    )
    progress, _ = NodeProgress.objects.update_or_create(
        node=node,
        user=student,
        defaults=_progress_defaults(),
    )
    _apply_demo_progress_payload(
        progress=progress,
        spec=spec,
        resource_payloads=resource_payloads,
        stage_feedback=stage_feedback,
    )
    return node, progress


# 维护意图：返回演示节点进度的基础默认值
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _progress_defaults() -> dict[str, object]:
    """返回演示节点进度的基础默认值。"""
    return {
        "completed_resources": [],
        "completed_exams": [],
        "mastery_before": None,
        "mastery_after": None,
        "extra_data": {"defense_demo_preset": True},
    }


# 维护意图：把预置资源或预置阶段测试数据写入节点进度
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _apply_demo_progress_payload(
    *,
    progress: NodeProgress,
    spec: DemoNodeSpec,
    resource_payloads: dict[str, list[dict[str, object]]],
    stage_feedback: dict[str, object],
) -> None:
    """把预置资源或预置阶段测试数据写入节点进度。"""
    extra_data = dict(progress.extra_data or {})
    extra_data["defense_demo_preset"] = True
    knowledge_point = spec["knowledge_point"]
    if spec["node_type"] == "study" and isinstance(knowledge_point, KnowledgePoint):
        extra_data["preset_resources"] = {
            "internal_resources": resource_payloads.get(knowledge_point.name, []),
            "external_resources": [],
        }
    if spec["node_type"] == "test":
        extra_data["preset_stage_test"] = stage_feedback
    progress.extra_data = extra_data
    progress.save(update_fields=["extra_data", "updated_at"])


# 维护意图：已完成演示时，回放阶段测试完成后的节点状态和进度
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _apply_completed_stage_result(
    *,
    node_map: dict[int, PathNode],
    progress_map: dict[int, NodeProgress],
    resource_payloads: dict[str, list[dict[str, object]]],
    stage_exam: Exam,
    completed_stage_result: dict[str, object],
) -> None:
    """已完成演示时，回放阶段测试完成后的节点状态和进度。"""
    _apply_completed_statuses(node_map)
    mastery_before_map, mastery_after_map = _mastery_maps_from_result(
        completed_stage_result
    )
    for order_index in (1, 2, 3):
        _complete_study_progress(
            node=node_map.get(order_index),
            progress=progress_map.get(order_index),
            resource_payloads=resource_payloads,
            mastery_before_map=mastery_before_map,
            mastery_after_map=mastery_after_map,
        )
    _complete_stage_progress(
        stage_progress=progress_map.get(4),
        stage_exam=stage_exam,
        completed_stage_result=completed_stage_result,
        mastery_before_map=mastery_before_map,
        mastery_after_map=mastery_after_map,
    )


# 维护意图：将演示路径推进到阶段测试已完成后的固定状态
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _apply_completed_statuses(node_map: dict[int, PathNode]) -> None:
    """将演示路径推进到阶段测试已完成后的固定状态。"""
    completed_status_map = {
        1: "completed",
        2: "completed",
        3: "completed",
        4: "completed",
        5: "active",
        6: "locked",
    }
    for order_index, status in completed_status_map.items():
        node = node_map.get(order_index)
        if not node or node.status == status:
            continue
        node.status = status
        node.save(update_fields=["status"])


# 维护意图：从阶段测试结果中提取前后掌握度快照
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _mastery_maps_from_result(
    completed_stage_result: dict[str, object],
) -> tuple[dict[int, float], dict[int, float]]:
    """从阶段测试结果中提取前后掌握度快照。"""
    mastery_before_map: dict[int, float] = {}
    mastery_after_map: dict[int, float] = {}
    mastery_changes = completed_stage_result.get("mastery_changes")
    if not isinstance(mastery_changes, list):
        return mastery_before_map, mastery_after_map

    for item in mastery_changes:
        if isinstance(item, dict):
            _collect_mastery_change(item, mastery_before_map, mastery_after_map)
    return mastery_before_map, mastery_after_map


# 维护意图：收集单条掌握度变化
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _collect_mastery_change(
    item: dict[str, object],
    mastery_before_map: dict[int, float],
    mastery_after_map: dict[int, float],
) -> None:
    """收集单条掌握度变化。"""
    point_id = item.get("knowledge_point_id")
    mastery_before = item.get("mastery_before")
    mastery_after = item.get("mastery_after")
    if isinstance(point_id, int) and isinstance(mastery_before, (int, float)):
        mastery_before_map[point_id] = float(mastery_before)
    if isinstance(point_id, int) and isinstance(mastery_after, (int, float)):
        mastery_after_map[point_id] = float(mastery_after)


# 维护意图：回放已完成学习节点的资源完成和掌握度变化
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _complete_study_progress(
    *,
    node: PathNode | None,
    progress: NodeProgress | None,
    resource_payloads: dict[str, list[dict[str, object]]],
    mastery_before_map: dict[int, float],
    mastery_after_map: dict[int, float],
) -> None:
    """回放已完成学习节点的资源完成和掌握度变化。"""
    if not node or not progress or not node.knowledge_point:
        return
    payloads = resource_payloads.get(node.knowledge_point.name, [])
    progress.completed_resources = [
        str(payload["resource_id"])
        for payload in payloads
        if isinstance(payload, dict) and isinstance(payload.get("resource_id"), int)
    ]
    point_id = node.knowledge_point_id
    if point_id in mastery_before_map:
        progress.mastery_before = mastery_before_map[point_id]
    if point_id in mastery_after_map:
        progress.mastery_after = mastery_after_map[point_id]
    progress.save(
        update_fields=[
            "completed_resources",
            "mastery_before",
            "mastery_after",
            "updated_at",
        ]
    )


# 维护意图：回放阶段测试节点完成状态和结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _complete_stage_progress(
    *,
    stage_progress: NodeProgress | None,
    stage_exam: Exam,
    completed_stage_result: dict[str, object],
    mastery_before_map: dict[int, float],
    mastery_after_map: dict[int, float],
) -> None:
    """回放阶段测试节点完成状态和结果。"""
    if not stage_progress:
        return
    completed_exams = list(stage_progress.completed_exams or [])
    if stage_exam.id not in completed_exams:
        completed_exams.append(stage_exam.id)
    stage_progress.completed_exams = completed_exams
    average_before = _average_snapshot(mastery_before_map)
    average_after = _average_snapshot(mastery_after_map)
    if average_before is not None:
        stage_progress.mastery_before = average_before
    if average_after is not None:
        stage_progress.mastery_after = average_after
    extra_data = dict(stage_progress.extra_data or {})
    extra_data["stage_test_result"] = completed_stage_result
    stage_progress.extra_data = extra_data
    stage_progress.save(
        update_fields=[
            "completed_exams",
            "mastery_before",
            "mastery_after",
            "extra_data",
            "updated_at",
        ]
    )
