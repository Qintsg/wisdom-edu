"""测试数据种子构建辅助工具。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from assessments.models import Question, SurveyQuestion
from common.neo4j_service import neo4j_service
from courses.models import Class, ClassCourse, Course, Enrollment
from knowledge.models import KnowledgePoint, KnowledgeRelation, Resource
from tools.common import User
from tools.db_demo_preset import _preset_student1_demo_data
from tools.rag_index import refresh_rag_corpus
from tools.testing import _status_flag
from users.models import ActivationCode, ClassInvitation, UserCourseContext


@dataclass
class SeededTestDataState:
    """记录一次测试数据灌库后的关键对象集合。"""

    admin_user: User
    teachers: list[User]
    students: list[User]
    courses: list[Course]
    classes: list[Class]
    big_data_course: Course | None
    big_data_class: Class | None


def _seed_course_content(
    target_course: Course,
    course_teacher: User,
    seed: dict[str, Any],
) -> None:
    """为课程创建最小可运行的知识图谱、资源与题目数据。"""
    point_map: dict[str, KnowledgePoint] = {}
    for index, point_cfg in enumerate(seed.get("knowledge_points", []), start=1):
        point, _ = KnowledgePoint.objects.update_or_create(
            course=target_course,
            name=point_cfg["name"],
            defaults={
                "description": point_cfg.get("description", ""),
                "chapter": point_cfg.get("chapter", f"第{index}章"),
                "order": point_cfg.get("order", index),
                "is_published": True,
            },
        )
        point_map[point_cfg["key"]] = point

    for relation_cfg in seed.get("relations", []):
        pre_point = point_map.get(relation_cfg.get("pre"))
        post_point = point_map.get(relation_cfg.get("post"))
        if not pre_point or not post_point:
            continue
        KnowledgeRelation.objects.get_or_create(
            course=target_course,
            pre_point=pre_point,
            post_point=post_point,
            defaults={"relation_type": relation_cfg.get("type", "prerequisite")},
        )

    for index, resource_cfg in enumerate(seed.get("resources", []), start=1):
        resource, _ = Resource.objects.update_or_create(
            course=target_course,
            title=resource_cfg["title"],
            resource_type=resource_cfg.get("type", "document"),
            defaults={
                "url": resource_cfg.get("url")
                or f"https://example.com/{int(target_course.pk)}/{index}",
                "description": resource_cfg.get("description", ""),
                "chapter_number": resource_cfg.get("chapter_number", str(index)),
                "sort_order": index,
                "is_visible": True,
                "uploaded_by": course_teacher,
            },
        )
        point_keys = resource_cfg.get("point_keys", [])
        linked_points = [point_map[key] for key in point_keys if key in point_map]
        if linked_points:
            cast(Any, resource.knowledge_points).set(linked_points)

    for index, question_cfg in enumerate(seed.get("questions", []), start=1):
        question, _ = Question.objects.update_or_create(
            course=target_course,
            content=question_cfg["content"],
            defaults={
                "chapter": question_cfg.get("chapter", f"第{index}章"),
                "question_type": question_cfg.get("question_type", "single_choice"),
                "options": question_cfg.get("options", []),
                "answer": question_cfg.get("answer", {"answer": "A"}),
                "analysis": question_cfg.get("analysis", ""),
                "difficulty": question_cfg.get("difficulty", "medium"),
                "score": question_cfg.get("score", 5),
                "is_visible": True,
                "created_by": course_teacher,
            },
        )
        point_keys = question_cfg.get("point_keys", [])
        linked_points = [point_map[key] for key in point_keys if key in point_map]
        if linked_points:
            cast(Any, question.knowledge_points).set(linked_points)


def _create_user(username: str, password: str, **kwargs: object) -> User:
    """创建或更新用户，并设置密码。"""
    user, _ = User.objects.update_or_create(username=username, defaults=kwargs)
    user.set_password(password)
    user.save()
    return cast(User, user)


def _seed_user_accounts(data: dict[str, Any]) -> tuple[User, list[User], list[User]]:
    """写入管理员、教师和学生账号。"""
    admin_cfg = data["users"]["admin"]
    admin_user = _create_user(
        username=admin_cfg["username"],
        password=admin_cfg["password"],
        email=admin_cfg["email"],
        role=admin_cfg["role"],
        is_superuser=True,
        is_staff=True,
    )
    print(f"  {_status_flag(True)} 管理员: {getattr(admin_user, 'username', '')}")

    teachers: list[User] = []
    for cfg in data["users"].get("teachers", []):
        teacher = _create_user(
            username=cfg["username"],
            password=cfg["password"],
            email=cfg["email"],
            role=cfg["role"],
            real_name=cfg.get("real_name", ""),
        )
        teachers.append(teacher)
        print(f"  {_status_flag(True)} 教师: {getattr(teacher, 'username', '')}")

    students: list[User] = []
    for cfg in data["users"].get("students", []):
        student = _create_user(
            username=cfg["username"],
            password=cfg["password"],
            email=cfg["email"],
            role=cfg["role"],
            real_name=cfg.get("real_name", ""),
            student_id=cfg.get("student_id", ""),
        )
        students.append(student)
        print(f"  {_status_flag(True)} 学生: {getattr(student, 'username', '')}")
    return admin_user, teachers, students


def _seed_activation_codes(data: dict[str, Any], admin_user: User) -> None:
    """写入激活码种子数据。"""
    for activation_code in data.get("activation_codes", []):
        ActivationCode.objects.update_or_create(
            code=activation_code["code"],
            defaults={
                "code_type": activation_code["code_type"],
                "created_by": admin_user,
                "remark": activation_code.get("remark", ""),
            },
        )


def _seed_courses(
    data: dict[str, Any],
    teachers: list[User],
    admin_user: User,
) -> list[Course]:
    """写入课程和最小课程内容。"""
    courses: list[Course] = []
    for course_cfg in data.get("courses", []):
        teacher_index = course_cfg.get("teacher_index", 0)
        teacher = teachers[teacher_index] if teachers else admin_user
        course, _ = Course.objects.update_or_create(
            name=course_cfg["name"],
            defaults={
                "description": course_cfg.get("description", ""),
                "created_by": teacher,
                "is_public": course_cfg.get("is_public", True),
                "initial_assessment_count": course_cfg.get("initial_assessment_count", 10),
            },
        )
        courses.append(course)

        seed_cfg = (data.get("course_seed_content") or {}).get(course_cfg["name"])
        if seed_cfg:
            _seed_course_content(course, teacher, seed_cfg)
    return courses


def _seed_classes(
    data: dict[str, Any],
    teachers: list[User],
    admin_user: User,
    courses: list[Course],
) -> list[Class]:
    """写入班级和班级课程关联。"""
    classes: list[Class] = []
    for class_cfg in data.get("classes", []):
        teacher_index = class_cfg.get("teacher_index", 0)
        teacher = teachers[teacher_index] if teachers else admin_user
        class_obj, _ = Class.objects.update_or_create(
            name=class_cfg["name"],
            defaults={
                "description": class_cfg.get("description", ""),
                "teacher": teacher,
                "semester": class_cfg.get("semester", ""),
            },
        )
        classes.append(class_obj)
        for course_index in class_cfg.get("course_indices", []):
            if 0 <= course_index < len(courses):
                ClassCourse.objects.get_or_create(
                    class_obj=class_obj,
                    course=courses[course_index],
                    defaults={"published_by": teacher},
                )
    return classes


def _resolve_big_data_context(
    courses: list[Course],
    classes: list[Class],
) -> tuple[Course | None, Class | None]:
    """确定大数据演示课程及其对应班级。"""
    big_data_course = next(
        (course for course in courses if course.name == "大数据技术与应用"),
        courses[0] if courses else None,
    )
    if not big_data_course or not classes:
        return big_data_course, None
    big_data_class = next(
        (
            class_obj
            for class_obj in classes
            if ClassCourse.objects.filter(class_obj=class_obj, course=big_data_course).exists()
        ),
        classes[0],
    )
    return big_data_course, big_data_class


def _attach_students_to_classes(
    students: list[User],
    classes: list[Class],
    big_data_course: Course | None,
    big_data_class: Class | None,
) -> None:
    """建立学生的班级和默认课程上下文。"""
    if not classes:
        return

    for index, student in enumerate(students):
        target_class = classes[index % len(classes)]
        Enrollment.objects.get_or_create(
            user=student,
            class_obj=target_class,
            role="student",
        )
        if big_data_class and target_class != big_data_class:
            Enrollment.objects.get_or_create(
                user=student,
                class_obj=big_data_class,
                role="student",
            )

        UserCourseContext.objects.update_or_create(
            user=student,
            defaults={
                "current_class": big_data_class or target_class,
                "current_course": big_data_course,
            },
        )

    demo_student = next((student for student in students if student.username == "student1"), None)
    if demo_student:
        for class_obj in classes:
            Enrollment.objects.get_or_create(
                user=demo_student,
                class_obj=class_obj,
                role="student",
            )


def _seed_student_demo_state(students: list[User], big_data_course: Course | None) -> None:
    """为 student1 预置演示用大数据课程状态。"""
    if not big_data_course or not students:
        return
    demo_student = next((student for student in students if student.username == "student1"), None)
    _preset_student1_demo_data(demo_student, big_data_course)


def _seed_class_invitations(
    data: dict[str, Any],
    classes: list[Class],
    admin_user: User,
) -> None:
    """写入班级邀请码。"""
    for invitation_cfg in data.get("class_invitations", []):
        class_index = invitation_cfg.get("class_index", 0)
        if class_index >= len(classes):
            continue
        created_by = classes[class_index].teacher or admin_user
        ClassInvitation.objects.update_or_create(
            code=invitation_cfg["code"],
            defaults={
                "class_obj": classes[class_index],
                "created_by": created_by,
                "max_uses": invitation_cfg.get("max_uses", 0),
            },
        )


def _seed_survey_questions(data: dict[str, Any], courses: list[Course]) -> None:
    """写入问卷题目种子。"""
    survey_data = data.get("survey_questions", {})
    for survey_question in survey_data.get("habit", []):
        SurveyQuestion.objects.update_or_create(
            text=survey_question["text"],
            survey_type="habit",
            course=None,
            defaults={
                "question_type": survey_question.get("question_type", "single_select"),
                "options": survey_question.get("options", []),
                "order": survey_question.get("order", 1),
                "is_global": survey_question.get("is_global", True),
            },
        )

    for survey_question in survey_data.get("ability", []):
        SurveyQuestion.objects.update_or_create(
            text=survey_question["text"],
            survey_type="ability",
            course=courses[0] if courses else None,
            defaults={
                "question_type": survey_question.get("question_type", "single_select"),
                "options": survey_question.get("options", []),
                "dimension": survey_question.get("score_dimension"),
                "order": survey_question.get("order", 1),
                "is_global": False,
            },
        )


def seed_database_from_testdata(data: dict[str, Any]) -> SeededTestDataState:
    """按 testdata 结构灌入基础测试数据。"""
    admin_user, teachers, students = _seed_user_accounts(data)
    _seed_activation_codes(data, admin_user)
    courses = _seed_courses(data, teachers, admin_user)
    classes = _seed_classes(data, teachers, admin_user, courses)
    big_data_course, big_data_class = _resolve_big_data_context(courses, classes)
    _attach_students_to_classes(students, classes, big_data_course, big_data_class)
    _seed_student_demo_state(students, big_data_course)
    _seed_class_invitations(data, classes, admin_user)
    _seed_survey_questions(data, courses)
    return SeededTestDataState(
        admin_user=admin_user,
        teachers=teachers,
        students=students,
        courses=courses,
        classes=classes,
        big_data_course=big_data_course,
        big_data_class=big_data_class,
    )


def sync_seeded_courses(courses: list[Course]) -> None:
    """同步课程图谱和 GraphRAG 索引。"""
    for course in courses:
        try:
            if neo4j_service.is_available:
                neo4j_service.sync_knowledge_graph(int(course.pk))
                print(f"  {_status_flag(True)} 已同步课程图谱到 Neo4j: {course.name}")
        except Exception as error:
            print(f"  {_status_flag(False)} Neo4j 同步失败: {course.name} ({error})")

        try:
            index_paths = refresh_rag_corpus(course_id=int(course.pk))
            if index_paths:
                print(f"  {_status_flag(True)} 已构建课程 GraphRAG 索引: {course.name}")
        except Exception as error:
            print(f"  {_status_flag(False)} GraphRAG 索引构建失败: {course.name} ({error})")
