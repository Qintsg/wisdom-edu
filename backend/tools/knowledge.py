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
    resolve_path, load_json, get_course,
)
from tools.knowledge_import_support import (
    parse_flat_knowledge_excel,
    parse_hierarchical_knowledge_excel,
    parse_knowledge_excel,
    read_knowledge_import_source,
    sync_knowledge_graph_copy,
    upsert_course_knowledge_edges,
    upsert_course_knowledge_nodes,
    validate_import_json_payload,
    write_tmp_knowledge_json,
)


# 维护意图：校验JSON文件结构
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def validate_json(file: str, schema: str):
    """校验JSON文件结构"""
    validate_import_json_payload(file, schema)
    print(f'校验通过: {file} ({schema})')


# 维护意图：导入知识图谱（JSON格式）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def import_knowledge(file: str, course_id: int, replace: bool = False,
                     dry_run: bool = False):
    """导入知识图谱（JSON格式）"""
    validate_json(file, 'knowledge')
    data = validate_import_json_payload(file, "knowledge")
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
        name_to_point, id_to_point = upsert_course_knowledge_nodes(
            course=course,
            nodes=nodes,
        )
        rel_count = upsert_course_knowledge_edges(
            course=course,
            edges=edges,
            name_to_point=name_to_point,
            id_to_point=id_to_point,
        )

    print(f'知识图谱导入完成: 课程={course.name}, 节点={len(nodes)}, 关系={rel_count}')
    sync_knowledge_graph_copy(course)


# 维护意图：导入知识图谱（支持JSON和Excel格式）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def import_knowledge_map(file_path: str, course_id: Optional[int] = None,
                         course_name: Optional[str] = None):
    """导入知识图谱（支持JSON和Excel格式）"""
    path = resolve_path(file_path)
    if not path.exists():
        print(f'错误：文件不存在 - {path}')
        return {'success': False, 'error': 'file_not_found'}

    if path.suffix.lower() not in ['.json', '.xlsx', '.xls']:
        print(f'错误：不支持的文件格式 - {path.suffix}')
        return {'success': False, 'error': 'unsupported_format'}
    data = read_knowledge_import_source(path)
    if data is None:
        return {'success': False, 'error': 'parse_error'}

    if course_id:
        course = get_course(course_id)
    else:
        cname = course_name or data.get('course_name') or path.stem
        course = Course.objects.create(name=cname, description=f'从 {path.name} 导入')

    tmp_json = write_tmp_knowledge_json(data)
    import_knowledge(str(tmp_json), int(course.pk), replace=False, dry_run=False)

    return {
        'success': True,
        'course_id': int(course.pk),
        'course_name': course.name,
        'node_count': len(data.get('nodes', [])),
        'edge_count': len(data.get('edges', [])),
    }


# 维护意图：解析Excel格式的知识图谱文件
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _parse_knowledge_excel(path: Path) -> Optional[dict]:
    """解析Excel格式的知识图谱文件"""
    return parse_knowledge_excel(path)


# 维护意图：解析层级知识点格式的Excel
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _parse_hierarchical_excel(path: Path, header_row: int) -> dict:
    """解析层级知识点格式的Excel"""
    return parse_hierarchical_knowledge_excel(path, header_row)


# 维护意图：解析普通单sheet格式的Excel
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _parse_flat_excel(path: Path) -> dict:
    """解析普通单sheet格式的Excel"""
    return parse_flat_knowledge_excel(path)


# 维护意图：导出知识图谱为JSON
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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
