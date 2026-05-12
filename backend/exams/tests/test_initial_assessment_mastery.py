"""学生端初始评测掌握度回归测试。"""

from __future__ import annotations

from unittest.mock import patch

from rest_framework.test import APITestCase

from assessments.services.assessment_helpers import calculate_initial_mastery_baseline
from assessments.models import AnswerHistory, Question
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint, KnowledgeRelation
from users.models import User


class StudentInitialAssessmentMasteryTests(APITestCase):
    """验证学生端初始评测掌握度写回契约。"""

    def setUp(self) -> None:
        """构造初始评测提交所需的学生、教师、课程、知识点和题目。"""
        self.student = User.objects.create_user(
            username="initial_mastery_student",
            password="Test123456",
            role="student",
        )
        self.teacher = User.objects.create_user(
            username="initial_mastery_teacher",
            password="Test123456",
            role="teacher",
        )
        self.course = Course.objects.create(
            name="学生端初测掌握度课程",
            created_by=self.teacher,
            initial_assessment_count=3,
        )
        self.pre_point = KnowledgePoint.objects.create(
            course=self.course,
            name="前置初测知识点",
            order=1,
            is_published=True,
        )
        self.post_point = KnowledgePoint.objects.create(
            course=self.course,
            name="后置初测知识点",
            order=2,
            is_published=True,
        )
        self.inferred_point = KnowledgePoint.objects.create(
            course=self.course,
            name="未测 MEFKT 推断点",
            order=3,
            is_published=True,
        )
        KnowledgeRelation.objects.create(
            course=self.course,
            pre_point=self.pre_point,
            post_point=self.post_point,
            relation_type="prerequisite",
        )
        self.pre_question = self._create_initial_question(
            content="前置初测题",
            point=self.pre_point,
        )
        self.post_question = self._create_initial_question(
            content="后置初测题",
            point=self.post_point,
        )
        self.client.force_authenticate(user=self.student)

    def _create_initial_question(self, *, content: str, point: KnowledgePoint) -> Question:
        """创建一题可用于初始评测的单选题。"""
        question = Question.objects.create(
            course=self.course,
            content=content,
            question_type="single_choice",
            options=[{"value": "A", "label": "正确"}, {"value": "B", "label": "错误"}],
            answer={"answer": "A"},
            score=1,
            is_visible=True,
            for_initial_assessment=True,
            created_by=self.teacher,
        )
        question.knowledge_points.add(point)
        return question

    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_submit_should_use_initial_prior_instead_of_raw_accuracy(
        self,
        mock_predict_mastery,
    ) -> None:
        """小样本直接写回应使用统一弱先验，避免 0/50/100 裸正确率尖峰。"""
        mock_predict_mastery.return_value = {
            "predictions": {},
            "confidence": 0.0,
            "model_type": "builtin",
        }

        response = self.client.post(
            "/api/student/assessments/initial/submit",
            {
                "course_id": self.course.id,
                "answers": {
                    str(self.pre_question.id): "B",
                    str(self.post_question.id): "A",
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        pre_mastery = float(
            KnowledgeMastery.objects.get(
                user=self.student,
                course=self.course,
                knowledge_point=self.pre_point,
            ).mastery_rate
        )
        post_mastery = float(
            KnowledgeMastery.objects.get(
                user=self.student,
                course=self.course,
                knowledge_point=self.post_point,
            ).mastery_rate
        )
        expected_pre = calculate_initial_mastery_baseline(0, 1)
        self.assertAlmostEqual(pre_mastery, expected_pre, places=3)
        self.assertAlmostEqual(post_mastery, expected_pre, places=3)
        self.assertNotIn(round(pre_mastery, 2), {0.25, 0.30, 0.50})
        self.assertNotIn(round(post_mastery, 2), {0.25, 0.30, 0.50})

    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_submit_should_ignore_fallback_unmeasured_predictions(
        self,
        mock_predict_mastery,
    ) -> None:
        """统计回退预测不能给未作答知识点批量写入固定掌握度。"""
        mock_predict_mastery.return_value = {
            "predictions": {
                self.pre_point.id: 0.52,
                self.inferred_point.id: 0.30,
            },
            "confidence": 0.3,
            "model_type": "builtin",
        }

        response = self.client.post(
            "/api/student/assessments/initial/submit",
            {
                "course_id": self.course.id,
                "answers": {
                    str(self.pre_question.id): "A",
                    str(self.post_question.id): "B",
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        mock_predict_mastery.assert_called_once()
        called_kwargs = mock_predict_mastery.call_args.kwargs
        self.assertIn(self.inferred_point.id, called_kwargs["knowledge_points"])
        self.assertFalse(
            KnowledgeMastery.objects.filter(
                user=self.student,
                course=self.course,
                knowledge_point=self.inferred_point,
            ).exists()
        )
        self.assertEqual(
            AnswerHistory.objects.filter(
                user=self.student,
                course=self.course,
                source="initial",
            ).count(),
            2,
        )

    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_submit_should_keep_real_mefkt_unmeasured_predictions(
        self,
        mock_predict_mastery,
    ) -> None:
        """真实 MEFKT 结果可以为未直接测到的已发布知识点写入推断掌握度。"""
        mock_predict_mastery.return_value = {
            "predictions": {
                self.pre_point.id: 0.61,
                self.inferred_point.id: 0.72,
            },
            "confidence": 0.8,
            "model_type": "mefkt_question_online",
        }

        response = self.client.post(
            "/api/student/assessments/initial/submit",
            {
                "course_id": self.course.id,
                "answers": {
                    str(self.pre_question.id): "A",
                    str(self.post_question.id): "A",
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        pre_mastery = float(
            KnowledgeMastery.objects.get(
                user=self.student,
                course=self.course,
                knowledge_point=self.pre_point,
            ).mastery_rate
        )
        inferred_mastery = float(
            KnowledgeMastery.objects.get(
                user=self.student,
                course=self.course,
                knowledge_point=self.inferred_point,
            ).mastery_rate
        )
        self.assertAlmostEqual(pre_mastery, calculate_initial_mastery_baseline(1, 1), places=3)
        self.assertAlmostEqual(inferred_mastery, 0.72, places=3)
