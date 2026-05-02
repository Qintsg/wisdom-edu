from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from common.defense_demo_progress import (
    _as_object_dict,
    _build_mastery_change_payload,
    _coerce_mastery_after_map,
    _question_knowledge_points,
)
from common.utils import (
    build_answer_display,
    build_normalized_score_map,
    decorate_question_options,
    extract_answer_value,
    score_questions,
)
from courses.models import Course
from exams.models import Exam, ExamQuestion, ExamSubmission, FeedbackReport
from knowledge.models import KnowledgeMastery, KnowledgePoint
from users.models import User

def _build_stage_feedback_payload(points: list[KnowledgePoint]) -> dict[str, object]:
    """
    构建阶段测试固定反馈结果。
    :param points: 知识点列表。
    :return: 阶段测试反馈字典。
    """
    return {
        "feedback_report": {
            "summary": "阶段测试结果表明该学生已经完成从概念理解到框架认知的第一轮迁移，适合进入下一阶段资源巩固。",
            "analysis": "三道题均回答正确，说明学生已经能够把大数据概念、Hadoop 生态和 Spark 计算模型串联成完整的知识结构。",
            "knowledge_gaps": [points[2].name],
            "recommendations": [
                "继续通过资源巩固 Spark 的内存计算和执行抽象。",
                "回到知识图谱页面，观察知识点之间的前置与后继关系。",
                "进入后续节点完成进阶资源拓展。",
            ],
            "next_tasks": [
                "查看刷新出的后续学习节点。",
                "继续完成课程资源页中的拓展学习。",
            ],
            "conclusion": "测试通过，系统已根据掌握度变化准备下一阶段学习内容。",
        },
        "mastery_after": {
            points[0].id: 0.72,
            points[1].id: 0.81,
            points[2].id: 0.86,
        },
    }


def _ensure_warmup_stage_submission_and_feedback(
    course: Course,
    warmup_student: User,
    stage_exam: Exam,
    points: list[KnowledgePoint],
) -> dict[str, object]:
    """
    为预热账号补齐真实阶段测试提交与反馈报告。

    这样学生端的考试结果页、反馈报告页和浏览器巡检都能命中真实数据，
    避免预热账号只有练习轨迹、却没有可直接展示的阶段测试结果。

    :param course: 主课程。
    :param warmup_student: 预热学生账号。
    :param stage_exam: 阶段测试试卷。
    :param points: 演示知识点列表。
    :return: None。
    """
    stage_exam_questions = list(
        ExamQuestion.objects.filter(exam=stage_exam)
        .select_related("question")
        .prefetch_related("question__knowledge_points")
        .order_by("order")
    )
    stage_feedback = _build_stage_feedback_payload(points)
    if not stage_exam_questions:
        return {"submitted_at": timezone.now(), "stage_feedback": stage_feedback}

    questions = [exam_question.question for exam_question in stage_exam_questions]
    submission_answers = {
        str(question.id): extract_answer_value(question.answer)
        for question in questions
    }
    score_map = build_normalized_score_map(
        [
            (exam_question.question_id, float(exam_question.score or exam_question.question.score or 0))
            for exam_question in stage_exam_questions
        ],
        target_total_score=float(stage_exam.total_score or 0),
    )
    grading = score_questions(submission_answers, questions, score_map=score_map)
    submitted_at = timezone.now() - timedelta(days=1, hours=3)
    graded_at = submitted_at + timedelta(minutes=18)
    pass_score = float(stage_exam.pass_score or 0)
    if pass_score <= 0:
        pass_score = max(round(float(grading["total_score"]) * 0.6, 2), 1.0)
    passed = float(grading["score"]) >= pass_score

    submission, _ = ExamSubmission.objects.update_or_create(
        exam=stage_exam,
        user=warmup_student,
        defaults={
            "answers": submission_answers,
            "score": Decimal(str(float(grading["score"]))),
            "is_passed": passed,
            "graded_at": graded_at,
        },
    )
    if submission.submitted_at != submitted_at:
        submission.submitted_at = submitted_at
        submission.save(update_fields=["submitted_at"])

    mastery_after_map = _coerce_mastery_after_map(stage_feedback.get("mastery_after"))
    mastery_changes: list[dict[str, object]] = []
    for point in points:
        mastery_after = mastery_after_map.get(point.id)
        if mastery_after is None:
            continue
        mastery_record = KnowledgeMastery.objects.filter(
            user=warmup_student,
            course=course,
            knowledge_point=point,
        ).first()
        existing_before = float(mastery_record.mastery_rate) if mastery_record else 0.0
        fallback_before = max(round(float(mastery_after) - 0.18, 2), 0.28)
        mastery_before = (
            existing_before
            if 0 < existing_before < float(mastery_after)
            else fallback_before
        )
        KnowledgeMastery.objects.update_or_create(
            user=warmup_student,
            course=course,
            knowledge_point=point,
            defaults={"mastery_rate": Decimal(str(float(mastery_after)))},
        )
        mastery_changes.append(
            {
                "knowledge_point_id": point.id,
                "knowledge_point_name": point.name,
                "mastery_before": round(float(mastery_before), 4),
                "mastery_after": round(float(mastery_after), 4),
                "improvement": round(float(mastery_after) - float(mastery_before), 4),
            }
        )

    feedback_payload = _as_object_dict(stage_feedback.get("feedback_report"))
    FeedbackReport.objects.update_or_create(
        user=warmup_student,
        exam=stage_exam,
        defaults={
            "source": "exam",
            "exam_submission": submission,
            "status": "completed",
            "overview": {
                "score": round(float(grading["score"]), 2),
                "total_score": round(float(grading["total_score"]), 2),
                "passed": passed,
                "correct_count": len(questions),
                "total_count": len(questions),
                "total_questions": len(questions),
                "accuracy": 100.0,
                "summary": feedback_payload.get("summary", ""),
                "knowledge_gaps": feedback_payload.get("knowledge_gaps", []),
                "mastery_changes": mastery_changes,
            },
            "analysis": feedback_payload.get("analysis", ""),
            "recommendations": feedback_payload.get("recommendations", []),
            "next_tasks": feedback_payload.get("next_tasks", []),
            "conclusion": feedback_payload.get("conclusion", ""),
        },
    )
    return {"submitted_at": submitted_at, "stage_feedback": stage_feedback}


def _build_demo_stage_test_result(
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
    stage_exam_questions = list(
        ExamQuestion.objects.filter(exam=stage_exam)
        .select_related("question")
        .prefetch_related("question__knowledge_points")
        .order_by("order")
    )
    questions = [exam_question.question for exam_question in stage_exam_questions]
    submission_answers = {
        str(question.id): extract_answer_value(question.answer)
        for question in questions
    }
    score_map = build_normalized_score_map(
        [
            (exam_question.question_id, float(exam_question.score or exam_question.question.score or 0))
            for exam_question in stage_exam_questions
        ],
        target_total_score=float(stage_exam.total_score or 0),
    )
    grading = score_questions(submission_answers, questions, score_map=score_map)
    stage_feedback = _build_stage_feedback_payload(points)
    mastery_after_snapshot = _coerce_mastery_after_map(stage_feedback.get("mastery_after"))
    question_result_map = {
        str(item["question_id"]): item for item in grading["question_results"]
    }
    question_details: list[dict[str, object]] = []
    for question in questions:
        question_id = str(question.id)
        student_answer = submission_answers[question_id]
        correct_answer = question_result_map.get(question_id, {}).get(
            "correct_answer",
            extract_answer_value(question.answer),
        )
        decorated_options = decorate_question_options(
            question.options,
            question.question_type,
            student_answer=student_answer,
            correct_answer=correct_answer,
        )
        question_details.append(
            {
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
                "score": question_result_map.get(question_id, {}).get("earned_score", 0),
                "full_score": question_result_map.get(question_id, {}).get("assigned_score", 0),
            }
        )

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
        "question_details": question_details,
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
