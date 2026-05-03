"""
操作日志模块 - 视图
Operation Logs Module - Views

提供管理员查看操作日志的API接口
Provides API endpoints for admins to view operation logs
"""
import csv
import codecs
import io
from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from django.core.paginator import Paginator
from django.db.models import Count, Q, QuerySet
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.utils import timezone
from typing import Protocol, TypeGuard

from .models import OperationLog
from .serializers import OperationLogSerializer
from common.responses import success_response, error_response, forbidden_response


UTF8_BOM = codecs.BOM_UTF8.decode('utf-8')


# 维护意图：描述日志管理接口所需的最小用户能力集
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class _AdminCapableUser(Protocol):
    """描述日志管理接口所需的最小用户能力集。"""

    role: str
    is_superuser: bool


# 维护意图：统一应用日志列表与导出的筛选条件
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _apply_log_filters(request: Request, queryset: QuerySet[OperationLog]) -> QuerySet[OperationLog]:
    """统一应用日志列表与导出的筛选条件。"""
    action_type = request.query_params.get('action_type')
    module = request.query_params.get('module')
    user_id = request.query_params.get('user_id')
    start_date = request.query_params.get('start_date') or request.query_params.get('start_time')
    end_date = request.query_params.get('end_date') or request.query_params.get('end_time')
    keyword = request.query_params.get('keyword')

    if action_type:
        queryset = queryset.filter(action_type=action_type)
    if module:
        queryset = queryset.filter(module=module)
    if user_id:
        queryset = queryset.filter(user_id=user_id)

    # 日期筛选 - 兼容 ISO 格式和 YYYY-MM-DD
    if start_date:
        # 如果是 ISO 格式，只取日期部分
        if 'T' in start_date:
            start_date = start_date.split('T')[0]
        queryset = queryset.filter(created_at__date__gte=start_date)

    if end_date:
        if 'T' in end_date:
            end_date = end_date.split('T')[0]
        queryset = queryset.filter(created_at__date__lte=end_date)

    # 关键字搜索
    if keyword:
        queryset = queryset.filter(
            Q(description__icontains=keyword)
            | Q(user__username__icontains=keyword)
            | Q(error_message__icontains=keyword)
            | Q(request_path__icontains=keyword)
        )

    return queryset


# 维护意图：检查用户是否为管理员
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def is_admin(user: AbstractBaseUser | AnonymousUser) -> TypeGuard[_AdminCapableUser]:
    """检查用户是否为管理员"""
    return bool(getattr(user, 'role', None) == 'admin' or getattr(user, 'is_superuser', False))


# 维护意图：获取操作日志列表（仅管理员可访问） GET /api/logs/ 查询参数： - page: 页码（默认1） - page_size: 每页数量（默认20，最大100） - action_ty。
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_operation_logs(request):
    """
    获取操作日志列表（仅管理员可访问）
    GET /api/logs/
    
    查询参数：
    - page: 页码（默认1）
    - page_size: 每页数量（默认20，最大100）
    - action_type: 操作类型筛选
    - module: 模块筛选
    - user_id: 用户ID筛选
    - start_date: 开始日期（YYYY-MM-DD）
    - end_date: 结束日期（YYYY-MM-DD）
    """
    # 权限检查
    if not is_admin(request.user):
        return forbidden_response(msg='权限不足，仅管理员可查看操作日志')

    page = request.query_params.get('page', 1)

    # 兼容前端 size 参数
    size_param = request.query_params.get('page_size') or request.query_params.get('size') or 20
    try:
        page_size = min(int(size_param), 100)
        page_size = max(1, page_size)
    except (ValueError, TypeError):
        page_size = 20

    keyword = request.query_params.get('keyword')
    level = request.query_params.get('level')  # info/error

    # 构建查询
    queryset = _apply_log_filters(request, OperationLog.objects.all().select_related('user'))

    # 级别筛选 (映射 is_success)
    if level:
        if level.lower() == 'error':
            queryset = queryset.filter(is_success=False)
        elif level.lower() == 'info':
            queryset = queryset.filter(is_success=True)

    # 分页
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    # 序列化
    serializer = OperationLogSerializer(page_obj.object_list, many=True)

    return success_response(
        data={
            'results': serializer.data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
    )


# 维护意图：获取操作日志详情（仅管理员可访问） GET /api/logs/{log_id}/
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_operation_log_detail(request, log_id):
    """
    获取操作日志详情（仅管理员可访问）
    GET /api/logs/{log_id}/
    """
    # 权限检查
    if not is_admin(request.user):
        return forbidden_response(msg='权限不足，仅管理员可查看操作日志')

    try:
        log = OperationLog.objects.get(id=log_id)
    except OperationLog.DoesNotExist:
        return error_response(msg='日志不存在', code=404)

    serializer = OperationLogSerializer(log)
    return success_response(data=serializer.data)


# 维护意图：获取操作日志统计信息（仅管理员可访问） GET /api/logs/statistics/ 返回： - 按操作类型统计 - 按模块统计 - 按日期统计（最近7天）
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_log_statistics(request):
    """
    获取操作日志统计信息（仅管理员可访问）
    GET /api/logs/statistics/
    
    返回：
    - 按操作类型统计
    - 按模块统计
    - 按日期统计（最近7天）
    """
    # 权限检查
    if not is_admin(request.user):
        return forbidden_response(msg='权限不足，仅管理员可查看操作日志')

    # 按操作类型统计
    action_stats = OperationLog.objects.values('action_type').annotate(
        count=Count('id')
    ).order_by('-count')

    # 按模块统计
    module_stats = OperationLog.objects.values('module').annotate(
        count=Count('id')
    ).order_by('-count')

    # 最近7天统计
    seven_days_ago = timezone.now() - timedelta(days=7)
    daily_stats = OperationLog.objects.filter(
        created_at__gte=seven_days_ago
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')

    return success_response(
        data={
            'by_action_type': list(action_stats),
            'by_module': list(module_stats),
            'daily': list(daily_stats)
        }
    )


# 维护意图：获取日志筛选选项 GET /api/logs/options/
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_log_filter_options(request):
    """
    获取日志筛选选项
    GET /api/logs/options/
    """
    # 权限检查
    if not is_admin(request.user):
        return forbidden_response(msg='权限不足，仅管理员可查看操作日志')

    return success_response(data={
        'action_types': [{'value': k, 'label': v} for k, v in OperationLog.ACTION_TYPES],
        'modules': [{'value': k, 'label': v} for k, v in OperationLog.MODULE_CHOICES]
    })


# 维护意图：获取日志模块列表 GET /api/admin/logs/modules/
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_log_modules(request):
    """
    获取日志模块列表
    GET /api/admin/logs/modules/
    """
    if not is_admin(request.user):
        return forbidden_response()

    modules = [{'value': k, 'label': v} for k, v in OperationLog.MODULE_CHOICES]
    return success_response(data=modules)


# 维护意图：获取日志操作类型列表 GET /api/admin/logs/actions/
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_log_actions(request):
    """
    获取日志操作类型列表
    GET /api/admin/logs/actions/
    """
    if not is_admin(request.user):
        return forbidden_response()

    actions = [{'value': k, 'label': v} for k, v in OperationLog.ACTION_TYPES]
    return success_response(data=actions)


# 维护意图：导出操作日志为 CSV GET /api/admin/logs/export/ 支持与 list_operation_logs 相同的筛选参数
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_logs(request):
    """
    导出操作日志为 CSV
    GET /api/admin/logs/export/

    支持与 list_operation_logs 相同的筛选参数
    """
    if not is_admin(request.user):
        return forbidden_response()

    # 复用筛选逻辑
    queryset = _apply_log_filters(request, OperationLog.objects.all().select_related('user'))

    # 限制导出数量
    queryset = queryset[:10000]

    # 构造HTTP响应
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="operation_logs.csv"'
    # 写入文件内容
    response.write(UTF8_BOM)  # BOM for Excel UTF-8

    writer = csv.writer(response)
    writer.writerow(['ID', '用户', '操作', '模块', '路径', '描述', '成功', '错误信息', '时间'])

    action_map = dict(OperationLog.ACTION_TYPES)
    module_map = dict(OperationLog.MODULE_CHOICES)

    for log in queryset:
        writer.writerow([
            log.id,
            log.user.username if log.user else '-',
            action_map.get(log.action_type, log.action_type),
            module_map.get(log.module, log.module),
            log.request_path,
            log.description,
            '是' if log.is_success else '否',
            log.error_message or '',
            log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
        ])

    return response


# 维护意图：清理过期日志 DELETE /api/admin/logs/clean/ 查询参数： - days: 保留最近N天的日志（默认90）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clean_expired_logs(request):
    """
    清理过期日志
    DELETE /api/admin/logs/clean/

    查询参数：
    - days: 保留最近N天的日志（默认90）
    """
    if not is_admin(request.user):
        return forbidden_response()

    days = int(request.query_params.get('days', 90))
    if days < 7:
        return error_response(msg='保留天数不能少于7天')

    cutoff = timezone.now() - timedelta(days=days)
    deleted_count, _ = OperationLog.objects.filter(created_at__lt=cutoff).delete()

    return success_response(data={
        'deleted_count': deleted_count,
        'kept_days': days,
    }, msg=f'已清理 {deleted_count} 条过期日志')
