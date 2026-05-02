"""学习路径相关的学生 RAG 视图。"""

from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.responses import error_response, success_response
from .student_rag_support import build_ai_resource_payload, get_student_path_node


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_ai_resources(request: Request, node_id: int) -> Response:
    """Return resource recommendations for a learning-path node."""
    node = get_student_path_node(node_id, request.user)
    if node is None:
        return error_response(msg="节点不存在", code=404)
    return success_response(data=build_ai_resource_payload(request.user, node))
