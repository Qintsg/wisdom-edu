from __future__ import annotations

from assessments.models import AbilityScore, AnswerHistory, AssessmentResult, AssessmentStatus
from courses.models import Class, ClassCourse, Course, Enrollment
from exams.models import ExamSubmission, FeedbackReport
from knowledge.models import KnowledgeMastery, ProfileSummary
from learning.models import LearningPath
from users.models import HabitPreference, User, UserCourseContext

from common.defense_demo_config import (
    DEFENSE_DEMO_CLASS_NAME,
    DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS,
    DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME,
    DEFENSE_DEMO_TEACHER_USERNAME,
    DEFENSE_DEMO_WARMUP_STUDENT_USERNAME,
)

# 维护意图：创建或更新演示账号。
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _ensure_user(
    *,
    username: str,
    password: str,
    email: str,
    role: str,
    real_name: str,
    student_id: str = "",
) -> User:
    """
    创建或更新演示账号。
    :param username: 用户名。
    :param password: 明文密码。
    :param email: 邮箱。
    :param role: 角色。
    :param real_name: 真实姓名。
    :param student_id: 学号。
    :return: 用户对象。
    """
    user, _ = User.objects.update_or_create(
        username=username,
        defaults={
            "email": email,
            "role": role,
            "real_name": real_name,
            "student_id": student_id or None,
            "is_staff": role in ("teacher", "admin"),
        },
    )
    user.set_password(password)
    user.save(update_fields=["email", "role", "real_name", "student_id", "password", "is_staff"])
    return user


# 维护意图：创建或更新支撑课程。
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _ensure_course(course_name: str, teacher: User) -> Course:
    """
    创建或更新支撑课程。
    :param course_name: 课程名称。
    :param teacher: 教师对象。
    :return: 课程对象。
    """
    course, _ = Course.objects.update_or_create(
        name=course_name,
        defaults={
            "description": "系统讲授关系数据库理论、SQL 语言与事务管理，培养学生数据建模与查询优化的实践能力。",
            "created_by": teacher,
            "is_public": True,
            "initial_assessment_count": 6,
        },
    )
    return course


# 维护意图：仅创建演示专用账号，供数据重建前置使用。
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def ensure_defense_demo_accounts() -> dict[str, int]:
    """
    仅创建演示专用账号，供数据重建前置使用。
    :return: 账号 ID 摘要。
    """
    teacher = _ensure_user(
        username=DEFENSE_DEMO_TEACHER_USERNAME,
        password="Test123456",
        email="wangjg@edu.cn",
        role="teacher",
        real_name="王建国",
    )
    warmup_student = _ensure_user(
        username=DEFENSE_DEMO_WARMUP_STUDENT_USERNAME,
        password="Test123456",
        email="limh2024@stu.edu.cn",
        role="student",
        real_name="李明辉",
        student_id="2024210101",
    )
    primary_student = _ensure_user(
        username=DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME,
        password="Test123456",
        email="zhangsy2024@stu.edu.cn",
        role="student",
        real_name="张思远",
        student_id="2024210135",
    )
    for student_spec in DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS:
        _ensure_user(
            username=student_spec["username"],
            password="Test123456",
            email=student_spec["email"],
            role="student",
            real_name=student_spec["real_name"],
            student_id=student_spec["student_id"],
        )
    return {
        "teacher_id": teacher.id,
        "warmup_student_id": warmup_student.id,
        "primary_student_id": primary_student.id,
    }


# 维护意图：创建或更新演示班级。
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _ensure_class(teacher: User, primary_course: Course, support_course: Course) -> Class:
    """
    创建或更新演示班级。
    :param teacher: 教师对象。
    :param primary_course: 主课程。
    :param support_course: 支撑课程。
    :return: 班级对象。
    """
    class_obj, _ = Class.objects.update_or_create(
        name=DEFENSE_DEMO_CLASS_NAME,
        defaults={
            "description": "2025-2026 学年第一学期大数据技术基础课程教学班。",
            "teacher": teacher,
            "semester": "2025-2026-1",
            "course": primary_course,
            "is_active": True,
        },
    )

    for course in (primary_course, support_course):
        class_course, _ = ClassCourse.objects.get_or_create(
            class_obj=class_obj,
            course=course,
            defaults={"published_by": teacher, "is_active": True},
        )
        if not class_course.is_active:
            class_course.is_active = True
            class_course.published_by = teacher
            class_course.save(update_fields=["is_active", "published_by"])
    return class_obj


# 维护意图：清空仅入班演示账号在主演示课程中的学习轨迹。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _reset_course_only_student_state(primary_course: Course, student: User) -> None:
    """
    清空仅入班演示账号在主演示课程中的学习轨迹。
    :param primary_course: 主演示课程。
    :param student: 仅入班学生账号。
    :return: None。
    """
    # DEFENSE_DEMO_PRESET: student2~5 需要保持“只加入班级、未产生学习轨迹”的状态，
    # 以便答辩时稳定演示首次进入测评中心的真实入口。
    FeedbackReport.objects.filter(user=student, assessment_result__course=primary_course).delete()
    FeedbackReport.objects.filter(user=student, exam__course=primary_course).delete()
    ExamSubmission.objects.filter(user=student, exam__course=primary_course).delete()
    LearningPath.objects.filter(user=student, course=primary_course).delete()
    AssessmentResult.objects.filter(user=student, course=primary_course).delete()
    AnswerHistory.objects.filter(user=student, course=primary_course).delete()
    AssessmentStatus.objects.filter(user=student, course=primary_course).delete()
    AbilityScore.objects.filter(user=student, course=primary_course).delete()
    KnowledgeMastery.objects.filter(user=student, course=primary_course).delete()
    ProfileSummary.objects.filter(user=student, course=primary_course).delete()
    HabitPreference.objects.filter(user=student).delete()


# 维护意图：确保 student2~5 已加入答辩班级且无主演示课程轨迹。
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _ensure_course_only_demo_students(primary_course: Course, defense_class: Class) -> list[User]:
    """
    确保 student2~5 已加入答辩班级且无主演示课程轨迹。
    :param primary_course: 主演示课程。
    :param defense_class: 演示班级。
    :return: 已处理的仅入班学生列表。
    """
    course_only_students: list[User] = []
    for student_spec in DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS:
        student = User.objects.get(username=student_spec["username"])
        Enrollment.objects.update_or_create(
            user=student,
            class_obj=defense_class,
            defaults={"role": "student"},
        )
        UserCourseContext.objects.update_or_create(
            user=student,
            defaults={"current_course": primary_course, "current_class": defense_class},
        )
        _reset_course_only_student_state(primary_course, student)
        course_only_students.append(student)
    return course_only_students
