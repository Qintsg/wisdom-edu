from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from assessments.models import AssessmentStatus
from common.defense_demo import (
    get_defense_demo_visible_order,
    is_defense_demo_student,
)
from common.responses import error_response, success_response
from common.utils import validate_course_exists
from learning.models import LearningPath
from learning.path_adjustment import (
    insert_remediation_nodes,
    refresh_learning_path_from_mastery,
)
from learning.view_helpers import _get_authenticated_user, _serialize_path_nodes

# 维护意图：获取个性化学习路径 GET /api/learning-path
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_learning_path(request):
    """
    获取个性化学习路径
    GET /api/learning-path
    """
    course_id = request.query_params.get("course_id")
    if not course_id:
        return error_response(msg="缺少课程ID")

    if not validate_course_exists(course_id):
        return error_response(msg="课程不存在", code=404)

    user = _get_authenticated_user(request)

    # 初始评测门禁：未完成全局测评或课程知识测评时，引导前端进入对应评测流程。
    has_global_ability = user.ability_scores.exists()
    has_global_habit = hasattr(user, "habit_preference")
    status = AssessmentStatus.objects.filter(user=user, course_id=course_id).first()
    knowledge_done = status.knowledge_done if status else False
    if not (has_global_ability and has_global_habit and knowledge_done):
        next_step = "ability"
        next_step_msg = "请先完成学习能力评测"
        if has_global_ability and not has_global_habit:
            next_step = "habit"
            next_step_msg = "请先完成学习偏好问卷"
        elif has_global_ability and has_global_habit and not knowledge_done:
            next_step = "knowledge"
            next_step_msg = "请先完成本课程知识评测"

        return success_response(
            data={
                "path_id": None,
                "nodes": [],
                "need_assessment": True,
                "next_step": next_step,
                "next_step_msg": next_step_msg,
                "dynamic": False,
                "generating": False,
            },
            msg="请先完成初始评测",
        )

    path = (
        LearningPath.objects.filter(user=user, course_id=course_id)
        .prefetch_related("nodes")
        .first()
    )

    if not path:
        path = generate_initial_path(user, course_id)

    visible_order = (
        get_defense_demo_visible_order(path, user)
        if is_defense_demo_student(user, path.course)
        else None
    )

    return success_response(
        data={
            "path_id": path.id,
            "nodes": _serialize_path_nodes(path, max_visible_order=visible_order),
            "dynamic": path.is_dynamic,
            "generating": False,
        }
    )


# 维护意图：刷新/调整学习路径 POST /api/learning-path/adjust
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def adjust_learning_path(request):
    """
    刷新/调整学习路径
    POST /api/learning-path/adjust
    """
    course_id = request.data.get("course_id")
    reason = request.data.get("reason", "")

    if not course_id:
        return error_response(msg="缺少课程ID")

    if not validate_course_exists(course_id):
        return error_response(msg="课程不存在", code=404)

    user = _get_authenticated_user(request)
    path = LearningPath.objects.filter(user=user, course_id=course_id).first()

    if not path:
        return error_response(msg="学习路径不存在", code=404)

    if reason in ["manual_refresh", "rebuild", "refresh"]:
        return success_response(
            data=refresh_learning_path_from_mastery(
                path=path,
                user=user,
                course_id=course_id,
            ),
            msg="路径已刷新",
        )

    return success_response(
        data=insert_remediation_nodes(path),
        msg="路径已更新",
    )


# 维护意图：生成初始学习路径
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def generate_initial_path(user, course_id):
    """生成初始学习路径"""
    from courses.models import Course
    from ai_services.services.path_service import PathService

    course = Course.objects.get(id=course_id)
    return PathService().generate_path(user, course)
