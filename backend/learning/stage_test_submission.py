"""阶段测试提交入口。"""

from __future__ import annotations

from common.defense_demo import (
    get_defense_demo_stage_test_payload,
    is_defense_demo_student,
)
from learning.models import NodeProgress, PathNode
from learning.stage_test_demo_submission import submit_demo_stage_test
from learning.stage_test_evaluation import evaluate_stage_test
from learning.stage_test_standard_submission import submit_standard_stage_test
from learning.view_helpers import _snapshot_mastery_for_points
from users.models import User


# 维护意图：提交阶段测试答案并返回兼容前端的结果 payload
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def submit_stage_test_answers(
    *,
    node: PathNode,
    user: User,
    answers: dict[str, object],
) -> dict[str, object]:
    """提交阶段测试答案并返回兼容前端的结果 payload。"""
    evaluation = evaluate_stage_test(node=node, user=user, answers=answers)
    progress, _ = NodeProgress.objects.get_or_create(node=node, user=user)
    tracked_point_ids = sorted(evaluation.point_stats.keys())
    mastery_before_snapshot = _snapshot_mastery_for_points(
        user,
        node.path.course_id,
        tracked_point_ids,
    )
    demo_stage_payload = get_defense_demo_stage_test_payload(progress)

    if demo_stage_payload and is_defense_demo_student(user, node.path.course):
        return submit_demo_stage_test(
            node=node,
            user=user,
            progress=progress,
            evaluation=evaluation,
            demo_stage_payload=demo_stage_payload,
            mastery_before_snapshot=mastery_before_snapshot,
            tracked_point_ids=tracked_point_ids,
        )

    return submit_standard_stage_test(
        node=node,
        user=user,
        progress=progress,
        evaluation=evaluation,
        mastery_before_snapshot=mastery_before_snapshot,
        tracked_point_ids=tracked_point_ids,
    )
