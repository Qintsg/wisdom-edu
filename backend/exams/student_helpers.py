"""学生端考试接口共享 helper。"""
from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation

from common.utils import (
    build_answer_display,
    build_normalized_score_map,
    check_answer,
    clean_display_text,
    decorate_question_options,
    extract_answer_value,
    score_questions,
)
from knowledge.models import KnowledgeMastery, KnowledgePoint

from .models import ExamQuestion


logger = logging.getLogger(__name__)


def snapshot_mastery_for_points(user, course_id: int, point_ids: list[int]) -> dict[int, float]:
    """读取考试相关知识点的掌握度快照。"""
    if not point_ids:
        return {}
    return {
        row.knowledge_point_id: float(row.mastery_rate)
        for row in KnowledgeMastery.objects.filter(user=user, course_id=course_id, knowledge_point_id__in=point_ids)
    }


def build_mastery_change_payload(before_snapshot: dict[int, float], after_snapshot: dict[int, float]) -> list[dict[str, object]]:
    """构建报告可直接消费的掌握度变化明细。"""
    point_ids = sorted(set(before_snapshot.keys()) | set(after_snapshot.keys()))
    point_name_map = {row.id: row.name for row in KnowledgePoint.objects.filter(id__in=point_ids)}
    return [{
        "knowledge_point_id": point_id,
        "knowledge_point_name": point_name_map.get(point_id, f"知识点 {point_id}"),
        "mastery_before": round(float(before_snapshot.get(point_id, 0.0)), 4),
        "mastery_after": round(float(after_snapshot.get(point_id, before_snapshot.get(point_id, 0.0))), 4),
        "improvement": round(float(after_snapshot.get(point_id, before_snapshot.get(point_id, 0.0))) - float(before_snapshot.get(point_id, 0.0)), 4),
    } for point_id in point_ids]


def resolve_pass_threshold(exam) -> float:
    """解析考试及格线。"""
    try:
        threshold = float(Decimal(str(exam.pass_score)))
        if threshold > 0:
            return threshold
    except (TypeError, ValueError, InvalidOperation):
        pass

    try:
        total_score = float(Decimal(str(exam.total_score)))
    except (TypeError, ValueError, InvalidOperation):
        total_score = 100.0
    fallback = max(round(total_score * 0.6, 2), 1.0) if total_score > 0 else 60.0
    logger.warning(
        "检测到无效及格线，已使用兜底阈值: exam_id=%s, pass_score=%s, total_score=%s, fallback=%s",
        getattr(exam, "id", None),
        getattr(exam, "pass_score", None),
        getattr(exam, "total_score", None),
        fallback,
    )
    return fallback


def build_exam_score_map(exam, exam_questions):
    """构建考试题目分值映射。"""
    return build_normalized_score_map(
        [(exam_question.question_id, float(exam_question.score or getattr(exam_question.question, "score", 0) or 0)) for exam_question in exam_questions],
        target_total_score=float(exam.total_score or 0),
    )


def build_question_detail(question, student_answer, question_result):
    """构建单题回显详情。"""
    correct_answer = question_result.get("correct_answer", extract_answer_value(question.answer))
    is_correct = question_result.get("is_correct", check_answer(question.question_type, student_answer, question.answer))
    decorated_options = decorate_question_options(
        getattr(question, "options", None),
        question.question_type,
        student_answer=student_answer,
        correct_answer=correct_answer,
    )
    return {
        "question_id": question.id,
        "content": question.content,
        "question_type": question.question_type,
        "your_answer": student_answer,
        "student_answer": student_answer,
        "correct_answer": correct_answer,
        "student_answer_display": build_answer_display(student_answer, question.question_type, decorated_options),
        "correct_answer_display": build_answer_display(correct_answer, question.question_type, decorated_options),
        "is_correct": is_correct,
        "analysis": question_result.get("analysis") or getattr(question, "analysis", "") or "",
        "options": decorated_options,
        "score": question_result.get("earned_score", 0),
        "full_score": question_result.get("assigned_score", 0),
    }


def build_exam_question_details(exam_questions, answers, question_result_map):
    """构建整张试卷的题目详情列表。"""
    question_details = []
    for exam_question in exam_questions:
        question = exam_question.question
        student_answer = (answers or {}).get(str(question.id))
        question_details.append(build_question_detail(question, student_answer, question_result_map.get(str(question.id), {})))
    return question_details


def normalize_feedback_payload(report, question_details):
    """规范化反馈报告载荷。"""
    overview = dict(report.overview) if isinstance(report.overview, dict) else {}
    raw_analysis = report.analysis
    summary = clean_display_text(overview.get("summary")) if isinstance(overview, dict) else ""
    analysis_text = ""
    knowledge_gaps = []
    if isinstance(raw_analysis, str):
        analysis_text = clean_display_text(raw_analysis)
    elif isinstance(raw_analysis, list):
        if raw_analysis and all(isinstance(item, str) for item in raw_analysis):
            knowledge_gaps = [clean_display_text(item) for item in raw_analysis if clean_display_text(item)]
        elif raw_analysis and all(isinstance(item, dict) for item in raw_analysis):
            extracted_gaps = [clean_display_text(item.get("knowledge_point_name") or item.get("analysis")) for item in raw_analysis]
            knowledge_gaps = [item for item in extracted_gaps if item]
    elif isinstance(raw_analysis, dict):
        analysis_text = clean_display_text(raw_analysis.get("analysis"))
        gaps = raw_analysis.get("knowledge_gaps", [])
        if isinstance(gaps, list):
            knowledge_gaps = [clean_display_text(item) for item in gaps if clean_display_text(item)]

    if not summary:
        summary = analysis_text or clean_display_text(report.conclusion)
    if analysis_text == summary:
        analysis_text = ""
    if question_details:
        overview["score"] = round(sum(float(item.get("score") or 0) for item in question_details), 2)
        overview["correct_count"] = sum(1 for item in question_details if item["is_correct"])
        overview["total_count"] = len(question_details)
        overview["total_questions"] = len(question_details)
        overview["accuracy"] = round(overview["correct_count"] / max(len(question_details), 1) * 100, 1)

    correct_count = overview.get("correct_count")
    total_count = overview.get("total_count") or overview.get("total_questions")
    accuracy = overview.get("accuracy")
    mastery_changes = overview.get("mastery_changes", [])
    return {
        "report_id": report.id,
        "exam_id": report.exam_id,
        "status": report.status,
        "pending": report.status == "pending",
        "retryable": report.status == "failed",
        "poll_interval_ms": 2000 if report.status == "pending" else None,
        "overview": overview,
        "summary": summary,
        "analysis": analysis_text,
        "knowledge_gaps": knowledge_gaps,
        "recommendations": report.recommendations or [],
        "next_tasks": report.next_tasks or [],
        "conclusion": report.conclusion or "",
        "question_details": question_details,
        "correct_count": correct_count,
        "total_count": total_count,
        "accuracy": accuracy,
        "mastery_changes": mastery_changes if isinstance(mastery_changes, list) else [],
        "generated_at": report.generated_at.isoformat() if report.generated_at else None,
    }


def build_feedback_overview(
    *,
    score,
    total_score,
    passed,
    correct_count,
    total_count,
    accuracy,
    kt_analysis=None,
    summary="",
    knowledge_gaps=None,
    mastery_changes=None,
):
    """构建反馈概览字典。"""
    return {
        "score": float(score or 0),
        "total_score": float(total_score or 0),
        "passed": bool(passed),
        "correct_count": int(correct_count or 0),
        "total_count": int(total_count or 0),
        "total_questions": int(total_count or 0),
        "accuracy": float(accuracy or 0),
        "kt_analysis": kt_analysis or {},
        "summary": clean_display_text(summary),
        "knowledge_gaps": knowledge_gaps or [],
        "mastery_changes": mastery_changes or [],
    }


def build_feedback_report_ref(report):
    """构建反馈报告引用信息。"""
    return {"report_id": report.id, "exam_id": report.exam_id, "status": report.status, "retryable": report.status == "failed", "poll_url": f"/api/student/feedback/{report.exam_id}"}


def build_submission_feedback_snapshot(submission):
    """基于考试提交构建反馈快照。"""
    exam = submission.exam
    exam_questions = list(
        ExamQuestion.objects.filter(exam=exam).select_related("question").prefetch_related("question__knowledge_points").order_by("order")
    )
    questions = [exam_question.question for exam_question in exam_questions]
    score_map = build_exam_score_map(exam, exam_questions)
    grading = score_questions(submission.answers or {}, questions, score_map=score_map)
    question_result_map = {str(item["question_id"]): item for item in grading["question_results"]}
    question_details = build_exam_question_details(exam_questions, submission.answers or {}, question_result_map)
    correct_count = sum(1 for item in question_details if item["is_correct"])
    total_count = len(question_details)
    accuracy = round(correct_count / total_count * 100, 1) if total_count else 0
    return {
        "exam_questions": exam_questions,
        "grading": grading,
        "question_details": question_details,
        "correct_count": correct_count,
        "total_count": total_count,
        "accuracy": accuracy,
        "passed": float(grading["score"]) >= resolve_pass_threshold(exam),
    }
