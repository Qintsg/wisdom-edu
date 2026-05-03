"""阶段测试评分与每题反馈详情构建。"""

from __future__ import annotations

import logging

from assessments.models import AnswerHistory, Question
from common.utils import (
    build_answer_display,
    build_normalized_score_map,
    check_answer,
    decorate_question_options,
    extract_answer_value,
    score_questions,
    serialize_answer_payload,
)
from knowledge.models import KnowledgePoint
from learning.models import PathNode
from learning.stage_test_models import PASS_THRESHOLD, TOTAL_SCORE, StageTestEvaluation
from users.models import User


logger = logging.getLogger(__name__)


# 维护意图：读取题目、评分并记录每题作答历史
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def evaluate_stage_test(
    *,
    node: PathNode,
    user: User,
    answers: dict[str, object],
) -> StageTestEvaluation:
    """读取题目、评分并记录每题作答历史。"""
    question_ids = question_ids_from_answers(answers)
    question_map = question_map_for_node(node, question_ids)
    questions = [question_map[question_id] for question_id in question_ids if question_id in question_map]
    grading = grade_stage_questions(answers, questions)
    question_result_map = {
        str(item["question_id"]): item
        for item in grading["question_results"]
    }
    question_details = build_question_details(
        node=node,
        user=user,
        answers=answers,
        questions=questions,
        question_result_map=question_result_map,
    )
    detailed_mistakes = build_detailed_mistakes(question_details, question_map)
    score = float(grading["score"])
    correct_count = sum(1 for item in grading["question_results"] if item["is_correct"])
    total_count = len(questions)

    return StageTestEvaluation(
        answers=answers,
        questions=questions,
        question_map=question_map,
        point_stats=grading["point_stats"],
        question_details=question_details,
        detailed_mistakes=detailed_mistakes,
        score=score,
        passed=score >= PASS_THRESHOLD,
        correct_count=correct_count,
        total_count=total_count,
        accuracy=round(correct_count / total_count * 100, 1) if total_count else 0,
    )


# 维护意图：将前端答案 key 转成题目 ID，忽略无法解析的异常 key
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def question_ids_from_answers(answers: dict[str, object]) -> list[int]:
    """将前端答案 key 转成题目 ID，忽略无法解析的异常 key。"""
    question_ids: list[int] = []
    for question_id_text in answers:
        try:
            question_ids.append(int(question_id_text))
        except (TypeError, ValueError):
            logger.warning("阶段测试答案包含非法题目ID: %s", question_id_text)
    return question_ids


# 维护意图：按课程约束读取可评分题目
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def question_map_for_node(node: PathNode, question_ids: list[int]) -> dict[int, Question]:
    """按课程约束读取可评分题目。"""
    return {
        question.id: question
        for question in Question.objects.filter(
            id__in=question_ids,
            course=node.path.course,
        ).prefetch_related("knowledge_points")
    }


# 维护意图：使用统一评分工具按 100 分制计算阶段测试成绩
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def grade_stage_questions(
    answers: dict[str, object],
    questions: list[Question],
) -> dict[str, object]:
    """使用统一评分工具按 100 分制计算阶段测试成绩。"""
    stage_score_map = build_normalized_score_map(
        [(question.id, 1) for question in questions],
        target_total_score=TOTAL_SCORE,
        equal_weight=True,
    )
    return score_questions(answers, questions, score_map=stage_score_map)


# 维护意图：生成每题详情并写入 AnswerHistory
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_question_details(
    *,
    node: PathNode,
    user: User,
    answers: dict[str, object],
    questions: list[Question],
    question_result_map: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    """生成每题详情并写入 AnswerHistory。"""
    question_details: list[dict[str, object]] = []
    for question in questions:
        result = question_result_map.get(str(question.id), {})
        question_detail = build_single_question_detail(
            node=node,
            user=user,
            answers=answers,
            question=question,
            result=result,
        )
        question_details.append(question_detail)
    return question_details


# 维护意图：构造单题反馈详情并记录作答历史
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_single_question_detail(
    *,
    node: PathNode,
    user: User,
    answers: dict[str, object],
    question: Question,
    result: dict[str, object],
) -> dict[str, object]:
    """构造单题反馈详情并记录作答历史。"""
    student_answer = answers.get(str(question.id))
    correct_value = result.get("correct_answer", extract_answer_value(question.answer))
    is_correct = result.get(
        "is_correct",
        check_answer(question.question_type, student_answer, question.answer),
    )
    decorated_options = decorate_question_options(
        question.options,
        question.question_type,
        student_answer=student_answer,
        correct_answer=correct_value,
    )
    question_points: list[KnowledgePoint] = list(question.knowledge_points.all())
    primary_point = question_points[0] if question_points else None
    AnswerHistory.objects.create(
        user=user,
        course=node.path.course,
        question=question,
        knowledge_point=primary_point,
        student_answer=serialize_answer_payload(question.question_type, student_answer),
        correct_answer=serialize_answer_payload(question.question_type, correct_value),
        is_correct=is_correct,
        score=result.get("earned_score", 0),
    )
    return {
        "question_id": question.id,
        "content": question.content,
        "question_type": question.question_type,
        "student_answer": student_answer,
        "correct_answer": correct_value,
        "student_answer_display": build_answer_display(
            student_answer,
            question.question_type,
            decorated_options,
        ),
        "correct_answer_display": build_answer_display(
            correct_value,
            question.question_type,
            decorated_options,
        ),
        "is_correct": is_correct,
        "analysis": result.get("analysis") or question.analysis or "",
        "options": decorated_options,
        "knowledge_points": [
            {"id": point.id, "name": point.name}
            for point in question_points
        ],
        "score": result.get("earned_score", 0),
        "full_score": result.get("assigned_score", 0),
    }


# 维护意图：从题目详情中提取错题报告输入
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_detailed_mistakes(
    question_details: list[dict[str, object]],
    question_map: dict[int, Question],
) -> list[dict[str, object]]:
    """从题目详情中提取错题报告输入。"""
    return [
        mistake_detail(item, question_map.get(item["question_id"]))
        for item in question_details
        if not item["is_correct"]
    ]


# 维护意图：构造单道错题详情
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def mistake_detail(
    item: dict[str, object],
    question: Question | None,
) -> dict[str, object]:
    """构造单道错题详情。"""
    related_points = list(question.knowledge_points.all()) if question else []
    primary_point = related_points[0] if related_points else None
    return {
        "question_id": item["question_id"],
        "question_text": question.content if question else "",
        "knowledge_point_name": primary_point.name if primary_point else "",
        "student_answer": item.get("student_answer"),
        "correct_answer": item.get("correct_answer"),
        "student_answer_display": item.get("student_answer_display"),
        "correct_answer_display": item.get("correct_answer_display"),
        "analysis": item.get("analysis") or (question.analysis if question else ""),
        "options": item.get("options", []),
    }
