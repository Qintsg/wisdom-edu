#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
课程内容绑定服务回归测试。
@Project : wisdom-edu
@File : test_content_binding.py
@Author : Qintsg
@Date : 2026-05-13 10:40
'''

from __future__ import annotations

from django.test import TestCase

from assessments.models import Question
from courses.models import Course
from knowledge.models import KnowledgePoint, Resource
from knowledge.services.content_binding import CourseContentBindingService
from users.models import User


class CourseContentBindingServiceTests(TestCase):
    """验证课程题目与资源可自动补齐知识点绑定。"""

    def setUp(self) -> None:
        """构造大数据课程中常见的未绑定题目与资源。"""
        self.teacher = User.objects.create_user(
            username="binding_teacher",
            password="Test123456",
            role="teacher",
        )
        self.course = Course.objects.create(
            name="大数据技术与应用",
            created_by=self.teacher,
        )
        self.spark_point = KnowledgePoint.objects.create(
            course=self.course,
            name="Spark",
            order=1,
            is_published=True,
        )
        self.spark_sql_point = KnowledgePoint.objects.create(
            course=self.course,
            name="Spark SQL基本操作",
            order=2,
            is_published=True,
        )
        self.recommend_point = KnowledgePoint.objects.create(
            course=self.course,
            name="PySpark推荐应用",
            order=3,
            is_published=True,
        )
        self.text_point = KnowledgePoint.objects.create(
            course=self.course,
            name="PySpark文本处理应用",
            order=4,
            is_published=True,
        )
        self.hadoop_point = KnowledgePoint.objects.create(
            course=self.course,
            name="Hadoop",
            order=5,
            is_published=True,
        )
        self.mapreduce_workflow_point = KnowledgePoint.objects.create(
            course=self.course,
            name="MapReduce工作原理",
            order=6,
            is_published=True,
        )
        self.linear_model_point = KnowledgePoint.objects.create(
            course=self.course,
            name="线性回归模型原理",
            order=7,
            is_published=True,
        )
        self.pyspark_linear_point = KnowledgePoint.objects.create(
            course=self.course,
            name="PySpark线性回归应用",
            order=8,
            is_published=True,
        )
        self.nosql_point = KnowledgePoint.objects.create(
            course=self.course,
            name="NoSql数据库",
            order=9,
            is_published=True,
        )
        self.hadoop_install_point = KnowledgePoint.objects.create(
            course=self.course,
            name="Hadoop安装与使用",
            order=10,
            is_published=True,
        )
        self.big_data_concept_point = KnowledgePoint.objects.create(
            course=self.course,
            name="大数据基本概念",
            order=11,
            is_published=True,
        )
        self.big_data_app_point = KnowledgePoint.objects.create(
            course=self.course,
            name="大数据应用",
            order=12,
            is_published=True,
        )
        self.question = Question.objects.create(
            course=self.course,
            content="在 PySpark 中，下列哪一项常用于去除停用词（stop words）？",
            question_type="single_choice",
            options=[{"value": "A", "label": "StopWordsRemover"}],
            answer={"answer": "A"},
            created_by=self.teacher,
        )
        self.resource = Resource.objects.create(
            course=self.course,
            title="7.4 Spark SQL基本操作",
            resource_type="document",
            uploaded_by=self.teacher,
        )
        self.combo_resource = Resource.objects.create(
            course=self.course,
            title="PySpark机器学习自然语言处理与推荐系统",
            resource_type="document",
            uploaded_by=self.teacher,
        )
        self.mapreduce_question = Question.objects.create(
            course=self.course,
            content="Hadoop WordCount 示例中，Map 和 Reduce 阶段的主要职责是什么？",
            question_type="single_choice",
            options=[{"value": "A", "label": "分词与聚合"}],
            answer={"answer": "A"},
            created_by=self.teacher,
        )
        self.pyspark_linear_question = Question.objects.create(
            course=self.course,
            content="在 PySpark 中，实现线性回归模型训练通常使用哪个组件？",
            question_type="single_choice",
            options=[{"value": "A", "label": "LinearRegression"}],
            answer={"answer": "A"},
            created_by=self.teacher,
        )
        self.hbase_question = Question.objects.create(
            course=self.course,
            content="下面关于 Region 的说法，哪个是错误的？",
            question_type="single_choice",
            options=[{"value": "A", "label": "Region 是 HBase 的数据分片"}],
            answer={"answer": "A"},
            created_by=self.teacher,
        )
        self.linux_resource = Resource.objects.create(
            course=self.course,
            title="2.4 Linux基础",
            resource_type="document",
            uploaded_by=self.teacher,
        )
        self.big_data_video = Resource.objects.create(
            course=self.course,
            title="1.2 大数据概念和影响",
            resource_type="video",
            uploaded_by=self.teacher,
        )

    def test_build_plan_should_prefer_specific_big_data_points(self) -> None:
        """绑定计划应优先选择具体知识点，避免只落到 Spark 泛化节点。"""
        service = CourseContentBindingService(course_id=int(self.course.id))

        plan = service.build_plan()

        question_change = next(change for change in plan.question_changes if change.item_id == self.question.id)
        resource_change = next(change for change in plan.resource_changes if change.item_id == self.resource.id)
        combo_change = next(change for change in plan.resource_changes if change.item_id == self.combo_resource.id)
        mapreduce_change = next(change for change in plan.question_changes if change.item_id == self.mapreduce_question.id)
        pyspark_linear_change = next(
            change for change in plan.question_changes if change.item_id == self.pyspark_linear_question.id
        )
        hbase_change = next(change for change in plan.question_changes if change.item_id == self.hbase_question.id)
        linux_change = next(change for change in plan.resource_changes if change.item_id == self.linux_resource.id)
        big_data_change = next(change for change in plan.resource_changes if change.item_id == self.big_data_video.id)
        self.assertEqual(question_change.point_names, ("PySpark文本处理应用",))
        self.assertEqual(resource_change.point_names, ("Spark SQL基本操作",))
        self.assertEqual(combo_change.point_names, ("PySpark推荐应用", "PySpark文本处理应用"))
        self.assertEqual(mapreduce_change.point_names, ("MapReduce工作原理",))
        self.assertEqual(pyspark_linear_change.point_names, ("PySpark线性回归应用",))
        self.assertEqual(hbase_change.point_names, ("NoSql数据库",))
        self.assertEqual(linux_change.point_names, ("Hadoop安装与使用",))
        self.assertEqual(big_data_change.point_names, ("大数据基本概念", "大数据应用"))

    def test_apply_plan_should_write_question_and_resource_bindings(self) -> None:
        """应用绑定计划后题目和资源应具备可供 MEFKT 使用的知识点关系。"""
        service = CourseContentBindingService(course_id=int(self.course.id))
        plan = service.build_plan()

        service.apply_plan(plan)

        self.assertEqual(
            list(self.question.knowledge_points.values_list("name", flat=True)),
            ["PySpark文本处理应用"],
        )
        self.assertEqual(
            list(self.resource.knowledge_points.values_list("name", flat=True)),
            ["Spark SQL基本操作"],
        )
