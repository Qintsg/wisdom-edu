#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 推理模块。"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, cast

from platform_ai.kt.torch_device import resolve_torch_device
from .mefkt_runtime import (
    CourseQuestionRuntimeBundle,
    _append_history_outcome,
    _build_sorted_history_records,
    _coerce_int,
    _move_bundle_tensors_to_device,
    build_course_runtime_bundle,
)

logger = logging.getLogger(__name__)
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent

if TYPE_CHECKING:
    from models.MEFKT.model import MEFKTSequenceModel
    from torch import Tensor


def _resolve_backend_path(path_value: str | None) -> Path | None:
    """将环境变量中的模型路径统一解析为后端根目录下的绝对路径。"""
    if path_value is None:
        return None
    normalized = str(path_value).strip()
    if not normalized:
        return None
    candidate = Path(normalized)
    if candidate.is_absolute():
        return candidate
    return (BACKEND_ROOT / candidate).resolve()


class MEFKTPredictor:
    """运行时加载并执行 MEFKT 序列预测。"""

    def __init__(self) -> None:
        self._model: MEFKTSequenceModel | None = None
        self._metadata: dict[str, object] = {}
        self._model_path: str | None = None
        self._metadata_path: str | None = None
        self._item_id_to_index: dict[int, int] = {}
        self._index_to_item_id: dict[int, int] = {}
        self._runtime_mode = "legacy"
        self._device = "cpu"
        self._torch_device = None
        self._sequence_state_dict: dict[str, Tensor] = {}
        self._graph_state_dict: dict[str, Tensor] = {}
        self._attribute_state_dict: dict[str, Tensor] = {}
        self._fusion_state_dict: dict[str, Tensor] = {}
        self._course_bundle_cache: dict[int, CourseQuestionRuntimeBundle] = {}

    @property
    def is_loaded(self) -> bool:
        """当前模型是否已加载。"""
        return self._model is not None or bool(self._sequence_state_dict)

    def load_model(self, model_path: str, metadata_path: str | None = None) -> bool:
        """加载保存好的 MEFKT 模型。"""
        try:
            import torch
            from torch import Tensor as TorchTensor
        except ImportError:
            logger.error("PyTorch 未安装，无法加载 MEFKT 模型")
            return False

        from models.MEFKT.model import MEFKTSequenceModel

        model_file = _resolve_backend_path(model_path)
        if model_file is None or not model_file.exists():
            logger.error("MEFKT 模型文件不存在: %s", model_path)
            return False

        metadata_file = (
            _resolve_backend_path(metadata_path) if metadata_path else None
        ) or model_file.with_suffix(".meta.json")
        checkpoint = torch.load(str(model_file), map_location="cpu", weights_only=False)
        metadata_payload = dict(checkpoint.get("metadata") or {})
        runtime_device = resolve_torch_device()
        if metadata_file.exists():
            try:
                metadata_payload = json.loads(metadata_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                logger.warning("MEFKT 元数据解析失败，回退到 checkpoint 内嵌元数据")

        self._metadata = metadata_payload
        self._model_path = str(model_file)
        self._metadata_path = str(metadata_file)
        self._device = runtime_device.label
        self._torch_device = runtime_device.device
        self._course_bundle_cache.clear()

        runtime_schema = str(metadata_payload.get("runtime_schema") or "").strip()
        if runtime_schema == "question_online_v1" and checkpoint.get("graph_state_dict"):
            self._runtime_mode = "question_online"
            self._model = None
            self._item_id_to_index = {}
            self._index_to_item_id = {}
            self._sequence_state_dict = cast(
                dict[str, TorchTensor],
                dict(checkpoint.get("sequence_state_dict") or checkpoint.get("state_dict") or {}),
            )
            self._graph_state_dict = cast(dict[str, TorchTensor], dict(checkpoint.get("graph_state_dict") or {}))
            self._attribute_state_dict = cast(dict[str, TorchTensor], dict(checkpoint.get("attribute_state_dict") or {}))
            self._fusion_state_dict = cast(dict[str, TorchTensor], dict(checkpoint.get("fusion_state_dict") or {}))
            logger.info(
                "MEFKT 题目级在线模型加载成功: dataset=%s, device=%s, path=%s",
                metadata_payload.get("training_dataset"),
                self._device,
                model_file,
            )
            return True

        item_ids = [int(item_id) for item_id in metadata_payload.get("item_ids", [])]
        item_count = int(metadata_payload.get("item_count") or len(item_ids))
        embedding_dim = int(metadata_payload.get("embedding_dim") or 256)
        num_heads = int(metadata_payload.get("num_heads") or 4)
        head_dim = int(metadata_payload.get("head_dim") or 32)
        if item_count <= 0:
            logger.error("MEFKT 元数据缺少有效 item_count")
            return False
        if not item_ids:
            item_ids = list(range(item_count))

        model = MEFKTSequenceModel(
            item_count=item_count,
            item_embedding_dim=embedding_dim,
            num_heads=num_heads,
            head_dim=head_dim,
        ).to(runtime_device.device)
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()

        self._runtime_mode = "legacy"
        self._model = model
        self._item_id_to_index = {int(item_id): index for index, item_id in enumerate(item_ids)}
        self._index_to_item_id = {index: int(item_id) for index, item_id in enumerate(item_ids)}
        self._sequence_state_dict = {}
        self._graph_state_dict = {}
        self._attribute_state_dict = {}
        self._fusion_state_dict = {}
        logger.info(
            "MEFKT 旧版模型加载成功: items=%d, device=%s, path=%s",
            item_count,
            self._device,
            model_file,
        )
        return True

    def _build_history_tensors_legacy(
        self,
        answer_history: list[dict[str, object]],
    ) -> tuple[list[int], list[int], list[float], int]:
        """将旧版知识点历史转成模型输入格式。"""
        sortable_records = _build_sorted_history_records(answer_history)

        history_indices: list[int] = []
        history_correct: list[int] = []
        history_gap_hours: list[float] = []
        recognized_count = 0
        previous_time: datetime | None = None
        for _, current_time, record in sortable_records:
            item_id_raw = record.get("knowledge_point_id")
            if item_id_raw is None:
                continue
            item_id = int(str(item_id_raw))
            if item_id not in self._item_id_to_index:
                continue
            recognized_count += 1
            history_indices.append(self._item_id_to_index[item_id])
            previous_time = _append_history_outcome(
                history_correct=history_correct,
                history_gap_hours=history_gap_hours,
                record=record,
                current_time=current_time,
                previous_time=previous_time,
            )
        return history_indices, history_correct, history_gap_hours, recognized_count

    def _build_course_runtime_bundle(self, course_id: int) -> CourseQuestionRuntimeBundle:
        """基于课程题目、知识图谱与资源关系构建题目级在线特征。"""
        if course_id in self._course_bundle_cache:
            return self._course_bundle_cache[course_id]
        bundle = build_course_runtime_bundle(course_id)
        self._course_bundle_cache[course_id] = bundle
        return bundle

    def _resolve_runtime_history_index(
        self,
        bundle: CourseQuestionRuntimeBundle,
        record: dict[str, object],
    ) -> int | None:
        """将题目级或知识点级历史记录映射到课程题图节点。"""
        question_id_raw = record.get("question_id")
        if question_id_raw is not None:
            question_id = int(str(question_id_raw))
            if question_id in bundle.question_id_to_index:
                return bundle.question_id_to_index[question_id]
        point_id_raw = record.get("knowledge_point_id")
        if point_id_raw is not None:
            point_id = int(str(point_id_raw))
            return bundle.representative_question_index.get(point_id)
        return None

    def _build_history_tensors_runtime(
        self,
        answer_history: list[dict[str, object]],
        bundle: CourseQuestionRuntimeBundle,
    ) -> tuple[list[int], list[int], list[float], int]:
        """将题目级在线部署历史转成模型输入格式。"""
        sortable_records = _build_sorted_history_records(answer_history)

        history_indices: list[int] = []
        history_correct: list[int] = []
        history_gap_hours: list[float] = []
        recognized_count = 0
        previous_time: datetime | None = None
        for _, current_time, record in sortable_records:
            item_index = self._resolve_runtime_history_index(bundle, record)
            if item_index is None:
                continue
            recognized_count += 1
            history_indices.append(int(item_index))
            previous_time = _append_history_outcome(
                history_correct=history_correct,
                history_gap_hours=history_gap_hours,
                record=record,
                current_time=current_time,
                previous_time=previous_time,
            )
        return history_indices, history_correct, history_gap_hours, recognized_count

    def _predict_legacy(
        self,
        answer_history: list[dict[str, object]],
        knowledge_point_ids: list[int] | None = None,
    ) -> dict[str, object]:
        """执行旧版知识点级 checkpoint 推理。"""
        import torch

        assert self._model is not None
        device = self._torch_device or torch.device("cpu")
        history_indices, history_correct, history_gap_hours, recognized_count = self._build_history_tensors_legacy(answer_history)
        target_ids = set(int(item_id) for item_id in (knowledge_point_ids or []))
        if not target_ids:
            for record in answer_history:
                current_item_id = record.get("knowledge_point_id")
                if current_item_id is not None:
                    target_ids.add(int(str(current_item_id)))
        known_target_ids = [item_id for item_id in sorted(target_ids) if item_id in self._item_id_to_index]
        if not known_target_ids:
            return {
                "predictions": {},
                "confidence": 0.0,
                "model_type": "mefkt",
                "analysis": "MEFKT 未识别到可用知识点，无法输出掌握度预测",
            }

        candidate_tensor = torch.tensor(
            [self._item_id_to_index[item_id] for item_id in known_target_ids],
            dtype=torch.long,
            device=device,
        )
        if history_indices:
            history_index_tensor = torch.tensor(history_indices, dtype=torch.long, device=device)
            history_correct_tensor = torch.tensor(history_correct, dtype=torch.long, device=device)
            history_gap_tensor = torch.tensor(history_gap_hours, dtype=torch.float32, device=device)
            probability_tensor = self._model.predict_candidate(
                history_item_indices=history_index_tensor,
                history_correct_flags=history_correct_tensor,
                history_time_gaps=history_gap_tensor,
                candidate_item_indices=candidate_tensor,
            )
        else:
            probability_tensor = torch.full((len(known_target_ids),), 0.25, dtype=torch.float32, device=device)

        predictions = {
            item_id: round(float(probability), 4)
            for item_id, probability in zip(known_target_ids, probability_tensor.detach().cpu().tolist(), strict=True)
        }
        history_coverage = recognized_count / max(len(answer_history), 1)
        confidence = min(0.9, 0.42 + len(history_indices) / 30.0 * 0.28 + history_coverage * 0.2)
        return {
            "predictions": predictions,
            "confidence": round(confidence, 3),
            "model_type": "mefkt_real",
            "analysis": f"MEFKT 推理完成：识别 {recognized_count}/{len(answer_history)} 条有效交互，输出 {len(predictions)} 个知识点掌握度",
        }

    def _predict_question_online(
        self,
        *,
        answer_history: list[dict[str, object]],
        knowledge_point_ids: list[int] | None,
        course_id: int,
    ) -> dict[str, object]:
        """执行题目级在线部署预测，并聚合回知识点掌握度。"""
        import torch
        from models.MEFKT.model import (
            GraphContrastiveEncoder,
            LinearAlignmentFusion,
            MEFKTSequenceModel,
            MultiAttributeEncoder,
            load_compatible_state,
        )

        device = self._torch_device or torch.device("cpu")
        bundle = self._build_course_runtime_bundle(course_id)
        feature_dim = _coerce_int(self._metadata.get("feature_dim"), int(bundle.node_feature_matrix.size(1)))
        relation_dim = _coerce_int(self._metadata.get("relation_dim"), int(bundle.relation_stats_matrix.size(1)))
        align_dim = _coerce_int(self._metadata.get("align_dim"), 128)
        hidden_dim = _coerce_int(self._metadata.get("hidden_dim"), 128)
        num_heads = _coerce_int(self._metadata.get("num_heads"), 4)
        head_dim = _coerce_int(self._metadata.get("head_dim"), 32)
        embedding_dim = _coerce_int(self._metadata.get("embedding_dim"), align_dim * 2)
        type_mapping = cast(dict[str, int], self._metadata.get("type_mapping") or {"unknown": 0})

        graph_encoder = GraphContrastiveEncoder(feature_dim, hidden_dim, align_dim).to(device)
        attribute_encoder = MultiAttributeEncoder(feature_dim, max(type_mapping.values(), default=0) + 1, align_dim, relation_dim=relation_dim).to(device)
        fusion_layer = LinearAlignmentFusion(align_dim, align_dim, align_dim).to(device)
        load_compatible_state(graph_encoder, self._graph_state_dict)
        load_compatible_state(attribute_encoder, self._attribute_state_dict)
        load_compatible_state(fusion_layer, self._fusion_state_dict)
        graph_encoder.eval()
        attribute_encoder.eval()
        fusion_layer.eval()

        (
            node_feature_matrix,
            relation_stats_matrix,
            adjacency_matrix,
            difficulty_vector,
            response_time_vector,
            exercise_type_vector,
        ) = _move_bundle_tensors_to_device(bundle, device)

        with torch.no_grad():
            struct_embedding = graph_encoder.encode(node_feature_matrix, adjacency_matrix)
            attribute_result = attribute_encoder(
                node_feature_matrix=node_feature_matrix,
                difficulty_vector=difficulty_vector,
                response_time_vector=response_time_vector,
                exercise_type_vector=exercise_type_vector,
                exercise_adjacency=adjacency_matrix,
                relation_stats_matrix=relation_stats_matrix,
            )
            fused_embedding = fusion_layer(struct_embedding, attribute_result.embedding)

        sequence_embedding_dim = int(fused_embedding.size(1))
        if embedding_dim != sequence_embedding_dim:
            logger.warning(
                "MEFKT 运行时融合维度与元数据不一致，将使用运行时维度: metadata=%d, runtime=%d",
                embedding_dim,
                sequence_embedding_dim,
            )

        sequence_model = MEFKTSequenceModel(
            item_count=len(bundle.question_ids),
            item_embedding_dim=sequence_embedding_dim,
            num_heads=num_heads,
            head_dim=head_dim,
            pretrained_item_embedding=fused_embedding.detach().cpu(),
        ).to(device)
        load_compatible_state(sequence_model, self._sequence_state_dict)
        sequence_model.eval()

        history_indices, history_correct, history_gap_hours, recognized_count = self._build_history_tensors_runtime(answer_history, bundle)
        target_point_ids = set(int(point_id) for point_id in (knowledge_point_ids or []))
        if not target_point_ids:
            for record in answer_history:
                point_id_raw = record.get("knowledge_point_id")
                if point_id_raw is not None:
                    target_point_ids.add(int(str(point_id_raw)))
                question_id_raw = record.get("question_id")
                if question_id_raw is not None:
                    target_point_ids.update(bundle.question_to_points.get(int(str(question_id_raw)), []))
        if not target_point_ids:
            target_point_ids.update(bundle.point_to_question_indices.keys())
        candidate_question_indices = sorted(
            {
                question_index
                for point_id in target_point_ids
                for question_index in bundle.point_to_question_indices.get(int(point_id), [])
            }
        )
        if not candidate_question_indices:
            return {
                "predictions": {},
                "confidence": 0.0,
                "model_type": "mefkt_question_online",
                "analysis": "当前课程题图中未找到可关联到目标知识点的题目节点",
            }

        candidate_tensor = torch.tensor(candidate_question_indices, dtype=torch.long, device=device)
        if history_indices:
            probability_tensor = sequence_model.predict_candidate(
                history_item_indices=torch.tensor(history_indices, dtype=torch.long, device=device),
                history_correct_flags=torch.tensor(history_correct, dtype=torch.long, device=device),
                history_time_gaps=torch.tensor(history_gap_hours, dtype=torch.float32, device=device),
                candidate_item_indices=candidate_tensor,
            )
        else:
            probability_tensor = torch.full((len(candidate_question_indices),), 0.28, dtype=torch.float32, device=device)

        per_question_predictions = {
            bundle.question_ids[question_index]: float(probability)
            for question_index, probability in zip(
                candidate_question_indices,
                probability_tensor.detach().cpu().tolist(),
                strict=True,
            )
        }
        predictions: dict[int, float] = {}
        for point_id in sorted(target_point_ids):
            point_question_indices = bundle.point_to_question_indices.get(int(point_id), [])
            if not point_question_indices:
                continue
            probabilities = [
                per_question_predictions.get(bundle.question_ids[question_index])
                for question_index in point_question_indices
                if bundle.question_ids[question_index] in per_question_predictions
            ]
            if not probabilities:
                representative_index = bundle.representative_question_index.get(int(point_id))
                if representative_index is not None:
                    representative_question_id = bundle.question_ids[representative_index]
                    representative_probability = per_question_predictions.get(representative_question_id, 0.35)
                    probabilities = [representative_probability]
            predictions[int(point_id)] = round(sum(probabilities) / max(len(probabilities), 1), 4)

        history_coverage = recognized_count / max(len(answer_history), 1)
        candidate_coverage = len(candidate_question_indices) / max(len(bundle.question_ids), 1)
        confidence = min(0.93, 0.46 + len(history_indices) / 24.0 * 0.24 + history_coverage * 0.14 + candidate_coverage * 0.08)
        return {
            "predictions": predictions,
            "confidence": round(confidence, 3),
            "model_type": "mefkt_question_online",
            "question_predictions": {
                question_id: round(probability, 4) for question_id, probability in per_question_predictions.items()
            },
            "analysis": f"MEFKT 题目级在线部署完成：课程题图 {len(bundle.question_ids)} 题，识别 {recognized_count}/{len(answer_history)} 条有效交互，聚合输出 {len(predictions)} 个知识点掌握度",
        }

    def predict(
        self,
        answer_history: list[dict[str, object]],
        knowledge_point_ids: list[int] | None = None,
        course_id: int | None = None,
    ) -> dict[str, object]:
        """根据答题历史预测知识点掌握度。"""
        if not self.is_loaded:
            raise RuntimeError("MEFKT 模型未加载，请先调用 load_model()")
        if self._runtime_mode == "question_online":
            if course_id is None:
                raise ValueError("题目级在线部署模式需要传入 course_id")
            return self._predict_question_online(
                answer_history=answer_history,
                knowledge_point_ids=knowledge_point_ids,
                course_id=int(course_id),
            )
        assert self._model is not None
        return self._predict_legacy(answer_history, knowledge_point_ids)

    def get_info(self) -> dict[str, object]:
        """输出当前加载状态与元数据摘要。"""
        return {
            "loaded": self.is_loaded,
            "runtime_mode": self._runtime_mode,
            "device": self._device,
            "model_path": self._model_path,
            "metadata_path": self._metadata_path,
            "training_mode": self._metadata.get("training_mode"),
            "training_dataset": self._metadata.get("training_dataset"),
            "runtime_schema": self._metadata.get("runtime_schema"),
            "item_count": self._metadata.get("item_count"),
            "best_metrics": self._metadata.get("best_metrics"),
            "paper_title": self._metadata.get("paper_title"),
            "paper_doi": self._metadata.get("paper_doi"),
        }


mefkt_predictor = MEFKTPredictor()


def auto_load_model() -> bool:
    """从环境变量或默认路径自动加载 MEFKT 模型。"""
    from .mefkt_loader import auto_load_mefkt_model

    return auto_load_mefkt_model(mefkt_predictor, BACKEND_ROOT, os.environ)
