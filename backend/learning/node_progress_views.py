from __future__ import annotations

from django.db import DatabaseError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.defense_demo import advance_defense_demo_path, is_defense_demo_student
from common.responses import error_response, success_response
from learning.models import LearningPath, NodeProgress, PathNode
from learning.view_helpers import _coerce_string_list, _get_authenticated_user
from platform_ai.rag import student_learning_rag

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_learning_progress(request):
    """
    获取学习进度
    GET /api/student/learning-progress
    """
    course_id = request.query_params.get("course_id")
    if not course_id:
        return error_response(msg="缺少课程ID")

    user = _get_authenticated_user(request)
    path = LearningPath.objects.filter(user=user, course_id=course_id).first()

    if not path:
        return success_response(
            data={
                "total_nodes": 0,
                "completed_nodes": 0,
                "progress_rate": 0,
                "current_node": None,
            }
        )

    total_nodes = path.nodes.count()
    completed_nodes = path.nodes.filter(status="completed").count()
    progress_rate = completed_nodes / total_nodes if total_nodes > 0 else 0

    # 计算累计学习时长（分钟）：已完成节点的估计时间之和
    from django.db.models import Sum

    study_time = (
        path.nodes.filter(status="completed").aggregate(total=Sum("estimated_minutes"))[
            "total"
        ]
        or 0
    )

    current_node = path.nodes.filter(status="active").first()

    return success_response(
        data={
            "total_nodes": total_nodes,
            "completed_nodes": completed_nodes,
            "progress_rate": round(progress_rate, 2),
            "progress": round(progress_rate, 2),
            "study_time": study_time,
            "current_node": {"node_id": current_node.id, "title": current_node.title}
            if current_node
            else None,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_learning_node(request, node_id):
    """
    开始学习节点
    POST /api/path-nodes/{node_id}/start
    """
    user = _get_authenticated_user(request)

    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    if node.status == "locked":
        return error_response(msg="该节点尚未解锁")

    node.status = "active"
    try:
        node.save(update_fields=["status"])
    except DatabaseError:
        return error_response(msg="节点已被刷新，请重新加载路径", code=409)

    # 创建或更新进度记录（用于记录学习开始时间等）
    NodeProgress.objects.get_or_create(node=node, user=user)

    return success_response(
        data={"node_id": node.id, "status": node.status}, msg="开始学习"
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_path_node(request, node_id):
    """
    完成学习节点
    POST /api/path-nodes/{node_id}/complete
    """
    user = _get_authenticated_user(request)

    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    # DEFENSE_DEMO_PRESET: 答辩链路需要固定节点顺序，学习节点完成时只推进到
    # 下一个预置节点，避免调用完整路径重排后破坏现场讲稿和截图顺序。
    if is_defense_demo_student(user, node.path.course):
        advance_defense_demo_path(node, user)
    else:
        node.status = "completed"
        try:
            node.save(update_fields=["status"])
        except DatabaseError:
            return error_response(msg="节点已被刷新，请重新加载路径", code=409)

        # 只解锁下一个节点，不重新生成全量路径，避免过早插入补强节点
        from ai_services.services.path_service import PathService

        PathService().unlock_next_node(node)

    return success_response(
        data={
            "node_id": node.id,
            "status": node.status,
            "path_refreshed": not is_defense_demo_student(user, node.path.course),
        },
        msg="节点已完成",
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def skip_path_node(request, node_id):
    """
    跳过学习节点
    POST /api/path-nodes/{node_id}/skip
    """
    user = _get_authenticated_user(request)
    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    if is_defense_demo_student(user, node.path.course):
        advance_defense_demo_path(node, user, mark_skipped=True)
    else:
        node.status = "skipped"
        node.save(update_fields=["status"])

        # 只解锁下一个节点，不重新生成全量路径
        from ai_services.services.path_service import PathService

        PathService().unlock_next_node(node)

    return success_response(
        data={
            "node_id": node.id,
            "status": node.status,
            "path_refreshed": not is_defense_demo_student(user, node.path.course),
        },
        msg="节点已跳过",
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_node_resources(request, node_id):
    """
    获取节点资源列表（兼容端点）
    GET /api/path-nodes/{node_id}/resources

    资源现在通过AI实时推荐，此端点返回空列表，保留向前兼容。
    前端应使用 get_ai_resources 获取推荐资源。
    """
    user = _get_authenticated_user(request)

    if not PathNode.objects.filter(id=node_id, path__user=user).exists():
        return error_response(msg="节点不存在", code=404)

    return success_response(data={"resources": []})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_ai_resources(request, node_id):
    """
    获取节点的AI推荐资源（内部+外部）
    GET /api/student/path-nodes/{node_id}/ai-resources

    两次独立LLM调用：
    1. recommend_internal_resources() — 从课程资源库中筛选最相关的内部资源
    2. recommend_external_resources() — 推荐外部学习资源
    返回 {internal_resources: [...], external_resources: [...]}
    """
    user = _get_authenticated_user(request)

    try:
        node = PathNode.objects.select_related("knowledge_point", "path__course").get(
            id=node_id, path__user=user
        )
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    progress = NodeProgress.objects.filter(node=node, user=user).first()
    mastery_val = None
    if progress and progress.mastery_after is not None:
        mastery_val = float(progress.mastery_after)
    elif progress and progress.mastery_before is not None:
        mastery_val = float(progress.mastery_before)
    completed_ids = (
        set(_coerce_string_list(progress.completed_resources))
        if progress
        else set()
    )
    recommendation_payload = student_learning_rag.recommend_resources_for_node(
        node=node,
        user=user,
        mastery_value=mastery_val,
        completed_resource_ids=completed_ids,
        internal_count=2,
        external_count=0 if node.node_type == "test" else 2,
    )
    return success_response(
        data={
            "internal_resources": recommendation_payload.get("internal_resources", []),
            "external_resources": recommendation_payload.get("external_resources", []),
            "service_status": "available",
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_node_exams(request, node_id):
    """
    获取节点测验列表
    GET /api/path-nodes/{node_id}/exams
    """
    user = _get_authenticated_user(request)

    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    exams = []
    if node.exam:
        exams.append(
            {
                "exam_id": node.exam.id,
                "title": node.exam.title,
                "duration": node.exam.duration,
                "pass_score": float(node.exam.pass_score)
                if node.exam.pass_score
                else 60,
            }
        )

    return success_response(data={"exams": exams})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pause_node_resource(request, node_id, resource_id):
    """
    暂停资源学习
    POST /api/student/path-nodes/{node_id}/resources/{resource_id}/pause
    """
    user = _get_authenticated_user(request)

    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    # 记录暂停进度
    progress, _ = NodeProgress.objects.get_or_create(
        user=user,
        node=node,
        defaults={"status": "in_progress"},
    )

    # 存储暂停位置（如有前端传来的 position）
    position = request.data.get("position", 0)
    if not progress.extra_data:
        progress.extra_data = {}
    progress.extra_data[f"resource_{resource_id}_position"] = position
    progress.save()

    return success_response(msg="已暂停")
