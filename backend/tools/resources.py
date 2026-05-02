"""资源导入模块。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from knowledge.models import KnowledgePoint, Resource

from tools.common import clean_nan, get_course, load_json
from tools.knowledge import validate_json

from django.db import transaction


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


def should_skip_existing_resource(course, row: ResourceImportRow, *, replace: bool) -> bool:
    """判断当前资源是否应因同课同标题已存在而跳过。"""
    if replace:
        return False
    return Resource.objects.filter(course=course, title=row.title).exists()


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


def preview_link_resources(queryset, count: int) -> None:
    """输出最多 20 条即将删除的外部链接资源。"""
    for resource in queryset[:20]:
        print(f'  - [{resource.id}] {resource.title} (url={resource.url})')
    if count > 20:
        print(f'  ... 还有 {count - 20} 条')
