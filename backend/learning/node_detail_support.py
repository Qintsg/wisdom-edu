"""学习路径节点详情与节点测验辅助工具。"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from django.db import DatabaseError

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


# 维护意图：节点小测完成后刷新 KT 掌握度所需的最小上下文
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class NodeExamMasteryRefresh:
    """节点小测完成后刷新 KT 掌握度所需的最小上下文。"""

    user: Any
    node: PathNode
    point_stats: dict[int, dict[str, Any]]
    score: float
    total_score: float
    progress: NodeProgress


# 维护意图：按用户和可选课程上下文加载路径节点
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_node_for_user(*, user, node_id: int, course_id: str | None = None) -> PathNode | None:
    """按用户和可选课程上下文加载路径节点。"""
    # 节点详情接口只能访问当前用户学习路径内的节点，避免跨用户枚举。
    query = PathNode.objects.select_related("knowledge_point").filter(id=node_id, path__user=user)
    if course_id:
        query = query.filter(path__course_id=course_id)
    return query.first()


# 维护意图：确保节点进度存在，并在首次访问时写入 mastery_before
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def ensure_progress_baseline(*, node: PathNode, user) -> tuple[NodeProgress, float | None]:
    """确保节点进度存在，并在首次访问时写入 mastery_before。"""
    progress, _ = NodeProgress.objects.get_or_create(node=node, user=user)
    current_mastery_rate = None
    if node.knowledge_point_id:
        # mastery_before 只在首次访问时固定，后续测验才能展示真实前后变化。
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


# 维护意图：构造节点详情接口响应
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_node_detail_payload(*, node: PathNode, progress: NodeProgress, current_mastery_rate: float | None) -> dict[str, Any]:
    """构造节点详情接口响应。"""
    # 外部资源当前由学习路径编排层填充，这里只汇总节点自身的完成状态。
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


# 维护意图：标记单个节点资源为已完成
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def mark_node_resource_completed(progress: NodeProgress, resource_id: str) -> dict[str, Any]:
    """标记单个节点资源为已完成。"""
    str_id = str(resource_id)
    completed_resource_ids = _coerce_string_list(progress.completed_resources)
    if str_id not in completed_resource_ids:
        # completed_resources 存储字符串，兼容内部整数 ID 与 ext_ 前缀外部资源。
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


# 维护意图：构建节点小测的批改上下文
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_node_exam_context(node: PathNode, answers: dict[str, Any]) -> dict[str, Any]:
    """构建节点小测的批改上下文。"""
    exam = node.exam
    exam_questions = list(ExamQuestion.objects.filter(exam=exam).select_related("question"))
    questions = [exam_question.question for exam_question in exam_questions]
    # 评分入口沿用 common.utils，确保节点小测与普通考试批改规则一致。
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


# 维护意图：创建或更新节点考试提交记录
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def upsert_node_exam_submission(*, exam, user, answers: dict[str, Any], score: float, passed: bool) -> ExamSubmission:
    """创建或更新节点考试提交记录。"""
    submission, _ = ExamSubmission.objects.update_or_create(
        exam=exam,
        user=user,
        defaults={"answers": answers, "score": score, "is_passed": passed},
    )
    return submission


# 维护意图：根据节点考试结果推进节点状态与学习路径状态
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_node_exam_progress(*, node: PathNode, progress: NodeProgress, exam_id: int, passed: bool) -> None:
    """根据节点考试结果推进节点状态与学习路径状态。"""
    completed_exam_ids = list(progress.completed_exams or [])
    if exam_id not in completed_exam_ids:
        completed_exam_ids.append(exam_id)
        progress.completed_exams = completed_exam_ids

    if passed:
        node.status = "completed"
        # 节点通过后只激活紧邻的后续节点，避免一次提交跳过路径约束。
        next_node = PathNode.objects.filter(path=node.path, order_index__gt=node.order_index).first()
        if next_node and next_node.status == "locked":
            next_node.status = "active"
            next_node.save()
    else:
        node.status = "failed"

    node.save()
    progress.save()


# 维护意图：记录节点考试答题历史，并返回 KT 所需的答题轨迹
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def persist_node_exam_histories(*, user, node: PathNode, answers: dict[str, Any], questions, question_result_map: dict[str, dict[str, Any]]) -> list[dict[str, int]]:
    """记录节点考试答题历史，并返回 KT 所需的答题轨迹。"""
    from assessments.models import AnswerHistory

    answer_history_records: list[dict[str, int]] = []
    for question in questions:
        # 每题持久化一条 AnswerHistory，后续 KT 使用全量课程轨迹而不是单次提交。
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


# 维护意图：加载当前课程下已记录的 KT 答题轨迹
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_node_kt_history(context: NodeExamMasteryRefresh) -> list[dict[str, int]]:
    """加载当前课程下已记录的 KT 答题轨迹。"""
    from assessments.models import AnswerHistory

    all_history = list(
        AnswerHistory.objects.filter(user=context.user, course=context.node.path.course)
        .order_by("answered_at")
        .values("question_id", "knowledge_point_id", "is_correct")
    )
    return [
        {
            "question_id": history["question_id"],
            "knowledge_point_id": history["knowledge_point_id"],
            "correct": 1 if history["is_correct"] else 0,
        }
        for history in all_history
    ]


# 维护意图：从本次小测统计或节点绑定知识点中提取 KT 预测目标
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_node_knowledge_point_ids(context: NodeExamMasteryRefresh) -> list[int]:
    """从本次小测统计或节点绑定知识点中提取 KT 预测目标。"""
    if context.point_stats:
        return list(context.point_stats.keys())
    return [context.node.knowledge_point_id] if context.node.knowledge_point_id else []


# 维护意图：将 KT 预测掌握度回写到 KnowledgeMastery
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def persist_node_kt_predictions(context: NodeExamMasteryRefresh, kt_predictions: dict[int, float]) -> None:
    """将 KT 预测掌握度回写到 KnowledgeMastery。"""
    for knowledge_point_id, mastery_value in kt_predictions.items():
        try:
            mastery, _ = KnowledgeMastery.objects.get_or_create(
                user=context.user,
                course=context.node.path.course,
                knowledge_point_id=knowledge_point_id,
            )
            mastery.mastery_rate = max(0, min(1, round(float(mastery_value), 4)))
            mastery.save()
        except (DatabaseError, TypeError, ValueError) as error:
            logger.warning(
                build_log_message(
                    "kt.node_exam.mastery_update_fail",
                    user_id=context.user.id,
                    exam_id=context.node.exam_id,
                    knowledge_point_id=knowledge_point_id,
                    error=error,
                )
            )


# 维护意图：KT 不可用时用小测通过状态做保守掌握度加减分
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def apply_node_mastery_fallback(context: NodeExamMasteryRefresh) -> float:
    """KT 不可用时用小测通过状态做保守掌握度加减分。"""
    mastery_update = 0.1 if (context.total_score > 0 and context.score >= context.total_score * 0.6) else -0.1
    if context.node.knowledge_point:
        mastery, _ = KnowledgeMastery.objects.get_or_create(
            user=context.user,
            course=context.node.path.course,
            knowledge_point=context.node.knowledge_point,
        )
        mastery.mastery_rate = max(0, min(1, float(mastery.mastery_rate) + mastery_update))
        mastery.save()
        context.progress.mastery_after = mastery.mastery_rate
        context.progress.save()
    return mastery_update


# 维护意图：尝试用 KT 刷新掌握度；失败时降级到简单加减分
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def refresh_node_exam_mastery(context: NodeExamMasteryRefresh) -> str | float:
    """尝试用 KT 刷新掌握度；失败时降级到简单加减分。"""
    try:
        from ai_services.services.kt_service import kt_service

        # KT 属于智能服务增强链路；缺失历史、模型或依赖时必须降级，不阻断答题提交。
        kt_history = load_node_kt_history(context)
        knowledge_point_ids = resolve_node_knowledge_point_ids(context)
        if not kt_history or not knowledge_point_ids:
            raise ValueError("无可用的答题历史或知识点")

        kt_result = kt_service.predict_mastery(
            user_id=context.user.id,
            course_id=context.node.path.course_id,
            answer_history=kt_history,
            knowledge_points=knowledge_point_ids,
        )
        kt_predictions = kt_result.get("predictions", {})
        persist_node_kt_predictions(context, kt_predictions)

        context.progress.mastery_after = context.score / context.total_score if context.total_score > 0 else 0
        context.progress.save()
        logger.info(
            build_log_message(
                "kt.node_exam.success",
                user_id=context.user.id,
                exam_id=context.node.exam_id,
                answer_count=len(kt_history),
                prediction_count=len(kt_predictions),
            )
        )
        return "kt"
    except (DatabaseError, ImportError, RuntimeError, TypeError, ValueError) as error:
        logger.error(
            build_log_message(
                "kt.node_exam.fail",
                user_id=context.user.id,
                exam_id=context.node.exam_id,
                error=error,
            )
        )
        return apply_node_mastery_fallback(context)
