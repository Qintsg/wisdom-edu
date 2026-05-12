"""
学习能力评测视图。

兼容课程级 Assessment 与全局 SurveyQuestion 两种能力评测模式。
"""
from __future__ import annotations

from collections.abc import Mapping

from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.permissions import IsStudent
from common.responses import error_response, success_response
from courses.models import Enrollment
from users.models import User

from .ability_survey_defaults import DEFAULT_ABILITY_QUESTIONS
from .assessment_helpers import (
    ABILITY_ASSESSMENT_FIXED_ID,
    answer_tokens_for,
    get_authenticated_user,
    normalize_options,
)
from .models import (
    AbilityScore,
    Assessment,
    AssessmentResult,
    AssessmentStatus,
    Question,
    SurveyQuestion,
)


AnswerMap = dict[str, object]
DimensionScores = dict[str, dict[str, float]]


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent])
def retake_ability_assessment(request: Request) -> Response:
    """
    重新进入能力评测（重做入口）。
    GET /api/student/assessments/initial/ability/retake
    """
    return get_ability_assessment(request)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_ability_assessment(request: Request) -> Response:
    """
    获取学习能力评估测评试题。
    GET /api/assessments/initial/ability
    """
    course_id = request.query_params.get("course_id")
    assessment = _get_course_ability_assessment(course_id)
    if assessment is not None:
        return success_response(data=_serialize_assessment_payload(assessment))

    survey_questions = _get_or_create_global_ability_questions()
    return success_response(data=_serialize_survey_payload(survey_questions))


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def submit_ability_assessment(request: Request) -> Response:
    """
    提交学习能力评估测评答案。
    POST /api/student/assessments/initial/ability
    """
    course_id = request.data.get("course_id")
    answer_payload = request.data.get("answers", [])
    if not answer_payload:
        return error_response(msg="缺少答案数据")

    user = get_authenticated_user(request)
    answer_map = _normalize_answer_map(answer_payload)
    assessment = _get_course_ability_assessment(course_id)
    score_result = _score_ability_answers(assessment, answer_map)

    with transaction.atomic():
        resolved_course_id = _save_ability_result(
            user=user,
            course_id=course_id,
            assessment=assessment,
            answer_map=answer_map,
            score_result=score_result,
        )
        _mark_ability_assessment_done(user, resolved_course_id)

    return success_response(
        data={
            "score": round(score_result["score_percentage"], 1),
            "ability_analysis": score_result["ability_analysis"],
            "completed": True,
        },
        msg="测评提交成功",
    )


def _get_course_ability_assessment(course_id: object) -> Assessment | None:
    """查找课程级能力测评，未指定课程时返回 None。"""
    if not course_id:
        return None
    return Assessment.objects.filter(
        course_id=course_id,
        assessment_type="ability",
        is_active=True,
    ).first()


def _get_or_create_global_ability_questions() -> list[SurveyQuestion]:
    """读取全局能力评测题；首次部署无数据时写入默认题。"""
    survey_question_qs = SurveyQuestion.objects.filter(
        survey_type="ability"
    ).order_by("order")
    if not survey_question_qs.exists():
        SurveyQuestion.objects.bulk_create(
            [SurveyQuestion(**question_payload) for question_payload in DEFAULT_ABILITY_QUESTIONS]
        )
        survey_question_qs = SurveyQuestion.objects.filter(
            survey_type="ability"
        ).order_by("order")
    return list(survey_question_qs)


def _serialize_survey_payload(
    survey_questions: list[SurveyQuestion],
) -> dict[str, object]:
    """序列化全局能力问卷响应。"""
    return {
        "assessment_id": ABILITY_ASSESSMENT_FIXED_ID,
        "title": "学习能力评估",
        "questions": [
            {
                "question_id": question.id,
                "content": question.text,
                "options": question.options,
                "type": question.question_type,
                "dimension": question.dimension,
            }
            for question in survey_questions
        ],
    }


def _serialize_assessment_payload(assessment: Assessment) -> dict[str, object]:
    """序列化课程级 Assessment 能力测评响应。"""
    questions = list(assessment.questions.all())
    return {
        "assessment_id": assessment.id,
        "title": assessment.title,
        "questions": [
            {
                "question_id": question.id,
                "content": question.content,
                "options": question.options,
                "type": question.question_type,
            }
            for question in questions
        ],
    }


def _normalize_answer_map(answer_payload: object) -> AnswerMap:
    """兼容 dict 和列表两种答案提交结构。"""
    if isinstance(answer_payload, Mapping):
        return {
            str(question_id): answer
            for question_id, answer in answer_payload.items()
        }
    if not isinstance(answer_payload, list):
        return {}
    return {
        str(answer["question_id"]): answer["answer"]
        for answer in answer_payload
        if isinstance(answer, Mapping)
        and "question_id" in answer
        and "answer" in answer
    }


def _score_ability_answers(
    assessment: Assessment | None,
    answer_map: AnswerMap,
) -> dict[str, object]:
    """根据课程 Assessment 或全局问卷模式计算能力分。"""
    if assessment is not None:
        total_score, total_possible = _score_course_assessment(assessment, answer_map)
        return {
            "total_score": total_score,
            "score_percentage": _percentage(total_score, total_possible),
            "ability_analysis": {},
        }

    total_score, total_possible, dimension_scores = _score_global_survey(answer_map)
    return {
        "total_score": total_score,
        "score_percentage": _percentage(total_score, total_possible),
        "ability_analysis": _build_ability_analysis(dimension_scores),
    }


def _score_course_assessment(
    assessment: Assessment,
    answer_map: AnswerMap,
) -> tuple[float, float]:
    """按标准题目答案计算课程级能力测评分数。"""
    total_score = 0.0
    total_possible = 0.0
    for question in assessment.questions.all():
        total_possible += float(question.score)
        if _is_question_answer_correct(question, answer_map.get(str(question.id))):
            total_score += float(question.score)
    return total_score, total_possible


def _is_question_answer_correct(question: Question, student_answer: object) -> bool:
    """判断课程级题目答案是否正确。"""
    correct_answer = (
        question.answer.get("answer", question.answer)
        if isinstance(question.answer, dict)
        else question.answer
    )
    if question.question_type in ["single_choice", "true_false"]:
        return student_answer == correct_answer
    if question.question_type == "multiple_choice":
        return answer_tokens_for(
            correct_answer,
            question.question_type,
        ) == answer_tokens_for(student_answer, question.question_type)
    return False


def _score_global_survey(answer_map: AnswerMap) -> tuple[float, float, DimensionScores]:
    """按全局问卷选项分值计算能力维度得分。"""
    total_score = 0.0
    total_possible = 0.0
    dimension_scores: DimensionScores = {}
    question_map = {
        str(question.id): question
        for question in SurveyQuestion.objects.filter(id__in=_answer_question_ids(answer_map))
    }

    for question_id, answer_value in answer_map.items():
        survey_question = question_map.get(question_id)
        if survey_question is None:
            continue
        option_score = _survey_option_score(survey_question, answer_value)
        total_score += option_score
        total_possible += 5
        _add_dimension_score(
            dimension_scores,
            survey_question.dimension or "综合",
            option_score,
            5,
        )
    return total_score, total_possible, dimension_scores


def _answer_question_ids(answer_map: AnswerMap) -> list[int]:
    """提取可用于批量查询的问卷题目 ID。"""
    question_ids: list[int] = []
    for question_id in answer_map:
        try:
            question_ids.append(int(question_id))
        except ValueError:
            continue
    return question_ids


def _survey_option_score(
    survey_question: SurveyQuestion,
    answer_value: object,
) -> float:
    """读取全局问卷答案对应的选项分，默认 3 分。"""
    for option in normalize_options(
        survey_question.options,
        survey_question.question_type,
    ):
        if option.get("value") == answer_value:
            return float(option.get("score", 3))
    return 3.0


def _add_dimension_score(
    dimension_scores: DimensionScores,
    dimension: str,
    score: float,
    max_score: float,
) -> None:
    """累计单个能力维度分和满分。"""
    if dimension not in dimension_scores:
        dimension_scores[dimension] = {"total": 0.0, "max": 0.0}
    dimension_scores[dimension]["total"] += score
    dimension_scores[dimension]["max"] += max_score


def _build_ability_analysis(dimension_scores: DimensionScores) -> dict[str, float]:
    """把维度累计分转换为百分制。"""
    return {
        dimension: round(scores["total"] / scores["max"] * 100, 1)
        if scores["max"] > 0
        else 0
        for dimension, scores in dimension_scores.items()
    }


def _percentage(total_score: float, total_possible: float) -> float:
    """计算百分制分数，避免除零。"""
    return total_score / total_possible * 100 if total_possible > 0 else 0


def _save_ability_result(
    *,
    user: User,
    course_id: object,
    assessment: Assessment | None,
    answer_map: AnswerMap,
    score_result: Mapping[str, object],
) -> object:
    """保存能力分析和课程级测评结果，并返回实际课程 ID。"""
    resolved_course_id = course_id or _resolve_default_course_id(user)
    ability_analysis = score_result["ability_analysis"]
    if resolved_course_id:
        AbilityScore.objects.update_or_create(
            user=user,
            course_id=resolved_course_id,
            defaults={"scores": ability_analysis},
        )

    if assessment is not None:
        AssessmentResult.objects.update_or_create(
            user=user,
            assessment=assessment,
            defaults={
                "course_id": course_id,
                "answers": answer_map,
                "score": score_result["total_score"],
                "result_data": {"ability_analysis": ability_analysis},
            },
        )
    return resolved_course_id


def _resolve_default_course_id(user: User) -> object:
    """无 course_id 提交时，沿用旧逻辑取第一个活跃选课课程。"""
    enrollment = Enrollment.objects.filter(user=user).first()
    if not enrollment or not enrollment.class_obj:
        return None

    class_course = enrollment.class_obj.class_courses.filter(is_active=True).first()
    return class_course.course_id if class_course else None


def _mark_ability_assessment_done(user: User, course_id: object) -> None:
    """有课程上下文时标记能力评测完成。"""
    if not course_id:
        return
    status, _ = AssessmentStatus.objects.get_or_create(user=user, course_id=course_id)
    status.ability_done = True
    status.save()
