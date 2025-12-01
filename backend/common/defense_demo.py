#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
演示环境预置能力。
@Project : wisdom-edu
@File : defense_demo.py
@Author : Qintsg
@Date : 2026-03-27
"""

from __future__ import annotations

from typing import Any, cast

from decimal import Decimal
from datetime import timedelta

from django.utils import timezone

from assessments.models import (
    Assessment, AssessmentQuestion, AssessmentResult, AssessmentStatus,
    AbilityScore, AnswerHistory, Question,
)
from common.utils import (
    build_answer_display,
    build_normalized_score_map,
    decorate_question_options,
    extract_answer_value,
    score_questions,
    serialize_answer_payload,
)
from courses.models import Class, ClassCourse, Course, Enrollment
from exams.models import Exam, ExamQuestion, ExamSubmission, FeedbackReport
from knowledge.models import KnowledgeMastery, KnowledgePoint, KnowledgeRelation, ProfileSummary, Resource
from learning.models import LearningPath, NodeProgress, PathNode
from users.models import HabitPreference, User, UserCourseContext

DEFENSE_DEMO_MARKER = "DEFENSE_DEMO_PRESET"
DEFENSE_DEMO_TEACHER_USERNAME = "teacher"
DEFENSE_DEMO_WARMUP_STUDENT_USERNAME = "student1"
DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME = "student"
DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS: tuple[dict[str, str], ...] = (
    {
        "username": "student2",
        "email": "student2@example.com",
        "real_name": "学生2",
        "student_id": "20240002",
    },
    {
        "username": "student3",
        "email": "student3@example.com",
        "real_name": "学生3",
        "student_id": "20240003",
    },
    {
        "username": "student4",
        "email": "student4@example.com",
        "real_name": "学生4",
        "student_id": "20240004",
    },
    {
        "username": "student5",
        "email": "student5@example.com",
        "real_name": "学生5",
        "student_id": "20240005",
    },
)
DEFENSE_DEMO_SUPPORT_COURSE_NAME = "数据库原理与应用"
DEFENSE_DEMO_CLASS_NAME = "2024级大数据技术1班"
DEMO_ASSESSMENT_PRESETS: dict[str, dict[str, object]] = {
    DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME: {
        "habit_preference": {
            "preferred_resource": "video",
            "preferred_study_time": "evening",
            "study_pace": "moderate",
            "study_duration": "medium",
            "review_frequency": "weekly",
            "learning_style": "visual",
            "accept_challenge": True,
            "daily_goal_minutes": 50,
            "weekly_goal_days": 5,
            "preferences": {
                "preferred_resource": "video",
                "preferred_study_time": "evening",
                "study_pace": "moderate",
                "daily_goal_minutes": 50,
                "weekly_goal_days": 5,
                "review_frequency": "weekly",
                "learning_style": "visual",
                "accept_challenge": True,
                "difficulty_strategy": "先看解析再重试",
            },
        },
        "ability_scores": {
            "逻辑推理": 84,
            "抽象思维": 79,
            "信息整合": 81,
            "学习迁移": 76,
        },
        "profile_summary": {
            "summary": "该学生对大数据基础概念有一定掌握，但在 Hadoop 组件识别和 Spark 高级特性理解上仍存在薄弱环节。",
            "weakness": "对 HDFS 与 MapReduce 的职责区分不够清晰；RDD 惰性求值与容错机制的判断有误。",
            "suggestion": "建议沿概念 → 生态结构 → 计算模型的顺序逐步学习，着重强化 Hadoop 组件辨识和 Spark 核心抽象。",
        },
        "planned_answers": ["B", "C", "A", "C", "A", ["A", "B"]],
        "assessment_feedback": {
            "summary": "初始评测显示该学生对大数据基础概念掌握较好，但在 Hadoop 组件辨识和 Spark 高级特性上存在知识盲区。",
            "analysis": "学生在概念类题目上表现稳定，但对平台组件职责和分布式计算高级抽象的区分仍需加强。",
            "recommendations": [
                "先沿知识图谱梳理概念与组件关系。",
                "重点复习 Hadoop 组件的职责划分，区分 HDFS、YARN 与 MapReduce。",
                "结合实例理解 RDD 惰性求值与容错特性，完成阶段测试后根据掌握度变化继续补强。",
            ],
            "next_tasks": [
                "进入学习路径完成前三个学习节点。",
                "在阶段测试中验证概念迁移效果。",
            ],
            "conclusion": "基础概念掌握较好，Hadoop 生态与 Spark 高级特性是当前主要提升方向，建议分阶段针对性强化。",
        },
    },
    DEFENSE_DEMO_WARMUP_STUDENT_USERNAME: {
        "habit_preference": {
            "preferred_resource": "document",
            "preferred_study_time": "morning",
            "study_pace": "adaptive",
            "study_duration": "medium",
            "review_frequency": "spaced",
            "learning_style": "reading",
            "accept_challenge": True,
            "daily_goal_minutes": 65,
            "weekly_goal_days": 5,
            "preferences": {
                "preferred_resource": "document",
                "preferred_study_time": "morning",
                "study_pace": "adaptive",
                "daily_goal_minutes": 65,
                "weekly_goal_days": 5,
                "review_frequency": "spaced",
                "learning_style": "reading",
                "accept_challenge": True,
                "difficulty_strategy": "先梳理框架再做题验证",
            },
        },
        "ability_scores": {
            "逻辑推理": 88,
            "抽象思维": 86,
            "信息整合": 85,
            "学习迁移": 83,
        },
        "profile_summary": {
            "summary": "该学生已经建立较稳定的大数据基础认知，能够较好地串联概念、平台组件与计算模型。",
            "weakness": "对 Spark 惰性求值和执行抽象仍需通过阶段测试后的资源巩固进一步加深。",
            "suggestion": "建议继续沿学习路径完成阶段测试后的进阶节点，并结合知识图谱复盘关键依赖关系。",
        },
        "planned_answers": ["B", "C", "C", "C", "A", ["A", "B"]],
        "assessment_feedback": {
            "summary": "初始评测结果表明该学生基础较扎实，已能准确识别 Hadoop 核心组件，但在 Spark 细节理解上仍有提升空间。",
            "analysis": "学生对概念与组件题表现稳定，说明前两章知识框架已建立；Spark 多选题失分显示其对执行抽象的细节掌握还不够牢固。",
            "recommendations": [
                "优先完成 Spark 计算模型相关学习节点，再通过阶段测试验证掌握度提升。",
                "结合资源页中的资料，复盘 RDD 与 MapReduce 的差异。",
            ],
            "next_tasks": [
                "查看学习路径并完成前三个学习节点。",
                "完成阶段测试，观察掌握度变化和后续节点刷新。",
            ],
            "conclusion": "学生已经具备继续推进阶段测试和进阶学习的基础，适合作为答辩演示中的预热账号。",
        },
    },
}


def _get_demo_assessment_preset(username: str) -> dict[str, object]:
    """
    获取演示账号的评测与画像预置。
    :param username: 演示账号用户名。
    :return: 评测预置字典；未知账号回退到主演示学生配置。
    """
    preset = DEMO_ASSESSMENT_PRESETS.get(username)
    if isinstance(preset, dict):
        return preset
    return DEMO_ASSESSMENT_PRESETS[DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME]


def get_course_defense_demo_config(course: Course | None) -> dict[str, object]:
    """
    读取课程上的演示预置配置。
    :param course: 课程对象。
    :return: 课程配置中的预置字典。
    """
    if not course or not isinstance(course.config, dict):
        return {}
    raw_config = course.config.get("defense_demo")
    return raw_config if isinstance(raw_config, dict) else {}


def is_defense_demo_primary_course(course: Course | None) -> bool:
    """
    判断课程是否为主演示课程。
    :param course: 课程对象。
    :return: True 表示主演示课程。
    """
    return get_course_defense_demo_config(course).get("mode") == "primary"


def is_defense_demo_student(user: User | None, course: Course | None) -> bool:
    """
    判断是否为演示专用学生账号。
    :param user: 当前用户对象。
    :param course: 当前课程对象。
    :return: True 表示应走预置链路。
    """
    return bool(
        user
        and getattr(user, "username", "") == DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME
        and is_defense_demo_primary_course(course)
    )


def get_defense_demo_intro_payload(course: Course | None, point_id: int | None) -> dict[str, object] | None:
    """
    获取知识点介绍预置。
    :param course: 课程对象。
    :param point_id: 知识点 ID。
    :return: 预置介绍字典；不存在时返回 None。
    """
    if not point_id:
        return None

    point_map = get_course_defense_demo_config(course).get("point_intro_presets")
    if not isinstance(point_map, dict):
        return None

    payload = point_map.get(str(point_id))
    return payload if isinstance(payload, dict) else None


def get_defense_demo_resource_payload(progress: NodeProgress | None) -> dict[str, object] | None:
    """
    获取学习节点资源推荐预置。
    :param progress: 节点进度对象。
    :return: 资源推荐预置；不存在时返回 None。
    """
    if not progress or not isinstance(progress.extra_data, dict):
        return None
    payload = progress.extra_data.get("preset_resources")
    return payload if isinstance(payload, dict) else None


def get_defense_demo_stage_test_payload(progress: NodeProgress | None) -> dict[str, object] | None:
    """
    获取阶段测试固定反馈预置。
    :param progress: 节点进度对象。
    :return: 阶段测试预置；不存在时返回 None。
    """
    if not progress or not isinstance(progress.extra_data, dict):
        return None
    payload = progress.extra_data.get("preset_stage_test")
    return payload if isinstance(payload, dict) else None


def get_defense_demo_visible_order(path: LearningPath, user: User) -> int | None:
    """
    计算演示路径当前可见的最大节点顺序。
    :param path: 学习路径对象。
    :param user: 当前用户对象。
    :return: 最大可见顺序；不限制时返回 None。
    """
    config = get_course_defense_demo_config(path.course)
    visible_before_test_order = config.get("visible_before_test_order")
    if not isinstance(visible_before_test_order, int):
        return None

    stage_test_node = (
        path.nodes.filter(node_type="test").order_by("order_index", "id").first()
    )
    if not stage_test_node:
        return None

    progress = NodeProgress.objects.filter(node=stage_test_node, user=user).first()
    stage_result = None
    if progress and isinstance(progress.extra_data, dict):
        stage_result = progress.extra_data.get("stage_test_result")
    if isinstance(stage_result, dict) and stage_result.get("passed"):
        return None
    return visible_before_test_order


def _activate_next_locked_node(node: PathNode) -> None:
    """
    激活当前节点之后的下一个锁定节点。
    :param node: 当前学习路径节点。
    :return: None。
    """
    next_node = (
        PathNode.objects.filter(path=node.path, order_index__gt=node.order_index)
        .order_by("order_index", "id")
        .first()
    )
    if next_node and next_node.status == "locked":
        next_node.status = "active"
        next_node.save(update_fields=["status"])


def _set_related_knowledge_points(target: Question | Resource, point: KnowledgePoint) -> None:
    """
    统一设置题目或资源的知识点关联，避免 ManyToMany 静态推断噪声。
    :param target: 题目或资源对象。
    :param point: 关联知识点。
    :return: None。
    """
    relation_manager = cast(Any, target.knowledge_points)
    relation_manager.set([point])


def _question_knowledge_points(question: Question) -> list[KnowledgePoint]:
    """
    获取题目关联的知识点列表，并为静态分析提供明确类型。
    :param question: 题目对象。
    :return: 知识点列表。
    """
    relation_manager = cast(Any, question.knowledge_points)
    return [point for point in relation_manager.all() if isinstance(point, KnowledgePoint)]


def _question_options(question: Question) -> list[dict[str, object]]:
    """
    归一化题目选项，避免 JSONField 推断为 Any 时带来的类型噪声。
    :param question: 题目对象。
    :return: 仅包含字典项的选项列表。
    """
    if not isinstance(question.options, list):
        return []

    normalized_options: list[dict[str, object]] = []
    for option in question.options:
        if isinstance(option, dict):
            normalized_options.append(option)
    return normalized_options


def _as_object_dict(raw_value: object) -> dict[str, object]:
    """
    将任意对象收窄为字符串键字典。
    :param raw_value: 原始值。
    :return: 字典；不满足时返回空字典。
    """
    return raw_value if isinstance(raw_value, dict) else {}


def _coerce_mastery_after_map(raw_value: object) -> dict[int, float]:
    """
    规整阶段测试反馈中的掌握度映射。
    :param raw_value: 原始掌握度映射对象。
    :return: 以知识点 ID 为键的浮点数字典。
    """
    mastery_after_map: dict[int, float] = {}
    if not isinstance(raw_value, dict):
        return mastery_after_map

    for raw_key, raw_item in raw_value.items():
        if isinstance(raw_key, int) and isinstance(raw_item, int | float):
            mastery_after_map[raw_key] = float(raw_item)
            continue
        if isinstance(raw_key, str) and raw_key.isdigit() and isinstance(raw_item, int | float):
            mastery_after_map[int(raw_key)] = float(raw_item)
    return mastery_after_map


def _average_snapshot(snapshot: dict[int, float]) -> float | None:
    """
    计算掌握度快照的平均值。
    :param snapshot: 掌握度快照。
    :return: 平均值；无数据时返回 None。
    """
    if not snapshot:
        return None
    return round(sum(snapshot.values()) / len(snapshot), 4)


def _capture_mastery_snapshot(
    course: Course,
    student: User,
    points: list[KnowledgePoint],
) -> dict[int, float]:
    """
    读取指定知识点的当前掌握度快照。
    :param course: 所属课程。
    :param student: 学生账号。
    :param points: 需要关注的知识点列表。
    :return: 以知识点 ID 为键的掌握度映射。
    """
    return {
        mastery.knowledge_point_id: float(mastery.mastery_rate)
        for mastery in KnowledgeMastery.objects.filter(
            user=student,
            course=course,
            knowledge_point__in=points,
        )
    }


def _build_mastery_change_payload(
    points: list[KnowledgePoint],
    mastery_before_snapshot: dict[int, float],
    mastery_after_snapshot: dict[int, float],
) -> list[dict[str, object]]:
    """
    构建阶段测试前后的掌握度变化明细。
    :param points: 参与测试的知识点列表。
    :param mastery_before_snapshot: 测试前掌握度快照。
    :param mastery_after_snapshot: 测试后掌握度快照。
    :return: 掌握度变化列表。
    """
    mastery_changes: list[dict[str, object]] = []
    for point in points:
        before_rate = round(float(mastery_before_snapshot.get(point.id, 0.0)), 4)
        after_rate = round(float(mastery_after_snapshot.get(point.id, before_rate)), 4)
        mastery_changes.append(
            {
                "knowledge_point_id": point.id,
                "knowledge_point_name": point.name,
                "mastery_before": before_rate,
                "mastery_after": after_rate,
                "improvement": round(after_rate - before_rate, 4),
            }
        )
    return mastery_changes


def advance_defense_demo_path(node: PathNode, user: User, mark_skipped: bool = False) -> None:
    """
    按预置顺序推进学习路径，而不是触发完整重规划。
    :param node: 当前节点对象。
    :param user: 当前用户对象。
    :param mark_skipped: 是否将当前节点标记为跳过。
    :return: None。
    """

    node.status = "skipped" if mark_skipped else "completed"
    node.save(update_fields=["status"])
    _activate_next_locked_node(node)


def complete_defense_demo_stage_test(
    node: PathNode,
    user: User,
    progress: NodeProgress,
) -> None:
    """
    完成阶段测试后的固定解锁动作。
    :param node: 当前测试节点。
    :param user: 当前用户对象。
    :param progress: 当前节点进度。
    :return: None。
    """
    _ = user
    node.status = "completed"
    node.save(update_fields=["status"])
    _activate_next_locked_node(node)

    progress.updated_at = timezone.now()
    progress.save(update_fields=["updated_at"])


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


def _ensure_demo_points(course: Course) -> list[KnowledgePoint]:
    """
    创建演示专用知识点。
    :param course: 主课程。
    :return: 依顺序排列的知识点列表。
    """
    point_specs = [
        {
            "name": "大数据概念与特征",
            "chapter": "第1章 大数据技术基础",
            "description": "理解大数据的 4V 特征、典型应用与教学场景中的数据驱动价值。",
            "teaching_goal": "能概括大数据的核心特征，并说明其在真实业务中的意义。",
            "order": 9001,
        },
        {
            "name": "Hadoop 生态组成",
            "chapter": "第2章 Hadoop",
            "description": "区分 HDFS、MapReduce、YARN 在大数据平台中的职责。",
            "teaching_goal": "能解释 Hadoop 生态各组件之间的分工关系。",
            "order": 9002,
        },
        {
            "name": "Spark 核心计算模型",
            "chapter": "第3章 Spark",
            "description": "理解 Spark 的内存计算优势、RDD 抽象与批处理/迭代计算特点。",
            "teaching_goal": "能比较 Spark 与传统 MapReduce 在处理模式上的差异。",
            "order": 9003,
        },
    ]

    points: list[KnowledgePoint] = []
    for spec in point_specs:
        point, _ = KnowledgePoint.objects.update_or_create(
            course=course,
            name=spec["name"],
            defaults={
                "chapter": spec["chapter"],
                "description": spec["description"],
                "teaching_goal": spec["teaching_goal"],
                "order": spec["order"],
                "is_published": True,
            },
        )
        points.append(point)

    for index in range(len(points) - 1):
        KnowledgeRelation.objects.get_or_create(
            course=course,
            pre_point=points[index],
            post_point=points[index + 1],
            defaults={"relation_type": "prerequisite"},
        )
    return points


def _ensure_demo_resources(course: Course, teacher: User, points: list[KnowledgePoint]) -> dict[str, list[dict[str, object]]]:
    """
    创建学习节点固定展示用资源。
    :param course: 主演示课程。
    :param teacher: 教师对象。
    :param points: 知识点列表。
    :return: 按知识点名称组织的资源展示载荷。
    """
    resource_specs: dict[str, list[dict[str, object]]] = {
        points[0].name: [
            {
                "title": "大数据概念与特征导读",
                "resource_type": "document",
                "description": "帮助学生快速建立对 4V 特征和应用场景的整体认识。",
                "url": "/media/resources/bigdata-concepts-guide.pdf",
                "duration": 600,
            },
            {
                "title": "大数据典型应用案例",
                "resource_type": "video",
                "description": "通过案例说明大数据在真实场景中的业务价值。",
                "url": "/media/resources/bigdata-case-study.mp4",
                "duration": 420,
            },
        ],
        points[1].name: [
            {
                "title": "Hadoop 生态架构详解",
                "resource_type": "document",
                "description": "展示 HDFS、YARN 与 MapReduce 的协作关系及各组件职责。",
                "url": "/media/resources/hadoop-ecosystem-overview.pdf",
                "duration": 480,
            },
            {
                "title": "Hadoop 核心组件解析",
                "resource_type": "video",
                "description": "分模块说明 Hadoop 生态各核心组件职责。",
                "url": "/media/resources/hadoop-components-explained.mp4",
                "duration": 540,
            },
        ],
        points[2].name: [
            {
                "title": "Spark 内存计算原理",
                "resource_type": "document",
                "description": "从执行模型角度解释 Spark 的性能优势与 RDD 抽象。",
                "url": "/media/resources/spark-memory-computing.pdf",
                "duration": 360,
            },
            {
                "title": "Spark 与 MapReduce 对比分析",
                "resource_type": "link",
                "description": "对照展示两种计算框架在迭代任务中的性能差异。",
                "url": "/media/resources/spark-vs-mapreduce.pdf",
                "duration": 300,
            },
        ],
    }

    payload_map: dict[str, list[dict[str, object]]] = {}
    for point_idx, point in enumerate(points, start=1):
        payload_map[point.name] = []
        for index, spec in enumerate(resource_specs[point.name], start=1):
            resource, _ = Resource.objects.update_or_create(
                course=course,
                title=spec["title"],
                defaults={
                    "resource_type": spec["resource_type"],
                    "description": spec["description"],
                    "url": spec["url"],
                    "duration": spec["duration"],
                    "chapter_number": f"{point_idx}.{index}",
                    "sort_order": 9500 + index,
                    "is_visible": True,
                    "uploaded_by": teacher,
                },
            )
            _set_related_knowledge_points(resource, point)
            payload_map[point.name].append(
                {
                    "resource_id": resource.id,
                    "title": resource.title,
                    "type": resource.resource_type,
                    "description": resource.description or "",
                    "duration": resource.duration or 0,
                    "url": resource.url or "",
                    "required": True,
                    "is_internal": True,
                    "recommended_reason": f"该资源与“{point.name}”直接对应，有助于建立核心概念认知。",
                    "learning_tips": "建议先快速浏览核心概念，再带着整理笔记的方式回读重点段落。",
                    "completed": False,
                }
            )
    return payload_map


def _ensure_demo_stage_test(course: Course, teacher: User, points: list[KnowledgePoint]) -> Exam:
    """
    创建阶段测试题与试卷。
    :param course: 主课程。
    :param teacher: 教师对象。
    :param points: 知识点列表。
    :return: 阶段测试试卷对象。
    """
    question_specs = [
        {
            "content": "下列哪一项最能体现大数据区别于传统数据处理的核心特征？",
            "question_type": "single_choice",
            "answer": {"answer": "A"},
            "analysis": "4V 特征体现了大数据在规模、速度和多样性上的典型差异。",
            "knowledge_point": points[0],
            "options": [
                {"label": "A", "content": "数据规模大、类型多、处理速度要求高"},
                {"label": "B", "content": "只关注结构化数据的统计分析"},
                {"label": "C", "content": "仅在单机环境下进行离线处理"},
                {"label": "D", "content": "主要依赖人工整理和人工判断"},
            ],
        },
        {
            "content": "在 Hadoop 生态中，负责资源调度和集群管理的组件是哪个？",
            "question_type": "single_choice",
            "answer": {"answer": "B"},
            "analysis": "YARN 负责统一的资源管理与任务调度。",
            "knowledge_point": points[1],
            "options": [
                {"label": "A", "content": "HDFS"},
                {"label": "B", "content": "YARN"},
                {"label": "C", "content": "Hive"},
                {"label": "D", "content": "Sqoop"},
            ],
        },
        {
            "content": "关于 Spark 与 MapReduce 的区别，下列说法正确的是哪些？",
            "question_type": "multiple_choice",
            "answer": {"answers": ["A", "C"]},
            "analysis": "Spark 强调内存计算和更适合迭代场景，而 MapReduce 更偏批处理磁盘中转。",
            "knowledge_point": points[2],
            "options": [
                {"label": "A", "content": "Spark 更适合迭代计算场景"},
                {"label": "B", "content": "MapReduce 天然以内存计算为主"},
                {"label": "C", "content": "Spark 可通过 RDD 等抽象减少多轮磁盘落地"},
                {"label": "D", "content": "二者在执行模型上完全相同"},
            ],
        },
    ]

    ordered_questions: list[Question] = []
    for index, spec in enumerate(question_specs, start=1):
        question, _ = Question.objects.update_or_create(
            course=course,
            content=spec["content"],
            defaults={
                "chapter": "阶段测试",
                "question_type": spec["question_type"],
                "options": spec["options"],
                "answer": spec["answer"],
                "analysis": spec["analysis"],
                "difficulty": "medium",
                "score": Decimal("33.33") if index < 3 else Decimal("33.34"),
                "is_visible": True,
                "created_by": teacher,
            },
        )
        _set_related_knowledge_points(question, cast(KnowledgePoint, spec["knowledge_point"]))
        ordered_questions.append(question)

    exam, _ = Exam.objects.update_or_create(
        course=course,
        title="阶段测试：大数据基础综合",
        defaults={
            "description": "基于前三个学习节点的核心知识点出题，检验阶段学习成果并触发后续路径调整。",
            "exam_type": "node_test",
            "total_score": Decimal("100"),
            "pass_score": Decimal("60"),
            "duration": 10,
            "status": "published",
            "created_by": teacher,
        },
    )
    ExamQuestion.objects.filter(exam=exam).exclude(question__in=ordered_questions).delete()
    for index, question in enumerate(ordered_questions, start=1):
        exam_question, _ = ExamQuestion.objects.update_or_create(
            exam=exam,
            question=question,
            defaults={
                "order": index,
                "score": Decimal("35") if index < 3 else Decimal("30"),
            },
        )
        _ = exam_question
    return exam


def _build_point_intro_payloads(points: list[KnowledgePoint]) -> dict[str, dict[str, object]]:
    """
    为知识点创建固定介绍内容。
    :param points: 知识点列表。
    :return: 以知识点 ID 字符串为键的介绍映射。
    """
    payloads = [
        {
            "introduction": "大数据概念与特征节点主要帮助学生理解为什么现代数据处理要从单机思维转向分布式与海量场景。重点理解 4V 特征及其如何支撑后续 Hadoop 与 Spark 的学习。",
            "key_concepts": ["4V 特征", "分布式处理", "数据价值挖掘"],
            "learning_tips": "先抓住海量、多样、实时这三个关键词，再把它们和实际业务场景对应起来。",
            "difficulty": "easy",
            "sources": ["大数据概念与特征导读"],
        },
        {
            "introduction": "Hadoop 生态组成节点用于解释大数据平台为什么要把存储、计算和资源管理拆成多个组件。学生在这一节点应该能区分 HDFS、MapReduce 和 YARN 的职责分工。",
            "key_concepts": ["HDFS", "MapReduce", "YARN"],
            "learning_tips": "建议把组件关系先画成结构图，再用一句话分别概括每个组件负责什么。",
            "difficulty": "medium",
            "sources": ["Hadoop 生态架构详解"],
        },
        {
            "introduction": "Spark 核心计算模型节点用于引出内存计算与迭代任务优化这两个核心优势。这里展示的是从框架执行机制角度理解 Spark，而不是只背诵概念。",
            "key_concepts": ["RDD", "内存计算", "迭代任务"],
            "learning_tips": "把 Spark 与 MapReduce 做对比记忆，会更容易理解它为什么适合机器学习和图计算场景。",
            "difficulty": "medium",
            "sources": ["Spark 内存计算原理"],
        },
    ]

    intro_map: dict[str, dict[str, object]] = {}
    for point, payload in zip(points, payloads, strict=True):
        point.introduction = str(payload["introduction"])
        point.save(update_fields=["introduction", "updated_at"])
        intro_map[str(point.id)] = payload
    return intro_map


def _build_ai_demo_query_payloads(points: list[KnowledgePoint]) -> list[dict[str, object]]:
    """
    为答辩演示准备可直接复用的 AI 助手提问脚本。
    :param points: 主演示课程知识点列表。
    :return: 供课程配置与 CLI 输出复用的提问预置。
    """
    return [
        {
            "title": "图谱关系问答",
            "question": f"{points[2].name} 的前置知识是什么？为什么建议先学这些内容？",
            "point_id": points[2].id,
            "point_name": points[2].name,
            "expected_modes": ["graph_tools", "local"],
            "expected_focus": ["前置知识", "课程证据"],
        },
        {
            "title": "课程证据追问",
            "question": f"围绕 {points[1].name}，当前课程里有哪些资源或证据最值得先看？",
            "point_id": points[1].id,
            "point_name": points[1].name,
            "expected_modes": ["graph_tools", "local"],
            "expected_focus": ["资源推荐", "课程证据"],
        },
        {
            "title": "课程级学习建议",
            "question": "如果我接下来只剩 20 分钟，应该先复习哪些大数据基础内容？",
            "point_id": None,
            "point_name": "",
            "expected_modes": ["local", "global", "graph_tools"],
            "expected_focus": ["课程级 GraphRAG", "学习路径建议"],
        },
    ]


def _ensure_demo_assessment_questions(
    course: Course, teacher: User, points: list[KnowledgePoint],
) -> list[Question]:
    """
    为初始评测创建固定题目（2 题/知识点，共 6 题）。
    :param course: 所属课程。
    :param teacher: 教师（创建者）。
    :param points: 知识点列表。
    :return: 题目列表（按出题顺序）。
    """

    # 题目规格：知识点 → 2 道题，总分 100（16.67*4 + 16.66*2）
    specs = [
        # ---- 大数据概念与特征（points[0]）----
        {
            "content": '下列哪项是大数据"4V"特征中用于描述数据产生速度的维度？',
            "question_type": "single_choice",
            "answer": {"answer": "B"},
            "analysis": "Velocity 指数据产生和流动的速度，是大数据区别于传统数据集的关键维度之一。",
            "knowledge_point": points[0],
            "options": [
                {"label": "A", "content": "Volume"},
                {"label": "B", "content": "Velocity"},
                {"label": "C", "content": "Variety"},
                {"label": "D", "content": "Value"},
            ],
            "score": Decimal("16.67"),
        },
        {
            "content": "大数据处理与传统数据处理的关键区别在于？",
            "question_type": "single_choice",
            "answer": {"answer": "C"},
            "analysis": "大数据处理需要分布式架构才能在可接受的时间内完成海量异构数据的存储与计算。",
            "knowledge_point": points[0],
            "options": [
                {"label": "A", "content": "数据量大但处理逻辑完全相同"},
                {"label": "B", "content": "必须使用云计算平台"},
                {"label": "C", "content": "需要分布式架构支持海量异构数据的存储与计算"},
                {"label": "D", "content": "只能处理结构化数据"},
            ],
            "score": Decimal("16.67"),
        },
        # ---- Hadoop 生态组成（points[1]）----
        {
            "content": "在 Hadoop 生态系统中，负责分布式文件存储的核心组件是？",
            "question_type": "single_choice",
            "answer": {"answer": "C"},
            "analysis": "HDFS（Hadoop Distributed File System）是 Hadoop 的分布式文件存储层，提供高吞吐量的数据访问。",
            "knowledge_point": points[1],
            "options": [
                {"label": "A", "content": "MapReduce"},
                {"label": "B", "content": "YARN"},
                {"label": "C", "content": "HDFS"},
                {"label": "D", "content": "Hive"},
            ],
            "score": Decimal("16.67"),
        },
        {
            "content": "YARN 在 Hadoop 中的主要职责是什么？",
            "question_type": "single_choice",
            "answer": {"answer": "C"},
            "analysis": "YARN 统一管理集群资源并调度各类计算框架的任务，是 Hadoop 2.x 后的核心组件。",
            "knowledge_point": points[1],
            "options": [
                {"label": "A", "content": "数据存储"},
                {"label": "B", "content": "数据清洗"},
                {"label": "C", "content": "资源调度与集群管理"},
                {"label": "D", "content": "数据可视化"},
            ],
            "score": Decimal("16.67"),
        },
        # ---- Spark 核心计算模型（points[2]）----
        {
            "content": "Spark 相比 MapReduce 的核心优势主要体现在？",
            "question_type": "single_choice",
            "answer": {"answer": "A"},
            "analysis": "Spark 利用内存计算模型，大幅减少了中间结果的磁盘 IO，尤其适合迭代和交互式计算。",
            "knowledge_point": points[2],
            "options": [
                {"label": "A", "content": "基于内存的计算模型减少磁盘 IO"},
                {"label": "B", "content": "使用更少的集群节点"},
                {"label": "C", "content": "不需要集群环境即可运行"},
                {"label": "D", "content": "只能处理批量数据"},
            ],
            "score": Decimal("16.66"),
        },
        {
            "content": "以下关于 RDD（弹性分布式数据集）的描述，哪些是正确的？",
            "question_type": "multiple_choice",
            "answer": {"answers": ["A", "C"]},
            "analysis": "RDD 是只读的分区数据集合，支持惰性求值（lazy evaluation），在行动算子触发时才真正执行计算。",
            "knowledge_point": points[2],
            "options": [
                {"label": "A", "content": "RDD 是只读的分区数据集合"},
                {"label": "B", "content": "RDD 不支持容错机制"},
                {"label": "C", "content": "RDD 支持惰性求值"},
                {"label": "D", "content": "RDD 只能存储文本数据"},
            ],
            "score": Decimal("16.66"),
        },
    ]

    ordered: list[Question] = []
    for spec in specs:
        # 以课程+题目内容为唯一键，确保幂等
        question, _ = Question.objects.update_or_create(
            course=course,
            content=spec["content"],
            defaults={
                "chapter": "初始评测",
                "question_type": spec["question_type"],
                "options": spec["options"],
                "answer": spec["answer"],
                "analysis": spec["analysis"],
                "difficulty": "medium",
                "score": spec["score"],
                "is_visible": False,
                "for_initial_assessment": True,
                "created_by": teacher,
            },
        )
        _set_related_knowledge_points(question, cast(KnowledgePoint, spec["knowledge_point"]))
        ordered.append(question)
    return ordered


def _build_assessment_report_payload(
    questions: list[Question],
    planned_raw: list[object],
) -> tuple[dict[str, object], list[dict[str, object]], list[bool]]:
    """
    构建初始评测答题明细（含故意错题），匹配真实提交流程的数据结构。
    :param questions: 6 道评测题目（顺序固定）。
    :return: (原始答案字典, 题目详情列表, 各题正误列表)。
    """

    if len(planned_raw) != len(questions):
        raise ValueError("演示评测答案配置与题目数量不一致")

    raw_answers: dict[str, object] = {}
    question_details: list[dict[str, object]] = []
    is_correct_flags: list[bool] = []

    for question, student_raw in zip(questions, planned_raw, strict=True):
        q_id = str(question.id)
        raw_answers[q_id] = student_raw

        # 提取正确答案原始值
        correct_raw = question.answer.get("answers") or question.answer.get("answer")

        # 判定正误（匹配 submit_knowledge_assessment 逻辑）
        if question.question_type == "multiple_choice":
            correct_set = {str(x).strip().upper() for x in (correct_raw if isinstance(correct_raw, list) else [correct_raw])}
            student_set = {str(x).strip().upper() for x in (student_raw if isinstance(student_raw, list) else [student_raw])}
            is_correct = correct_set == student_set
        else:
            is_correct = str(student_raw).strip().upper() == str(correct_raw).strip().upper()

        is_correct_flags.append(is_correct)

        # 选项装饰
        decorated_options = decorate_question_options(
            question.options,
            question.question_type,
            student_answer=student_raw,
            correct_answer=correct_raw,
        )
        question_details.append({
            "question_id": question.id,
            "content": question.content,
            "question_type": question.question_type,
            "student_answer": student_raw,
            "correct_answer": correct_raw,
            "student_answer_display": build_answer_display(student_raw, question.question_type, decorated_options),
            "correct_answer_display": build_answer_display(correct_raw, question.question_type, decorated_options),
            "is_correct": is_correct,
            "analysis": question.analysis or "",
            "options": decorated_options,
            "knowledge_points": [
                {"id": point.id, "name": point.name}
                for point in _question_knowledge_points(question)
            ],
        })

    return raw_answers, question_details, is_correct_flags


def _ensure_demo_assessment_state(
    course: Course,
    student: User,
    teacher: User,
    points: list[KnowledgePoint],
) -> None:
    """
    预置学生的初始评测、画像和掌握度状态，数据结构与真实提交流程完全一致。
    :param course: 主课程。
    :param student: 学生账号。
    :param teacher: 教师账号（创建评测题目）。
    :param points: 知识点列表。
    :return: None。
    """

    preset = _get_demo_assessment_preset(student.username)
    habit_defaults = {
        "preferred_resource": "video",
        "preferred_study_time": "evening",
        "study_pace": "moderate",
        "study_duration": "medium",
        "review_frequency": "weekly",
        "learning_style": "visual",
        "accept_challenge": True,
        "daily_goal_minutes": 50,
        "weekly_goal_days": 5,
        "preferences": {
            "preferred_resource": "video",
            "preferred_study_time": "evening",
            "study_pace": "moderate",
            "daily_goal_minutes": 50,
            "weekly_goal_days": 5,
            "review_frequency": "weekly",
            "learning_style": "visual",
            "accept_challenge": True,
            "difficulty_strategy": "先看解析再重试",
        },
    }
    raw_habit_defaults = preset.get("habit_preference")
    if isinstance(raw_habit_defaults, dict):
        habit_defaults.update(raw_habit_defaults)

    ability_scores = {
        "逻辑推理": 84,
        "抽象思维": 79,
        "信息整合": 81,
        "学习迁移": 76,
    }
    raw_ability_scores = preset.get("ability_scores")
    if isinstance(raw_ability_scores, dict):
        ability_scores = {
            key: int(value)
            for key, value in raw_ability_scores.items()
            if isinstance(key, str) and isinstance(value, int | float)
        }

    profile_defaults = {
        "summary": "该学生对大数据基础概念有一定掌握，但在 Hadoop 组件识别和 Spark 高级特性理解上仍存在薄弱环节。",
        "weakness": "对 HDFS 与 MapReduce 的职责区分不够清晰；RDD 惰性求值与容错机制的判断有误。",
        "suggestion": "建议沿概念 → 生态结构 → 计算模型的顺序逐步学习，着重强化 Hadoop 组件辨识和 Spark 核心抽象。",
    }
    raw_profile_defaults = preset.get("profile_summary")
    if isinstance(raw_profile_defaults, dict):
        profile_defaults.update(raw_profile_defaults)

    assessment_feedback_defaults = {
        "summary": "初始评测显示该学生对大数据基础概念掌握较好，但在 Hadoop 组件辨识和 Spark 高级特性上存在知识盲区。",
        "analysis": "学生在概念类题目上表现稳定，但对平台组件职责和分布式计算高级抽象的区分仍需加强。",
        "recommendations": [
            "先沿知识图谱梳理概念与组件关系。",
            "重点复习 Hadoop 组件的职责划分，区分 HDFS、YARN 与 MapReduce。",
            "结合实例理解 RDD 惰性求值与容错特性，完成阶段测试后根据掌握度变化继续补强。",
        ],
        "next_tasks": [
            "进入学习路径完成前三个学习节点。",
            "在阶段测试中验证概念迁移效果。",
        ],
        "conclusion": "基础概念掌握较好，Hadoop 生态与 Spark 高级特性是当前主要提升方向，建议分阶段针对性强化。",
    }
    raw_assessment_feedback = preset.get("assessment_feedback")
    if isinstance(raw_assessment_feedback, dict):
        assessment_feedback_defaults.update(raw_assessment_feedback)

    planned_answers = preset.get("planned_answers")
    if not isinstance(planned_answers, list):
        planned_answers = ["B", "C", "A", "C", "A", ["A", "B"]]

    # ---- 学习习惯（匹配 submit_habit_survey 产出） ----
    HabitPreference.objects.update_or_create(
        user=student,
        defaults=habit_defaults,
    )

    # ---- 学习能力 ----
    AbilityScore.objects.update_or_create(
        user=student,
        course=course,
        defaults={"scores": ability_scores},
    )

    # ---- 评测状态 ----
    AssessmentStatus.objects.update_or_create(
        user=student,
        course=course,
        defaults={
            "knowledge_done": True,
            "ability_done": True,
            "habit_done": True,
            "generating": False,
            "generation_error": "",
        },
    )

    # ---- 画像摘要 ----
    ProfileSummary.objects.update_or_create(
        user=student,
        course=course,
        defaults=profile_defaults,
    )

    # ---- 创建评测题目（6 题，2 题/知识点） ----
    questions = _ensure_demo_assessment_questions(course, teacher, points)

    # ---- 构建答题明细（含 2 道错题） ----
    raw_answers, question_details, is_correct_flags = _build_assessment_report_payload(
        questions,
        planned_answers,
    )

    # ---- 创建 Assessment 及 AssessmentQuestion 关联 ----
    knowledge_assessment = (
        Assessment.objects.filter(course=course, assessment_type="knowledge", is_active=True)
        .order_by("id")
        .first()
    )
    if not knowledge_assessment:
        knowledge_assessment = Assessment.objects.create(
            course=course,
            title=f"{course.name} 初始知识评测",
            assessment_type="knowledge",
            description="基于课程知识点的初始掌握度评测。",
            is_active=True,
        )

    # through 模型记录（匹配 get_knowledge_assessment 的创建逻辑）
    for order, question in enumerate(questions, start=1):
        AssessmentQuestion.objects.update_or_create(
            assessment=knowledge_assessment,
            question=question,
            defaults={"order": order},
        )

    # ---- 逐题创建 AnswerHistory（匹配 submit_knowledge_assessment） ----
    for question, is_correct in zip(questions, is_correct_flags, strict=True):
        point = question.knowledge_points.first()
        student_raw = raw_answers[str(question.id)]
        correct_raw = question.answer.get("answers") or question.answer.get("answer")
        AnswerHistory.objects.update_or_create(
            user=student,
            course=course,
            question=question,
            source="initial",
            defaults={
                "knowledge_point": point,
                "student_answer": serialize_answer_payload(question.question_type, student_raw),
                "correct_answer": serialize_answer_payload(question.question_type, correct_raw),
                "is_correct": is_correct,
                "score": Decimal(str(float(question.score))) if is_correct else Decimal("0"),
                "source": "initial",
            },
        )

    # ---- 贝叶斯掌握度基线（匹配 _calculate_initial_mastery_baseline） ----
    # 公式: mastery = (correct + 4.0 * 0.25) / (total + 4.0), cap [0, 0.85]
    point_stats: dict[int, dict[str, int]] = {}
    for question, is_correct in zip(questions, is_correct_flags, strict=True):
        for p in _question_knowledge_points(question):
            if p.id not in point_stats:
                point_stats[p.id] = {"correct": 0, "total": 0}
            point_stats[p.id]["total"] += 1
            if is_correct:
                point_stats[p.id]["correct"] += 1

    mastery_map: dict[int, Decimal] = {}
    for pid, stats in point_stats.items():
        raw = (stats["correct"] + 0.25 * 4.0) / (stats["total"] + 4.0)
        mastery_map[pid] = Decimal(str(round(min(max(raw, 0.0), 0.85), 4)))

    for point in points:
        KnowledgeMastery.objects.update_or_create(
            user=student,
            course=course,
            knowledge_point=point,
            defaults={"mastery_rate": mastery_map.get(point.id, Decimal("0.25"))},
        )

    # ---- 计算得分汇总 ----
    total_score = sum(float(q.score or 0) for q in questions)
    earned_score = sum(
        float(q.score) for q, correct in zip(questions, is_correct_flags, strict=True) if correct
    )
    correct_count = sum(is_correct_flags)
    total_count = len(questions)
    accuracy = round(correct_count / total_count * 100, 1) if total_count else 0.0

    # ---- AssessmentResult（匹配 submit_knowledge_assessment 产出） ----
    assessment_result, _ = AssessmentResult.objects.update_or_create(
        user=student,
        assessment=knowledge_assessment,
        defaults={
            "course": course,
            "answers": raw_answers,
            "score": Decimal(str(round(earned_score, 2))),
            "result_data": {
                "mastery": [
                    {"point_id": p.id, "point_name": p.name, "mastery_rate": float(mastery_map.get(p.id, 0.25))}
                    for p in points
                ],
                "question_details": question_details,
                "total_score": round(total_score, 2),
                "correct_count": correct_count,
                "total_count": total_count,
            },
        },
    )

    # ---- FeedbackReport（匹配 _async_generate_after_assessment 产出） ----
    weak_points = [p for p in points if float(mastery_map.get(p.id, 0)) < 0.4]
    FeedbackReport.objects.update_or_create(
        user=student,
        source="assessment",
        assessment_result=assessment_result,
        defaults={
            "exam": None,
            "status": "completed",
            "overview": {
                "score": round(earned_score, 2),
                "total_score": round(total_score, 2),
                "correct_count": correct_count,
                "total_count": total_count,
                "accuracy": accuracy,
                "summary": str(assessment_feedback_defaults["summary"]),
                "knowledge_gaps": [p.name for p in weak_points]
                if weak_points
                else [points[-1].name],
            },
            "analysis": str(assessment_feedback_defaults["analysis"]),
            "recommendations": list(assessment_feedback_defaults["recommendations"]),
            "next_tasks": list(assessment_feedback_defaults["next_tasks"]),
            "conclusion": str(assessment_feedback_defaults["conclusion"]),
        },
    )


def _build_demo_student_answer(question: Question, force_correct: bool) -> tuple[dict[str, object], dict[str, object], bool]:
    """
    构造更贴近真实提交的学生答案载荷。
    :param question: 题目对象。
    :param force_correct: 是否生成正确答案。
    :return: (学生答案, 正确答案, 是否答对)。
    """
    correct_payload = question.answer or {}
    question_type = question.question_type

    if question_type == "multiple_choice":
        correct_answers = list(correct_payload.get("answers") or [])
        student_answers = list(correct_answers)
        if not force_correct and student_answers:
            fallback_option = next(
                (
                    option.get("label")
                    for option in _question_options(question)
                    if option.get("label") not in student_answers
                ),
                None,
            )
            if fallback_option:
                student_answers = [str(student_answers[0]), str(fallback_option)]
            else:
                student_answers = student_answers[:-1] or student_answers
        return (
            serialize_answer_payload(question_type, student_answers),
            serialize_answer_payload(question_type, correct_answers),
            force_correct,
        )

    correct_answer = str(correct_payload.get("answer") or "")
    student_answer = correct_answer
    if not force_correct:
        student_answer = str(
            next(
                (
                    option.get("label")
                    for option in _question_options(question)
                    if option.get("label") and option.get("label") != correct_answer
                ),
                correct_answer,
            )
        )
    return (
        serialize_answer_payload(question_type, student_answer),
        serialize_answer_payload(question_type, correct_answer),
        force_correct,
    )


def _seed_demo_practice_histories(
    course: Course,
    warmup_student: User,
    primary_student: User,
    stage_exam: Exam,
) -> None:
    """
    补充更接近真实学习过程的练习与阶段测试轨迹。

    这样做的目的不是改变答辩预置结论，而是为 KT / 推荐 / 画像链路
    提供更自然的时间序列证据，避免演示账号只拥有一次性“写死”评测。

    :param course: 主课程。
    :param warmup_student: 预热学生账号。
    :param primary_student: 主演示学生账号。
    :param stage_exam: 阶段测试试卷。
    :return: None。
    """
    now = timezone.now()
    practice_questions = list(
        Question.objects.filter(course=course, for_initial_assessment=True)
        # 预取关联知识点
        .prefetch_related("knowledge_points")
        .order_by("id")
    )
    stage_questions = [
        exam_question.question
        for exam_question in ExamQuestion.objects.filter(exam=stage_exam)
        # 预取关联题目
        .select_related("question")
        .order_by("order")
    ]
    if not practice_questions or not stage_questions:
        return

    history_specs = [
        (warmup_student, practice_questions[0], True, "practice", None, 9),
        (warmup_student, practice_questions[2], True, "practice", None, 8),
        (warmup_student, stage_questions[0], True, "exam", stage_exam.id, 6),
        (warmup_student, stage_questions[1], True, "exam", stage_exam.id, 6),
        (warmup_student, stage_questions[2], True, "exam", stage_exam.id, 6),
        (primary_student, practice_questions[0], True, "practice", None, 7),
        (primary_student, practice_questions[1], False, "practice", None, 6),
        (primary_student, practice_questions[3], True, "practice", None, 5),
        (primary_student, practice_questions[4], False, "practice", None, 4),
        (primary_student, stage_questions[0], True, "exam", stage_exam.id, 2),
        (primary_student, stage_questions[1], True, "exam", stage_exam.id, 2),
        (primary_student, stage_questions[2], True, "exam", stage_exam.id, 2),
    ]

    tracked_users = [warmup_student, primary_student]
    tracked_question_ids = [question.id for question in practice_questions + stage_questions]
    AnswerHistory.objects.filter(
        user__in=tracked_users,
        course=course,
        question_id__in=tracked_question_ids,
        source__in=["practice", "exam"],
    ).delete()

    for student, question, force_correct, source, exam_id, offset_days in history_specs:
        point = question.knowledge_points.first()
        if not point:
            continue
        student_answer, correct_answer, is_correct = _build_demo_student_answer(
            question=question,
            force_correct=force_correct,
        )
        history = AnswerHistory.objects.create(
            user=student,
            course=course,
            question=question,
            knowledge_point=point,
            student_answer=student_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            score=Decimal(str(float(question.score))) if is_correct else Decimal("0"),
            source=source,
            exam_id=exam_id,
        )
        history.answered_at = now - timedelta(days=offset_days, hours=(2 if source == "practice" else 1))
        history.save(update_fields=["answered_at"])


def _build_stage_feedback_payload(points: list[KnowledgePoint]) -> dict[str, object]:
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


def _ensure_warmup_stage_submission_and_feedback(
    course: Course,
    warmup_student: User,
    stage_exam: Exam,
    points: list[KnowledgePoint],
) -> dict[str, object]:
    """
    为预热账号补齐真实阶段测试提交与反馈报告。

    这样学生端的考试结果页、反馈报告页和浏览器巡检都能命中真实数据，
    避免预热账号只有练习轨迹、却没有可直接展示的阶段测试结果。

    :param course: 主课程。
    :param warmup_student: 预热学生账号。
    :param stage_exam: 阶段测试试卷。
    :param points: 演示知识点列表。
    :return: None。
    """
    stage_exam_questions = list(
        ExamQuestion.objects.filter(exam=stage_exam)
        .select_related("question")
        .prefetch_related("question__knowledge_points")
        .order_by("order")
    )
    stage_feedback = _build_stage_feedback_payload(points)
    if not stage_exam_questions:
        return {"submitted_at": timezone.now(), "stage_feedback": stage_feedback}

    questions = [exam_question.question for exam_question in stage_exam_questions]
    submission_answers = {
        str(question.id): extract_answer_value(question.answer)
        for question in questions
    }
    score_map = build_normalized_score_map(
        [
            (exam_question.question_id, float(exam_question.score or exam_question.question.score or 0))
            for exam_question in stage_exam_questions
        ],
        target_total_score=float(stage_exam.total_score or 0),
    )
    grading = score_questions(submission_answers, questions, score_map=score_map)
    submitted_at = timezone.now() - timedelta(days=1, hours=3)
    graded_at = submitted_at + timedelta(minutes=18)
    pass_score = float(stage_exam.pass_score or 0)
    if pass_score <= 0:
        pass_score = max(round(float(grading["total_score"]) * 0.6, 2), 1.0)
    passed = float(grading["score"]) >= pass_score

    submission, _ = ExamSubmission.objects.update_or_create(
        exam=stage_exam,
        user=warmup_student,
        defaults={
            "answers": submission_answers,
            "score": Decimal(str(float(grading["score"]))),
            "is_passed": passed,
            "graded_at": graded_at,
        },
    )
    if submission.submitted_at != submitted_at:
        submission.submitted_at = submitted_at
        submission.save(update_fields=["submitted_at"])

    mastery_after_map = _coerce_mastery_after_map(stage_feedback.get("mastery_after"))
    mastery_changes: list[dict[str, object]] = []
    for point in points:
        mastery_after = mastery_after_map.get(point.id)
        if mastery_after is None:
            continue
        mastery_record = KnowledgeMastery.objects.filter(
            user=warmup_student,
            course=course,
            knowledge_point=point,
        ).first()
        existing_before = float(mastery_record.mastery_rate) if mastery_record else 0.0
        fallback_before = max(round(float(mastery_after) - 0.18, 2), 0.28)
        mastery_before = (
            existing_before
            if 0 < existing_before < float(mastery_after)
            else fallback_before
        )
        KnowledgeMastery.objects.update_or_create(
            user=warmup_student,
            course=course,
            knowledge_point=point,
            defaults={"mastery_rate": Decimal(str(float(mastery_after)))},
        )
        mastery_changes.append(
            {
                "knowledge_point_id": point.id,
                "knowledge_point_name": point.name,
                "mastery_before": round(float(mastery_before), 4),
                "mastery_after": round(float(mastery_after), 4),
                "improvement": round(float(mastery_after) - float(mastery_before), 4),
            }
        )

    feedback_payload = _as_object_dict(stage_feedback.get("feedback_report"))
    FeedbackReport.objects.update_or_create(
        user=warmup_student,
        exam=stage_exam,
        defaults={
            "source": "exam",
            "exam_submission": submission,
            "status": "completed",
            "overview": {
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
            },
            "analysis": feedback_payload.get("analysis", ""),
            "recommendations": feedback_payload.get("recommendations", []),
            "next_tasks": feedback_payload.get("next_tasks", []),
            "conclusion": feedback_payload.get("conclusion", ""),
        },
    )
    return {"submitted_at": submitted_at, "stage_feedback": stage_feedback}


def _build_demo_stage_test_result(
    stage_exam: Exam,
    points: list[KnowledgePoint],
    mastery_before_snapshot: dict[int, float],
    submitted_at,
) -> dict[str, object]:
    """
    生成已完成阶段测试的固定结果快照，供预热账号直接展示完整报告页。
    :param stage_exam: 阶段测试试卷。
    :param points: 演示知识点列表。
    :param mastery_before_snapshot: 阶段测试前的掌握度快照。
    :param submitted_at: 固定提交时间。
    :return: 阶段测试结果字典。
    """
    stage_exam_questions = list(
        ExamQuestion.objects.filter(exam=stage_exam)
        .select_related("question")
        .prefetch_related("question__knowledge_points")
        .order_by("order")
    )
    questions = [exam_question.question for exam_question in stage_exam_questions]
    submission_answers = {
        str(question.id): extract_answer_value(question.answer)
        for question in questions
    }
    score_map = build_normalized_score_map(
        [
            (exam_question.question_id, float(exam_question.score or exam_question.question.score or 0))
            for exam_question in stage_exam_questions
        ],
        target_total_score=float(stage_exam.total_score or 0),
    )
    grading = score_questions(submission_answers, questions, score_map=score_map)
    stage_feedback = _build_stage_feedback_payload(points)
    mastery_after_snapshot = _coerce_mastery_after_map(stage_feedback.get("mastery_after"))
    question_result_map = {
        str(item["question_id"]): item for item in grading["question_results"]
    }
    question_details: list[dict[str, object]] = []
    for question in questions:
        question_id = str(question.id)
        student_answer = submission_answers[question_id]
        correct_answer = question_result_map.get(question_id, {}).get(
            "correct_answer",
            extract_answer_value(question.answer),
        )
        decorated_options = decorate_question_options(
            question.options,
            question.question_type,
            student_answer=student_answer,
            correct_answer=correct_answer,
        )
        question_details.append(
            {
                "question_id": question.id,
                "content": question.content,
                "question_type": question.question_type,
                "student_answer": student_answer,
                "correct_answer": correct_answer,
                "student_answer_display": build_answer_display(
                    student_answer,
                    question.question_type,
                    decorated_options,
                ),
                "correct_answer_display": build_answer_display(
                    correct_answer,
                    question.question_type,
                    decorated_options,
                ),
                "is_correct": True,
                "analysis": question.analysis or "",
                "options": decorated_options,
                "knowledge_points": [
                    {"id": point.id, "name": point.name}
                    for point in _question_knowledge_points(question)
                ],
                "score": question_result_map.get(question_id, {}).get("earned_score", 0),
                "full_score": question_result_map.get(question_id, {}).get("assigned_score", 0),
            }
        )

    return {
        "score": float(grading["score"]),
        "total_score": float(grading["total_score"]),
        "passed": True,
        "pass_threshold": float(stage_exam.pass_score or 60),
        "correct": len(questions),
        "correct_count": len(questions),
        "total": len(questions),
        "total_count": len(questions),
        "accuracy": 100.0,
        "mistakes": [],
        "question_details": question_details,
        "point_stats": grading["point_stats"],
        "mastery_changes": _build_mastery_change_payload(
            points,
            mastery_before_snapshot,
            mastery_after_snapshot,
        ),
        "feedback_report": _as_object_dict(stage_feedback.get("feedback_report")),
        "submitted_at": submitted_at.isoformat(),
        "node_status": "completed",
        "path_refreshed": True,
    }


def _ensure_demo_learning_path(
    course: Course,
    student: User,
    points: list[KnowledgePoint],
    resource_payloads: dict[str, list[dict[str, object]]],
    stage_exam: Exam,
    completed_stage_result: dict[str, object] | None = None,
) -> None:
    """
    创建固定学习路径与节点进度预置。
    :param course: 主课程。
    :param student: 学生账号。
    :param points: 知识点列表。
    :param resource_payloads: 固定资源展示载荷。
    :param stage_exam: 阶段测试试卷。
    :return: None。
    """
    path, _ = LearningPath.objects.update_or_create(
        user=student,
        course=course,
        defaults={
            "ai_reason": "先强化基础概念，再进入生态架构理解，最后串联计算模型，通过阶段测试触发后续节点。",
            "is_dynamic": True,
        },
    )

    node_specs = [
        {
            "title": "学习节点 1：大数据概念与特征",
            "goal": "理解 4V 特征和大数据在教学场景中的实际价值。",
            "criterion": "能用自己的话概括大数据的核心特征。",
            "suggestion": "先理解为什么数据规模与速度变化会推动架构升级。",
            "status": "active",
            "order_index": 1,
            "estimated_minutes": 6,
            "knowledge_point": points[0],
            "node_type": "study",
        },
        {
            "title": "学习节点 2：Hadoop 生态组成",
            "goal": "掌握 HDFS、MapReduce、YARN 之间的协作关系。",
            "criterion": "能说明存储、计算、调度三者各自负责什么。",
            "suggestion": "建议先看结构图，再结合组件职责做对照理解。",
            "status": "locked",
            "order_index": 2,
            "estimated_minutes": 5,
            "knowledge_point": points[1],
            "node_type": "study",
        },
        {
            "title": "学习节点 3：Spark 核心计算模型",
            "goal": "理解 Spark 与 MapReduce 在执行机制上的差异。",
            "criterion": "能解释为什么 Spark 更适合迭代与内存计算场景。",
            "suggestion": "重点关注执行模型差异，而不是只背诵框架名称。",
            "status": "locked",
            "order_index": 3,
            "estimated_minutes": 5,
            "knowledge_point": points[2],
            "node_type": "study",
        },
        {
            "title": "阶段测试：大数据基础综合",
            "goal": "验证前三个学习节点的核心概念是否已经连成完整链路。",
            "criterion": "通过阶段测试并触发后续学习节点。",
            "suggestion": "完成测试后注意观察掌握度变化与路径节点的刷新。",
            "status": "locked",
            "order_index": 4,
            "estimated_minutes": 4,
            "knowledge_point": points[2],
            "node_type": "test",
        },
        {
            "title": "进阶节点 1：批处理与内存计算巩固",
            "goal": "基于测试结果继续强化分布式与内存计算的比较理解。",
            "criterion": "完成后续资源浏览与概念对照。",
            "suggestion": "通过资源对比批处理和内存计算的实际差异。",
            "status": "locked",
            "order_index": 5,
            "estimated_minutes": 4,
            "knowledge_point": points[2],
            "node_type": "study",
        },
        {
            "title": "进阶节点 2：课程资源拓展学习",
            "goal": "进入下一阶段资源拓展与知识图谱联动学习。",
            "criterion": "进入资源页与知识图谱页继续学习。",
            "suggestion": "结合知识图谱中的前置关系定位薄弱环节。",
            "status": "locked",
            "order_index": 6,
            "estimated_minutes": 4,
            "knowledge_point": points[1],
            "node_type": "study",
        },
    ]

    stage_feedback = _build_stage_feedback_payload(points)

    kept_titles = {spec["title"] for spec in node_specs}
    path.nodes.exclude(title__in=kept_titles).delete()

    node_map: dict[int, PathNode] = {}
    progress_map: dict[int, NodeProgress] = {}
    for spec in node_specs:
        node, _ = PathNode.objects.update_or_create(
            path=path,
            title=spec["title"],
            defaults={
                "goal": spec["goal"],
                "criterion": spec["criterion"],
                "suggestion": spec["suggestion"],
                "status": spec["status"],
                "order_index": spec["order_index"],
                "estimated_minutes": spec["estimated_minutes"],
                "knowledge_point": spec["knowledge_point"],
                "node_type": spec["node_type"],
                "exam": stage_exam if spec["node_type"] == "test" else None,
            },
        )
        progress_defaults: dict[str, object] = {
            "completed_resources": [],
            "completed_exams": [],
            "mastery_before": None,
            "mastery_after": None,
            "extra_data": {"defense_demo_preset": True},
        }
        progress, _ = NodeProgress.objects.update_or_create(
            node=node,
            user=student,
            defaults=progress_defaults,
        )
        extra_data = dict(progress.extra_data or {})
        extra_data["defense_demo_preset"] = True
        if spec["node_type"] == "study":
            extra_data["preset_resources"] = {
                "internal_resources": resource_payloads.get(spec["knowledge_point"].name, []),
                "external_resources": [],
            }
        if spec["node_type"] == "test":
            extra_data["preset_stage_test"] = stage_feedback
        progress.extra_data = extra_data
        progress.save(update_fields=["extra_data", "updated_at"])
        node_map[spec["order_index"]] = node
        progress_map[spec["order_index"]] = progress

    if not isinstance(completed_stage_result, dict):
        return

    completed_status_map = {
        1: "completed",
        2: "completed",
        3: "completed",
        4: "completed",
        5: "active",
        6: "locked",
    }
    for order_index, status in completed_status_map.items():
        node = node_map.get(order_index)
        if not node or node.status == status:
            continue
        node.status = status
        node.save(update_fields=["status"])

    mastery_changes = completed_stage_result.get("mastery_changes")
    mastery_before_map: dict[int, float] = {}
    mastery_after_map: dict[int, float] = {}
    if isinstance(mastery_changes, list):
        for item in mastery_changes:
            if not isinstance(item, dict):
                continue
            point_id = item.get("knowledge_point_id")
            mastery_before = item.get("mastery_before")
            mastery_after = item.get("mastery_after")
            if isinstance(point_id, int) and isinstance(mastery_before, int | float):
                mastery_before_map[point_id] = float(mastery_before)
            if isinstance(point_id, int) and isinstance(mastery_after, int | float):
                mastery_after_map[point_id] = float(mastery_after)

    for order_index in (1, 2, 3):
        node = node_map.get(order_index)
        progress = progress_map.get(order_index)
        if not node or not progress or not node.knowledge_point:
            continue
        payloads = resource_payloads.get(node.knowledge_point.name, [])
        progress.completed_resources = [
            str(payload["resource_id"])
            for payload in payloads
            if isinstance(payload, dict) and isinstance(payload.get("resource_id"), int)
        ]
        point_id = node.knowledge_point_id
        if point_id in mastery_before_map:
            progress.mastery_before = mastery_before_map[point_id]
        if point_id in mastery_after_map:
            progress.mastery_after = mastery_after_map[point_id]
        progress.save(
            update_fields=[
                "completed_resources",
                "mastery_before",
                "mastery_after",
                "updated_at",
            ]
        )

    stage_progress = progress_map.get(4)
    if stage_progress:
        completed_exams = list(stage_progress.completed_exams or [])
        if stage_exam.id not in completed_exams:
            completed_exams.append(stage_exam.id)
        stage_progress.completed_exams = completed_exams
        average_before = _average_snapshot(mastery_before_map)
        average_after = _average_snapshot(mastery_after_map)
        if average_before is not None:
            stage_progress.mastery_before = average_before
        if average_after is not None:
            stage_progress.mastery_after = average_after
        extra_data = dict(stage_progress.extra_data or {})
        extra_data["stage_test_result"] = completed_stage_result
        stage_progress.extra_data = extra_data
        stage_progress.save(
            update_fields=[
                "completed_exams",
                "mastery_before",
                "mastery_after",
                "extra_data",
                "updated_at",
            ]
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
