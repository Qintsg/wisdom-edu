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

class MEFKTServiceTests(SimpleTestCase):
    """Cover MEFKT model registration, metadata and runtime loading."""

    def test_kt_service_model_info_should_expose_mefkt_config(self):
        """KT model-info payload should list MEFKT as an optional model."""
        from ai_services.services.kt_service import KnowledgeTracingService

        service = KnowledgeTracingService(
            enabled_models=["mefkt"],
            fusion_weights={"mefkt": 1.0},
            prediction_mode="single",
        )

        info = service.get_model_info()
        self.assertNotIn("dkt", info["models"])
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


class KTSyntheticDataRealismTests(SimpleTestCase):
    """Validate that synthetic KT trajectories preserve expected structure."""

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
