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

from assessments.models import AnswerHistory, Question
from courses.models import Course
from exams.models import FeedbackReport
from knowledge.models import KnowledgeMastery, KnowledgePoint, Resource
from learning.models import LearningPath, NodeProgress, PathNode
from tools.demo_student1_snapshot_types import (
    DESKTOP_HTML_NAMES,
    DesktopSnapshot,
    QuestionSnapshot,
)
from users.models import User


def default_ability_scores() -> dict[str, int]:
    """返回桌面画像快照中的默认能力分。"""
    return {"处理速度": 60, "工作记忆": 60, "知觉推理": 60, "言语理解": 60}


def default_path_titles() -> list[str]:
    """返回桌面路径快照中的默认节点序列。"""
    return [
        "大数据概念基础复盘",
        "Spark定义与特征巩固",
        "大数据智能分析挖掘巩固",
        "基于潜在因子的推荐方法巩固",
        "大数据存储与管理巩固",
        "Spark SQL原理与特征基础",
        "大数据系统实践基础",
        "综合实践基础",
        "阶段测试：Spark SQL原理与特征、大数据系统实践、综合实践",
    ]


def build_mastery_rates(course: Course) -> dict[int, float]:
    """为课程知识点生成演示友好的 6/28/40 掌握度分布。"""
    points = list(KnowledgePoint.objects.filter(course=course).order_by("order", "id"))
    target_values = target_mastery_values(len(points))
    rates: dict[int, float] = {}
    explicit = [
        (("大数据存储与管理",), 0.98),
        (("基于潜在因子的推荐方法",), 0.97),
        (("Spark定义与特征",), 0.87),
        (("综合实践",), 0.24),
        (("Spark SQL原理与特征", "Spark SQL原理"), 0.24),
        (("自然语言处理实践", "PySpark自然语言处理实践"), 0.31),
    ]
    for candidates, value in explicit:
        point = first_unassigned_point(points, rates, candidates)
        if point:
            rates[int(point.id)] = value
    for point, value in zip([point for point in points if int(point.id) not in rates], target_values):
        rates[int(point.id)] = value
    return rates


def build_snapshot_mastery_rates(course: Course, snapshot: DesktopSnapshot) -> dict[int, float]:
    """
    按桌面测评报告中的掌握度值生成写库映射。
    :param course: 目标课程。
    :param snapshot: 桌面 HTML 解析出的快照。
    :return: 知识点 ID 到掌握度的映射。
    """
    if not snapshot.report_mastery:
        return build_mastery_rates(course)

    points = ensure_snapshot_mastery_points(course=course, mastery_names=list(snapshot.report_mastery))
    point_by_name = {point.name: point for point in points}
    rates: dict[int, float] = {}
    for point_name, rate in snapshot.report_mastery.items():
        point = point_by_name.get(point_name)
        if point is not None:
            rates[int(point.id)] = round(float(rate), 3)

    remaining_points = [point for point in points if int(point.id) not in rates]
    remaining_values = target_mastery_values(len(remaining_points))
    for point, rate in zip(remaining_points, remaining_values):
        rates[int(point.id)] = rate
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
        if point_name in existing_by_name:
            continue
        max_order += 1
        existing_by_name[point_name] = KnowledgePoint.objects.create(
            course=course,
            name=point_name,
            description="从 student1 桌面测评报告解析补齐的演示知识点。",
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
    return "桌面快照补充"


def infer_snapshot_point_level(point_name: str) -> int:
    """
    为桌面报告补充知识点推断层级。
    :param point_name: 知识点名称。
    :return: 知识点层级。
    """
    if "组成" in point_name or "模型" in point_name or "特征" in point_name:
        return 3
    return 2


def target_mastery_values(count: int) -> list[float]:
    """按目标数量生成剩余知识点掌握度值。"""
    if count <= 0:
        return []
    high = [0.84, 0.82, 0.80, 0.79, 0.78, 0.77]
    medium = [round(0.79 - index * 0.18 / 27, 3) for index in range(28)]
    low = [0.45] * 20 + [0.454] * 17 + [0.43, 0.42, 0.41, 0.40]
    return (high + medium + low)[:count]


def first_unassigned_point(
    points: list[KnowledgePoint],
    rates: dict[int, float],
    candidates: tuple[str, ...],
) -> KnowledgePoint | None:
    """按名称候选匹配一个尚未赋值的知识点。"""
    for candidate in candidates:
        for point in points:
            if int(point.id) not in rates and candidate in point.name:
                return point
    return None


def create_path_node(
    *,
    path: LearningPath,
    course: Course,
    title: str,
    index: int,
    completed_until: int,
    snapshot: DesktopSnapshot,
) -> PathNode:
    """创建单个学习路径节点。"""
    node_type = "test" if title.startswith("阶段测试") else "study"
    return PathNode.objects.create(
        path=path,
        node_type=node_type,
        knowledge_point=match_point_for_title(course, title),
        title=title,
        goal=path_goal(title, snapshot),
        criterion=path_criterion(node_type),
        suggestion=path_suggestion(title, snapshot),
        status=path_status_for_index(index, completed_until, node_type),
        order_index=index,
        estimated_minutes=snapshot.selected_minutes if title == snapshot.selected_path_title else 45,
    )


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
                    "mastery_before": Decimal("0.240") if "Spark SQL" in node.title else Decimal("0.520"),
                    "mastery_after": Decimal("0.680") if "Spark SQL" in node.title else Decimal("0.820"),
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


def path_status_for_index(index: int, completed_until: int, node_type: str) -> str:
    """根据快照进度判断路径节点状态。"""
    if index <= completed_until:
        return "completed"
    if node_type == "test":
        return "locked"
    if index == completed_until + 1:
        return "active"
    return "locked"


def find_title_index(titles: list[str], target: str) -> int:
    """查找目标路径节点序号。"""
    for index, title in enumerate(titles):
        if target in title:
            return index
    return 5


def path_goal(title: str, snapshot: DesktopSnapshot) -> str:
    """生成路径节点学习目标。"""
    if title == snapshot.selected_path_title:
        return snapshot.selected_goal
    if title.startswith("阶段测试"):
        return "检验 Spark SQL、大数据系统实践与综合实践的阶段掌握情况。"
    return f"掌握{title.replace('巩固', '').replace('基础', '')}的核心概念及应用。"


def path_criterion(node_type: str) -> str:
    """生成路径节点达标条件。"""
    if node_type == "test":
        return "阶段测试达到 60 分以上后进入后续学习。"
    return "完成推荐资源学习并能回答核心概念问题。"


def path_suggestion(title: str, snapshot: DesktopSnapshot) -> str:
    """生成路径节点学习建议。"""
    if title == snapshot.selected_path_title:
        return snapshot.selected_suggestion
    return f"结合课程资源复习{title.replace('巩固', '').replace('基础', '')}相关内容。"


def mastery_payload_for_course(*, user: User, course: Course) -> list[dict[str, object]]:
    """构建测评结果中的掌握度列表。"""
    rows = KnowledgeMastery.objects.filter(user=user, course=course).select_related("knowledge_point")
    return [
        {"point_id": row.knowledge_point_id, "point_name": row.knowledge_point.name, "mastery_rate": float(row.mastery_rate)}
        for row in rows.order_by("knowledge_point__order", "knowledge_point_id")
    ]


def question_correct_answer(question: Question, parsed: QuestionSnapshot | None) -> object:
    """读取题目标准答案。"""
    if parsed:
        return parsed.correct_answer
    if isinstance(question.answer, dict):
        return question.answer.get("answer", question.answer.get("answers", question.answer))
    return question.answer


def wrong_answer_for(correct_answer: object) -> object:
    """生成与标准答案不同的演示作答。"""
    if isinstance(correct_answer, bool):
        return not correct_answer
    if isinstance(correct_answer, str):
        return "B" if correct_answer != "B" else "A"
    if isinstance(correct_answer, list):
        return []
    return None


def answer_display(answer: object) -> str:
    """生成答案展示文本。"""
    if answer is True:
        return "正确"
    if answer is False:
        return "错误"
    if isinstance(answer, list):
        return "、".join(str(item) for item in answer)
    return str(answer)


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
            "summary": "当前画像基于桌面导出的 50 道初始评测题生成。",
            "knowledge_gaps": ["大数据技术基础", "大数据概述", "大数据基本概念"],
        },
        analysis=["系统已识别出薄弱知识点，后续学习行为会继续校准掌握度。"],
        recommendations=["优先完成当前学习路径节点，巩固 Spark SQL 原理与特征。"],
        next_tasks=["进入大数据系统实践基础节点。", "学习后重新查看画像与掌握度变化。"],
        conclusion="当前结果适合作为刚完成初始评测后的真实起点数据。",
    )


def write_snapshot_metadata(*, course: Course, snapshot: DesktopSnapshot) -> None:
    """将桌面 HTML 与资源解析摘要写入课程配置。"""
    config = dict(course.config or {})
    config["student1_desktop_demo_snapshot"] = {
        "html_files": list(DESKTOP_HTML_NAMES.values()),
        "asset_count": len(snapshot.assets),
        "asset_total_bytes": sum(asset.size for asset in snapshot.assets),
        "assets": [
            {"relative_path": asset.relative_path, "size": asset.size}
            for asset in snapshot.assets
        ],
        "score": snapshot.score,
        "correct_count": snapshot.correct_count,
        "total_count": snapshot.total_count,
        "mastery_count": len(snapshot.report_mastery),
        "path_titles": snapshot.path_titles,
        "selected_path_title": snapshot.selected_path_title,
    }
    course.config = config
    course.save(update_fields=["config", "updated_at"])
