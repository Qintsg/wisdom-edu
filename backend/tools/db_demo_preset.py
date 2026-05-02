"""student1 演示课程状态预置工具。"""

from typing import TYPE_CHECKING, Any, Optional, cast

from tools.db_demo_preset_support import (
    apply_student1_static_state,
    build_mastery_payload,
    build_student1_answer_value,
    build_student1_demo_defaults,
    build_student1_feedback_defaults,
    rebuild_student1_path,
)
from tools.common import User
from tools.testing import _status_flag

if TYPE_CHECKING:
    from users.models import User as UserModel
DEFAULT_BOOTSTRAP_COURSE_NAME = "大数据技术与应用"
INITIAL_MASTERY_PRIOR_MEAN = 0.25
INITIAL_MASTERY_PRIOR_STRENGTH = 4.0


def _calculate_initial_mastery_baseline(correct_count: int, total_count: int) -> float:
    """使用与初始评测接口一致的保守基线计算掌握度。"""
    if total_count <= 0:
        return round(INITIAL_MASTERY_PRIOR_MEAN, 4)

    mastery_rate = (
        correct_count + INITIAL_MASTERY_PRIOR_MEAN * INITIAL_MASTERY_PRIOR_STRENGTH
    ) / (total_count + INITIAL_MASTERY_PRIOR_STRENGTH)
    return round(max(0.0, min(0.85, mastery_rate)), 4)


def _reset_course_demo_state(student: "UserModel", course: Any) -> None:
    """清理指定学生在课程下的预置轨迹，便于幂等重建。"""
    from assessments.models import AbilityScore, AssessmentResult, AssessmentStatus, AnswerHistory
    from exams.models import ExamSubmission, FeedbackReport
    from knowledge.models import KnowledgeMastery, ProfileSummary
    from learning.models import LearningPath

    FeedbackReport.objects.filter(user=student, assessment_result__course=course).delete()
    FeedbackReport.objects.filter(user=student, exam__course=course).delete()
    ExamSubmission.objects.filter(user=student, exam__course=course).delete()
    LearningPath.objects.filter(user=student, course=course).delete()
    AssessmentResult.objects.filter(user=student, course=course).delete()
    AnswerHistory.objects.filter(user=student, course=course).delete()
    AssessmentStatus.objects.filter(user=student, course=course).delete()
    AbilityScore.objects.filter(user=student, course=course).delete()
    KnowledgeMastery.objects.filter(user=student, course=course).delete()
    ProfileSummary.objects.filter(user=student, course=course).delete()


def _preset_student1_demo_data(
    student: Optional["UserModel"],
    course: "Any",
) -> None:
    """为 student1 预置更贴近真实的“刚完成初始评测”状态。"""
    if not student or not course:
        return

    from collections import defaultdict
    from decimal import Decimal

    from assessments.models import Assessment, AssessmentQuestion, AssessmentResult, AnswerHistory, Question
    from exams.models import FeedbackReport
    from knowledge.models import KnowledgeMastery, KnowledgePoint, ProfileSummary, Resource
    from learning.path_rules import apply_prerequisite_caps
    from common.utils import check_answer, extract_answer_value, serialize_answer_payload
    defaults = build_student1_demo_defaults()

    points = list(KnowledgePoint.objects.filter(course=course).order_by("order", "id"))
    questions = list(
        Question.objects.filter(course=course)
        .prefetch_related("knowledge_points")
        .order_by("id")
    )
    resources = list(Resource.objects.filter(course=course).order_by("sort_order", "id"))
    selected_questions = [question for question in questions if question.for_initial_assessment]
    selected_questions = selected_questions or questions
    if not points or not selected_questions:
        print(f"  {_status_flag(False)} student1 预置跳过: 课程缺少知识点或题目")
        return
    course.initial_assessment_count = len(selected_questions)
    course.save(update_fields=["initial_assessment_count", "updated_at"])

    _reset_course_demo_state(student, course)
    apply_student1_static_state(student, course, defaults)

    assessment, _ = Assessment.objects.update_or_create(
        course=course,
        assessment_type="knowledge",
        defaults={
            "title": f"{course.name} 初始评测",
            "description": "系统自动生成的初始知识评测",
            "is_active": True,
        },
    )
    AssessmentQuestion.objects.filter(assessment=assessment).exclude(
        question__in=selected_questions
    ).delete()
    for order, question in enumerate(selected_questions, start=1):
        AssessmentQuestion.objects.update_or_create(
            assessment=assessment,
            question=question,
            defaults={"order": order},
        )

    planned_correct = [index % 5 != 1 for index in range(len(selected_questions))]
    total_score = Decimal("0")
    correct_count = 0
    raw_answers: dict[str, object] = {}
    question_details: list[dict[str, object]] = []
    point_stats: dict[int, dict[str, int | str]] = defaultdict(
        lambda: {"correct": 0, "total": 0, "name": ""}
    )

    for idx, question in enumerate(selected_questions):
        intended_correct = planned_correct[idx] if idx < len(planned_correct) else True
        student_answer = _build_student_answer_value(question, intended_correct)
        correct_answer = extract_answer_value(question.answer)
        history_answer = serialize_answer_payload(question.question_type, student_answer)
        history_correct = serialize_answer_payload(question.question_type, correct_answer)
        is_correct = check_answer(question.question_type, student_answer, question.answer)

        earned = question.score if is_correct else Decimal("0")
        total_score += earned
        if is_correct:
            correct_count += 1

        linked_points = list(question.knowledge_points.all())
        primary_point = linked_points[0] if linked_points else None
        raw_answers[str(question.id)] = student_answer
        question_details.append(
            {
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
            }
        )
        for point in linked_points:
            point_stats[point.id]["total"] += 1
            point_stats[point.id]["name"] = point.name
            if is_correct:
                point_stats[point.id]["correct"] += 1

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

    max_possible = sum((question.score for question in selected_questions), Decimal("0"))
    mastery_map = {point.id: float(INITIAL_MASTERY_PRIOR_MEAN) for point in points}
    for point_id, stats in point_stats.items():
        mastery_map[point_id] = _calculate_initial_mastery_baseline(
            int(stats["correct"]),
            int(stats["total"]),
        )
    mastery_map = apply_prerequisite_caps(mastery_map, int(course.pk))
    mastery_payload = build_mastery_payload(points, mastery_map, INITIAL_MASTERY_PRIOR_MEAN)

    assessment_result, _ = AssessmentResult.objects.update_or_create(
        user=student,
        assessment=assessment,
        defaults={
            "course": course,
            "answers": raw_answers,
            "score": total_score,
            "result_data": {
                "mastery": mastery_payload,
                "question_details": question_details,
                "total_score": float(max_possible),
                "correct_count": correct_count,
                "total_count": len(selected_questions),
            },
        },
    )

    for point in points:
        KnowledgeMastery.objects.update_or_create(
            user=student,
            course=course,
            knowledge_point=point,
            defaults={
                "mastery_rate": Decimal(
                    str(round(float(mastery_map.get(point.id, INITIAL_MASTERY_PRIOR_MEAN)), 4))
                ),
            },
        )

    weakest_points = [
        point["point_name"]
        for point in mastery_payload
        if float(point["mastery_rate"]) <= 0.3
    ][:3]
    weakest_text = "、".join(weakest_points) if weakest_points else "暂无明显薄弱点"

    ProfileSummary.objects.update_or_create(
        user=student,
        course=course,
        defaults={
            "summary": defaults.profile_defaults["summary"],
            "weakness": weakest_text,
            "suggestion": defaults.profile_defaults["suggestion"],
        },
    )

    FeedbackReport.objects.update_or_create(
        user=student,
        source="assessment",
        assessment_result=assessment_result,
        defaults=build_student1_feedback_defaults(
            total_questions=len(selected_questions),
            weakest_points=weakest_points,
            total_score=total_score,
            max_possible=max_possible,
            correct_count=correct_count,
        ),
    )

    node_count = rebuild_student1_path(
        student=student,
        course=course,
        points=points,
        resources=resources,
        mastery_map=mastery_map,
        prior_mean=INITIAL_MASTERY_PRIOR_MEAN,
        defaults=defaults,
    )

    print(
        f"  {_status_flag(True)} student1 演示数据预置完成: "
        f"初始评测={total_score}/{max_possible}, 路径节点={node_count}, 基线知识点={max(len(points) - len(point_stats), 0)}"
    )


def preset_student1_demo_course_state(
    course_name: str = DEFAULT_BOOTSTRAP_COURSE_NAME,
) -> bool:
    """按课程名重建 student1 的演示预置，供 pg_bootstrap 复用。"""
    from courses.models import Course

    normalized_course_name = course_name.strip() or DEFAULT_BOOTSTRAP_COURSE_NAME
    course = Course.objects.filter(name=normalized_course_name).first()
    student = User.objects.filter(username="student1").first()
    if not course or not student:
        print(
            f"  {_status_flag(False)} student1 预置跳过: 缺少课程[{normalized_course_name}]或账号 student1"
        )
        return False

    _preset_student1_demo_data(cast("UserModel", student), course)
    return True
