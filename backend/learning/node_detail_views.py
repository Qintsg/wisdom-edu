from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.responses import error_response, success_response
from learning.node_detail_support import (
    NodeExamMasteryRefresh,
    build_node_detail_payload,
    build_node_exam_context,
    ensure_progress_baseline,
    load_node_for_user,
    mark_node_resource_completed,
    persist_node_exam_histories,
    refresh_node_exam_mastery,
    update_node_exam_progress,
    upsert_node_exam_submission,
)
from learning.view_helpers import _get_authenticated_user


# 维护意图：获取节点任务详情与资源列表 GET /api/path-nodes/{node_id}
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_path_node_detail(request, node_id):
    """
    获取节点任务详情与资源列表
    GET /api/path-nodes/{node_id}
    """
    course_id = request.query_params.get("course_id")

    user = _get_authenticated_user(request)

    node = load_node_for_user(user=user, node_id=node_id, course_id=course_id)
    if node is None:
        return error_response(msg="节点不存在", code=404)

    progress, current_mastery_rate = ensure_progress_baseline(node=node, user=user)
    return success_response(data=build_node_detail_payload(node=node, progress=progress, current_mastery_rate=current_mastery_rate))


# 维护意图：标记资源学习完成 POST /api/path-nodes/{node_id}/resources/{resource_id}/complete 支持内部资源ID（整数）和外部资源ID（ext。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_node_resource(request, node_id, resource_id):
    """
    标记资源学习完成
    POST /api/path-nodes/{node_id}/resources/{resource_id}/complete
    支持内部资源ID（整数）和外部资源ID（ext_前缀字符串）
    """
    user = _get_authenticated_user(request)

    node = load_node_for_user(user=user, node_id=node_id)
    if node is None:
        return error_response(msg="节点不存在", code=404)

    progress, _ = ensure_progress_baseline(node=node, user=user)
    payload = mark_node_resource_completed(progress, resource_id)
    return success_response(data=payload, msg="资源已标记为已学习")


# 维护意图：提交节点练习/小测验结果 POST /api/path-nodes/{node_id}/exams/{exam_id}/submit
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_node_exam(request, node_id, exam_id):
    """
    提交节点练习/小测验结果
    POST /api/path-nodes/{node_id}/exams/{exam_id}/submit
    """
    user = _get_authenticated_user(request)
    answers = request.data.get("answers", {})

    # 验证 answers 格式
    if not isinstance(answers, dict):
        return error_response(msg="答案格式错误，应为字典格式")

    node = load_node_for_user(user=user, node_id=node_id)
    if node is None:
        return error_response(msg="节点不存在", code=404)

    if not node.exam or node.exam.id != exam_id:
        return error_response(msg="测验不属于该节点", code=404)

    exam_context = build_node_exam_context(node, answers)
    upsert_node_exam_submission(
        exam=node.exam,
        user=user,
        answers=answers,
        score=exam_context["score"],
        passed=exam_context["passed"],
    )
    progress, _ = ensure_progress_baseline(node=node, user=user)
    update_node_exam_progress(
        node=node,
        progress=progress,
        exam_id=exam_id,
        passed=exam_context["passed"],
    )
    persist_node_exam_histories(
        user=user,
        node=node,
        answers=answers,
        questions=exam_context["questions"],
        question_result_map=exam_context["question_result_map"],
    )
    mastery_update = refresh_node_exam_mastery(
        NodeExamMasteryRefresh(
            user=user,
            node=node,
            point_stats=exam_context["point_stats"],
            score=exam_context["score"],
            total_score=exam_context["total_score"],
            progress=progress,
        )
    )

    return success_response(
        data={
            "score": exam_context["score"],
            "total_score": exam_context["total_score"],
            "passed": exam_context["passed"],
            "mistakes": exam_context["mistakes"],
            "mastery_update": mastery_update,
            "node_status": node.status,
        },
        msg="测验提交成功",
    )
