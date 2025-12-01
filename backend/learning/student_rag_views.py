"""学习路径相关的学生 RAG 视图。"""

from __future__ import annotations

import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.defense_demo import get_defense_demo_resource_payload, is_defense_demo_student
from common.logging_utils import build_log_message
from common.responses import error_response, success_response
from learning.models import NodeProgress, PathNode
from platform_ai.rag import student_learning_rag

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_ai_resources(request, node_id: int):
    """Return resource recommendations for a learning-path node.

    The primary path uses the student RAG service. When that service fails, the
    view falls back to a small set of directly linked internal resources so the
    student can still continue learning.
    """
    user = request.user

    try:
        node = PathNode.objects.select_related("knowledge_point", "path__course").get(
            id=node_id,
            path__user=user,
        )
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    if not node.knowledge_point:
        return success_response(data={"internal_resources": [], "external_resources": []})

    progress = NodeProgress.objects.filter(node=node, user=user).first()
    # DEFENSE_DEMO_PRESET: 答辩学习节点使用预置资源推荐，保证现场不依赖
    # 外部检索、重排或模型稳定性，同时保持前端真实加载流程不变。
    preset_payload = get_defense_demo_resource_payload(progress)
    if preset_payload and is_defense_demo_student(user, node.path.course):
        return success_response(
            data={
                "internal_resources": preset_payload.get("internal_resources", []),
                "external_resources": preset_payload.get("external_resources", []),
                "service_status": "preset",
            }
        )

    mastery_value = None
    if progress and progress.mastery_before is not None:
        mastery_value = float(progress.mastery_before)

    # NodeProgress stores resource identifiers in JSON; normalizing to strings
    # keeps membership checks stable across integer and string payload variants.
    completed_resource_ids = set()
    if progress and progress.completed_resources:
        completed_resource_ids = {str(resource_id) for resource_id in progress.completed_resources}

    try:
        recommendation = student_learning_rag.recommend_resources_for_node(
            node=node,
            user=user,
            mastery_value=mastery_value,
            completed_resource_ids=completed_resource_ids,
            external_count=0 if node.node_type == "test" else 2,
        )
    except Exception as exc:
        logger.warning(
            build_log_message(
                "rag.node_resources.fail",
                user_id=user.id,
                node_id=node.id,
                course_id=node.path.course_id,
                error=exc,
            )
        )
        # Fallback only serves course-owned visible resources. This avoids
        # surfacing unrelated external content when the ranking layer is down.
        recommendation = {
            "internal_resources": [
                {
                    "resource_id": resource.id,
                    "title": resource.title,
                    "type": resource.resource_type,
                    "url": resource.url or (resource.file.url if resource.file else ""),
                    "description": resource.description or "",
                    "duration": resource.duration,
                    "required": resource.resource_type in ("video", "document"),
                    "recommended_reason": f"该课程内资源与“{node.knowledge_point.name}”直接关联，可优先学习。",
                    "learning_tips": "建议先学习课程内资源，再结合外部资料补充理解。",
                    "is_internal": True,
                    "completed": str(resource.id) in completed_resource_ids,
                }
                for resource in node.knowledge_point.resources.filter(is_visible=True)[:2]
            ],
            "external_resources": [],
        }

    return success_response(
        data={
            "internal_resources": recommendation.get("internal_resources", []),
            "external_resources": recommendation.get("external_resources", []),
        }
    )
