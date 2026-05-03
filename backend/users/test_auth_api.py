"""用户认证与激活码 API 测试。"""

from __future__ import annotations

from rest_framework import status
from rest_framework.test import APITestCase

from .models import ActivationCode, User


# 维护意图：认证 API 测试
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class AuthAPITests(APITestCase):
    """认证 API 测试。"""

    # 维护意图：测试学生注册
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_register_student(self):
        """测试学生注册。"""
        response = self.client.post('/api/auth/register', {
            'username': 'new_student',
            'password': 'TestPassword123!@#',
            'email': 'student@test.com',
            'role': 'student'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['role'], 'student')
        self.assertIn('token', response.data['data'])

    # 维护意图：测试教师注册无激活码失败
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_register_teacher_without_activation_code(self):
        """测试教师注册无激活码失败。"""
        response = self.client.post('/api/auth/register', {
            'username': 'new_teacher',
            'password': 'TestPassword123!@#',
            'email': 'teacher@test.com',
            'role': 'teacher'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # 维护意图：测试教师使用激活码注册
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_register_teacher_with_activation_code(self):
        """测试教师使用激活码注册。"""
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

    # 维护意图：测试登录
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_login(self):
        """测试登录。"""
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

    # 维护意图：测试密码错误登录
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_login_wrong_password(self):
        """测试密码错误登录。"""
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

    # 维护意图：测试获取用户信息
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_userinfo(self):
        """测试获取用户信息。"""
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

    # 维护意图：测试更新用户信息
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_update_userinfo(self):
        """测试更新用户信息。"""
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


# 维护意图：激活码 API 测试
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ActivationCodeAPITests(APITestCase):
    """激活码 API 测试。"""

    # 维护意图：创建管理员与学生用户
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def setUp(self):
        """创建管理员与学生用户。"""
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

    # 维护意图：测试管理员生成激活码
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_generate_activation_code_as_admin(self):
        """测试管理员生成激活码。"""
        self.client.force_authenticate(user=self.admin)

        response = self.client.post('/api/admin/activation-codes/generate', {
            'code_type': 'teacher',
            'count': 3
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['data']['codes']), 3)

    # 维护意图：测试学生无法生成激活码
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_generate_activation_code_as_student(self):
        """测试学生无法生成激活码。"""
        self.client.force_authenticate(user=self.student)

        response = self.client.post('/api/admin/activation-codes/generate', {
            'code_type': 'teacher',
            'count': 1
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 维护意图：测试获取激活码列表
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_list_activation_codes(self):
        """测试获取激活码列表。"""
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
