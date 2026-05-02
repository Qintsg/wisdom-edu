"""
学习习惯问卷视图。

处理全局或课程级习惯问卷题目获取，并写入用户学习偏好。
"""
from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping

from django.db import DatabaseError, transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.permissions import IsStudent
from common.responses import error_response, success_response
from courses.models import Enrollment
from users.models import HabitPreference, User

from .assessment_helpers import HABIT_SURVEY_FIXED_ID, get_authenticated_user
from .habit_survey_defaults import DEFAULT_HABIT_QUESTIONS
from .models import AssessmentStatus, SurveyQuestion


logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_habit_survey(request: Request) -> Response:
    """
    获取学习习惯问卷题目。
    GET /api/assessments/initial/habit
    """
    course_id = request.query_params.get("course_id")
    try:
        questions = _get_or_create_habit_questions(course_id)
    except DatabaseError as exc:
        logger.exception("习惯问卷题目获取失败: %s", exc)
        return error_response(msg="问卷题目获取失败", code=500)

    return success_response(
        data={
            "survey_id": HABIT_SURVEY_FIXED_ID,
            "title": "学习习惯调查问卷",
            "questions": _serialize_habit_questions(questions),
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def submit_habit_survey(request: Request) -> Response:
    """
    提交学习习惯问卷答案。
    POST /api/student/assessments/initial/habit
    """
    course_id = request.data.get("course_id")
    response_payload = request.data.get("responses", [])
    if not response_payload:
        return error_response(msg="缺少问卷回答")

    user = get_authenticated_user(request)
    try:
        field_map, extra_preferences = _map_habit_responses(response_payload)
        all_preferences = {**field_map, **extra_preferences}
        with transaction.atomic():
            _save_habit_preference(user, field_map, all_preferences)
            _mark_habit_assessment_done(user, course_id)

        return success_response(
            data={"preferences": all_preferences, "completed": True},
            msg="问卷提交成功",
        )
    except Exception as exc:
        logger.exception("习惯问卷提交失败: %s", exc)
        return error_response(msg=f"问卷提交失败: {str(exc)}", code=500)


def _get_or_create_habit_questions(course_id: str | None) -> list[SurveyQuestion]:
    """读取习惯问卷题目；首次部署无数据时写入全局默认题。"""
    habit_question_qs = _habit_question_queryset(course_id)
    if not habit_question_qs.exists():
        _seed_default_habit_questions()
        habit_question_qs = SurveyQuestion.objects.filter(
            survey_type="habit", is_global=True
        ).order_by("order")
    return list(habit_question_qs)


def _seed_default_habit_questions() -> None:
    """幂等写入内置全局问卷题，避免并发初始化产生异常。"""
    with transaction.atomic():
        for question_payload in DEFAULT_HABIT_QUESTIONS:
            SurveyQuestion.objects.get_or_create(
                survey_type="habit",
                is_global=True,
                order=question_payload["order"],
                text=question_payload["text"],
                defaults={
                    "question_type": question_payload["question_type"],
                    "options": question_payload["options"],
                },
            )


def _habit_question_queryset(course_id: str | None):
    """构造全局题和课程级题的联合查询。"""
    return (
        SurveyQuestion.objects.filter(survey_type="habit", is_global=True)
        | SurveyQuestion.objects.filter(survey_type="habit", course_id=course_id)
    ).order_by("order")


def _serialize_habit_questions(
    questions: Iterable[SurveyQuestion],
) -> list[dict[str, object]]:
    """序列化前端问卷渲染需要的最小字段。"""
    return [
        {
            "question_id": question.id,
            "text": question.text,
            "options": question.options,
            "type": question.question_type,
        }
        for question in questions
    ]


def _map_habit_responses(
    response_payload: object,
) -> tuple[dict[str, object], dict[str, object]]:
    """把问卷答案映射到 HabitPreference 字段和扩展偏好。"""
    field_map: dict[str, object] = {}
    extra_preferences: dict[str, object] = {}

    for response in _normalize_response_items(response_payload):
        question_id = response.get("question_id")
        answer = response.get("answer")
        question = SurveyQuestion.objects.filter(id=question_id).first()
        if question is None:
            continue

        target_field = _resolve_habit_field(question.text)
        if target_field == "difficulty_strategy":
            extra_preferences[target_field] = answer
        elif target_field:
            field_map[target_field] = _normalize_habit_answer(target_field, answer)
        else:
            extra_preferences[f"q_{question_id}"] = answer

    return field_map, extra_preferences


def _normalize_response_items(
    response_payload: object,
) -> list[Mapping[str, object]]:
    """兼容历史 dict 与新列表两种提交结构。"""
    if isinstance(response_payload, Mapping):
        return [
            {"question_id": question_id, "answer": answer}
            for question_id, answer in response_payload.items()
        ]
    if not isinstance(response_payload, list):
        return []
    return [item for item in response_payload if isinstance(item, Mapping)]


def _resolve_habit_field(question_text: object) -> str:
    """根据题干语义定位偏好字段。"""
    text = str(question_text or "")
    if "形式" in text or "获取新知识" in text:
        return "preferred_resource"
    if "效率最高" in text or "哪段时间" in text:
        return "preferred_study_time"
    if "学习节奏" in text:
        return "study_pace"
    if "花多少时间" in text or ("每天" in text and "时间" in text):
        return "daily_goal_minutes"
    if "每周" in text and "几天" in text:
        return "weekly_goal_days"
    if "复习频率" in text or "复习" in text:
        return "review_frequency"
    if "学习风格" in text:
        return "learning_style"
    if "挑战" in text:
        return "accept_challenge"
    if "困难" in text:
        return "difficulty_strategy"
    return ""


def _normalize_habit_answer(field_name: str, answer: object) -> object:
    """把问卷原始答案转成模型字段需要的类型。"""
    answer_text = str(answer or "")
    if field_name == "daily_goal_minutes":
        return int(answer_text) if answer_text.isdigit() else 60
    if field_name == "weekly_goal_days":
        return int(answer_text) if answer_text.isdigit() else 5
    if field_name == "accept_challenge":
        return answer in ("yes", "moderate")
    return answer


def _save_habit_preference(
    user: User,
    field_map: Mapping[str, object],
    all_preferences: Mapping[str, object],
) -> None:
    """保存用户学习偏好，同时保持历史默认值兼容。"""
    daily_goal_minutes = field_map.get("daily_goal_minutes", 60)
    HabitPreference.objects.update_or_create(
        user=user,
        defaults={
            "preferred_resource": field_map.get("preferred_resource", "video"),
            "preferred_study_time": field_map.get("preferred_study_time", "evening"),
            "study_pace": field_map.get("study_pace", "moderate"),
            "study_duration": _study_duration_bucket(daily_goal_minutes),
            "review_frequency": field_map.get("review_frequency", "weekly"),
            "learning_style": field_map.get("learning_style", "visual"),
            "accept_challenge": field_map.get("accept_challenge", True),
            "daily_goal_minutes": daily_goal_minutes,
            "weekly_goal_days": field_map.get("weekly_goal_days", 5),
            "preferences": dict(all_preferences),
        },
    )


def _study_duration_bucket(daily_goal_minutes: object) -> str:
    """把分钟目标映射到旧版枚举字段。"""
    return {"30": "short", "60": "medium"}.get(str(daily_goal_minutes), "long")


def _mark_habit_assessment_done(user: User, course_id: object) -> None:
    """按课程或已选课程批量标记习惯问卷完成。"""
    if course_id:
        status, _ = AssessmentStatus.objects.get_or_create(user=user, course_id=course_id)
        status.habit_done = True
        status.save(update_fields=["habit_done"])
        return

    AssessmentStatus.objects.filter(user=user).update(habit_done=True)
    _create_missing_course_assessment_statuses(user)


def _create_missing_course_assessment_statuses(user: User) -> None:
    """为已有选课但尚无状态记录的课程补齐完成状态。"""
    enrolled_course_ids = set(
        Enrollment.objects.filter(user=user).values_list(
            "class_obj__class_courses__course_id", flat=True
        )
    )
    existing_course_ids = set(
        AssessmentStatus.objects.filter(user=user).values_list("course_id", flat=True)
    )
    AssessmentStatus.objects.bulk_create(
        [
            AssessmentStatus(user=user, course_id=course_id, habit_done=True)
            for course_id in enrolled_course_ids - existing_course_ids
            if course_id
        ]
    )
