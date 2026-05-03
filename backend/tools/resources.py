"""资源导入模块。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from knowledge.models import KnowledgePoint, Resource

from tools.common import clean_nan, get_course, load_json
from tools.knowledge import validate_json

from django.db import transaction


# 维护意图：资源 JSON 中单条可入库记录的规范化结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class ResourceImportRow:
    """资源 JSON 中单条可入库记录的规范化结果。"""

    title: str
    resource_type: str
    description: str
    url: str | None
    chapter_number: str | None
    sort_order: int
    is_visible: bool
    knowledge_points: Sequence[str]


# 维护意图：导入资源库（JSON格式）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def import_resources_json(
    file: str,
    course_id: int,
    replace: bool = False,
    dry_run: bool = False,
) -> None:
    """导入资源库（JSON格式）"""
    validate_json(file, 'resources')
    course = get_course(course_id)
    resource_rows = parse_resource_rows(load_json(file).get('resources', []))

    if not resource_rows:
        print('未找到resources，跳过导入。')
        return

    if dry_run:
        print(f'[DRY-RUN] 将导入资源JSON: 课程={course.name}, '
              f'资源={len(resource_rows)}, replace={replace}')
        return

    with transaction.atomic():
        if replace:
            deleted_count, _ = Resource.objects.filter(course=course).delete()
            print(f'已清理旧资源: 课程={course.name}, 删除={deleted_count}')
        created = create_resource_rows(course, resource_rows, replace=replace)

    print(f'资源JSON导入完成: 课程={course.name}, 新增资源={created}')


# 维护意图：清洗资源 JSON 列表，过滤缺少标题的记录
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_resource_rows(raw_resources: object) -> list[ResourceImportRow]:
    """清洗资源 JSON 列表，过滤缺少标题的记录。"""
    if not isinstance(raw_resources, list):
        return []

    rows: list[ResourceImportRow] = []
    for index, item in enumerate(raw_resources):
        if isinstance(item, Mapping):
            row = build_resource_row(item, sort_order=index)
            if row:
                rows.append(row)
    return rows


# 维护意图：将资源原始字典转换为明确字段，避免入库逻辑反复解析 JSON
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_resource_row(item: Mapping[object, object], sort_order: int) -> ResourceImportRow | None:
    """将资源原始字典转换为明确字段，避免入库逻辑反复解析 JSON。"""
    title = clean_nan(item.get('title', ''))
    if not title:
        return None
    knowledge_points = item.get('knowledge_points', [])
    return ResourceImportRow(
        title=title,
        resource_type=str(item.get('resource_type') or 'document'),
        description=clean_nan(item.get('description', '')),
        url=str(item.get('url')).strip() if item.get('url') else None,
        chapter_number=str(item.get('chapter_number')).strip() if item.get('chapter_number') else None,
        sort_order=sort_order,
        is_visible=bool(item.get('is_visible', True)),
        knowledge_points=[str(name) for name in knowledge_points] if isinstance(knowledge_points, list) else [],
    )


# 维护意图：批量创建资源并绑定知识点，保留 replace=false 时的去重语义
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def create_resource_rows(course, resource_rows: Sequence[ResourceImportRow], *, replace: bool) -> int:
    """批量创建资源并绑定知识点，保留 replace=false 时的去重语义。"""
    kp_map = {point.name: point for point in KnowledgePoint.objects.filter(course=course)}
    created = 0
    for row in resource_rows:
        if should_skip_existing_resource(course, row, replace=replace):
            continue
        resource = create_resource(course, row)
        bind_resource_points(resource, row.knowledge_points, kp_map)
        created += 1
    return created


# 维护意图：判断当前资源是否应因同课同标题已存在而跳过
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def should_skip_existing_resource(course, row: ResourceImportRow, *, replace: bool) -> bool:
    """判断当前资源是否应因同课同标题已存在而跳过。"""
    if replace:
        return False
    return Resource.objects.filter(course=course, title=row.title).exists()


# 维护意图：创建单条学习资源记录
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def create_resource(course, row: ResourceImportRow) -> Resource:
    """创建单条学习资源记录。"""
    return Resource.objects.create(
        course=course,
        title=row.title,
        resource_type=row.resource_type,
        description=row.description,
        url=row.url,
        chapter_number=row.chapter_number,
        sort_order=row.sort_order,
        is_visible=row.is_visible,
    )


# 维护意图：将资源关联到同课程下存在的知识点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def bind_resource_points(
    resource: Resource,
    point_names: Sequence[str],
    kp_map: Mapping[str, KnowledgePoint],
) -> None:
    """将资源关联到同课程下存在的知识点。"""
    for point_name in point_names:
        knowledge_point = kp_map.get(point_name)
        if knowledge_point:
            resource.knowledge_points.add(knowledge_point)


# 维护意图：删除数据库中 resource_type='link' 的外部链接资源记录
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def delete_link_resources(course_id: int | None = None, dry_run: bool = True) -> None:
    """
    删除数据库中 resource_type='link' 的外部链接资源记录

    Args:
        course_id: 指定课程ID（可选，为空则删除所有课程的）
        dry_run: 是否仅预览（默认True）
    """
    queryset = Resource.objects.filter(resource_type='link')
    if course_id:
        course = get_course(course_id)
        queryset = queryset.filter(course=course)
        scope = f'课程={course.name}'
    else:
        scope = '所有课程'

    count = queryset.count()
    if count == 0:
        print(f'未找到外部链接资源（{scope}）')
        return

    print(f'\n将要删除的外部链接资源（{scope}，共{count}条）：')
    preview_link_resources(queryset, count)

    if dry_run:
        print(f'\n[DRY-RUN] 共 {count} 条外部链接资源将被删除。'
              f'使用 --no-dry-run 执行实际删除。')
        return

    deleted, _ = queryset.delete()
    print(f'\n已删除 {deleted} 条外部链接资源（{scope}）')


# 维护意图：输出最多 20 条即将删除的外部链接资源
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def preview_link_resources(queryset, count: int) -> None:
    """输出最多 20 条即将删除的外部链接资源。"""
    for resource in queryset[:20]:
        print(f'  - [{resource.id}] {resource.title} (url={resource.url})')
    if count > 20:
        print(f'  ... 还有 {count - 20} 条')
