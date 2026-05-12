"""Learning-path mastery refresh regression tests."""

from unittest.mock import patch

from rest_framework.test import APITestCase

from assessments.models import AnswerHistory, Question
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint, ProfileSummary
from learning.models import LearningPath, PathNode
from users.models import User


class LearningPathMasteryRefreshTests(APITestCase):
    """验证路径刷新写回掌握度时区分真实 MEFKT 与统计回退。"""

    def setUp(self):
        """创建包含已测点与未测点的最小学习路径。"""
        self.student = User.objects.create_user(
            username="mastery_refresh_student",
            password="Test123456",
            role="student",
        )
        self.teacher = User.objects.create_user(
            username="mastery_refresh_teacher",
            password="Test123456",
            role="teacher",
        )
        self.course = Course.objects.create(
            name="路径掌握度刷新课程",
            created_by=self.teacher,
        )
        self.point_done = KnowledgePoint.objects.create(
            course=self.course, name="已测知识点", order=1, is_published=True
        )
        self.point_future = KnowledgePoint.objects.create(
            course=self.course, name="未测知识点", order=2, is_published=True
        )
        self.path = LearningPath.objects.create(
            user=self.student,
            course=self.course,
            ai_reason="原始路径",
        )
        PathNode.objects.create(
            path=self.path,
            knowledge_point=self.point_done,
            title="已完成节点",
            node_type="study",
            status="completed",
            order_index=0,
        )
        PathNode.objects.create(
            path=self.path,
            knowledge_point=self.point_future,
            title="旧未来节点",
            node_type="study",
            status="locked",
            order_index=1,
        )
        KnowledgeMastery.objects.create(
            user=self.student,
            course=self.course,
            knowledge_point=self.point_done,
            mastery_rate=0.45,
        )
        KnowledgeMastery.objects.create(
            user=self.student,
            course=self.course,
            knowledge_point=self.point_future,
            mastery_rate=0.3,
        )
        ProfileSummary.objects.create(
            user=self.student,
            course=self.course,
            summary="当前画像摘要",
            weakness="当前薄弱点",
            suggestion="当前建议",
        )
        self.question = Question.objects.create(
            course=self.course,
            content="路径刷新证据题",
            question_type="single_choice",
            options=[{"value": "A", "label": "A"}],
            answer={"answer": "A"},
            score=1,
            is_visible=True,
            created_by=self.teacher,
        )
        self.question.knowledge_points.add(self.point_done)
        AnswerHistory.objects.create(
            user=self.student,
            course=self.course,
            question=self.question,
            knowledge_point=self.point_done,
            student_answer={"answer": "A"},
            correct_answer={"answer": "A"},
            is_correct=True,
            score=1,
            source="initial",
        )
        self.client.force_authenticate(user=self.student)

    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_refresh_learning_path_should_keep_mefkt_inferred_unmeasured_mastery(
        self,
        mock_predict_mastery,
    ):
        """真实 MEFKT 输出可以推断未直接测到的未来知识点。"""
        mock_predict_mastery.return_value = {
            "predictions": {
                self.point_done.id: 0.82,
                self.point_future.id: 0.74,
            },
            "confidence": 0.8,
            "model_type": "mefkt_question_online",
            "answer_count": 1,
        }

        response = self.client.post(
            "/api/student/ai/refresh-learning-path",
            {"course_id": self.course.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        future_mastery = KnowledgeMastery.objects.get(
            user=self.student,
            course=self.course,
            knowledge_point=self.point_future,
        )
        self.assertAlmostEqual(float(future_mastery.mastery_rate), 0.74, places=3)

    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_refresh_learning_path_should_ignore_builtin_unmeasured_mastery(
        self,
        mock_predict_mastery,
    ):
        """统计回退不能把未测知识点覆盖成默认或低置信预测。"""
        mock_predict_mastery.return_value = {
            "predictions": {
                self.point_done.id: 0.82,
                self.point_future.id: 0.4,
            },
            "confidence": 0.3,
            "model_type": "builtin",
            "answer_count": 1,
        }

        response = self.client.post(
            "/api/student/ai/refresh-learning-path",
            {"course_id": self.course.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        future_mastery = KnowledgeMastery.objects.get(
            user=self.student,
            course=self.course,
            knowledge_point=self.point_future,
        )
        self.assertAlmostEqual(float(future_mastery.mastery_rate), 0.3, places=3)
