"""Assessment API regression tests for scoring and mastery updates."""

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from rest_framework.test import APITestCase

from assessments.assessment_helpers import calculate_initial_mastery_baseline
from assessments.models import (
    Assessment,
    AssessmentQuestion,
    AbilityScore,
    Question,
    SurveyQuestion,
)
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint, KnowledgeRelation
from tools.db_seed_support import _seed_survey_questions
from users.models import User


class AbilityAssessmentScoringTests(APITestCase):
    """Verify ability assessments only persist evidence-backed dimensions."""

    def setUp(self):
        """Create a minimal single-question ability assessment."""
        self.student = User.objects.create_user(
            username='ability_student',
            password='Test123456',
            role='student',
        )
        self.teacher = User.objects.create_user(
            username='ability_teacher',
            password='Test123456',
            role='teacher',
        )
        self.course = Course.objects.create(
            name='能力评测课程',
            created_by=self.teacher,
        )
        self.assessment = Assessment.objects.create(
            course=self.course,
            title='课程能力评测',
            assessment_type='ability',
            is_active=True,
        )
        self.question = Question.objects.create(
            course=self.course,
            content='能力题目',
            question_type='single_choice',
            options=[
                {'value': 'A', 'label': '正确'},
                {'value': 'B', 'label': '错误'},
            ],
            answer={'answer': 'A'},
            score=5,
            is_visible=True,
            created_by=self.teacher,
        )
        AssessmentQuestion.objects.create(
            assessment=self.assessment,
            question=self.question,
            order=0,
        )
        self.client.force_authenticate(user=self.student)

    def test_submit_ability_assessment_should_not_fabricate_dimension_scores(self):
        """Submissions without dimension evidence should keep analysis dictionaries empty."""
        response = self.client.post(
            '/api/student/assessments/initial/ability/submit',
            {
                'course_id': self.course.id,
                'answers': [{'question_id': self.question.id, 'answer': 'A'}],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['ability_analysis'], {})

        ability_score = AbilityScore.objects.get(user=self.student, course=self.course)
        self.assertEqual(ability_score.scores, {})


class SurveyQuestionSeedTests(APITestCase):
    """验证基础测试数据会补齐内置能力与习惯问卷题。"""

    def test_seed_survey_questions_should_use_builtin_defaults_when_config_empty(self):
        """空 survey_questions 配置也应生成默认问卷题。"""
        _seed_survey_questions({"survey_questions": {"habit": [], "ability": []}}, [])

        self.assertGreater(SurveyQuestion.objects.filter(survey_type="habit").count(), 0)
        self.assertGreater(SurveyQuestion.objects.filter(survey_type="ability").count(), 0)
        self.assertFalse(SurveyQuestion.objects.filter(survey_type="ability", is_global=False).exists())


class KnowledgeAssessmentMasteryTests(APITestCase):
    """Check prerequisite-aware mastery updates for knowledge assessments."""

    def setUp(self):
        """Build a prerequisite pair so conservative mastery rules are observable."""
        self.student = User.objects.create_user(
            username='knowledge_student',
            password='Test123456',
            role='student',
        )
        self.teacher = User.objects.create_user(
            username='knowledge_teacher',
            password='Test123456',
            role='teacher',
        )
        self.course = Course.objects.create(
            name='知识测评课程',
            created_by=self.teacher,
        )
        self.assessment = Assessment.objects.create(
            course=self.course,
            title='知识测评',
            assessment_type='knowledge',
            is_active=True,
        )
        self.pre_point = KnowledgePoint.objects.create(course=self.course, name='前置知识点', order=1)
        self.post_point = KnowledgePoint.objects.create(course=self.course, name='后置知识点', order=2)
        self.inferred_point = KnowledgePoint.objects.create(
            course=self.course,
            name='MEFKT未测推断点',
            order=3,
            is_published=True,
        )
        KnowledgeRelation.objects.create(
            course=self.course,
            pre_point=self.pre_point,
            post_point=self.post_point,
            relation_type='prerequisite',
        )
        self.pre_question = Question.objects.create(
            course=self.course,
            content='前置题目',
            question_type='single_choice',
            options=[{'value': 'A', 'label': 'A'}, {'value': 'B', 'label': 'B'}],
            answer={'answer': 'A'},
            score=2,
            is_visible=True,
            created_by=self.teacher,
        )
        self.pre_question.knowledge_points.add(self.pre_point)
        self.post_question = Question.objects.create(
            course=self.course,
            content='后置题目',
            question_type='single_choice',
            options=[{'value': 'A', 'label': 'A'}, {'value': 'B', 'label': 'B'}],
            answer={'answer': 'A'},
            score=2,
            is_visible=True,
            created_by=self.teacher,
        )
        self.post_question.knowledge_points.add(self.post_point)
        AssessmentQuestion.objects.create(assessment=self.assessment, question=self.pre_question, order=0)
        AssessmentQuestion.objects.create(assessment=self.assessment, question=self.post_question, order=1)
        self.client.force_authenticate(user=self.student)

    @patch('ai_services.services.kt_service.kt_service.predict_mastery')
    def test_knowledge_assessment_should_keep_mastery_conservative_and_respect_prerequisite(self, mock_predict_mastery):
        """A stronger downstream prediction should still be capped by prerequisite weakness."""
        mock_predict_mastery.return_value = {
            'predictions': {
                self.pre_point.id: 0.82,
                self.post_point.id: 0.91,
            },
            'confidence': 0.8,
            'model_type': 'mefkt_real',
            'answer_count': 2,
        }

        response = self.client.post(
            '/api/student/assessments/initial/knowledge/submit',
            {
                'course_id': self.course.id,
                'answers': [
                    {'question_id': self.pre_question.id, 'answer': 'B'},
                    {'question_id': self.post_question.id, 'answer': 'A'},
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        pre_mastery = float(KnowledgeMastery.objects.get(user=self.student, course=self.course, knowledge_point=self.pre_point).mastery_rate)
        post_mastery = float(KnowledgeMastery.objects.get(user=self.student, course=self.course, knowledge_point=self.post_point).mastery_rate)
        self.assertLess(pre_mastery, 0.6)
        self.assertLessEqual(post_mastery, pre_mastery)

    @patch('assessments.knowledge_views.threading.Thread')
    @patch('ai_services.services.kt_service.kt_service.predict_mastery')
    def test_knowledge_assessment_should_persist_mefkt_unmeasured_inference(
        self,
        mock_predict_mastery,
        _mock_thread,
    ):
        """初测提交本身应保留真实 MEFKT 对未测知识点的推断。"""
        mock_predict_mastery.return_value = {
            'predictions': {
                self.pre_point.id: 0.58,
                self.inferred_point.id: 0.71,
            },
            'confidence': 0.8,
            'model_type': 'mefkt_question_online',
            'answer_count': 1,
        }

        response = self.client.post(
            '/api/student/assessments/initial/knowledge/submit',
            {
                'course_id': self.course.id,
                'answers': [
                    {'question_id': self.pre_question.id, 'answer': 'A'},
                    {'question_id': self.post_question.id, 'answer': 'A'},
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        mock_predict_mastery.assert_called_once()
        called_kwargs = mock_predict_mastery.call_args.kwargs
        self.assertIn(self.inferred_point.id, called_kwargs['knowledge_points'])
        inferred_mastery = KnowledgeMastery.objects.get(
            user=self.student,
            course=self.course,
            knowledge_point=self.inferred_point,
        )
        self.assertAlmostEqual(float(inferred_mastery.mastery_rate), 0.71, places=3)
        self.assertTrue(
            any(
                item['point_id'] == self.inferred_point.id
                and item['point_name'] == self.inferred_point.name
                for item in response.data['data']['mastery']
            )
        )

    @patch('assessments.knowledge_views.threading.Thread')
    @patch('ai_services.services.kt_service.kt_service.predict_mastery')
    def test_knowledge_assessment_should_spread_small_sample_mastery(self, mock_predict_mastery, _mock_thread):
        """初测小样本掌握度应避开旧 25/30/50 尖峰。"""
        mock_predict_mastery.return_value = {
            'predictions': {},
            'confidence': 0.0,
            'model_type': 'builtin',
            'answer_count': 2,
        }

        response = self.client.post(
            '/api/student/assessments/initial/knowledge/submit',
            {
                'course_id': self.course.id,
                'answers': [
                    {'question_id': self.pre_question.id, 'answer': 'B'},
                    {'question_id': self.post_question.id, 'answer': 'A'},
                ],
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        pre_mastery = float(KnowledgeMastery.objects.get(user=self.student, course=self.course, knowledge_point=self.pre_point).mastery_rate)
        post_mastery = float(KnowledgeMastery.objects.get(user=self.student, course=self.course, knowledge_point=self.post_point).mastery_rate)
        self.assertAlmostEqual(pre_mastery, calculate_initial_mastery_baseline(0, 1), places=3)
        self.assertLessEqual(post_mastery, pre_mastery)
        self.assertNotIn(round(pre_mastery, 2), {0.25, 0.30, 0.50})


class RepairInitialMasteryCommandTests(APITestCase):
    """验证现有初测掌握度修复命令。"""

    def setUp(self):
        """创建旧尖峰掌握度和可 MEFKT 推断的未测知识点。"""
        self.teacher = User.objects.create_user(username='repair_teacher', password='Test123456', role='teacher')
        self.student = User.objects.create_user(username='repair_student', password='Test123456', role='student')
        self.course = Course.objects.create(name='掌握度修复课程', created_by=self.teacher)
        self.measured_point = KnowledgePoint.objects.create(course=self.course, name='已测知识点', order=1, is_published=True)
        self.inferred_point = KnowledgePoint.objects.create(course=self.course, name='未测知识点', order=2, is_published=True)
        self.question = Question.objects.create(
            course=self.course,
            content='已测题目',
            question_type='single_choice',
            options=[{'value': 'A', 'label': 'A'}, {'value': 'B', 'label': 'B'}],
            answer={'answer': 'A'},
            score=2,
            is_visible=True,
            created_by=self.teacher,
        )
        self.question.knowledge_points.add(self.measured_point)
        from assessments.models import AnswerHistory

        AnswerHistory.objects.create(
            user=self.student,
            course=self.course,
            question=self.question,
            knowledge_point=self.measured_point,
            student_answer={'answer': 'A'},
            correct_answer={'answer': 'A'},
            is_correct=True,
            score=2,
            source='initial',
        )
        KnowledgeMastery.objects.create(
            user=self.student,
            course=self.course,
            knowledge_point=self.measured_point,
            mastery_rate=0.25,
        )
        KnowledgeMastery.objects.create(
            user=self.student,
            course=self.course,
            knowledge_point=self.inferred_point,
            mastery_rate=0.25,
        )

    @patch('ai_services.services.kt_service.kt_service.predict_mastery')
    def test_repair_initial_mastery_should_apply_mefkt_inferred_points(self, mock_predict_mastery):
        """修复命令应允许真实 MEFKT 推断未测知识点。"""
        mock_predict_mastery.return_value = {
            'predictions': {
                self.measured_point.id: 0.8,
                self.inferred_point.id: 0.72,
            },
            'model_type': 'mefkt_question_online',
            'confidence': 0.8,
        }
        output = StringIO()

        call_command(
            'repair_initial_mastery',
            '--apply',
            user_id=self.student.id,
            course_id=self.course.id,
            stdout=output,
        )

        measured_rate = float(KnowledgeMastery.objects.get(user=self.student, knowledge_point=self.measured_point).mastery_rate)
        inferred_rate = float(KnowledgeMastery.objects.get(user=self.student, knowledge_point=self.inferred_point).mastery_rate)
        self.assertGreater(measured_rate, 0.25)
        self.assertAlmostEqual(inferred_rate, 0.72, places=3)
        self.assertIn('已写回', output.getvalue())

    @patch('ai_services.services.kt_service.kt_service.predict_mastery')
    def test_repair_initial_mastery_should_ignore_fallback_unmeasured_points(self, mock_predict_mastery):
        """修复命令不应让统计回退覆盖未测知识点。"""
        mock_predict_mastery.return_value = {
            'predictions': {
                self.measured_point.id: 0.4,
                self.inferred_point.id: 0.4,
            },
            'model_type': 'builtin',
            'confidence': 0.3,
        }

        call_command(
            'repair_initial_mastery',
            '--apply',
            user_id=self.student.id,
            course_id=self.course.id,
            stdout=StringIO(),
        )

        inferred_rate = float(KnowledgeMastery.objects.get(user=self.student, knowledge_point=self.inferred_point).mastery_rate)
        self.assertEqual(inferred_rate, 0.25)
