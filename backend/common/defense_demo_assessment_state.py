from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from assessments.models import (
    AnswerHistory,
    Question,
)
from courses.models import Course
from exams.models import Exam, ExamQuestion
from knowledge.models import KnowledgePoint
from users.models import User

from common.defense_demo_assessment_questions import (
    _build_assessment_report_payload,
    _ensure_demo_assessment_questions,
)
from common.defense_demo_assessment_support import (
    _build_demo_mastery_map,
    _ensure_demo_knowledge_assessment,
    _load_demo_assessment_defaults,
    _persist_demo_mastery_records,
    _refresh_demo_answer_histories,
    _seed_demo_profile_state,
    _upsert_demo_assessment_feedback,
    _upsert_demo_assessment_result,
)
from common.defense_demo_progress import _question_options
from common.utils import extract_answer_value, serialize_answer_payload

# 维护意图：预置学生的初始评测、画像和掌握度状态，数据结构与真实提交流程完全一致。
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
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
    defaults = _load_demo_assessment_defaults(student.username)
    _seed_demo_profile_state(course, student, defaults)

    # ---- 创建或复用评测题目（优先使用课程资源导入题） ----
    questions = _ensure_demo_assessment_questions(course, teacher, points)

    # ---- 构建答题明细（题量变化时自动生成错题分布） ----
    raw_answers, question_details, is_correct_flags = _build_assessment_report_payload(
        questions,
        defaults.planned_answers,
    )

    # ---- 创建 Assessment 及 AssessmentQuestion 关联 ----
    knowledge_assessment = _ensure_demo_knowledge_assessment(course, questions)

    # ---- 逐题创建 AnswerHistory（匹配 submit_knowledge_assessment） ----
    _refresh_demo_answer_histories(course, student, questions, raw_answers, is_correct_flags)

    # ---- 贝叶斯掌握度基线（匹配 _calculate_initial_mastery_baseline） ----
    # 公式: mastery = (correct + 4.0 * 0.25) / (total + 4.0), cap [0, 0.85]
    mastery_map = _build_demo_mastery_map(questions, is_correct_flags)
    _persist_demo_mastery_records(course, student, points, mastery_map)

    # ---- AssessmentResult（匹配 submit_knowledge_assessment 产出） ----
    assessment_result = _upsert_demo_assessment_result(
        course,
        student,
        knowledge_assessment,
        questions,
        points,
        raw_answers,
        question_details,
        is_correct_flags,
        mastery_map,
    )

    # ---- FeedbackReport（匹配 _async_generate_after_assessment 产出） ----
    _upsert_demo_assessment_feedback(
        student,
        assessment_result=assessment_result,
        points=points,
        mastery_map=mastery_map,
        is_correct_flags=is_correct_flags,
        questions=questions,
        defaults=defaults,
    )


# 维护意图：构造更贴近真实提交的学生答案载荷。
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
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


# 维护意图：补充更接近真实学习过程的练习与阶段测试轨迹。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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
