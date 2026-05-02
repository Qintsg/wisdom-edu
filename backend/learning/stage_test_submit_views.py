from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.responses import error_response, success_response
from learning.models import PathNode
from learning.stage_test_submission import submit_stage_test_answers
from learning.view_helpers import _get_authenticated_user


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_stage_test(request, node_id):
    """
    提交阶段测试答案（内嵌做题）。
    POST /api/student/path-nodes/{node_id}/stage-test/submit
    """
    user = _get_authenticated_user(request)
    answers = request.data.get("answers", {})
    if not isinstance(answers, dict):
        return error_response(msg="答案格式错误，应为字典格式")

    try:
        node = PathNode.objects.select_related("path", "knowledge_point").get(
            id=node_id,
            path__user=user,
        )
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    if node.node_type != "test":
        return error_response(msg="该节点不是测试节点")

    return success_response(
        data=submit_stage_test_answers(node=node, user=user, answers=answers),
        msg="阶段测试提交成功",
    )
