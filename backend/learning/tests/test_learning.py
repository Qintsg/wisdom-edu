"""Regression tests for learning-path APIs and stage-test scoring."""

from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APITestCase

from assessments.models import Question
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint, KnowledgeRelation, ProfileSummary, Resource
from learning.models import LearningPath, NodeProgress, PathNode
from learning.paths.rules import apply_prerequisite_caps
from users.models import User


class PrerequisiteCapTests(TestCase):
    """验证前置掌握度约束覆盖 KT 预测中的非发布知识点。"""

    def test_caps_should_apply_to_unpublished_predicted_point(self):
        """非发布后继点仍应受已知前置点掌握度上限约束。"""
        teacher = User.objects.create_user(
            username="cap_teacher",
            password="Test123456",
            role="teacher",
        )
        course = Course.objects.create(
            name="前置约束课程",
            created_by=teacher,
        )
        prerequisite = KnowledgePoint.objects.create(
            course=course,
            name="前置知识点",
            order=1,
            is_published=True,
        )
        predicted_only = KnowledgePoint.objects.create(
            course=course,
            name="预测后继知识点",
            order=2,
            is_published=False,
        )
        KnowledgeRelation.objects.create(
            course=course,
            pre_point=prerequisite,
            post_point=predicted_only,
            relation_type="prerequisite",
        )

        adjusted = apply_prerequisite_caps(
            {
                prerequisite.id: 0.4,
                predicted_only.id: 0.9,
            },
            course.id,
        )

        self.assertEqual(adjusted[predicted_only.id], 0.4)


class LearningResourceRouteTests(APITestCase):
    """Exercise resource-completion routes exposed on learning path nodes."""

    def setUp(self):
        """Create a study node whose external resources are addressed by string IDs."""
        self.student = User.objects.create_user(
            username="student_route",
            password="Test123456",
            role="student",
        )
        self.teacher = User.objects.create_user(
            username="teacher_route",
            password="Test123456",
            role="teacher",
        )
        self.course = Course.objects.create(
            name="学习路径测试课程",
            created_by=self.teacher,
        )
        self.point = KnowledgePoint.objects.create(
            course=self.course,
            name="判断题知识点",
        )
        self.path = LearningPath.objects.create(
            user=self.student,
            course=self.course,
            ai_reason="测试路径",
        )
        self.node = PathNode.objects.create(
            path=self.path,
            knowledge_point=self.point,
            title="外部资源节点",
            node_type="study",
            status="active",
            order_index=1,
        )
        self.client.force_authenticate(user=self.student)

    def test_complete_external_resource_should_accept_string_identifier(self):
        """External resource identifiers should round-trip as stored string values."""
        response = self.client.post(
            f"/api/student/path-nodes/{self.node.id}/resources/ext_{self.node.id}_0/complete",
            {"course_id": self.course.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        progress = NodeProgress.objects.get(node=self.node, user=self.student)
        self.assertIn(f"ext_{self.node.id}_0", progress.completed_resources)

    @patch("platform_ai.rag.student.dependencies.StudentRAGDependenciesMixin._llm_facade")
    def test_ai_resources_should_use_fast_course_resource_recommendation(self, mock_llm_facade):
        """节点 AI 资源接口默认不应触发慢速 LLM 推荐。"""
        mock_llm_facade.side_effect = AssertionError("默认资源接口不应调用 LLM")
        resource = Resource.objects.create(
            course=self.course,
            title="路径资源",
            resource_type="video",
            url="https://edu.qintsg.xyz/path-resource",
            uploaded_by=self.teacher,
        )
        resource.knowledge_points.add(self.point)

        response = self.client.get(f"/api/student/path-nodes/{self.node.id}/ai-resources")

        self.assertEqual(response.status_code, 200)
        payload = response.data["data"]
        self.assertEqual(payload["service_status"], "available")
        self.assertEqual(payload["external_resources"], [])
        self.assertEqual(payload["internal_resources"][0]["resource_id"], resource.id)
        mock_llm_facade.assert_not_called()


class StageTestScoringTests(APITestCase):
    """Verify student-facing stage tests expose stable scoring semantics."""

    def setUp(self):
        """Prepare one study node and one active stage-test node with eight questions."""
        self.student = User.objects.create_user(
            username="stage_student",
            password="Test123456",
            role="student",
        )
        self.teacher = User.objects.create_user(
            username="stage_teacher",
            password="Test123456",
            role="teacher",
        )
        self.course = Course.objects.create(
            name="阶段测试课程",
            created_by=self.teacher,
        )
        self.point = KnowledgePoint.objects.create(
            course=self.course,
            name="阶段测试知识点",
        )
        self.path = LearningPath.objects.create(
            user=self.student,
            course=self.course,
            ai_reason="测试路径",
        )
        self.study_node = PathNode.objects.create(
            path=self.path,
            knowledge_point=self.point,
            title="学习节点",
            node_type="study",
            status="completed",
            order_index=1,
        )
        self.test_node = PathNode.objects.create(
            path=self.path,
            knowledge_point=self.point,
            title="阶段测试节点",
            node_type="test",
            status="active",
            order_index=2,
        )
        self.question_ids = []
        for index in range(8):
            question = Question.objects.create(
                course=self.course,
                content=f"判断题{index + 1}",
                question_type="true_false",
                options=[],
                answer={"answer": True},
                score=1,
                is_visible=True,
                created_by=self.teacher,
            )
            question.knowledge_points.add(self.point)
            self.question_ids.append(question.id)

        self.client.force_authenticate(user=self.student)

    @patch("ai_services.services.llm.service.LLMService.generate_feedback_report")
    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_stage_test_should_return_100_point_scale_and_question_details(
        self, mock_predict_mastery, mock_feedback_report
    ):
        """Stage-test payloads should use percentage scoring and include per-question detail."""
        mock_predict_mastery.return_value = {
            "predictions": {self.point.id: 0.42},
            "confidence": 0.8,
            "model_type": "mefkt",
        }
        mock_feedback_report.return_value = {
            "summary": "阶段测试摘要",
            "analysis": "阶段测试分析",
            "knowledge_gaps": ["阶段测试知识点"],
            "recommendations": ["复习判断题"],
            "next_tasks": ["完成阶段复盘"],
            "conclusion": "继续保持",
        }
        answers = {
            str(question_id): ("true" if index == 0 else "false")
            for index, question_id in enumerate(self.question_ids)
        }
        response = self.client.post(
            f"/api/student/path-nodes/{self.test_node.id}/stage-test/submit",
            {"answers": answers},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.data["data"]
        self.assertEqual(payload["correct_count"], 1)
        self.assertEqual(payload["total_count"], 8)
        self.assertEqual(payload["accuracy"], 12.5)
        self.assertEqual(payload["score"], 12.5)
        self.assertEqual(payload["pass_threshold"], 60.0)
        self.assertEqual(len(payload["question_details"]), 8)
        self.assertEqual(payload["feedback_report"]["summary"], "阶段测试摘要")
        first_wrong = next(
            item for item in payload["question_details"] if not item["is_correct"]
        )
        self.assertIn(first_wrong["correct_answer_display"], {"A. 正确", "正确"})


class LearningPathRefreshTests(APITestCase):
    """Validate how refreshed paths preserve current progress context."""

    def setUp(self):
        """Seed completed, active, and future nodes so refresh behavior is measurable."""
        self.student = User.objects.create_user(
            username="refresh_student",
            password="Test123456",
            role="student",
        )
        self.teacher = User.objects.create_user(
            username="refresh_teacher",
            password="Test123456",
            role="teacher",
        )
        self.course = Course.objects.create(
            name="路径刷新课程",
            created_by=self.teacher,
        )
        self.point_done = KnowledgePoint.objects.create(
            course=self.course, name="已完成知识点", order=1, is_published=True
        )
        self.point_active = KnowledgePoint.objects.create(
            course=self.course, name="当前知识点", order=2, is_published=True
        )
        self.point_future = KnowledgePoint.objects.create(
            course=self.course, name="未来知识点", order=3, is_published=True
        )
        self.path = LearningPath.objects.create(
            user=self.student,
            course=self.course,
            ai_reason="原始路径",
        )
        self.done_node = PathNode.objects.create(
            path=self.path,
            knowledge_point=self.point_done,
            title="已完成节点",
            node_type="study",
            status="completed",
            order_index=0,
        )
        self.active_node = PathNode.objects.create(
            path=self.path,
            knowledge_point=self.point_active,
            title="当前节点",
            node_type="study",
            status="active",
            order_index=1,
        )
        self.locked_node = PathNode.objects.create(
            path=self.path,
            knowledge_point=self.point_future,
            title="旧未来节点",
            node_type="study",
            status="locked",
            order_index=2,
        )
        KnowledgeMastery.objects.create(
            user=self.student,
            course=self.course,
            knowledge_point=self.point_done,
            mastery_rate=0.9,
        )
        KnowledgeMastery.objects.create(
            user=self.student,
            course=self.course,
            knowledge_point=self.point_active,
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
        self.client.force_authenticate(user=self.student)

    @patch("ai_services.services.llm.service.LLMService.plan_learning_path")
    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_refresh_learning_path_should_preserve_current_context(
        self, mock_predict_mastery, mock_plan_learning_path
    ):
        """Refreshing a path should keep the active node while replacing stale future nodes."""
        mock_predict_mastery.return_value = {
            "predictions": {},
            "confidence": 0.0,
            "model_type": "default",
            "answer_count": 0,
        }
        mock_plan_learning_path.return_value = {
            "reason": "已保留当前节点并重建未来路径",
            "nodes": [{"title": self.point_future.name}],
        }

        response = self.client.post(
            "/api/student/ai/refresh-learning-path",
            {"course_id": self.course.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.data["data"]
        self.assertEqual(payload["change_summary"]["preserved_context"], 2)
        self.assertEqual(payload["change_summary"]["removed_count"], 1)
        self.assertTrue(any(node["title"] == "当前节点" for node in payload["nodes"]))

    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_refresh_learning_path_should_reinsert_low_mastery_completed_point(
        self, mock_predict_mastery
    ):
        """Low-mastery completed points should be reinserted as remedial work."""
        self.point_future.is_published = False
        self.point_future.save(update_fields=["is_published"])
        KnowledgeMastery.objects.filter(
            user=self.student,
            course=self.course,
            knowledge_point=self.point_done,
        ).update(mastery_rate=0.45)
        mock_predict_mastery.return_value = {
            "predictions": {
                self.point_done.id: 0.45,
                self.point_active.id: 0.72,
            },
            "confidence": 0.8,
            "model_type": "mefkt",
            "answer_count": 3,
        }

        response = self.client.post(
            "/api/student/ai/refresh-learning-path",
            {"course_id": self.course.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.data["data"]
        remedial_nodes = [
            node
            for node in payload["nodes"]
            if node["knowledge_point_id"] == self.point_done.id
            and node.get("is_inserted")
        ]
        self.assertTrue(remedial_nodes)
        self.assertIn("补强", remedial_nodes[0]["title"])

    @patch("ai_services.services.path.generation_nodes.AppConfig.max_path_nodes", return_value=2)
    @patch("ai_services.services.kt.service.kt_service.predict_mastery")
    def test_refresh_learning_path_should_reinsert_remedial_point_when_node_cap_reached(
        self,
        mock_predict_mastery,
        _mock_max_path_nodes,
    ):
        """节点数达到上限时仍应优先保留低掌握完成点的补强机会。"""
        self.point_future.is_published = False
        self.point_future.save(update_fields=["is_published"])
        KnowledgeMastery.objects.filter(
            user=self.student,
            course=self.course,
            knowledge_point=self.point_done,
        ).update(mastery_rate=0.45)
        mock_predict_mastery.return_value = {
            "predictions": {
                self.point_done.id: 0.45,
                self.point_active.id: 0.72,
            },
            "confidence": 0.8,
            "model_type": "mefkt",
            "answer_count": 3,
        }

        response = self.client.post(
            "/api/student/ai/refresh-learning-path",
            {"course_id": self.course.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.data["data"]
        remedial_nodes = [
            node
            for node in payload["nodes"]
            if node["knowledge_point_id"] == self.point_done.id
            and node.get("is_inserted")
        ]
        self.assertTrue(remedial_nodes)
        self.assertIn("补强", remedial_nodes[0]["title"])
