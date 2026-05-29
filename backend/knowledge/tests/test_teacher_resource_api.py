#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
教师端资源接口回归测试。
@Project : wisdom-edu
@File : test_teacher_resource_api.py
@Author : Qintsg
@Date : 2026-05-29 00:00
'''

from unittest.mock import patch

from rest_framework.test import APITestCase

from courses.models import Course
from knowledge.models import KnowledgePoint, Resource
from users.models import User


class TeacherResourceApiTests(APITestCase):
    """教师端资源创建接口测试。"""

    def setUp(self) -> None:
        """
        创建教师、课程和知识点上下文。

        :return: None。
        """
        self.teacher = User.objects.create_user(
            username="resource_teacher_api",
            password="Test123456",
            role="teacher",
        )
        self.course = Course.objects.create(
            name="资源接口课程",
            created_by=self.teacher,
        )
        self.point = KnowledgePoint.objects.create(
            course=self.course,
            name="资源接口知识点",
            is_published=True,
        )
        self.other_point = KnowledgePoint.objects.create(
            course=self.course,
            name="资源接口第二知识点",
            is_published=True,
        )
        self.client.force_authenticate(user=self.teacher)

    @patch("knowledge.api.teacher.resource.schedule_course_rag_index_refresh")
    def test_create_resource_should_accept_single_knowledge_point_id_string(
        self,
        mock_refresh,
    ) -> None:
        """
        multipart 单值 knowledge_point_ids 应作为列表写入关联。

        :param mock_refresh: RAG 索引刷新调度 mock。
        :return: None。
        """
        response = self.client.post(
            "/api/teacher/resources/create",
            {
                "course_id": self.course.id,
                "title": "资源接口回归资源",
                "resource_type": "link",
                "url": "https://edu.qintsg.xyz/resource-regression",
                "knowledge_point_ids": str(self.point.id),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        resource = Resource.objects.get(id=response.data["data"]["resource_id"])
        self.assertEqual(list(resource.knowledge_points.values_list("id", flat=True)), [self.point.id])
        mock_refresh.assert_called_once_with(self.course.id)

    @patch("knowledge.api.teacher.resource.schedule_course_rag_index_refresh")
    def test_create_resource_should_keep_repeated_multipart_knowledge_points(
        self,
        _mock_refresh,
    ) -> None:
        """
        multipart 重复 knowledge_point_ids 字段应保留全部知识点。

        :param _mock_refresh: RAG 索引刷新调度 mock。
        :return: None。
        """
        response = self.client.post(
            "/api/teacher/resources/create",
            {
                "course_id": self.course.id,
                "title": "资源接口多知识点资源",
                "resource_type": "link",
                "url": "https://edu.qintsg.xyz/resource-multi-point",
                "knowledge_point_ids": [str(self.point.id), str(self.other_point.id)],
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 201)
        resource = Resource.objects.get(id=response.data["data"]["resource_id"])
        self.assertEqual(
            list(resource.knowledge_points.order_by("id").values_list("id", flat=True)),
            [self.point.id, self.other_point.id],
        )

    @patch("knowledge.api.teacher.resource.schedule_course_rag_index_refresh")
    def test_update_resource_should_clear_explicit_empty_knowledge_points(
        self,
        _mock_refresh,
    ) -> None:
        """
        更新资源显式传空知识点列表时应清空既有关联。

        :param _mock_refresh: RAG 索引刷新调度 mock。
        :return: None。
        """
        resource = Resource.objects.create(
            course=self.course,
            title="待清空资源",
            resource_type="link",
            url="https://edu.qintsg.xyz/resource-clear-points",
            uploaded_by=self.teacher,
        )
        resource.knowledge_points.set([self.point, self.other_point])

        response = self.client.put(
            f"/api/teacher/resources/{resource.id}",
            {"knowledge_point_ids": []},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        resource.refresh_from_db()
        self.assertEqual(list(resource.knowledge_points.all()), [])

    @patch("knowledge.api.teacher.resource.schedule_course_rag_index_refresh")
    def test_update_resource_should_prioritize_explicit_empty_points_over_point_id(
        self,
        _mock_refresh,
    ) -> None:
        """
        显式空 knowledge_point_ids 应优先于旧 point_id 字段，避免清空失败。

        :param _mock_refresh: RAG 索引刷新调度 mock。
        :return: None。
        """
        resource = Resource.objects.create(
            course=self.course,
            title="待兼容清空资源",
            resource_type="link",
            url="https://edu.qintsg.xyz/resource-clear-compatible",
            uploaded_by=self.teacher,
        )
        resource.knowledge_points.set([self.point])

        response = self.client.put(
            f"/api/teacher/resources/{resource.id}",
            {"knowledge_point_ids": [], "point_id": self.point.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        resource.refresh_from_db()
        self.assertEqual(list(resource.knowledge_points.all()), [])

    @patch("knowledge.api.teacher.resource.schedule_course_rag_index_refresh")
    def test_create_resource_should_reject_invalid_knowledge_point_id(
        self,
        mock_refresh,
    ) -> None:
        """
        非法知识点 ID 应返回 400，避免多对多 set 抛出 500。

        :param mock_refresh: RAG 索引刷新调度 mock。
        :return: None。
        """
        response = self.client.post(
            "/api/teacher/resources/create",
            {
                "course_id": self.course.id,
                "title": "资源非法知识点",
                "resource_type": "link",
                "url": "https://edu.qintsg.xyz/resource-invalid-point",
                "knowledge_point_ids": "abc",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["msg"], "知识点ID格式错误")
        mock_refresh.assert_not_called()
