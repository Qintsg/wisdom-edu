"""
Neo4j 图数据库操作模块

合并了原 neo4j_tools.py（数据管理）和 neo4j_testing.py（测试导入），
提供完整的 Neo4j 管理功能。
"""

from typing import Optional

from common.neo4j_service import neo4j_service
from courses.models import Course


# 维护意图：同步课程知识图谱到Neo4j
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def sync_neo4j(course_id: int):
    """同步课程知识图谱到Neo4j"""
    neo4j_service.reset_connection_state()
    if not neo4j_service.is_available:
        raise RuntimeError('Neo4j不可用，无法同步知识图谱。')

    result = neo4j_service.sync_knowledge_graph(course_id)
    stats = neo4j_service.get_graph_stats(course_id)
    if stats.get('node_count', 0) <= 0:
        raise RuntimeError(f'Neo4j同步后课程 {course_id} 图数据仍为空。')

    print(f"Neo4j同步完成: nodes={result.get('nodes', 0)}, "
          f"relations={result.get('relations', 0)}")
    return result


# 维护意图：查看Neo4j状态
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def neo4j_status():
    """查看Neo4j状态"""
    print('Neo4j状态：')
    print('可用' if neo4j_service.is_available else '不可用')
    if not neo4j_service.is_available:
        return

    for c in Course.objects.all().order_by('id'):
        stats = neo4j_service.get_graph_stats(int(c.pk))
        print(f"- {c.name}: nodes={stats.get('nodes', 0)}, "
              f"relations={stats.get('relations', 0)}")


# 维护意图：同步所有课程到Neo4j
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def neo4j_sync_all():
    """同步所有课程到Neo4j"""
    if not neo4j_service.is_available:
        print('Neo4j不可用，跳过。')
        return

    total_nodes = total_rel = 0
    for c in Course.objects.all().order_by('id'):
        result = neo4j_service.sync_knowledge_graph(int(c.pk))
        total_nodes += result.get('nodes', 0)
        total_rel += result.get('relations', 0)
        print(f"- 已同步 {c.name}: nodes={result.get('nodes', 0)}, "
              f"relations={result.get('relations', 0)}")

    print(f'全部完成: nodes={total_nodes}, relations={total_rel}')


# 维护意图：清理Neo4j图数据
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def neo4j_clear(course_id: Optional[int] = None, yes: bool = False):
    """清理Neo4j图数据"""
    if not neo4j_service.is_available:
        print('Neo4j不可用，跳过。')
        return

    if not yes:
        confirm = input('将清理Neo4j数据，继续? (y/N): ').strip().lower()
        if confirm != 'y':
            print('已取消')
            return

    if course_id:
        result = neo4j_service.clear_course_graph(course_id)
        if result:
            print(f'已清理课程 {course_id} 的图数据')
        else:
            print(f'课程 {course_id} 图数据清理失败')
    else:
        neo4j_service.clear_all()
        print('已清理全部图数据')


# ── 以下函数从 neo4j_testing.py 合并 ──

# 维护意图：测试Neo4j连接并同步前两个课程的知识图谱
# 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
# 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
def test_neo4j_connection():
    """测试Neo4j连接并同步前两个课程的知识图谱"""
    print('开始Neo4j测试...')
    if not neo4j_service.is_available:
        print('  ⚠ Neo4j不可用，跳过。')
        return

    print('  ✓ Neo4j连接成功')

    for c in Course.objects.all()[:2]:
        result = neo4j_service.sync_knowledge_graph(int(getattr(c, 'pk', 0)))
        print(f"  - {c.name}: nodes={result.get('nodes', 0)}, "
              f"relations={result.get('relations', 0)}")


# 维护意图：从testdata.json5导入Neo4j测试数据
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def import_neo4j_test_data():
    """从testdata.json5导入Neo4j测试数据"""
    from tools.testing import _load_testdata

    data = _load_testdata()
    if not data:
        return

    graphs = data.get('neo4j_knowledge_graph', [])
    if not graphs:
        print('未找到neo4j_knowledge_graph配置。')
        return

    if not neo4j_service.is_available:
        print('Neo4j不可用。')
        return

    for g in graphs:
        result = neo4j_service.import_test_data(g)
        course_identifier = g.get('course_name', g.get('course_id'))
        print(f"已导入 {course_identifier}: "
              f"nodes={result.get('nodes', 0)}, "
              f"relations={result.get('relations', 0)}")


# 维护意图：清空Neo4j数据库中的所有数据
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def clear_neo4j_data(yes: bool = False):
    """清空Neo4j数据库中的所有数据

    Args:
        yes (bool): 是否跳过确认提示直接执行
    """
    if not neo4j_service.is_available:
        print('Neo4j不可用。')
        return

    if not yes:
        confirm = input('⚠ 将清空Neo4j全部数据，继续？(y/N): ').strip().lower()
        if confirm != 'y':
            print('已取消。')
            return

    result = neo4j_service.clear_all()
    print(f"已清理: nodes={result.get('nodes_deleted', 0)}, "
          f"relations={result.get('relations_deleted', 0)}")
