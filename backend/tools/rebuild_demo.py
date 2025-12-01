"""演示环境重建工具。"""

from __future__ import annotations

from assessments.models import AnswerHistory, AssessmentResult, AssessmentStatus
from common.defense_demo import (
    DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS,
    DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME,
    DEFENSE_DEMO_SUPPORT_COURSE_NAME,
    DEFENSE_DEMO_TEACHER_USERNAME,
    DEFENSE_DEMO_WARMUP_STUDENT_USERNAME,
    ensure_defense_demo_accounts,
    ensure_defense_demo_environment,
)
from common.neo4j_service import neo4j_service
from courses.models import Course
from exams.models import FeedbackReport
from exams.score_policy import sync_course_exam_totals
from knowledge.models import ProfileSummary
from learning.models import LearningPath
from users.models import User

from tools.bootstrap import bootstrap_course_assets
from tools.db_management import pg_bootstrap


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

    course = Course.objects.filter(name=course_name).first()
    if course:
        if sync_graph:
            neo4j_service.sync_knowledge_graph(course.id)
        synced_exam_count = sync_course_exam_totals(course.id)
        # 演示环境依赖图谱能力，课程存在但图为空时应尽快中断，避免前端
        # 进入演示后才暴露知识图谱或 RAG 链路缺失的问题。
        graph_stats = neo4j_service.get_graph_stats(course.id) if neo4j_service.is_available else {}
        if sync_graph and graph_stats.get('node_count', 0) <= 0:
            raise RuntimeError(f'课程 {course.id} 的 Neo4j 图数据为空，请检查同步链路。')
        print(f'演示课程已就绪: id={course.id}, name={course.name}')
        print(f'  - 已同步考试总分口径: {synced_exam_count} 场')
        print(f'  - Neo4j图数据: nodes={graph_stats.get("node_count", 0)}, relations={graph_stats.get("relation_count", 0)}')
        if not sync_graph:
            print('  - 警告: 当前环境未连接 Neo4j，本次演示将使用 PostgreSQL 回退图数据。')
        print(
            f'  - 答辩账号: teacher={DEFENSE_DEMO_TEACHER_USERNAME}, '
            f'warmup={DEFENSE_DEMO_WARMUP_STUDENT_USERNAME}, '
            f'demo={DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME}'
        )
        print(
            f'  - 支撑课程: {DEFENSE_DEMO_SUPPORT_COURSE_NAME}, '
            f'class_id={demo_summary.get("class_id")}, '
            f'stage_exam_id={demo_summary.get("stage_exam_id")}'
        )
        defense_demo_config = course.config.get('defense_demo') if isinstance(course.config, dict) else {}
        assistant_demo_queries = (
            defense_demo_config.get('assistant_demo_queries', [])
            if isinstance(defense_demo_config, dict)
            else []
        )
        if isinstance(assistant_demo_queries, list) and assistant_demo_queries:
            print('  - 推荐 AI 助手演示提问:')
            for query_payload in assistant_demo_queries[:3]:
                if not isinstance(query_payload, dict):
                    continue
                title = str(query_payload.get('title', '')).strip() or 'AI 助手问答'
                question = str(query_payload.get('question', '')).strip()
                point_name = str(query_payload.get('point_name', '')).strip()
                suffix = f'（知识点：{point_name}）' if point_name else ''
                if question:
                    print(f'    * {title}{suffix}: {question}')
        for username in (
            DEFENSE_DEMO_WARMUP_STUDENT_USERNAME,
            DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME,
            *(student_spec['username'] for student_spec in DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS),
        ):
            user = User.objects.filter(username=username).first()
            if not user:
                print(f'账号缺失: {username}')
                continue
            # 这里输出的是演示入口最常检查的几个状态，便于在一次重建后快速
            # 判断画像、学习路径和报告链路是否都已回填成功。
            status = AssessmentStatus.objects.filter(user=user, course=course).first()
            path = LearningPath.objects.filter(user=user, course=course).first()
            assessment_result_count = AssessmentResult.objects.filter(user=user, course=course).count()
            answer_history_count = AnswerHistory.objects.filter(user=user, course=course).count()
            assessment_report_count = FeedbackReport.objects.filter(
                user=user,
                source='assessment',
                assessment_result__course=course,
            ).count()
            exam_report_count = FeedbackReport.objects.filter(user=user, exam__course=course).count()
            profile_exists = ProfileSummary.objects.filter(user=user, course=course).exists()
            in_demo_class = user.enrollments.filter(class_obj_id=demo_summary.get('class_id')).exists()
            print(
                f'  - {username}: '
                f'in_demo_class={in_demo_class}, '
                f'ability={getattr(status, "ability_done", False)}, '
                f'habit={getattr(status, "habit_done", False)}, '
                f'knowledge={getattr(status, "knowledge_done", False)}, '
                f'profile={profile_exists}, '
                f'path_nodes={path.nodes.count() if path else 0}, '
                f'assessment_results={assessment_result_count}, '
                f'answer_history={answer_history_count}, '
                f'assessment_reports={assessment_report_count}, '
                f'exam_reports={exam_report_count}'
            )
        print('下一步: 使用 python tools.py browser-audit --scenario prepare-defense-demo --headed 预检答辩链路。')
    else:
        print(f'警告: 未找到课程 {course_name}，请检查资源目录与导入日志。')
