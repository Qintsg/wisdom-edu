#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
student1 大数据学习状态预置脚本。
@Project : wisdom-edu
@File : demo_student1_snapshot.py
@Author : Qintsg
@Date : 2026-05-13 13:20
'''

from __future__ import annotations

from decimal import Decimal

from django.db import transaction

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
from knowledge.services.content_binding import CourseContentBindingService
from knowledge.models import KnowledgeMastery, KnowledgePoint, ProfileSummary
from learning.models import LearningPath
from tools.demo_student1_snapshot_parse import load_inline_snapshot
from tools.demo_student1_snapshot_support import (
    attach_node_resources,
    build_snapshot_mastery_rates,
    create_path_node,
    default_ability_scores,
    mastery_payload_for_course,
    write_feedback_report,
    write_snapshot_metadata,
)
from tools.demo_student1_snapshot_types import (
    DEMO_COURSE_NAME,
    DEMO_STUDENT_USERNAME,
    DesktopSnapshot,
    QuestionSnapshot,
    StudentDemoPresetResult,
)
from users.models import HabitPreference, User


def preset_student1_big_data_snapshot(
    *,
    course_name: str = DEMO_COURSE_NAME,
    username: str = DEMO_STUDENT_USERNAME,
    dry_run: bool = False,
) -> StudentDemoPresetResult:
    """
    将内置的 student1 大数据学习状态写入数据库。
    :param course_name: 目标课程名称。
    :param username: 目标学生账号。
    :param dry_run: 是否仅输出摘要。
    :return: 写入结果摘要。
    """
    if course_name != DEMO_COURSE_NAME:
        return StudentDemoPresetResult(applied=False, skipped_reason="非大数据课程，跳过")

    course = Course.objects.filter(name=course_name).first()
    user = User.objects.filter(username=username).first()
    if course is None or user is None:
        reason = f"缺少课程或学生: course={course_name}, username={username}"
        return StudentDemoPresetResult(applied=False, skipped_reason=reason)

    snapshot = load_inline_snapshot()

    if dry_run:
        return StudentDemoPresetResult(
            applied=False,
            skipped_reason="dry-run",
            course_id=int(course.id),
            mastery_count=len(snapshot.report_mastery)
            or KnowledgePoint.objects.filter(course=course).count(),
            question_count=len(snapshot.question_details),
            path_node_count=len(snapshot.path_nodes),
        )

    with transaction.atomic():
        mastery_count = _write_profile_and_mastery(user=user, course=course, snapshot=snapshot)
        question_count = _write_initial_assessment(user=user, course=course, snapshot=snapshot)
        path_node_count = _write_learning_path(user=user, course=course, snapshot=snapshot)
        write_snapshot_metadata(course=course, snapshot=snapshot)

    return StudentDemoPresetResult(
        applied=True,
        skipped_reason=None,
        course_id=int(course.id),
        mastery_count=mastery_count,
        question_count=question_count,
        path_node_count=path_node_count,
    )


def _write_profile_and_mastery(*, user: User, course: Course, snapshot: DesktopSnapshot) -> int:
    """写入能力、习惯、画像摘要和知识点掌握度。"""
    AbilityScore.objects.update_or_create(
        user=user,
        course=course,
        defaults={"scores": snapshot.ability_scores or default_ability_scores()},
    )
    HabitPreference.objects.update_or_create(
        user=user,
        defaults={
            "preferred_resource": "video",
            "preferred_study_time": "evening",
            "study_pace": "adaptive",
            "study_duration": "medium",
            "review_frequency": "weekly",
            "learning_style": "visual",
            "accept_challenge": True,
            "daily_goal_minutes": 45,
            "weekly_goal_days": 5,
            "preferences": {"source": "desktop_student1_demo_snapshot", "learner_tags": snapshot.learner_tags},
        },
    )
    ProfileSummary.objects.update_or_create(
        user=user,
        course=course,
        defaults={"summary": snapshot.profile_summary, "weakness": snapshot.profile_weakness, "suggestion": snapshot.profile_suggestion},
    )
    rate_map = build_snapshot_mastery_rates(course, snapshot)
    for point_id, rate in rate_map.items():
        KnowledgeMastery.objects.update_or_create(
            user=user,
            knowledge_point_id=point_id,
            defaults={"course": course, "mastery_rate": Decimal(str(rate))},
        )
    return len(rate_map)


def _bind_snapshot_course_content(*, course: Course) -> None:
    """
    补齐内置预置知识点加入后的题目与资源绑定。
    :param course: 目标课程。
    :return: None。
    """
    service = CourseContentBindingService(course_id=int(course.pk))
    plan = service.build_plan(replace_existing=True)
    service.apply_plan(plan)


def _write_initial_assessment(*, user: User, course: Course, snapshot: DesktopSnapshot) -> int:
    """写入 50 题、80 分的初始知识测评快照。"""
    assessment = Assessment.objects.filter(
        course=course,
        assessment_type="knowledge",
    ).order_by("-is_active", "id").first()
    if assessment is None:
        assessment = Assessment.objects.create(
            course=course,
            assessment_type="knowledge",
            title=f"{course.name} 知识水平测评",
            description=f"用于评估学生对{course.name}核心知识掌握情况的初始测评。",
            is_active=True,
        )
    else:
        assessment.title = f"{course.name} 知识水平测评"
        assessment.description = f"用于评估学生对{course.name}核心知识掌握情况的初始测评。"
        assessment.is_active = True
        assessment.save(update_fields=["title", "description", "is_active"])
    _bind_snapshot_course_content(course=course)
    questions = _resolve_snapshot_questions(course=course, assessment=assessment, snapshot=snapshot)
    questions = _load_snapshot_assessment_questions(assessment)
    answer_dict, details = _build_assessment_payload(questions, snapshot)
    AnswerHistory.objects.filter(user=user, course=course, source="initial").delete()
    AssessmentResult.objects.filter(
        user=user,
        course=course,
        assessment__assessment_type="knowledge",
    ).exclude(assessment=assessment).delete()
    histories = [_build_history(user=user, course=course, question=question, detail=detail) for question, detail in details]
    AnswerHistory.objects.bulk_create(histories, batch_size=200)
    result, _ = AssessmentResult.objects.update_or_create(
        user=user,
        assessment=assessment,
        defaults={
            "course": course,
            "answers": answer_dict,
            "score": Decimal(str(snapshot.score)),
            "result_data": {
                "mastery": mastery_payload_for_course(user=user, course=course),
                "question_details": [detail for _, detail in details],
                "feedback_report": _feedback_report_payload(snapshot),
                "total_score": 100,
                "correct_count": snapshot.correct_count,
                "total_count": snapshot.total_count,
            },
        },
    )
    write_feedback_report(user=user, result=result, snapshot=snapshot)
    AssessmentStatus.objects.update_or_create(
        user=user,
        course=course,
        defaults={"knowledge_done": True, "ability_done": True, "habit_done": True, "generating": False, "generation_error": None},
    )
    return len(details)


def _write_learning_path(*, user: User, course: Course, snapshot: DesktopSnapshot) -> int:
    """写入与桌面快照一致的 9 节点学习路径。"""
    LearningPath.objects.filter(user=user, course=course).delete()
    path = LearningPath.objects.create(
        user=user,
        course=course,
        ai_reason=snapshot.path_reason,
        is_dynamic=False,
    )
    nodes = [
        create_path_node(
            path=path,
            course=course,
            snapshot_node=snapshot_node,
            snapshot=snapshot,
        )
        for snapshot_node in snapshot.path_nodes
    ]
    attach_node_resources(user=user, course=course, nodes=nodes)
    return len(nodes)


def _resolve_snapshot_questions(
    *,
    course: Course,
    assessment: Assessment,
    snapshot: DesktopSnapshot,
) -> list[Question]:
    """按内置快照解析、更新或创建初始评测题并绑定到测评。"""
    existing_by_content = {
        str(question.content): question
        for question in Question.objects.filter(course=course, for_initial_assessment=True).order_by("id")
    }
    questions = [
        _upsert_snapshot_question(
            course=course,
            detail=detail,
            existing_by_content=existing_by_content,
        )
        for detail in snapshot.question_details[: snapshot.total_count]
    ]
    AssessmentQuestion.objects.filter(assessment=assessment).delete()
    AssessmentQuestion.objects.bulk_create(
        [
            AssessmentQuestion(assessment=assessment, question=question, order=index)
            for index, question in enumerate(questions)
        ]
    )
    return questions


def _load_snapshot_assessment_questions(assessment: Assessment) -> list[Question]:
    """
    重新读取已完成课程内容绑定的初始评测题目。
    :param assessment: 目标知识测评。
    :return: 按测评顺序排列的题目列表。
    """
    return list(
        assessment.questions.all()
        .prefetch_related("knowledge_points")
        .order_by("assessmentquestion__order", "id")
    )


def _upsert_snapshot_question(
    *,
    course: Course,
    detail: QuestionSnapshot,
    existing_by_content: dict[str, Question],
) -> Question:
    """按题干稳定更新或创建内置初始评测题。"""
    question = existing_by_content.get(detail.content)
    defaults = {
        "question_type": detail.question_type,
        "options": detail.options,
        "answer": _answer_payload(detail),
        "analysis": detail.analysis,
        "score": Decimal(str(detail.score)),
        "difficulty": detail.difficulty,
        "for_initial_assessment": True,
        "is_visible": True,
    }
    if question is None:
        question = Question.objects.create(
            course=course,
            content=detail.content,
            **defaults,
        )
        existing_by_content[detail.content] = question
    else:
        for field_name, value in defaults.items():
            setattr(question, field_name, value)
        question.save(update_fields=[*defaults.keys(), "updated_at"])
    point_ids = _match_points_for_question(course=course, detail=detail)
    if point_ids:
        question.knowledge_points.set(point_ids)
    return question


def _answer_payload(detail: QuestionSnapshot) -> dict[str, object]:
    """构造 Question.answer 使用的标准答案结构。"""
    if detail.question_type == "multiple_choice":
        return {"answers": list(detail.correct_answer or [])}
    return {"answer": detail.correct_answer}


def _match_point_for_question(*, course: Course, detail: QuestionSnapshot) -> KnowledgePoint | None:
    """
    为 HTML 中补齐的题目推断知识点。
    :param course: 目标课程。
    :param detail: 单题快照。
    :return: 匹配到的知识点。
    """
    text = f"{detail.content} {detail.analysis}"
    for point in KnowledgePoint.objects.filter(course=course).order_by("-level", "order", "id"):
        if point.name and point.name in text:
            return point
    return KnowledgePoint.objects.filter(course=course).order_by("order", "id").first()


def _match_points_for_question(*, course: Course, detail: QuestionSnapshot) -> list[int]:
    """
    为内置题目匹配知识点。
    :param course: 目标课程。
    :param detail: 单题快照。
    :return: 匹配到的知识点 ID。
    """
    explicit_names = detail.knowledge_point_names or []
    explicit_points = list(
        KnowledgePoint.objects.filter(course=course, name__in=explicit_names)
        .order_by("order", "id")
        .values_list("id", flat=True)
    )
    if explicit_points:
        return [int(point_id) for point_id in explicit_points]
    matched = _match_point_for_question(course=course, detail=detail)
    return [int(matched.id)] if matched else []


def _build_assessment_payload(
    questions: list[Question],
    snapshot: DesktopSnapshot,
) -> tuple[dict[str, object], list[tuple[Question, dict[str, object]]]]:
    """构建 AssessmentResult.answers 与 question_details。"""
    answer_dict: dict[str, object] = {}
    details: list[tuple[Question, dict[str, object]]] = []
    parsed_by_order = {detail.order: detail for detail in snapshot.question_details}
    for index, question in enumerate(questions, start=1):
        parsed = parsed_by_order.get(index)
        if parsed is None:
            continue
        is_correct = parsed.is_correct
        correct_answer = parsed.correct_answer
        student_answer = parsed.student_answer
        answer_dict[str(question.id)] = student_answer
        details.append((question, _question_detail(question, parsed, student_answer, correct_answer, is_correct)))
    return answer_dict, details


def _question_detail(
    question: Question,
    parsed: QuestionSnapshot | None,
    student_answer: object,
    correct_answer: object,
    is_correct: bool,
) -> dict[str, object]:
    """构造前端报告使用的单题详情。"""
    points = list(question.knowledge_points.all())
    return {
        "question_id": question.id,
        "content": parsed.content if parsed and parsed.content else question.content,
        "question_type": question.question_type,
        "student_answer": student_answer,
        "correct_answer": correct_answer,
        "student_answer_display": parsed.student_answer_display if parsed else "",
        "correct_answer_display": parsed.correct_answer_display if parsed else "",
        "is_correct": is_correct,
        "analysis": parsed.analysis if parsed and parsed.analysis else (question.analysis or ""),
        "options": _decorated_options(question, student_answer, correct_answer),
        "knowledge_points": [{"id": point.id, "name": point.name} for point in points],
    }


def _build_history(*, user: User, course: Course, question: Question, detail: dict[str, object]) -> AnswerHistory:
    """构造一条初始评测答题历史。"""
    point = question.knowledge_points.order_by("order", "id").first()
    return AnswerHistory(
        user=user,
        course=course,
        question=question,
        knowledge_point=point,
        student_answer={"answer": detail["student_answer"]},
        correct_answer={"answer": detail["correct_answer"]},
        is_correct=bool(detail["is_correct"]),
        score=2 if detail["is_correct"] else 0,
        source="initial",
    )


def _decorated_options(
    question: Question,
    student_answer: object,
    correct_answer: object,
) -> list[dict[str, object]]:
    """
    为测评报告题目选项补充正确项与学生选择标记。
    :param question: 题目对象。
    :param student_answer: 学生作答。
    :param correct_answer: 标准答案。
    :return: 前端可展示的选项列表。
    """
    from common.domain.utils import decorate_question_options

    return decorate_question_options(
        question.options or [],
        question.question_type,
        student_answer=student_answer,
        correct_answer=correct_answer,
    )


def _feedback_report_payload(snapshot: DesktopSnapshot) -> dict[str, object]:
    """构造 AssessmentResult.result_data 中的反馈报告快照。"""
    return {
        "summary": snapshot.feedback_report.summary,
        "analysis": snapshot.feedback_report.summary,
        "knowledge_gaps": snapshot.feedback_report.knowledge_gaps,
        "recommendations": snapshot.feedback_report.recommendations,
        "next_tasks": snapshot.feedback_report.next_tasks,
        "encouragement": snapshot.feedback_report.encouragement,
        "conclusion": snapshot.feedback_report.conclusion,
    }
