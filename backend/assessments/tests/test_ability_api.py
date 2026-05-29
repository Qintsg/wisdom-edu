#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
能力评测接口回归测试。
@Project : wisdom-edu
@File : test_ability_api.py
@Author : Qintsg
@Date : 2026-05-29 00:00
'''

from rest_framework.test import APITestCase

from users.models import User


class AbilityAssessmentApiTests(APITestCase):
    """能力评测接口测试。"""

    def setUp(self) -> None:
        """
        创建学生用户并登录测试客户端。

        :return: None。
        """
        self.student = User.objects.create_user(
            username="ability_retake_student",
            password="Test123456",
            role="student",
        )
        self.client.force_authenticate(user=self.student)

    def test_retake_ability_assessment_should_return_questions(self) -> None:
        """
        重做能力评测入口不应直接调用已装饰视图导致 500。

        :return: None。
        """
        response = self.client.get("/api/student/assessments/initial/ability/retake")

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data["data"]["questions"]), 0)

    def test_retake_ability_assessment_should_reject_invalid_course_id(self) -> None:
        """
        重做能力评测应拒绝非数字课程 ID，避免 ORM 过滤抛 500。

        :return: None。
        """
        response = self.client.get(
            "/api/student/assessments/initial/ability/retake?course_id=abc"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["msg"], "课程ID格式错误")

    def test_submit_ability_assessment_should_reject_missing_course(self) -> None:
        """
        提交能力评测时不存在课程 ID 应返回 400，避免写入外键异常。

        :return: None。
        """
        response = self.client.post(
            "/api/student/assessments/initial/ability/submit",
            {"course_id": 99999999, "answers": {"1": "A"}},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["msg"], "课程不存在")
