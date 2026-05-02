"""学生端初始评测视图。"""
from __future__ import annotations

import logging
import random
from collections import defaultdict
from decimal import InvalidOperation

from django.db import DatabaseError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.logging_utils import build_log_message
from common.responses import error_response, success_response
from common.utils import check_answer, extract_answer_value, validate_course_exists
from assessments.models import AnswerHistory, AssessmentStatus, Question
from knowledge.models import KnowledgeMastery


logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initial_assessment_start(request):
    """开始初始评测（随机抽题）。"""
    course_id = request.data.get("course_id")
    if not course_id:
        return error_response(msg="缺少课程ID")

    course = validate_course_exists(course_id)
    if course is None:
        return error_response(msg="课程不存在", code=404)

    questions = list(Question.objects.filter(course=course, for_initial_assessment=True, is_visible=True).prefetch_related("knowledge_points"))
    if not questions:
        return error_response(msg="课程暂无初始评测题目")

    count = min(course.initial_assessment_count, len(questions))
    selected = random.sample(questions, count)
    return success_response(data={
        "course_id": course.id,
        "questions": [{
            "question_id": question.id,
            "content": question.content,
            "options": question.options,
            "type": question.question_type,
            "score": float(question.score),
        } for question in selected],
        "count": count,
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initial_assessment_submit(request):
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

    user = request.user
    try:
        question_ids = [int(question_id) for question_id in answers.keys()]
    except (ValueError, TypeError):
        return error_response(msg="题目ID格式错误")
    questions = Question.objects.filter(id__in=question_ids).prefetch_related("knowledge_points")
    total_score = 0
    correct_count = 0
    knowledge_point_stats = defaultdict(lambda: {"correct": 0, "total": 0})

    for question in questions:
        question_id = str(question.id)
        student_answer = answers.get(question_id)
        correct_answer = extract_answer_value(question.answer)
        is_correct = check_answer(question.question_type, student_answer, question.answer)
        score = float(question.score) if is_correct else 0
        total_score += score
        if is_correct:
            correct_count += 1

        first_point = question.knowledge_points.first()
        AnswerHistory.objects.create(
            user=user,
            course=course,
            question=question,
            knowledge_point=first_point,
            student_answer={"answer": student_answer},
            correct_answer={"answer": correct_answer},
            is_correct=is_correct,
            score=score,
            source="initial",
        )
        for knowledge_point in question.knowledge_points.all():
            knowledge_point_stats[knowledge_point.id]["total"] += 1
            if is_correct:
                knowledge_point_stats[knowledge_point.id]["correct"] += 1

    knowledge_mastery = {}
    for knowledge_point_id, stats in knowledge_point_stats.items():
        mastery_rate = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        KnowledgeMastery.objects.update_or_create(
            user=user,
            course=course,
            knowledge_point_id=knowledge_point_id,
            defaults={"mastery_rate": mastery_rate},
        )
        knowledge_mastery[knowledge_point_id] = mastery_rate

    try:
        from ai_services.services.kt_service import kt_service
        all_history = list(AnswerHistory.objects.filter(user=user, course=course).order_by("answered_at").values("question_id", "knowledge_point_id", "is_correct"))
        kt_history = [{"question_id": item["question_id"], "knowledge_point_id": item["knowledge_point_id"], "correct": 1 if item["is_correct"] else 0} for item in all_history]
        knowledge_point_ids = list(knowledge_point_stats.keys())
        if kt_history and knowledge_point_ids:
            kt_result = kt_service.predict_mastery(user_id=user.id, course_id=course.id, answer_history=kt_history, knowledge_points=knowledge_point_ids)
            kt_predictions = kt_result.get("predictions", {})
            for knowledge_point_id, rate in kt_predictions.items():
                try:
                    KnowledgeMastery.objects.update_or_create(
                        user=user,
                        course=course,
                        knowledge_point_id=knowledge_point_id,
                        defaults={"mastery_rate": max(0, min(1, round(float(rate), 4)))},
                    )
                    knowledge_mastery[int(knowledge_point_id)] = round(float(rate), 4)
                except (DatabaseError, InvalidOperation, OverflowError, TypeError, ValueError) as error:
                    logger.warning(build_log_message("kt.initial_assessment.mastery_skip", user_id=user.id, course_id=course.id, knowledge_point_id=knowledge_point_id, error=error))
            logger.info("KT服务调用成功(初始评测): 用户=%s, 答题历史=%d条, 预测结果=%d条", user.id, len(kt_history), len(kt_predictions))
    except Exception as error:
        logger.error("KT服务调用失败(初始评测): 用户=%s, 错误=%s", user.id, error)

    status, _ = AssessmentStatus.objects.get_or_create(user=user, course=course)
    status.knowledge_done = True
    status.save()
    return success_response(data={"score": total_score, "correct_count": correct_count, "total_count": len(questions), "knowledge_mastery": knowledge_mastery}, msg="初始评测完成")
