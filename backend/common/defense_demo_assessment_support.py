from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from assessments.models import (
    AbilityScore,
    AnswerHistory,
    Assessment,
    AssessmentQuestion,
    AssessmentResult,
    AssessmentStatus,
    Question,
)
from courses.models import Course
from exams.models import FeedbackReport
from knowledge.models import KnowledgeMastery, KnowledgePoint, ProfileSummary
from users.models import HabitPreference, User

from common.defense_demo_config import _get_demo_assessment_preset
from common.defense_demo_progress import _question_knowledge_points
from common.utils import extract_answer_value, serialize_answer_payload


# 维护意图：答辩演示账号的评测默认值集合
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class DemoAssessmentDefaults:
    """答辩演示账号的评测默认值集合。"""

    habit_defaults: dict[str, object]
    ability_scores: dict[str, int]
    profile_defaults: dict[str, object]
    assessment_feedback_defaults: dict[str, object]
    planned_answers: list[object]


# 维护意图：从演示预置配置中解析学生测评默认值
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def _load_demo_assessment_defaults(student_username: str) -> DemoAssessmentDefaults:
    """从演示预置配置中解析学生测评默认值。"""
    preset = _get_demo_assessment_preset(student_username)
    habit_defaults: dict[str, object] = {
        "preferred_resource": "video",
        "preferred_study_time": "evening",
        "study_pace": "moderate",
        "study_duration": "medium",
        "review_frequency": "weekly",
        "learning_style": "visual",
        "accept_challenge": True,
        "daily_goal_minutes": 50,
        "weekly_goal_days": 5,
        "preferences": {
            "preferred_resource": "video",
            "preferred_study_time": "evening",
            "study_pace": "moderate",
            "daily_goal_minutes": 50,
            "weekly_goal_days": 5,
            "review_frequency": "weekly",
            "learning_style": "visual",
            "accept_challenge": True,
            "difficulty_strategy": "先看解析再重试",
        },
    }
    raw_habit_defaults = preset.get("habit_preference")
    if isinstance(raw_habit_defaults, dict):
        habit_defaults.update(raw_habit_defaults)

    ability_scores = {
        "逻辑推理": 84,
        "抽象思维": 79,
        "信息整合": 81,
        "学习迁移": 76,
    }
    raw_ability_scores = preset.get("ability_scores")
    if isinstance(raw_ability_scores, dict):
        ability_scores = {
            key: int(value)
            for key, value in raw_ability_scores.items()
            if isinstance(key, str) and isinstance(value, int | float)
        }

    profile_defaults: dict[str, object] = {
        "summary": "该学生对大数据基础概念有一定掌握，但在 Hadoop 组件识别和 Spark 高级特性理解上仍存在薄弱环节。",
        "weakness": "对 HDFS 与 MapReduce 的职责区分不够清晰；RDD 惰性求值与容错机制的判断有误。",
        "suggestion": "建议沿概念 → 生态结构 → 计算模型的顺序逐步学习，着重强化 Hadoop 组件辨识和 Spark 核心抽象。",
    }
    raw_profile_defaults = preset.get("profile_summary")
    if isinstance(raw_profile_defaults, dict):
        profile_defaults.update(raw_profile_defaults)

    assessment_feedback_defaults: dict[str, object] = {
        "summary": "初始评测显示该学生对大数据基础概念掌握较好，但在 Hadoop 组件辨识和 Spark 高级特性上存在知识盲区。",
        "analysis": "学生在概念类题目上表现稳定，但对平台组件职责和分布式计算高级抽象的区分仍需加强。",
        "recommendations": [
            "先沿知识图谱梳理概念与组件关系。",
            "重点复习 Hadoop 组件的职责划分，区分 HDFS、YARN 与 MapReduce。",
            "结合实例理解 RDD 惰性求值与容错特性，完成阶段测试后根据掌握度变化继续补强。",
        ],
        "next_tasks": [
            "进入学习路径完成前三个学习节点。",
            "在阶段测试中验证概念迁移效果。",
        ],
        "conclusion": "基础概念掌握较好，Hadoop 生态与 Spark 高级特性是当前主要提升方向，建议分阶段针对性强化。",
    }
    raw_assessment_feedback = preset.get("assessment_feedback")
    if isinstance(raw_assessment_feedback, dict):
        assessment_feedback_defaults.update(raw_assessment_feedback)

    planned_answers = preset.get("planned_answers")
    if not isinstance(planned_answers, list):
        planned_answers = ["B", "C", "A", "C", "A", ["A", "B"]]

    return DemoAssessmentDefaults(
        habit_defaults=habit_defaults,
        ability_scores=ability_scores,
        profile_defaults=profile_defaults,
        assessment_feedback_defaults=assessment_feedback_defaults,
        planned_answers=planned_answers,
    )


# 维护意图：补齐习惯、能力、评测状态和画像摘要
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _seed_demo_profile_state(
    course: Course,
    student: User,
    defaults: DemoAssessmentDefaults,
) -> None:
    """补齐习惯、能力、评测状态和画像摘要。"""
    HabitPreference.objects.update_or_create(
        user=student,
        defaults=defaults.habit_defaults,
    )
    AbilityScore.objects.update_or_create(
        user=student,
        course=course,
        defaults={"scores": defaults.ability_scores},
    )
    AssessmentStatus.objects.update_or_create(
        user=student,
        course=course,
        defaults={
            "knowledge_done": True,
            "ability_done": True,
            "habit_done": True,
            "generating": False,
            "generation_error": "",
        },
    )
    ProfileSummary.objects.update_or_create(
        user=student,
        course=course,
        defaults=defaults.profile_defaults,
    )


# 维护意图：创建或复用初始知识评测及 through 关联
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _ensure_demo_knowledge_assessment(
    course: Course,
    questions: list[Question],
) -> Assessment:
    """创建或复用初始知识评测及 through 关联。"""
    knowledge_assessment = (
        Assessment.objects.filter(course=course, assessment_type="knowledge", is_active=True)
        .order_by("id")
        .first()
    )
    if knowledge_assessment is None:
        knowledge_assessment = Assessment.objects.create(
            course=course,
            title=f"{course.name} 初始知识评测",
            assessment_type="knowledge",
            description="基于课程知识点的初始掌握度评测。",
            is_active=True,
        )

    AssessmentQuestion.objects.filter(assessment=knowledge_assessment).exclude(
        question__in=questions,
    ).delete()
    for order, question in enumerate(questions, start=1):
        AssessmentQuestion.objects.update_or_create(
            assessment=knowledge_assessment,
            question=question,
            defaults={"order": order},
        )
    return knowledge_assessment


# 维护意图：按真实提交流程刷新初始评测答题历史
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _refresh_demo_answer_histories(
    course: Course,
    student: User,
    questions: list[Question],
    raw_answers: dict[str, object],
    is_correct_flags: list[bool],
) -> None:
    """按真实提交流程刷新初始评测答题历史。"""
    for question, is_correct in zip(questions, is_correct_flags, strict=True):
        point = question.knowledge_points.first()
        student_raw = raw_answers[str(question.id)]
        correct_raw = extract_answer_value(question.answer)
        AnswerHistory.objects.update_or_create(
            user=student,
            course=course,
            question=question,
            source="initial",
            defaults={
                "knowledge_point": point,
                "student_answer": serialize_answer_payload(question.question_type, student_raw),
                "correct_answer": serialize_answer_payload(question.question_type, correct_raw),
                "is_correct": is_correct,
                "score": Decimal(str(float(question.score))) if is_correct else Decimal("0"),
                "source": "initial",
            },
        )


# 维护意图：根据初始评测正误生成贝叶斯掌握度基线
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _build_demo_mastery_map(
    questions: list[Question],
    is_correct_flags: list[bool],
) -> dict[int, Decimal]:
    """根据初始评测正误生成贝叶斯掌握度基线。"""
    point_stats: dict[int, dict[str, int]] = {}
    for question, is_correct in zip(questions, is_correct_flags, strict=True):
        for point in _question_knowledge_points(question):
            if point.id not in point_stats:
                point_stats[point.id] = {"correct": 0, "total": 0}
            point_stats[point.id]["total"] += 1
            if is_correct:
                point_stats[point.id]["correct"] += 1

    mastery_map: dict[int, Decimal] = {}
    for point_id, stats in point_stats.items():
        raw_mastery = (stats["correct"] + 0.25 * 4.0) / (stats["total"] + 4.0)
        mastery_map[point_id] = Decimal(str(round(min(max(raw_mastery, 0.0), 0.85), 4)))
    return mastery_map


# 维护意图：写回演示账号的知识掌握度记录
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _persist_demo_mastery_records(
    course: Course,
    student: User,
    points: list[KnowledgePoint],
    mastery_map: dict[int, Decimal],
) -> None:
    """写回演示账号的知识掌握度记录。"""
    for point in points:
        KnowledgeMastery.objects.update_or_create(
            user=student,
            course=course,
            knowledge_point=point,
            defaults={"mastery_rate": mastery_map.get(point.id, Decimal("0.25"))},
        )


# 维护意图：更新初始评测结果快照
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _upsert_demo_assessment_result(
    course: Course,
    student: User,
    knowledge_assessment: Assessment,
    questions: list[Question],
    points: list[KnowledgePoint],
    raw_answers: dict[str, object],
    question_details: list[dict[str, object]],
    is_correct_flags: list[bool],
    mastery_map: dict[int, Decimal],
) -> AssessmentResult:
    """更新初始评测结果快照。"""
    total_score = sum(float(question.score or 0) for question in questions)
    earned_score = sum(
        float(question.score)
        for question, is_correct in zip(questions, is_correct_flags, strict=True)
        if is_correct
    )
    correct_count = sum(is_correct_flags)
    return AssessmentResult.objects.update_or_create(
        user=student,
        assessment=knowledge_assessment,
        defaults={
            "course": course,
            "answers": raw_answers,
            "score": Decimal(str(round(earned_score, 2))),
            "result_data": {
                "mastery": [
                    {
                        "point_id": point.id,
                        "point_name": point.name,
                        "mastery_rate": float(mastery_map.get(point.id, Decimal("0.25"))),
                    }
                    for point in points
                ],
                "question_details": question_details,
                "total_score": round(total_score, 2),
                "correct_count": correct_count,
                "total_count": len(questions),
            },
        },
    )[0]


# 维护意图：回填与异步生成一致的初始评测反馈报告
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def _upsert_demo_assessment_feedback(
    student: User,
    assessment_result: AssessmentResult,
    points: list[KnowledgePoint],
    mastery_map: dict[int, Decimal],
    is_correct_flags: list[bool],
    questions: list[Question],
    defaults: DemoAssessmentDefaults,
) -> None:
    """回填与异步生成一致的初始评测反馈报告。"""
    total_score = sum(float(question.score or 0) for question in questions)
    earned_score = sum(
        float(question.score)
        for question, is_correct in zip(questions, is_correct_flags, strict=True)
        if is_correct
    )
    correct_count = sum(is_correct_flags)
    total_count = len(questions)
    accuracy = round(correct_count / total_count * 100, 1) if total_count else 0.0
    weak_points = [point for point in points if float(mastery_map.get(point.id, Decimal("0"))) < 0.4]
    FeedbackReport.objects.update_or_create(
        user=student,
        source="assessment",
        assessment_result=assessment_result,
        defaults={
            "exam": None,
            "status": "completed",
            "overview": {
                "score": round(earned_score, 2),
                "total_score": round(total_score, 2),
                "correct_count": correct_count,
                "total_count": total_count,
                "accuracy": accuracy,
                "summary": str(defaults.assessment_feedback_defaults["summary"]),
                "knowledge_gaps": [point.name for point in weak_points] if weak_points else [points[-1].name],
            },
            "analysis": str(defaults.assessment_feedback_defaults["analysis"]),
            "recommendations": list(defaults.assessment_feedback_defaults["recommendations"]),
            "next_tasks": list(defaults.assessment_feedback_defaults["next_tasks"]),
            "conclusion": str(defaults.assessment_feedback_defaults["conclusion"]),
        },
    )
