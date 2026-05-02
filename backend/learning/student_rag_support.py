"""学生学习节点 RAG 资源推荐支撑逻辑。"""

from __future__ import annotations

import logging

from common.defense_demo import get_defense_demo_resource_payload, is_defense_demo_student
from common.logging_utils import build_log_message
from learning.models import NodeProgress, PathNode
from platform_ai.rag import student_learning_rag


logger = logging.getLogger(__name__)


def get_student_path_node(node_id: int, user: object) -> PathNode | None:
    """读取当前学生拥有的学习路径节点。"""
    return (
        PathNode.objects.select_related("knowledge_point", "path__course")
        .filter(id=node_id, path__user=user)
        .first()
    )


def build_ai_resource_payload(user: object, node: PathNode) -> dict[str, object]:
    """组装学习节点 AI 推荐资源响应。"""
    if not node.knowledge_point:
        return empty_resource_payload()

    progress = NodeProgress.objects.filter(node=node, user=user).first()
    preset_payload = defense_demo_resource_payload(user, node, progress)
    if preset_payload is not None:
        return preset_payload

    completed_resource_ids = completed_resource_id_set(progress)
    recommendation = recommend_node_resources(
        user=user,
        node=node,
        progress=progress,
        completed_resource_ids=completed_resource_ids,
    )
    return {
        "internal_resources": recommendation.get("internal_resources", []),
        "external_resources": recommendation.get("external_resources", []),
    }


def empty_resource_payload() -> dict[str, object]:
    """返回空资源推荐载荷。"""
    return {"internal_resources": [], "external_resources": []}


def defense_demo_resource_payload(
    user: object,
    node: PathNode,
    progress: NodeProgress | None,
) -> dict[str, object] | None:
    """答辩演示账号命中时返回预置资源推荐。"""
    preset_payload = get_defense_demo_resource_payload(progress)
    if not preset_payload or not is_defense_demo_student(user, node.path.course):
        return None
    return {
        "internal_resources": preset_payload.get("internal_resources", []),
        "external_resources": preset_payload.get("external_resources", []),
        "service_status": "preset",
    }


def completed_resource_id_set(progress: NodeProgress | None) -> set[str]:
    """标准化已完成资源 ID，兼容 JSON 中的整数和字符串。"""
    if not progress or not progress.completed_resources:
        return set()
    return {str(resource_id) for resource_id in progress.completed_resources}


def mastery_before_value(progress: NodeProgress | None) -> float | None:
    """读取推荐资源使用的学习前掌握度。"""
    if progress and progress.mastery_before is not None:
        return float(progress.mastery_before)
    return None


def recommend_node_resources(
    *,
    user: object,
    node: PathNode,
    progress: NodeProgress | None,
    completed_resource_ids: set[str],
) -> dict[str, object]:
    """调用学生 RAG 推荐服务，失败时退回课程内可见资源。"""
    try:
        return student_learning_rag.recommend_resources_for_node(
            node=node,
            user=user,
            mastery_value=mastery_before_value(progress),
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
        return fallback_node_resources(node, completed_resource_ids)


def fallback_node_resources(node: PathNode, completed_resource_ids: set[str]) -> dict[str, object]:
    """RAG 推荐失败时仅返回课程内与知识点直接关联的可见资源。"""
    return {
        "internal_resources": [
            build_fallback_resource_payload(resource, node, completed_resource_ids)
            for resource in node.knowledge_point.resources.filter(is_visible=True)[:2]
        ],
        "external_resources": [],
    }


def build_fallback_resource_payload(resource: object, node: PathNode, completed_resource_ids: set[str]) -> dict[str, object]:
    """序列化课程内兜底资源推荐项。"""
    return {
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
