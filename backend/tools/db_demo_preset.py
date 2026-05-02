"""student1 演示课程状态预置工具。"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, cast

from tools.common import User
from tools.db_demo_preset_assessment import (
    build_student1_assessment_attempt,
    persist_student1_assessment_result,
    persist_student1_mastery,
    Student1AssessmentAttempt,
    weakest_point_names,
)
from tools.db_demo_preset_support import (
    apply_student1_static_state,
    build_student1_demo_defaults,
    build_student1_feedback_defaults,
    load_student1_demo_course_data,
    rebuild_student1_path,
    reset_course_demo_state,
    Student1DemoDefaults,
    sync_student1_initial_assessment,
)
from tools.testing import _status_flag

if TYPE_CHECKING:
    from assessments.models import AssessmentResult
    from courses.models import Course
    from users.models import User as UserModel


DEFAULT_BOOTSTRAP_COURSE_NAME = "大数据技术与应用"
INITIAL_MASTERY_PRIOR_MEAN = 0.25
INITIAL_MASTERY_PRIOR_STRENGTH = 4.0


def preset_student1_demo_data(
    student: "UserModel | None",
    course: "Course | None",
) -> None:
    """为 student1 预置更贴近真实的“刚完成初始评测”状态。"""
    if not student or not course:
        return

    defaults = build_student1_demo_defaults()
    course_data = load_student1_demo_course_data(course)
    if not course_data.points or not course_data.selected_questions:
        print(f"  {_status_flag(False)} student1 预置跳过: 课程缺少知识点或题目")
        return

    course.initial_assessment_count = len(course_data.selected_questions)
    course.save(update_fields=["initial_assessment_count", "updated_at"])
    reset_course_demo_state(student, course)
    apply_student1_static_state(student, course, defaults)

    assessment = sync_student1_initial_assessment(course, course_data.selected_questions)
    attempt = build_student1_assessment_attempt(
        student=student,
        course=course,
        points=course_data.points,
        selected_questions=course_data.selected_questions,
        prior_mean=INITIAL_MASTERY_PRIOR_MEAN,
        prior_strength=INITIAL_MASTERY_PRIOR_STRENGTH,
    )
    assessment_result = persist_student1_assessment_result(
        student=student,
        course=course,
        assessment=assessment,
        attempt=attempt,
    )
    persist_student1_mastery(
        student=student,
        course=course,
        points=course_data.points,
        mastery_map=attempt.mastery_map,
        prior_mean=INITIAL_MASTERY_PRIOR_MEAN,
    )

    weakest_points = weakest_point_names(attempt.mastery_payload)
    persist_student1_profile_and_feedback(
        student=student,
        course=course,
        defaults=defaults,
        assessment_result=assessment_result,
        weakest_points=weakest_points,
        attempt=attempt,
    )
    node_count = rebuild_student1_path(
        student=student,
        course=course,
        points=course_data.points,
        resources=course_data.resources,
        mastery_map=attempt.mastery_map,
        prior_mean=INITIAL_MASTERY_PRIOR_MEAN,
        defaults=defaults,
    )
    print_student1_preset_result(
        total_score=attempt.total_score,
        max_possible=attempt.max_possible,
        node_count=node_count,
        baseline_count=max(len(course_data.points) - len(attempt.point_stats), 0),
    )


def persist_student1_profile_and_feedback(
    *,
    student: "UserModel",
    course: "Course",
    defaults: Student1DemoDefaults,
    assessment_result: "AssessmentResult",
    weakest_points: list[str],
    attempt: Student1AssessmentAttempt,
) -> None:
    """写入 student1 演示画像摘要和反馈报告。"""
    from exams.models import FeedbackReport
    from knowledge.models import ProfileSummary

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
            total_questions=len(attempt.raw_answers),
            weakest_points=weakest_points,
            total_score=attempt.total_score,
            max_possible=attempt.max_possible,
            correct_count=attempt.correct_count,
        ),
    )


def print_student1_preset_result(
    *,
    total_score: Decimal,
    max_possible: Decimal,
    node_count: int,
    baseline_count: int,
) -> None:
    """输出 student1 演示预置结果。"""
    print(
        f"  {_status_flag(True)} student1 演示数据预置完成: "
        f"初始评测={total_score}/{max_possible}, 路径节点={node_count}, 基线知识点={baseline_count}"
    )


def _preset_student1_demo_data(
    student: "UserModel | None",
    course: "Course | None",
) -> None:
    """兼容旧导入路径的 student1 预置入口。"""
    preset_student1_demo_data(student, course)


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

    preset_student1_demo_data(cast("UserModel", student), course)
    return True
