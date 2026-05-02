"""考试反馈报告服务辅助工具。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ReportGenerationContext:
    """一次反馈报告生成所需的批改与画像上下文。"""

    exam_questions: list[Any]
    questions: list[Any]
    grading: dict[str, Any]
    question_details: list[dict[str, Any]]
    mistakes: list[dict[str, Any]]
    correct_count: int
    total_count: int
    accuracy: float
    answer_history_records: list[dict[str, int]]
    kt_analysis: dict[str, Any]
    detailed_mistakes: list[dict[str, Any]]
    ability_data: dict[str, Any]
    habit_data: dict[str, Any] | None


@dataclass
class NormalizedLLMFeedback:
    """规范化后的 LLM 报告字段。"""

    summary: str
    analysis: str
    knowledge_gaps: list[Any]
    recommendations: list[Any]
    next_tasks: list[Any]
    conclusion: str


def build_report_generation_context(*, report, exam, submission, load_exam_questions, build_exam_score_map, build_exam_question_details, build_answer_history_records, refresh_kt_analysis, build_detailed_mistakes, extract_habit_preferences) -> ReportGenerationContext:
    """构造反馈报告生成过程中需要的完整上下文。"""
    from assessments.models import AbilityScore
    from common.utils import score_questions

    exam_questions = list(
        load_exam_questions(exam)
    )
    questions = [exam_question.question for exam_question in exam_questions]
    score_map = build_exam_score_map(exam, exam_questions)
    grading = score_questions(submission.answers or {}, questions, score_map=score_map)
    question_result_map = {
        str(item["question_id"]): item for item in grading["question_results"]
    }
    question_details = build_exam_question_details(
        exam_questions, submission.answers or {}, question_result_map
    )
    mistakes = [detail for detail in question_details if not detail["is_correct"]]
    correct_count = sum(1 for item in question_details if item["is_correct"])
    total_count = len(question_details)
    accuracy = round(correct_count / total_count * 100, 1) if total_count else 0

    submission_answers = submission.answers or {}
    answer_history_records = build_answer_history_records(
        exam_questions,
        submission_answers,
    )
    kt_analysis = refresh_kt_analysis(
        report,
        exam,
        report.user,
        answer_history_records,
    )
    detailed_mistakes = build_detailed_mistakes(exam_questions, mistakes)
    ability = AbilityScore.objects.filter(user=report.user, course_id=exam.course_id).first()
    ability_data = ability.scores if ability and isinstance(ability.scores, dict) else {}
    habit_data = extract_habit_preferences(report.user)
    return ReportGenerationContext(
        exam_questions=exam_questions,
        questions=questions,
        grading=grading,
        question_details=question_details,
        mistakes=mistakes,
        correct_count=correct_count,
        total_count=total_count,
        accuracy=accuracy,
        answer_history_records=answer_history_records,
        kt_analysis=kt_analysis,
        detailed_mistakes=detailed_mistakes,
        ability_data=ability_data,
        habit_data=habit_data,
    )


def normalize_llm_feedback(
    *,
    llm_result: dict[str, Any],
    clean_text,
    normalize_list,
) -> NormalizedLLMFeedback:
    """把 LLM 结构化结果规整为稳定字段。"""
    summary = clean_text(llm_result.get("summary"))
    analysis = clean_text(llm_result.get("analysis"))
    knowledge_gaps = normalize_list(llm_result, "knowledge_gaps")
    recommendations = normalize_list(llm_result, "recommendations")
    next_tasks = normalize_list(llm_result, "next_tasks")
    conclusion = clean_text(
        llm_result.get("encouragement") or llm_result.get("conclusion")
    )
    if not summary:
        summary = analysis or conclusion or "AI 报告已生成。"
    return NormalizedLLMFeedback(
        summary=summary,
        analysis=analysis,
        knowledge_gaps=knowledge_gaps,
        recommendations=recommendations,
        next_tasks=next_tasks,
        conclusion=conclusion,
    )


def build_report_overview(
    *,
    report,
    exam,
    grading: dict[str, Any],
    pass_threshold: float,
    correct_count: int,
    total_count: int,
    accuracy: float,
    kt_analysis: dict[str, Any],
    ability_data: dict[str, Any],
    habit_data: dict[str, Any] | None,
    summary: str,
    knowledge_gaps: list[Any],
) -> dict[str, Any]:
    """构造反馈报告 overview。"""
    existing_overview = dict(report.overview) if isinstance(report.overview, dict) else {}
    return {
        "score": float(grading["score"]),
        "total_score": float(exam.total_score),
        "passed": float(grading["score"]) >= pass_threshold,
        "correct_count": correct_count,
        "total_count": total_count,
        "total_questions": total_count,
        "accuracy": accuracy,
        "kt_analysis": kt_analysis,
        "ability_scores": ability_data,
        "habit_preferences": habit_data,
        "summary": summary,
        "knowledge_gaps": knowledge_gaps,
        "mastery_changes": existing_overview.get("mastery_changes", []),
    }


def apply_completed_report(
    *,
    report,
    overview: dict[str, Any],
    normalized_feedback: NormalizedLLMFeedback,
    detailed_mistakes: list[dict[str, Any]],
    save_fields: list[str],
) -> dict[str, Any]:
    """把成功生成的反馈报告写回模型。"""
    report.overview = overview
    report.status = "completed"
    report.analysis = (
        normalized_feedback.analysis
        or normalized_feedback.knowledge_gaps
        or [
            {
                "question_id": item["question_id"],
                "analysis": item.get("analysis") or "暂无解析",
                "knowledge_point_name": item.get("knowledge_point_name", ""),
            }
            for item in detailed_mistakes
        ]
    )
    report.recommendations = normalized_feedback.recommendations
    report.next_tasks = normalized_feedback.next_tasks
    report.conclusion = normalized_feedback.conclusion or "继续保持，按建议逐步巩固即可。"
    report.save(update_fields=save_fields)
    return overview
