"""用户模块 - 管理员激活码接口。"""

import csv
from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdmin
from common.responses import created_response, error_response, success_response
from .admin_helpers import UTF8_BOM, _parse_pagination
from .models import ActivationCode


# 维护意图：生成激活码（仅管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def generate_activation_code(request):
    """生成激活码（仅管理员）。"""
    user = request.user
    code_type = request.data.get('code_type', 'teacher')
    if code_type not in ['teacher', 'admin']:
        return error_response(msg='无效的激活码类型', code=400)

    try:
        count = min(int(request.data.get('count', 1)), 50)
        if count < 1:
            count = 1
    except (ValueError, TypeError):
        count = 1

    try:
        expires_days = int(request.data.get('expires_days', 0))
        if expires_days < 0:
            expires_days = 0
    except (ValueError, TypeError):
        expires_days = 0

    expires_at = timezone.now() + timedelta(days=expires_days) if expires_days > 0 else None
    remark = request.data.get('remark', '')
    codes = []
    for _ in range(count):
        code = ActivationCode.objects.create(
            code=ActivationCode.generate_code(),
            code_type=code_type,
            created_by=user,
            expires_at=expires_at,
            remark=remark,
        )
        codes.append({
            'code': code.code,
            'code_type': code.code_type,
            'expires_at': code.expires_at.isoformat() if code.expires_at else None,
        })

    return created_response(data={'codes': codes}, msg=f'成功生成 {count} 个激活码')


# 维护意图：获取激活码列表（仅管理员）
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def list_activation_codes(request):
    """获取激活码列表（仅管理员）。"""
    queryset = ActivationCode.objects.all()
    code_type = request.query_params.get('code_type')
    if code_type:
        queryset = queryset.filter(code_type=code_type)

    is_used = request.query_params.get('is_used')
    if is_used is not None:
        queryset = queryset.filter(is_used=is_used.lower() == 'true')

    page, page_size = _parse_pagination(request.query_params)
    start = (page - 1) * page_size
    end = start + page_size
    total = queryset.count()
    codes = queryset.select_related('used_by')[start:end]

    return success_response(data={
        'total': total,
        'page': page,
        'page_size': page_size,
        'codes': [
            {
                'id': code.id,
                'code': code.code,
                'code_type': code.code_type,
                'is_used': code.is_used,
                'used_by': code.used_by.username if code.used_by else None,
                'used_at': code.used_at.isoformat() if code.used_at else None,
                'expires_at': code.expires_at.isoformat() if code.expires_at else None,
                'remark': code.remark,
                'created_at': code.created_at.isoformat(),
            }
            for code in codes
        ],
    })


# 维护意图：获取激活码详情 / 删除激活码（仅管理员）
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def delete_activation_code(request, code_id):
    """获取激活码详情 / 删除激活码（仅管理员）。"""
    try:
        code = ActivationCode.objects.get(id=code_id)
    except ActivationCode.DoesNotExist:
        return error_response(msg='激活码不存在', code=404)

    if request.method == 'GET':
        return success_response(data={
            'id': code.id,
            'code': code.code,
            'code_type': code.code_type,
            'is_used': code.is_used,
            'used_by': code.used_by.username if code.used_by else None,
            'used_at': code.used_at.isoformat() if code.used_at else None,
            'expires_at': code.expires_at.isoformat() if code.expires_at else None,
            'remark': code.remark,
            'created_at': code.created_at.isoformat(),
        })

    if code.is_used:
        return error_response(msg='已使用的激活码不能删除', code=400)
    code.delete()
    return success_response(msg='激活码已删除')


# 维护意图：获取激活码详情（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def activation_code_detail(request, code_id):
    """获取激活码详情（管理员）。"""
    try:
        code = ActivationCode.objects.get(id=code_id)
    except ActivationCode.DoesNotExist:
        return error_response(msg='激活码不存在', code=404)

    return success_response(data={
        'id': code.id,
        'code': code.code,
        'code_type': code.code_type,
        'is_used': code.is_used,
        'used_by': code.used_by.username if code.used_by else None,
        'used_at': code.used_at.isoformat() if code.used_at else None,
        'expires_at': code.expires_at.isoformat() if code.expires_at else None,
        'remark': code.remark,
        'created_at': code.created_at.isoformat(),
        'created_by': code.created_by.username if code.created_by else None,
    })


# 维护意图：批量删除激活码（管理员）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def activation_code_batch_delete(request):
    """批量删除激活码（管理员）。"""
    code_ids = request.data.get('code_ids', [])
    if not code_ids:
        return error_response(msg='请提供激活码ID列表', code=400)

    deleted_count, _ = ActivationCode.objects.filter(id__in=code_ids, is_used=False).delete()
    return success_response(data={'deleted_count': deleted_count}, msg=f'已删除 {deleted_count} 个激活码')


# 维护意图：验证激活码有效性
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['POST'])
@permission_classes([])
def activation_code_validate(request):
    """验证激活码有效性。"""
    code_str = request.data.get('code')
    if not code_str:
        return error_response(msg='请提供激活码', code=400)

    try:
        code = ActivationCode.objects.get(code=code_str)
    except ActivationCode.DoesNotExist:
        return error_response(msg='激活码不存在', code=404)

    return success_response(data={
        'code': code.code,
        'code_type': code.code_type,
        'is_valid': code.is_valid(),
        'is_used': code.is_used,
        'expires_at': code.expires_at.isoformat() if code.expires_at else None,
    })


# 维护意图：导出激活码列表为 CSV
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def activation_code_export(request):
    """导出激活码列表为 CSV。"""
    queryset = ActivationCode.objects.all().select_related('used_by', 'created_by')
    code_type = request.query_params.get('code_type')
    if code_type:
        queryset = queryset.filter(code_type=code_type)

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="activation_codes.csv"'
    response.write(UTF8_BOM)

    writer = csv.writer(response)
    writer.writerow(['ID', '激活码', '类型', '已使用', '使用者', '使用时间', '过期时间', '备注', '创建时间'])
    for code in queryset[:10000]:
        writer.writerow([
            code.id,
            code.code,
            code.code_type,
            '是' if code.is_used else '否',
            code.used_by.username if code.used_by else '',
            code.used_at.strftime('%Y-%m-%d %H:%M:%S') if code.used_at else '',
            code.expires_at.strftime('%Y-%m-%d %H:%M:%S') if code.expires_at else '永不过期',
            code.remark or '',
            code.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response
