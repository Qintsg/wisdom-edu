#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
student1 大数据桌面快照预置脚本。
@Project : wisdom-edu
@File : demo_student1_snapshot.py
@Author : Qintsg
@Date : 2026-05-13 13:20
'''

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

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
from tools.demo_student1_snapshot_parse import load_desktop_snapshot
from tools.demo_student1_snapshot_support import (
    answer_display,
    attach_node_resources,
    build_snapshot_mastery_rates,
    create_path_node,
    default_ability_scores,
    default_path_titles,
    find_title_index,
    mastery_payload_for_course,
    question_correct_answer,
    write_feedback_report,
    write_snapshot_metadata,
    wrong_answer_for,
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
    desktop_root: str | Path | None = None,
    dry_run: bool = False,
    fail_on_missing: bool = False,
) -> StudentDemoPresetResult:
    """
    将桌面导出的 student1 大数据页面快照写入演示库。
    :param course_name: 目标课程名称。
    :param username: 目标学生账号。
    :param desktop_root: 桌面目录，默认使用当前用户 Desktop。
    :param dry_run: 是否仅解析并输出摘要。
    :param fail_on_missing: 缺少桌面快照时是否抛出异常。
    :return: 写入结果摘要。
    """
    if course_name != DEMO_COURSE_NAME:
        return StudentDemoPresetResult(applied=False, skipped_reason="非大数据演示课程，跳过")

    course = Course.objects.filter(name=course_name).first()
    user = User.objects.filter(username=username).first()
    if course is None or user is None:
        reason = f"缺少课程或学生: course={course_name}, username={username}"
        if fail_on_missing:
            raise ValueError(reason)
        return StudentDemoPresetResult(applied=False, skipped_reason=reason)

    try:
        snapshot = load_desktop_snapshot(desktop_root)
    except FileNotFoundError as exc:
        if fail_on_missing:
            raise
        return StudentDemoPresetResult(applied=False, skipped_reason=str(exc))

    if dry_run:
        return StudentDemoPresetResult(
            applied=False,
            skipped_reason="dry-run",
            course_id=int(course.id),
            mastery_count=len(snapshot.report_mastery)
            or KnowledgePoint.objects.filter(course=course).count(),
            question_count=len(snapshot.question_details),
            path_node_count=len(snapshot.path_titles or default_path_titles()),
            asset_count=len(snapshot.assets),
        )

    with transaction.atomic():
        mastery_count = _write_profile_and_mastery(user=user, course=course, snapshot=snapshot)
        _bind_snapshot_course_content(course=course)
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
        asset_count=len(snapshot.assets),
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
    补齐桌面快照知识点加入后的题目与资源绑定。
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
            description="基于桌面快照预置的 student1 初始评测。",
            is_active=True,
        )
    else:
        assessment.title = f"{course.name} 知识水平测评"
        assessment.description = "基于桌面快照预置的 student1 初始评测。"
        assessment.is_active = True
        assessment.save(update_fields=["title", "description", "is_active"])
    questions = _resolve_snapshot_questions(course=course, assessment=assessment, snapshot=snapshot)
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
    """写入完成到 Spark SQL 原理与特征基础的学习路径。"""
    LearningPath.objects.filter(user=user, course=course).delete()
    path = LearningPath.objects.create(
        user=user,
        course=course,
        ai_reason="根据桌面快照预置：已完成基础复盘并推进到 Spark SQL 原理与特征基础。",
        is_dynamic=False,
    )
    titles = snapshot.path_titles or default_path_titles()
    completed_until = find_title_index(titles, "Spark SQL原理与特征基础")
    nodes = [
        create_path_node(
            path=path,
            course=course,
            title=title,
            index=index,
            completed_until=completed_until,
            snapshot=snapshot,
        )
        for index, title in enumerate(titles)
    ]
    attach_node_resources(user=user, course=course, nodes=nodes)
    return len(nodes)


def _resolve_snapshot_questions(
    *,
    course: Course,
    assessment: Assessment,
    snapshot: DesktopSnapshot,
) -> list[Question]:
    """解析或创建初始评测题并绑定到测评。"""
    parsed_details = snapshot.question_details[: snapshot.total_count]
    existing = list(
        Question.objects.filter(course=course, for_initial_assessment=True)
        .prefetch_related("knowledge_points")
        .order_by("id")[: snapshot.total_count]
    )
    if len(existing) < snapshot.total_count:
        existing.extend(_create_missing_questions(course=course, details=parsed_details[len(existing) :]))
    AssessmentQuestion.objects.filter(assessment=assessment).delete()
    AssessmentQuestion.objects.bulk_create(
        [
            AssessmentQuestion(assessment=assessment, question=question, order=index)
            for index, question in enumerate(existing)
        ]
    )
    return existing


def _create_missing_questions(*, course: Course, details: list[QuestionSnapshot]) -> list[Question]:
    """当课程题库不足 50 题时按 HTML 快照补齐题目。"""
    created: list[Question] = []
    for detail in details:
        fallback_point = _match_point_for_question(course=course, detail=detail)
        question = Question.objects.create(
            course=course,
            content=detail.content or f"初始评测快照题目 {detail.order}",
            question_type="true_false",
            answer={"answer": bool(detail.correct_answer)},
            analysis=detail.analysis,
            score=2,
            for_initial_assessment=True,
            is_visible=True,
        )
        if fallback_point:
            question.knowledge_points.add(fallback_point)
        created.append(question)
    return created


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
        is_correct = parsed.is_correct if parsed else index <= snapshot.correct_count
        correct_answer = question_correct_answer(question, parsed)
        student_answer = correct_answer if is_correct else wrong_answer_for(correct_answer)
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
        "student_answer_display": answer_display(student_answer),
        "correct_answer_display": answer_display(correct_answer),
        "is_correct": is_correct,
        "analysis": parsed.analysis if parsed and parsed.analysis else (question.analysis or ""),
        "options": question.options or [],
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
