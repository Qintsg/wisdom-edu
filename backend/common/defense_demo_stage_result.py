from __future__ import annotations

from typing import Any

from assessments.models import Question
from common.defense_demo_progress import (
    _as_object_dict,
    _build_mastery_change_payload,
    _coerce_mastery_after_map,
    _question_knowledge_points,
)
from common.defense_demo_stage import (
    build_stage_feedback_payload,
    build_submission_answers,
    collect_exam_questions,
    grade_stage_exam,
    load_stage_exam_questions,
)
from common.utils import (
    build_answer_display,
    decorate_question_options,
    extract_answer_value,
)
from exams.models import Exam
from knowledge.models import KnowledgePoint


# 维护意图：把评分明细按题目 ID 建索引。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_question_result_map(grading: dict[str, Any]) -> dict[str, dict[str, object]]:
    """
    把评分明细按题目 ID 建索引。
    :param grading: 评分结果。
    :return: 题目 ID 字符串到评分明细的映射。
    """
    return {
        str(item["question_id"]): item
        for item in grading["question_results"]
    }


# 维护意图：构造阶段测试单题展示明细。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_question_detail(
    question: Question,
    submission_answers: dict[str, object],
    question_result_map: dict[str, dict[str, object]],
) -> dict[str, object]:
    """
    构造阶段测试单题展示明细。
    :param question: 题目。
    :param submission_answers: 提交答案。
    :param question_result_map: 评分明细映射。
    :return: 单题展示字典。
    """
    question_id = str(question.id)
    result_payload = question_result_map.get(question_id, {})
    student_answer = submission_answers[question_id]
    correct_answer = result_payload.get(
        "correct_answer",
        extract_answer_value(question.answer),
    )
    decorated_options = decorate_question_options(
        question.options,
        question.question_type,
        student_answer=student_answer,
        correct_answer=correct_answer,
    )
    return {
        "question_id": question.id,
        "content": question.content,
        "question_type": question.question_type,
        "student_answer": student_answer,
        "correct_answer": correct_answer,
        "student_answer_display": build_answer_display(
            student_answer,
            question.question_type,
            decorated_options,
        ),
        "correct_answer_display": build_answer_display(
            correct_answer,
            question.question_type,
            decorated_options,
        ),
        "is_correct": True,
        "analysis": question.analysis or "",
        "options": decorated_options,
        "knowledge_points": [
            {"id": point.id, "name": point.name}
            for point in _question_knowledge_points(question)
        ],
        "score": result_payload.get("earned_score", 0),
        "full_score": result_payload.get("assigned_score", 0),
    }


# 维护意图：构造阶段测试全部题目展示明细。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_question_details(
    questions: list[Question],
    submission_answers: dict[str, object],
    question_result_map: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    """
    构造阶段测试全部题目展示明细。
    :param questions: 阶段测试题目。
    :param submission_answers: 提交答案。
    :param question_result_map: 评分明细映射。
    :return: 单题展示列表。
    """
    return [
        build_question_detail(question, submission_answers, question_result_map)
        for question in questions
    ]


# 维护意图：生成已完成阶段测试的固定结果快照，供预热账号直接展示完整报告页。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_demo_stage_test_result(
    stage_exam: Exam,
    points: list[KnowledgePoint],
    mastery_before_snapshot: dict[int, float],
    submitted_at,
) -> dict[str, object]:
    """
    生成已完成阶段测试的固定结果快照，供预热账号直接展示完整报告页。
    :param stage_exam: 阶段测试试卷。
    :param points: 演示知识点列表。
    :param mastery_before_snapshot: 阶段测试前的掌握度快照。
    :param submitted_at: 固定提交时间。
    :return: 阶段测试结果字典。
    """
    stage_exam_questions = load_stage_exam_questions(stage_exam)
    questions = collect_exam_questions(stage_exam_questions)
    submission_answers = build_submission_answers(questions)
    grading = grade_stage_exam(stage_exam, stage_exam_questions, questions, submission_answers)
    stage_feedback = build_stage_feedback_payload(points)
    mastery_after_snapshot = _coerce_mastery_after_map(stage_feedback.get("mastery_after"))
    question_result_map = build_question_result_map(grading)
    return {
        "score": float(grading["score"]),
        "total_score": float(grading["total_score"]),
        "passed": True,
        "pass_threshold": float(stage_exam.pass_score or 60),
        "correct": len(questions),
        "correct_count": len(questions),
        "total": len(questions),
        "total_count": len(questions),
        "accuracy": 100.0,
        "mistakes": [],
        "question_details": build_question_details(
            questions,
            submission_answers,
            question_result_map,
        ),
        "point_stats": grading["point_stats"],
        "mastery_changes": _build_mastery_change_payload(
            points,
            mastery_before_snapshot,
            mastery_after_snapshot,
        ),
        "feedback_report": _as_object_dict(stage_feedback.get("feedback_report")),
        "submitted_at": submitted_at.isoformat(),
        "node_status": "completed",
        "path_refreshed": True,
    }
