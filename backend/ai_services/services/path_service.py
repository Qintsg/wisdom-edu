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

from ai_services.services.path_generation_support import (
    REMEDIAL_REINSERTION_THRESHOLD,
    attach_resources_to_created_nodes,
    build_generation_plan,
    load_course_point_ids,
    sync_course_mastery,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from courses.models import Course
    from knowledge.models import KnowledgePoint
    from users.models import User


# 维护意图：学习路径服务类 提供学习路径的生成、调整和进度管理功能
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class PathService:
    """
    学习路径服务类

    提供学习路径的生成、调整和进度管理功能
    """
    # 维护意图：为用户生成学习路径（与手动刷新对齐的完整逻辑） 流程： 1. 调用KT服务更新掌握度 2. 保留已完成/进行中/跳过/失败的节点 3. 按掌握度排序剩余知识点 4. 根据配置节点上限和测试间隔。
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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
        course_point_ids = load_course_point_ids(course_id)
        mastery_dict = (
            {
                int(item["knowledge_point_id"]): float(item["mastery_rate"])
                for item in mastery_data
            }
            if mastery_data
            else sync_course_mastery(
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

            # --- 5. 规划剩余知识点分层 ---
            auto_completed_points, pending_points, _ = partition_points_for_path(
                course_id,
                mastery_dict,
                excluded_point_ids=preserved_kp_ids,
            )
            prereq_map, dependents_map = build_prerequisite_maps(course_id)
            generation_plan = build_generation_plan(
                learning_path=learning_path,
                preserved_nodes=preserved_nodes,
                auto_completed_points=auto_completed_points,
                pending_points=pending_points,
                mastery_dict=mastery_dict,
                prereq_map=prereq_map,
                dependents_map=dependents_map,
                remedial_point_ids=remedial_point_ids,
            )
            nodes_to_create = generation_plan.nodes_to_create
            node_resource_map = generation_plan.node_resource_points
            linked_points = generation_plan.linked_points

            # --- 7. 批量创建并关联资源 ---
            if nodes_to_create:
                created_nodes = PathNode.objects.bulk_create(nodes_to_create)
                attach_resources_to_created_nodes(created_nodes, node_resource_map)

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

    # 维护意图：解锁下一个节点
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    # 维护意图：在路径中插入补救节点 当学生某个知识点掌握度不足时，动态插入补救学习节点
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    # 维护意图：获取学习路径的进度信息
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
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
