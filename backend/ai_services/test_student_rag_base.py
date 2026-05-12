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

class StudentLearningRAGFixture(SimpleTestCase):
    """Cover the rebuilt student GraphRAG service with course-scoped fixtures."""

    def setUp(self):
        """Prepare a synthetic GraphRAG payload and lightweight node/resource doubles."""
        self.course = SimpleNamespace(id=101, name="GraphRAG 测试课程")
        self.point_intro = SimpleNamespace(
            id=1,
            name="数组基础",
            introduction="数组基础是后续遍历与查找操作的前置知识。",
            description="介绍数组的定义、结构和基本访问方式。",
            chapter="第一章",
        )
        self.point_traverse = SimpleNamespace(
            id=2,
            name="数组遍历",
            introduction="数组遍历依赖数组基础，用于后续查找与统计。",
            description="理解顺序遍历和常见循环写法。",
            chapter="第一章",
        )
        self.resource = SimpleNamespace(
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
        self.payload = {
            "course_id": self.course.id,
            "index_type": "native_graphrag_v1",
            "entities": [
                {
                    "id": "kp:1",
                    "entity_type": "knowledge_point",
                    "title": "数组基础",
                    "summary": "数组基础是前置知识，重点理解索引和访问方式。",
                    "url": "",
                    "metadata": {"knowledge_point_id": 1, "chapter": "第一章", "tags": ["基础"]},
                },
                {
                    "id": "kp:2",
                    "entity_type": "knowledge_point",
                    "title": "数组遍历",
                    "summary": "数组遍历依赖数组基础，常见写法包括 for 循环。",
                    "url": "",
                    "metadata": {"knowledge_point_id": 2, "chapter": "第一章", "tags": ["遍历"]},
                },
                {
                    "id": "resource:11",
                    "entity_type": "resource",
                    "title": "数组入门视频",
                    "summary": "讲解数组概念和遍历的课程资源。",
                    "url": "https://example.com/array-video",
                    "metadata": {"resource_id": 11, "knowledge_point_ids": [1, 2], "chapter": "1.1"},
                },
            ],
            "relationships": [
                {
                    "source": "kp:1",
                    "target": "kp:2",
                    "relation_type": "prerequisite",
                    "weight": 1.0,
                    "metadata": {},
                },
                {
                    "source": "kp:1",
                    "target": "resource:11",
                    "relation_type": "supported_by",
                    "weight": 0.8,
                    "metadata": {},
                },
                {
                    "source": "kp:2",
                    "target": "resource:11",
                    "relation_type": "supported_by",
                    "weight": 0.8,
                    "metadata": {},
                },
            ],
            "communities": [
                {
                    "id": "community:1",
                    "entity_ids": ["kp:1", "kp:2", "resource:11"],
                    "entity_count": 3,
                    "top_entities": ["kp:1", "kp:2"],
                    "themes": ["数组", "遍历"],
                }
            ],
            "community_reports": [
                {
                    "community_id": "community:1",
                    "title": "社区报告 1",
                    "summary": "该社区围绕数组基础、数组遍历组织，主题集中在数组与遍历。",
                    "themes": ["数组", "遍历"],
                    "top_entities": [
                        {"id": "kp:1", "title": "数组基础", "entity_type": "knowledge_point"},
                        {"id": "kp:2", "title": "数组遍历", "entity_type": "knowledge_point"},
                    ],
                    "relation_breakdown": {"prerequisite": 1, "supported_by": 2},
                }
            ],
            "documents": [
                {
                    "id": "kp:1",
                    "kind": "knowledge_point",
                    "title": "数组基础",
                    "content": "数组基础是后续遍历的前置知识。",
                    "url": "",
                    "metadata": {"knowledge_point_id": 1},
                },
                {
                    "id": "kp:2",
                    "kind": "knowledge_point",
                    "title": "数组遍历",
                    "content": "数组遍历常用 for 循环与索引访问。",
                    "url": "",
                    "metadata": {"knowledge_point_id": 2},
                },
                {
                    "id": "resource:11",
                    "kind": "resource",
                    "title": "数组入门视频",
                    "content": "讲解数组概念、索引访问和基础遍历。",
                    "url": "https://example.com/array-video",
                    "metadata": {"resource_id": 11, "knowledge_point_ids": [1, 2]},
                },
                {
                    "id": "community:1",
                    "kind": "community_report",
                    "title": "社区报告 1",
                    "content": "该社区围绕数组基础与数组遍历展开。",
                    "url": "",
                    "metadata": {"community_id": "community:1", "entity_ids": ["kp:1", "kp:2", "resource:11"]},
                },
            ],
        }
