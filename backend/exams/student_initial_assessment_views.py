"""学生端初始评测视图。"""
from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from common.responses import error_response, success_response
from common.utils import validate_course_exists

from .student_initial_assessment_support import (
    apply_kt_initial_mastery,
    build_initial_assessment_result,
    load_answered_questions,
    mark_initial_assessment_done,
    parse_answer_question_ids,
    score_initial_assessment,
    select_initial_questions,
    serialize_initial_questions,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initial_assessment_start(request: Request) -> Response:
    """开始初始评测（随机抽题）。"""
    course_id = request.data.get("course_id")
    if not course_id:
        return error_response(msg="缺少课程ID")

    course = validate_course_exists(course_id)
    if course is None:
        return error_response(msg="课程不存在", code=404)

    selection = select_initial_questions(course)
    if not selection.questions:
        return error_response(msg="课程暂无初始评测题目")

    return success_response(data={
        "course_id": course.id,
        "questions": serialize_initial_questions(selection.questions),
        "count": selection.count,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initial_assessment_submit(request: Request) -> Response:
    """提交初始评测。"""
    course_id = request.data.get("course_id")
    answers = request.data.get("answers", {})
    if not course_id or not answers:
        return error_response(msg="缺少必填参数")
    if not isinstance(answers, dict):
        return error_response(msg="答案格式错误，应为字典格式")

    course = validate_course_exists(course_id)
    if course is None:
        return error_response(msg="课程不存在", code=404)

    try:
        question_ids = parse_answer_question_ids(answers)
    except ValueError:
        return error_response(msg="题目ID格式错误")

    score = score_initial_assessment(
        user=request.user,
        course=course,
        questions=load_answered_questions(question_ids),
        answers=answers,
    )
    apply_kt_initial_mastery(
        user=request.user,
        course=course,
        knowledge_point_stats=score.knowledge_point_stats,
        knowledge_mastery=score.knowledge_mastery,
    )
    mark_initial_assessment_done(user=request.user, course=course)
    return success_response(data=build_initial_assessment_result(score), msg="初始评测完成")
