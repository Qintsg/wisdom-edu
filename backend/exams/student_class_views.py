"""学生端班级相关考试视图。"""
from __future__ import annotations

import logging

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.logging_utils import build_log_message
from common.responses import error_response, success_response

from .models import Exam, ExamSubmission


logger = logging.getLogger(__name__)


# 维护意图：获取班级成员列表
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_class_members(request, class_id):
    """获取班级成员列表。"""
    from courses.models import Class, Enrollment
    from users.models import User

    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    if not Enrollment.objects.filter(class_obj=class_obj, user=request.user).exists():
        return error_response(msg="您不是该班级成员", code=403)

    members = User.objects.filter(id__in=Enrollment.objects.filter(class_obj=class_obj).values_list("user_id", flat=True))
    return success_response(data=[{"user_id": member.id, "username": member.username, "real_name": member.real_name} for member in members])


# 维护意图：获取班级学习排行榜
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_class_ranking(request, class_id):
    """获取班级学习排行榜。"""
    from courses.models import Class, Enrollment
    from knowledge.models import KnowledgeMastery

    logger.debug(build_log_message("exam.student_class_ranking.request", user_id=getattr(request.user, "id", None), class_id=class_id))
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    ranking = []
    enrollments = Enrollment.objects.filter(class_obj=class_obj).select_related("user")
    for enrollment in enrollments:
        rates = [float(mastery.mastery_rate) for mastery in KnowledgeMastery.objects.filter(user=enrollment.user)]
        avg_mastery = sum(rates) / len(rates) if rates else 0
        ranking.append({
            "user_id": enrollment.user_id,
            "username": enrollment.user.username,
            "real_name": enrollment.user.real_name,
            "avg_mastery": round(avg_mastery, 2),
        })
    ranking.sort(key=lambda item: item["avg_mastery"], reverse=True)
    for index, row in enumerate(ranking, 1):
        row["rank"] = index
    return success_response(data=ranking)


# 维护意图：获取班级通知公告（简版）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_class_notifications(request, class_id):
    """获取班级通知公告（简版）。"""
    from courses.models import Class, ClassCourse

    logger.debug(build_log_message("exam.student_class_notifications.request", user_id=getattr(request.user, "id", None), class_id=class_id))
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    course_ids = ClassCourse.objects.filter(class_obj=class_obj).values_list("course_id", flat=True)
    exams = Exam.objects.filter(course_id__in=course_ids, status="published").order_by("-created_at")[:10]
    return success_response(data=[{
        "id": exam.id,
        "title": f"新作业：{exam.title}",
        "type": "exam",
        "created_at": exam.created_at.isoformat() if exam.created_at else "",
    } for exam in exams])


# 维护意图：获取班级作业列表（映射到考试列表）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_class_assignments(request, class_id):
    """获取班级作业列表（映射到考试列表）。"""
    from courses.models import Class, ClassCourse

    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    course_ids = ClassCourse.objects.filter(class_obj=class_obj).values_list("course_id", flat=True)
    exams = Exam.objects.filter(course_id__in=course_ids, status="published").order_by("-created_at")
    submitted_ids = set(ExamSubmission.objects.filter(user=request.user, exam__in=exams, score__gte=0).values_list("exam_id", flat=True))
    return success_response(data=[{
        "id": exam.id,
        "title": exam.title,
        "course_name": exam.course.name if exam.course else "",
        "status": "submitted" if exam.id in submitted_ids else "pending",
        "created_at": exam.created_at.isoformat() if exam.created_at else "",
    } for exam in exams])
