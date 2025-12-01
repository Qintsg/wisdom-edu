"""学习路径服务模块。

职责：
1. 统一更新课程全量知识点掌握度（KT + 默认兜底）。
2. 按“低掌握度 + 关联知识点”生成小批次学习路径。
3. 保留已完成/进行中节点，仅重建后续 locked 节点。
"""

# pyright: reportAttributeAccessIssue=false, reportGeneralTypeIssues=false, reportArgumentType=false

import logging
from typing import Dict, List, Optional, Set, TYPE_CHECKING
from django.db import transaction

logger = logging.getLogger(__name__)

REMEDIAL_REINSERTION_THRESHOLD = 0.6

if TYPE_CHECKING:
    from courses.models import Course
    from knowledge.models import KnowledgePoint
    from users.models import User


class PathService:
    """
    学习路径服务类

    提供学习路径的生成、调整和进度管理功能
    """

    def _load_course_point_ids(self, course_id: int) -> List[int]:
        """返回课程内所有已发布知识点 ID。"""
        from knowledge.models import KnowledgePoint

        return list(
            KnowledgePoint.objects.filter(course_id=course_id, is_published=True)
            .order_by("order", "id")
            .values_list("id", flat=True)
        )

    def _build_linked_pending_batch(
        self,
        pending_points: List["KnowledgePoint"],
        mastery_dict: Dict[int, float],
        prereq_map: Dict[int, List[int]],
        dependents_map: Dict[int, List[int]],
        batch_size: int,
    ) -> List["KnowledgePoint"]:
        """从待学习知识点中，选取“最低掌握度且尽量互相关联”的小批次。"""
        if not pending_points or batch_size <= 0:
            return []

        pending_by_id = {point.id: point for point in pending_points}
        pending_ids = set(pending_by_id.keys())

        # 先按掌握度（低→高）排序，确定种子点。
        ordered = sorted(
            pending_points,
            key=lambda point: (
                float(mastery_dict.get(point.id, 0)),
                point.order,
                point.id,
            ),
        )
        seed_point = ordered[0]

        selected_ids: List[int] = [seed_point.id]
        visited_ids: Set[int] = {seed_point.id}
        queue_ids: List[int] = [seed_point.id]

        # 在前置/后继图上做宽搜，优先把关联点拉进同一轮。
        while queue_ids and len(selected_ids) < batch_size:
            current_id = queue_ids.pop(0)
            neighbor_ids = prereq_map.get(current_id, []) + dependents_map.get(
                current_id, []
            )
            for neighbor_id in neighbor_ids:
                if neighbor_id in visited_ids or neighbor_id not in pending_ids:
                    continue
                visited_ids.add(neighbor_id)
                selected_ids.append(neighbor_id)
                queue_ids.append(neighbor_id)
                if len(selected_ids) >= batch_size:
                    break

        # 若关联点不足，回退为低掌握度补齐。
        if len(selected_ids) < batch_size:
            for point in ordered:
                if point.id in visited_ids:
                    continue
                selected_ids.append(point.id)
                visited_ids.add(point.id)
                if len(selected_ids) >= batch_size:
                    break

        return [
            pending_by_id[point_id]
            for point_id in selected_ids
            if point_id in pending_by_id
        ]

    def _sync_course_mastery(
        self,
        user: "User",
        course: "Course",
        course_point_ids: List[int],
    ) -> Dict[int, float]:
        """同步课程全量掌握度，保证路径规划覆盖全部知识点。"""
        from assessments.models import AnswerHistory
        from ai_services.services import kt_service
        from knowledge.models import KnowledgeMastery
        from learning.path_rules import apply_prerequisite_caps

        course_id = course.id
        mastery_dict: Dict[int, float] = {}

        answer_records = list(
            AnswerHistory.objects.filter(user=user, course_id=course_id)
            .order_by("answered_at")
            .values("question_id", "knowledge_point_id", "is_correct")
        )
        kt_history = [
            {
                "question_id": record["question_id"],
                "knowledge_point_id": record["knowledge_point_id"],
                "correct": 1 if record["is_correct"] else 0,
            }
            for record in answer_records
            if record["knowledge_point_id"]
        ]

        if kt_history:
            try:
                kt_result = kt_service.predict_mastery(
                    user_id=user.id,
                    course_id=course_id,
                    answer_history=kt_history,
                    knowledge_points=course_point_ids,
                )
                raw_predictions = kt_result.get("predictions") or {}
                mastery_dict = {
                    int(point_id): float(value)
                    for point_id, value in raw_predictions.items()
                }
                logger.info(
                    "KT服务调用成功(路径生成): 用户=%s, 答题历史=%d条, 预测结果=%d条",
                    user.id,
                    len(kt_history),
                    len(mastery_dict),
                )
            except Exception as kt_error:
                logger.error(
                    "KT预测失败(路径生成): 用户=%s, 错误=%s", user.id, kt_error
                )

        # 覆盖全部知识点：有记录沿用，无记录默认0.25。
        existing_mastery = {
            row.knowledge_point_id: float(row.mastery_rate)
            for row in KnowledgeMastery.objects.filter(user=user, course_id=course_id)
        }
        for point_id in course_point_ids:
            if point_id not in mastery_dict:
                mastery_dict[point_id] = existing_mastery.get(point_id, 0.25)

        mastery_dict = apply_prerequisite_caps(
            mastery_dict, course_id=course_id, buffer=0.05
        )

        for point_id, mastery_rate in mastery_dict.items():
            # 更新或创建记录
            KnowledgeMastery.objects.update_or_create(
                user=user,
                course_id=course_id,
                knowledge_point_id=point_id,
                defaults={"mastery_rate": float(mastery_rate)},
            )
        return mastery_dict

    def generate_path(
        self,
        user: "User",
        course: "Course",
        mastery_data: Optional[List[Dict[str, float]]] = None,
    ):
        """
        为用户生成学习路径（与手动刷新对齐的完整逻辑）

        流程：
        1. 调用KT服务更新掌握度
        2. 保留已完成/进行中/跳过/失败的节点
        3. 按掌握度排序剩余知识点
        4. 根据配置节点上限和测试间隔，创建学习+测评节点
        5. 关联学习资源
        6. 激活第一个可学习节点

        Args:
            user: User实例
            course: Course实例
            mastery_data: 知识点掌握度数据（可选，未提供则自动获取）

        Returns:
            LearningPath实例
        """
        from learning.models import LearningPath, PathNode
        from knowledge.models import KnowledgeMastery
        from common.config import AppConfig
        from learning.path_rules import (
            partition_points_for_path,
            build_prerequisite_maps,
        )

        course_id = course.id

        # --- 1. 统一同步全量掌握度（覆盖课程所有已发布知识点） ---
        course_point_ids = self._load_course_point_ids(course_id)
        mastery_dict = (
            {
                int(item["knowledge_point_id"]): float(item["mastery_rate"])
                for item in mastery_data
            }
            if mastery_data
            else self._sync_course_mastery(
                user=user, course=course, course_point_ids=course_point_ids
            )
        )

        # --- 2. 停用头部说明文案，避免为页面统计卡片额外触发 LLM 调用 ---
        ai_reason = ""

        with transaction.atomic():
            # --- 3. 同步学习路径主记录 ---
            learning_path, created = LearningPath.objects.update_or_create(
                user=user,
                course=course,
                defaults={
                    "ai_reason": ai_reason,
                },
            )
            if not created:
                learning_path.is_dynamic = True
                learning_path.save(update_fields=["is_dynamic"])

            # --- 4. 保留已有进度节点，删除locked ---
            preserved_statuses = ("completed", "active", "skipped", "failed")
            preserved_nodes = list(
                learning_path.nodes.filter(status__in=preserved_statuses)
            )
            remedial_point_ids = {
                node.knowledge_point_id
                for node in preserved_nodes
                if node.status == "completed"
                and node.knowledge_point_id
                and float(mastery_dict.get(node.knowledge_point_id, 0))
                < REMEDIAL_REINSERTION_THRESHOLD
            }
            preserved_kp_ids = {
                n.knowledge_point_id for n in preserved_nodes if n.knowledge_point_id
            }
            preserved_kp_ids -= remedial_point_ids

            learning_path.nodes.filter(status="locked").delete()

            max_order = max((n.order_index for n in preserved_nodes), default=-1)
            next_order = max_order + 1

            # --- 5. 规划剩余知识点分层 ---
            auto_completed_points, pending_points, _ = partition_points_for_path(
                course_id,
                mastery_dict,
                excluded_point_ids=preserved_kp_ids,
            )
            prereq_map, dependents_map = build_prerequisite_maps(course_id)

            # --- 6. 按config上限和测试间隔创建学习节点 + 测评节点 ---
            max_nodes = AppConfig.max_path_nodes()
            test_interval = AppConfig.path_test_interval()
            remaining_quota = max(0, max_nodes - len(preserved_nodes))

            nodes_to_create = []
            node_resource_map = []
            study_batch = []
            order_idx = next_order

            completed_quota = min(len(auto_completed_points), remaining_quota)
            for point in auto_completed_points[:completed_quota]:
                nodes_to_create.append(
                    PathNode(
                        path=learning_path,
                        knowledge_point=point,
                        title=f"{point.name}巩固",
                        goal=f"你已达到 {point.name} 的默认完成标准",
                        criterion="掌握度已达默认完成阈值",
                        suggestion="系统已将该知识点标记为默认完成，可按需回顾相关资源。",
                        status="completed",
                        order_index=order_idx,
                        node_type="study",
                        estimated_minutes=15,
                    )
                )
                node_resource_map.append(point)
                order_idx += 1

            pending_quota = max(0, remaining_quota - completed_quota)
            study_batch_size = max(
                1, min(AppConfig.path_test_interval(), pending_quota)
            )
            linked_points = self._build_linked_pending_batch(
                pending_points=pending_points,
                mastery_dict=mastery_dict,
                prereq_map=prereq_map,
                dependents_map=dependents_map,
                batch_size=study_batch_size,
            )

            for point in linked_points:
                mastery = mastery_dict.get(point.id, 0)
                is_remedial_reinsertion = point.id in remedial_point_ids
                nodes_to_create.append(
                    PathNode(
                        path=learning_path,
                        knowledge_point=point,
                        title=(
                            f"{point.name}补强"
                            if is_remedial_reinsertion
                            else f"{point.name}" + ("提升" if mastery > 0.5 else "基础")
                        ),
                        goal=f"掌握{point.name}的核心概念及应用",
                        criterion="完成所有学习资源和测验，正确率≥80%",
                        suggestion=(
                            f"最近一次测试后，{point.name} 掌握度降至 {round(float(mastery) * 100)}%，请优先补强。"
                            if is_remedial_reinsertion
                            else f"{'巩固' if mastery > 0.5 else '重点学习'}{point.name}相关内容。"
                        ),
                        status="locked",
                        order_index=order_idx,
                        node_type="study",
                        estimated_minutes=max(
                            15, min(60, int(30 + (1 - mastery) * 30))
                        ),
                        is_inserted=is_remedial_reinsertion,
                    )
                )
                node_resource_map.append(point)
                study_batch.append(point)
                order_idx += 1

            if study_batch:
                kp_name_list = [point.name for point in study_batch]
                if len(kp_name_list) > 3:
                    test_title = f"阶段测试：{'、'.join(kp_name_list[:3])}等{len(kp_name_list)}个知识点"
                else:
                    test_title = f"阶段测试：{'、'.join(kp_name_list)}"
                nodes_to_create.append(
                    PathNode(
                        path=learning_path,
                        knowledge_point=study_batch[-1],
                        title=test_title,
                        goal=f"检验{'、'.join(kp_name_list)}的掌握程度",
                        criterion="正确率≥80%视为通过",
                        suggestion="综合运用前几个知识点完成测试题。",
                        status="locked",
                        order_index=order_idx,
                        node_type="test",
                        estimated_minutes=15,
                    )
                )
                node_resource_map.append(None)
                order_idx += 1

            # --- 7. 批量创建并关联资源 ---
            if nodes_to_create:
                created_nodes = PathNode.objects.bulk_create(nodes_to_create)
                for node, point in zip(created_nodes, node_resource_map):
                    if point is not None:
                        resources = point.resources.filter(is_visible=True)[:5]
                        if resources:
                            node.resources.add(*list(resources))

            # --- 8. 确保有一个active节点 ---
            if not learning_path.nodes.filter(status="active").exists():
                first_locked = (
                    learning_path.nodes.filter(status="locked")
                    .order_by("order_index")
                    .first()
                )
                if first_locked:
                    first_locked.status = "active"
                    first_locked.save()

            learning_path.save()

        total_nodes = len(preserved_nodes) + len(nodes_to_create)
        logger.info(
            "为用户 %s 生成学习路径，共 %d 个节点（保留%d个，新建%d个，小批次学习节点=%d）",
            user.username,
            total_nodes,
            len(preserved_nodes),
            len(nodes_to_create),
            len([point for point in locals().get("linked_points", [])]),
        )

        return learning_path

    def unlock_next_node(self, current_node):
        """
        解锁下一个节点

        Args:
            current_node: 当前完成的PathNode实例
        """
        from learning.models import PathNode

        next_node = (
            PathNode.objects.filter(
                path=current_node.path,
                order_index__gt=current_node.order_index,
                status="locked",
            )
            .order_by("order_index")
            .first()
        )

        if next_node:
            next_node.status = "active"
            next_node.save()
            logger.info(f"解锁节点: {next_node.title}")

    def insert_remedial_node(self, path, knowledge_point, after_node):
        """
        在路径中插入补救节点

        当学生某个知识点掌握度不足时，动态插入补救学习节点

        Args:
            path: LearningPath实例
            knowledge_point: 需要补救的KnowledgePoint实例
            after_node: 插入位置（在此节点之后）
        """
        from learning.models import PathNode
        from django.db.models import F

        with transaction.atomic():
            # 将后续节点顺序后移
            PathNode.objects.filter(
                path=path, order_index__gt=after_node.order_index
            ).update(order_index=F("order_index") + 1)

            # 插入补救节点
            remedial_node = PathNode.objects.create(
                path=path,
                knowledge_point=knowledge_point,
                title=f"{knowledge_point.name}补强",
                goal=f"强化{knowledge_point.name}的理解和应用",
                suggestion="请仔细复习相关内容，完成配套练习",
                status="active",
                order_index=after_node.order_index + 1,
                is_inserted=True,
            )

            # 标记路径已动态调整
            path.is_dynamic = True
            path.save()

        logger.info(f"插入补救节点: {remedial_node.title}")

        return remedial_node

    def get_path_progress(self, path) -> Dict[str, object]:
        """
        获取学习路径的进度信息

        Args:
            path: LearningPath实例

        Returns:
            进度信息
        """
        nodes = path.nodes.all()
        total = nodes.count()
        completed = nodes.filter(status="completed").count()
        active = nodes.filter(status="active").first()

        return {
            "total_nodes": total,
            "completed_nodes": completed,
            "progress_percent": round(completed / total * 100, 1) if total > 0 else 0,
            "current_node": {
                "id": active.id,
                "title": active.title,
                "goal": active.goal,
            }
            if active
            else None,
            "is_completed": completed == total and total > 0,
        }
