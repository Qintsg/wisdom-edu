"""Regression tests for AI-facing student and search services."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from uuid import UUID
from random import Random

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APITestCase

from ai_services.services.student_graph_rag_service import student_graph_rag_service
from ai_services.services.web_search_service import (
    SEARCH_PROVIDERS,
    _search_with_provider,
    search_learning_resources,
)
from courses.models import Course
from typing import cast
from types import SimpleNamespace
from knowledge.models import KnowledgePoint, Resource
from platform_ai.mcp import ExternalResourceCandidate, InternalResourceCandidate
from platform_ai.mcp.resources import LearningResourceMCPService
from platform_ai.rag import student_learning_rag
from platform_ai.rag.runtime import (
    COURSE_RETRIEVAL_MODE,
    GraphRAGSearchHit,
    TokenHashEmbedder,
    student_graphrag_runtime,
)
from tools.kt_synthetic import _build_kp_profiles, _simulate_student_sequence
from users.models import User
from .test_student_rag_base import StudentLearningRAGFixture


# 维护意图：StudentLearningRAGRuntimeTests
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class StudentLearningRAGRuntimeTests(StudentLearningRAGFixture):
    # 维护意图：Runtime materialization should create Qdrant points and GraphRAG artifact metadata
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    @patch("platform_ai.rag.runtime.neo4j_service.sync_course_graphrag_projection")
    @patch.object(student_graphrag_runtime, "_qdrant")
    @patch.object(student_graphrag_runtime, "_embedder")
    def test_runtime_materialization_should_write_qdrant_points(
        self,
        mock_embedder,
        mock_qdrant,
        mock_sync_projection,
    ):
        """Runtime materialization should create Qdrant points and GraphRAG artifact metadata."""

        # 维护意图：轻量 Qdrant stub，避免测试依赖真实向量服务
        # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
        # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
        class StubQdrantClient:
            """轻量 Qdrant stub，避免测试依赖真实向量服务。"""

            def __init__(self):
                self.created_collections = []
                self.upserted_points = []

            # 维护意图：Pretend that every collection needs to be created for this test
            # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
            # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
            def collection_exists(self, collection_name):
                """Pretend that every collection needs to be created for this test."""
                _ = collection_name
                return False

            # 维护意图：Record collection creation inputs for later assertions
            # 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
            # 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
            def create_collection(self, collection_name, vectors_config, on_disk_payload):
                """Record collection creation inputs for later assertions."""
                self.created_collections.append((collection_name, vectors_config, on_disk_payload))
                return True

            # 维护意图：Capture upserted points without contacting a real Qdrant service
            # 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
            # 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
            def upsert(self, collection_name, points, wait):
                """Capture upserted points without contacting a real Qdrant service."""
                _ = (collection_name, wait)
                self.upserted_points.extend(points)
                return None

        stub_client = StubQdrantClient()
        mock_embedder.return_value = ("hash", TokenHashEmbedder(64))
        mock_qdrant.return_value = stub_client
        mock_sync_projection.return_value = {
            "documents": 2,
            "relations": 2,
            "status": "success",
        }

        payload = {
            "documents": [
                {
                    "id": "kp:1",
                    "kind": "knowledge_point",
                    "title": "数组基础",
                    "content": "数组基础是后续遍历的前置知识。",
                    "url": "",
                    "metadata": {"course_id": 101, "knowledge_point_id": 1},
                },
                {
                    "id": "resource:11",
                    "kind": "resource",
                    "title": "数组入门视频",
                    "content": "讲解数组概念、索引访问和基础遍历。",
                    "url": "https://example.com/array-video",
                    "metadata": {"course_id": 101, "knowledge_point_ids": [1, 2]},
                },
            ]
        }

        artifact_report = student_graphrag_runtime.materialize_course_payload(101, payload)

        self.assertEqual(artifact_report["collection_name"], student_graphrag_runtime.collection_name(101))
        self.assertEqual(artifact_report["vector_points"], 2)
        self.assertTrue(artifact_report["neo4j_projection_ready"])
        self.assertEqual(len(stub_client.created_collections), 1)
        self.assertEqual(len(stub_client.upserted_points), 2)
        self.assertEqual(
            stub_client.upserted_points[0].payload["external_id"],
            "kp:1",
        )
        UUID(str(stub_client.upserted_points[0].id))

    # 维护意图：Node resource recommendations should surface linked internal resources first
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    @patch("platform_ai.rag.student.Resource.objects.filter")
    def test_recommend_resources_for_node_should_return_internal_course_resources(self, mock_resource_filter):
        """Node resource recommendations should surface linked internal resources first."""
        mock_resource_filter.return_value.order_by.return_value = [self.resource]
        node_resource_manager = Mock()
        node_resource_manager.filter.return_value.order_by.return_value = [self.resource]
        node = SimpleNamespace(
            knowledge_point=self.point_intro,
            resources=node_resource_manager,
            path=SimpleNamespace(course=self.course),
        )

        recommendation = student_learning_rag.recommend_resources_for_node(
            node=node,
            user=SimpleNamespace(id=501),
            mastery_value=0.25,
            completed_resource_ids=set(),
            external_count=0,
        )

        self.assertTrue(recommendation["internal_resources"])
        self.assertEqual(
            recommendation["internal_resources"][0]["resource_id"], self.resource.id
        )
        self.assertEqual(recommendation["external_resources"], [])

    # 维护意图：Unbound course resources should still be recommended when they match the node point
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    @patch("platform_ai.rag.student.Resource.objects.filter")
    def test_recommend_resources_for_node_should_fallback_to_course_local_resources(self, mock_resource_filter):
        """Unbound course resources should still be recommended when they match the node point."""
        local_resource = SimpleNamespace(
            id=12,
            title="数组基础本地视频",
            resource_type="video",
            url="/media/resources/array-local.mp4",
            file=None,
            description="讲解数组基础、索引访问和遍历方式。",
            duration=360,
            sort_order=1,
            chapter_number="1.1",
        )
        empty_query = Mock()
        empty_query.order_by.return_value = []
        course_query = Mock()
        course_query.order_by.return_value = [local_resource]
        mock_resource_filter.side_effect = [empty_query, course_query]
        node_resource_manager = Mock()
        node_resource_manager.filter.return_value.order_by.return_value = []
        node = SimpleNamespace(
            knowledge_point=self.point_intro,
            resources=node_resource_manager,
            path=SimpleNamespace(course=self.course),
        )

        recommendation = student_learning_rag.recommend_resources_for_node(
            node=node,
            user=SimpleNamespace(id=501),
            mastery_value=0.25,
            completed_resource_ids=set(),
            external_count=0,
        )

        self.assertEqual(
            recommendation["internal_resources"][0]["resource_id"],
            local_resource.id,
        )
        self.assertTrue(recommendation["internal_resources"][0]["is_internal"])
