#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
student1 桌面快照预置数据回归测试。
@Project : wisdom-edu
@File : test_demo_presets.py
@Author : Qintsg
@Date : 2026-05-13 19:50
'''

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase

from assessments.models import (
    AnswerHistory,
    AssessmentResult,
    AssessmentStatus,
    Question,
)
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint, Resource
from learning.models import LearningPath, NodeProgress, PathNode
from tools.demo_student1_snapshot import preset_student1_big_data_snapshot
from tools.demo_student1_snapshot_parse import load_desktop_snapshot
from tools.demo_student1_snapshot_types import DESKTOP_HTML_NAMES
from users.models import HabitPreference, User


class StudentDesktopSnapshotPresetTests(TestCase):
    """验证 student1 大数据课程桌面快照预置链路。"""

    def setUp(self) -> None:
        """构造预置服务所需的教师、学生、课程、知识点和题库。"""
        self.teacher = User.objects.create_user(
            username="teacher1",
            password="Test123456",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="student1",
            password="Test123456",
            role="student",
        )
        self.course = Course.objects.create(
            name="大数据技术与应用",
            created_by=self.teacher,
            initial_assessment_count=3,
        )
        self.points = [
            KnowledgePoint.objects.create(
                course=self.course,
                name=name,
                order=index,
                is_published=True,
            )
            for index, name in enumerate(
                [
                    "大数据存储与管理",
                    "Spark定义与特征",
                    "Spark SQL原理与特征",
                    "大数据系统实践",
                    "综合实践",
                ]
            )
        ]
        self.resource = Resource.objects.create(
            course=self.course,
            title="Spark SQL 原理与特征讲义",
            resource_type="document",
            url="https://edu.qintsg.xyz/resources/spark-sql",
            is_visible=True,
            uploaded_by=self.teacher,
        )
        self.resource.knowledge_points.add(self.points[2])
        self.questions = [
            self._create_question(index=index, point=point)
            for index, point in enumerate(self.points[:3], start=1)
        ]

    def _create_question(self, *, index: int, point: KnowledgePoint) -> Question:
        """
        创建一题初始测评判断题。
        :param index: 题目序号。
        :param point: 关联知识点。
        :return: 题目对象。
        """
        question = Question.objects.create(
            course=self.course,
            content=f"初始评测题 {index}：{point.name} 是否属于大数据课程核心内容？",
            question_type="true_false",
            options=[],
            answer={"answer": True},
            score=2,
            is_visible=True,
            for_initial_assessment=True,
            created_by=self.teacher,
        )
        question.knowledge_points.add(point)
        return question

    def test_load_desktop_snapshot_should_parse_html_and_assets(self) -> None:
        """解析三份 HTML 后应得到报告、画像、路径和资源摘要。"""
        with TemporaryDirectory() as root:
            desktop_root = Path(root)
            self._write_snapshot_files(desktop_root)

            snapshot = load_desktop_snapshot(desktop_root)

        self.assertEqual(snapshot.score, 80)
        self.assertEqual(snapshot.correct_count, 2)
        self.assertEqual(snapshot.total_count, 3)
        self.assertEqual(len(snapshot.question_details), 3)
        self.assertEqual(snapshot.report_mastery["Spark SQL原理与特征"], 0.24)
        self.assertEqual(snapshot.selected_path_title, "Spark SQL原理与特征基础")
        self.assertEqual(snapshot.selected_minutes, 52)
        self.assertEqual(len(snapshot.path_titles), 9)
        self.assertEqual(len(snapshot.assets), 3)

    def test_preset_student1_snapshot_should_seed_visible_student_state(self) -> None:
        """目标课程预置后，学生端门禁、掌握度、初测结果和路径均可读取。"""
        with TemporaryDirectory() as root:
            desktop_root = Path(root)
            self._write_snapshot_files(desktop_root)

            summary = preset_student1_big_data_snapshot(desktop_root=desktop_root)

        self.assertTrue(summary.applied)
        self.assertEqual(summary.mastery_count, 5)
        self.assertEqual(summary.question_count, 3)
        self.assertEqual(summary.path_node_count, 9)
        self.assertEqual(summary.asset_count, 3)

        status = AssessmentStatus.objects.get(user=self.student, course=self.course)
        self.assertTrue(status.knowledge_done)
        self.assertTrue(status.ability_done)
        self.assertTrue(status.habit_done)
        self.assertFalse(status.generating)
        self.assertTrue(HabitPreference.objects.filter(user=self.student).exists())
        self.assertEqual(
            AnswerHistory.objects.filter(
                user=self.student,
                course=self.course,
                source="initial",
            ).count(),
            3,
        )
        result = AssessmentResult.objects.get(
            user=self.student,
            course=self.course,
            assessment__assessment_type="knowledge",
        )
        self.assertEqual(float(result.score), 80.0)
        self.assertEqual(result.result_data["correct_count"], 2)
        self.assertEqual(result.result_data["total_count"], 3)
        self.assertEqual(len(result.result_data["question_details"]), 3)
        self.assertEqual(len(result.result_data["mastery"]), 5)
        spark_sql_mastery = KnowledgeMastery.objects.get(
            user=self.student,
            course=self.course,
            knowledge_point__name="Spark SQL原理与特征",
        )
        self.assertEqual(float(spark_sql_mastery.mastery_rate), 0.24)
        path = LearningPath.objects.get(user=self.student, course=self.course)
        nodes = list(PathNode.objects.filter(path=path).order_by("order_index"))
        spark_sql_node = next(node for node in nodes if node.title == "Spark SQL原理与特征基础")
        next_node = next(node for node in nodes if node.title == "大数据系统实践基础")
        self.assertEqual(spark_sql_node.status, "completed")
        self.assertEqual(next_node.status, "active")
        self.assertTrue(
            NodeProgress.objects.filter(user=self.student, node=spark_sql_node).exists()
        )
        self.course.refresh_from_db()
        self.assertEqual(
            self.course.config["student1_desktop_demo_snapshot"]["asset_count"],
            3,
        )
        self.assertEqual(
            len(self.course.config["student1_desktop_demo_snapshot"]["assets"]),
            3,
        )

    def test_preset_student1_snapshot_should_be_idempotent(self) -> None:
        """重复执行预置不会叠加初测历史、结果或路径节点。"""
        with TemporaryDirectory() as root:
            desktop_root = Path(root)
            self._write_snapshot_files(desktop_root)

            first_summary = preset_student1_big_data_snapshot(desktop_root=desktop_root)
            second_summary = preset_student1_big_data_snapshot(desktop_root=desktop_root)

        self.assertTrue(first_summary.applied)
        self.assertTrue(second_summary.applied)
        self.assertEqual(
            AnswerHistory.objects.filter(
                user=self.student,
                course=self.course,
                source="initial",
            ).count(),
            first_summary.question_count,
        )
        self.assertEqual(
            AssessmentResult.objects.filter(
                user=self.student,
                course=self.course,
                assessment__assessment_type="knowledge",
            ).count(),
            1,
        )
        path = LearningPath.objects.get(user=self.student, course=self.course)
        self.assertEqual(path.nodes.count(), first_summary.path_node_count)

    def test_preset_student1_snapshot_should_skip_non_demo_course(self) -> None:
        """非大数据课程不会写入演示预置数据。"""
        other_course = Course.objects.create(
            name="Python 程序设计",
            created_by=self.teacher,
        )

        summary = preset_student1_big_data_snapshot(course_name=other_course.name)

        self.assertFalse(summary.applied)
        self.assertEqual(KnowledgeMastery.objects.filter(course=other_course).count(), 0)

    def _write_snapshot_files(self, root: Path) -> None:
        """
        写入最小可解析的桌面 HTML 和资源目录。
        :param root: 临时桌面目录。
        :return: None。
        """
        for key, file_name in DESKTOP_HTML_NAMES.items():
            (root / file_name).write_text(
                self._html_for_key(key),
                encoding="utf-8",
            )
            asset_dir = root / file_name.replace(".html", "_files")
            asset_dir.mkdir(parents=True, exist_ok=True)
            (asset_dir / f"{key}.css").write_text("body{}", encoding="utf-8")

    def _html_for_key(self, key: str) -> str:
        """
        返回指定页面的测试 HTML。
        :param key: 页面类型。
        :return: HTML 内容。
        """
        if key == "report":
            return self._report_html()
        if key == "profile":
            return self._profile_html()
        return self._path_html()

    def _report_html(self) -> str:
        """
        构造最小测评报告 HTML。
        :return: HTML 内容。
        """
        items = [
            ("大数据存储与管理", 98),
            ("Spark定义与特征", 87),
            ("Spark SQL原理与特征", 24),
            ("大数据系统实践", 24),
            ("综合实践", 29),
        ]
        mastery = "".join(
            f'<span class="mastery-name">{name}</span><span class="mastery-value">{value}%</span>'
            for name, value in items
        )
        questions = "".join(
            self._question_html(index=index, is_correct=index < 3)
            for index in range(1, 4)
        )
        return (
            "<html><body>"
            "<div>80 / 100</div><div>答对 2 / 3 题</div>"
            f"{mastery}{questions}"
            "</body></html>"
        )

    def _question_html(self, *, index: int, is_correct: bool) -> str:
        """
        构造单题 HTML。
        :param index: 题号。
        :param is_correct: 是否作答正确。
        :return: HTML 片段。
        """
        status = "正确" if is_correct else "错误"
        student = "true" if is_correct else "false"
        return (
            '<div data-v-fba69e73="" class="el-collapse-item">'
            f'第 {index} 题<span class="el-tag__content">{status}</span>'
            f'<p class="question-content">初始评测题 {index}</p>'
            f'你的答案：</span><span>{student}</span>'
            '正确答案：</span><span>true</span>'
            '<p><span>解析：</span>需要结合课程资源复习。</p>'
            "</div>"
        )

    def _profile_html(self) -> str:
        """
        构造最小画像 HTML。
        :return: HTML 内容。
        """
        return (
            "<html><body>"
            "画像总结整体掌握度 57.3%，高掌握 2 个。"
            "薄弱环节 Spark SQL原理与特征（24%），综合实践（29%）。"
            "AI 学习建议"
            "系统基于当前画像，推荐以下学习动作：优先巩固 Spark SQL。"
            "处理速度: 60 / 100 工作记忆: 60 / 100 知觉推理: 60 / 100 言语理解: 60 / 100"
            "高效型学习者 视觉型 晚间学习 自适应"
            "退出登录"
            "</body></html>"
        )

    def _path_html(self) -> str:
        """
        构造最小学习路径 HTML。
        :return: HTML 内容。
        """
        titles = [
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
        stations = "".join(
            f'<div class="station-label completed">{title}</div>'
            for title in titles
        )
        return (
            "<html><body>"
            f"{stations}"
            "阶段测试：Spark SQL原理与特征、大数据系统实践、综合实践\n"
            "Spark SQL原理与特征基础\n"
            "预计 52 分钟 掌握Spark SQL原理与特征的核心概念及应用 "
            "重点学习Spark SQL原理与特征相关内容。"
            "</body></html>"
        )
