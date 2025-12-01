"""
用户模块 - 测试用例

测试用户认证、注册、激活码、班级邀请码等功能
"""
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User, ActivationCode, ClassInvitation, HabitPreference
from courses.models import Course, Class, Enrollment
from knowledge.models import KnowledgeMastery, KnowledgePoint, ProfileSummary
from .services import LearnerProfileService


class UserModelTests(TestCase):
    """用户模型测试"""

    def test_create_student(self):
        """测试创建学生用户"""
        user = User.objects.create_user(
            username='test_student',
            password='TestPassword123',
            email='student@test.com',
            role='student'
        )
        self.assertEqual(user.role, 'student')
        self.assertTrue(user.is_student)
        self.assertFalse(user.is_teacher)
        self.assertFalse(user.is_admin)

    def test_create_teacher(self):
        """测试创建教师用户"""
        user = User.objects.create_user(
            username='test_teacher',
            password='TestPassword123',
            email='teacher@test.com',
            role='teacher'
        )
        self.assertEqual(user.role, 'teacher')
        self.assertTrue(user.is_teacher)
        self.assertFalse(user.is_student)

    def test_create_admin(self):
        """测试创建管理员用户"""
        user = User.objects.create_superuser(
            username='test_admin',
            password='AdminPassword123',
            email='admin@test.com',
            role='admin'
        )
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_admin)


class ActivationCodeModelTests(TestCase):
    """激活码模型测试"""

    def setUp(self):
        """创建测试用户"""
        self.admin = User.objects.create_superuser(
            username='admin',
            password='AdminPassword123',
            email='admin@test.com',
            role='admin'
        )

    def test_generate_code(self):
        """测试生成激活码"""
        code = ActivationCode.generate_code()
        self.assertEqual(len(code), 8)
        self.assertTrue(code.isupper())

    def test_create_activation_code(self):
        """测试创建激活码"""
        code = ActivationCode.objects.create(
            code=ActivationCode.generate_code(),
            code_type='teacher',
            created_by=self.admin
        )
        self.assertFalse(code.is_used)
        self.assertTrue(code.is_valid())

    def test_use_activation_code(self):
        """测试使用激活码"""
        code = ActivationCode.objects.create(
            code=ActivationCode.generate_code(),
            code_type='teacher',
            created_by=self.admin
        )
        teacher = User.objects.create_user(
            username='new_teacher',
            password='TestPassword123',
            role='teacher'
        )
        result = code.use(teacher)
        self.assertTrue(result)
        self.assertTrue(code.is_used)
        self.assertEqual(code.used_by, teacher)
        self.assertIsNotNone(code.used_at)

    def test_cannot_reuse_activation_code(self):
        """测试激活码不能重复使用"""
        code = ActivationCode.objects.create(
            code=ActivationCode.generate_code(),
            code_type='teacher',
            created_by=self.admin,
            is_used=True
        )
        self.assertFalse(code.is_valid())


class ClassInvitationModelTests(TestCase):
    """班级邀请码模型测试"""

    def setUp(self):
        """创建测试数据"""
        self.teacher = User.objects.create_user(
            username='teacher',
            password='TestPassword123',
            role='teacher'
        )
        self.course = Course.objects.create(
            name='测试课程',
            created_by=self.teacher
        )
        self.class_obj = Class.objects.create(
            course=self.course,
            name='测试班级',
            teacher=self.teacher
        )

    def test_generate_code(self):
        """测试生成邀请码"""
        code = ClassInvitation.generate_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isupper())

    def test_create_invitation(self):
        """测试创建邀请码"""
        invitation = ClassInvitation.objects.create(
            code=ClassInvitation.generate_code(),
            class_obj=self.class_obj,
            created_by=self.teacher
        )
        self.assertTrue(invitation.is_valid())
        self.assertEqual(invitation.use_count, 0)

    def test_use_invitation(self):
        """测试使用邀请码"""
        invitation = ClassInvitation.objects.create(
            code=ClassInvitation.generate_code(),
            class_obj=self.class_obj,
            created_by=self.teacher
        )
        invitation.use()
        self.assertEqual(invitation.use_count, 1)

    def test_invitation_max_uses(self):
        """测试邀请码使用次数限制"""
        invitation = ClassInvitation.objects.create(
            code=ClassInvitation.generate_code(),
            class_obj=self.class_obj,
            created_by=self.teacher,
            max_uses=2
        )
        invitation.use()
        self.assertTrue(invitation.is_valid())
        invitation.use()
        self.assertFalse(invitation.is_valid())


class AuthAPITests(APITestCase):
    """认证API测试"""

    def test_register_student(self):
        """测试学生注册"""
        response = self.client.post('/api/auth/register', {
            'username': 'new_student',
            'password': 'TestPassword123!@#',
            'email': 'student@test.com',
            'role': 'student'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['role'], 'student')
        self.assertIn('token', response.data['data'])

    def test_register_teacher_without_activation_code(self):
        """测试教师注册（无激活码应该失败）"""
        response = self.client.post('/api/auth/register', {
            'username': 'new_teacher',
            'password': 'TestPassword123!@#',
            'email': 'teacher@test.com',
            'role': 'teacher'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_teacher_with_activation_code(self):
        """测试教师注册（使用激活码）"""
        admin = User.objects.create_superuser(
            username='admin',
            password='AdminPassword123',
            role='admin'
        )
        activation_code = ActivationCode.objects.create(
            code='TESTCODE',
            code_type='teacher',
            created_by=admin
        )

        response = self.client.post('/api/auth/register', {
            'username': 'new_teacher',
            'password': 'TestPassword123!@#',
            'email': 'teacher@test.com',
            'role': 'teacher',
            'activation_code': 'TESTCODE'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        activation_code.refresh_from_db()
        self.assertTrue(activation_code.is_used)

    def test_login(self):
        """测试登录"""
        User.objects.create_user(
            username='testuser',
            password='TestPassword123',
            role='student'
        )
        response = self.client.post('/api/auth/login', {
            'username': 'testuser',
            'password': 'TestPassword123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data['data'])

    def test_login_wrong_password(self):
        """测试登录（密码错误）"""
        User.objects.create_user(
            username='testuser',
            password='TestPassword123',
            role='student'
        )
        response = self.client.post('/api/auth/login', {
            'username': 'testuser',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_userinfo(self):
        """测试获取用户信息"""
        user = User.objects.create_user(
            username='testuser',
            password='TestPassword123',
            email='test@test.com',
            role='student'
        )
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/auth/userinfo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['username'], 'testuser')

    def test_update_userinfo(self):
        """测试更新用户信息"""
        user = User.objects.create_user(
            username='testuser',
            password='TestPassword123',
            role='student'
        )
        self.client.force_authenticate(user=user)

        response = self.client.put('/api/auth/userinfo/update', {
            'email': 'newemail@test.com',
            'real_name': '张三',
            'student_id': '20240001'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertEqual(user.email, 'newemail@test.com')
        self.assertEqual(user.real_name, '张三')
        self.assertEqual(user.student_id, '20240001')


class ActivationCodeAPITests(APITestCase):
    """激活码API测试"""

    def setUp(self):
        """创建管理员用户"""
        self.admin = User.objects.create_superuser(
            username='admin',
            password='AdminPassword123',
            role='admin'
        )
        self.student = User.objects.create_user(
            username='student',
            password='TestPassword123',
            role='student'
        )

    def test_generate_activation_code_as_admin(self):
        """测试管理员生成激活码"""
        self.client.force_authenticate(user=self.admin)

        response = self.client.post('/api/admin/activation-codes/generate', {
            'code_type': 'teacher',
            'count': 3
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['data']['codes']), 3)

    def test_generate_activation_code_as_student(self):
        """测试学生无法生成激活码"""
        self.client.force_authenticate(user=self.student)

        response = self.client.post('/api/admin/activation-codes/generate', {
            'code_type': 'teacher',
            'count': 1
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_activation_codes(self):
        """测试获取激活码列表"""
        self.client.force_authenticate(user=self.admin)

        for _ in range(5):
            ActivationCode.objects.create(
                code=ActivationCode.generate_code(),
                code_type='teacher',
                created_by=self.admin
            )

        response = self.client.get('/api/admin/activation-codes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total'], 5)


class ClassInvitationAPITests(APITestCase):
    """班级邀请码API测试"""

    def setUp(self):
        """创建测试数据"""
        self.teacher = User.objects.create_user(
            username='teacher',
            password='TestPassword123',
            role='teacher'
        )
        self.student = User.objects.create_user(
            username='student',
            password='TestPassword123',
            role='student'
        )
        self.course = Course.objects.create(
            name='测试课程',
            created_by=self.teacher
        )
        self.class_obj = Class.objects.create(
            course=self.course,
            name='测试班级',
            teacher=self.teacher
        )

    def test_generate_invitation(self):
        """测试教师生成邀请码"""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post('/api/teacher/invitations/generate', {
            'class_id': self.class_obj.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('code', response.data['data'])

    def test_student_join_class(self):
        """测试学生加入班级"""
        ClassInvitation.objects.create(
            code='INVITE',
            class_obj=self.class_obj,
            created_by=self.teacher
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.post('/api/classes/join', {
            'code': 'INVITE'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(Enrollment.objects.filter(
            user=self.student,
            class_obj=self.class_obj
        ).exists())

    def test_cannot_join_class_twice(self):
        """测试不能重复加入班级"""
        ClassInvitation.objects.create(
            code='INVITE',
            class_obj=self.class_obj,
            created_by=self.teacher
        )

        Enrollment.objects.create(
            user=self.student,
            class_obj=self.class_obj
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.post('/api/classes/join', {
            'code': 'INVITE'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_my_classes(self):
        """测试获取我的班级列表"""
        Enrollment.objects.create(
            user=self.student,
            class_obj=self.class_obj
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.get('/api/my-classes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['classes']), 1)

    def test_leave_class(self):
        """测试退出班级"""
        Enrollment.objects.create(
            user=self.student,
            class_obj=self.class_obj
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.delete(f'/api/classes/{self.class_obj.id}/leave')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(Enrollment.objects.filter(
            user=self.student,
            class_obj=self.class_obj
        ).exists())


class ClassStudentsAPITests(APITestCase):
    """班级学生管理API测试"""

    def setUp(self):
        """创建测试数据"""
        self.teacher = User.objects.create_user(
            username='teacher',
            password='TestPassword123',
            role='teacher'
        )
        self.student1 = User.objects.create_user(
            username='student1',
            password='TestPassword123',
            role='student'
        )
        self.student2 = User.objects.create_user(
            username='student2',
            password='TestPassword123',
            role='student'
        )
        self.course = Course.objects.create(
            name='测试课程',
            created_by=self.teacher
        )
        self.class_obj = Class.objects.create(
            course=self.course,
            name='测试班级',
            teacher=self.teacher
        )
        Enrollment.objects.create(user=self.student1, class_obj=self.class_obj)
        Enrollment.objects.create(user=self.student2, class_obj=self.class_obj)

    def test_get_class_students(self):
        """测试获取班级学生列表"""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(f'/api/teacher/classes/{self.class_obj.id}/students')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total'], 2)

    def test_remove_student_from_class(self):
        """测试从班级移除学生"""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.delete(
            f'/api/teacher/classes/{self.class_obj.id}/students/{self.student1.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(Enrollment.objects.filter(
            user=self.student1,
            class_obj=self.class_obj
        ).exists())


class HabitPreferenceTests(APITestCase):
    """学习习惯偏好测试"""

    def setUp(self):
        """创建测试用户"""
        self.user = User.objects.create_user(
            username='student',
            password='TestPassword123',
            role='student'
        )

    def test_update_habit_preference(self):
        """测试更新学习偏好"""
        self.client.force_authenticate(user=self.user)

        response = self.client.put('/api/profile/habit', {
            'preferred_resource': 'video',
            'preferred_study_time': 'evening'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        pref = HabitPreference.objects.get(user=self.user)
        self.assertEqual(pref.preferred_resource, 'video')
        self.assertEqual(pref.preferred_study_time, 'evening')

    def test_get_profile(self):
        """测试获取画像"""
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/profile')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('knowledge_mastery', response.data['data'])
        self.assertIn('ability_scores', response.data['data'])
        self.assertIn('habit_preferences', response.data['data'])


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
