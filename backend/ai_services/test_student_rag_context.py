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
from .test_student_rag_base import StudentLearningRAGFixture


class StudentLearningRAGContextTests(StudentLearningRAGFixture):
    @patch.object(student_learning_rag, "_ensure_index")
    def test_build_path_context_should_expose_multi_mode_sources(self, mock_ensure_index):
        """Path context should include GraphRAG sections and course-owned evidence sources."""
        mock_ensure_index.return_value = self.payload
        result = student_learning_rag.build_path_context(
            course_id=int(self.course.id),
            target="掌握数组基础与遍历",
            pending_points=[self.point_intro, self.point_traverse],
        )

        self.assertIn("Local Search", result["retrieved_context"])
        self.assertTrue(result["retrieved_sources"])
        source_titles = [item["title"] for item in result["retrieved_sources"]]
        self.assertIn("数组入门视频", source_titles)
        self.assertTrue(
            any(item["query_mode"] in {"local", "global", "drift"} for item in result["retrieved_sources"])
        )

    @patch("platform_ai.rag.student.llm_facade")
    @patch.object(student_learning_rag, "_ensure_index")
    def test_answer_graph_question_should_fallback_to_graph_context_when_llm_unavailable(
        self, mock_ensure_index, mock_llm
    ):
        """Question answering should still return graph-grounded content without LLM."""
        mock_ensure_index.return_value = self.payload
        mock_llm.is_available = False

        result = student_learning_rag.answer_graph_question(
            course_id=int(self.course.id),
            point=self.point_intro,
            question="数组基础应该如何入门？",
        )

        self.assertEqual(result["mode"], "graph_rag")
        self.assertEqual(result["query_modes"], ["local", "global", "drift"])
        self.assertIn("数组基础", result["answer"])
        self.assertTrue(result["sources"])

    @patch("platform_ai.rag.student.student_graphrag_runtime.search_documents")
    @patch.object(student_learning_rag, "_ensure_index")
    def test_local_context_should_merge_vector_hits_into_sources(self, mock_ensure_index, mock_search_documents):
        """Local context should merge Neo4j GraphRAG vector hits before native graph evidence."""
        mock_ensure_index.return_value = self.payload
        mock_search_documents.return_value = [
            GraphRAGSearchHit(
                external_id="kp:1",
                doc_id="kp:1",
                title="数组基础",
                kind="knowledge_point",
                excerpt="数组基础是后续遍历的前置知识。",
                url="",
                score=0.91,
                point_ids=[1],
                matched_points=[{"point_id": 1, "point_name": "数组基础"}],
                prerequisites=[],
                postrequisites=[{"point_id": 2, "point_name": "数组遍历"}],
            )
        ]

        local_context = student_learning_rag._build_local_context(
            course_id=int(self.course.id),
            query="数组基础如何入门",
            seed_entity_ids={"kp:1"},
        )

        self.assertIn("向量证据", local_context.context)
        self.assertTrue(
            any(source.get("retrieval_source") == COURSE_RETRIEVAL_MODE for source in local_context.sources)
        )

    @patch("platform_ai.rag.student.student_graphrag_runtime.query_graph")
    @patch("platform_ai.rag.student.llm_facade")
    @patch.object(student_learning_rag, "_ensure_index")
    def test_answer_graph_question_should_merge_graph_query_sources(
        self,
        mock_ensure_index,
        mock_llm,
        mock_query_graph,
    ):
        """Question answering should merge Text2Cypher graph-query evidence into the final payload."""
        mock_ensure_index.return_value = self.payload
        mock_llm.is_available = False
        mock_query_graph.return_value = {
            "context": "结构化图查询：\n- 数组基础 的前置知识包括：变量与索引。",
            "sources": [
                {
                    "id": "cypher:1:0:graph",
                    "title": "数组基础 · 图关系",
                    "kind": "graph_query",
                    "url": "",
                    "excerpt": "数组基础 的前置知识包括：变量与索引。",
                    "query_mode": "graph_tools",
                    "retrieval_source": "text2cypher",
                }
            ],
            "tools_selected": ["graph_structure_query"],
            "generated_cypher": "MATCH (target:KnowledgePoint {id: 1}) RETURN target",
            "query_modes": ["graph_tools"],
            "matched_point_ids": [1],
            "mode": "neo4j_graphrag_tools",
        }

        result = student_learning_rag.answer_graph_question(
            course_id=int(self.course.id),
            point=self.point_intro,
            question="数组基础的前置知识是什么？",
        )

        self.assertEqual(result["mode"], "neo4j_graphrag_tools")
        self.assertIn("graph_tools", result["query_modes"])
        self.assertTrue(
            any(source.get("retrieval_source") == "text2cypher" for source in result["sources"])
        )

    @patch("platform_ai.rag.student.student_graphrag_runtime.query_graph")
    @patch.object(student_learning_rag, "_ensure_index")
    def test_build_point_support_payload_should_include_graph_query_summary(
        self,
        mock_ensure_index,
        mock_query_graph,
    ):
        """Knowledge-point support payload should surface graph-query summaries for the detail drawer."""
        mock_ensure_index.return_value = self.payload
        mock_query_graph.return_value = {
            "context": "结构化图查询：\n- 数组基础 的前置知识包括：变量与索引。",
            "sources": [
                {
                    "id": "cypher:1:0:graph",
                    "title": "数组基础 · 图关系",
                    "kind": "graph_query",
                    "url": "",
                    "excerpt": "数组基础 的前置知识包括：变量与索引。",
                    "query_mode": "graph_tools",
                    "retrieval_source": "text2cypher",
                }
            ],
            "tools_selected": ["graph_structure_query"],
            "generated_cypher": "MATCH (target:KnowledgePoint {id: 1}) RETURN target",
            "query_modes": ["graph_tools"],
            "matched_point_ids": [1],
            "mode": "neo4j_graphrag_tools",
        }

        result = student_learning_rag.build_point_support_payload(
            course_id=int(self.course.id),
            point=self.point_intro,
        )

        self.assertEqual(result["mode"], "neo4j_graphrag_tools")
        self.assertIn("前置知识", result["summary"])
        self.assertTrue(
            any(source.get("query_mode") == "graph_tools" for source in result["sources"])
        )

    @patch("platform_ai.rag.student.student_graphrag_runtime.query_graph")
    @patch("platform_ai.rag.student.llm_facade")
    @patch.object(student_learning_rag, "_ensure_index")
    def test_answer_course_question_should_merge_course_level_graph_sources(
        self,
        mock_ensure_index,
        mock_llm,
        mock_query_graph,
    ):
        """Course-level GraphRAG answers should keep graph-query evidence even without a focused point."""
        mock_ensure_index.return_value = self.payload
        mock_llm.is_available = False
        mock_query_graph.return_value = {
            "context": "结构化图查询：\n- 数组基础 与 数组遍历 存在 prerequisite 关系。",
            "sources": [
                {
                    "id": "cypher:1:2:graph",
                    "title": "数组基础 · 图关系",
                    "kind": "graph_query",
                    "url": "",
                    "excerpt": "数组基础 与 数组遍历 存在 prerequisite 关系。",
                    "query_mode": "graph_tools",
                    "retrieval_source": "text2cypher",
                }
            ],
            "tools_selected": ["graph_structure_query"],
            "generated_cypher": "MATCH (a:KnowledgePoint)-[:PREREQUISITE]->(b:KnowledgePoint) RETURN a, b",
            "query_modes": ["graph_tools"],
            "matched_point_ids": [1, 2],
            "mode": "neo4j_graphrag_tools",
        }

        result = student_learning_rag.answer_course_question(
            course_id=int(self.course.id),
            question="数组基础和数组遍历是什么关系？",
            seed_point_ids=[1, 2],
        )

        self.assertEqual(result["mode"], "neo4j_graphrag_tools")
        self.assertIn("graph_tools", result["query_modes"])
        self.assertEqual(result["matched_point_ids"], [1, 2])
        self.assertTrue(
            any(source.get("retrieval_source") == "text2cypher" for source in result["sources"])
        )
