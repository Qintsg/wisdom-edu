"""Regression tests for learning-path APIs and stage-test scoring."""

from unittest.mock import patch

from rest_framework.test import APITestCase

from assessments.models import Question
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint, ProfileSummary
from learning.models import LearningPath, NodeProgress, PathNode
from users.models import User


# 维护意图：Exercise resource-completion routes exposed on learning path nodes
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class LearningResourceRouteTests(APITestCase):
    """Exercise resource-completion routes exposed on learning path nodes."""

    # 维护意图：Create a study node whose external resources are addressed by string IDs
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    # 维护意图：External resource identifiers should round-trip as stored string values
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
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


# 维护意图：Verify student-facing stage tests expose stable scoring semantics
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class StageTestScoringTests(APITestCase):
    """Verify student-facing stage tests expose stable scoring semantics."""

    # 维护意图：Prepare one study node and one active stage-test node with eight questions
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    # 维护意图：Stage-test payloads should use percentage scoring and include per-question detail
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    @patch("ai_services.services.llm_service.generate_feedback_report")
    @patch("ai_services.services.kt_service.kt_service.predict_mastery")
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


# 维护意图：Validate how refreshed paths preserve current progress context
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class LearningPathRefreshTests(APITestCase):
    """Validate how refreshed paths preserve current progress context."""

    # 维护意图：Seed completed, active, and future nodes so refresh behavior is measurable
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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
            course=self.course, name="已完成知识点", order=1
        )
        self.point_active = KnowledgePoint.objects.create(
            course=self.course, name="当前知识点", order=2
        )
        self.point_future = KnowledgePoint.objects.create(
            course=self.course, name="未来知识点", order=3
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

    # 维护意图：Refreshing a path should keep the active node while replacing stale future nodes
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    @patch("ai_services.services.llm_service.LLMService.plan_learning_path")
    @patch("ai_services.services.kt_service.kt_service.predict_mastery")
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
        self.assertEqual(payload["change_summary"]["preserved_context"], 1)
        self.assertEqual(payload["change_summary"]["removed_count"], 1)
        self.assertTrue(any(node["title"] == "当前节点" for node in payload["nodes"]))

    # 维护意图：Low-mastery completed points should be reinserted as remedial work
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    @patch("ai_services.services.kt_service.kt_service.predict_mastery")
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
