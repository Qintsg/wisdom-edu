"""用户模块 - 管理员用户管理接口。"""

from __future__ import annotations

import logging

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.permissions import IsAdmin
from common.responses import created_response, error_response, success_response
from .admin_helpers import _parse_pagination
from .admin_user_management_support import (
    build_admin_user_detail_payload,
    build_admin_user_list_payload,
    build_user_export_response,
    build_user_import_template_response,
    create_admin_user,
    delete_admin_user,
    delete_admin_users,
    get_admin_user,
    import_admin_users,
    read_user_import_rows,
    reset_admin_user_password,
    set_admin_user_active,
    update_admin_user,
)


logger = logging.getLogger(__name__)


# 维护意图：获取用户列表（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_list(request: Request) -> Response:
    """获取用户列表（管理员）。"""
    page, size = _parse_pagination(request.query_params, size_key="size")
    return success_response(data=build_admin_user_list_payload(request.query_params, page, size))


# 维护意图：获取用户详情（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_detail(request: Request, user_id: int) -> Response:
    """获取用户详情（管理员）。"""
    target_user = get_admin_user(user_id)
    if target_user is None:
        return error_response(msg="用户不存在", code=404)
    return success_response(data=build_admin_user_detail_payload(target_user))


# 维护意图：创建用户（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_create(request: Request) -> Response:
    """创建用户（管理员）。"""
    payload, error_message = create_admin_user(request.data)
    if error_message:
        return error_response(msg=error_message, code=400)
    return created_response(data=payload, msg="用户创建成功")


# 维护意图：更新用户信息（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_update(request: Request, user_id: int) -> Response:
    """更新用户信息（管理员）。"""
    target_user = get_admin_user(user_id)
    if target_user is None:
        return error_response(msg="用户不存在", code=404)
    if target_user.id == request.user.id and "role" in request.data:
        return error_response(msg="不能修改自己的角色", code=400)

    updated_fields, error_message = update_admin_user(target_user, request.data)
    if error_message:
        return error_response(msg=error_message)
    return success_response(
        data={"user_id": target_user.id, "updated_fields": updated_fields},
        msg="用户信息已更新",
    )


# 维护意图：删除用户（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_delete(request: Request, user_id: int) -> Response:
    """删除用户（管理员）。"""
    if user_id == request.user.id:
        return error_response(msg="不能删除自己")
    target_user = get_admin_user(user_id)
    if target_user is None:
        return error_response(msg="用户不存在", code=404)

    username = delete_admin_user(target_user)
    return success_response(msg=f"用户 {username} 已删除")


# 维护意图：重置用户密码（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_reset_password(request: Request, user_id: int) -> Response:
    """重置用户密码（管理员）。"""
    target_user = get_admin_user(user_id)
    if target_user is None:
        return error_response(msg="用户不存在", code=404)

    response_data = reset_admin_user_password(target_user, request.data.get("new_password"))
    return success_response(data=response_data, msg="密码已重置")


# 维护意图：禁用用户（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_disable(request: Request, user_id: int) -> Response:
    """禁用用户（管理员）。"""
    if user_id == request.user.id:
        return error_response(msg="不能禁用自己")
    target_user = get_admin_user(user_id)
    if target_user is None:
        return error_response(msg="用户不存在", code=404)

    return success_response(msg=set_admin_user_active(target_user, False))


# 维护意图：启用用户（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_enable(request: Request, user_id: int) -> Response:
    """启用用户（管理员）。"""
    target_user = get_admin_user(user_id)
    if target_user is None:
        return error_response(msg="用户不存在", code=404)
    return success_response(msg=set_admin_user_active(target_user, True))


# 维护意图：批量删除用户（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_batch_delete(request: Request) -> Response:
    """批量删除用户（管理员）。"""
    user_ids = request.data.get("user_ids", [])
    if not user_ids:
        return error_response(msg="请提供要删除的用户ID列表")

    deleted_count = delete_admin_users(user_ids, request.user.id)
    return success_response(data={"deleted_count": deleted_count}, msg=f"已删除 {deleted_count} 个用户")


# 维护意图：从 Excel/CSV 批量导入用户（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_import(request: Request) -> Response:
    """从 Excel/CSV 批量导入用户（管理员）。"""
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return error_response(msg="请上传文件")

    rows, error_message = read_user_import_rows(uploaded_file)
    if error_message:
        return error_response(msg=error_message)
    created_count, skipped = import_admin_users(rows)
    return success_response(
        data={"created_count": created_count, "skipped": skipped},
        msg=f"成功导入 {created_count} 个用户",
    )


# 维护意图：导出用户列表为 CSV
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_export(request: Request) -> HttpResponse:
    """导出用户列表为 CSV。"""
    return build_user_export_response(request.query_params)


# 维护意图：获取用户导入模板
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_template(request: Request) -> HttpResponse:
    """获取用户导入模板。"""
    logger.debug("管理员下载用户导入模板: admin=%s", getattr(request.user, "id", None))
    return build_user_import_template_response()
