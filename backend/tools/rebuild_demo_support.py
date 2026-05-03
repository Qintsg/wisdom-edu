"""演示环境重建结果汇总辅助工具。"""

from __future__ import annotations

from collections.abc import Iterable

from assessments.models import AnswerHistory, AssessmentResult, AssessmentStatus
from common.defense_demo import (
    DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS,
    DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME,
    DEFENSE_DEMO_SUPPORT_COURSE_NAME,
    DEFENSE_DEMO_TEACHER_USERNAME,
    DEFENSE_DEMO_WARMUP_STUDENT_USERNAME,
)
from common.neo4j_service import neo4j_service
from courses.models import Course
from exams.models import FeedbackReport
from exams.score_policy import sync_course_exam_totals
from knowledge.models import ProfileSummary
from learning.models import LearningPath
from users.models import User


# 维护意图：返回需要在重建结果中展示的全部演示账号
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def iter_demo_usernames() -> Iterable[str]:
    """返回需要在重建结果中展示的全部演示账号。"""
    yield DEFENSE_DEMO_WARMUP_STUDENT_USERNAME
    yield DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME
    for student_spec in DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS:
        yield student_spec["username"]


# 维护意图：按课程名称读取重建后的主课程
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_demo_course(course_name: str) -> Course | None:
    """按课程名称读取重建后的主课程。"""
    return Course.objects.filter(name=course_name).first()


# 维护意图：同步演示课程的图谱与考试总分口径
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def sync_demo_course_runtime(
    *,
    course: Course,
    sync_graph: bool,
) -> tuple[int, dict[str, int]]:
    """同步演示课程的图谱与考试总分口径。"""
    if sync_graph:
        neo4j_service.sync_knowledge_graph(course.id)
    synced_exam_count = sync_course_exam_totals(course.id)
    graph_stats = (
        neo4j_service.get_graph_stats(course.id)
        if neo4j_service.is_available
        else {}
    )
    return synced_exam_count, graph_stats


# 维护意图：在启用 Neo4j 的场景下，确保演示课程图谱已经可用
# 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
# 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
def assert_demo_graph_ready(
    *,
    course: Course,
    sync_graph: bool,
    graph_stats: dict[str, int],
) -> None:
    """在启用 Neo4j 的场景下，确保演示课程图谱已经可用。"""
    if sync_graph and graph_stats.get("node_count", 0) <= 0:
        raise RuntimeError(f"课程 {course.id} 的 Neo4j 图数据为空，请检查同步链路。")


# 维护意图：打印主课程、图谱和答辩账号的整体就绪状态
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def print_demo_course_summary(
    *,
    course: Course,
    demo_summary: dict[str, int],
    sync_graph: bool,
    synced_exam_count: int,
    graph_stats: dict[str, int],
) -> None:
    """打印主课程、图谱和答辩账号的整体就绪状态。"""
    print(f"演示课程已就绪: id={course.id}, name={course.name}")
    print(f"  - 已同步考试总分口径: {synced_exam_count} 场")
    print(
        f'  - Neo4j图数据: nodes={graph_stats.get("node_count", 0)}, '
        f'relations={graph_stats.get("relation_count", 0)}'
    )
    if not sync_graph:
        print("  - 警告: 当前环境未连接 Neo4j，本次演示将使用 PostgreSQL 回退图数据。")
    print(
        f"  - 答辩账号: teacher={DEFENSE_DEMO_TEACHER_USERNAME}, "
        f"warmup={DEFENSE_DEMO_WARMUP_STUDENT_USERNAME}, "
        f"demo={DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME}"
    )
    print(
        f"  - 支撑课程: {DEFENSE_DEMO_SUPPORT_COURSE_NAME}, "
        f'class_id={demo_summary.get("class_id")}, '
        f'stage_exam_id={demo_summary.get("stage_exam_id")}'
    )


# 维护意图：打印推荐的 AI 助手演示提问
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def print_assistant_demo_queries(course: Course) -> None:
    """打印推荐的 AI 助手演示提问。"""
    defense_demo_config = (
        course.config.get("defense_demo")
        if isinstance(course.config, dict)
        else {}
    )
    assistant_demo_queries = (
        defense_demo_config.get("assistant_demo_queries", [])
        if isinstance(defense_demo_config, dict)
        else []
    )
    if not isinstance(assistant_demo_queries, list) or not assistant_demo_queries:
        return

    print("  - 推荐 AI 助手演示提问:")
    for query_payload in assistant_demo_queries[:3]:
        if not isinstance(query_payload, dict):
            continue
        title = str(query_payload.get("title", "")).strip() or "AI 助手问答"
        question = str(query_payload.get("question", "")).strip()
        point_name = str(query_payload.get("point_name", "")).strip()
        suffix = f"（知识点：{point_name}）" if point_name else ""
        if question:
            print(f"    * {title}{suffix}: {question}")


# 维护意图：汇总单个演示账号在主演示课程下的关键状态
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _user_course_status(
    *,
    user: User,
    course: Course,
    demo_class_id: int | None,
) -> dict[str, object]:
    """汇总单个演示账号在主演示课程下的关键状态。"""
    status = AssessmentStatus.objects.filter(user=user, course=course).first()
    path = LearningPath.objects.filter(user=user, course=course).first()
    return {
        "in_demo_class": user.enrollments.filter(class_obj_id=demo_class_id).exists(),
        "ability_done": getattr(status, "ability_done", False),
        "habit_done": getattr(status, "habit_done", False),
        "knowledge_done": getattr(status, "knowledge_done", False),
        "profile_exists": ProfileSummary.objects.filter(user=user, course=course).exists(),
        "path_nodes": path.nodes.count() if path else 0,
        "assessment_results": AssessmentResult.objects.filter(user=user, course=course).count(),
        "answer_history": AnswerHistory.objects.filter(user=user, course=course).count(),
        "assessment_reports": FeedbackReport.objects.filter(
            user=user,
            source="assessment",
            assessment_result__course=course,
        ).count(),
        "exam_reports": FeedbackReport.objects.filter(
            user=user,
            exam__course=course,
        ).count(),
    }


# 维护意图：输出演示账号在主演示课程下的关键信息
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def print_demo_user_statuses(course: Course, demo_summary: dict[str, int]) -> None:
    """输出演示账号在主演示课程下的关键信息。"""
    demo_class_id = demo_summary.get("class_id")
    for username in iter_demo_usernames():
        user = User.objects.filter(username=username).first()
        if not user:
            print(f"账号缺失: {username}")
            continue
        status_payload = _user_course_status(
            user=user,
            course=course,
            demo_class_id=demo_class_id,
        )
        print(
            f"  - {username}: "
            f'in_demo_class={status_payload["in_demo_class"]}, '
            f'ability={status_payload["ability_done"]}, '
            f'habit={status_payload["habit_done"]}, '
            f'knowledge={status_payload["knowledge_done"]}, '
            f'profile={status_payload["profile_exists"]}, '
            f'path_nodes={status_payload["path_nodes"]}, '
            f'assessment_results={status_payload["assessment_results"]}, '
            f'answer_history={status_payload["answer_history"]}, '
            f'assessment_reports={status_payload["assessment_reports"]}, '
            f'exam_reports={status_payload["exam_reports"]}'
        )


# 维护意图：打印答辩链路预检建议
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def print_demo_followup_hint() -> None:
    """打印答辩链路预检建议。"""
    print(
        "下一步: 使用 python tools.py browser-audit "
        "--scenario prepare-defense-demo --headed 预检答辩链路。"
    )
