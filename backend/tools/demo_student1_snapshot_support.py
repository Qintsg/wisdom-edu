#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
student1 大数据快照预置写库辅助函数。
@Project : wisdom-edu
@File : demo_student1_snapshot_support.py
@Author : Qintsg
@Date : 2026-05-13 13:38
'''

from __future__ import annotations

from decimal import Decimal

from django.db.models import Max

from courses.models import Course
from exams.models import FeedbackReport
from knowledge.models import KnowledgeMastery, KnowledgePoint, Resource
from learning.models import LearningPath, NodeProgress, PathNode
from tools.demo_student1_snapshot_types import DesktopSnapshot, PathNodeSnapshot
from users.models import User


def default_ability_scores() -> dict[str, int]:
    """返回桌面画像快照中的默认能力分。"""
    return {"处理速度": 60, "工作记忆": 60, "知觉推理": 60, "言语理解": 60}


def build_snapshot_mastery_rates(course: Course, snapshot: DesktopSnapshot) -> dict[int, float]:
    """
    按桌面测评报告中的掌握度值生成写库映射。
    :param course: 目标课程。
    :param snapshot: 内置预置快照。
    :return: 知识点 ID 到掌握度的映射。
    """
    if not snapshot.report_mastery:
        return {}

    points = ensure_snapshot_mastery_points(course=course, mastery_names=list(snapshot.report_mastery))
    point_by_name = {point.name: point for point in points}
    rates: dict[int, float] = {}
    for point_name, rate in snapshot.report_mastery.items():
        point = point_by_name.get(point_name)
        if point is not None:
            rates[int(point.id)] = round(float(rate), 3)
    return rates


def ensure_snapshot_mastery_points(
    *,
    course: Course,
    mastery_names: list[str],
) -> list[KnowledgePoint]:
    """
    确保桌面报告中的知识点名称在课程中都有对应记录。
    :param course: 目标课程。
    :param mastery_names: 桌面报告中的知识点名称序列。
    :return: 当前课程知识点列表。
    """
    existing_by_name = {
        point.name: point
        for point in KnowledgePoint.objects.filter(course=course).order_by("order", "id")
    }
    max_order = (
        KnowledgePoint.objects.filter(course=course).aggregate(max_order=Max("order"))["max_order"]
        or 0
    )
    for point_name in mastery_names:
        point = existing_by_name.get(point_name)
        if point is not None:
            if point.description == "从 student1 桌面测评报告解析补齐的演示知识点。":
                point.description = ""
                point.save(update_fields=["description", "updated_at"])
            continue
        max_order += 1
        existing_by_name[point_name] = KnowledgePoint.objects.create(
            course=course,
            name=point_name,
            description="",
            chapter=infer_snapshot_point_chapter(point_name),
            level=infer_snapshot_point_level(point_name),
            point_type="knowledge",
            is_published=True,
            order=max_order,
        )
    return list(KnowledgePoint.objects.filter(course=course).order_by("order", "id"))


def infer_snapshot_point_chapter(point_name: str) -> str:
    """
    为桌面报告补充知识点推断章节路径。
    :param point_name: 知识点名称。
    :return: 章节路径。
    """
    if "Hadoop" in point_name:
        return "大数据存储与管理 > Hadoop"
    if "Spark" in point_name:
        return "大数据存储与管理 > Spark"
    if "大数据" in point_name:
        return "大数据技术基础"
    return "大数据技术与应用综合实践"


def infer_snapshot_point_level(point_name: str) -> int:
    """
    为桌面报告补充知识点推断层级。
    :param point_name: 知识点名称。
    :return: 知识点层级。
    """
    if "组成" in point_name or "模型" in point_name or "特征" in point_name:
        return 3
    return 2


def create_path_node(
    *,
    path: LearningPath,
    course: Course,
    snapshot_node: PathNodeSnapshot,
    snapshot: DesktopSnapshot,
) -> PathNode:
    """创建单个学习路径节点。"""
    node = PathNode.objects.create(
        path=path,
        node_type=snapshot_node.node_type,
        knowledge_point=match_point_for_snapshot_node(course, snapshot_node),
        title=snapshot_node.title,
        goal=snapshot_node.goal,
        criterion=snapshot_node.criterion,
        suggestion=snapshot_node.suggestion,
        status=snapshot_node.status,
        order_index=snapshot_node.order,
        estimated_minutes=snapshot_node.estimated_minutes,
    )
    node._snapshot_node = snapshot_node
    return node


def attach_node_resources(*, user: User, course: Course, nodes: list[PathNode]) -> None:
    """为路径节点绑定课程资源并补齐完成进度。"""
    resources = list(Resource.objects.filter(course=course).prefetch_related("knowledge_points").order_by("sort_order", "id"))
    for node in nodes:
        related = choose_node_resources(node, resources)
        if related:
            node.resources.set(related[:3])
        if node.status == "completed":
            NodeProgress.objects.update_or_create(
                node=node,
                user=user,
                defaults={
                    "completed_resources": [str(resource.id) for resource in related[:3]],
                    "completed_exams": [],
                    "mastery_before": progress_mastery(node, "mastery_before"),
                    "mastery_after": progress_mastery(node, "mastery_after"),
                    "extra_data": {"source": "desktop_student1_demo_snapshot"},
                },
            )


def choose_node_resources(node: PathNode, resources: list[Resource]) -> list[Resource]:
    """按知识点或标题关键词选择节点资源。"""
    if node.knowledge_point_id:
        matched = [resource for resource in resources if node.knowledge_point_id in {point.id for point in resource.knowledge_points.all()}]
        if matched:
            return matched
    title = node.title.replace("巩固", "").replace("基础", "")
    return [resource for resource in resources if title[:4] and title[:4] in resource.title]


def match_point_for_title(course: Course, title: str) -> KnowledgePoint | None:
    """用路径标题匹配课程知识点。"""
    keywords = [item for item in title.replace("阶段测试：", "").replace("、", ",").split(",") if item]
    keywords.extend([title.replace("巩固", "").replace("基础", ""), title])
    points = list(KnowledgePoint.objects.filter(course=course).order_by("order", "id"))
    for keyword in keywords:
        for point in points:
            if keyword and (keyword in point.name or point.name in keyword):
                return point
    return None


def match_point_for_snapshot_node(course: Course, node: PathNodeSnapshot) -> KnowledgePoint | None:
    """
    按显式快照知识点优先匹配路径节点。
    :param course: 目标课程。
    :param node: 路径节点快照。
    :return: 匹配到的知识点。
    """
    if node.knowledge_point_name:
        point = KnowledgePoint.objects.filter(course=course, name=node.knowledge_point_name).first()
        if point is not None:
            return point
    return match_point_for_title(course, node.title)


def progress_mastery(node: PathNode, field_name: str) -> Decimal | None:
    """
    读取节点快照中的掌握度进度。
    :param node: 已创建路径节点。
    :param field_name: `mastery_before` 或 `mastery_after`。
    :return: 可写入 NodeProgress 的 Decimal。
    """
    snapshot = getattr(node, "_snapshot_node", None)
    value = getattr(snapshot, field_name, None)
    if value is None:
        return None
    return Decimal(str(value))


def mastery_payload_for_course(*, user: User, course: Course) -> list[dict[str, object]]:
    """构建测评结果中的掌握度列表。"""
    rows = KnowledgeMastery.objects.filter(user=user, course=course).select_related("knowledge_point")
    return [
        {"point_id": row.knowledge_point_id, "point_name": row.knowledge_point.name, "mastery_rate": float(row.mastery_rate)}
        for row in rows.order_by("knowledge_point__order", "knowledge_point_id")
    ]


def write_feedback_report(*, user: User, result: object, snapshot: DesktopSnapshot) -> None:
    """写入初始评测反馈报告。"""
    FeedbackReport.objects.filter(
        user=user,
        source="assessment",
        assessment_result=result,
    ).delete()
    FeedbackReport.objects.create(
        user=user,
        source="assessment",
        assessment_result=result,
        status="completed",
        overview={
            "score": snapshot.score,
            "correct_count": snapshot.correct_count,
            "total_count": snapshot.total_count,
            "accuracy": round(snapshot.correct_count / max(snapshot.total_count, 1) * 100, 1),
            "summary": snapshot.feedback_report.summary,
            "knowledge_gaps": snapshot.feedback_report.knowledge_gaps,
        },
        analysis=snapshot.feedback_report.summary,
        recommendations=snapshot.feedback_report.recommendations,
        next_tasks=snapshot.feedback_report.next_tasks,
        conclusion=snapshot.feedback_report.conclusion,
    )


def write_snapshot_metadata(*, course: Course, snapshot: DesktopSnapshot) -> None:
    """将内置预置摘要写入课程配置。"""
    config = dict(course.config or {})
    config["student1_big_data_preset"] = {
        "version": snapshot.preset_version,
        "score": snapshot.score,
        "correct_count": snapshot.correct_count,
        "total_count": snapshot.total_count,
        "question_count": len(snapshot.question_details),
        "mastery_count": len(snapshot.report_mastery),
        "path_node_count": len(snapshot.path_nodes),
        "completed_nodes": len([node for node in snapshot.path_nodes if node.status == "completed"]),
        "path_titles": snapshot.path_titles,
        "selected_path_title": snapshot.selected_path_title,
    }
    config.pop("student1_desktop_demo_snapshot", None)
    course.config = config
    course.save(update_fields=["config", "updated_at"])
