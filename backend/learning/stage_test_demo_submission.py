"""答辩预置阶段测试提交流程。"""

from __future__ import annotations

from django.db import transaction

from common.defense_demo import complete_defense_demo_stage_test
from knowledge.models import KnowledgeMastery
from learning.models import NodeProgress, PathNode
from learning.stage_test_models import StageTestEvaluation
from learning.stage_test_results import persist_stage_progress, stage_response_payload
from users.models import User


# 维护意图：答辩预置阶段测试使用固定掌握度和固定反馈
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def submit_demo_stage_test(
    *,
    node: PathNode,
    user: User,
    progress: NodeProgress,
    evaluation: StageTestEvaluation,
    demo_stage_payload: dict[str, object],
    mastery_before_snapshot: dict[int, float],
    tracked_point_ids: list[int],
) -> dict[str, object]:
    """答辩预置阶段测试使用固定掌握度和固定反馈。"""
    feedback_report = demo_feedback_report(demo_stage_payload)
    with transaction.atomic():
        update_demo_node_status(node, user, progress, evaluation.passed)
        apply_demo_mastery(user, node, demo_stage_payload)
        mastery_changes = persist_stage_progress(
            user=user,
            node=node,
            progress=progress,
            evaluation=evaluation,
            feedback_report=feedback_report,
            mastery_before_snapshot=mastery_before_snapshot,
            tracked_point_ids=tracked_point_ids,
            path_refreshed=evaluation.passed,
            update_fields=["mastery_before", "mastery_after", "extra_data", "updated_at"],
        )

    return stage_response_payload(
        evaluation=evaluation,
        mastery_changes=mastery_changes,
        feedback_report=feedback_report,
        node_status=node.status,
        path_refreshed=evaluation.passed,
    )


# 维护意图：更新答辩预置阶段测试节点状态
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_demo_node_status(
    node: PathNode,
    user: User,
    progress: NodeProgress,
    passed: bool,
) -> None:
    """更新答辩预置阶段测试节点状态。"""
    if passed:
        complete_defense_demo_stage_test(node, user, progress)
        return
    node.status = "failed"
    node.save(update_fields=["status"])


# 维护意图：按答辩预置 payload 写入固定掌握度
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_demo_mastery(
    user: User,
    node: PathNode,
    demo_stage_payload: dict[str, object],
) -> None:
    """按答辩预置 payload 写入固定掌握度。"""
    mastery_after_map = demo_stage_payload.get("mastery_after", {})
    if not isinstance(mastery_after_map, dict):
        return
    for point_id_text, mastery_value in mastery_after_map.items():
        apply_single_demo_mastery(
            user=user,
            node=node,
            point_id_text=point_id_text,
            mastery_value=mastery_value,
        )


# 维护意图：写入单个答辩预置知识点掌握度，非法数据直接跳过
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_single_demo_mastery(
    *,
    user: User,
    node: PathNode,
    point_id_text: object,
    mastery_value: object,
) -> None:
    """写入单个答辩预置知识点掌握度，非法数据直接跳过。"""
    try:
        point_id = int(point_id_text)
        mastery_rate = round(float(mastery_value), 4)
    except (TypeError, ValueError):
        return
    KnowledgeMastery.objects.update_or_create(
        user=user,
        course=node.path.course,
        knowledge_point_id=point_id,
        defaults={"mastery_rate": mastery_rate},
    )


# 维护意图：读取答辩预置反馈报告
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def demo_feedback_report(demo_stage_payload: dict[str, object]) -> dict[str, object]:
    """读取答辩预置反馈报告。"""
    feedback_report = demo_stage_payload.get("feedback_report")
    return feedback_report if isinstance(feedback_report, dict) else {}
