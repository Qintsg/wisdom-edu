"""演示环境重建工具。"""

from __future__ import annotations

from common.defense_demo import (
    DEFENSE_DEMO_TEACHER_USERNAME,
    ensure_defense_demo_accounts,
    ensure_defense_demo_environment,
)
from common.neo4j_service import neo4j_service
from tools.bootstrap import bootstrap_course_assets
from tools.db_management import pg_bootstrap
from tools.rebuild_demo_support import (
    assert_demo_graph_ready,
    load_demo_course,
    print_assistant_demo_queries,
    print_demo_course_summary,
    print_demo_followup_hint,
    print_demo_user_statuses,
    sync_demo_course_runtime,
)


# 维护意图：重建演示库并校验课程、图谱和学生示例数据是否齐备
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def rebuild_demo_data(
    course_name: str = '大数据技术与应用',
    teacher: str = DEFENSE_DEMO_TEACHER_USERNAME,
    resources_root: str | None = None,
) -> None:
    """重建演示库并校验课程、图谱和学生示例数据是否齐备。"""
    print('开始全库重建并导入演示数据...')
    pg_bootstrap(run_migrate=True, clear_first=True)
    ensure_defense_demo_accounts()
    sync_graph = neo4j_service.is_available
    bootstrap_course_assets(
        course_name=course_name,
        teacher=teacher,
        replace=True,
        sync_graph=sync_graph,
        dry_run=False,
        resources_root=resources_root,
    )
    # DEFENSE_DEMO_PRESET: 答辩模式需要确定性的账号、班级、路径与反馈状态，
    # 因此在课程资产导入后统一补齐演示专用实体，再重新同步图谱与统计。
    demo_summary = ensure_defense_demo_environment(course_name)

    course = load_demo_course(course_name)
    if course:
        synced_exam_count, graph_stats = sync_demo_course_runtime(
            course=course,
            sync_graph=sync_graph,
        )
        # 演示环境依赖图谱能力，课程存在但图为空时应尽快中断，避免前端
        # 进入演示后才暴露知识图谱或 RAG 链路缺失的问题。
        assert_demo_graph_ready(
            course=course,
            sync_graph=sync_graph,
            graph_stats=graph_stats,
        )
        print_demo_course_summary(
            course=course,
            demo_summary=demo_summary,
            sync_graph=sync_graph,
            synced_exam_count=synced_exam_count,
            graph_stats=graph_stats,
        )
        print_assistant_demo_queries(course)
        print_demo_user_statuses(course, demo_summary)
        print_demo_followup_hint()
    else:
        print(f'警告: 未找到课程 {course_name}，请检查资源目录与导入日志。')
