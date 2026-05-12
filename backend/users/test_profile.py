"""学习习惯偏好与画像缓存测试。"""

from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from assessments.models import AnswerHistory, Question
from courses.models import Course
from knowledge.models import KnowledgeMastery, KnowledgePoint, ProfileSummary
from .models import HabitPreference, User
from .services import LearnerProfileService


class HabitPreferenceTests(APITestCase):
    """学习习惯偏好测试。"""

    def setUp(self):
        """创建测试用户。"""
        self.user = User.objects.create_user(
            username='student',
            password='TestPassword123',
            role='student'
        )

    def test_update_habit_preference(self):
        """测试更新学习偏好。"""
        self.client.force_authenticate(user=self.user)

        response = self.client.put('/api/student/profile/habit', {
            'preferred_resource': 'video',
            'preferred_study_time': 'evening'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        pref = HabitPreference.objects.get(user=self.user)
        self.assertEqual(pref.preferred_resource, 'video')
        self.assertEqual(pref.preferred_study_time, 'evening')

    def test_get_profile(self):
        """测试获取画像。"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/student/profile')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('knowledge_mastery', response.data['data'])
        self.assertIn('ability_scores', response.data['data'])
        self.assertIn('habit_preferences', response.data['data'])

    def test_legacy_profile_routes_should_not_be_exposed(self):
        """旧画像 API 路径不应继续暴露，避免测试和前端回退到历史入口。"""
        self.client.force_authenticate(user=self.user)

        profile_response = self.client.get('/api/profile')
        habit_response = self.client.put('/api/profile/habit', {
            'preferred_resource': 'video',
            'preferred_study_time': 'evening',
        })

        self.assertEqual(profile_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(habit_response.status_code, status.HTTP_404_NOT_FOUND)


class LearnerProfileServiceCacheTests(TestCase):
    """学习者画像服务缓存回归测试。"""

    def setUp(self):
        """创建带缓存画像的最小课程上下文。"""
        self.teacher = User.objects.create_user(
            username='profile_teacher',
            password='TestPassword123',
            role='teacher'
        )
        self.student = User.objects.create_user(
            username='profile_student',
            password='TestPassword123',
            role='student'
        )
        self.course = Course.objects.create(
            name='画像缓存测试课程',
            created_by=self.teacher
        )
        self.point = KnowledgePoint.objects.create(
            course=self.course,
            name='Hadoop 基础',
            description='用于验证缓存画像的测试知识点。',
            is_published=True,
        )
        self.inferred_point = KnowledgePoint.objects.create(
            course=self.course,
            name='MapReduce 推断点',
            description='用于验证 MEFKT 未测推断。',
            is_published=True,
        )
        KnowledgeMastery.objects.create(
            user=self.student,
            course=self.course,
            knowledge_point=self.point,
            mastery_rate=0.25,
        )
        ProfileSummary.objects.create(
            user=self.student,
            course=self.course,
            summary='缓存画像摘要',
            weakness='Hadoop 基础',
            suggestion='建议先完成路径首节点学习。',
        )
        self.service = LearnerProfileService(self.student)

    @patch('ai_services.services.kt_service')
    @patch('ai_services.services.llm_service')
    def test_generate_profile_for_course_should_reuse_cached_summary(
        self,
        mock_llm_service,
        mock_kt_service,
    ):
        """未强刷时应直接返回已有画像摘要，避免高成本重算。"""
        mock_kt_service.predict_mastery.side_effect = AssertionError(
            '命中缓存时不应重新触发 KT 预测'
        )
        mock_llm_service.analyze_profile.side_effect = AssertionError(
            '命中缓存时不应重新触发 LLM 画像分析'
        )

        result = self.service.generate_profile_for_course(self.course.id)

        self.assertTrue(result['success'])
        self.assertTrue(result['cached'])
        self.assertEqual(result['summary'], '缓存画像摘要')
        self.assertEqual(result['weakness'], 'Hadoop 基础')
        self.assertEqual(result['suggestion'], '建议先完成路径首节点学习。')
        self.assertEqual(result['strength'], ['Hadoop 基础'])

    @patch('ai_services.services.llm_service')
    @patch('ai_services.services.kt_service')
    def test_generate_profile_for_course_should_keep_mefkt_inferred_points(
        self,
        mock_kt_service,
        mock_llm_service,
    ):
        """强制刷新画像时允许真实 MEFKT 写回未测知识点推断。"""
        question = Question.objects.create(
            course=self.course,
            content='画像刷新证据题',
            question_type='single_choice',
            options=[{'value': 'A', 'label': 'A'}],
            answer={'answer': 'A'},
            score=1,
            is_visible=True,
            created_by=self.teacher,
        )
        question.knowledge_points.add(self.point)
        AnswerHistory.objects.create(
            user=self.student,
            course=self.course,
            question=question,
            knowledge_point=self.point,
            student_answer={'answer': 'A'},
            correct_answer={'answer': 'A'},
            is_correct=True,
            score=1,
            source='initial',
        )
        mock_kt_service.predict_mastery.return_value = {
            'predictions': {
                self.point.id: 0.82,
                self.inferred_point.id: 0.73,
            },
            'model_type': 'mefkt_question_online',
            'confidence': 0.8,
        }
        mock_llm_service.analyze_profile.return_value = {
            'summary': '画像摘要',
            'weakness': [],
            'suggestion': '继续学习',
            'strength': ['Hadoop 基础'],
        }

        result = self.service.generate_profile_for_course(self.course.id, force_refresh=True)

        self.assertTrue(result['success'])
        inferred_mastery = KnowledgeMastery.objects.get(
            user=self.student,
            course=self.course,
            knowledge_point=self.inferred_point,
        )
        self.assertAlmostEqual(float(inferred_mastery.mastery_rate), 0.73, places=3)

    @patch('ai_services.services.llm_service')
    @patch('ai_services.services.kt_service')
    def test_generate_profile_for_course_should_ignore_builtin_unmeasured_points(
        self,
        mock_kt_service,
        mock_llm_service,
    ):
        """画像刷新中的统计回退不能污染未测知识点。"""
        question = Question.objects.create(
            course=self.course,
            content='画像刷新回退题',
            question_type='single_choice',
            options=[{'value': 'A', 'label': 'A'}],
            answer={'answer': 'A'},
            score=1,
            is_visible=True,
            created_by=self.teacher,
        )
        question.knowledge_points.add(self.point)
        AnswerHistory.objects.create(
            user=self.student,
            course=self.course,
            question=question,
            knowledge_point=self.point,
            student_answer={'answer': 'A'},
            correct_answer={'answer': 'A'},
            is_correct=True,
            score=1,
            source='initial',
        )
        KnowledgeMastery.objects.filter(
            user=self.student,
            course=self.course,
            knowledge_point=self.inferred_point,
        ).delete()
        mock_kt_service.predict_mastery.return_value = {
            'predictions': {
                self.point.id: 0.82,
                self.inferred_point.id: 0.4,
            },
            'model_type': 'builtin',
            'confidence': 0.3,
        }
        mock_llm_service.analyze_profile.return_value = {
            'summary': '画像摘要',
            'weakness': [],
            'suggestion': '继续学习',
            'strength': ['Hadoop 基础'],
        }

        result = self.service.generate_profile_for_course(self.course.id, force_refresh=True)

        self.assertTrue(result['success'])
        self.assertFalse(
            KnowledgeMastery.objects.filter(
                user=self.student,
                course=self.course,
                knowledge_point=self.inferred_point,
            ).exists()
        )
