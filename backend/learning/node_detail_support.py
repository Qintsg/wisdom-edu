"""学习路径节点详情与节点测验辅助工具。"""
from __future__ import annotations

import logging
from typing import Any

from common.logging_utils import build_log_message
from common.utils import (
    check_answer,
    extract_answer_value,
    score_questions,
    serialize_answer_payload,
)
from exams.models import ExamQuestion, ExamSubmission
from knowledge.models import KnowledgeMastery
from learning.models import NodeProgress, PathNode
from learning.view_helpers import _build_exam_score_map, _coerce_string_list


logger = logging.getLogger(__name__)


def load_node_for_user(*, user, node_id: int, course_id: str | None = None) -> PathNode | None:
    """按用户和可选课程上下文加载路径节点。"""
    query = PathNode.objects.select_related("knowledge_point").filter(id=node_id, path__user=user)
    if course_id:
        query = query.filter(path__course_id=course_id)
    return query.first()


def ensure_progress_baseline(*, node: PathNode, user) -> tuple[NodeProgress, float | None]:
    """确保节点进度存在，并在首次访问时写入 mastery_before。"""
    progress, _ = NodeProgress.objects.get_or_create(node=node, user=user)
    current_mastery_rate = None
    if node.knowledge_point_id:
        mastery_record = KnowledgeMastery.objects.filter(
            user=user,
            course_id=node.path.course_id,
            knowledge_point_id=node.knowledge_point_id,
        ).first()
        if mastery_record:
            current_mastery_rate = float(mastery_record.mastery_rate)
            if progress.mastery_before is None:
                progress.mastery_before = current_mastery_rate
                progress.save(update_fields=["mastery_before", "updated_at"])
    return progress, current_mastery_rate


def build_node_detail_payload(*, node: PathNode, progress: NodeProgress, current_mastery_rate: float | None) -> dict[str, Any]:
    """构造节点详情接口响应。"""
    completed_resource_ids = _coerce_string_list(progress.completed_resources)
    exercises = []
    if node.exam:
        exercises.append({"exam_id": node.exam.id, "title": node.exam.title, "required": True})
    return {
        "node_id": node.id,
        "node_title": node.title,
        "knowledge_point_id": node.knowledge_point_id,
        "knowledge_point_name": node.knowledge_point.name if node.knowledge_point else None,
        "goal": node.goal,
        "resources": [],
        "exercises": exercises,
        "status": node.status,
        "progress": {
            "resources_completed": len(completed_resource_ids),
            "resources_total": 0,
            "exercises_completed": len(progress.completed_exams),
            "exercises_total": 1 if node.exam else 0,
        },
        "mastery_before": float(progress.mastery_before) if progress.mastery_before is not None else current_mastery_rate,
        "mastery_after": float(progress.mastery_after) if progress.mastery_after is not None else None,
    }


def mark_node_resource_completed(progress: NodeProgress, resource_id: str) -> dict[str, Any]:
    """标记单个节点资源为已完成。"""
    str_id = str(resource_id)
    completed_resource_ids = _coerce_string_list(progress.completed_resources)
    if str_id not in completed_resource_ids:
        completed_resource_ids.append(str_id)
        progress.completed_resources = completed_resource_ids
        progress.save()
    return {
        "message": f"资源 {resource_id} 已完成学习",
        "progress": {
            "resources_completed": len(progress.completed_resources),
            "resources_total": 0,
            "exercises_completed": len(progress.completed_exams),
            "exercises_total": 1 if progress.node.exam else 0,
        },
    }


def build_node_exam_context(node: PathNode, answers: dict[str, Any]) -> dict[str, Any]:
    """构建节点小测的批改上下文。"""
    exam = node.exam
    exam_questions = list(ExamQuestion.objects.filter(exam=exam).select_related("question"))
    questions = [exam_question.question for exam_question in exam_questions]
    score_map = _build_exam_score_map(exam, exam_questions)
    grading = score_questions(answers, questions, score_map=score_map)
    question_result_map = {
        str(item["question_id"]): item for item in grading["question_results"]
    }
    total_score = float(exam.total_score or grading["total_score"] or 0)
    return {
        "exam_questions": exam_questions,
        "questions": questions,
        "grading": grading,
        "question_result_map": question_result_map,
        "score": float(grading["score"]),
        "mistakes": grading["mistakes"],
        "point_stats": grading["point_stats"],
        "total_score": total_score,
        "passed": float(grading["score"]) >= float(exam.pass_score),
    }


def upsert_node_exam_submission(*, exam, user, answers: dict[str, Any], score: float, passed: bool) -> ExamSubmission:
    """创建或更新节点考试提交记录。"""
    submission, _ = ExamSubmission.objects.update_or_create(
        exam=exam,
        user=user,
        defaults={"answers": answers, "score": score, "is_passed": passed},
    )
    return submission


def update_node_exam_progress(*, node: PathNode, progress: NodeProgress, exam_id: int, passed: bool) -> None:
    """根据节点考试结果推进节点状态与学习路径状态。"""
    completed_exam_ids = list(progress.completed_exams or [])
    if exam_id not in completed_exam_ids:
        completed_exam_ids.append(exam_id)
        progress.completed_exams = completed_exam_ids

    if passed:
        node.status = "completed"
        next_node = PathNode.objects.filter(path=node.path, order_index__gt=node.order_index).first()
        if next_node and next_node.status == "locked":
            next_node.status = "active"
            next_node.save()
    else:
        node.status = "failed"

    node.save()
    progress.save()


def persist_node_exam_histories(*, user, node: PathNode, answers: dict[str, Any], questions, question_result_map: dict[str, dict[str, Any]]) -> list[dict[str, int]]:
    """记录节点考试答题历史，并返回 KT 所需的答题轨迹。"""
    from assessments.models import AnswerHistory

    answer_history_records: list[dict[str, int]] = []
    for question in questions:
        question_id = str(question.id)
        result = question_result_map.get(question_id, {})
        student_answer = answers.get(question_id, "")
        correct_answer = result.get("correct_answer", extract_answer_value(question.answer))
        is_correct = result.get("is_correct", check_answer(question.question_type, student_answer, question.answer))
        knowledge_point = question.knowledge_points.first() if hasattr(question, "knowledge_points") else None
        AnswerHistory.objects.create(
            user=user,
            course=node.path.course,
            question=question,
            knowledge_point=knowledge_point,
            student_answer=serialize_answer_payload(question.question_type, student_answer),
            correct_answer=serialize_answer_payload(question.question_type, correct_answer),
            is_correct=is_correct,
            score=result.get("earned_score", 0),
            source="node_exam",
        )
        if knowledge_point:
            answer_history_records.append(
                {
                    "question_id": question.id,
                    "knowledge_point_id": knowledge_point.id,
                    "correct": 1 if is_correct else 0,
                }
            )
    return answer_history_records


def refresh_node_exam_mastery(*, user, node: PathNode, point_stats: dict[int, dict[str, Any]], answer_history_records: list[dict[str, int]], score: float, total_score: float, progress: NodeProgress) -> str | float:
    """尝试用 KT 刷新掌握度；失败时降级到简单加减分。"""
    try:
        from assessments.models import AnswerHistory
        from ai_services.services.kt_service import kt_service

        all_history = list(
            AnswerHistory.objects.filter(user=user, course=node.path.course)
            .order_by("answered_at")
            .values("question_id", "knowledge_point_id", "is_correct")
        )
        kt_history = [
            {
                "question_id": history["question_id"],
                "knowledge_point_id": history["knowledge_point_id"],
                "correct": 1 if history["is_correct"] else 0,
            }
            for history in all_history
        ]
        knowledge_point_ids = list(point_stats.keys()) if point_stats else ([node.knowledge_point_id] if node.knowledge_point_id else [])
        if not kt_history or not knowledge_point_ids:
            raise ValueError("无可用的答题历史或知识点")

        kt_result = kt_service.predict_mastery(
            user_id=user.id,
            course_id=node.path.course_id,
            answer_history=kt_history,
            knowledge_points=knowledge_point_ids,
        )
        kt_predictions = kt_result.get("predictions", {})
        for knowledge_point_id, mastery_value in kt_predictions.items():
            try:
                mastery, _ = KnowledgeMastery.objects.get_or_create(
                    user=user,
                    course=node.path.course,
                    knowledge_point_id=knowledge_point_id,
                )
                mastery.mastery_rate = max(0, min(1, round(mastery_value, 4)))
                mastery.save()
            except Exception as error:
                logger.warning(
                    build_log_message(
                        "kt.node_exam.mastery_update_fail",
                        user_id=user.id,
                        exam_id=node.exam_id,
                        knowledge_point_id=knowledge_point_id,
                        error=error,
                    )
                )

        progress.mastery_after = score / total_score if total_score > 0 else 0
        progress.save()
        logger.info(
            build_log_message(
                "kt.node_exam.success",
                user_id=user.id,
                exam_id=node.exam_id,
                answer_count=len(kt_history),
                prediction_count=len(kt_predictions),
            )
        )
        return "kt"
    except Exception as error:
        logger.error(
            build_log_message(
                "kt.node_exam.fail",
                user_id=user.id,
                exam_id=node.exam_id,
                error=error,
            )
        )
        mastery_update = 0.1 if (total_score > 0 and score >= total_score * 0.6) else -0.1
        if node.knowledge_point:
            mastery, _ = KnowledgeMastery.objects.get_or_create(
                user=user,
                course=node.path.course,
                knowledge_point=node.knowledge_point,
            )
            mastery.mastery_rate = max(0, min(1, float(mastery.mastery_rate) + mastery_update))
            mastery.save()
            progress.mastery_after = mastery.mastery_rate
            progress.save()
        return mastery_update
