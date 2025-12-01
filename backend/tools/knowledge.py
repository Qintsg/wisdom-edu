"""
知识图谱导入导出模块

支持JSON和Excel格式的知识图谱导入，以及JSON格式的导出。
"""
import json
from pathlib import Path
from typing import Dict, Optional
from django.db import transaction
from knowledge.models import KnowledgePoint, KnowledgeRelation
from courses.models import Course
from tools.common import (
    BASE_DIR, resolve_path, load_json, get_course,
    split_multi_values, clean_nan,
)
from tools.testing import _status_flag


def validate_json(file: str, schema: str):
    """校验JSON文件结构"""
    data = load_json(file)
    if schema == 'knowledge':
        if not isinstance(data, dict):
            raise ValueError('知识图谱JSON必须是对象')
        if 'nodes' not in data or not isinstance(data['nodes'], list):
            raise ValueError('知识图谱JSON缺少 nodes(list)')
    elif schema == 'questions':
        if not isinstance(data, dict):
            raise ValueError('题库JSON必须是对象')
        if 'questions' not in data or not isinstance(data['questions'], list):
            raise ValueError('题库JSON缺少 questions(list)')
    elif schema == 'resources':
        if not isinstance(data, dict):
            raise ValueError('资源JSON必须是对象')
        if 'resources' not in data or not isinstance(data['resources'], list):
            raise ValueError('资源JSON缺少 resources(list)')
    else:
        raise ValueError(f'未知schema: {schema}')
    print(f'校验通过: {file} ({schema})')


def import_knowledge(file: str, course_id: int, replace: bool = False,
                     dry_run: bool = False):
    """导入知识图谱（JSON格式）"""
    validate_json(file, 'knowledge')
    data = load_json(file)
    course = get_course(course_id)
    nodes = data.get('nodes', [])
    edges = data.get('edges', [])

    if not nodes:
        print('未找到nodes，跳过导入。')
        return

    if dry_run:
        print(f'[DRY-RUN] 将导入知识图谱: 课程={course.name}, '
              f'节点={len(nodes)}, 关系={len(edges)}')
        return

    with transaction.atomic():
        if replace:
            KnowledgeRelation.objects.filter(course=course).delete()
            KnowledgePoint.objects.filter(course=course).delete()

        name_to_point: Dict[str, KnowledgePoint] = {
            p.name: p for p in KnowledgePoint.objects.filter(course=course)
        }
        id_to_point: Dict[str, KnowledgePoint] = {}

        for idx, node in enumerate(nodes):
            node_name = clean_nan(node.get('name', f'知识点{idx + 1}'))
            if not node_name:
                continue

            point = name_to_point.get(node_name)
            if not point:
                point = KnowledgePoint.objects.create(
                    course=course,
                    name=node_name,
                    chapter=clean_nan(node.get('chapter')),
                    description=clean_nan(node.get('description')),
                    level=int(node.get('level') or 1),
                    tags=clean_nan(node.get('tags', '')),
                    cognitive_dimension=clean_nan(node.get('cognitive_dimension', '')),
                    category=clean_nan(node.get('category', '')),
                    teaching_goal=clean_nan(node.get('teaching_goal', '')),
                    order=idx,
                    is_published=True,
                )
                name_to_point[node_name] = point
            else:
                # 仅在现有记录为空时补齐扩展字段，避免覆盖教师已维护的数据。
                updated = False
                for field in ('tags', 'cognitive_dimension', 'category', 'teaching_goal'):
                    new_val = clean_nan(node.get(field, ''))
                    if new_val and not getattr(point, field, ''):
                        setattr(point, field, new_val)
                        updated = True
                desc = clean_nan(node.get('description'))
                if desc and not point.description:
                    point.description = desc
                    updated = True
                if updated:
                    point.save()

            if node.get('id'):
                id_to_point[str(node['id'])] = point

        rel_count = 0
        for edge in edges:
            source_raw = str(edge.get('source', ''))
            target_raw = str(edge.get('target', ''))
            source = id_to_point.get(source_raw) or name_to_point.get(source_raw)
            target = id_to_point.get(target_raw) or name_to_point.get(target_raw)

            if not source or not target or source == target:
                continue

            KnowledgeRelation.objects.get_or_create(
                course=course,
                pre_point=source,
                post_point=target,
                defaults={'relation_type': edge.get('relation') or 'prerequisite'},
            )
            rel_count += 1

    print(f'知识图谱导入完成: 课程={course.name}, 节点={len(nodes)}, 关系={rel_count}')

    # 若图服务可用，则在 PostgreSQL 写入后顺带刷新图谱副本。
    try:
        from common.neo4j_service import neo4j_service
        if neo4j_service.is_available:
            result = neo4j_service.sync_knowledge_graph(int(course.pk))
            print(f'Neo4j同步完成: nodes={result.get("nodes", 0)}, relations={result.get("relations", 0)}')
        else:
            print(f'{_status_flag(False)} Neo4j不可用，跳过同步。知识图谱仅保存在PostgreSQL中。')
    except Exception as e:
        print(f'{_status_flag(False)} Neo4j同步失败: {e}')


def import_knowledge_map(file_path: str, course_id: Optional[int] = None,
                         course_name: Optional[str] = None):
    """导入知识图谱（支持JSON和Excel格式）"""
    path = resolve_path(file_path)
    if not path.exists():
        print(f'错误：文件不存在 - {path}')
        return {'success': False, 'error': 'file_not_found'}

    if path.suffix.lower() == '.json':
        data = load_json(str(path))
    elif path.suffix.lower() in ['.xlsx', '.xls']:
        data = _parse_knowledge_excel(path)
        if data is None:
            return {'success': False, 'error': 'parse_error'}
    else:
        print(f'错误：不支持的文件格式 - {path.suffix}')
        return {'success': False, 'error': 'unsupported_format'}

    if course_id:
        course = get_course(course_id)
    else:
        cname = course_name or data.get('course_name') or path.stem
        course = Course.objects.create(name=cname, description=f'从 {path.name} 导入')

    tmp_json = BASE_DIR / 'runtime_logs' / 'tmp_knowledge_import.json'
    tmp_json.parent.mkdir(parents=True, exist_ok=True)
    tmp_json.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    import_knowledge(str(tmp_json), int(course.pk), replace=False, dry_run=False)

    return {
        'success': True,
        'course_id': int(course.pk),
        'course_name': course.name,
        'node_count': len(data.get('nodes', [])),
        'edge_count': len(data.get('edges', [])),
    }


def _parse_knowledge_excel(path: Path) -> Optional[dict]:
    """解析Excel格式的知识图谱文件"""
    try:
        import pandas as pd
    except ImportError:
        print('错误：未安装pandas，无法解析Excel')
        return None

    xls = pd.ExcelFile(path)

    # 双Sheet格式
    if 'nodes' in xls.sheet_names and 'edges' in xls.sheet_names:
        nodes_df = pd.read_excel(path, sheet_name='nodes')
        edges_df = pd.read_excel(path, sheet_name='edges')
        return {
            'nodes': nodes_df.to_dict('records'),
            'edges': edges_df.to_dict('records')
        }

    # 检测层级知识点格式
    df_raw = pd.read_excel(path, sheet_name=0, header=None, nrows=5)

    is_hierarchical = False
    header_row = 0
    for check_row in range(min(3, len(df_raw))):
        row_vals = [str(v) for v in df_raw.iloc[check_row]]
        if any('级知识点' in v for v in row_vals):
            is_hierarchical = True
            header_row = check_row
            break

    if is_hierarchical:
        return _parse_hierarchical_excel(path, header_row)
    return _parse_flat_excel(path)


def _parse_hierarchical_excel(path: Path, header_row: int) -> dict:
    """解析层级知识点格式的Excel"""
    import pandas as pd

    df = pd.read_excel(path, sheet_name=0, header=header_row)
    columns = [str(c).strip() for c in df.columns]

    cn_num_order = {'一': 1, '二': 2, '三': 3, '四': 4,
                    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
    level_cols = sorted(
        [c for c in columns if '级知识点' in c],
        key=lambda x: cn_num_order.get(x[0], 99)
    )

    pre_col = next((c for c in columns if '前置' in c), None)
    post_col = next((c for c in columns if '后置' in c), None)
    related_col = next((c for c in columns if '关联' in c), None)
    tag_col = next((c for c in columns if '标签' in c), None)
    dim_col = next((c for c in columns if '认知维度' in c), None)
    cat_col = next((c for c in columns if c == '分类'), None)
    desc_col = next((c for c in columns if any(k in c for k in ['知识点说明', '说明', '描述'])), None)
    goal_col = next((c for c in columns if '教学目标' in c), None)

    nodes = []
    edges = []
    id_by_name: Dict[str, str] = {}
    node_id_counter = 0
    current_parents = [''] * len(level_cols)

    for _, row in df.iterrows():
        name = ''
        level = 0
        for lvl_idx, lc in enumerate(level_cols):
            val = clean_nan(row.get(lc, ''))
            if val:
                name = val
                level = lvl_idx + 1
                current_parents[lvl_idx] = name
                for deeper in range(lvl_idx + 1, len(level_cols)):
                    current_parents[deeper] = ''
                break

        if not name:
            continue

        node_id_counter += 1
        node_id = str(node_id_counter)

        chapter_parts = [current_parents[i] for i in range(level - 1) if current_parents[i]]
        chapter = ' > '.join(chapter_parts) if chapter_parts else ''

        tags = clean_nan(row.get(tag_col, '')) if tag_col else ''
        dimension = clean_nan(row.get(dim_col, '')) if dim_col else ''
        category = clean_nan(row.get(cat_col, '')) if cat_col else ''
        description = clean_nan(row.get(desc_col, '')) if desc_col else ''
        goal = clean_nan(row.get(goal_col, '')) if goal_col else ''

        node = {
            'id': node_id, 'name': name,
            'chapter': chapter, 'description': description,
            'level': level,
            'tags': tags,
            'cognitive_dimension': dimension,
            'category': category,
            'teaching_goal': goal,
        }
        nodes.append(node)
        id_by_name[name] = node_id

        # 父子关系
        if level > 1:
            parent_name = current_parents[level - 2]
            if parent_name and parent_name in id_by_name:
                edges.append({'source': id_by_name[parent_name], 'target': node_id, 'relation': 'includes'})

        # 前置/后置/关联
        for col, rel_type, is_source in [
            (pre_col, 'prerequisite', False),
            (post_col, 'prerequisite', True),
            (related_col, 'related', True),
        ]:
            if not col:
                continue
            val = clean_nan(row.get(col, ''))
            if not val:
                continue
            for ref_name in split_multi_values(val):
                if ref_name in id_by_name:
                    src = node_id if is_source else id_by_name[ref_name]
                    tgt = id_by_name[ref_name] if is_source else node_id
                    edges.append({'source': src, 'target': tgt, 'relation': rel_type})

    return {'nodes': nodes, 'edges': edges}


def _parse_flat_excel(path: Path) -> dict:
    """解析普通单sheet格式的Excel"""
    import pandas as pd

    df = pd.read_excel(path, sheet_name=0)
    columns = [str(c) for c in df.columns]

    name_col = next(
        (c for c in columns if any(k in c.lower() for k in ['知识点', '名称', 'name', 'point'])),
        columns[0]
    )
    chapter_col = next(
        (c for c in columns if any(k in c.lower() for k in ['章节', 'chapter', '目录'])),
        None
    )
    desc_col = next(
        (c for c in columns if any(k in c.lower() for k in ['描述', '说明', 'description'])),
        None
    )
    pre_col = next(
        (c for c in columns if any(k in c.lower() for k in ['先修', '前置', 'prerequisite'])),
        None
    )

    nodes = []
    edges = []
    id_by_name: Dict[str, str] = {}

    for i, (_, row) in enumerate(df.iterrows()):
        name = clean_nan(row.get(name_col, ''))
        if not name:
            continue
        node_id = str(i + 1)
        node = {
            'id': node_id, 'name': name,
            'chapter': clean_nan(row.get(chapter_col, '')) if chapter_col else '',
            'description': clean_nan(row.get(desc_col, '')) if desc_col else '',
        }
        nodes.append(node)
        id_by_name[name] = node_id

    if pre_col:
        for i, (_, row) in enumerate(df.iterrows()):
            target_name = clean_nan(row.get(name_col, ''))
            if not target_name:
                continue
            target = id_by_name.get(target_name, target_name)
            pre_value = clean_nan(row.get(pre_col, ''))
            for pre_name in split_multi_values(pre_value):
                source = id_by_name.get(pre_name, pre_name)
                edges.append({'source': source, 'target': target, 'relation': 'prerequisite'})

    return {'nodes': nodes, 'edges': edges}


def export_knowledge_map(course_id: int, output_path: str):
    """导出知识图谱为JSON"""
    course = get_course(course_id)
    points = KnowledgePoint.objects.filter(course=course).order_by('order')
    relations = KnowledgeRelation.objects.filter(course=course)

    data = {
        'course_id': int(course.pk),
        'course_name': course.name,
        'nodes': [
            {'id': p.pk, 'name': p.name, 'description': p.description or '',
             'chapter': p.chapter or '', 'type': p.point_type}
            for p in points
        ],
        'edges': [
            {'source': r.pre_point_id, 'target': r.post_point_id,
             'relation': r.relation_type}
            for r in relations
        ],
    }

    path = resolve_path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'导出完成：{path}')
