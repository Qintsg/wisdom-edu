"""student1 演示课程状态预置辅助工具。"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from knowledge.models import Resource


# 维护意图：student1 演示预置使用的固定默认值
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class Student1DemoDefaults:
    """student1 演示预置使用的固定默认值。"""

    habit_defaults: dict[str, object]
    ability_scores: dict[str, int]
    profile_defaults: dict[str, str]
    path_node_configs: list[dict[str, object]]


# 维护意图：student1 演示预置需要的课程数据
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class Student1DemoCourseData:
    """student1 演示预置需要的课程数据。"""

    points: list[object]
    questions: list[object]
    resources: list[Resource]
    selected_questions: list[object]


# 维护意图：构造 student1 演示用固定默认值
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_student1_demo_defaults() -> Student1DemoDefaults:
    """构造 student1 演示用固定默认值。"""
    return Student1DemoDefaults(
        habit_defaults={
            "preferred_resource": "video",
            "preferred_study_time": "evening",
            "study_pace": "adaptive",
            "study_duration": "medium",
            "review_frequency": "weekly",
            "learning_style": "visual",
            "accept_challenge": True,
            "daily_goal_minutes": 45,
            "weekly_goal_days": 5,
            "preferences": {
                "preferred_resource": "video",
                "preferred_study_time": "evening",
                "study_pace": "adaptive",
                "daily_goal_minutes": 45,
                "weekly_goal_days": 5,
            },
        },
        ability_scores={
            "逻辑推理": 78,
            "抽象思维": 74,
            "信息整合": 76,
            "学习迁移": 72,
        },
        profile_defaults={
            "summary": (
                "该学生刚完成课程初始评测，当前仅对少量核心知识点建立了基础判断，"
                "整体仍处于学习起步阶段，大部分知识点掌握度维持在保守基线附近。"
            ),
            "suggestion": (
                "建议先围绕前三个核心知识点完成路径首节点学习，"
                "再通过课程资源逐步把 25% 基线知识点拉升到可稳定应用的水平。"
            ),
        },
        path_node_configs=[
            {
                "title": "大数据概念基础复盘",
                "goal": "建立 4V 特征与典型应用场景的基础认知",
                "status": "active",
                "estimated_minutes": 20,
            },
            {
                "title": "Hadoop 生态结构入门",
                "goal": "认识 HDFS、YARN 与 MapReduce 的职责划分",
                "status": "locked",
                "estimated_minutes": 35,
            },
            {
                "title": "Spark 计算模型预习",
                "goal": "理解 Spark 的核心抽象与内存计算优势",
                "status": "locked",
                "estimated_minutes": 35,
            },
        ],
    )


# 维护意图：加载 student1 预置所需的知识点、题目和资源
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_student1_demo_course_data(course) -> Student1DemoCourseData:
    """加载 student1 预置所需的知识点、题目和资源。"""
    from assessments.models import Question
    from knowledge.models import KnowledgePoint

    points = list(KnowledgePoint.objects.filter(course=course).order_by("order", "id"))
    questions = list(
        Question.objects.filter(course=course)
        .prefetch_related("knowledge_points")
        .order_by("id")
    )
    resources = list(Resource.objects.filter(course=course).order_by("sort_order", "id"))
    selected_questions = [question for question in questions if question.for_initial_assessment]
    return Student1DemoCourseData(
        points=points,
        questions=questions,
        resources=resources,
        selected_questions=selected_questions or questions,
    )


# 维护意图：清理指定学生在课程下的预置轨迹，便于幂等重建
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def reset_course_demo_state(student, course) -> None:
    """清理指定学生在课程下的预置轨迹，便于幂等重建。"""
    from assessments.models import AbilityScore, AssessmentResult, AssessmentStatus, AnswerHistory
    from exams.models import ExamSubmission, FeedbackReport
    from knowledge.models import KnowledgeMastery, ProfileSummary
    from learning.models import LearningPath

    FeedbackReport.objects.filter(user=student, assessment_result__course=course).delete()
    FeedbackReport.objects.filter(user=student, exam__course=course).delete()
    ExamSubmission.objects.filter(user=student, exam__course=course).delete()
    LearningPath.objects.filter(user=student, course=course).delete()
    AssessmentResult.objects.filter(user=student, course=course).delete()
    AnswerHistory.objects.filter(user=student, course=course).delete()
    AssessmentStatus.objects.filter(user=student, course=course).delete()
    AbilityScore.objects.filter(user=student, course=course).delete()
    KnowledgeMastery.objects.filter(user=student, course=course).delete()
    ProfileSummary.objects.filter(user=student, course=course).delete()


# 维护意图：同步 student1 初始评测定义与题目顺序
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def sync_student1_initial_assessment(course, selected_questions: list[object]):
    """同步 student1 初始评测定义与题目顺序。"""
    from assessments.models import Assessment, AssessmentQuestion

    assessment, _ = Assessment.objects.update_or_create(
        course=course,
        assessment_type="knowledge",
        defaults={
            "title": f"{course.name} 初始评测",
            "description": "系统自动生成的初始知识评测",
            "is_active": True,
        },
    )
    AssessmentQuestion.objects.filter(assessment=assessment).exclude(
        question__in=selected_questions
    ).delete()
    for order, question in enumerate(selected_questions, start=1):
        AssessmentQuestion.objects.update_or_create(
            assessment=assessment,
            question=question,
            defaults={"order": order},
        )
    return assessment


# 维护意图：按题型生成可用于预置答题历史的原始答案值
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_student1_answer_value(question, force_correct: bool) -> object:
    """按题型生成可用于预置答题历史的原始答案值。"""
    from common.utils import extract_answer_value

    correct_raw = extract_answer_value(question.answer)
    if force_correct:
        return correct_raw

    option_labels = [
        str(option.get("label"))
        for option in (question.options or [])
        if isinstance(option, dict) and option.get("label") is not None
    ]
    if question.question_type == "multiple_choice":
        correct_values = [str(value) for value in correct_raw] if isinstance(correct_raw, list) else [str(correct_raw)]
        fallback = next((label for label in option_labels if label not in correct_values), "A")
        return [correct_values[0], fallback] if correct_values else [fallback]
    if question.question_type == "true_false":
        normalized = str(correct_raw).strip().lower()
        return "false" if normalized in {"true", "a", "正确", "对"} else "true"
    return next(
        (label for label in option_labels if label != str(correct_raw)),
        "B" if str(correct_raw).upper() != "B" else "A",
    )


# 维护意图：写入 student1 的习惯、能力与评测完成状态
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_student1_static_state(student, course, defaults: Student1DemoDefaults) -> None:
    """写入 student1 的习惯、能力与评测完成状态。"""
    from assessments.models import AbilityScore, AssessmentStatus
    from users.models import HabitPreference

    AssessmentStatus.objects.update_or_create(
        user=student,
        course=course,
        defaults={
            "ability_done": True,
            "habit_done": True,
            "knowledge_done": True,
        },
    )
    HabitPreference.objects.update_or_create(user=student, defaults=defaults.habit_defaults)
    AbilityScore.objects.update_or_create(
        user=student,
        course=course,
        defaults={"scores": defaults.ability_scores},
    )


# 维护意图：构造初始评测结果中的 mastery 列表
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_mastery_payload(points, mastery_map: dict[int, float], prior_mean: float) -> list[dict[str, object]]:
    """构造初始评测结果中的 mastery 列表。"""
    return [
        {
            "point_id": point.id,
            "point_name": point.name,
            "mastery_rate": round(float(mastery_map.get(point.id, prior_mean)), 4),
        }
        for point in points
    ]


# 维护意图：构造 student1 预置反馈报告默认值
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_student1_feedback_defaults(
    *,
    total_questions: int,
    weakest_points: list[str],
    total_score: Decimal,
    max_possible: Decimal,
    correct_count: int,
) -> dict[str, object]:
    """构造 student1 预置反馈报告默认值。"""
    return {
        "status": "completed",
        "overview": {
            "score": round(float(total_score), 2),
            "total_score": round(float(max_possible), 2),
            "correct_count": correct_count,
            "total_count": total_questions,
            "accuracy": round(correct_count / max(total_questions, 1) * 100, 1),
            "summary": f"已完成 {total_questions} 道初始评测题，系统已基于完整题组生成掌握度画像。",
            "knowledge_gaps": weakest_points,
        },
        "analysis": f"当前画像基于课程资源示例中的 {total_questions} 道初始评测题生成，系统已识别出薄弱知识点，但仍需要通过后续学习行为逐步校准掌握度。",
        "recommendations": [
            "优先学习路径中的首个激活节点，巩固最基础的核心概念。",
            "先补足 25% 基线知识点对应的课程资源，再进入后续练习。",
        ],
        "next_tasks": [
            "完成当前激活的首个学习节点。",
            "学习后重新查看画像与掌握度变化。",
        ],
        "conclusion": "当前结果适合作为“刚完成初始评测”的真实起点数据，不代表稳定掌握水平。",
    }


# 维护意图：重建 student1 的初始学习路径节点
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def rebuild_student1_path(
    *,
    student,
    course,
    points,
    resources: list[Resource],
    mastery_map: dict[int, float],
    prior_mean: float,
    defaults: Student1DemoDefaults,
) -> int:
    """重建 student1 的初始学习路径节点。"""
    from learning.models import LearningPath, NodeProgress, PathNode

    path, _ = LearningPath.objects.update_or_create(
        user=student,
        course=course,
        defaults={
            "ai_reason": (
                f"你刚完成 {len(defaults.path_node_configs)} 个首轮学习节点前置评估，系统已按完整题组估计知识点掌握度。"
                "建议先从概念复盘开始，逐步推进到 Hadoop 与 Spark 的核心内容。"
            ),
        },
    )
    path.nodes.all().delete()

    for order, node_cfg in enumerate(defaults.path_node_configs, start=1):
        point = points[order - 1] if order <= len(points) else points[-1]
        node = PathNode.objects.create(
            path=path,
            knowledge_point=point,
            title=str(node_cfg["title"]),
            goal=str(node_cfg["goal"]),
            criterion="完成节点学习并掌握对应知识点的核心概念。",
            suggestion="建议先阅读对应课程资源，再用错题与知识图谱进行回顾。",
            status=str(node_cfg["status"]),
            order_index=order,
            node_type="study",
            estimated_minutes=int(node_cfg["estimated_minutes"]),
        )
        linked_resource_ids = [
            resource.id
            for resource in resources
            if resource.knowledge_points.filter(id=point.id).exists()
        ]
        if linked_resource_ids:
            node.resources.set(linked_resource_ids)
        NodeProgress.objects.update_or_create(
            node=node,
            user=student,
            defaults={
                "completed_resources": [],
                "completed_exams": [],
                "mastery_before": Decimal(
                    str(round(float(mastery_map.get(point.id, prior_mean)), 4))
                ),
                "mastery_after": None,
                "extra_data": {
                    "testdata_preset": True,
                    "preset_stage": "initial_assessment_completed",
                },
            },
        )
    return len(defaults.path_node_configs)
