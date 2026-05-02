"""教师端班级邀请码管理视图。"""
from __future__ import annotations

import random
import string
from datetime import timedelta

from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsTeacherOrAdmin
from common.responses import created_response, error_response, forbidden_response, success_response
from users.models import ClassInvitation

from .models import Class


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def generate_class_invitation(request):
    """生成班级邀请码。"""
    user = request.user
    class_id = request.data.get("class_id")
    max_uses = request.data.get("max_uses", 100)
    expires_days = request.data.get("expires_days", 30)
    if not class_id:
        return error_response(msg="请提供班级ID", code=400)
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    if user.role == "teacher" and class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权为此班级生成邀请码")
    try:
        max_uses = int(max_uses)
        expires_days = int(expires_days)
    except (TypeError, ValueError):
        return error_response(msg="邀请码配置格式错误", code=400)
    if max_uses < 0:
        return error_response(msg="最大使用次数不能小于0", code=400)
    if expires_days < 1 or expires_days > 365:
        return error_response(msg="有效天数需在1到365天之间", code=400)

    code = None
    for _ in range(10):
        candidate = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not ClassInvitation.objects.filter(code=candidate).exists():
            code = candidate
            break
    if code is None:
        return error_response(msg="邀请码生成失败，请重试", code=500)

    invitation = ClassInvitation.objects.create(code=code, class_obj=class_obj, created_by=user, max_uses=max_uses, expires_at=timezone.now() + timedelta(days=expires_days))
    course_name = class_obj.course.name if class_obj.course else None
    return created_response(data={
        "invitation_id": invitation.id,
        "code": invitation.code,
        "class_id": class_obj.id,
        "class_name": class_obj.name,
        "course_name": course_name,
        "max_uses": invitation.max_uses,
        "use_count": invitation.use_count,
        "expires_at": invitation.expires_at.isoformat() if invitation.expires_at else None,
        "is_active": invitation.is_active,
        "is_valid": invitation.is_valid(),
        "created_at": invitation.created_at.isoformat(),
    }, msg="邀请码生成成功")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def list_class_invitations(request, class_id):
    """获取班级邀请码列表。"""
    user = request.user
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)
    if user.role == "teacher" and class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权查看此班级的邀请码")
    invitations = ClassInvitation.objects.filter(class_obj=class_obj).order_by("-created_at")
    return success_response(data={"class_id": class_id, "class_name": class_obj.name, "invitations": [{"id": invitation.id, "code": invitation.code, "max_uses": invitation.max_uses, "use_count": invitation.use_count, "expires_at": invitation.expires_at.isoformat() if invitation.expires_at else None, "is_active": invitation.is_active, "is_valid": invitation.is_valid(), "created_at": invitation.created_at.isoformat()} for invitation in invitations]})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacherOrAdmin])
def delete_class_invitation(request, invitation_id):
    """删除班级邀请码。"""
    user = request.user
    try:
        invitation = ClassInvitation.objects.get(id=invitation_id)
    except ClassInvitation.DoesNotExist:
        return error_response(msg="邀请码不存在", code=404)
    if user.role == "teacher" and invitation.class_obj.teacher_id != user.id:
        return forbidden_response(msg="无权删除此邀请码")
    invitation.delete()
    return success_response(msg="邀请码已删除")
