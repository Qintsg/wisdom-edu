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
from tools.dkt_training import _build_kp_profiles, _simulate_student_sequence
from users.models import User

class StudentAIMulticourseTests(APITestCase):
    """Ensure AI endpoints keep student queries scoped to the chosen course."""

    def setUp(self):
        """Create two courses that intentionally share the same point name."""
        self.teacher = User.objects.create_user(
            username="teacher_multi",
            email="teacher_multi@example.com",
            password="Test123456",
            role="teacher",
        )
        self.student = User.objects.create_user(
            username="student_multi",
            email="student_multi@example.com",
            password="Test123456",
            role="student",
        )
        self.course_a = Course.objects.create(name="课程A", created_by=self.teacher)
        self.course_b = Course.objects.create(name="课程B", created_by=self.teacher)
        self.point_a = KnowledgePoint.objects.create(
            course=self.course_a,
            name="共享知识点",
            description="课程A的知识点",
            is_published=True,
        )
        self.point_b = KnowledgePoint.objects.create(
            course=self.course_b,
            name="共享知识点",
            description="课程B的知识点",
            is_published=True,
        )
        self.resource_a = Resource.objects.create(
            course=self.course_a,
            title="课程A资源",
            resource_type="document",
            url="https://example.com/course-a",
            uploaded_by=self.teacher,
            is_visible=True,
        )
        self.resource_a.knowledge_points.add(self.point_a)
        self.client.force_authenticate(user=self.student)

    def test_graph_rag_search_should_only_return_points_from_selected_course(self):
        """Point search should not leak similarly named points from other courses."""
        result = student_graph_rag_service.search_points(
            user=self.student,
            course_id=self.course_a.id,
            query="共享知识点",
            limit=10,
        )

        matched_ids = [item["point_id"] for item in result["matched_points"]]
        self.assertIn(self.point_a.id, matched_ids)
        self.assertNotIn(self.point_b.id, matched_ids)

    @patch("ai_services.services.student_graph_rag_service.student_graphrag_runtime.search_points")
    def test_graph_rag_search_should_surface_runtime_supporting_sources(self, mock_runtime_search):
        """Hybrid GraphRAG matches should expose supporting source titles to the UI."""
        mock_runtime_search.return_value = [
            {
                "point_id": self.point_a.id,
                "graph_rag_score": 3.25,
                "source_titles": ["课程A资源"],
                "prerequisites": [],
                "postrequisites": [],
            }
        ]

        result = student_graph_rag_service.search_points(
            user=self.student,
            course_id=self.course_a.id,
            query="课程A资源",
            limit=8,
        )

        self.assertEqual(result["retrieval_mode"], COURSE_RETRIEVAL_MODE)
        self.assertEqual(result["matched_points"][0]["supporting_sources"], ["课程A资源"])

    def test_graph_rag_search_should_match_point_names_inside_full_sentence(self):
        """Full-sentence queries should still resolve explicit point names within the selected course."""
        result = student_graph_rag_service.search_points(
            user=self.student,
            course_id=self.course_a.id,
            query="我想知道共享知识点和课程资源之间是什么关系",
            limit=5,
        )

        self.assertEqual(result["retrieval_mode"], "name_match")
        self.assertEqual(result["matched_points"][0]["point_id"], self.point_a.id)

    @patch("ai_services.services.student_graph_rag_service.student_learning_rag.answer_course_question")
    def test_graph_rag_ask_should_route_structure_question_without_point(self, mock_answer_course_question):
        """Structure questions without point_id should use the course-level GraphRAG answer path first."""
        mock_answer_course_question.return_value = {
            "answer": "共享知识点与课程资源之间存在直接关联。",
            "sources": [
                {
                    "id": "cypher:course-a",
                    "title": "共享知识点 · 图关系",
                    "kind": "graph_query",
                    "url": "",
                    "excerpt": "共享知识点与课程资源之间存在直接关联。",
                    "query_mode": "graph_tools",
                    "retrieval_source": "text2cypher",
                }
            ],
            "mode": "neo4j_graphrag_tools",
            "query_modes": ["local", "graph_tools"],
            "key_points": ["共享知识点"],
            "matched_point_ids": [self.point_a.id],
        }

        result = student_graph_rag_service.ask(
            user=self.student,
            course_id=self.course_a.id,
            question="共享知识点和课程资源之间是什么关系？",
        )

        mock_answer_course_question.assert_called_once()
        self.assertEqual(result["mode"], "neo4j_graphrag_tools")
        self.assertEqual(result["matched_point"]["point_id"], self.point_a.id)
        self.assertEqual(result["query_modes"], ["local", "graph_tools"])

    @patch("ai_services.services.student_graph_rag_service.student_learning_rag.answer_graph_question")
    def test_graph_rag_ask_endpoint_should_surface_runtime_modes(self, mock_answer_graph_question):
        """The graph-rag ask endpoint should preserve the enhanced runtime mode metadata."""
        mock_answer_graph_question.return_value = {
            "answer": "共享知识点的前置知识包括课程A基础。",
            "sources": [
                {
                    "id": "cypher:1",
                    "title": "共享知识点 · 图关系",
                    "kind": "graph_query",
                    "url": "",
                    "excerpt": "共享知识点的前置知识包括课程A基础。",
                    "query_mode": "graph_tools",
                    "retrieval_source": "text2cypher",
                }
            ],
            "mode": "neo4j_graphrag_tools",
            "query_modes": ["local", "graph_tools"],
            "key_points": ["课程A基础"],
        }

        response = self.client.post(
            "/api/student/ai/graph-rag/ask",
            {
                "course_id": self.course_a.id,
                "point_id": self.point_a.id,
                "question": "共享知识点的前置知识是什么？",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.data["data"]
        self.assertEqual(payload["mode"], "neo4j_graphrag_tools")
        self.assertEqual(payload["query_modes"], ["local", "graph_tools"])
        self.assertEqual(payload["key_points"], ["课程A基础"])

    def test_ai_resource_reason_should_reject_cross_course_resource_requests(self):
        """Resource reasoning should reject mismatched course and point combinations."""
        response = self.client.post(
            "/api/student/ai/resource-reason",
            {
                "resource_id": self.resource_a.id,
                "course_id": self.course_b.id,
                "point_id": self.point_b.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("不匹配", response.data["msg"])


class _MCPStubResponse:
    """Small response double for resource MCP HTTP calls."""

    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        """Mirror requests.Response without raising in success fixtures."""

    def json(self) -> dict[str, object]:
        """Return the configured JSON payload."""

        return self.payload


class _MCPStubSession:
    """Capture Exa and Firecrawl requests without network access."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def post(self, url: str, headers: dict[str, str], json: dict[str, object], timeout: int) -> _MCPStubResponse:
        """Return deterministic Exa / Firecrawl payloads."""

        self.calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        if "firecrawl" in url:
            return _MCPStubResponse(
                {
                    "success": True,
                    "data": {
                        "markdown": "数组基础讲解，包含索引访问、顺序遍历和示例代码。",
                        "metadata": {"title": "数组基础官方教程", "description": "数组入门正文摘要"},
                    },
                }
            )
        return _MCPStubResponse(
            {
                "results": [
                    {
                        "title": "数组基础教程",
                        "url": "https://docs.example.com/array",
                        "highlights": ["数组基础包含索引访问和遍历。"],
                        "text": "数组基础长文本。",
                    }
                ]
            }
        )


class ResourceMCPServiceTests(SimpleTestCase):
    """Cover Exa + Firecrawl resource MCP integration."""

    @override_settings(
        RESOURCE_MCP_ENABLED=True,
        RESOURCE_MCP_EXA_ENABLED=True,
        RESOURCE_MCP_FIRECRAWL_ENABLED=True,
        RESOURCE_MCP_TIMEOUT_SECONDS=9,
        RESOURCE_MCP_FIRECRAWL_LIMIT=1,
        EXA_API_KEY="exa-demo-key",
        EXA_SEARCH_URL="https://api.exa.ai/search",
        EXA_SEARCH_TYPE="neural",
        EXA_MAX_RESULTS=4,
        FIRECRAWL_API_KEY="firecrawl-demo-key",
        FIRECRAWL_SCRAPE_URL="https://api.firecrawl.dev/v1/scrape",
        FIRECRAWL_TIMEOUT_MILLISECONDS=12000,
    )
    def test_external_resource_mcp_should_search_exa_and_enrich_with_firecrawl(self):
        """External resource MCP should call Exa first, then enrich the page body."""

        stub_session = _MCPStubSession()
        service = LearningResourceMCPService(session=stub_session)

        resources = service.search_external_resources(
            point_name="数组基础",
            student_mastery=0.25,
            existing_titles=[],
            course_name="数据结构",
            count=1,
        )

        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0].provider, "exa_firecrawl")
        self.assertEqual(resources[0].title, "数组基础官方教程")
        self.assertIn("数组入门正文摘要", resources[0].snippet)
        self.assertEqual(stub_session.calls[0]["headers"]["x-api-key"], "exa-demo-key")
        self.assertEqual(
            stub_session.calls[1]["headers"]["Authorization"],
            "Bearer firecrawl-demo-key",
        )

    @patch("platform_ai.rag.student.llm_facade.recommend_external_resources")
    @patch("platform_ai.rag.student.resource_mcp_service.search_internal_resources")
    @patch("platform_ai.rag.student.resource_mcp_service.search_external_resources")
    def test_node_resource_recommendation_should_prefer_mcp_external_results(
        self,
        mock_mcp_search,
        mock_internal_search,
        mock_llm_external,
    ):
        """RAG resource recommendation should use MCP results before LLM web fallback."""

        resource = SimpleNamespace(
            id=11,
            title="数组入门视频",
            resource_type="video",
            url="https://example.com/array-video",
            file=None,
            description="讲解数组概念、索引访问和基础遍历。",
            duration=300,
            sort_order=0,
            chapter_number="1.1",
        )
        point = SimpleNamespace(id=1, name="数组基础", chapter="第一章")
        course = SimpleNamespace(id=101, name="数据结构")
        node_resource_manager = Mock()
        node_resource_manager.filter.return_value.order_by.return_value = [resource]
        node = SimpleNamespace(
            knowledge_point=point,
            resources=node_resource_manager,
            path=SimpleNamespace(course=course),
        )
        mock_internal_search.return_value = [
            InternalResourceCandidate(resource=resource, score=1000, source="path_node")
        ]
        mock_mcp_search.return_value = [
            ExternalResourceCandidate(
                title="数组基础官方教程",
                url="https://docs.example.com/array",
                resource_type="document",
                source="docs.example.com",
                provider="exa_firecrawl",
                snippet="数组基础正文摘要",
                reason="Exa 与 Firecrawl 确认该资源相关。",
                learning_tips="先学课程内资源，再读外部教程。",
            )
        ]

        recommendation = student_learning_rag.recommend_resources_for_node(
            node=node,
            user=SimpleNamespace(id=501),
            mastery_value=0.25,
            completed_resource_ids=set(),
            external_count=1,
        )

        self.assertEqual(recommendation["external_resources"][0]["provider"], "exa_firecrawl")
        self.assertEqual(recommendation["external_resources"][0]["source"], "docs.example.com")
        mock_llm_external.assert_not_called()
