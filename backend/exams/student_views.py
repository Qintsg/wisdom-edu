#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
考试模块学生接口。
包含考试列表、详情、提交、成绩、反馈报告、初始评测与班级相关接口。
@Project : wisdom-edu
@File : student_views.py
@Author : Qintsg
@Date : 2026-03-23
"""

import logging
from decimal import Decimal, InvalidOperation
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import DatabaseError, models, transaction
from django.db.models import Q

from common.responses import success_response, error_response
from common.permissions import IsStudent
from common.utils import (
    build_answer_display,
    build_normalized_score_map,
    check_answer,
    clean_display_text,
    decorate_question_options,
    extract_answer_value,
    safe_int,
    score_questions,
    serialize_answer_payload,
    validate_course_exists,
)
from common.logging_utils import build_log_message
from .models import Exam, ExamQuestion, ExamSubmission, FeedbackReport
from assessments.models import Question
from knowledge.models import KnowledgeMastery, KnowledgePoint

logger = logging.getLogger(__name__)


def _snapshot_mastery_for_points(
    user, course_id: int, point_ids: list[int]
) -> dict[int, float]:
    """
    读取考试相关知识点的掌握度快照。
    :param user: 当前学生对象。
    :param course_id: 课程 ID。
    :param point_ids: 知识点 ID 列表。
    :return: 掌握度快照映射。
    """

    if not point_ids:
        return {}
    return {
        row.knowledge_point_id: float(row.mastery_rate)
        for row in KnowledgeMastery.objects.filter(
            user=user,
            course_id=course_id,
            knowledge_point_id__in=point_ids,
        )
    }


def _build_mastery_change_payload(
    before_snapshot: dict[int, float], after_snapshot: dict[int, float]
) -> list[dict[str, object]]:
    """
    构建报告可直接消费的掌握度变化明细。
    :param before_snapshot: 变更前掌握度快照。
    :param after_snapshot: 变更后掌握度快照。
    :return: 掌握度变化列表。
    """

    point_ids = sorted(set(before_snapshot.keys()) | set(after_snapshot.keys()))
    point_name_map = {
        row.id: row.name for row in KnowledgePoint.objects.filter(id__in=point_ids)
    }
    return [
        {
            "knowledge_point_id": point_id,
            "knowledge_point_name": point_name_map.get(point_id, f"知识点 {point_id}"),
            "mastery_before": round(float(before_snapshot.get(point_id, 0.0)), 4),
            "mastery_after": round(
                float(after_snapshot.get(point_id, before_snapshot.get(point_id, 0.0))),
                4,
            ),
            "improvement": round(
                float(after_snapshot.get(point_id, before_snapshot.get(point_id, 0.0)))
                - float(before_snapshot.get(point_id, 0.0)),
                4,
            ),
        }
        for point_id in point_ids
    ]


def _resolve_pass_threshold(exam):
    """
    解析考试及格线。
    :param exam: 考试对象。
    :return: 及格阈值分数。
    """
    try:
        threshold = float(Decimal(str(exam.pass_score)))
        if threshold > 0:
            return threshold
    except (TypeError, ValueError, InvalidOperation):
        pass

    try:
        total_score = float(Decimal(str(exam.total_score)))
    except (TypeError, ValueError, InvalidOperation):
        total_score = 100.0

    fallback = max(round(total_score * 0.6, 2), 1.0) if total_score > 0 else 60.0
    logger.warning(
        "检测到无效及格线，已使用兜底阈值: exam_id=%s, pass_score=%s, total_score=%s, fallback=%s",
        getattr(exam, "id", None),
        getattr(exam, "pass_score", None),
        getattr(exam, "total_score", None),
        fallback,
    )
    return fallback


def _build_exam_score_map(exam, exam_questions):
    """
    构建考试题目分值映射。
    :param exam: 考试对象。
    :param exam_questions: 试卷题目关联列表。
    :return: 归一化后的分值映射。
    """
    return build_normalized_score_map(
        [
            (eq.question_id, float(eq.score or getattr(eq.question, "score", 0) or 0))
            for eq in exam_questions
        ],
        target_total_score=float(exam.total_score or 0),
    )


def _build_question_detail(question, student_answer, question_result):
    """
    构建单题回显详情。
    :param question: 题目对象。
    :param student_answer: 学生答案。
    :param question_result: 批改结果字典。
    :return: 单题详情字典。
    """
    correct_answer = question_result.get(
        "correct_answer", extract_answer_value(question.answer)
    )
    is_correct = question_result.get(
        "is_correct",
        check_answer(question.question_type, student_answer, question.answer),
    )
    decorated_options = decorate_question_options(
        getattr(question, "options", None),
        question.question_type,
        student_answer=student_answer,
        correct_answer=correct_answer,
    )
    return {
        "question_id": question.id,
        "content": question.content,
        "question_type": question.question_type,
        "your_answer": student_answer,
        "student_answer": student_answer,
        "correct_answer": correct_answer,
        "student_answer_display": build_answer_display(
            student_answer, question.question_type, decorated_options
        ),
        "correct_answer_display": build_answer_display(
            correct_answer, question.question_type, decorated_options
        ),
        "is_correct": is_correct,
        "analysis": question_result.get("analysis")
        or getattr(question, "analysis", "")
        or "",
        "options": decorated_options,
        "score": question_result.get("earned_score", 0),
        "full_score": question_result.get("assigned_score", 0),
    }


def _build_exam_question_details(exam_questions, answers, question_result_map):
    """
    构建整张试卷的题目详情列表。
    :param exam_questions: 试卷题目关联列表。
    :param answers: 学生答案字典。
    :param question_result_map: 题目批改结果映射。
    :return: 题目详情列表。
    """
    question_details = []
    for eq in exam_questions:
        question = eq.question
        student_answer = (answers or {}).get(str(question.id))
        detail = _build_question_detail(
            question,
            student_answer,
            question_result_map.get(str(question.id), {}),
        )
        question_details.append(detail)
    return question_details


def _normalize_feedback_payload(report, question_details):
    """
    规范化反馈报告载荷。
    :param report: 反馈报告对象。
    :param question_details: 题目详情列表。
    :return: 前端可直接消费的反馈字典。
    """
    overview = dict(report.overview) if isinstance(report.overview, dict) else {}
    raw_analysis = report.analysis

    summary = (
        clean_display_text(overview.get("summary"))
        if isinstance(overview, dict)
        else ""
    )
    analysis_text = ""
    knowledge_gaps = []

    if isinstance(raw_analysis, str):
        analysis_text = clean_display_text(raw_analysis)
    elif isinstance(raw_analysis, list):
        if raw_analysis and all(isinstance(item, str) for item in raw_analysis):
            knowledge_gaps = [
                clean_display_text(item)
                for item in raw_analysis
                if clean_display_text(item)
            ]
        elif raw_analysis and all(isinstance(item, dict) for item in raw_analysis):
            extracted_gaps = [
                clean_display_text(
                    item.get("knowledge_point_name") or item.get("analysis")
                )
                for item in raw_analysis
            ]
            knowledge_gaps = [item for item in extracted_gaps if item]
    elif isinstance(raw_analysis, dict):
        analysis_text = clean_display_text(raw_analysis.get("analysis"))
        gaps = raw_analysis.get("knowledge_gaps", [])
        if isinstance(gaps, list):
            knowledge_gaps = [
                clean_display_text(item) for item in gaps if clean_display_text(item)
            ]

    if not summary:
        summary = analysis_text or clean_display_text(report.conclusion)
    if analysis_text == summary:
        analysis_text = ""

    if question_details:
        overview["score"] = round(
            sum(float(item.get("score") or 0) for item in question_details), 2
        )
        overview["correct_count"] = sum(
            1 for item in question_details if item["is_correct"]
        )
        overview["total_count"] = len(question_details)
        overview["total_questions"] = len(question_details)
        overview["accuracy"] = round(
            overview["correct_count"] / max(len(question_details), 1) * 100, 1
        )

    correct_count = overview.get("correct_count")
    total_count = overview.get("total_count") or overview.get("total_questions")
    accuracy = overview.get("accuracy")
    mastery_changes = overview.get("mastery_changes", [])

    return {
        "report_id": report.id,
        "exam_id": report.exam_id,
        "status": report.status,
        "pending": report.status == "pending",
        "retryable": report.status == "failed",
        "poll_interval_ms": 2000 if report.status == "pending" else None,
        "overview": overview,
        "summary": summary,
        "analysis": analysis_text,
        "knowledge_gaps": knowledge_gaps,
        "recommendations": report.recommendations or [],
        "next_tasks": report.next_tasks or [],
        "conclusion": report.conclusion or "",
        "question_details": question_details,
        "correct_count": correct_count,
        "total_count": total_count,
        "accuracy": accuracy,
        "mastery_changes": mastery_changes if isinstance(mastery_changes, list) else [],
        "generated_at": report.generated_at.isoformat()
        if report.generated_at
        else None,
    }


def _build_feedback_overview(
    *,
    score,
    total_score,
    passed,
    correct_count,
    total_count,
    accuracy,
    kt_analysis=None,
    summary="",
    knowledge_gaps=None,
    mastery_changes=None,
):
    """
    构建反馈概览字典。
    :param score: 得分。
    :param total_score: 总分。
    :param passed: 是否通过。
    :param correct_count: 答对题数。
    :param total_count: 题目总数。
    :param accuracy: 正确率。
    :param kt_analysis: KT 分析结果。
    :param summary: 摘要文本。
    :param knowledge_gaps: 知识短板列表。
    :param mastery_changes: 掌握度变化列表。
    :return: 反馈概览字典。
    """
    return {
        "score": float(score or 0),
        "total_score": float(total_score or 0),
        "passed": bool(passed),
        "correct_count": int(correct_count or 0),
        "total_count": int(total_count or 0),
        "total_questions": int(total_count or 0),
        "accuracy": float(accuracy or 0),
        "kt_analysis": kt_analysis or {},
        "summary": clean_display_text(summary),
        "knowledge_gaps": knowledge_gaps or [],
        "mastery_changes": mastery_changes or [],
    }


def _build_feedback_report_ref(report):
    """
    构建反馈报告引用信息。
    :param report: 反馈报告对象。
    :return: 报告引用字典。
    """
    return {
        "report_id": report.id,
        "exam_id": report.exam_id,
        "status": report.status,
        "retryable": report.status == "failed",
        "poll_url": f"/api/student/feedback/{report.exam_id}",
    }


def _build_submission_feedback_snapshot(submission):
    """
    基于考试提交构建反馈快照。
    :param submission: 考试提交对象。
    :return: 反馈快照字典。
    """
    exam = submission.exam
    exam_questions = list(
        ExamQuestion.objects.filter(exam=exam)
        .select_related("question")
        .prefetch_related("question__knowledge_points")
        .order_by("order")
    )
    questions = [eq.question for eq in exam_questions]
    score_map = _build_exam_score_map(exam, exam_questions)
    grading = score_questions(submission.answers or {}, questions, score_map=score_map)
    question_result_map = {
        str(item["question_id"]): item for item in grading["question_results"]
    }
    question_details = _build_exam_question_details(
        exam_questions, submission.answers or {}, question_result_map
    )
    correct_count = sum(1 for item in question_details if item["is_correct"])
    total_count = len(question_details)
    accuracy = round(correct_count / total_count * 100, 1) if total_count else 0
    return {
        "exam_questions": exam_questions,
        "grading": grading,
        "question_details": question_details,
        "correct_count": correct_count,
        "total_count": total_count,
        "accuracy": accuracy,
        "passed": float(grading["score"]) >= _resolve_pass_threshold(exam),
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_list(request):
    """
    获取考试列表
    GET /api/exams
    """
    course_id = request.query_params.get("course_id")
    exam_type = request.query_params.get("type")  # chapter, midterm, final
    page = max(1, safe_int(request.query_params.get("page"), 1))
    size = min(max(1, safe_int(request.query_params.get("size"), 20)), 100)

    user = request.user
    exams = Exam.objects.filter(status="published")

    if course_id:
        exams = exams.filter(course_id=course_id)

    if exam_type:
        exams = exams.filter(exam_type=exam_type)

    # 对学生过滤开放时间和班级归属
    if user.role == "student":
        now = timezone.now()
        exams = exams.filter(Q(start_time__lte=now) | Q(start_time__isnull=True))

        from courses.models import Enrollment, ClassCourse

        enrolled_class_infos = (
            Enrollment.objects.filter(user=user)
            .select_related("class_obj")
            .values("class_obj_id", "class_obj__class_courses__course_id")
        )

        enrolled_class_ids = set(item["class_obj_id"] for item in enrolled_class_infos)
        enrolled_course_ids = set(
            item["class_obj__class_courses__course_id"]
            for item in enrolled_class_infos
            if item["class_obj__class_courses__course_id"]
        )

        # 如果没有指定course_id，则限定为用户已选课程的考试
        if not course_id:
            exams = exams.filter(course_id__in=enrolled_course_ids)

        # 仅显示学生所在班级的考试 (或未指定特定班级但属于该课程的考试)
        exams = exams.filter(
            Q(target_class_id__in=enrolled_class_ids) | Q(target_class__isnull=True)
        )
    elif user.role == "teacher":
        # 教师查看自己创建的考试
        exams = exams.filter(created_by=user)

    total = exams.count()
    start = (page - 1) * size
    exams = exams[start : start + size]

    submissions = {
        s.exam_id: s for s in ExamSubmission.objects.filter(user=user, exam__in=exams)
    }

    exam_list_data = []
    for e in exams:
        submission = submissions.get(e.id)
        submission_score = (
            float(submission.score)
            if submission and submission.score is not None
            else None
        )
        is_submitted = submission_score is not None and submission_score >= 0
        threshold = _resolve_pass_threshold(e)
        passed = None
        if is_submitted:
            passed = submission_score >= threshold

        exam_list_data.append(
            {
                "exam_id": e.id,
                "title": e.title,
                "type": e.exam_type,
                "status": e.status,
                "total_score": float(e.total_score),
                "duration": e.duration,
                "start_time": e.start_time.isoformat() if e.start_time else None,
                "end_time": e.end_time.isoformat() if e.end_time else None,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "submitted": is_submitted,
                "score": submission_score if is_submitted else None,
                "passed": passed,
                "submitted_at": submission.submitted_at.isoformat()
                if submission and submission.submitted_at
                else None,
            }
        )

    return success_response(data={"total": total, "exams": exam_list_data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_detail(request, exam_id):
    """
    获取考试详情（含题目，不含答案）
    GET /api/exams/{exam_id}
    """
    try:
        exam = Exam.objects.get(id=exam_id, status="published")
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    user = request.user

    # 检查是否可以访问
    if user.role == "student":
        now = timezone.now()
        if exam.start_time and exam.start_time > now:
            return error_response(msg="作业尚未开始", code=403)
        if exam.end_time and exam.end_time < now:
            return error_response(msg="作业已结束", code=403)

    exam_questions = (
        ExamQuestion.objects.filter(exam=exam)
        .select_related("question")
        .order_by("order")
    )

    score_map = _build_exam_score_map(exam, exam_questions)
    questions = []
    for eq in exam_questions:
        q = eq.question
        questions.append(
            {
                "question_id": q.id,
                "content": q.content,
                "options": q.options,
                "type": q.question_type,
                "score": score_map.get(str(q.id), 0),
            }
        )

    return success_response(
        data={
            "exam_id": exam.id,
            "title": exam.title,
            "description": exam.description,
            "total_score": float(exam.total_score),
            "pass_score": _resolve_pass_threshold(exam),
            "duration": exam.duration,
            "questions": questions,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def exam_submit(request, exam_id):
    """
    提交考试答案
    POST /api/student/exams/{exam_id}/submit

    注意：仅学生可以提交考试
    """
    answers = request.data.get("answers", {})

    if not answers:
        return error_response(msg="答案不能为空")

    # 验证 answers 格式
    if not isinstance(answers, dict):
        return error_response(msg="答案格式错误，应为字典格式")

    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    user = request.user

    # 已正式提交的不允许再次提交，草稿允许覆盖
    if ExamSubmission.objects.filter(exam=exam, user=user, score__gte=0).exists():
        return error_response(msg="已经提交过该作业")

    # 检查时间
    now = timezone.now()
    if exam.end_time and exam.end_time < now:
        return error_response(msg="作业已结束，无法提交", code=403)

    exam_questions = list(
        ExamQuestion.objects.filter(exam=exam)
        .select_related("question")
        .prefetch_related("question__knowledge_points")
    )
    questions = [eq.question for eq in exam_questions]
    score_map = _build_exam_score_map(exam, exam_questions)
    grading = score_questions(answers, questions, score_map=score_map)
    score = grading["score"]
    mistakes = grading["mistakes"]
    question_result_map = {
        str(item["question_id"]): item for item in grading["question_results"]
    }
    question_details = _build_exam_question_details(
        exam_questions, answers, question_result_map
    )

    pass_threshold = _resolve_pass_threshold(exam)
    passed = score >= pass_threshold
    correct_count = sum(1 for item in grading["question_results"] if item["is_correct"])
    accuracy = round(correct_count / len(questions) * 100, 1) if questions else 0

    # 保存提交（事务保护，防止并发重复提交）
    from django.db import IntegrityError
    from assessments.models import AnswerHistory

    with transaction.atomic():
        existing_submission = (
            ExamSubmission.objects.select_for_update()
            .filter(exam=exam, user=user)
            .first()
        )
        if (
            existing_submission
            and existing_submission.score is not None
            and float(existing_submission.score) >= 0
        ):
            return error_response(msg="已经提交过该作业")
        if existing_submission:
            submission = existing_submission
            submission.answers = answers
            submission.score = score
            submission.is_passed = passed
            submission.graded_at = timezone.now()
            submission.save(
                update_fields=["answers", "score", "is_passed", "graded_at"]
            )
        else:
            try:
                submission = ExamSubmission.objects.create(
                    exam=exam,
                    user=user,
                    answers=answers,
                    score=score,
                    is_passed=passed,
                    graded_at=timezone.now(),
                )
            except IntegrityError:
                return error_response(msg="已经提交过该作业")

        # ---- 记录答题历史（供KT分析用） ----
        mistake_qids = {str(m["question_id"]) for m in mistakes}
        answer_history_records = []
        for q in questions:
            q_id = str(q.id)
            result = question_result_map.get(q_id, {})
            student_answer = answers.get(q_id)
            correct_value = result.get("correct_answer", extract_answer_value(q.answer))
            is_correct = result.get("is_correct", q_id not in mistake_qids)
            kp = q.knowledge_points.first()

            AnswerHistory.objects.create(
                user=user,
                course=exam.course,
                question=q,
                knowledge_point=kp,
                student_answer=serialize_answer_payload(
                    q.question_type, student_answer
                ),
                correct_answer=serialize_answer_payload(q.question_type, correct_value),
                is_correct=is_correct,
                score=result.get("earned_score", 0),
                source="exam",
                exam_id=exam.id,
            )

            # 收集KT所需数据
            if kp:
                answer_history_records.append(
                    {
                        "question_id": q.id,
                        "knowledge_point_id": kp.id,
                        "correct": 1 if is_correct else 0,
                    }
                )

        tracked_point_ids = sorted(
            {
                int(item["knowledge_point_id"])
                for item in answer_history_records
                if item.get("knowledge_point_id")
            }
        )
        mastery_before_snapshot = _snapshot_mastery_for_points(
            user, exam.course_id, tracked_point_ids
        )

        # ---- KT服务：知识追踪预测 ----
        kt_analysis = {}
        try:
            from ai_services.services import kt_service

            if answer_history_records:
                kt_result = kt_service.predict_mastery(
                    user_id=user.id,
                    course_id=exam.course_id,
                    answer_history=answer_history_records,
                )
                kt_predictions = kt_result.get("predictions") or {}
                if kt_predictions:
                    from knowledge.models import KnowledgeMastery

                    for kp_id, rate in kt_predictions.items():
                        try:
                            KnowledgeMastery.objects.update_or_create(
                                user=user,
                                course_id=exam.course_id,
                                knowledge_point_id=kp_id,
                                defaults={"mastery_rate": float(rate)},
                            )
                        # KT 掌握度写回失败时仅跳过当前知识点，避免影响交卷主流程。
                        except (
                            DatabaseError,
                            InvalidOperation,
                            OverflowError,
                            TypeError,
                            ValueError,
                        ) as error:
                            logger.warning(
                                build_log_message(
                                    "kt.exam_submit.mastery_skip",
                                    user_id=user.id,
                                    exam_id=exam.id,
                                    knowledge_point_id=kp_id,
                                    error=error,
                                )
                            )
                    kt_analysis = {
                        "predictions": kt_predictions,
                        "confidence": kt_result.get("confidence", 0),
                        "model_type": kt_result.get("model_type", "unknown"),
                    }
                    logger.info(
                        build_log_message(
                            "kt.exam_submit.success",
                            user_id=user.id,
                            exam_id=exam.id,
                            answer_count=len(answer_history_records),
                            prediction_count=len(kt_predictions),
                        )
                    )
        except Exception as e:
            logger.error(
                build_log_message(
                    "kt.exam_submit.fail", user_id=user.id, exam_id=exam.id, error=e
                )
            )

        mastery_after_snapshot = _snapshot_mastery_for_points(
            user, exam.course_id, tracked_point_ids
        )
        mastery_changes = _build_mastery_change_payload(
            mastery_before_snapshot, mastery_after_snapshot
        )

        # ---- 创建 pending 报告并在事务提交后异步生成 ----
        overview = _build_feedback_overview(
            score=score,
            total_score=exam.total_score,
            passed=passed,
            correct_count=correct_count,
            total_count=len(questions),
            accuracy=accuracy,
            kt_analysis=kt_analysis,
            mastery_changes=mastery_changes,
        )
        report, _ = FeedbackReport.objects.update_or_create(
            user=user,
            exam=exam,
            defaults={
                "exam_submission": submission,
                "status": "pending",
                "overview": overview,
                "analysis": "",
                "recommendations": [],
                "next_tasks": [],
                "conclusion": "",
            },
        )
        from .report_service import enqueue_feedback_report_on_commit

        enqueue_feedback_report_on_commit(report.id, force=True)

    return success_response(
        data={
            "submission_id": submission.id,
            "score": score,
            "total_score": float(exam.total_score),
            "pass_score": pass_threshold,
            "passed": passed,
            "correct_count": correct_count,
            "total_count": len(questions),
            "accuracy": accuracy,
            "question_details": question_details,
            "mistakes": [
                {
                    "question_id": m["question_id"],
                    "correct_answer": m["correct_answer"],
                    "your_answer": m["student_answer"],
                    "analysis": m["analysis"],
                }
                for m in mistakes
            ],
            "mastery_changes": mastery_changes,
            "feedback_report": _build_feedback_report_ref(report),
        },
        msg="作业提交成功",
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_result(request, exam_id):
    """
    获取考试结果
    GET /api/exams/{exam_id}/result
    """
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    user = request.user

    try:
        submission = ExamSubmission.objects.get(exam=exam, user=user)
    except ExamSubmission.DoesNotExist:
        return error_response(msg="您尚未完成该作业", code=404)

    snapshot = _build_submission_feedback_snapshot(submission)
    question_details = snapshot["question_details"]
    correct_count = snapshot["correct_count"]
    total_count = snapshot["total_count"]
    accuracy = snapshot["accuracy"]
    display_score = float(snapshot["grading"]["score"])
    pass_threshold = _resolve_pass_threshold(exam)
    passed = snapshot["passed"]

    if (
        submission.score is None
        or float(submission.score) != display_score
        or submission.is_passed != passed
    ):
        submission.score = display_score
        submission.is_passed = passed
        submission.graded_at = submission.graded_at or timezone.now()
        submission.save(update_fields=["score", "is_passed", "graded_at"])

    return success_response(
        data={
            "exam_id": exam.id,
            "exam_title": exam.title,
            "score": display_score,
            "total_score": float(exam.total_score),
            "pass_score": pass_threshold,
            "passed": passed,
            "submitted_at": submission.submitted_at.isoformat(),
            "correct_count": correct_count,
            "total_count": total_count,
            "accuracy": accuracy,
            "questions": question_details,
            "question_details": question_details,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_feedback_report(request):
    """
    生成反馈报告
    POST /api/feedback/generate
    """
    exam_id = request.data.get("exam_id")
    force = request.data.get("force", False)

    if not exam_id:
        return error_response(msg="缺少作业ID")

    user = request.user

    try:
        submission = ExamSubmission.objects.get(exam_id=exam_id, user=user)
    except ExamSubmission.DoesNotExist:
        return error_response(msg="您尚未完成该作业", code=404)

    report = FeedbackReport.objects.filter(exam_id=exam_id, user=user).first()
    snapshot = _build_submission_feedback_snapshot(submission)
    question_details = snapshot["question_details"]

    if report and report.status == "completed" and not force:
        return success_response(
            data=_normalize_feedback_payload(report, question_details)
        )

    overview = (
        dict(report.overview) if report and isinstance(report.overview, dict) else {}
    )
    overview.update(
        _build_feedback_overview(
            score=snapshot["grading"]["score"],
            total_score=submission.exam.total_score,
            passed=snapshot["passed"],
            correct_count=snapshot["correct_count"],
            total_count=snapshot["total_count"],
            accuracy=snapshot["accuracy"],
            kt_analysis=overview.get("kt_analysis", {}),
            summary=overview.get("summary", ""),
            knowledge_gaps=overview.get("knowledge_gaps", []),
        )
    )

    report, _ = FeedbackReport.objects.update_or_create(
        exam_id=exam_id,
        user=user,
        defaults={
            "exam_submission": submission,
            "status": "pending",
            "overview": overview,
            "analysis": "",
            "recommendations": [],
            "next_tasks": [],
            "conclusion": "",
        },
    )

    from .report_service import enqueue_feedback_report_on_commit

    enqueue_feedback_report_on_commit(report.id, force=bool(force))

    payload = _normalize_feedback_payload(report, question_details)
    msg = "AI 反馈报告已重新排队生成" if force else "AI 反馈报告生成中"
    return success_response(data=payload, msg=msg)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_feedback_report(request, exam_id):
    """
    获取反馈报告
    GET /api/feedback/{exam_id}
    """
    user = request.user

    report = FeedbackReport.objects.filter(exam_id=exam_id, user=user).first()

    if not report:
        return error_response(msg="报告不存在", code=404)

    question_details = []
    if report.exam_submission and report.exam:
        snapshot = _build_submission_feedback_snapshot(report.exam_submission)
        question_details = snapshot["question_details"]

    return success_response(data=_normalize_feedback_payload(report, question_details))


# ========== 教师端考试管理 ==========


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initial_assessment_start(request):
    """
    开始初始评测（随机抽题）
    POST /api/assessments/initial/start
    """
    import random

    course_id = request.data.get("course_id")

    if not course_id:
        return error_response(msg="缺少课程ID")

    course = validate_course_exists(course_id)
    if course is None:
        return error_response(msg="课程不存在", code=404)

    questions = list(
        Question.objects.filter(
            course=course, for_initial_assessment=True, is_visible=True
        ).prefetch_related("knowledge_points")
    )

    if not questions:
        return error_response(msg="课程暂无初始评测题目")

    # 随机抽取
    count = min(course.initial_assessment_count, len(questions))
    selected = random.sample(questions, count)

    return success_response(
        data={
            "course_id": course.id,
            "questions": [
                {
                    "question_id": q.id,
                    "content": q.content,
                    "options": q.options,
                    "type": q.question_type,
                    "score": float(q.score),
                }
                for q in selected
            ],
            "count": count,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initial_assessment_submit(request):
    """
    提交初始评测
    POST /api/assessments/initial/submit
    """
    from assessments.models import AnswerHistory, AssessmentStatus
    from knowledge.models import KnowledgeMastery
    from collections import defaultdict

    course_id = request.data.get("course_id")
    answers = request.data.get("answers", {})

    if not course_id or not answers:
        return error_response(msg="缺少必填参数")

    # 验证 answers 格式
    if not isinstance(answers, dict):
        return error_response(msg="答案格式错误，应为字典格式")

    course = validate_course_exists(course_id)
    if course is None:
        return error_response(msg="课程不存在", code=404)

    user = request.user

    try:
        question_ids = [int(qid) for qid in answers.keys()]
    except (ValueError, TypeError):
        return error_response(msg="题目ID格式错误")
    questions = Question.objects.filter(id__in=question_ids).prefetch_related(
        "knowledge_points"
    )

    # 评分并记录答题历史
    total_score = 0
    correct_count = 0
    kp_stats = defaultdict(lambda: {"correct": 0, "total": 0})

    for q in questions:
        qid = str(q.id)
        student_answer = answers.get(qid)
        correct_answer = extract_answer_value(q.answer)
        is_correct = check_answer(q.question_type, student_answer, q.answer)

        score = float(q.score) if is_correct else 0
        total_score += score
        if is_correct:
            correct_count += 1

        # 记录答题历史
        kp = q.knowledge_points.first()
        AnswerHistory.objects.create(
            user=user,
            course=course,
            question=q,
            knowledge_point=kp,
            student_answer={"answer": student_answer},
            correct_answer={"answer": correct_answer},
            is_correct=is_correct,
            score=score,
            source="initial",
        )

        # 统计知识点正确率
        for kp in q.knowledge_points.all():
            kp_stats[kp.id]["total"] += 1
            if is_correct:
                kp_stats[kp.id]["correct"] += 1

    # 更新知识掌握度
    # 更新知识掌握度（先用简单正确率，再尝试KT服务覆盖）
    knowledge_mastery = {}
    for kp_id, stats in kp_stats.items():
        mastery_rate = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        KnowledgeMastery.objects.update_or_create(
            user=user,
            course=course,
            knowledge_point_id=kp_id,
            defaults={"mastery_rate": mastery_rate},
        )
        knowledge_mastery[kp_id] = mastery_rate

    # 使用 KT 服务进行更精确的掌握度预测（覆盖简单正确率结果）
    try:
        from ai_services.services.kt_service import kt_service

        all_history = list(
            AnswerHistory.objects.filter(user=user, course=course)
            .order_by("answered_at")
            .values("question_id", "knowledge_point_id", "is_correct")
        )
        kt_history = [
            {
                "question_id": h["question_id"],
                "knowledge_point_id": h["knowledge_point_id"],
                "correct": 1 if h["is_correct"] else 0,
            }
            for h in all_history
        ]
        kp_ids_list = list(kp_stats.keys())
        if kt_history and kp_ids_list:
            kt_result = kt_service.predict_mastery(
                user_id=user.id,
                course_id=course.id,
                answer_history=kt_history,
                knowledge_points=kp_ids_list,
            )
            kt_predictions = kt_result.get("predictions", {})
            for kp_id, rate in kt_predictions.items():
                try:
                    KnowledgeMastery.objects.update_or_create(
                        user=user,
                        course=course,
                        knowledge_point_id=kp_id,
                        defaults={
                            "mastery_rate": max(0, min(1, round(float(rate), 4)))
                        },
                    )
                    knowledge_mastery[int(kp_id)] = round(float(rate), 4)
                # 单个知识点掌握度同步失败时继续处理其余结果，保证整体反馈可返回。
                except (
                    DatabaseError,
                    InvalidOperation,
                    OverflowError,
                    TypeError,
                    ValueError,
                ) as error:
                    logger.warning(
                        build_log_message(
                            "kt.initial_assessment.mastery_skip",
                            user_id=user.id,
                            course_id=course.id,
                            knowledge_point_id=kp_id,
                            error=error,
                        )
                    )
            logger.info(
                "KT服务调用成功(初始评测): 用户=%s, 答题历史=%d条, 预测结果=%d条",
                user.id,
                len(kt_history),
                len(kt_predictions),
            )
    except Exception as e:
        logger.error("KT服务调用失败(初始评测): 用户=%s, 错误=%s", user.id, e)

    # 更新评测状态
    status, _ = AssessmentStatus.objects.get_or_create(user=user, course=course)
    status.knowledge_done = True
    status.save()

    return success_response(
        data={
            "score": total_score,
            "correct_count": correct_count,
            "total_count": len(questions),
            "knowledge_mastery": knowledge_mastery,
        },
        msg="初始评测完成",
    )


# ============ 教师考试管理扩展 ============


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def exam_save_draft(request, exam_id):
    """
    保存考试草稿
    POST /api/student/exams/{exam_id}/draft
    """
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    answers = request.data.get("answers", {})

    # 使用 ExamSubmission 存储草稿（is_draft 字段 或 用 score=-1 标记）
    submission, _ = ExamSubmission.objects.update_or_create(
        exam=exam,
        user=request.user,
        defaults={
            "answers": answers,
            "score": -1,  # -1 标记为草稿
        },
    )

    return success_response(
        data={"submission_id": submission.id, "saved": True}, msg="草稿已保存"
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_statistics(request, exam_id):
    """
    获取考试统计数据（学生视角）
    GET /api/student/exams/{exam_id}/statistics
    """
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    my_sub = ExamSubmission.objects.filter(
        exam=exam, user=request.user, score__gte=0
    ).first()
    all_subs = ExamSubmission.objects.filter(exam=exam, score__gte=0)

    avg = all_subs.aggregate(avg=models.Avg("score"))["avg"] or 0
    total = all_subs.count()

    # 我的排名
    rank = 0
    if my_sub:
        rank = all_subs.filter(score__gt=my_sub.score).count() + 1

    return success_response(
        data={
            "my_score": float(my_sub.score) if my_sub else None,
            "average_score": round(float(avg), 1),
            "total_submissions": total,
            "my_rank": rank,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_answer_sheet(request, exam_id):
    """
    查看标准答案
    GET /api/student/exams/{exam_id}/answer-sheet
    """
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    # 只有已提交的学生才能查看答案
    submitted = ExamSubmission.objects.filter(
        exam=exam, user=request.user, score__gte=0
    ).exists()
    if not submitted:
        return error_response(msg="请先完成作业再查看答案")

    questions = Question.objects.filter(
        id__in=ExamQuestion.objects.filter(exam=exam).values_list(
            "question_id", flat=True
        )
    )

    return success_response(
        data=[
            {
                "question_id": q.id,
                "content": q.content,
                "correct_answer": extract_answer_value(q.answer),
                "analysis": q.analysis or "",
            }
            for q in questions
        ]
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def exam_retake(request, exam_id):
    """
    重新参加考试
    POST /api/student/exams/{exam_id}/retake
    """
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    # 检查是否允许重考（简单策略：删除旧提交）
    old_subs = ExamSubmission.objects.filter(exam=exam, user=request.user)
    if not old_subs.exists():
        return error_response(msg="您尚未完成此作业")

    old_subs.delete()
    return success_response(msg="已重置，可以重新作答")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exam_download(request, exam_id):
    """
    下载考试答案报告
    GET /api/student/exams/{exam_id}/download
    """
    import codecs
    import csv
    from django.http import HttpResponse

    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return error_response(msg="作业不存在", code=404)

    sub = ExamSubmission.objects.filter(
        exam=exam, user=request.user, score__gte=0
    ).first()
    if not sub:
        return error_response(msg="您尚未完成此作业")

    # 构造HTTP响应
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = (
        f'attachment; filename="homework_{exam_id}_result.csv"'
    )
    # 写入文件内容
    response.write(codecs.BOM_UTF8.decode("utf-8"))

    writer = csv.writer(response)
    writer.writerow(["题号", "题目", "您的答案", "正确答案", "是否正确"])

    questions = Question.objects.filter(
        id__in=ExamQuestion.objects.filter(exam=exam).values_list(
            "question_id", flat=True
        )
    )
    answers = sub.answers or {}

    for i, q in enumerate(questions, 1):
        my_ans = answers.get(str(q.id), "")
        correct_answer = extract_answer_value(q.answer)
        is_correct = check_answer(q.question_type, my_ans, q.answer)
        writer.writerow(
            [i, q.content, my_ans, correct_answer, "✓" if is_correct else "✗"]
        )

    return response


# ============ 学生端 — 班级 ============


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_class_members(request, class_id):
    """
    获取班级成员列表
    GET /api/student/classes/{class_id}/members
    """
    from courses.models import Enrollment, Class
    from users.models import User

    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    # 确认是该班级学生
    if not Enrollment.objects.filter(class_obj=class_obj, user=request.user).exists():
        return error_response(msg="您不是该班级成员", code=403)

    members = User.objects.filter(
        id__in=Enrollment.objects.filter(class_obj=class_obj).values_list(
            "user_id", flat=True
        )
    )

    return success_response(
        data=[
            {"user_id": m.id, "username": m.username, "real_name": m.real_name}
            for m in members
        ]
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_class_ranking(request, class_id):
    """
    获取班级学习排行榜
    GET /api/student/classes/{class_id}/ranking
    """
    from courses.models import Enrollment, Class
    from knowledge.models import KnowledgeMastery

    # 写入调试日志，保留请求上下文
    logger.debug(
        build_log_message(
            "exam.student_class_ranking.request",
            user_id=getattr(request.user, "id", None),
            class_id=class_id,
        )
    )

    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    enrollments = Enrollment.objects.filter(class_obj=class_obj).select_related("user")

    ranking = []
    for e in enrollments:
        masteries = KnowledgeMastery.objects.filter(user=e.user)
        rates = [float(m.mastery_rate) for m in masteries]
        avg = sum(rates) / len(rates) if rates else 0
        ranking.append(
            {
                "user_id": e.user_id,
                "username": e.user.username,
                "real_name": e.user.real_name,
                "avg_mastery": round(avg, 2),
            }
        )

    ranking.sort(key=lambda x: x["avg_mastery"], reverse=True)
    for i, r in enumerate(ranking, 1):
        r["rank"] = i

    return success_response(data=ranking)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_class_notifications(request, class_id):
    """
    获取班级通知公告（简版）
    GET /api/student/classes/{class_id}/notifications
    """
    from courses.models import Class

    # 写入调试日志，保留请求上下文
    logger.debug(
        build_log_message(
            "exam.student_class_notifications.request",
            user_id=getattr(request.user, "id", None),
            class_id=class_id,
        )
    )

    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    from .models import Exam
    from courses.models import ClassCourse

    course_ids = ClassCourse.objects.filter(class_obj=class_obj).values_list(
        "course_id", flat=True
    )
    exams = Exam.objects.filter(course_id__in=course_ids, status="published").order_by(
        "-created_at"
    )[:10]

    return success_response(
        data=[
            {
                "id": e.id,
                "title": f"新作业：{e.title}",
                "type": "exam",
                "created_at": e.created_at.isoformat() if e.created_at else "",
            }
            for e in exams
        ]
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_class_assignments(request, class_id):
    """
    获取班级作业列表（映射到考试列表）
    GET /api/student/classes/{class_id}/assignments
    """
    from courses.models import Class

    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg="班级不存在", code=404)

    from .models import Exam
    from courses.models import ClassCourse

    course_ids = ClassCourse.objects.filter(class_obj=class_obj).values_list(
        "course_id", flat=True
    )
    exams = Exam.objects.filter(course_id__in=course_ids, status="published").order_by(
        "-created_at"
    )

    # 检查学生是否已提交
    submitted_ids = set(
        ExamSubmission.objects.filter(
            user=request.user, exam__in=exams, score__gte=0
        ).values_list("exam_id", flat=True)
    )

    return success_response(
        data=[
            {
                "id": e.id,
                "title": e.title,
                "course_name": e.course.name if e.course else "",
                "status": "submitted" if e.id in submitted_ids else "pending",
                "created_at": e.created_at.isoformat() if e.created_at else "",
            }
            for e in exams
        ]
    )


# ============ 教师端 — 考试扩展 ============
