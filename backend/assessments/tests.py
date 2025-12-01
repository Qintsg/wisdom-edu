"""Assessment API regression tests for scoring and mastery updates."""

from rest_framework.test import APITestCase

from unittest.mock import patch

from assessments.models import Assessment, AssessmentQuestion, AbilityScore, Question
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint, KnowledgeRelation
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
            'model_type': 'dkt_real',
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
