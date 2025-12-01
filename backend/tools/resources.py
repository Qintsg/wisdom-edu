"""
资源导入模块
"""

from knowledge.models import KnowledgePoint, Resource

from tools.common import clean_nan, get_course, load_json
from tools.knowledge import validate_json

from django.db import transaction


def import_resources_json(
    file: str,
    course_id: int,
    replace: bool = False,
    dry_run: bool = False,
):
    """导入资源库（JSON格式）"""
    validate_json(file, 'resources')
    data = load_json(file)
    course = get_course(course_id)
    resources = data.get('resources', [])

    if not resources:
        print('未找到resources，跳过导入。')
        return

    if dry_run:
        print(f'[DRY-RUN] 将导入资源JSON: 课程={course.name}, '
              f'资源={len(resources)}, replace={replace}')
        return

    kp_map = {p.name: p for p in KnowledgePoint.objects.filter(course=course)}
    created = 0

    with transaction.atomic():
        if replace:
            Resource.objects.filter(course=course).delete()

        for idx, item in enumerate(resources):
            title = clean_nan(item.get('title', ''))
            if not title:
                continue

            if not replace and Resource.objects.filter(
                course=course, title=title
            ).exists():
                continue

            resource = Resource.objects.create(
                course=course,
                title=title,
                resource_type=item.get('resource_type') or 'document',
                description=clean_nan(item.get('description', '')),
                url=item.get('url') or None,
                chapter_number=item.get('chapter_number') or None,
                sort_order=idx,
                is_visible=bool(item.get('is_visible', True)),
            )

            for kp_name in item.get('knowledge_points', []):
                kp = kp_map.get(kp_name)
                if kp:
                    resource.knowledge_points.add(kp)
            created += 1

    print(f'资源JSON导入完成: 课程={course.name}, 新增资源={created}')


def delete_link_resources(course_id: int = None, dry_run: bool = True):
    """
    删除数据库中 resource_type='link' 的外部链接资源记录
    
    Args:
        course_id: 指定课程ID（可选，为空则删除所有课程的）
        dry_run: 是否仅预览（默认True）
    """
    qs = Resource.objects.filter(resource_type='link')
    if course_id:
        course = get_course(course_id)
        qs = qs.filter(course=course)
        scope = f'课程={course.name}'
    else:
        scope = '所有课程'

    count = qs.count()
    if count == 0:
        print(f'未找到外部链接资源（{scope}）')
        return

    print(f'\n将要删除的外部链接资源（{scope}，共{count}条）：')
    for resource in qs[:20]:
        print(f'  - [{resource.id}] {resource.title} (url={resource.url})')
    if count > 20:
        print(f'  ... 还有 {count - 20} 条')

    if dry_run:
        print(f'\n[DRY-RUN] 共 {count} 条外部链接资源将被删除。'
              f'使用 --no-dry-run 执行实际删除。')
        return

    deleted, _ = qs.delete()
    print(f'\n已删除 {deleted} 条外部链接资源（{scope}）')
