"""用户、激活码和班级邀请码模型测试。"""

from __future__ import annotations

from django.test import TestCase

from courses.models import Class, Course
from .models import ActivationCode, ClassInvitation, User


class UserModelTests(TestCase):
    """用户模型测试。"""

    def test_create_student(self):
        """测试创建学生用户。"""
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
        """测试创建教师用户。"""
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
        """测试创建管理员用户。"""
        user = User.objects.create_superuser(
            username='test_admin',
            password='AdminPassword123',
            email='admin@test.com',
            role='admin'
        )
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_admin)


class ActivationCodeModelTests(TestCase):
    """激活码模型测试。"""

    def setUp(self):
        """创建测试用户。"""
        self.admin = User.objects.create_superuser(
            username='admin',
            password='AdminPassword123',
            email='admin@test.com',
            role='admin'
        )

    def test_generate_code(self):
        """测试生成激活码。"""
        code = ActivationCode.generate_code()
        self.assertEqual(len(code), 8)
        self.assertTrue(code.isupper())

    def test_create_activation_code(self):
        """测试创建激活码。"""
        code = ActivationCode.objects.create(
            code=ActivationCode.generate_code(),
            code_type='teacher',
            created_by=self.admin
        )
        self.assertFalse(code.is_used)
        self.assertTrue(code.is_valid())

    def test_use_activation_code(self):
        """测试使用激活码。"""
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
        """测试激活码不能重复使用。"""
        code = ActivationCode.objects.create(
            code=ActivationCode.generate_code(),
            code_type='teacher',
            created_by=self.admin,
            is_used=True
        )
        self.assertFalse(code.is_valid())


class ClassInvitationModelTests(TestCase):
    """班级邀请码模型测试。"""

    def setUp(self):
        """创建测试数据。"""
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
        """测试生成邀请码。"""
        code = ClassInvitation.generate_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isupper())

    def test_create_invitation(self):
        """测试创建邀请码。"""
        invitation = ClassInvitation.objects.create(
            code=ClassInvitation.generate_code(),
            class_obj=self.class_obj,
            created_by=self.teacher
        )
        self.assertTrue(invitation.is_valid())
        self.assertEqual(invitation.use_count, 0)

    def test_use_invitation(self):
        """测试使用邀请码。"""
        invitation = ClassInvitation.objects.create(
            code=ClassInvitation.generate_code(),
            class_obj=self.class_obj,
            created_by=self.teacher
        )
        invitation.use()
        self.assertEqual(invitation.use_count, 1)

    def test_invitation_max_uses(self):
        """测试邀请码使用次数限制。"""
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
