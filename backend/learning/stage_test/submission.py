"""阶段测试提交入口。"""

from __future__ import annotations

from learning.models import NodeProgress, PathNode
from learning.stage_test.evaluation import evaluate_stage_test
from learning.stage_test.standard_submission import submit_standard_stage_test
from learning.api.helpers import _snapshot_mastery_for_points
from users.models import User


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
    return submit_standard_stage_test(
        node=node,
        user=user,
        progress=progress,
        evaluation=evaluation,
        mastery_before_snapshot=mastery_before_snapshot,
        tracked_point_ids=tracked_point_ids,
    )
