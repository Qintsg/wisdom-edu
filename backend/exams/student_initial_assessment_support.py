"""学生端初始评测提交支持逻辑。"""
from __future__ import annotations

import logging
import random
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import InvalidOperation

from django.db import DatabaseError

from assessments.models import AnswerHistory, AssessmentStatus, Question
from common.logging_utils import build_log_message
from common.utils import check_answer, extract_answer_value
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint
from users.models import User


logger = logging.getLogger(__name__)

KnowledgePointStats = dict[int, dict[str, int]]


# 维护意图：初始评测抽题结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class InitialQuestionSelection:
    """初始评测抽题结果。"""

    questions: list[Question]
    count: int


# 维护意图：初始评测判分与知识点掌握度结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class InitialAssessmentScore:
    """初始评测判分与知识点掌握度结果。"""

    total_score: float
    correct_count: int
    total_count: int
    knowledge_point_stats: KnowledgePointStats
    knowledge_mastery: dict[int, float]


# 维护意图：单题答题历史写入参数
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class InitialAnswerRecord:
    """单题答题历史写入参数。"""

    user: User
    course: Course
    question: Question
    student_answer: object
    is_correct: bool
    score: float
    knowledge_points: Sequence[KnowledgePoint]


# 维护意图：按课程初始评测配置随机抽取可见题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def select_initial_questions(course: Course) -> InitialQuestionSelection:
    """按课程初始评测配置随机抽取可见题目。"""
    questions = list(
        Question.objects.filter(
            course=course,
            for_initial_assessment=True,
            is_visible=True,
        ).prefetch_related("knowledge_points")
    )
    if not questions:
        return InitialQuestionSelection(questions=[], count=0)
    count = min(course.initial_assessment_count, len(questions))
    return InitialQuestionSelection(questions=random.sample(questions, count), count=count)


# 维护意图：转换为前端初始评测题目载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def serialize_initial_questions(questions: Sequence[Question]) -> list[dict[str, object]]:
    """转换为前端初始评测题目载荷。"""
    return [
        {
            "question_id": question.id,
            "content": question.content,
            "options": question.options,
            "type": question.question_type,
            "score": float(question.score),
        }
        for question in questions
    ]


# 维护意图：解析答案字典中的题目 ID
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_answer_question_ids(answers: Mapping[str, object]) -> list[int]:
    """解析答案字典中的题目 ID。"""
    try:
        return [int(question_id) for question_id in answers.keys()]
    except (ValueError, TypeError) as error:
        raise ValueError("题目ID格式错误") from error


# 维护意图：加载本次提交涉及的题目及其知识点
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_answered_questions(question_ids: Sequence[int]) -> list[Question]:
    """加载本次提交涉及的题目及其知识点。"""
    return list(
        Question.objects.filter(id__in=question_ids).prefetch_related("knowledge_points")
    )


# 维护意图：完成初始评测判分、答题历史写入和规则掌握度更新
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def score_initial_assessment(
    *,
    user: User,
    course: Course,
    questions: Sequence[Question],
    answers: Mapping[str, object],
) -> InitialAssessmentScore:
    """完成初始评测判分、答题历史写入和规则掌握度更新。"""
    total_score = 0.0
    correct_count = 0
    knowledge_point_stats: KnowledgePointStats = defaultdict(lambda: {"correct": 0, "total": 0})

    for question in questions:
        student_answer = answers.get(str(question.id))
        is_correct = check_answer(question.question_type, student_answer, question.answer)
        score = float(question.score) if is_correct else 0.0
        total_score += score
        correct_count += 1 if is_correct else 0
        knowledge_points = list(question.knowledge_points.all())
        create_initial_answer_history(
            InitialAnswerRecord(
                user=user,
                course=course,
                question=question,
                student_answer=student_answer,
                is_correct=is_correct,
                score=score,
                knowledge_points=knowledge_points,
            )
        )
        update_question_stats(knowledge_point_stats, knowledge_points, is_correct)

    knowledge_mastery = update_rule_based_mastery(
        user=user,
        course=course,
        knowledge_point_stats=knowledge_point_stats,
    )
    return InitialAssessmentScore(
        total_score=total_score,
        correct_count=correct_count,
        total_count=len(questions),
        knowledge_point_stats=dict(knowledge_point_stats),
        knowledge_mastery=knowledge_mastery,
    )


# 维护意图：写入初始评测答题历史，供后续 KT 和学习报告使用
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def create_initial_answer_history(record: InitialAnswerRecord) -> None:
    """写入初始评测答题历史，供后续 KT 和学习报告使用。"""
    first_point = record.knowledge_points[0] if record.knowledge_points else None
    try:
        AnswerHistory.objects.create(
            user=record.user,
            course=record.course,
            question=record.question,
            knowledge_point=first_point,
            student_answer={"answer": record.student_answer},
            correct_answer={"answer": extract_answer_value(record.question.answer)},
            is_correct=record.is_correct,
            score=record.score,
            source="initial",
        )
    except DatabaseError:
        logger.exception("初始评测答题历史写入失败: user=%s question=%s", record.user.id, record.question.id)
        raise


# 维护意图：按题目关联知识点累计规则掌握度统计
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_question_stats(
    knowledge_point_stats: KnowledgePointStats,
    knowledge_points: Sequence[KnowledgePoint],
    is_correct: bool,
) -> None:
    """按题目关联知识点累计规则掌握度统计。"""
    for knowledge_point in knowledge_points:
        knowledge_point_stats[knowledge_point.id]["total"] += 1
        if is_correct:
            knowledge_point_stats[knowledge_point.id]["correct"] += 1


# 维护意图：根据初始评测正确率更新规则掌握度
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_rule_based_mastery(
    *,
    user: User,
    course: Course,
    knowledge_point_stats: KnowledgePointStats,
) -> dict[int, float]:
    """根据初始评测正确率更新规则掌握度。"""
    knowledge_mastery: dict[int, float] = {}
    for knowledge_point_id, stats in knowledge_point_stats.items():
        mastery_rate = stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0
        KnowledgeMastery.objects.update_or_create(
            user=user,
            course=course,
            knowledge_point_id=knowledge_point_id,
            defaults={"mastery_rate": mastery_rate},
        )
        knowledge_mastery[knowledge_point_id] = mastery_rate
    return knowledge_mastery


# 维护意图：调用 KT 服务二次修正初始评测掌握度
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_kt_initial_mastery(
    *,
    user: User,
    course: Course,
    knowledge_point_stats: KnowledgePointStats,
    knowledge_mastery: dict[int, float],
) -> None:
    """调用 KT 服务二次修正初始评测掌握度。"""
    try:
        from ai_services.services.kt_service import kt_service

        kt_history = build_initial_kt_history(user=user, course=course)
        knowledge_point_ids = list(knowledge_point_stats.keys())
        if not kt_history or not knowledge_point_ids:
            return
        kt_result = kt_service.predict_mastery(
            user_id=user.id,
            course_id=course.id,
            answer_history=kt_history,
            knowledge_points=knowledge_point_ids,
        )
        kt_predictions = kt_result.get("predictions", {})
        persist_kt_predictions(
            user=user,
            course=course,
            kt_predictions=kt_predictions,
            knowledge_mastery=knowledge_mastery,
        )
        logger.info(
            "KT服务调用成功(初始评测): 用户=%s, 答题历史=%d条, 预测结果=%d条",
            user.id,
            len(kt_history),
            len(kt_predictions),
        )
    except Exception as error:
        logger.error("KT服务调用失败(初始评测): 用户=%s, 错误=%s", user.id, error)


# 维护意图：读取当前学生课程历史并转换为 KT 服务输入
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_initial_kt_history(*, user: User, course: Course) -> list[dict[str, int | None]]:
    """读取当前学生课程历史并转换为 KT 服务输入。"""
    all_history = list(
        AnswerHistory.objects.filter(user=user, course=course)
        .order_by("answered_at")
        .values("question_id", "knowledge_point_id", "is_correct")
    )
    return [
        {
            "question_id": item["question_id"],
            "knowledge_point_id": item["knowledge_point_id"],
            "correct": 1 if item["is_correct"] else 0,
        }
        for item in all_history
    ]


# 维护意图：持久化 KT 输出，并跳过无法转换的异常条目
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def persist_kt_predictions(
    *,
    user: User,
    course: Course,
    kt_predictions: Mapping[object, object],
    knowledge_mastery: dict[int, float],
) -> None:
    """持久化 KT 输出，并跳过无法转换的异常条目。"""
    for knowledge_point_id, rate in kt_predictions.items():
        try:
            normalized_rate = round(float(rate), 4)
            KnowledgeMastery.objects.update_or_create(
                user=user,
                course=course,
                knowledge_point_id=knowledge_point_id,
                defaults={"mastery_rate": max(0.0, min(1.0, normalized_rate))},
            )
            knowledge_mastery[int(knowledge_point_id)] = normalized_rate
        except (DatabaseError, InvalidOperation, OverflowError, TypeError, ValueError) as error:
            logger.warning(
                build_log_message(
                    "kt.initial_assessment.mastery_skip",
                    user_id=user.id,
                    course_id=course.id,
                    knowledge_point_id=knowledge_point_id,
                    error=error,
                )
            )


# 维护意图：标记课程初始评测已完成
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def mark_initial_assessment_done(*, user: User, course: Course) -> None:
    """标记课程初始评测已完成。"""
    status, _ = AssessmentStatus.objects.get_or_create(user=user, course=course)
    status.knowledge_done = True
    status.save()


# 维护意图：构造初始评测提交响应载荷
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_initial_assessment_result(score: InitialAssessmentScore) -> dict[str, object]:
    """构造初始评测提交响应载荷。"""
    return {
        "score": score.total_score,
        "correct_count": score.correct_count,
        "total_count": score.total_count,
        "knowledge_mastery": score.knowledge_mastery,
    }
