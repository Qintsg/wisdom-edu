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

from assessments.services.assessment_helpers import calculate_initial_mastery_baseline
from assessments.services.knowledge_assessment_logic import blend_mastery_with_kt
from courses.models import Course
from knowledge.models import KnowledgePoint
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
