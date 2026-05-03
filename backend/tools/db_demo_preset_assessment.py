"""student1 演示初始评测预置逻辑。"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from tools.db_demo_preset_support import build_mastery_payload, build_student1_answer_value


# 维护意图：student1 初始评测预置结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class Student1AssessmentAttempt:
    """student1 初始评测预置结果。"""

    total_score: Decimal
    max_possible: Decimal
    correct_count: int
    raw_answers: dict[str, object]
    question_details: list[dict[str, object]]
    point_stats: dict[int, dict[str, int | str]]
    mastery_map: dict[int, float]
    mastery_payload: list[dict[str, object]]


# 维护意图：使用与初始评测接口一致的保守基线计算掌握度
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def calculate_initial_mastery_baseline(
    *,
    correct_count: int,
    total_count: int,
    prior_mean: float,
    prior_strength: float,
) -> float:
    """使用与初始评测接口一致的保守基线计算掌握度。"""
    if total_count <= 0:
        return round(prior_mean, 4)

    mastery_rate = (correct_count + prior_mean * prior_strength) / (total_count + prior_strength)
    return round(max(0.0, min(0.85, mastery_rate)), 4)


# 维护意图：构造 student1 初始评测答题历史与掌握度预置数据
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_student1_assessment_attempt(
    *,
    student,
    course,
    points: list[object],
    selected_questions: list[object],
    prior_mean: float,
    prior_strength: float,
) -> Student1AssessmentAttempt:
    """构造 student1 初始评测答题历史与掌握度预置数据。"""
    total_score = Decimal("0")
    correct_count = 0
    raw_answers: dict[str, object] = {}
    question_details: list[dict[str, object]] = []
    point_stats: dict[int, dict[str, int | str]] = defaultdict(
        lambda: {"correct": 0, "total": 0, "name": ""}
    )

    planned_correct = [index % 5 != 1 for index in range(len(selected_questions))]
    for index, question in enumerate(selected_questions):
        answer_result = persist_student1_question_answer(
            student=student,
            course=course,
            question=question,
            intended_correct=planned_correct[index] if index < len(planned_correct) else True,
        )
        total_score += answer_result["earned"]
        correct_count += 1 if answer_result["is_correct"] else 0
        raw_answers[str(question.id)] = answer_result["student_answer"]
        question_details.append(answer_result["question_detail"])
        update_student1_point_stats(
            point_stats,
            answer_result["linked_points"],
            bool(answer_result["is_correct"]),
        )

    mastery_map = build_student1_mastery_map(
        points=points,
        point_stats=point_stats,
        course_id=int(course.pk),
        prior_mean=prior_mean,
        prior_strength=prior_strength,
    )
    return Student1AssessmentAttempt(
        total_score=total_score,
        max_possible=sum((question.score for question in selected_questions), Decimal("0")),
        correct_count=correct_count,
        raw_answers=raw_answers,
        question_details=question_details,
        point_stats=dict(point_stats),
        mastery_map=mastery_map,
        mastery_payload=build_mastery_payload(points, mastery_map, prior_mean),
    )


# 维护意图：写入单题预置答题历史并返回题目详情
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def persist_student1_question_answer(
    *,
    student,
    course,
    question,
    intended_correct: bool,
) -> dict[str, object]:
    """写入单题预置答题历史并返回题目详情。"""
    from assessments.models import AnswerHistory
    from common.utils import check_answer, extract_answer_value, serialize_answer_payload

    student_answer = build_student1_answer_value(question, intended_correct)
    correct_answer = extract_answer_value(question.answer)
    history_answer = serialize_answer_payload(question.question_type, student_answer)
    history_correct = serialize_answer_payload(question.question_type, correct_answer)
    is_correct = check_answer(question.question_type, student_answer, question.answer)
    earned = question.score if is_correct else Decimal("0")
    linked_points = list(question.knowledge_points.all())
    primary_point = linked_points[0] if linked_points else None

    AnswerHistory.objects.update_or_create(
        user=student,
        course=course,
        question=question,
        source="initial",
        defaults={
            "knowledge_point": primary_point,
            "student_answer": history_answer,
            "correct_answer": history_correct,
            "is_correct": is_correct,
            "score": earned,
            "exam_id": None,
        },
    )
    return {
        "earned": earned,
        "is_correct": is_correct,
        "student_answer": student_answer,
        "linked_points": linked_points,
        "question_detail": {
            "question_id": question.id,
            "content": question.content,
            "question_type": question.question_type,
            "student_answer": student_answer,
            "correct_answer": history_correct.get("answers") or history_correct.get("answer"),
            "is_correct": is_correct,
            "analysis": question.analysis or "",
            "knowledge_points": [
                {"id": point.id, "name": point.name}
                for point in linked_points
            ],
        },
    }


# 维护意图：累计预置评测关联知识点统计
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_student1_point_stats(
    point_stats: dict[int, dict[str, int | str]],
    linked_points: list[object],
    is_correct: bool,
) -> None:
    """累计预置评测关联知识点统计。"""
    for point in linked_points:
        point_stats[point.id]["total"] += 1
        point_stats[point.id]["name"] = point.name
        if is_correct:
            point_stats[point.id]["correct"] += 1


# 维护意图：根据答题统计和先修约束构造演示掌握度
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_student1_mastery_map(
    *,
    points: list[object],
    point_stats: dict[int, dict[str, int | str]],
    course_id: int,
    prior_mean: float,
    prior_strength: float,
) -> dict[int, float]:
    """根据答题统计和先修约束构造演示掌握度。"""
    from learning.path_rules import apply_prerequisite_caps

    mastery_map = {point.id: float(prior_mean) for point in points}
    for point_id, stats in point_stats.items():
        mastery_map[point_id] = calculate_initial_mastery_baseline(
            correct_count=int(stats["correct"]),
            total_count=int(stats["total"]),
            prior_mean=prior_mean,
            prior_strength=prior_strength,
        )
    return apply_prerequisite_caps(mastery_map, course_id)


# 维护意图：写入 student1 初始评测结果
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def persist_student1_assessment_result(
    *,
    student,
    course,
    assessment,
    attempt: Student1AssessmentAttempt,
):
    """写入 student1 初始评测结果。"""
    from assessments.models import AssessmentResult

    assessment_result, _ = AssessmentResult.objects.update_or_create(
        user=student,
        assessment=assessment,
        defaults={
            "course": course,
            "answers": attempt.raw_answers,
            "score": attempt.total_score,
            "result_data": {
                "mastery": attempt.mastery_payload,
                "question_details": attempt.question_details,
                "total_score": float(attempt.max_possible),
                "correct_count": attempt.correct_count,
                "total_count": len(attempt.raw_answers),
            },
        },
    )
    return assessment_result


# 维护意图：写入 student1 课程知识点掌握度
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def persist_student1_mastery(
    *,
    student,
    course,
    points: list[object],
    mastery_map: dict[int, float],
    prior_mean: float,
) -> None:
    """写入 student1 课程知识点掌握度。"""
    from knowledge.models import KnowledgeMastery

    for point in points:
        KnowledgeMastery.objects.update_or_create(
            user=student,
            course=course,
            knowledge_point=point,
            defaults={
                "mastery_rate": Decimal(
                    str(round(float(mastery_map.get(point.id, prior_mean)), 4))
                ),
            },
        )


# 维护意图：提取最多 3 个低掌握度知识点名称
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def weakest_point_names(mastery_payload: list[dict[str, object]]) -> list[str]:
    """提取最多 3 个低掌握度知识点名称。"""
    return [
        str(point["point_name"])
        for point in mastery_payload
        if float(point["mastery_rate"]) <= 0.3
    ][:3]
