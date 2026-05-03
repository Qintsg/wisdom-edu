"""Regression tests for deterministic defense-demo data seeding."""

from django.test import TestCase

from assessments.models import AnswerHistory, AssessmentResult, AssessmentStatus, AbilityScore
from common.defense_demo import (
	DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS,
	DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME,
	DEFENSE_DEMO_TEACHER_USERNAME,
	DEFENSE_DEMO_WARMUP_STUDENT_USERNAME,
	ensure_defense_demo_accounts,
	ensure_defense_demo_environment,
)
from courses.models import Course
from exams.models import ExamSubmission, FeedbackReport
from knowledge.models import KnowledgeMastery, ProfileSummary
from learning.models import LearningPath, NodeProgress, PathNode
from users.models import HabitPreference, User, UserCourseContext


# 维护意图：Guard the completeness and idempotency of defense-demo preset data
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class DefenseDemoPresetTests(TestCase):
	"""Guard the completeness and idempotency of defense-demo preset data."""

	# 维护意图：Create the primary course and seed the deterministic defense-demo environment
	# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
	# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
	def setUp(self):
		"""Create the primary course and seed the deterministic defense-demo environment."""
		ensure_defense_demo_accounts()
		self.teacher = User.objects.get(username=DEFENSE_DEMO_TEACHER_USERNAME)
		self.course = Course.objects.create(
			name="大数据技术与应用",
			created_by=self.teacher,
			is_public=True,
		)
		self.summary = ensure_defense_demo_environment(self.course.name)
		self.warmup_student = User.objects.get(username=DEFENSE_DEMO_WARMUP_STUDENT_USERNAME)
		self.primary_student = User.objects.get(username=DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME)

	# 维护意图：The warmup account should expose assessment, profile, path and completed stage-test artifacts
	# 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
	# 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
	def test_warmup_student_should_receive_full_preset_journey(self):
		"""The warmup account should expose assessment, profile, path and completed stage-test artifacts."""
		assessment_status = AssessmentStatus.objects.get(
			user=self.warmup_student,
			course=self.course,
		)
		learning_path = LearningPath.objects.get(user=self.warmup_student, course=self.course)
		stage_node = PathNode.objects.get(path=learning_path, node_type="test")
		stage_progress = NodeProgress.objects.get(node=stage_node, user=self.warmup_student)
		context = UserCourseContext.objects.get(user=self.warmup_student)

		self.assertTrue(assessment_status.is_all_done)
		self.assertEqual(AbilityScore.objects.filter(user=self.warmup_student, course=self.course).count(), 1)
		self.assertEqual(ProfileSummary.objects.filter(user=self.warmup_student, course=self.course).count(), 1)
		self.assertEqual(KnowledgeMastery.objects.filter(user=self.warmup_student, course=self.course).count(), 3)
		self.assertEqual(AssessmentResult.objects.filter(user=self.warmup_student, course=self.course).count(), 1)
		self.assertEqual(FeedbackReport.objects.filter(user=self.warmup_student, source="assessment").count(), 1)
		self.assertEqual(
			FeedbackReport.objects.filter(
				user=self.warmup_student,
				source="exam",
				exam_id=self.summary["stage_exam_id"],
			).count(),
			1,
		)
		self.assertEqual(ExamSubmission.objects.filter(user=self.warmup_student, exam_id=self.summary["stage_exam_id"]).count(), 1)
		self.assertEqual(learning_path.nodes.count(), 6)
		self.assertEqual(stage_node.status, "completed")
		self.assertIn(self.summary["stage_exam_id"], stage_progress.completed_exams)
		self.assertTrue(stage_progress.extra_data["stage_test_result"]["passed"])
		self.assertEqual(len(stage_progress.extra_data["stage_test_result"]["question_details"]), 3)
		self.assertEqual(context.current_course_id, self.course.id)

	# 维护意图：Running the preset seeding repeatedly should stay idempotent for demo accounts
	# 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
	# 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
	def test_reseeding_should_not_duplicate_demo_histories_or_paths(self):
		"""Running the preset seeding repeatedly should stay idempotent for demo accounts."""
		ensure_defense_demo_environment(self.course.name)

		warmup_path = LearningPath.objects.get(user=self.warmup_student, course=self.course)
		primary_path = LearningPath.objects.get(user=self.primary_student, course=self.course)

		self.assertEqual(LearningPath.objects.filter(user=self.warmup_student, course=self.course).count(), 1)
		self.assertEqual(LearningPath.objects.filter(user=self.primary_student, course=self.course).count(), 1)
		self.assertEqual(NodeProgress.objects.filter(user=self.warmup_student, node__path=warmup_path).count(), 6)
		self.assertEqual(NodeProgress.objects.filter(user=self.primary_student, node__path=primary_path).count(), 6)
		self.assertEqual(
			AnswerHistory.objects.filter(user=self.warmup_student, course=self.course, source="initial").count(),
			6,
		)
		self.assertEqual(
			AnswerHistory.objects.filter(user=self.warmup_student, course=self.course, source="practice").count(),
			2,
		)
		self.assertEqual(
			AnswerHistory.objects.filter(
				user=self.warmup_student,
				course=self.course,
				source="exam",
				exam_id=self.summary["stage_exam_id"],
			).count(),
			3,
		)
		self.assertEqual(
			AnswerHistory.objects.filter(user=self.primary_student, course=self.course, source="initial").count(),
			6,
		)
		self.assertEqual(
			AnswerHistory.objects.filter(user=self.primary_student, course=self.course, source="practice").count(),
			4,
		)
		self.assertEqual(
			AnswerHistory.objects.filter(
				user=self.primary_student,
				course=self.course,
				source="exam",
				exam_id=self.summary["stage_exam_id"],
			).count(),
			3,
		)

	# 维护意图：Primary defense-demo course config should expose ready-to-run AI assistant prompts
	# 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
	# 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
	def test_primary_course_should_include_ai_demo_queries(self):
		"""Primary defense-demo course config should expose ready-to-run AI assistant prompts."""
		defense_demo_config = self.course.config.get("defense_demo", {})
		assistant_demo_queries = defense_demo_config.get("assistant_demo_queries", [])

		self.assertGreaterEqual(len(assistant_demo_queries), 3)
		self.assertTrue(any(item.get("point_id") for item in assistant_demo_queries if isinstance(item, dict)))
		self.assertTrue(
			any(
				"graph_tools" in item.get("expected_modes", [])
				for item in assistant_demo_queries
				if isinstance(item, dict)
			)
		)

	# 维护意图：student2~5 should be in the demo class but keep a pristine first-entry state
	# 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
	# 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
	def test_course_only_students_should_stay_enrolled_without_primary_course_traces(self):
		"""student2~5 should be in the demo class but keep a pristine first-entry state."""
		for student_spec in DEFENSE_DEMO_COURSE_ONLY_STUDENT_SPECS:
			student = User.objects.get(username=student_spec["username"])
			context = UserCourseContext.objects.get(user=student)

			self.assertTrue(student.enrollments.filter(class_obj_id=self.summary["class_id"]).exists())
			self.assertEqual(context.current_course_id, self.course.id)
			self.assertEqual(context.current_class_id, self.summary["class_id"])
			self.assertFalse(HabitPreference.objects.filter(user=student).exists())
			self.assertFalse(AssessmentStatus.objects.filter(user=student, course=self.course).exists())
			self.assertFalse(AssessmentResult.objects.filter(user=student, course=self.course).exists())
			self.assertFalse(AbilityScore.objects.filter(user=student, course=self.course).exists())
			self.assertFalse(ProfileSummary.objects.filter(user=student, course=self.course).exists())
			self.assertFalse(KnowledgeMastery.objects.filter(user=student, course=self.course).exists())
			self.assertFalse(LearningPath.objects.filter(user=student, course=self.course).exists())
			self.assertFalse(AnswerHistory.objects.filter(user=student, course=self.course).exists())
			self.assertFalse(ExamSubmission.objects.filter(user=student, exam__course=self.course).exists())
			self.assertFalse(FeedbackReport.objects.filter(user=student, exam__course=self.course).exists())
			self.assertFalse(
				FeedbackReport.objects.filter(
					user=student,
					assessment_result__course=self.course,
				).exists()
			)
