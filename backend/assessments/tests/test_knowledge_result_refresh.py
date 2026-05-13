#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
知识测评结果快照刷新回归测试。
@Project : wisdom-edu
@File : test_knowledge_result_refresh.py
@Author : Qintsg
@Date : 2026-05-13 11:45
'''

from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from assessments.models import Assessment, AssessmentQuestion, AssessmentResult, Question
from assessments.services.knowledge_result_refresh import refresh_knowledge_result_snapshot
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint
from users.models import User


class KnowledgeResultRefreshTests(TestCase):
    """验证后补知识点绑定后可重算既有初测结果快照。"""

    def setUp(self) -> None:
        """构造一个旧快照中缺少知识点绑定的知识测评结果。"""
        self.teacher = User.objects.create_user(
            username="refresh_teacher",
            password="Test123456",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="refresh_student",
            password="Test123456",
            role="student",
        )
        self.course = Course.objects.create(
            name="大数据技术与应用",
            created_by=self.teacher,
        )
        self.point = KnowledgePoint.objects.create(
            course=self.course,
            name="MapReduce工作原理",
            order=1,
            is_published=True,
        )
        self.question = Question.objects.create(
            course=self.course,
            content="MapReduce 中 Reduce 阶段的主要职责是什么？",
            question_type="single_choice",
            options=[{"value": "A", "label": "聚合中间结果"}],
            answer={"answer": "A"},
            score=2,
            created_by=self.teacher,
        )
        self.assessment = Assessment.objects.create(
            course=self.course,
            title="知识测评",
            assessment_type="knowledge",
            is_active=True,
        )
        AssessmentQuestion.objects.create(assessment=self.assessment, question=self.question, order=1)
        self.result = AssessmentResult.objects.create(
            user=self.student,
            course=self.course,
            assessment=self.assessment,
            answers={str(self.question.id): "A"},
            score=2,
            result_data={
                "mastery": [],
                "question_details": [
                    {
                        "question_id": self.question.id,
                        "student_answer": "A",
                        "correct_answer": "A",
                        "is_correct": True,
                        "knowledge_points": [],
                    }
                ],
                "total_score": 2,
                "correct_count": 1,
                "total_count": 1,
            },
        )

    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_refresh_should_update_snapshot_after_question_binding(self, mock_predict_mastery) -> None:
        """刷新后旧结果快照应带上最新知识点绑定和掌握度。"""
        self.question.knowledge_points.add(self.point)
        mock_predict_mastery.return_value = {
            "predictions": {self.point.id: 0.52},
            "confidence": 0.8,
            "model_type": "mefkt_question_online",
        }

        summary = refresh_knowledge_result_snapshot(self.result)

        self.assertIsNotNone(summary)
        self.result.refresh_from_db()
        refreshed_detail = self.result.result_data["question_details"][0]
        refreshed_mastery = self.result.result_data["mastery"][0]
        self.assertEqual(refreshed_detail["knowledge_points"], [{"id": self.point.id, "name": self.point.name}])
        self.assertEqual(refreshed_mastery["point_id"], self.point.id)
        self.assertTrue(
            KnowledgeMastery.objects.filter(
                user=self.student,
                course=self.course,
                knowledge_point=self.point,
            ).exists()
        )
