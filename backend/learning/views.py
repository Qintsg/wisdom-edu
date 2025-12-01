#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
学习路径模块视图。
提供学习路径、节点、进度相关的 API 端点。
@Project : wisdom-edu
@File : views.py
@Author : Qintsg
@Date : 2026-03-23
"""

import logging
from typing import cast

from django.db import DatabaseError, transaction, models
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.defense_demo import (
    advance_defense_demo_path,
    complete_defense_demo_stage_test,
    get_defense_demo_stage_test_payload,
    get_defense_demo_visible_order,
    is_defense_demo_student,
)
from common.logging_utils import build_log_message
from common.responses import success_response, error_response
from common.utils import (
    build_answer_display,
    build_normalized_score_map,
    check_answer,
    decorate_question_options,
    extract_answer_value,
    normalize_question_options,
    score_questions,
    serialize_answer_payload,
    validate_course_exists,
)
from assessments.models import AssessmentStatus
from exams.models import ExamQuestion, ExamSubmission
from knowledge.models import KnowledgePoint, KnowledgeMastery
from platform_ai.rag import student_learning_rag
from users.models import User

from .models import LearningPath, PathNode, NodeProgress

logger = logging.getLogger(__name__)


def _get_authenticated_user(request) -> User:
    """
    将请求中的用户对象收窄为项目内 User 类型。
    :param request: DRF 请求对象。
    :return: 已认证用户。
    """
    return cast(User, request.user)


def _coerce_string_list(raw_value: object) -> list[str]:
    """
    将 JSONField 中的资源 ID 值规整为字符串列表。
    :param raw_value: 原始 JSONField 值。
    :return: 字符串 ID 列表。
    """
    if not isinstance(raw_value, list):
        return []
    return [str(item) for item in raw_value]


def _path_node_sort_key(node: PathNode) -> tuple[int, int, int]:
    """
    生成仪表盘节点预览的排序键，优先展示未完成节点。
    :param node: 路径节点对象。
    :return: 排序键元组。
    """
    completion_rank = 1 if node.status == "completed" else 0
    return (completion_rank, node.order_index, node.id)


def _clean_text_for_llm(text: str, max_len: int = 80) -> str:
    """
    截取题干摘要供 LLM 选题使用。
    :param text: 原始题干文本。
    :param max_len: 最大截断长度。
    :return: 清洗后的短文本。
    """
    if not text:
        return ""
    import re
    from django.utils.html import strip_tags

    cleaned_text = strip_tags(str(text)).strip()
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    return cleaned_text[:max_len]


def _build_exam_score_map(exam, exam_questions):
    """
    构建试卷题目分值映射。
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


def _serialize_path_nodes(path, max_visible_order: int | None = None) -> list[dict[str, object]]:
    """
    统一序列化学习路径节点。
    :param path: 学习路径对象。
    :return: 节点序列化结果列表。
    """

    query = path.nodes.select_related("knowledge_point").prefetch_related("resources")
    if max_visible_order is not None:
        query = query.filter(order_index__lte=max_visible_order)
    ordered_nodes = list(query.order_by("order_index", "id"))
    return [
        {
            "node_id": node.id,
            "title": node.title,
            "goal": node.goal,
            "criterion": node.criterion,
            "status": node.status,
            "suggestion": node.suggestion,
            "node_type": node.node_type,
            "estimated_minutes": node.estimated_minutes,
            "knowledge_point_id": node.knowledge_point_id,
            "knowledge_point_name": node.knowledge_point.name
            if node.knowledge_point
            else None,
            "tasks_count": len(node.resources.all()) + (1 if node.exam else 0),
            "order_index": node.order_index,
        }
        for node in ordered_nodes
    ]


def _snapshot_mastery_for_points(
    user, course_id: int, point_ids: list[int]
) -> dict[int, float]:
    """
    读取指定知识点的当前掌握度快照。
    :param user: 当前用户对象。
    :param course_id: 课程 ID。
    :param point_ids: 知识点 ID 列表。
    :return: 以知识点 ID 为键的掌握度映射。
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


def _average_mastery(mastery_snapshot: dict[int, float]) -> float | None:
    """
    计算一组知识点掌握度的平均值。
    :param mastery_snapshot: 掌握度快照。
    :return: 平均掌握度，缺失时返回 None。
    """

    if not mastery_snapshot:
        return None
    values = list(mastery_snapshot.values())
    return round(sum(values) / len(values), 4)


def _build_mastery_change_payload(
    before_snapshot: dict[int, float], after_snapshot: dict[int, float]
) -> list[dict[str, object]]:
    """
    构建掌握度变化明细。
    :param before_snapshot: 调整前掌握度快照。
    :param after_snapshot: 调整后掌握度快照。
    :return: 掌握度变化列表。
    """

    point_ids = sorted(set(before_snapshot.keys()) | set(after_snapshot.keys()))
    point_name_map = {
        row.id: row.name for row in KnowledgePoint.objects.filter(id__in=point_ids)
    }
    mastery_changes: list[dict[str, object]] = []
    for point_id in point_ids:
        before_rate = round(float(before_snapshot.get(point_id, 0.0)), 4)
        after_rate = round(float(after_snapshot.get(point_id, before_rate)), 4)
        mastery_changes.append(
            {
                "knowledge_point_id": point_id,
                "knowledge_point_name": point_name_map.get(
                    point_id, f"知识点 {point_id}"
                ),
                "mastery_before": before_rate,
                "mastery_after": after_rate,
                "improvement": round(after_rate - before_rate, 4),
            }
        )
    return mastery_changes


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_learning_path(request):
    """
    获取个性化学习路径
    GET /api/learning-path
    """
    course_id = request.query_params.get("course_id")
    if not course_id:
        return error_response(msg="缺少课程ID")

    if not validate_course_exists(course_id):
        return error_response(msg="课程不存在", code=404)

    user = _get_authenticated_user(request)

    # 初始评测门禁：未完成全局测评或课程知识测评时，引导前端进入对应评测流程。
    has_global_ability = user.ability_scores.exists()
    has_global_habit = hasattr(user, "habit_preference")
    status = AssessmentStatus.objects.filter(user=user, course_id=course_id).first()
    knowledge_done = status.knowledge_done if status else False
    if not (has_global_ability and has_global_habit and knowledge_done):
        next_step = "ability"
        next_step_msg = "请先完成学习能力评测"
        if has_global_ability and not has_global_habit:
            next_step = "habit"
            next_step_msg = "请先完成学习偏好问卷"
        elif has_global_ability and has_global_habit and not knowledge_done:
            next_step = "knowledge"
            next_step_msg = "请先完成本课程知识评测"

        return success_response(
            data={
                "path_id": None,
                "nodes": [],
                "need_assessment": True,
                "next_step": next_step,
                "next_step_msg": next_step_msg,
                "dynamic": False,
                "generating": False,
            },
            msg="请先完成初始评测",
        )

    path = (
        LearningPath.objects.filter(user=user, course_id=course_id)
        .prefetch_related("nodes")
        .first()
    )

    if not path:
        path = generate_initial_path(user, course_id)

    visible_order = (
        get_defense_demo_visible_order(path, user)
        if is_defense_demo_student(user, path.course)
        else None
    )

    return success_response(
        data={
            "path_id": path.id,
            "nodes": _serialize_path_nodes(path, max_visible_order=visible_order),
            "dynamic": path.is_dynamic,
            "generating": False,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def adjust_learning_path(request):
    """
    刷新/调整学习路径
    POST /api/learning-path/adjust
    """
    course_id = request.data.get("course_id")
    reason = request.data.get("reason", "")

    if not course_id:
        return error_response(msg="缺少课程ID")

    if not validate_course_exists(course_id):
        return error_response(msg="课程不存在", code=404)

    user = _get_authenticated_user(request)
    path = LearningPath.objects.filter(user=user, course_id=course_id).first()

    if not path:
        return error_response(msg="学习路径不存在", code=404)

    # 用户主动刷新时，先调用KT更新掌握度，再增量重建路径
    if reason in ["manual_refresh", "rebuild", "refresh"]:
        try:
            from ai_services.services import kt_service
            from assessments.models import AnswerHistory

            answer_records = (
                AnswerHistory.objects.filter(user=user, course_id=course_id)
                .order_by("answered_at")
                .values("question_id", "knowledge_point_id", "is_correct")
            )
            if answer_records.exists():
                history = [
                    {
                        "question_id": r["question_id"],
                        "knowledge_point_id": r["knowledge_point_id"],
                        "correct": 1 if r["is_correct"] else 0,
                    }
                    for r in answer_records
                    if r["knowledge_point_id"]
                ]
                kt_result = kt_service.predict_mastery(
                    user_id=user.id, course_id=course_id, answer_history=history
                )
                kt_predictions = kt_result.get("predictions") or {}
                logger.info(
                    build_log_message(
                        "kt.path_refresh.success",
                        user_id=user.id,
                        course_id=course_id,
                        answer_count=len(history),
                        prediction_count=len(kt_predictions),
                    )
                )
                for kp_id, rate in kt_predictions.items():
                    try:
                        KnowledgeMastery.objects.update_or_create(
                            user=user,
                            course_id=course_id,
                            knowledge_point_id=kp_id,
                            defaults={"mastery_rate": float(rate)},
                        )
                    except Exception as e:
                        logger.warning(
                            build_log_message(
                                "kt.path_refresh.mastery_update_fail",
                                user_id=user.id,
                                course_id=course_id,
                                knowledge_point_id=kp_id,
                                error=e,
                            )
                        )
        except Exception as e:
            logger.error(
                build_log_message(
                    "kt.path_refresh.fail",
                    user_id=user.id,
                    course_id=course_id,
                    error=e,
                )
            )

        with transaction.atomic():
            # 保留已完成/进行中/已跳过/失败的节点，只删除locked状态的未来节点
            preserved_statuses = ("completed", "active", "skipped", "failed")
            preserved_nodes = list(path.nodes.filter(status__in=preserved_statuses))
            preserved_kp_ids = {
                n.knowledge_point_id for n in preserved_nodes if n.knowledge_point_id
            }

            # 删除所有locked节点
            path.nodes.filter(status="locked").delete()

            max_order = max((n.order_index for n in preserved_nodes), default=-1)
            next_order = max_order + 1

            # 仅重建尚未被保留节点覆盖的已发布知识点。
            remaining_points = (
                KnowledgePoint.objects.filter(course_id=course_id, is_published=True)
                .exclude(id__in=preserved_kp_ids)
                .order_by("order")
            )

            mastery_dict = {
                m.knowledge_point_id: float(m.mastery_rate)
                for m in KnowledgeMastery.objects.filter(user=user, course_id=course_id)
            }
            sorted_remaining = sorted(
                remaining_points, key=lambda p: mastery_dict.get(p.id, 0)
            )

            # 用配置参数控制节点上限和测试间隔
            from common.config import AppConfig

            max_nodes = AppConfig.max_path_nodes()
            test_interval = AppConfig.path_test_interval()

            # 新节点数量 = 上限 - 已保留节点数
            remaining_quota = max(0, max_nodes - len(preserved_nodes))

            # 批量创建新节点
            nodes_to_create = []
            node_resource_map = []
            study_batch = []
            order_idx = next_order

            for point in sorted_remaining[:remaining_quota]:
                mastery = mastery_dict.get(point.id, 0)
                nodes_to_create.append(
                    PathNode(
                        path=path,
                        knowledge_point=point,
                        title=f"{point.name}" + ("提升" if mastery > 0.5 else "基础"),
                        goal=f"掌握{point.name}的核心概念及应用",
                        criterion="完成所有学习资源和测验，正确率≥80%",
                        suggestion=f"{'巩固' if mastery > 0.5 else '重点学习'}{point.name}相关内容。",
                        status="locked",
                        order_index=order_idx,
                        node_type="study",
                        estimated_minutes=max(
                            15, min(60, int(30 + (1 - mastery) * 30))
                        ),
                    )
                )
                node_resource_map.append(point)
                study_batch.append(point)
                order_idx += 1

                if len(study_batch) >= test_interval:
                    kp_name_list = [p.name for p in study_batch]
                    test_names = "、".join(kp_name_list)
                    if len(kp_name_list) > 3:
                        test_title = f"阶段测试：{'、'.join(kp_name_list[:3])}等{len(kp_name_list)}个知识点"
                    else:
                        test_title = f"阶段测试：{test_names}"
                    nodes_to_create.append(
                        PathNode(
                            path=path,
                            knowledge_point=study_batch[-1],
                            title=test_title,
                            goal=f"检验{test_names}的掌握程度",
                            criterion="正确率≥80%视为通过",
                            suggestion="综合运用前几个知识点完成测试题。",
                            status="locked",
                            order_index=order_idx,
                            node_type="test",
                            estimated_minutes=15,
                        )
                    )
                    node_resource_map.append(None)
                    study_batch = []
                    order_idx += 1

            if nodes_to_create:
                created_nodes = PathNode.objects.bulk_create(nodes_to_create)
                for node, point in zip(created_nodes, node_resource_map):
                    if point is not None:
                        resources = point.resources.filter(is_visible=True)[:5]
                        if resources:
                            node.resources.set(resources)

            # 确保至少有一个active节点（如果全部保留节点已完成）
            if not path.nodes.filter(status="active").exists():
                first_locked = (
                    path.nodes.filter(status="locked").order_by("order_index").first()
                )
                if first_locked:
                    first_locked.status = "active"
                    first_locked.save()

            path.is_dynamic = True
            path.ai_reason = (
                "已根据KT预测和AI分析，保留你的学习进度并重新规划了未完成部分。"
            )
            path.save()

        nodes = []
        for node in (
            path.nodes.select_related("knowledge_point")
            .prefetch_related("resources")
            .order_by("order_index")
        ):
            nodes.append(
                {
                    "node_id": node.id,
                    "title": node.title,
                    "goal": node.goal,
                    "criterion": node.criterion,
                    "status": node.status,
                    "suggestion": node.suggestion,
                    "node_type": node.node_type,
                    "knowledge_point_id": node.knowledge_point_id,
                    "knowledge_point_name": node.knowledge_point.name
                    if node.knowledge_point
                    else None,
                    "tasks_count": len(node.resources.all()) + (1 if node.exam else 0),
                }
            )

        return success_response(
            data={
                "path_id": path.id,
                "nodes": nodes,
                "ai_reason": path.ai_reason,
                "dynamic": path.is_dynamic,
            },
            msg="路径已刷新",
        )

    # 兼容原有简化调整逻辑
    with transaction.atomic():
        # 查找未通过的节点
        failed_nodes = path.nodes.filter(status="failed")

        for failed_node in failed_nodes:
            # 检查是否已经有补习节点
            existing = path.nodes.filter(
                title__contains="强化练习",
                order_index__gt=failed_node.order_index,
                is_inserted=True,
            ).exists()

            if not existing and failed_node.knowledge_point:
                # 插入补习节点
                # 后移后续节点
                path.nodes.filter(order_index__gt=failed_node.order_index).update(
                    order_index=models.F("order_index") + 1
                )

                PathNode.objects.create(
                    path=path,
                    knowledge_point=failed_node.knowledge_point,
                    title=f"{failed_node.knowledge_point.name}强化练习",
                    goal=f"纠正对{failed_node.knowledge_point.name}的误解并掌握正确用法",
                    criterion="完成强化练习及复测",
                    suggestion=f"针对你在{failed_node.knowledge_point.name}测试中的错误，请完成以下强化练习。",
                    status="active",
                    order_index=failed_node.order_index + 1,
                    is_inserted=True,
                )

                # 将failed节点重新激活以便学生重试
                failed_node.status = "active"
                failed_node.save()

        path.is_dynamic = True
        path.ai_reason = (
            f"由于你在学习过程中出现困难，我们调整了学习路径以帮助你更好地掌握知识。"
        )
        path.save()

    path.refresh_from_db()
    nodes = []
    for node in path.nodes.prefetch_related("resources").all():
        nodes.append(
            {
                "node_id": node.id,
                "title": node.title,
                "goal": node.goal,
                "criterion": node.criterion,
                "status": node.status,
                "suggestion": node.suggestion,
                "tasks_count": len(node.resources.all()) + (1 if node.exam else 0),
            }
        )

    return success_response(
        data={
            "path_id": path.id,
            "nodes": nodes,
            "ai_reason": path.ai_reason,
            "dynamic": path.is_dynamic,
        },
        msg="路径已更新",
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_path_node_detail(request, node_id):
    """
    获取节点任务详情与资源列表
    GET /api/path-nodes/{node_id}
    """
    course_id = request.query_params.get("course_id")

    user = _get_authenticated_user(request)

    try:
        query = PathNode.objects.select_related("knowledge_point").filter(
            id=node_id, path__user=user
        )
        if course_id:
            query = query.filter(path__course_id=course_id)
        node = query.get()
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    progress, _ = NodeProgress.objects.get_or_create(node=node, user=user)
    completed_resource_ids = _coerce_string_list(progress.completed_resources)

    resources = []

    exercises = []
    if node.exam:
        exercises.append(
            {"exam_id": node.exam.id, "title": node.exam.title, "required": True}
        )

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

    return success_response(
        data={
            "node_id": node.id,
            "node_title": node.title,
            "knowledge_point_id": node.knowledge_point_id,
            "knowledge_point_name": node.knowledge_point.name
            if node.knowledge_point
            else None,
            "goal": node.goal,
            "resources": resources,
            "exercises": exercises,
            "status": node.status,
            "progress": {
                "resources_completed": len(completed_resource_ids),
                "resources_total": 0,
                "exercises_completed": len(progress.completed_exams),
                "exercises_total": 1 if node.exam else 0,
            },
            "mastery_before": float(progress.mastery_before)
            if progress.mastery_before is not None
            else current_mastery_rate,
            "mastery_after": float(progress.mastery_after)
            if progress.mastery_after is not None
            else None,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_node_resource(request, node_id, resource_id):
    """
    标记资源学习完成
    POST /api/path-nodes/{node_id}/resources/{resource_id}/complete
    支持内部资源ID（整数）和外部资源ID（ext_前缀字符串）
    """
    user = _get_authenticated_user(request)

    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    progress, _ = NodeProgress.objects.get_or_create(node=node, user=user)

    # 统一用字符串比对（兼容int和ext_前缀）
    str_id = str(resource_id)
    completed_resource_ids = _coerce_string_list(progress.completed_resources)
    if str_id not in completed_resource_ids:
        completed_resource_ids.append(str_id)
        progress.completed_resources = completed_resource_ids
        progress.save()

    return success_response(
        data={
            "message": f"资源 {resource_id} 已完成学习",
            "progress": {
                "resources_completed": len(progress.completed_resources),
                "resources_total": 0,
                "exercises_completed": len(progress.completed_exams),
                "exercises_total": 1 if node.exam else 0,
            },
        },
        msg="资源已标记为已学习",
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_node_exam(request, node_id, exam_id):
    """
    提交节点练习/小测验结果
    POST /api/path-nodes/{node_id}/exams/{exam_id}/submit
    """
    user = _get_authenticated_user(request)
    answers = request.data.get("answers", {})

    # 验证 answers 格式
    if not isinstance(answers, dict):
        return error_response(msg="答案格式错误，应为字典格式")

    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    if not node.exam or node.exam.id != exam_id:
        return error_response(msg="测验不属于该节点", code=404)

    exam = node.exam
    exam_questions = list(
        ExamQuestion.objects.filter(exam=exam).select_related("question")
    )
    questions = [eq.question for eq in exam_questions]
    score_map = _build_exam_score_map(exam, exam_questions)
    grading = score_questions(answers, questions, score_map=score_map)
    score = grading["score"]
    mistakes = grading["mistakes"]
    point_stats: dict[int, dict[str, object]] = grading["point_stats"]
    question_result_map = {
        str(item["question_id"]): item for item in grading["question_results"]
    }
    total_score = float(exam.total_score or grading["total_score"] or 0)

    passed = score >= float(exam.pass_score)

    # 保存提交
    submission, _ = ExamSubmission.objects.update_or_create(
        exam=exam,
        user=user,
        defaults={"answers": answers, "score": score, "is_passed": passed},
    )

    # 更新节点进度
    progress, _ = NodeProgress.objects.get_or_create(node=node, user=user)
    if exam.id not in progress.completed_exams:
        progress.completed_exams.append(exam.id)

    # 更新节点状态
    if passed:
        node.status = "completed"
        # 解锁下一个节点
        next_node = PathNode.objects.filter(
            path=node.path, order_index__gt=node.order_index
        ).first()
        if next_node and next_node.status == "locked":
            next_node.status = "active"
            next_node.save()
    else:
        node.status = "failed"

    node.save()
    progress.save()

    # 记录答题历史并使用KT服务更新掌握度
    try:
        from assessments.models import AnswerHistory
        from ai_services.services.kt_service import kt_service

        # 记录每道题的答题历史
        for q in questions:
            q_id = str(q.id)
            result = question_result_map.get(q_id, {})
            student_answer = answers.get(q_id, "")
            correct_answer = result.get(
                "correct_answer", extract_answer_value(q.answer)
            )
            is_correct = result.get(
                "is_correct", check_answer(q.question_type, student_answer, q.answer)
            )
            kp = q.knowledge_points.first() if hasattr(q, "knowledge_points") else None
            AnswerHistory.objects.create(
                user=user,
                course=node.path.course,
                question=q,
                knowledge_point=kp,
                student_answer=serialize_answer_payload(
                    q.question_type, student_answer
                ),
                correct_answer=serialize_answer_payload(
                    q.question_type, correct_answer
                ),
                is_correct=is_correct,
                score=result.get("earned_score", 0),
                source="node_exam",
            )

        # 汇总整门课程答题历史，供 KT 重算掌握度。
        all_history = list(
            AnswerHistory.objects.filter(user=user, course=node.path.course)
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

        kp_ids = (
            list(point_stats.keys())
            if point_stats
            else ([node.knowledge_point_id] if node.knowledge_point_id else [])
        )
        if kt_history and kp_ids:
            kt_result = kt_service.predict_mastery(
                user_id=user.id,
                course_id=node.path.course_id,
                answer_history=kt_history,
                knowledge_points=kp_ids,
            )
            kt_predictions = kt_result.get("predictions", {})
            for kp_id, mastery_val in kt_predictions.items():
                try:
                    mastery_obj, _ = KnowledgeMastery.objects.get_or_create(
                        user=user, course=node.path.course, knowledge_point_id=kp_id
                    )
                    mastery_obj.mastery_rate = max(0, min(1, round(mastery_val, 4)))
                    mastery_obj.save()
                except Exception as e:
                    logger.warning(
                        build_log_message(
                            "kt.node_exam.mastery_update_fail",
                            user_id=user.id,
                            exam_id=exam.id,
                            knowledge_point_id=kp_id,
                            error=e,
                        )
                    )

            progress.mastery_after = score / total_score if total_score > 0 else 0
            progress.save()
            mastery_update = "kt"
            logger.info(
                build_log_message(
                    "kt.node_exam.success",
                    user_id=user.id,
                    exam_id=exam.id,
                    answer_count=len(kt_history),
                    prediction_count=len(kt_predictions),
                )
            )
        else:
            raise ValueError("无可用的答题历史或知识点")

    except Exception as e:
        logger.error(
            build_log_message(
                "kt.node_exam.fail", user_id=user.id, exam_id=exam.id, error=e
            )
        )
        # 降级：使用简单 ±0.1 算法
        mastery_update = 0.1 if passed else -0.1
        if node.knowledge_point:
            mastery, _ = KnowledgeMastery.objects.get_or_create(
                user=user, course=node.path.course, knowledge_point=node.knowledge_point
            )
            mastery.mastery_rate = max(
                0, min(1, float(mastery.mastery_rate) + mastery_update)
            )
            mastery.save()
            progress.mastery_after = mastery.mastery_rate
            progress.save()

    return success_response(
        data={
            "score": score,
            "total_score": total_score,
            "passed": passed,
            "mistakes": mistakes,
            "mastery_update": mastery_update,
            "node_status": node.status,
        },
        msg="测验提交成功",
    )


def generate_initial_path(user, course_id):
    """生成初始学习路径"""
    from courses.models import Course
    from ai_services.services.path_service import PathService

    course = Course.objects.get(id=course_id)
    return PathService().generate_path(user, course)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_learning_progress(request):
    """
    获取学习进度
    GET /api/student/learning-progress
    """
    course_id = request.query_params.get("course_id")
    if not course_id:
        return error_response(msg="缺少课程ID")

    user = _get_authenticated_user(request)
    path = LearningPath.objects.filter(user=user, course_id=course_id).first()

    if not path:
        return success_response(
            data={
                "total_nodes": 0,
                "completed_nodes": 0,
                "progress_rate": 0,
                "current_node": None,
            }
        )

    total_nodes = path.nodes.count()
    completed_nodes = path.nodes.filter(status="completed").count()
    progress_rate = completed_nodes / total_nodes if total_nodes > 0 else 0

    # 计算累计学习时长（分钟）：已完成节点的估计时间之和
    from django.db.models import Sum

    study_time = (
        path.nodes.filter(status="completed").aggregate(total=Sum("estimated_minutes"))[
            "total"
        ]
        or 0
    )

    current_node = path.nodes.filter(status="active").first()

    return success_response(
        data={
            "total_nodes": total_nodes,
            "completed_nodes": completed_nodes,
            "progress_rate": round(progress_rate, 2),
            "progress": round(progress_rate, 2),
            "study_time": study_time,
            "current_node": {"node_id": current_node.id, "title": current_node.title}
            if current_node
            else None,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_learning_node(request, node_id):
    """
    开始学习节点
    POST /api/path-nodes/{node_id}/start
    """
    user = _get_authenticated_user(request)

    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    if node.status == "locked":
        return error_response(msg="该节点尚未解锁")

    node.status = "active"
    try:
        node.save(update_fields=["status"])
    except DatabaseError:
        return error_response(msg="节点已被刷新，请重新加载路径", code=409)

    # 创建或更新进度记录（用于记录学习开始时间等）
    NodeProgress.objects.get_or_create(node=node, user=user)

    return success_response(
        data={"node_id": node.id, "status": node.status}, msg="开始学习"
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_path_node(request, node_id):
    """
    完成学习节点
    POST /api/path-nodes/{node_id}/complete
    """
    user = _get_authenticated_user(request)

    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    # DEFENSE_DEMO_PRESET: 答辩链路需要固定节点顺序，学习节点完成时只推进到
    # 下一个预置节点，避免调用完整路径重排后破坏现场讲稿和截图顺序。
    if is_defense_demo_student(user, node.path.course):
        advance_defense_demo_path(node, user)
    else:
        node.status = "completed"
        try:
            node.save(update_fields=["status"])
        except DatabaseError:
            return error_response(msg="节点已被刷新，请重新加载路径", code=409)

        # 只解锁下一个节点，不重新生成全量路径，避免过早插入补强节点
        from ai_services.services.path_service import PathService

        PathService().unlock_next_node(node)

    return success_response(
        data={
            "node_id": node.id,
            "status": node.status,
            "path_refreshed": not is_defense_demo_student(user, node.path.course),
        },
        msg="节点已完成",
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def skip_path_node(request, node_id):
    """
    跳过学习节点
    POST /api/path-nodes/{node_id}/skip
    """
    user = _get_authenticated_user(request)
    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    if is_defense_demo_student(user, node.path.course):
        advance_defense_demo_path(node, user, mark_skipped=True)
    else:
        node.status = "skipped"
        node.save(update_fields=["status"])

        # 只解锁下一个节点，不重新生成全量路径
        from ai_services.services.path_service import PathService

        PathService().unlock_next_node(node)

    return success_response(
        data={
            "node_id": node.id,
            "status": node.status,
            "path_refreshed": not is_defense_demo_student(user, node.path.course),
        },
        msg="节点已跳过",
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_node_resources(request, node_id):
    """
    获取节点资源列表（兼容端点）
    GET /api/path-nodes/{node_id}/resources

    资源现在通过AI实时推荐，此端点返回空列表，保留向前兼容。
    前端应使用 get_ai_resources 获取推荐资源。
    """
    user = _get_authenticated_user(request)

    if not PathNode.objects.filter(id=node_id, path__user=user).exists():
        return error_response(msg="节点不存在", code=404)

    return success_response(data={"resources": []})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_ai_resources(request, node_id):
    """
    获取节点的AI推荐资源（内部+外部）
    GET /api/student/path-nodes/{node_id}/ai-resources

    两次独立LLM调用：
    1. recommend_internal_resources() — 从课程资源库中筛选最相关的内部资源
    2. recommend_external_resources() — 推荐外部学习资源
    返回 {internal_resources: [...], external_resources: [...]}
    """
    user = _get_authenticated_user(request)

    try:
        node = PathNode.objects.select_related("knowledge_point", "path__course").get(
            id=node_id, path__user=user
        )
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    progress = NodeProgress.objects.filter(node=node, user=user).first()
    mastery_val = None
    if progress and progress.mastery_after is not None:
        mastery_val = float(progress.mastery_after)
    elif progress and progress.mastery_before is not None:
        mastery_val = float(progress.mastery_before)
    completed_ids = (
        set(_coerce_string_list(progress.completed_resources))
        if progress
        else set()
    )
    recommendation_payload = student_learning_rag.recommend_resources_for_node(
        node=node,
        user=user,
        mastery_value=mastery_val,
        completed_resource_ids=completed_ids,
        internal_count=2,
        external_count=0 if node.node_type == "test" else 2,
    )
    return success_response(
        data={
            "internal_resources": recommendation_payload.get("internal_resources", []),
            "external_resources": recommendation_payload.get("external_resources", []),
            "service_status": "available",
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_node_exams(request, node_id):
    """
    获取节点测验列表
    GET /api/path-nodes/{node_id}/exams
    """
    user = _get_authenticated_user(request)

    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    exams = []
    if node.exam:
        exams.append(
            {
                "exam_id": node.exam.id,
                "title": node.exam.title,
                "duration": node.exam.duration,
                "pass_score": float(node.exam.pass_score)
                if node.exam.pass_score
                else 60,
            }
        )

    return success_response(data={"exams": exams})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pause_node_resource(request, node_id, resource_id):
    """
    暂停资源学习
    POST /api/student/path-nodes/{node_id}/resources/{resource_id}/pause
    """
    user = _get_authenticated_user(request)

    try:
        node = PathNode.objects.get(id=node_id, path__user=user)
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    # 记录暂停进度
    progress, _ = NodeProgress.objects.get_or_create(
        user=user,
        node=node,
        defaults={"status": "in_progress"},
    )

    # 存储暂停位置（如有前端传来的 position）
    position = request.data.get("position", 0)
    if not progress.extra_data:
        progress.extra_data = {}
    progress.extra_data[f"resource_{resource_id}_position"] = position
    progress.save()

    return success_response(msg="已暂停")


# ============ 阶段测试（内嵌做题）============


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_stage_test(request, node_id):
    """
    获取阶段测试题目（内嵌做题）
    GET /api/student/path-nodes/{node_id}/stage-test

    对于 node_type='test' 的测试节点，从该节点之前的学习节点覆盖的知识点中抽取题目。
    """
    from assessments.models import Question
    from exams.models import Exam, ExamQuestion

    user = _get_authenticated_user(request)
    try:
        node = PathNode.objects.select_related("path", "knowledge_point").get(
            id=node_id, path__user=user
        )
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    if node.node_type != "test":
        return error_response(msg="该节点不是测试节点")

    # 收集该测试节点之前、直到上一个测试节点之间的所有学习节点的知识点
    prev_test = (
        PathNode.objects.filter(
            path=node.path, order_index__lt=node.order_index, node_type="test"
        )
        .order_by("-order_index")
        .first()
    )
    lower_bound = prev_test.order_index if prev_test else -1

    preceding_study_nodes = PathNode.objects.filter(
        path=node.path,
        order_index__gt=lower_bound,
        order_index__lt=node.order_index,
        node_type="study",
    )

    kp_ids = set()
    for sn in preceding_study_nodes:
        if sn.knowledge_point_id:
            kp_ids.add(sn.knowledge_point_id)

    if not kp_ids:
        if node.knowledge_point_id:
            kp_ids.add(node.knowledge_point_id)

    # 优先使用节点显式绑定的测试试卷，这样教师和答辩预置都能稳定控制题目顺序。
    exam_set = node.exam if node.exam_id else None
    if not exam_set:
        exam_set = (
            Exam.objects.filter(
                course=node.path.course,
                exam_type="question_set",
                status="published",
            )
            .filter(questions__knowledge_points__id__in=kp_ids)
            .distinct()
            .first()
        )

    if exam_set:
        # 使用预设套题
        eq_list = (
            ExamQuestion.objects.filter(exam=exam_set)
            .select_related("question")
            .order_by("order")
        )
        questions = [eq.question for eq in eq_list]
    else:
        # 从题库中收集候选题目（按知识点关联）
        candidates = list(
            Question.objects.filter(
                course=node.path.course,
                knowledge_points__id__in=kp_ids,
                is_visible=True,
            )
            .distinct()
            .prefetch_related("knowledge_points")
        )

        # 降级策略：当知识点关联匹配无题时，放宽到课程级别查询
        if not candidates:
            logger.info(
                "阶段测试KP匹配无题，降级到课程级别查询: node_id=%s, kp_ids=%s",
                node_id,
                kp_ids,
            )
            candidates = list(
                Question.objects.filter(course=node.path.course, is_visible=True)
                .distinct()
                .prefetch_related("knowledge_points")
            )

        kp_names = [
            KnowledgePoint.objects.filter(id=kid).values_list("name", flat=True).first()
            or ""
            for kid in kp_ids
        ]

        if len(candidates) <= 10:
            questions = candidates
        else:
            # LLM 智能选题
            try:
                from ai_services.services import llm_service as _llm

                candidate_info = [
                    {
                        "id": q.id,
                        "content": _clean_text_for_llm(q.content),
                        "type": q.question_type,
                        "difficulty": q.difficulty,
                    }
                    for q in candidates[:50]  # 限制输入量，取前50个候选
                ]
                selected_ids = _llm.select_stage_test_questions(
                    candidates=candidate_info,
                    kp_names=kp_names,
                    count=10,
                )
                if selected_ids:
                    id_set = set(selected_ids)
                    questions = [q for q in candidates if q.id in id_set]
                    if not questions:
                        questions = candidates[:10]
                else:
                    questions = candidates[:10]
            except Exception as e:
                logger.warning("LLM选题失败，回退随机选题: %s", e)
                import random

                random.shuffle(candidates)
                questions = candidates[:10]

    progress = NodeProgress.objects.filter(node=node, user=user).first()
    stage_test_result = None
    if progress and isinstance(progress.extra_data, dict):
        stage_test_result = progress.extra_data.get("stage_test_result")

    if not questions:
        return success_response(
            data={
                "questions": [],
                "node_id": node.id,
                "message": "暂无可用题目",
                "pass_score": 60,
                "total_score": 100,
                "result": stage_test_result,
            },
            msg="暂无可用题目",
        )

    stage_score_map = build_normalized_score_map(
        [(q.id, 1) for q in questions],
        target_total_score=100,
        equal_weight=True,
    )
    question_list = []
    for q in questions:
        item = {
            "id": q.id,
            "content": q.content,
            "question_type": q.question_type,
            "difficulty": q.difficulty,
            "score": stage_score_map.get(str(q.id), 0),
            "knowledge_points": [
                {"id": kp.id, "name": kp.name}
                for kp in q.knowledge_points.filter(id__in=kp_ids)
            ],
        }
        if q.question_type in ("single_choice", "multiple_choice", "true_false"):
            item["options"] = [
                {
                    "key": option.get("letter") or option.get("value"),
                    "value": option.get("content")
                    or option.get("label")
                    or option.get("value"),
                    "answer_value": option.get("value"),
                }
                for option in normalize_question_options(q.options, q.question_type)
            ]
        question_list.append(item)

    return success_response(
        data={
            "node_id": node.id,
            "node_title": node.title,
            "questions": question_list,
            "total_score": 100,
            "pass_score": 60,
            "result": stage_test_result,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_stage_test(request, node_id):
    """
    提交阶段测试答案（内嵌做题）
    POST /api/student/path-nodes/{node_id}/stage-test/submit

    请求体: {"answers": {"question_id": "answer", ...}}
    """
    from assessments.models import Question, AnswerHistory

    user = _get_authenticated_user(request)
    answers = request.data.get("answers", {})

    if not isinstance(answers, dict):
        return error_response(msg="答案格式错误，应为字典格式")

    try:
        node = PathNode.objects.select_related("path", "knowledge_point").get(
            id=node_id, path__user=user
        )
    except PathNode.DoesNotExist:
        return error_response(msg="节点不存在", code=404)

    if node.node_type != "test":
        return error_response(msg="该节点不是测试节点")

    question_ids = [int(qid) for qid in answers.keys()]
    question_map = {
        question.id: question
        for question in Question.objects.filter(
            id__in=question_ids, course=node.path.course
        )
    }
    questions = [question_map[qid] for qid in question_ids if qid in question_map]

    # 评分
    total_score = 100.0
    stage_score_map = build_normalized_score_map(
        [(q.id, 1) for q in questions],
        target_total_score=total_score,
        equal_weight=True,
    )
    grading = score_questions(answers, questions, score_map=stage_score_map)
    score = grading["score"]
    point_stats: dict[int, dict[str, object]] = grading["point_stats"]
    question_result_map = {
        str(item["question_id"]): item for item in grading["question_results"]
    }
    pass_threshold = 60.0
    passed = score >= pass_threshold

    correct_count = sum(1 for item in grading["question_results"] if item["is_correct"])
    total_count = len(questions)
    accuracy = round(correct_count / total_count * 100, 1) if total_count else 0

    # 记录答题历史
    question_details = []
    for q in questions:
        q_id = str(q.id)
        result = question_result_map.get(q_id, {})
        student_answer = answers.get(q_id)
        correct_value = result.get("correct_answer", extract_answer_value(q.answer))
        is_correct = result.get(
            "is_correct", check_answer(q.question_type, student_answer, q.answer)
        )
        decorated_options = decorate_question_options(
            q.options,
            q.question_type,
            student_answer=student_answer,
            correct_answer=correct_value,
        )
        question_points: list[KnowledgePoint] = list(q.knowledge_points.all())
        kp = question_points[0] if question_points else None

        AnswerHistory.objects.create(
            user=user,
            course=node.path.course,
            question=q,
            knowledge_point=kp,
            student_answer=serialize_answer_payload(q.question_type, student_answer),
            correct_answer=serialize_answer_payload(q.question_type, correct_value),
            is_correct=is_correct,
            score=result.get("earned_score", 0),
        )

        question_details.append(
            {
                "question_id": q.id,
                "content": q.content,
                "question_type": q.question_type,
                "student_answer": student_answer,
                "correct_answer": correct_value,
                "student_answer_display": build_answer_display(
                    student_answer, q.question_type, decorated_options
                ),
                "correct_answer_display": build_answer_display(
                    correct_value, q.question_type, decorated_options
                ),
                "is_correct": is_correct,
                "analysis": result.get("analysis") or q.analysis or "",
                "options": decorated_options,
                "knowledge_points": [
                    {"id": point.id, "name": point.name}
                    for point in question_points
                ],
                "score": result.get("earned_score", 0),
                "full_score": result.get("assigned_score", 0),
            }
        )

    # 构建错题详情与报告输入
    detailed_mistakes = []
    for item in question_details:
        if item["is_correct"]:
            continue
        question = question_map.get(item["question_id"])
        related_points: list[KnowledgePoint] = (
            list(question.knowledge_points.all()) if question else []
        )
        kp = related_points[0] if related_points else None
        detailed_mistakes.append(
            {
                "question_id": item["question_id"],
                "question_text": question.content if question else "",
                "knowledge_point_name": kp.name if kp else "",
                "student_answer": item.get("student_answer"),
                "correct_answer": item.get("correct_answer"),
                "student_answer_display": item.get("student_answer_display"),
                "correct_answer_display": item.get("correct_answer_display"),
                "analysis": item.get("analysis")
                or (question.analysis if question else ""),
                "options": item.get("options", []),
            }
        )

    # 更新节点进度和状态
    progress, _ = NodeProgress.objects.get_or_create(node=node, user=user)
    demo_stage_payload = get_defense_demo_stage_test_payload(progress)
    tracked_point_ids = sorted(point_stats.keys())
    mastery_before_snapshot = _snapshot_mastery_for_points(
        user, node.path.course_id, tracked_point_ids
    )

    # DEFENSE_DEMO_PRESET: 答辩测试节点走固定题目、固定反馈、固定掌握度变化，
    # 避免 LLM/KT 波动影响现场节奏，同时保留真实提交与前端刷新动画。
    if demo_stage_payload and is_defense_demo_student(user, node.path.course):
        with transaction.atomic():
            if passed:
                complete_defense_demo_stage_test(node, user, progress)
            else:
                node.status = "failed"
                node.save(update_fields=["status"])

            mastery_after_map = demo_stage_payload.get("mastery_after", {})
            if isinstance(mastery_after_map, dict):
                for point_id_text, mastery_value in mastery_after_map.items():
                    try:
                        point_id = int(point_id_text)
                        mastery_rate = round(float(mastery_value), 4)
                    except (TypeError, ValueError):
                        continue
                    KnowledgeMastery.objects.update_or_create(
                        user=user,
                        course=node.path.course,
                        knowledge_point_id=point_id,
                        defaults={"mastery_rate": mastery_rate},
                    )

            mastery_after_snapshot = _snapshot_mastery_for_points(
                user, node.path.course_id, tracked_point_ids
            )
            mastery_changes = _build_mastery_change_payload(
                mastery_before_snapshot, mastery_after_snapshot
            )
            progress.mastery_before = _average_mastery(mastery_before_snapshot)
            progress.mastery_after = _average_mastery(mastery_after_snapshot)
            feedback_report = demo_stage_payload.get("feedback_report")
            progress.extra_data = progress.extra_data or {}
            progress.extra_data["stage_test_result"] = {
                "score": score,
                "total_score": total_score,
                "passed": passed,
                "pass_threshold": pass_threshold,
                "correct": correct_count,
                "correct_count": correct_count,
                "total": total_count,
                "total_count": total_count,
                "accuracy": accuracy,
                "mistakes": detailed_mistakes,
                "question_details": question_details,
                "point_stats": point_stats,
                "mastery_changes": mastery_changes,
                "feedback_report": feedback_report if isinstance(feedback_report, dict) else {},
                "submitted_at": timezone.now().isoformat(),
                "node_status": node.status,
                "path_refreshed": passed,
            }
            progress.save(update_fields=["mastery_before", "mastery_after", "extra_data", "updated_at"])

        return success_response(
            data={
                "score": score,
                "total_score": total_score,
                "passed": passed,
                "pass_threshold": pass_threshold,
                "correct": correct_count,
                "correct_count": correct_count,
                "total": total_count,
                "total_count": total_count,
                "accuracy": accuracy,
                "mistakes": detailed_mistakes,
                "question_details": question_details,
                "point_stats": point_stats,
                "mastery_changes": mastery_changes,
                "feedback_report": feedback_report if isinstance(feedback_report, dict) else {},
                "node_status": node.status,
                "path_refreshed": passed,
            },
            msg="阶段测试提交成功",
        )

    with transaction.atomic():
        if passed:
            node.status = "completed"
            node.save()
            # 解锁下一个节点
            next_node = (
                PathNode.objects.filter(
                    path=node.path, order_index__gt=node.order_index
                )
                .order_by("order_index")
                .first()
            )
            if next_node and next_node.status == "locked":
                next_node.status = "active"
                next_node.save()
        else:
            node.status = "failed"
            node.save()

        # 使用知识追踪服务更新掌握度
        try:
            from ai_services.services.kt_service import kt_service

            # 汇总该课程历史作答，避免阶段测试只看当前节点。
            all_history = list(
                AnswerHistory.objects.filter(user=user, course=node.path.course)
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
            kp_ids = list(point_stats.keys())
            kt_result = kt_service.predict_mastery(
                user_id=user.id,
                course_id=node.path.course_id,
                answer_history=kt_history,
                knowledge_points=kp_ids,
            )
            kt_predictions = kt_result.get("predictions", {})
            for kp_id, mastery_val in kt_predictions.items():
                try:
                    mastery_obj, _ = KnowledgeMastery.objects.get_or_create(
                        user=user, course=node.path.course, knowledge_point_id=kp_id
                    )
                    mastery_obj.mastery_rate = max(0, min(1, round(mastery_val, 4)))
                    mastery_obj.save()
                except Exception as e:
                    logger.warning(
                        build_log_message(
                            "kt.stage_test.mastery_update_fail",
                            user_id=user.id,
                            node_id=node.id,
                            knowledge_point_id=kp_id,
                            error=e,
                        )
                    )
            logger.info(
                build_log_message(
                    "kt.stage_test.success",
                    user_id=user.id,
                    node_id=node.id,
                    answer_count=len(kt_history),
                    prediction_count=len(kt_predictions),
                )
            )
        except Exception as e:
            logger.error(
                build_log_message(
                    "kt.stage_test.fail", user_id=user.id, node_id=node.id, error=e
                )
            )
            # 降级: 使用原始简单算法
            for kp_id, stats in point_stats.items():
                try:
                    if stats["total"] <= 0:
                        continue
                    mastery_delta = (
                        0.1 if stats["correct"] / stats["total"] >= 0.8 else -0.05
                    )
                    mastery, _ = KnowledgeMastery.objects.get_or_create(
                        user=user, course=node.path.course, knowledge_point_id=kp_id
                    )
                    mastery.mastery_rate = max(
                        0, min(1, float(mastery.mastery_rate) + mastery_delta)
                    )
                    mastery.save()
                except Exception as e2:
                    logger.warning(
                        build_log_message(
                            "kt.stage_test.fallback_mastery_update_fail",
                            user_id=user.id,
                            node_id=node.id,
                            knowledge_point_id=kp_id,
                            error=e2,
                        )
                    )

        mastery_after_snapshot = _snapshot_mastery_for_points(
            user, node.path.course_id, tracked_point_ids
        )
        progress.mastery_before = _average_mastery(mastery_before_snapshot)
        progress.mastery_after = _average_mastery(mastery_after_snapshot)
        mastery_changes = _build_mastery_change_payload(
            mastery_before_snapshot, mastery_after_snapshot
        )

        # 调用LLM生成阶段测试反馈报告
        feedback_report = {
            "summary": "",
            "analysis": "",
            "knowledge_gaps": [],
            "recommendations": [],
            "next_tasks": [],
            "conclusion": "",
        }
        try:
            from ai_services.services import llm_service as _llm

            llm_feedback = _llm.generate_feedback_report(
                exam_info={
                    "title": node.title,
                    "type": "阶段测试",
                },
                score=score,
                total_score=total_score,
                mistakes=detailed_mistakes,
            )
            feedback_report = {
                "summary": llm_feedback.get("summary", "")
                or (
                    llm_feedback.get("analysis", "")
                    if isinstance(llm_feedback.get("analysis"), str)
                    else ""
                ),
                "analysis": llm_feedback.get("analysis", "")
                if isinstance(llm_feedback.get("analysis"), str)
                else "",
                "knowledge_gaps": llm_feedback.get("knowledge_gaps", [])
                if isinstance(llm_feedback.get("knowledge_gaps"), list)
                else [],
                "recommendations": llm_feedback.get("recommendations", [])
                if isinstance(llm_feedback.get("recommendations"), list)
                else [],
                "next_tasks": llm_feedback.get("next_tasks", [])
                if isinstance(llm_feedback.get("next_tasks"), list)
                else [],
                "conclusion": llm_feedback.get("conclusion", "")
                or llm_feedback.get("encouragement", ""),
            }
            if feedback_report["analysis"] == feedback_report["summary"]:
                feedback_report["analysis"] = ""
        except Exception as e:
            logger.error(
                build_log_message(
                    "llm.stage_test.fail", user_id=user.id, node_id=node.id, error=e
                )
            )
            feedback_report = {
                "summary": "系统已根据你的答题情况生成阶段测试结果，建议结合错题和薄弱知识点继续巩固。",
                "analysis": "系统已根据你的答题情况生成阶段测试结果，建议结合错题和薄弱知识点继续巩固。",
                "knowledge_gaps": [
                    stats["name"] for _, stats in list(point_stats.items())[:3]
                ],
                "recommendations": [
                    "复习错题涉及知识点",
                    "结合学习资源再次梳理重点概念",
                    "完成后重新尝试阶段测试",
                ],
                "next_tasks": ["回顾当前阶段对应的学习节点", "重做错题并记录原因"],
                "conclusion": "继续保持，修正薄弱点后你的成绩会更稳！",
            }

        progress.extra_data = progress.extra_data or {}
        progress.extra_data["stage_test_result"] = {
            "score": score,
            "total_score": total_score,
            "passed": passed,
            "pass_threshold": pass_threshold,
            "correct": correct_count,
            "correct_count": correct_count,
            "total": total_count,
            "total_count": total_count,
            "accuracy": accuracy,
            "mistakes": detailed_mistakes,
            "question_details": question_details,
            "point_stats": point_stats,
            "mastery_changes": mastery_changes,
            "feedback_report": feedback_report,
            "submitted_at": timezone.now().isoformat(),
            "node_status": node.status,
        }
        progress.save()

    if passed:
        from ai_services.services.path_service import PathService

        PathService().generate_path(user, node.path.course)

    return success_response(
        data={
            "score": score,
            "total_score": total_score,
            "passed": passed,
            "pass_threshold": pass_threshold,
            "correct": correct_count,
            "correct_count": correct_count,
            "total": total_count,
            "total_count": total_count,
            "accuracy": accuracy,
            "mistakes": detailed_mistakes,
            "question_details": question_details,
            "point_stats": point_stats,
            "mastery_changes": mastery_changes,
            "feedback_report": feedback_report,
            "node_status": node.status,
            "path_refreshed": passed,
        },
        msg="阶段测试提交成功",
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    """
    学生仪表盘聚合数据
    GET /api/student/dashboard?course_id=xxx

    合并学习进度、路径预览、画像摘要，减少前端并发请求。
    """
    user = _get_authenticated_user(request)
    course_id = request.query_params.get("course_id")
    if not course_id:
        return error_response(msg="请提供 course_id 参数")

    try:
        course_id = int(course_id)
    except (TypeError, ValueError):
        return error_response(msg="course_id 必须为整数")

    data: dict[str, object] = {
        "progress": 0,
        "study_time": 0,
        "completed_nodes": 0,
        "total_nodes": 0,
        "mastered_points": 0,
        "nodes_preview": [],
        "recent_mastery": [],
        "pending_exams": [],
    }

    # 学习路径进度
    path = LearningPath.objects.filter(user=user, course_id=course_id).first()
    if path:
        nodes = PathNode.objects.filter(path=path).select_related("knowledge_point")
        total = nodes.count()
        completed = nodes.filter(status="completed").count()
        data["total_nodes"] = total
        data["completed_nodes"] = completed
        data["progress"] = completed / total if total > 0 else 0

        # 学习时长（用完成节点数估算，每节点约30分钟）
        data["study_time"] = completed * 30

        # 节点预览（前5个，未完成优先）
        data["nodes_preview"] = [
            {
                "node_id": n.id,
                "knowledge_point_name": n.knowledge_point.name
                if n.knowledge_point
                else "",
                "status": n.status,
                "order": n.order_index,
            }
            for n in sorted(nodes, key=_path_node_sort_key)[:5]
        ]

    # 知识掌握度
    mastery_qs = KnowledgeMastery.objects.filter(
        user=user, course_id=course_id
    ).select_related("knowledge_point")
    mastered = mastery_qs.filter(mastery_rate__gte=0.8).count()
    data["mastered_points"] = mastered

    # 最近更新的5个知识点掌握度
    data["recent_mastery"] = [
        {
            "name": m.knowledge_point.name if m.knowledge_point else "未知",
            "mastery_rate": float(m.mastery_rate),
            "updated_at": m.updated_at.isoformat()
            if hasattr(m, "updated_at") and m.updated_at
            else "",
        }
        for m in mastery_qs.order_by("-updated_at")[:5]
    ]

    # 待完成考试
    try:
        from exams.models import Exam, ExamSubmission

        published_exams = Exam.objects.filter(
            course_id=course_id, status="published", exam_type="exam"
        )
        submitted_ids = ExamSubmission.objects.filter(
            user=user, exam__course_id=course_id
        ).values_list("exam_id", flat=True)
        pending = published_exams.exclude(id__in=submitted_ids)[:3]
        data["pending_exams"] = [
            {"id": e.id, "title": e.title, "duration": e.duration} for e in pending
        ]
    except Exception as e:
        logger.warning("Dashboard待考试数据查询失败: %s", e)

    return success_response(data=data)
