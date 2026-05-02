from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import Any

from django.utils import timezone

from assessments.models import Question
from common.defense_demo_progress import _as_object_dict, _coerce_mastery_after_map
from common.utils import (
    build_normalized_score_map,
    extract_answer_value,
    score_questions,
)
from courses.models import Course
from exams.models import Exam, ExamQuestion, ExamSubmission, FeedbackReport
from knowledge.models import KnowledgeMastery, KnowledgePoint
from users.models import User


def build_stage_feedback_payload(points: list[KnowledgePoint]) -> dict[str, object]:
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


def load_stage_exam_questions(stage_exam: Exam) -> list[ExamQuestion]:
    """
    加载阶段测试题目及其知识点。
    :param stage_exam: 阶段测试试卷。
    :return: 按题目顺序排列的试卷题目。
    """
    return list(
        ExamQuestion.objects.filter(exam=stage_exam)
        .select_related("question")
        .prefetch_related("question__knowledge_points")
        .order_by("order")
    )


def collect_exam_questions(stage_exam_questions: list[ExamQuestion]) -> list[Question]:
    """
    从 ExamQuestion 列表中提取 Question。
    :param stage_exam_questions: 阶段测试题目关联。
    :return: 题目列表。
    """
    return [exam_question.question for exam_question in stage_exam_questions]


def build_submission_answers(questions: list[Question]) -> dict[str, object]:
    """
    生成演示阶段测试的全正确提交答案。
    :param questions: 阶段测试题目。
    :return: 以题目 ID 字符串为 key 的答案字典。
    """
    return {
        str(question.id): extract_answer_value(question.answer)
        for question in questions
    }


def build_stage_score_map(stage_exam: Exam, stage_exam_questions: list[ExamQuestion]) -> dict[int, float]:
    """
    构建阶段测试每题标准化得分映射。
    :param stage_exam: 阶段测试试卷。
    :param stage_exam_questions: 阶段测试题目关联。
    :return: 题目 ID 到得分的映射。
    """
    raw_scores = [
        (exam_question.question_id, float(exam_question.score or exam_question.question.score or 0))
        for exam_question in stage_exam_questions
    ]
    return build_normalized_score_map(
        raw_scores,
        target_total_score=float(stage_exam.total_score or 0),
    )


def grade_stage_exam(
    stage_exam: Exam,
    stage_exam_questions: list[ExamQuestion],
    questions: list[Question],
    submission_answers: dict[str, object],
) -> dict[str, Any]:
    """
    按真实评分工具计算演示阶段测试成绩。
    :param stage_exam: 阶段测试试卷。
    :param stage_exam_questions: 阶段测试题目关联。
    :param questions: 阶段测试题目。
    :param submission_answers: 提交答案。
    :return: 评分结果。
    """
    score_map = build_stage_score_map(stage_exam, stage_exam_questions)
    return score_questions(submission_answers, questions, score_map=score_map)


def resolve_pass_score(stage_exam: Exam, grading: dict[str, Any]) -> float:
    """
    解析阶段测试通过线，缺失时按总分 60% 兜底。
    :param stage_exam: 阶段测试试卷。
    :param grading: 评分结果。
    :return: 通过分数。
    """
    pass_score = float(stage_exam.pass_score or 0)
    if pass_score > 0:
        return pass_score
    return max(round(float(grading["total_score"]) * 0.6, 2), 1.0)


def upsert_stage_submission(
    stage_exam: Exam,
    warmup_student: User,
    submission_answers: dict[str, object],
    grading: dict[str, Any],
    submitted_at,
    passed: bool,
) -> ExamSubmission:
    """
    创建或更新预热账号的阶段测试提交。
    :param stage_exam: 阶段测试试卷。
    :param warmup_student: 预热学生账号。
    :param submission_answers: 提交答案。
    :param grading: 评分结果。
    :param submitted_at: 固定提交时间。
    :param passed: 是否通过。
    :return: 提交记录。
    """
    submission, _ = ExamSubmission.objects.update_or_create(
        exam=stage_exam,
        user=warmup_student,
        defaults={
            "answers": submission_answers,
            "score": Decimal(str(float(grading["score"]))),
            "is_passed": passed,
            "graded_at": submitted_at + timedelta(minutes=18),
        },
    )
    if submission.submitted_at != submitted_at:
        submission.submitted_at = submitted_at
        submission.save(update_fields=["submitted_at"])
    return submission


def build_mastery_changes(
    course: Course,
    warmup_student: User,
    points: list[KnowledgePoint],
    stage_feedback: dict[str, object],
) -> list[dict[str, object]]:
    """
    更新预热账号阶段测试后的掌握度，并返回掌握度变化摘要。
    :param course: 主课程。
    :param warmup_student: 预热学生账号。
    :param points: 演示知识点列表。
    :param stage_feedback: 阶段测试固定反馈。
    :return: 掌握度变化列表。
    """
    mastery_after_map = _coerce_mastery_after_map(stage_feedback.get("mastery_after"))
    mastery_changes: list[dict[str, object]] = []
    for point in points:
        mastery_after = mastery_after_map.get(point.id)
        if mastery_after is None:
            continue
        mastery_before = resolve_mastery_before(course, warmup_student, point, mastery_after)
        KnowledgeMastery.objects.update_or_create(
            user=warmup_student,
            course=course,
            knowledge_point=point,
            defaults={"mastery_rate": Decimal(str(float(mastery_after)))},
        )
        mastery_changes.append(
            build_mastery_change_item(point, mastery_before, float(mastery_after))
        )
    return mastery_changes


def resolve_mastery_before(
    course: Course,
    warmup_student: User,
    point: KnowledgePoint,
    mastery_after: float,
) -> float:
    """
    推导阶段测试前掌握度，优先使用已有记录，不合理时使用固定回退值。
    :param course: 主课程。
    :param warmup_student: 预热学生账号。
    :param point: 知识点。
    :param mastery_after: 阶段测试后掌握度。
    :return: 阶段测试前掌握度。
    """
    mastery_record = KnowledgeMastery.objects.filter(
        user=warmup_student,
        course=course,
        knowledge_point=point,
    ).first()
    existing_before = float(mastery_record.mastery_rate) if mastery_record else 0.0
    fallback_before = max(round(float(mastery_after) - 0.18, 2), 0.28)
    if 0 < existing_before < float(mastery_after):
        return existing_before
    return fallback_before


def build_mastery_change_item(
    point: KnowledgePoint,
    mastery_before: float,
    mastery_after: float,
) -> dict[str, object]:
    """
    构造单个知识点掌握度变化项。
    :param point: 知识点。
    :param mastery_before: 测试前掌握度。
    :param mastery_after: 测试后掌握度。
    :return: 掌握度变化字典。
    """
    return {
        "knowledge_point_id": point.id,
        "knowledge_point_name": point.name,
        "mastery_before": round(float(mastery_before), 4),
        "mastery_after": round(float(mastery_after), 4),
        "improvement": round(float(mastery_after) - float(mastery_before), 4),
    }


def upsert_stage_feedback_report(
    warmup_student: User,
    stage_exam: Exam,
    submission: ExamSubmission,
    grading: dict[str, Any],
    passed: bool,
    questions: list[Question],
    stage_feedback: dict[str, object],
    mastery_changes: list[dict[str, object]],
) -> None:
    """
    创建或更新预热账号阶段测试反馈报告。
    :param warmup_student: 预热学生账号。
    :param stage_exam: 阶段测试试卷。
    :param submission: 阶段测试提交记录。
    :param grading: 评分结果。
    :param passed: 是否通过。
    :param questions: 阶段测试题目。
    :param stage_feedback: 固定反馈 payload。
    :param mastery_changes: 掌握度变化列表。
    :return: None。
    """
    feedback_payload = _as_object_dict(stage_feedback.get("feedback_report"))
    FeedbackReport.objects.update_or_create(
        user=warmup_student,
        exam=stage_exam,
        defaults={
            "source": "exam",
            "exam_submission": submission,
            "status": "completed",
            "overview": build_feedback_overview(
                grading,
                passed,
                questions,
                feedback_payload,
                mastery_changes,
            ),
            "analysis": feedback_payload.get("analysis", ""),
            "recommendations": feedback_payload.get("recommendations", []),
            "next_tasks": feedback_payload.get("next_tasks", []),
            "conclusion": feedback_payload.get("conclusion", ""),
        },
    )


def build_feedback_overview(
    grading: dict[str, Any],
    passed: bool,
    questions: list[Question],
    feedback_payload: dict[str, object],
    mastery_changes: list[dict[str, object]],
) -> dict[str, object]:
    """
    构建反馈报告 overview 字段。
    :param grading: 评分结果。
    :param passed: 是否通过。
    :param questions: 阶段测试题目。
    :param feedback_payload: 固定反馈内容。
    :param mastery_changes: 掌握度变化列表。
    :return: overview 字典。
    """
    return {
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
    }


def ensure_warmup_stage_submission_and_feedback(
    course: Course,
    warmup_student: User,
    stage_exam: Exam,
    points: list[KnowledgePoint],
) -> dict[str, object]:
    """
    为预热账号补齐真实阶段测试提交与反馈报告。
    :param course: 主课程。
    :param warmup_student: 预热学生账号。
    :param stage_exam: 阶段测试试卷。
    :param points: 演示知识点列表。
    :return: 提交时间与阶段反馈上下文。
    """
    stage_feedback = build_stage_feedback_payload(points)
    stage_exam_questions = load_stage_exam_questions(stage_exam)
    if not stage_exam_questions:
        return {"submitted_at": timezone.now(), "stage_feedback": stage_feedback}

    questions = collect_exam_questions(stage_exam_questions)
    submission_answers = build_submission_answers(questions)
    grading = grade_stage_exam(stage_exam, stage_exam_questions, questions, submission_answers)
    submitted_at = timezone.now() - timedelta(days=1, hours=3)
    pass_score = resolve_pass_score(stage_exam, grading)
    passed = float(grading["score"]) >= pass_score
    submission = upsert_stage_submission(
        stage_exam,
        warmup_student,
        submission_answers,
        grading,
        submitted_at,
        passed,
    )
    mastery_changes = build_mastery_changes(course, warmup_student, points, stage_feedback)
    upsert_stage_feedback_report(
        warmup_student,
        stage_exam,
        submission,
        grading,
        passed,
        questions,
        stage_feedback,
        mastery_changes,
    )
    return {"submitted_at": submitted_at, "stage_feedback": stage_feedback}
