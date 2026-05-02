from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.responses import error_response, success_response
from learning.models import PathNode
from learning.stage_test_selection import build_stage_test_payload
from learning.view_helpers import _get_authenticated_user


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_stage_test(request, node_id):
    """
    获取阶段测试题目（内嵌做题）。
    GET /api/student/path-nodes/{node_id}/stage-test
    """
    user = _get_authenticated_user(request)
    try:
        node = PathNode.objects.select_related("path", "knowledge_point").get(
            id=node_id,
            path__user=user,
        )
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    if node.node_type != "test":
        return error_response(msg="该节点不是测试节点")

    payload, message = build_stage_test_payload(node, node_id)
    return success_response(data=payload, msg=message) if message else success_response(data=payload)
