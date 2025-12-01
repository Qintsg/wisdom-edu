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
from platform_ai.rag import student_learning_rag
from platform_ai.rag.runtime import (
    COURSE_RETRIEVAL_MODE,
    GraphRAGSearchHit,
    TokenHashEmbedder,
    student_graphrag_runtime,
)
from tools.dkt_training import _build_kp_profiles, _simulate_student_sequence
from users.models import User


class MEFKTServiceTests(SimpleTestCase):
    """Cover MEFKT model registration, metadata and runtime loading."""

    def test_kt_service_model_info_should_expose_mefkt_config(self):
        """KT model-info payload should list MEFKT as an optional model."""
        from ai_services.services.kt_service import KnowledgeTracingService

        service = KnowledgeTracingService(
            enabled_models=["dkt", "mefkt"],
            fusion_weights={"dkt": 0.5, "mefkt": 0.5},
            prediction_mode="fusion",
        )

        info = service.get_model_info()
        self.assertIn("mefkt", info["models"])
        self.assertEqual(
            info["models"]["mefkt"]["paper_doi"], "10.11896/jsjkx.250700092"
        )
        self.assertTrue(info["models"]["mefkt"]["is_enabled"])

    def test_mefkt_predictor_should_load_checkpoint_and_return_predictions(self):
        """A minimal MEFKT checkpoint should be loadable for KT prediction."""
        import json
        import torch
        from ai_services.services.mefkt_inference import MEFKTPredictor
        from models.MEFKT.model import MEFKTSequenceModel

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            model_path = temp_path / "mefkt_demo.pt"
            meta_path = temp_path / "mefkt_demo.meta.json"

            model = MEFKTSequenceModel(
                item_count=2,
                item_embedding_dim=8,
                num_heads=2,
                head_dim=4,
            )
            with torch.no_grad():
                model.item_embedding.weight.fill_(0.25)

            metadata = {
                "item_count": 2,
                "item_ids": [101, 102],
                "item_names": ["知识点A", "知识点B"],
                "embedding_dim": 8,
                "num_heads": 2,
                "head_dim": 4,
                "training_mode": "knowledge_point",
                "paper_title": "融合多视角习题表征与遗忘机制的深度知识追踪",
                "paper_doi": "10.11896/jsjkx.250700092",
            }
            torch.save({"state_dict": model.state_dict(), "metadata": metadata}, model_path)
            meta_path.write_text(json.dumps(metadata, ensure_ascii=False), encoding="utf-8")

            predictor = MEFKTPredictor()
            self.assertTrue(predictor.load_model(str(model_path), str(meta_path)))

            result = predictor.predict(
                answer_history=[
                    {
                        "knowledge_point_id": 101,
                        "correct": 1,
                        "timestamp": "2026-04-01T08:00:00",
                    },
                    {
                        "knowledge_point_id": 101,
                        "correct": 0,
                        "timestamp": "2026-04-03T09:00:00",
                    },
                ],
                knowledge_point_ids=[101, 102],
            )

            # 显式收窄预测映射，避免测试场景中的 object 索引告警。
            predictions = cast(dict[int, float], result["predictions"])
            self.assertEqual(result["model_type"], "mefkt_real")
            self.assertIn(101, predictions)
            self.assertIn(102, predictions)
            self.assertGreater(result["confidence"], 0)

    def test_mefkt_predictor_should_support_question_online_runtime(self):
        """Question-online runtime metadata should load and predict through the rebuilt course graph path."""
        import json
        import torch
        from ai_services.services.mefkt_inference import (
            CourseQuestionRuntimeBundle,
            MEFKTPredictor,
        )
        from models.MEFKT.model import (
            GraphContrastiveEncoder,
            LinearAlignmentFusion,
            MEFKTSequenceModel,
            MultiAttributeEncoder,
            NODE_FEATURE_SCHEMA,
            QUESTION_TYPE_VOCAB,
            RELATION_STAT_SCHEMA,
        )

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            model_path = temp_path / "mefkt_question_online.pt"
            meta_path = temp_path / "mefkt_question_online.meta.json"
            feature_dim = len(NODE_FEATURE_SCHEMA)
            relation_dim = len(RELATION_STAT_SCHEMA)
            align_dim = 8
            hidden_dim = 8
            num_heads = 2
            head_dim = 4
            type_count = max(QUESTION_TYPE_VOCAB.values()) + 1

            graph_encoder = GraphContrastiveEncoder(feature_dim, hidden_dim, align_dim)
            attribute_encoder = MultiAttributeEncoder(
                feature_dim,
                type_count,
                align_dim,
                relation_dim=relation_dim,
            )
            fusion_layer = LinearAlignmentFusion(align_dim, align_dim, align_dim)
            sequence_model = MEFKTSequenceModel(
                item_count=2,
                item_embedding_dim=align_dim * 2,
                num_heads=num_heads,
                head_dim=head_dim,
            )

            metadata = {
                "model_name": "MEFKT",
                "runtime_schema": "question_online_v1",
                "training_mode": "public_pretrain_question_online",
                "training_dataset": "assist2017",
                "item_count": 2,
                "item_ids": [201, 202],
                "item_names": ["题目A", "题目B"],
                "feature_dim": feature_dim,
                "relation_dim": relation_dim,
                "embedding_dim": align_dim * 2,
                "num_heads": num_heads,
                "head_dim": head_dim,
                "hidden_dim": hidden_dim,
                "align_dim": align_dim,
                "type_mapping": QUESTION_TYPE_VOCAB,
                "paper_title": "融合多视角习题表征与遗忘机制的深度知识追踪",
                "paper_doi": "10.11896/jsjkx.250700092",
            }
            torch.save(
                {
                    "state_dict": sequence_model.state_dict(),
                    "sequence_state_dict": sequence_model.state_dict(),
                    "graph_state_dict": graph_encoder.state_dict(),
                    "attribute_state_dict": attribute_encoder.state_dict(),
                    "fusion_state_dict": fusion_layer.state_dict(),
                    "metadata": metadata,
                },
                model_path,
            )
            meta_path.write_text(
                json.dumps(metadata, ensure_ascii=False),
                encoding="utf-8",
            )

            runtime_bundle = CourseQuestionRuntimeBundle(
                question_ids=[201, 202],
                question_id_to_index={201: 0, 202: 1},
                question_to_points={201: [301], 202: [302]},
                point_to_question_indices={301: [0], 302: [1]},
                representative_question_index={301: 0, 302: 1},
                node_feature_matrix=torch.full((2, feature_dim), 0.25, dtype=torch.float32),
                relation_stats_matrix=torch.full((2, relation_dim), 0.5, dtype=torch.float32),
                adjacency_matrix=torch.tensor([[0.0, 1.0], [1.0, 0.0]], dtype=torch.float32),
                difficulty_vector=torch.tensor([0.3, 0.6], dtype=torch.float32),
                response_time_vector=torch.tensor([0.4, 0.7], dtype=torch.float32),
                exercise_type_vector=torch.tensor([1, 1], dtype=torch.long),
            )

            predictor = MEFKTPredictor()
            self.assertTrue(predictor.load_model(str(model_path), str(meta_path)))
            self.assertEqual(predictor.get_info()["runtime_mode"], "question_online")

            with patch.object(
                predictor,
                "_build_course_runtime_bundle",
                return_value=runtime_bundle,
            ):
                result = predictor.predict(
                    answer_history=[
                        {
                            "question_id": 201,
                            "knowledge_point_id": 301,
                            "correct": 1,
                            "timestamp": "2026-04-01T08:00:00",
                        },
                        {
                            "question_id": 202,
                            "knowledge_point_id": 302,
                            "correct": 0,
                            "timestamp": "2026-04-02T08:00:00",
                        },
                    ],
                    knowledge_point_ids=[301, 302],
                    course_id=999,
                )

            # 显式收窄预测映射，避免测试断言触发容器类型误报。
            predictions = cast(dict[int, float], result["predictions"])
            self.assertEqual(result["model_type"], "mefkt_question_online")
            self.assertIn(301, predictions)
            self.assertIn(302, predictions)
            self.assertTrue(result["question_predictions"])
            self.assertGreater(result["confidence"], 0)

    def test_mefkt_perceived_distance_should_increase_with_longer_gap(self):
        """Longer time gaps should lead to larger forgetting-aware perceived distance."""
        import torch
        from models.MEFKT.model import MEFKTSequenceModel

        model = MEFKTSequenceModel(
            item_count=2,
            item_embedding_dim=8,
            num_heads=1,
            head_dim=4,
        )

        short_distance = model._perceived_distance(
            history_time_gap=torch.tensor([1.0, 1.0], dtype=torch.float32),
            relevance_score=torch.tensor([[0.5], [0.5]], dtype=torch.float32),
        )
        long_distance = model._perceived_distance(
            history_time_gap=torch.tensor([1.0, 12.0], dtype=torch.float32),
            relevance_score=torch.tensor([[0.5], [0.5]], dtype=torch.float32),
        )
        self.assertGreater(float(long_distance[0, 0]), float(short_distance[0, 0]))


class KTServiceRegressionTests(SimpleTestCase):
    """Cover KT fallback and empty-history regression scenarios."""

    def test_predict_mastery_should_degrade_gracefully_on_model_name_error(self):
        """Recoverable NameError exceptions from model runtimes should fall back to builtin stats."""
        from ai_services.services.kt_service import KnowledgeTracingService

        service = KnowledgeTracingService(
            enabled_models=["mefkt"],
            prediction_mode="single",
        )

        with patch.object(
            service,
            "_predict_with_mefkt",
            side_effect=NameError("Tensor is not defined"),
        ):
            result = service.predict_mastery(
                user_id=7,
                course_id=3,
                answer_history=[
                    {
                        "knowledge_point_id": 101,
                        "correct": 1,
                    }
                ],
                knowledge_points=[101],
            )

        predictions = cast(dict[int, float], result["predictions"])
        self.assertEqual(result["model_type"], "builtin")
        self.assertIn(101, predictions)
        self.assertEqual(result["answer_count"], 1)

    def test_predict_mastery_should_return_course_defaults_without_history(self):
        """Empty-history predictions should expand to course knowledge points instead of returning an empty map."""
        from ai_services.services.kt_service import KnowledgeTracingService

        service = KnowledgeTracingService()

        with patch.object(
            service,
            "_load_course_knowledge_point_ids",
            return_value=[301, 302, 303],
        ) as mocked_loader:
            result = service.predict_mastery(
                user_id=9,
                course_id=12,
                answer_history=[],
            )

        mocked_loader.assert_called_once_with(12)
        self.assertEqual(
            result["predictions"],
            {301: 0.25, 302: 0.25, 303: 0.25},
        )
        self.assertEqual(result["model_type"], "default")
        self.assertEqual(result["answer_count"], 0)
        self.assertIn("默认预测", result["analysis"])


class DKTSyntheticDataRealismTests(SimpleTestCase):
    """Validate that synthetic DKT training data preserves expected structure."""

    def setUp(self):
        """Build a small prerequisite graph that is easy to reason about in tests."""
        self.kp_to_idx = {101: 0, 102: 1, 103: 2, 104: 3}
        self.prereqs = {
            102: [101],
            103: [102],
            104: [102],
        }
        self.metadata = {
            101: {
                "name": "基础概念",
                "order": 1,
                "level": 1,
                "chapter": "第一章",
                "cognitive_dimension": "remember",
                "category": "factual",
                "tags": ["重点"],
                "question_stats": {"total": 4, "easy": 3, "medium": 1, "hard": 0},
            },
            102: {
                "name": "核心应用",
                "order": 2,
                "level": 2,
                "chapter": "第一章",
                "cognitive_dimension": "apply",
                "category": "conceptual",
                "tags": ["重点", "考点"],
                "question_stats": {"total": 5, "easy": 1, "medium": 3, "hard": 1},
            },
            103: {
                "name": "综合分析",
                "order": 3,
                "level": 3,
                "chapter": "第二章",
                "cognitive_dimension": "analyze",
                "category": "procedural",
                "tags": ["难点", "考点"],
                "question_stats": {"total": 6, "easy": 0, "medium": 3, "hard": 3},
            },
            104: {
                "name": "综合练习",
                "order": 4,
                "level": 2,
                "chapter": "第二章",
                "cognitive_dimension": "apply",
                "category": "procedural",
                "tags": ["重点"],
                "question_stats": {"total": 4, "easy": 1, "medium": 2, "hard": 1},
            },
        }

    def _profile(self, *, base_ability, archetype="steady"):
        """Return a deterministic learner profile for sequence simulation checks."""
        return {
            "archetype": archetype,
            "base_ability": base_ability,
            "learning_rate": 0.08,
            "forgetting_rate": 0.02,
            "slip_rate": 0.03,
            "guess_rate": 0.02,
            "review_bias": 0.42,
            "focus_bias": 0.62,
            "fatigue_sensitivity": 0.06,
            "persistence": 0.66,
            "session_span": 8,
        }

    def test_kp_profile_should_reflect_prerequisite_depth_and_item_difficulty(self):
        """Harder downstream points should receive higher synthesized difficulty."""
        profiles, _ = _build_kp_profiles(self.kp_to_idx, self.prereqs, self.metadata)

        self.assertLess(profiles[101]["difficulty"], profiles[102]["difficulty"])
        self.assertLess(profiles[102]["difficulty"], profiles[103]["difficulty"])
        self.assertGreater(profiles[103]["difficulty"], profiles[104]["difficulty"])

    def test_simulated_sequences_should_show_ability_gap_and_revisits(self):
        """Lower-ability learners should revisit more and score worse overall."""
        profiles, children_map = _build_kp_profiles(
            self.kp_to_idx, self.prereqs, self.metadata
        )

        low_result = _simulate_student_sequence(
            kp_to_idx=self.kp_to_idx,
            kp_profiles=profiles,
            children_map=children_map,
            rng=Random(7),
            seq_len=72,
            student_profile=self._profile(base_ability=0.28, archetype="struggling"),
        )
        high_result = _simulate_student_sequence(
            kp_to_idx=self.kp_to_idx,
            kp_profiles=profiles,
            children_map=children_map,
            rng=Random(7),
            seq_len=72,
            student_profile=self._profile(base_ability=0.76, archetype="advanced"),
        )

        self.assertGreater(high_result["accuracy"], low_result["accuracy"] + 0.08)
        self.assertGreater(low_result["revisit_ratio"], 0.2)
        self.assertGreaterEqual(high_result["sessions"], 2)
        self.assertGreaterEqual(len(set(high_result["kp_indices"])), 3)


class WebSearchServiceTests(SimpleTestCase):
    """Cover provider ordering and redirect filtering for resource search."""

    @patch("ai_services.services.web_search_service.requests.get")
    def test_search_with_baidu_should_resolve_redirect_and_filter_domain(
        self, mock_get
    ):
        """Baidu redirect links should resolve to the expected destination domain."""
        search_response = Mock()
        search_response.raise_for_status.return_value = None
        search_response.text = (
            "<html><body>"
            '<a href="https://www.baidu.com/link?url=demo123">大数据技术基础 - 菜鸟教程</a>'
            '<a href="https://www.baidu.com/link?url=other456">无关结果</a>'
            "</body></html>"
        )

        redirect_response = Mock()
        redirect_response.url = "https://www.runoob.com/hadoop/hadoop-tutorial.html"
        redirect_response.close.return_value = None

        other_redirect_response = Mock()
        other_redirect_response.url = "https://example.com/other"
        other_redirect_response.close.return_value = None

        mock_get.side_effect = [
            search_response,
            redirect_response,
            other_redirect_response,
        ]

        results = _search_with_provider(
            provider_name="baidu",
            query="大数据技术基础 site:runoob.com",
            expected_domain="runoob.com",
            max_results=3,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["url"], "https://www.runoob.com/hadoop/hadoop-tutorial.html"
        )
        self.assertIn("菜鸟教程", results[0]["title"])

    @patch(
        "ai_services.services.web_search_service._is_accessible_url", return_value=True
    )
    @patch("ai_services.services.web_search_service._search_with_provider")
    def test_search_learning_resources_should_use_configured_engines_in_order(
        self, mock_search_with_provider, _mock_accessible
    ):
        """Configured providers should be queried in priority order until one succeeds."""
        provider_calls = []
        configured_providers = [name for name, _ in SEARCH_PROVIDERS]
        primary_provider = configured_providers[0]
        fallback_provider = configured_providers[1]

        def side_effect(provider_name, query, expected_domain, max_results):
            """Return a single mocked hit only for the configured fallback provider."""
            # 显式消费关键字参数，保留真实调用签名并避免未使用形参告警。
            _ = (query, expected_domain, max_results)
            provider_calls.append(provider_name)
            if provider_name == primary_provider:
                return []
            if provider_name == fallback_provider:
                return [
                    {
                        "title": "大数据技术基础 - B站讲解",
                        "url": "https://www.bilibili.com/video/BV1demo",
                        "snippet": "示例摘要",
                    }
                ]
            return []

        mock_search_with_provider.side_effect = side_effect

        results = search_learning_resources(
            point_name="大数据技术基础",
            course_name="大数据技术与应用",
            count=1,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["source"], "bilibili.com")
        self.assertEqual(provider_calls[:2], [primary_provider, fallback_provider])
        self.assertEqual(set(provider_calls), {primary_provider, fallback_provider})


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


class StudentLearningRAGServiceTests(SimpleTestCase):
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

        class StubQdrantClient:
            """轻量 Qdrant stub，避免测试依赖真实向量服务。"""

            def __init__(self):
                self.created_collections = []
                self.upserted_points = []

            def collection_exists(self, collection_name):
                """Pretend that every collection needs to be created for this test."""
                _ = collection_name
                return False

            def create_collection(self, collection_name, vectors_config, on_disk_payload):
                """Record collection creation inputs for later assertions."""
                self.created_collections.append((collection_name, vectors_config, on_disk_payload))
                return True

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


class LLMProviderConfigTests(SimpleTestCase):
    """Validate multi-provider LLM configuration resolution."""

    @override_settings(
        LLM_PROVIDER="doubao",
        LLM_MODEL="ByteDance-Seed-1.8",
        LLM_API_FORMAT="openai-compatible",
        LLM_BASE_URL="",
        ARK_API_KEY="ark-demo-key",
        DOUBAO_API_KEY="",
        DOUBAO_BASE_URL="https://ark.example.com/api/v3",
    )
    def test_llm_service_should_resolve_explicit_doubao_provider(self):
        """Explicit provider settings should prefer provider-specific keys and URLs."""
        from ai_services.services.llm_service import LLMService

        service = LLMService()

        self.assertEqual(service.provider_name, "doubao")
        self.assertEqual(service.resolved_api_key, "ark-demo-key")
        self.assertEqual(service.resolved_base_url, "https://ark.example.com/api/v3")
        self.assertEqual(service.api_format, "openai-compatible")

    @override_settings(
        LLM_PROVIDER="custom",
        LLM_MODEL="campus-private-chat",
        LLM_API_FORMAT="chat-completions",
        LLM_BASE_URL="",
        LLM_API_KEY="",
        CUSTOM_LLM_API_KEY="custom-demo-key",
        CUSTOM_LLM_BASE_URL="https://llm.example.edu/v1",
    )
    def test_llm_service_should_resolve_custom_gateway_fields(self):
        """Custom provider should use dedicated custom gateway credentials when shared fields are blank."""
        from ai_services.services.llm_service import LLMService

        service = LLMService()

        self.assertEqual(service.provider_name, "custom")
        self.assertEqual(service.resolved_api_key, "custom-demo-key")
        self.assertEqual(service.resolved_base_url, "https://llm.example.edu/v1")
        self.assertEqual(service.api_format, "chat-completions")

    @override_settings(
        LLM_PROVIDER="deepseek",
        LLM_MODEL="deepseek-chat",
        DEEPSEEK_API_KEY="deepseek-demo-key",
        DEEPSEEK_BASE_URL="https://api.deepseek.com",
        LLM_HTTP_PROXY="http://127.0.0.1:8080",
        LLM_HTTPS_PROXY="http://127.0.0.1:8443",
        HTTP_PROXY="http://127.0.0.1:8080",
        HTTPS_PROXY="http://127.0.0.1:8443",
    )
    @patch("ai_services.services.llm_service.import_module")
    def test_llm_service_should_attach_https_proxy_to_chat_client(self, mock_import_module):
        """HTTPS model gateways should use the configured HTTPS proxy when initializing ChatOpenAI."""
        from ai_services.services.llm_service import LLMService

        chat_openai_class = Mock(return_value=Mock())
        mock_import_module.return_value = SimpleNamespace(ChatOpenAI=chat_openai_class)

        service = LLMService()
        service._create_llm_client(request_timeout=12, max_retries=0)

        self.assertEqual(service.resolved_proxy_url, "http://127.0.0.1:8443")
        self.assertEqual(
            chat_openai_class.call_args.kwargs["openai_proxy"],
            "http://127.0.0.1:8443",
        )


class LLMServiceRoutingTests(SimpleTestCase):
    """Guard against recursive agent routing in regular LLM calls."""

    @staticmethod
    def _build_service():
        from ai_services.services.llm_service import LLMService

        service = LLMService()
        service._api_key = "demo-key"
        return service

    def test_call_with_fallback_should_skip_agent_for_profile_analysis(self):
        """Profile analysis should go straight to the LLM client instead of the agent."""
        service = self._build_service()
        mock_llm = Mock()
        mock_llm.invoke.return_value = SimpleNamespace(content='{"summary": "直连LLM结果"}')
        service._get_llm = Mock(return_value=mock_llm)
        service._get_agent_service = Mock(
            return_value=Mock(is_available=True, invoke_json=Mock(return_value={"summary": "agent结果"}))
        )

        result = service.call_with_fallback(
            prompt="请生成画像摘要",
            call_type="profile_analysis",
            fallback_response={"summary": "fallback"},
        )

        service._get_agent_service.assert_not_called()
        mock_llm.invoke.assert_called_once()
        self.assertEqual(result["summary"], "直连LLM结果")

    def test_call_with_fallback_should_only_use_agent_for_explicit_agent_calls(self):
        """Only explicitly agent-scoped call types should enter the orchestration layer."""
        service = self._build_service()
        agent_service = Mock(is_available=True)
        agent_service.invoke_json.return_value = {"summary": "agent结果"}
        service._get_agent_service = Mock(return_value=agent_service)
        service._get_llm = Mock()

        result = service.call_with_fallback(
            prompt="请规划多工具任务",
            call_type="agent_orchestration",
            fallback_response={"summary": "fallback"},
        )

        service._get_agent_service.assert_called_once()
        service._get_llm.assert_not_called()
        self.assertEqual(result["summary"], "agent结果")


class LLMServiceLatencyPolicyTests(SimpleTestCase):
    """Ensure latency-sensitive AI routes fail fast instead of hanging behind the gateway."""

    @staticmethod
    def _build_service():
        from ai_services.services.llm_service import LLMService

        service = LLMService()
        service._api_key = "demo-key"
        return service

    def test_call_with_fallback_should_fast_fail_graph_rag_calls_without_repair(self):
        """GraphRAG answers should use a single attempt and skip JSON repair to stay within gateway budgets."""
        service = self._build_service()
        mock_llm = Mock()
        mock_llm.invoke.return_value = SimpleNamespace(content="这不是 JSON")
        service._get_llm_for_policy = Mock(return_value=mock_llm)
        service._repair_json_response = Mock(return_value={"answer": "修复结果"})

        fallback = {"answer": "fallback answer"}
        oversized_prompt = "图谱证据\n" + ("上下文片段-" * 2000)
        result = service.call_with_fallback(
            prompt=oversized_prompt,
            call_type="graph_rag_answer",
            fallback_response=fallback,
        )

        self.assertEqual(result, fallback)
        self.assertEqual(mock_llm.invoke.call_count, 1)
        service._repair_json_response.assert_not_called()
        messages = mock_llm.invoke.call_args.args[0]
        human_prompt = messages[1].content
        self.assertLessEqual(
            len(human_prompt),
            service._resolve_execution_policy("graph_rag_answer").max_prompt_chars,
        )

    def test_call_with_fallback_should_keep_repair_for_profile_analysis(self):
        """Non-latency-sensitive calls should retain JSON repair to preserve richer AI output."""
        service = self._build_service()
        mock_llm = Mock()
        mock_llm.invoke.return_value = SimpleNamespace(content="这不是 JSON")
        service._get_llm_for_policy = Mock(return_value=mock_llm)
        service._repair_json_response = Mock(return_value={"summary": "修复后的画像"})

        result = service.call_with_fallback(
            prompt="请生成学习画像",
            call_type="profile_analysis",
            fallback_response={"summary": "fallback"},
        )

        service._repair_json_response.assert_called_once()
        self.assertEqual(result["summary"], "修复后的画像")

    def test_chat_policy_should_fast_fail_like_other_interactive_routes(self):
        """Chat fallback should stay inside the gateway-safe timeout budget."""
        service = self._build_service()

        policy = service._resolve_execution_policy("chat")

        self.assertEqual(policy.request_timeout_seconds, service.GATEWAY_SAFE_TIMEOUT_SECONDS)
        self.assertEqual(policy.max_retries, 0)
        self.assertEqual(policy.max_attempts, 1)
        self.assertFalse(policy.allow_repair)


class LangChainAgentProxyTests(SimpleTestCase):
    """Ensure the thin agent wrapper reuses the same proxy settings as LLMService."""

    @override_settings(
        LLM_PROVIDER="deepseek",
        LLM_MODEL="deepseek-chat",
        DEEPSEEK_API_KEY="deepseek-demo-key",
        DEEPSEEK_BASE_URL="https://api.deepseek.com",
        LLM_HTTP_PROXY="http://127.0.0.1:8080",
        LLM_HTTPS_PROXY="http://127.0.0.1:8443",
        HTTP_PROXY="http://127.0.0.1:8080",
        HTTPS_PROXY="http://127.0.0.1:8443",
    )
    @patch("langchain_openai.ChatOpenAI")
    def test_agent_service_should_forward_proxy_to_chat_openai(self, mock_chat_openai):
        """Agent ChatOpenAI client should receive the resolved gateway proxy."""
        from platform_ai.llm.agent import get_default_agent_service

        service = get_default_agent_service()
        service._get_model()

        self.assertEqual(
            mock_chat_openai.call_args.kwargs["openai_proxy"],
            "http://127.0.0.1:8443",
        )


class FacadeGraphRAGLLMTests(SimpleTestCase):
    """Verify the custom GraphRAG adapter now targets the V2 LLM interface."""

    def test_facade_graphrag_llm_should_instantiate_without_legacy_warning(self):
        """Instantiation should no longer trigger the deprecated LLMInterface warning."""
        from neo4j_graphrag.llm import LLMInterfaceV2
        from platform_ai.rag.runtime import FacadeGraphRAGLLM

        with patch("neo4j_graphrag.llm.base.logger.warning") as mock_warning:
            llm = FacadeGraphRAGLLM()

        self.assertIsInstance(llm, LLMInterfaceV2)
        mock_warning.assert_not_called()

    def test_facade_graphrag_llm_should_accept_v2_message_lists(self):
        """The adapter should support V2-style message arrays in addition to legacy string prompts."""
        from platform_ai.rag.runtime import FacadeGraphRAGLLM

        call_with_fallback = Mock(return_value={"content": "MATCH (n) RETURN n LIMIT 5"})
        mocked_facade = SimpleNamespace(
            is_available=True,
            service=SimpleNamespace(model_name="qwen-plus"),
            call_with_fallback=call_with_fallback,
        )

        with patch("platform_ai.rag.runtime.llm_facade", new=mocked_facade):
            llm = FacadeGraphRAGLLM()
            response = llm.invoke(
                [{"role": "user", "content": "请根据课程图谱生成 Cypher"}],
                response_format={"type": "json_object"},
            )

        self.assertEqual(response.content, "MATCH (n) RETURN n LIMIT 5")
        self.assertEqual(
            call_with_fallback.call_args.kwargs["call_type"],
            "graph_rag_text2cypher",
        )
