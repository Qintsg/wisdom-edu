#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
教师端班级学生画像接口回归测试。
@Project : wisdom-edu
@File : test_teacher_student_profiles.py
@Author : Qintsg
@Date : 2026-05-29 00:00
'''

from rest_framework.test import APITestCase

from assessments.models import AbilityScore
from courses.models import Class, ClassCourse, Course, Enrollment
from users.models import User


class TeacherStudentProfileTests(APITestCase):
    """教师端班级学生画像接口测试。"""

    def setUp(self) -> None:
        """
        创建教师、学生、班级和课程上下文。

        :return: None。
        """
        self.teacher = User.objects.create_user(
            username="profile_teacher_api",
            password="Test123456",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="profile_student_api",
            password="Test123456",
            role="student",
        )
        self.course = Course.objects.create(
            name="班级画像课程",
            created_by=self.teacher,
        )
        self.other_course = Course.objects.create(
            name="班级画像其他课程",
            created_by=self.teacher,
        )
        self.class_obj = Class.objects.create(
            name="画像测试班级",
            teacher=self.teacher,
        )
        ClassCourse.objects.create(
            class_obj=self.class_obj,
            course=self.course,
            published_by=self.teacher,
        )
        ClassCourse.objects.create(
            class_obj=self.class_obj,
            course=self.other_course,
            published_by=self.teacher,
        )
        Enrollment.objects.create(
            user=self.student,
            class_obj=self.class_obj,
        )
        AbilityScore.objects.create(
            user=self.student,
            course=self.course,
            scores={"逻辑推理": 88},
        )
        AbilityScore.objects.create(
            user=self.student,
            course=self.other_course,
            scores={"逻辑推理": 12},
        )
        self.client.force_authenticate(user=self.teacher)

    def test_class_student_profiles_should_use_ability_score_json_field(self) -> None:
        """
        班级画像列表应读取 AbilityScore.scores，不能访问已删除的旧字段。

        :return: None。
        """
        response = self.client.get(
            f"/api/teacher/classes/{self.class_obj.id}/student-profiles"
        )

        self.assertEqual(response.status_code, 200)
        profile = response.data["data"]["profiles"][0]
        self.assertEqual(profile["ability_score"], {"逻辑推理": 88})

    def test_class_student_profiles_should_accept_explicit_course_context(self) -> None:
        """
        多课程班级画像列表应允许显式指定课程上下文。

        :return: None。
        """
        response = self.client.get(
            f"/api/teacher/classes/{self.class_obj.id}/student-profiles",
            {"course_id": self.other_course.id},
        )

        self.assertEqual(response.status_code, 200)
        profile = response.data["data"]["profiles"][0]
        self.assertEqual(profile["ability_score"], {"逻辑推理": 12})
