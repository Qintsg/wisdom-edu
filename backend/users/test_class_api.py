"""班级邀请码与班级学生管理 API 测试。"""

from __future__ import annotations

from rest_framework import status
from rest_framework.test import APITestCase

from courses.models import Class, ClassCourse, Course, Enrollment
from .models import ClassInvitation, User


class ClassInvitationAPITests(APITestCase):
    """班级邀请码 API 测试。"""

    def setUp(self):
        """创建测试数据。"""
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
        """测试教师生成邀请码。"""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post('/api/teacher/invitations/generate', {
            'class_id': self.class_obj.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('code', response.data['data'])

    def test_student_join_class(self):
        """测试学生加入班级。"""
        ClassInvitation.objects.create(
            code='INVITE',
            class_obj=self.class_obj,
            created_by=self.teacher
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.post('/api/student/classes/join', {
            'code': 'INVITE'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['class_id'], self.class_obj.id)
        self.assertEqual(response.data['data']['course_id'], self.course.id)
        self.assertEqual(response.data['data']['courses'][0]['course_id'], self.course.id)

        self.assertTrue(Enrollment.objects.filter(
            user=self.student,
            class_obj=self.class_obj
        ).exists())

    def test_cannot_join_class_twice(self):
        """测试不能重复加入班级。"""
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

        response = self.client.post('/api/student/classes/join', {
            'code': 'INVITE'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_join_class_returns_published_course_without_default_course(self):
        """测试无默认课程班级仍返回已发布课程摘要。"""
        another_class = Class.objects.create(
            name='无默认课程班级',
            teacher=self.teacher
        )
        ClassCourse.objects.create(
            class_obj=another_class,
            course=self.course,
            published_by=self.teacher,
        )
        ClassInvitation.objects.create(
            code='NODEFT',
            class_obj=another_class,
            created_by=self.teacher
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.post('/api/student/classes/join', {
            'code': 'nodeft'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['class_id'], another_class.id)
        self.assertEqual(response.data['data']['course_id'], self.course.id)
        self.assertEqual(response.data['data']['courses'][0]['course_name'], self.course.name)

    def test_my_classes(self):
        """测试获取我的班级列表。"""
        Enrollment.objects.create(
            user=self.student,
            class_obj=self.class_obj
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.get('/api/student/classes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']['classes']), 1)
        self.assertEqual(response.data['data']['classes'][0]['course_id'], self.course.id)

    def test_leave_class(self):
        """测试退出班级。"""
        Enrollment.objects.create(
            user=self.student,
            class_obj=self.class_obj
        )

        self.client.force_authenticate(user=self.student)

        response = self.client.delete(f'/api/student/classes/{self.class_obj.id}/leave')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(Enrollment.objects.filter(
            user=self.student,
            class_obj=self.class_obj
        ).exists())


class ClassStudentsAPITests(APITestCase):
    """班级学生管理 API 测试。"""

    def setUp(self):
        """创建测试数据。"""
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
        """测试获取班级学生列表。"""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(f'/api/teacher/classes/{self.class_obj.id}/students')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['total'], 2)

    def test_remove_student_from_class(self):
        """测试从班级移除学生。"""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.delete(
            f'/api/teacher/classes/{self.class_obj.id}/students/{self.student1.id}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(Enrollment.objects.filter(
            user=self.student1,
            class_obj=self.class_obj
        ).exists())
