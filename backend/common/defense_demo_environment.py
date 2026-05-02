from __future__ import annotations

from courses.models import Course, Enrollment
from users.models import User, UserCourseContext

from common.defense_demo_accounts import (
    _ensure_class,
    _ensure_course,
    _ensure_course_only_demo_students,
    ensure_defense_demo_accounts,
)
from common.defense_demo_assessment_state import (
    _ensure_demo_assessment_state,
    _seed_demo_practice_histories,
)
from common.defense_demo_config import (
    DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME,
    DEFENSE_DEMO_SUPPORT_COURSE_NAME,
    DEFENSE_DEMO_TEACHER_USERNAME,
    DEFENSE_DEMO_WARMUP_STUDENT_USERNAME,
)
from common.defense_demo_content import (
    _build_ai_demo_query_payloads,
    _build_point_intro_payloads,
    _ensure_demo_points,
    _ensure_demo_resources,
    _ensure_demo_stage_test,
)
from common.defense_demo_path import _ensure_demo_learning_path
from common.defense_demo_progress import _capture_mastery_snapshot
from common.defense_demo_stage import (
    _build_demo_stage_test_result,
    _ensure_warmup_stage_submission_and_feedback,
)

def ensure_defense_demo_environment(primary_course_name: str) -> dict[str, int]:
    """
    创建演示账号、班级与固定学习链路。
    :param primary_course_name: 主课程名称。
    :return: 关键对象 ID 摘要。
    """

    ensure_defense_demo_accounts()
    teacher = User.objects.get(username=DEFENSE_DEMO_TEACHER_USERNAME)
    warmup_student = User.objects.get(username=DEFENSE_DEMO_WARMUP_STUDENT_USERNAME)
    primary_student = User.objects.get(username=DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME)

    primary_course = Course.objects.get(name=primary_course_name)
    support_course = _ensure_course(DEFENSE_DEMO_SUPPORT_COURSE_NAME, teacher)
    defense_class = _ensure_class(teacher, primary_course, support_course)

    for student in (warmup_student, primary_student):
        Enrollment.objects.update_or_create(
            user=student,
            class_obj=defense_class,
            defaults={"role": "student"},
        )
        UserCourseContext.objects.update_or_create(
            user=student,
            defaults={"current_course": primary_course, "current_class": defense_class},
        )

    _ensure_course_only_demo_students(primary_course, defense_class)

    points = _ensure_demo_points(primary_course)
    resources = _ensure_demo_resources(primary_course, teacher, points)
    stage_exam = _ensure_demo_stage_test(primary_course, teacher, points)
    _ensure_demo_assessment_state(primary_course, warmup_student, teacher, points)
    _ensure_demo_assessment_state(primary_course, primary_student, teacher, points)
    warmup_mastery_before = _capture_mastery_snapshot(
        primary_course,
        warmup_student,
        points,
    )
    _seed_demo_practice_histories(primary_course, warmup_student, primary_student, stage_exam)
    warmup_stage_context = _ensure_warmup_stage_submission_and_feedback(
        primary_course,
        warmup_student,
        stage_exam,
        points,
    )
    _ensure_demo_learning_path(primary_course, primary_student, points, resources, stage_exam)
    _ensure_demo_learning_path(
        primary_course,
        warmup_student,
        points,
        resources,
        stage_exam,
        completed_stage_result=_build_demo_stage_test_result(
            stage_exam,
            points,
            warmup_mastery_before,
            warmup_stage_context["submitted_at"],
        ),
    )

    primary_config = dict(primary_course.config or {})
    primary_config["defense_demo"] = {
        "mode": "primary",
        "class_name": defense_class.name,
        "visible_before_test_order": 4,
        "point_intro_presets": _build_point_intro_payloads(points),
        "assistant_demo_queries": _build_ai_demo_query_payloads(points),
    }
    primary_course.config = primary_config
    primary_course.created_by = teacher
    primary_course.is_public = True
    primary_course.save(update_fields=["config", "created_by", "is_public", "updated_at"])

    support_config = dict(support_course.config or {})
    support_config["defense_demo"] = {
        "mode": "support",
        "class_name": defense_class.name,
    }
    support_course.config = support_config
    support_course.save(update_fields=["config", "updated_at"])

    return {
        "teacher_id": teacher.id,
        "warmup_student_id": warmup_student.id,
        "primary_student_id": primary_student.id,
        "class_id": defense_class.id,
        "primary_course_id": primary_course.id,
        "support_course_id": support_course.id,
        "stage_exam_id": stage_exam.id,
    }
