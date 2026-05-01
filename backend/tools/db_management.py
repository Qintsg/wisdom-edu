"""数据库管理功能。

包含数据库检查、Django系统检查、清空数据库、创建测试数据、PostgreSQL初始化等功能。
"""

from typing import TYPE_CHECKING, Any, List, Optional, cast

from tools.common import User
from tools.testing import CheckResult, _load_testdata, _print_checks, _status_flag

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


def db_check(as_json: bool = False):
    """执行数据库关键数据存在性检查。

    检查课程、知识点、题库、问卷、资源等核心业务数据是否存在。

    Args:
        as_json (bool): 是否以 JSON 格式输出结果
    """
    from assessments.models import Question, SurveyQuestion
    from courses.models import Course
    from knowledge.models import KnowledgePoint, Resource

    checks = [
        CheckResult("课程存在性", Course.objects.count() > 0, f"count={Course.objects.count()}"),
        CheckResult("知识点存在性", KnowledgePoint.objects.count() > 0, f"count={KnowledgePoint.objects.count()}"),
        CheckResult("题库存在性", Question.objects.count() > 0, f"count={Question.objects.count()}"),
        CheckResult("问卷存在性", SurveyQuestion.objects.count() > 0, f"count={SurveyQuestion.objects.count()}"),
        CheckResult("资源存在性", Resource.objects.count() > 0, f"count={Resource.objects.count()}"),
    ]
    _print_checks(checks, as_json=as_json)


def django_check(as_json: bool = False):
    """执行 Django 系统检查。

    Args:
        as_json (bool): 是否以 JSON 格式输出结果
    """
    from django.core.management import call_command

    checks: List[CheckResult] = []
    try:
        call_command("check")
        checks.append(CheckResult("Django系统检查", True, "ok"))
    except Exception as error:
        checks.append(CheckResult("Django系统检查", False, str(error)))
    _print_checks(checks, as_json=as_json)


def clear_database(model_names: Optional[List[str]] = None):
    """清空数据库中的核心业务数据。

    按照正确的依赖顺序删除数据，避免外键约束错误。

    Args:
        model_names (Optional[List[str]]): 要清空的模型名称列表，None 表示全部清空
    """
    from django.db import transaction

    from assessments.models import (
        AbilityScore,
        Assessment,
        AssessmentQuestion,
        AssessmentStatus,
        Question,
        SurveyQuestion,
    )
    from courses.models import Class, ClassCourse, Course, Enrollment
    from exams.models import Exam, ExamQuestion, ExamSubmission, FeedbackReport
    from knowledge.models import (
        KnowledgeMastery,
        KnowledgePoint,
        KnowledgeRelation,
        ProfileSummary,
        Resource,
    )
    from learning.models import LearningPath, NodeProgress, PathNode
    from users.models import ActivationCode, ClassInvitation, HabitPreference

    all_models = [
        NodeProgress,
        FeedbackReport,
        ExamSubmission,
        PathNode,
        LearningPath,
        ProfileSummary,
        KnowledgeMastery,
        AbilityScore,
        AssessmentStatus,
        ExamQuestion,
        Exam,
        AssessmentQuestion,
        Assessment,
        Question,
        SurveyQuestion,
        Resource,
        KnowledgeRelation,
        KnowledgePoint,
        HabitPreference,
        ActivationCode,
        ClassInvitation,
        Enrollment,
        ClassCourse,
        Class,
        Course,
        User,
    ]

    model_map = {model.__name__: model for model in all_models}

    if model_names:
        to_clear = [model_map[name] for name in model_names if name in model_map]
        invalid = [name for name in model_names if name not in model_map]
        if invalid:
            print(f"  {_status_flag(False)} 无效模型名: {', '.join(invalid)}")
    else:
        to_clear = all_models

    total = 0
    with transaction.atomic():
        for model in to_clear:
            count = model.objects.count()
            model.objects.all().delete()
            total += count
            print(f"  {_status_flag(True)} 已删除 {model.__name__}: {count}")
    print(f"数据库清理完成，共删除 {total} 条记录。")


def _preset_student1_demo_data(
    student: Optional["UserModel"],
    course: "Any",
) -> None:
    """为 student1 预置更贴近真实的“刚完成初始评测”状态。"""
    if not student or not course:
        return

    from collections import defaultdict
    from decimal import Decimal

    from assessments.models import (
        AbilityScore,
        Assessment,
        AssessmentQuestion,
        AssessmentResult,
        AssessmentStatus,
        AnswerHistory,
        Question,
    )
    from exams.models import FeedbackReport
    from knowledge.models import KnowledgeMastery, KnowledgePoint, ProfileSummary, Resource
    from learning.models import LearningPath, NodeProgress, PathNode
    from learning.path_rules import apply_prerequisite_caps
    from common.utils import check_answer, extract_answer_value, serialize_answer_payload
    from users.models import HabitPreference

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

    def _build_student_answer_value(question: Question, force_correct: bool) -> object:
        """
        按题型生成可用于预置答题历史的原始答案值。
        :param question: 课程初始评测题。
        :param force_correct: 是否返回正确答案。
        :return: 与真实提交一致的原始答案值。
        """
        correct_raw = extract_answer_value(question.answer)
        if force_correct:
            return correct_raw

        option_labels = [
            str(option.get("label"))
            for option in (question.options or [])
            if isinstance(option, dict) and option.get("label") is not None
        ]
        if question.question_type == "multiple_choice":
            correct_values = (
                [str(value) for value in correct_raw]
                if isinstance(correct_raw, list)
                else [str(correct_raw)]
            )
            fallback = next(
                (label for label in option_labels if label not in correct_values),
                "A",
            )
            return [correct_values[0], fallback] if correct_values else [fallback]
        if question.question_type == "true_false":
            normalized = str(correct_raw).strip().lower()
            return "false" if normalized in {"true", "a", "正确", "对"} else "true"
        return next(
            (label for label in option_labels if label != str(correct_raw)),
            "B" if str(correct_raw).upper() != "B" else "A",
        )

    _reset_course_demo_state(student, course)

    AssessmentStatus.objects.update_or_create(
        user=student,
        course=course,
        defaults={
            "ability_done": True,
            "habit_done": True,
            "knowledge_done": True,
        },
    )

    HabitPreference.objects.update_or_create(
        user=student,
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
            "preferences": {
                "preferred_resource": "video",
                "preferred_study_time": "evening",
                "study_pace": "adaptive",
                "daily_goal_minutes": 45,
                "weekly_goal_days": 5,
            },
        },
    )

    AbilityScore.objects.update_or_create(
        user=student,
        course=course,
        defaults={
            "scores": {
                "逻辑推理": 78,
                "抽象思维": 74,
                "信息整合": 76,
                "学习迁移": 72,
            }
        },
    )

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
    mastery_payload = [
        {
            "point_id": point.id,
            "point_name": point.name,
            "mastery_rate": round(float(mastery_map.get(point.id, INITIAL_MASTERY_PRIOR_MEAN)), 4),
        }
        for point in points
    ]

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
            "summary": (
                "该学生刚完成课程初始评测，当前仅对少量核心知识点建立了基础判断，"
                "整体仍处于学习起步阶段，大部分知识点掌握度维持在保守基线附近。"
            ),
            "weakness": weakest_text,
            "suggestion": (
                "建议先围绕前三个核心知识点完成路径首节点学习，"
                "再通过课程资源逐步把 25% 基线知识点拉升到可稳定应用的水平。"
            ),
        },
    )

    FeedbackReport.objects.update_or_create(
        user=student,
        source="assessment",
        assessment_result=assessment_result,
        defaults={
            "status": "completed",
            "overview": {
                "score": round(float(total_score), 2),
                "total_score": round(float(max_possible), 2),
                "correct_count": correct_count,
                "total_count": len(selected_questions),
                "accuracy": round(correct_count / max(len(selected_questions), 1) * 100, 1),
                "summary": f"已完成 {len(selected_questions)} 道初始评测题，系统已基于完整题组生成掌握度画像。",
                "knowledge_gaps": weakest_points,
            },
            "analysis": f"当前画像基于课程资源示例中的 {len(selected_questions)} 道初始评测题生成，系统已识别出薄弱知识点，但仍需要通过后续学习行为逐步校准掌握度。",
            "recommendations": [
                "优先学习路径中的首个激活节点，巩固最基础的核心概念。",
                "先补足 25% 基线知识点对应的课程资源，再进入后续练习。",
            ],
            "next_tasks": [
                "完成当前激活的首个学习节点。",
                "学习后重新查看画像与掌握度变化。",
            ],
            "conclusion": "当前结果适合作为“刚完成初始评测”的真实起点数据，不代表稳定掌握水平。",
        },
    )

    path, _ = LearningPath.objects.update_or_create(
        user=student,
        course=course,
        defaults={
            "ai_reason": (
                f"你刚完成 {len(selected_questions)} 道初始评测题，系统已按完整题组估计知识点掌握度。"
                "建议先从概念复盘开始，逐步推进到 Hadoop 与 Spark 的核心内容。"
            ),
        },
    )
    path.nodes.all().delete()
    node_configs = [
        {
            "title": "大数据概念基础复盘",
            "goal": "建立 4V 特征与典型应用场景的基础认知",
            "status": "active",
            "estimated_minutes": 20,
        },
        {
            "title": "Hadoop 生态结构入门",
            "goal": "认识 HDFS、YARN 与 MapReduce 的职责划分",
            "status": "locked",
            "estimated_minutes": 35,
        },
        {
            "title": "Spark 计算模型预习",
            "goal": "理解 Spark 的核心抽象与内存计算优势",
            "status": "locked",
            "estimated_minutes": 35,
        },
    ]
    for order, node_cfg in enumerate(node_configs, start=1):
        point = points[order - 1] if order <= len(points) else points[-1]
        node = PathNode.objects.create(
            path=path,
            knowledge_point=point,
            title=node_cfg["title"],
            goal=node_cfg["goal"],
            criterion="完成节点学习并掌握对应知识点的核心概念。",
            suggestion="建议先阅读对应课程资源，再用错题与知识图谱进行回顾。",
            status=node_cfg["status"],
            order_index=order,
            node_type="study",
            estimated_minutes=node_cfg["estimated_minutes"],
        )
        linked_resource_ids = [
            resource.id
            for resource in resources
            if resource.knowledge_points.filter(id=point.id).exists()
        ]
        if linked_resource_ids:
            node.resources.set(linked_resource_ids)
        NodeProgress.objects.update_or_create(
            node=node,
            user=student,
            defaults={
                "completed_resources": [],
                "completed_exams": [],
                "mastery_before": Decimal(
                    str(round(float(mastery_map.get(point.id, INITIAL_MASTERY_PRIOR_MEAN)), 4))
                ),
                "mastery_after": None,
                "extra_data": {
                    "testdata_preset": True,
                    "preset_stage": "initial_assessment_completed",
                },
            },
        )

    print(
        f"  {_status_flag(True)} student1 演示数据预置完成: "
        f"初始评测={total_score}/{max_possible}, 路径节点={len(node_configs)}, 基线知识点={max(len(points) - len(point_stats), 0)}"
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


def create_test_data():
    """从 testdata.json5 创建基础测试数据（用户、课程、班级）。

    知识点、题库、资源等课程数据需通过 `bootstrap-course-assets` 命令导入。
    """
    from django.db import transaction

    from assessments.models import Question, SurveyQuestion
    from common.neo4j_service import neo4j_service
    from courses.models import Class, ClassCourse, Course, Enrollment
    from knowledge.models import KnowledgePoint, KnowledgeRelation, Resource
    from tools.rag_index import refresh_rag_corpus
    from users.models import ActivationCode, ClassInvitation, UserCourseContext

    data = _load_testdata()
    if not data:
        return

    print("开始创建测试数据...")

    def _seed_course_content(
        target_course: Course,
        course_teacher: "UserModel",
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
                    "url": resource_cfg.get("url") or f"https://example.com/{int(target_course.pk)}/{index}",
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
                # Django 运行时为多对多字段提供 set()，这里显式收窄以满足静态分析。
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
                # Django 运行时为多对多字段提供 set()，这里显式收窄以满足静态分析。
                cast(Any, question.knowledge_points).set(linked_points)

    def _create_user(username: str, password: str, **kwargs) -> "UserModel":
        user, _ = User.objects.update_or_create(username=username, defaults=kwargs)
        user.set_password(password)
        user.save()
        return cast("UserModel", user)

    with transaction.atomic():
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

        teachers: List["UserModel"] = []
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

        students: List["UserModel"] = []
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

        for activation_code in data.get("activation_codes", []):
            ActivationCode.objects.update_or_create(
                code=activation_code["code"],
                defaults={
                    "code_type": activation_code["code_type"],
                    "created_by": admin_user,
                    "remark": activation_code.get("remark", ""),
                },
            )

        courses: List[Course] = []
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

        classes: List[Class] = []
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

        # 确保所有学生都加入包含"大数据技术与应用"的班级，
        # 同时为 student1 预置演示用学习数据。
        big_data_course = next(
            (c for c in courses if c.name == "大数据技术与应用"),
            courses[0] if courses else None,
        )
        big_data_class = next(
            (
                cls
                for cls in classes
                if ClassCourse.objects.filter(class_obj=cls, course=big_data_course).exists()
            ),
            classes[0] if classes else None,
        ) if big_data_course and classes else None

        if classes:
            for index, student in enumerate(students):
                # 先按均匀分布加入班级
                target_class = classes[index % len(classes)]
                Enrollment.objects.get_or_create(user=student, class_obj=target_class, role="student")

                # 确保也加入大数据班级
                if big_data_class and target_class != big_data_class:
                    Enrollment.objects.get_or_create(
                        user=student, class_obj=big_data_class, role="student"
                    )

                # 所有学生的默认课程上下文设为大数据
                UserCourseContext.objects.update_or_create(
                    user=student,
                    defaults={
                        "current_class": big_data_class or target_class,
                        "current_course": big_data_course,
                    },
                )

            # student1 额外加入所有班级
            demo_student = next(
                (student for student in students if student.username == "student1"),
                None,
            )
            if demo_student:
                for class_obj in classes:
                    Enrollment.objects.get_or_create(
                        user=demo_student,
                        class_obj=class_obj,
                        role="student",
                    )

        # 为 student1 预置大数据课程的初始评测、学习路径等演示数据
        if big_data_course and students:
            _preset_student1_demo_data(
                next((s for s in students if s.username == "student1"), None),
                big_data_course,
            )

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

        # 注意：不再在测试数据中预创建 HabitPreference，
        # 因为它会导致 get_assessment_status 误判习惯问卷已完成。
        # HabitPreference 只应在学生实际提交习惯问卷后创建。

        # 问卷题目（通常为空，由后端 API 自动创建默认题目）
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

    print("测试数据创建完成。")
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
            print(
                f"  {_status_flag(False)} GraphRAG 索引构建失败: {course.name} ({error})"
            )

    if courses:
        print("\n提示: 课程资源（知识图谱、题库、PPT等）需通过导入命令导入：")
        print("  python tools.py bootstrap-course-assets --course-name 大数据技术与应用")


def pg_bootstrap(
    run_migrate: bool = True,
    clear_first: bool = True,
    import_course_assets: bool = True,
    course_name: str | None = None,
):
    """初始化 PostgreSQL 测试环境。

    默认执行：迁移 → 清空 → 创建基础数据 → 导入课程资源/同步 Neo4j/刷新 GraphRAG
    → 重新修正 student1 的真实初测态预置。

    Args:
        run_migrate (bool): 是否执行数据库迁移
        clear_first (bool): 是否先清空数据库
        import_course_assets (bool): 是否额外导入课程资源并同步图谱
        course_name (str | None): 指定需要优先重建 student1 预置的课程名
    """
    from django.core.management import call_command
    from tools.bootstrap import import_course_resources

    print("开始初始化 PostgreSQL 测试样例...")

    if run_migrate:
        call_command("migrate")
        print(f"  {_status_flag(True)} 迁移完成")

    if clear_first:
        clear_database()

    create_test_data()

    if import_course_assets:
        target_course_name = (course_name or "").strip() or None
        try:
            import_course_resources(target_course_name)
        except Exception as error:
            print(f"  {_status_flag(False)} 课程资源自动导入失败: {error}")

        preset_student1_demo_course_state(
            target_course_name or DEFAULT_BOOTSTRAP_COURSE_NAME
        )

    print("PostgreSQL 测试样例初始化完成。")
