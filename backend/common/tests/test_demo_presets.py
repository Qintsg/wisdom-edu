#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
student1 大数据学习状态预置数据回归测试。
@Project : wisdom-edu
@File : test_demo_presets.py
@Author : Qintsg
@Date : 2026-05-13 19:50
'''

from __future__ import annotations

from django.test import TestCase

from assessments.models import (
    AnswerHistory,
    AssessmentResult,
    AssessmentStatus,
    Question,
)
from courses.models import Course
from exams.models import FeedbackReport
from knowledge.models import KnowledgeMastery, KnowledgePoint, Resource
from learning.models import LearningPath, NodeProgress, PathNode
from tools.demo_student1_snapshot import preset_student1_big_data_snapshot
from tools.demo_student1_snapshot_parse import load_inline_snapshot
from users.models import HabitPreference, User


class StudentDesktopSnapshotPresetTests(TestCase):
    """验证 student1 大数据课程内置预置链路。"""

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
                    "大数据概述",
                    "大数据技术基础",
                    "大数据基本概念",
                    "大数据存储与管理",
                    "Spark定义与特征",
                    "Spark SQL原理与特征",
                    "大数据智能分析挖掘",
                    "基于潜在因子的推荐方法",
                    "大数据系统实践",
                    "综合实践",
                    "PySpark自然语言处理实践",
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
        self.resource.knowledge_points.add(self.points[5])
        self.questions = [self._create_question(index=1, point=self.points[0])]

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

    def test_inline_snapshot_should_define_complete_student_state(self) -> None:
        """内置预置内容应包含画像、测评、掌握度和路径所需数据。"""
        snapshot = load_inline_snapshot()

        self.assertEqual(snapshot.score, 80)
        self.assertEqual(snapshot.correct_count, 40)
        self.assertEqual(snapshot.total_count, 50)
        self.assertEqual(len(snapshot.question_details), 50)
        self.assertEqual(len(snapshot.report_mastery), 74)
        self.assertEqual(snapshot.report_mastery["Spark SQL原理与特征"], 0.24)
        first_question = snapshot.question_details[0]
        second_question = snapshot.question_details[1]
        tf_question = snapshot.question_details[47]
        self.assertEqual(first_question.content, "大数据的四个V特征中，'Variety'指的是数据的什么性质？")
        self.assertEqual(first_question.options[1]["content"], "数据多样性")
        self.assertEqual(first_question.student_answer, "B")
        self.assertEqual(first_question.correct_answer, "B")
        self.assertIn("Variety", first_question.analysis)
        self.assertEqual(first_question.knowledge_point_names, ["大数据基本概念"])
        self.assertFalse(second_question.is_correct)
        self.assertEqual(second_question.student_answer, "A")
        self.assertEqual(second_question.correct_answer, "B")
        self.assertEqual(tf_question.question_type, "true_false")
        self.assertEqual(tf_question.options[0]["content"], "正确")
        self.assertEqual(tf_question.options[1]["content"], "错误")
        self.assertEqual(tf_question.student_answer_display, "true")
        self.assertEqual(tf_question.knowledge_point_names, ["推荐系统"])
        self.assertEqual(
            len([question for question in snapshot.question_details if question.knowledge_point_names]),
            50,
        )
        self.assertEqual(snapshot.selected_path_title, "Spark SQL原理与特征基础")
        self.assertEqual(snapshot.selected_minutes, 52)
        self.assertEqual(len(snapshot.path_titles), 9)
        self.assertEqual(len([node for node in snapshot.path_nodes if node.status == "completed"]), 8)
        self.assertIn("当前画像基于课程资源示例", snapshot.feedback_report.summary)
        self.assertIn("整体掌握仅57.3%", snapshot.profile_summary)
        self.assertIn("建议利用晚间", snapshot.profile_suggestion)

    def test_preset_student1_snapshot_should_seed_visible_student_state(self) -> None:
        """目标课程预置后，学生端门禁、掌握度、初测结果和路径均可读取。"""
        summary = preset_student1_big_data_snapshot()

        self.assertTrue(summary.applied)
        self.assertEqual(summary.mastery_count, 74)
        self.assertEqual(summary.question_count, 50)
        self.assertEqual(summary.path_node_count, 9)

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
            50,
        )
        result = AssessmentResult.objects.get(
            user=self.student,
            course=self.course,
            assessment__assessment_type="knowledge",
        )
        self.assertEqual(float(result.score), 80.0)
        self.assertEqual(result.result_data["correct_count"], 40)
        self.assertEqual(result.result_data["total_count"], 50)
        self.assertEqual(len(result.result_data["question_details"]), 50)
        self.assertEqual(len(result.result_data["mastery"]), 74)
        first_detail = result.result_data["question_details"][0]
        second_detail = result.result_data["question_details"][1]
        tf_detail = result.result_data["question_details"][47]
        self.assertEqual(first_detail["content"], "大数据的四个V特征中，'Variety'指的是数据的什么性质？")
        self.assertEqual(first_detail["options"][1]["label"], "数据多样性")
        self.assertTrue(first_detail["options"][1]["is_correct_option"])
        self.assertTrue(first_detail["options"][1]["is_student_selected"])
        self.assertEqual(first_detail["knowledge_points"][0]["name"], "大数据基本概念")
        self.assertFalse(second_detail["is_correct"])
        self.assertEqual(second_detail["student_answer"], "A")
        self.assertEqual(second_detail["correct_answer"], "B")
        self.assertEqual(tf_detail["question_type"], "true_false")
        self.assertEqual(tf_detail["options"][0]["label"], "正确")
        self.assertEqual(tf_detail["student_answer_display"], "true")
        report = FeedbackReport.objects.get(
            user=self.student,
            source="assessment",
            assessment_result=result,
        )
        self.assertEqual(report.status, "completed")
        self.assertIn("当前画像基于课程资源示例", report.overview["summary"])
        self.assertIn("优先学习路径中的首个激活节点", report.recommendations[0])
        spark_sql_mastery = KnowledgeMastery.objects.get(
            user=self.student,
            course=self.course,
            knowledge_point__name="Spark SQL原理与特征",
        )
        self.assertEqual(float(spark_sql_mastery.mastery_rate), 0.24)
        path = LearningPath.objects.get(user=self.student, course=self.course)
        nodes = list(PathNode.objects.filter(path=path).order_by("order_index"))
        self.assertEqual(len(nodes), 9)
        completed_nodes = [node for node in nodes if node.status == "completed"]
        self.assertEqual([node.order_index for node in completed_nodes], list(range(8)))
        spark_sql_node = next(node for node in nodes if node.title == "Spark SQL原理与特征基础")
        test_node = nodes[-1]
        self.assertEqual(spark_sql_node.status, "completed")
        self.assertEqual(test_node.status, "active")
        self.assertTrue(NodeProgress.objects.filter(user=self.student, node=spark_sql_node).exists())
        self.course.refresh_from_db()
        self.assertEqual(
            self.course.config["student1_big_data_preset"]["mastery_count"],
            74,
        )
        self.assertEqual(
            self.course.config["student1_big_data_preset"]["completed_nodes"],
            8,
        )

    def test_preset_student1_snapshot_should_be_idempotent(self) -> None:
        """重复执行预置不会叠加初测历史、结果或路径节点。"""
        first_summary = preset_student1_big_data_snapshot()
        second_summary = preset_student1_big_data_snapshot()

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
        """非大数据课程不会写入预置数据。"""
        other_course = Course.objects.create(
            name="Python 程序设计",
            created_by=self.teacher,
        )

        summary = preset_student1_big_data_snapshot(course_name=other_course.name)

        self.assertFalse(summary.applied)
        self.assertEqual(KnowledgeMastery.objects.filter(course=other_course).count(), 0)
