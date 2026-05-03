from __future__ import annotations

import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.responses import error_response, success_response
from knowledge.models import KnowledgeMastery
from learning.models import LearningPath, PathNode
from learning.view_helpers import _get_authenticated_user, _path_node_sort_key

logger = logging.getLogger(__name__)

# 维护意图：学生仪表盘聚合数据 GET /api/student/dashboard?course_id=xxx 合并学习进度、路径预览、画像摘要，减少前端并发请求
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    """
    学生仪表盘聚合数据
    GET /api/student/dashboard?course_id=xxx

    合并学习进度、路径预览、画像摘要，减少前端并发请求。
    """
    user = _get_authenticated_user(request)
    course_id = request.query_params.get("course_id")
    if not course_id:
        return error_response(msg="请提供 course_id 参数")

    try:
        course_id = int(course_id)
    except (TypeError, ValueError):
        return error_response(msg="course_id 必须为整数")

    data: dict[str, object] = {
        "progress": 0,
        "study_time": 0,
        "completed_nodes": 0,
        "total_nodes": 0,
        "mastered_points": 0,
        "nodes_preview": [],
        "recent_mastery": [],
        "pending_exams": [],
    }

    # 学习路径进度
    path = LearningPath.objects.filter(user=user, course_id=course_id).first()
    if path:
        nodes = PathNode.objects.filter(path=path).select_related("knowledge_point")
        total = nodes.count()
        completed = nodes.filter(status="completed").count()
        data["total_nodes"] = total
        data["completed_nodes"] = completed
        data["progress"] = completed / total if total > 0 else 0

        # 学习时长（用完成节点数估算，每节点约30分钟）
        data["study_time"] = completed * 30

        # 节点预览（前5个，未完成优先）
        data["nodes_preview"] = [
            {
                "node_id": n.id,
                "knowledge_point_name": n.knowledge_point.name
                if n.knowledge_point
                else "",
                "status": n.status,
                "order": n.order_index,
            }
            for n in sorted(nodes, key=_path_node_sort_key)[:5]
        ]

    # 知识掌握度
    mastery_qs = KnowledgeMastery.objects.filter(
        user=user, course_id=course_id
    ).select_related("knowledge_point")
    mastered = mastery_qs.filter(mastery_rate__gte=0.8).count()
    data["mastered_points"] = mastered

    # 最近更新的5个知识点掌握度
    data["recent_mastery"] = [
        {
            "name": m.knowledge_point.name if m.knowledge_point else "未知",
            "mastery_rate": float(m.mastery_rate),
            "updated_at": m.updated_at.isoformat()
            if hasattr(m, "updated_at") and m.updated_at
            else "",
        }
        for m in mastery_qs.order_by("-updated_at")[:5]
    ]

    # 待完成考试
    try:
        from exams.models import Exam, ExamSubmission

        published_exams = Exam.objects.filter(
            course_id=course_id, status="published", exam_type="exam"
        )
        submitted_ids = ExamSubmission.objects.filter(
            user=user, exam__course_id=course_id
        ).values_list("exam_id", flat=True)
        pending = published_exams.exclude(id__in=submitted_ids)[:3]
        data["pending_exams"] = [
            {"id": e.id, "title": e.title, "duration": e.duration} for e in pending
        ]
    except Exception as e:
        logger.warning("Dashboard待考试数据查询失败: %s", e)

    return success_response(data=data)
