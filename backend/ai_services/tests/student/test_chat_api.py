#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
学生端 AI 聊天 HTTP 接口回归测试。
@Project : wisdom-edu
@File : test_chat_api.py
@Author : Qintsg
@Date : 2026-05-29 00:00
'''

from rest_framework.test import APITestCase

from users.models import User


class StudentAIChatApiTests(APITestCase):
    """学生端 AI 聊天接口测试。"""

    def setUp(self) -> None:
        """
        创建学生用户并登录测试客户端。

        :return: None。
        """
        self.student = User.objects.create_user(
            username="ai_chat_student",
            password="Test123456",
            role="student",
        )
        self.client.force_authenticate(user=self.student)

    def test_knowledge_query_empty_payload_should_return_bad_request(self) -> None:
        """
        图谱问答兼容入口空问题应返回 400，而不是装饰视图互调导致 500。

        :return: None。
        """
        response = self.client.post(
            "/api/student/ai/knowledge-query",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["msg"], "请输入问题")
