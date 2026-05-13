#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
知识测评掌握度融合回归测试。
@Project : wisdom-edu
@File : test_knowledge_mastery_blending.py
@Author : Qintsg
@Date : 2026-05-13 11:55
'''

from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from ai_services.services.path.generation_support import sync_course_mastery
from assessments.models import AnswerHistory, Question
from assessments.services.assessment_helpers import calculate_initial_mastery_baseline
from assessments.services.knowledge_assessment_logic import blend_mastery_with_kt
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint
from users.profiles.generation import refresh_mastery_with_kt
from users.models import User


class KnowledgeMasteryBlendingTests(TestCase):
    """验证初测融合不会把单题知识点重新压成尖峰。"""

    def setUp(self) -> None:
        """构造一对单题对错知识点。"""
        self.teacher = User.objects.create_user(
            username="blend_teacher",
            password="Test123456",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="blend_student",
            password="Test123456",
            role="student",
        )
        self.course = Course.objects.create(
            name="融合测试课程",
            created_by=self.teacher,
        )
        self.wrong_point = KnowledgePoint.objects.create(
            course=self.course,
            name="单题错误知识点",
            order=1,
            is_published=True,
        )
        self.correct_point = KnowledgePoint.objects.create(
            course=self.course,
            name="单题正确知识点",
            order=2,
            is_published=True,
        )

    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_real_mefkt_should_soften_single_question_peaks(self, mock_predict_mastery) -> None:
        """真实 MEFKT 应削弱一题对错造成的 28% / 61% 固定峰值。"""
        mock_predict_mastery.return_value = {
            "predictions": {
                self.wrong_point.id: 0.49,
                self.correct_point.id: 0.50,
            },
            "confidence": 0.8,
            "model_type": "mefkt_question_online",
        }
        mastery_map = {
            self.wrong_point.id: calculate_initial_mastery_baseline(0, 1),
            self.correct_point.id: calculate_initial_mastery_baseline(1, 1),
        }
        point_stats = {
            self.wrong_point.id: {"correct": 0, "total": 1, "name": self.wrong_point.name},
            self.correct_point.id: {"correct": 1, "total": 1, "name": self.correct_point.name},
        }
        answer_history = [
            {"question_id": 1, "knowledge_point_id": self.wrong_point.id, "correct": 0},
            {"question_id": 2, "knowledge_point_id": self.correct_point.id, "correct": 1},
        ]

        blended = blend_mastery_with_kt(
            user_id=1,
            course_id=int(self.course.id),
            mastery_map=mastery_map,
            point_stats=point_stats,
            answer_history_records=answer_history,
        )

        self.assertGreater(blended[self.wrong_point.id], 0.30)
        self.assertLess(blended[self.correct_point.id], 0.60)
        self.assertLess(blended[self.wrong_point.id], blended[self.correct_point.id])

    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_path_mastery_sync_should_keep_initial_answer_signal(self, mock_predict_mastery) -> None:
        """路径生成同步不应把初测一错一对覆盖成相同 MEFKT 原始概率。"""
        self._create_initial_answer_history()
        mock_predict_mastery.return_value = {
            "predictions": {
                self.wrong_point.id: 0.49,
                self.correct_point.id: 0.50,
            },
            "confidence": 0.8,
            "model_type": "mefkt_question_online",
        }

        mastery = sync_course_mastery(
            user=self.student,
            course=self.course,
            course_point_ids=[self.wrong_point.id, self.correct_point.id],
        )

        self.assertLess(mastery[self.wrong_point.id], mastery[self.correct_point.id])
        self.assertLess(float(KnowledgeMastery.objects.get(
            user=self.student,
            knowledge_point=self.wrong_point,
        ).mastery_rate), 0.45)
        self.assertGreater(float(KnowledgeMastery.objects.get(
            user=self.student,
            knowledge_point=self.correct_point,
        ).mastery_rate), 0.50)

    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_profile_kt_refresh_should_keep_initial_answer_signal(self, mock_predict_mastery) -> None:
        """画像 KT 刷新不应把初测直接证据覆盖成接近 50% 的平坦预测。"""
        self._create_initial_answer_history()
        mock_predict_mastery.return_value = {
            "predictions": {
                self.wrong_point.id: 0.49,
                self.correct_point.id: 0.50,
            },
            "confidence": 0.8,
            "model_type": "mefkt_question_online",
        }

        mastery = refresh_mastery_with_kt(self.student, int(self.course.id))

        self.assertLess(mastery[self.wrong_point.id], mastery[self.correct_point.id])
        self.assertLess(float(KnowledgeMastery.objects.get(
            user=self.student,
            knowledge_point=self.wrong_point,
        ).mastery_rate), 0.45)
        self.assertGreater(float(KnowledgeMastery.objects.get(
            user=self.student,
            knowledge_point=self.correct_point,
        ).mastery_rate), 0.50)

    def _create_initial_answer_history(self) -> None:
        """创建一错一对的初始测评历史。"""
        wrong_question = Question.objects.create(
            course=self.course,
            content="错误题",
            question_type="single_choice",
            options=[{"value": "A", "label": "A"}, {"value": "B", "label": "B"}],
            answer={"answer": "A"},
            score=2,
            created_by=self.teacher,
        )
        wrong_question.knowledge_points.add(self.wrong_point)
        correct_question = Question.objects.create(
            course=self.course,
            content="正确题",
            question_type="single_choice",
            options=[{"value": "A", "label": "A"}, {"value": "B", "label": "B"}],
            answer={"answer": "A"},
            score=2,
            created_by=self.teacher,
        )
        correct_question.knowledge_points.add(self.correct_point)
        AnswerHistory.objects.create(
            user=self.student,
            course=self.course,
            question=wrong_question,
            knowledge_point=self.wrong_point,
            student_answer={"answer": "B"},
            correct_answer={"answer": "A"},
            is_correct=False,
            source="initial",
        )
        AnswerHistory.objects.create(
            user=self.student,
            course=self.course,
            question=correct_question,
            knowledge_point=self.correct_point,
            student_answer={"answer": "A"},
            correct_answer={"answer": "A"},
            is_correct=True,
            source="initial",
        )
