"""MEFKT 题目级在线推理执行器。"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from ai_services.services.mefkt_runtime import (
    CourseQuestionRuntimeBundle,
    _coerce_int,
    _move_bundle_tensors_to_device,
)

if TYPE_CHECKING:
    from torch import Tensor, device as TorchDevice


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QuestionOnlinePredictionInput:
    """题目级在线预测所需的运行时状态。"""

    answer_history: list[dict[str, object]]
    knowledge_point_ids: list[int] | None
    metadata: dict[str, object]
    sequence_state_dict: dict[str, Tensor]
    graph_state_dict: dict[str, Tensor]
    attribute_state_dict: dict[str, Tensor]
    fusion_state_dict: dict[str, Tensor]
    bundle: CourseQuestionRuntimeBundle
    history_indices: list[int]
    history_correct: list[int]
    history_gap_hours: list[float]
    recognized_count: int
    device: TorchDevice | str


@dataclass(frozen=True)
class QuestionOnlineModelBundle:
    """题目级在线推理临时模型。"""

    sequence_model: object
    sequence_embedding_dim: int


def predict_question_online(input_payload: QuestionOnlinePredictionInput) -> dict[str, object]:
    """执行题目级在线部署预测，并聚合回知识点掌握度。"""
    import torch

    model_bundle = _build_online_model_bundle(input_payload)
    target_point_ids = _resolve_target_point_ids(input_payload)
    candidate_question_indices = _resolve_candidate_question_indices(
        target_point_ids,
        input_payload.bundle,
    )
    if not candidate_question_indices:
        return _empty_question_online_response()

    probability_tensor = _predict_candidate_questions(
        input_payload=input_payload,
        sequence_model=model_bundle.sequence_model,
        candidate_question_indices=candidate_question_indices,
        torch_module=torch,
    )
    per_question_predictions = _build_per_question_predictions(
        input_payload.bundle,
        candidate_question_indices,
        probability_tensor,
    )
    predictions = _aggregate_point_predictions(
        bundle=input_payload.bundle,
        target_point_ids=target_point_ids,
        per_question_predictions=per_question_predictions,
    )
    return _question_online_response(
        input_payload=input_payload,
        candidate_question_indices=candidate_question_indices,
        per_question_predictions=per_question_predictions,
        predictions=predictions,
    )


def _build_online_model_bundle(
    input_payload: QuestionOnlinePredictionInput,
) -> QuestionOnlineModelBundle:
    """构造图编码器、属性编码器、融合层和序列模型。"""
    from models.MEFKT.model import MEFKTSequenceModel, load_compatible_state

    fused_embedding = _build_fused_question_embedding(input_payload)
    sequence_embedding_dim = int(fused_embedding.size(1))
    embedding_dim = _metadata_int(input_payload.metadata, "embedding_dim", sequence_embedding_dim)
    if embedding_dim != sequence_embedding_dim:
        logger.warning(
            "MEFKT 运行时融合维度与元数据不一致，将使用运行时维度: metadata=%d, runtime=%d",
            embedding_dim,
            sequence_embedding_dim,
        )

    sequence_model = MEFKTSequenceModel(
        item_count=len(input_payload.bundle.question_ids),
        item_embedding_dim=sequence_embedding_dim,
        num_heads=_metadata_int(input_payload.metadata, "num_heads", 4),
        head_dim=_metadata_int(input_payload.metadata, "head_dim", 32),
        pretrained_item_embedding=fused_embedding.detach().cpu(),
    ).to(input_payload.device)
    load_compatible_state(sequence_model, input_payload.sequence_state_dict)
    sequence_model.eval()
    return QuestionOnlineModelBundle(
        sequence_model=sequence_model,
        sequence_embedding_dim=sequence_embedding_dim,
    )


def _build_fused_question_embedding(input_payload: QuestionOnlinePredictionInput):
    """根据课程题图静态特征生成题目融合 embedding。"""
    import torch
    from models.MEFKT.model import (
        GraphContrastiveEncoder,
        LinearAlignmentFusion,
        MultiAttributeEncoder,
        load_compatible_state,
    )

    metadata = input_payload.metadata
    bundle = input_payload.bundle
    feature_dim = _metadata_int(metadata, "feature_dim", int(bundle.node_feature_matrix.size(1)))
    relation_dim = _metadata_int(metadata, "relation_dim", int(bundle.relation_stats_matrix.size(1)))
    align_dim = _metadata_int(metadata, "align_dim", 128)
    hidden_dim = _metadata_int(metadata, "hidden_dim", 128)
    type_mapping = cast(dict[str, int], metadata.get("type_mapping") or {"unknown": 0})

    graph_encoder = GraphContrastiveEncoder(feature_dim, hidden_dim, align_dim).to(input_payload.device)
    attribute_encoder = MultiAttributeEncoder(
        feature_dim,
        max(type_mapping.values(), default=0) + 1,
        align_dim,
        relation_dim=relation_dim,
    ).to(input_payload.device)
    fusion_layer = LinearAlignmentFusion(align_dim, align_dim, align_dim).to(input_payload.device)
    load_compatible_state(graph_encoder, input_payload.graph_state_dict)
    load_compatible_state(attribute_encoder, input_payload.attribute_state_dict)
    load_compatible_state(fusion_layer, input_payload.fusion_state_dict)
    graph_encoder.eval()
    attribute_encoder.eval()
    fusion_layer.eval()

    tensors = _move_bundle_tensors_to_device(bundle, input_payload.device)
    return _encode_fused_embedding(
        torch_module=torch,
        graph_encoder=graph_encoder,
        attribute_encoder=attribute_encoder,
        fusion_layer=fusion_layer,
        moved_tensors=tensors,
    )


def _encode_fused_embedding(
    *,
    torch_module,
    graph_encoder,
    attribute_encoder,
    fusion_layer,
    moved_tensors,
):
    """运行图编码、属性编码和线性融合。"""
    (
        node_feature_matrix,
        relation_stats_matrix,
        adjacency_matrix,
        difficulty_vector,
        response_time_vector,
        exercise_type_vector,
    ) = moved_tensors

    with torch_module.no_grad():
        struct_embedding = graph_encoder.encode(node_feature_matrix, adjacency_matrix)
        attribute_result = attribute_encoder(
            node_feature_matrix=node_feature_matrix,
            difficulty_vector=difficulty_vector,
            response_time_vector=response_time_vector,
            exercise_type_vector=exercise_type_vector,
            exercise_adjacency=adjacency_matrix,
            relation_stats_matrix=relation_stats_matrix,
        )
        return fusion_layer(struct_embedding, attribute_result.embedding)


def _metadata_int(metadata: dict[str, object], key: str, default: int) -> int:
    """读取元数据整数配置。"""
    return _coerce_int(metadata.get(key), default)


def _resolve_target_point_ids(input_payload: QuestionOnlinePredictionInput) -> set[int]:
    """解析本次预测需要输出的知识点集合。"""
    target_point_ids = set(int(point_id) for point_id in (input_payload.knowledge_point_ids or []))
    if not target_point_ids:
        target_point_ids.update(_points_from_answer_history(input_payload))
    if not target_point_ids:
        target_point_ids.update(input_payload.bundle.point_to_question_indices.keys())
    return target_point_ids


def _points_from_answer_history(input_payload: QuestionOnlinePredictionInput) -> set[int]:
    """从历史作答记录中推导目标知识点。"""
    target_point_ids: set[int] = set()
    for record in input_payload.answer_history:
        point_id_raw = record.get("knowledge_point_id")
        if point_id_raw is not None:
            target_point_ids.add(int(str(point_id_raw)))
        question_id_raw = record.get("question_id")
        if question_id_raw is not None:
            target_point_ids.update(
                input_payload.bundle.question_to_points.get(int(str(question_id_raw)), [])
            )
    return target_point_ids


def _resolve_candidate_question_indices(
    target_point_ids: set[int],
    bundle: CourseQuestionRuntimeBundle,
) -> list[int]:
    """将目标知识点映射到候选题节点索引。"""
    return sorted(
        {
            question_index
            for point_id in target_point_ids
            for question_index in bundle.point_to_question_indices.get(int(point_id), [])
        }
    )


def _empty_question_online_response() -> dict[str, object]:
    """课程题图无法关联目标知识点时的稳定响应。"""
    return {
        "predictions": {},
        "confidence": 0.0,
        "model_type": "mefkt_question_online",
        "analysis": "当前课程题图中未找到可关联到目标知识点的题目节点",
    }


def _predict_candidate_questions(
    *,
    input_payload: QuestionOnlinePredictionInput,
    sequence_model,
    candidate_question_indices: list[int],
    torch_module,
):
    """用序列模型预测候选题正确概率。"""
    candidate_tensor = torch_module.tensor(
        candidate_question_indices,
        dtype=torch_module.long,
        device=input_payload.device,
    )
    if input_payload.history_indices:
        return sequence_model.predict_candidate(
            history_item_indices=torch_module.tensor(
                input_payload.history_indices,
                dtype=torch_module.long,
                device=input_payload.device,
            ),
            history_correct_flags=torch_module.tensor(
                input_payload.history_correct,
                dtype=torch_module.long,
                device=input_payload.device,
            ),
            history_time_gaps=torch_module.tensor(
                input_payload.history_gap_hours,
                dtype=torch_module.float32,
                device=input_payload.device,
            ),
            candidate_item_indices=candidate_tensor,
        )
    return torch_module.full(
        (len(candidate_question_indices),),
        0.28,
        dtype=torch_module.float32,
        device=input_payload.device,
    )


def _build_per_question_predictions(
    bundle: CourseQuestionRuntimeBundle,
    candidate_question_indices: list[int],
    probability_tensor,
) -> dict[int, float]:
    """将题节点索引概率映射回题目 ID。"""
    return {
        bundle.question_ids[question_index]: float(probability)
        for question_index, probability in zip(
            candidate_question_indices,
            probability_tensor.detach().cpu().tolist(),
            strict=True,
        )
    }


def _aggregate_point_predictions(
    *,
    bundle: CourseQuestionRuntimeBundle,
    target_point_ids: set[int],
    per_question_predictions: dict[int, float],
) -> dict[int, float]:
    """将题目概率聚合为知识点掌握度。"""
    predictions: dict[int, float] = {}
    for point_id in sorted(target_point_ids):
        probabilities = _point_probabilities(
            bundle=bundle,
            point_id=int(point_id),
            per_question_predictions=per_question_predictions,
        )
        if not probabilities:
            continue
        predictions[int(point_id)] = round(sum(probabilities) / max(len(probabilities), 1), 4)
    return predictions


def _point_probabilities(
    *,
    bundle: CourseQuestionRuntimeBundle,
    point_id: int,
    per_question_predictions: dict[int, float],
) -> list[float]:
    """读取知识点关联题目的预测概率，必要时使用代表题兜底。"""
    point_question_indices = bundle.point_to_question_indices.get(point_id, [])
    probabilities = [
        per_question_predictions.get(bundle.question_ids[question_index])
        for question_index in point_question_indices
        if bundle.question_ids[question_index] in per_question_predictions
    ]
    if probabilities:
        return probabilities
    representative_index = bundle.representative_question_index.get(point_id)
    if representative_index is None:
        return []
    representative_question_id = bundle.question_ids[representative_index]
    return [per_question_predictions.get(representative_question_id, 0.35)]


def _question_online_response(
    *,
    input_payload: QuestionOnlinePredictionInput,
    candidate_question_indices: list[int],
    per_question_predictions: dict[int, float],
    predictions: dict[int, float],
) -> dict[str, object]:
    """构造题目级在线部署预测响应。"""
    history_coverage = input_payload.recognized_count / max(len(input_payload.answer_history), 1)
    candidate_coverage = len(candidate_question_indices) / max(len(input_payload.bundle.question_ids), 1)
    confidence = min(
        0.93,
        0.46
        + len(input_payload.history_indices) / 24.0 * 0.24
        + history_coverage * 0.14
        + candidate_coverage * 0.08,
    )
    return {
        "predictions": predictions,
        "confidence": round(confidence, 3),
        "model_type": "mefkt_question_online",
        "question_predictions": {
            question_id: round(probability, 4)
            for question_id, probability in per_question_predictions.items()
        },
        "analysis": (
            f"MEFKT 题目级在线部署完成：课程题图 {len(input_payload.bundle.question_ids)} 题，"
            f"识别 {input_payload.recognized_count}/{len(input_payload.answer_history)} 条有效交互，"
            f"聚合输出 {len(predictions)} 个知识点掌握度"
        ),
    }
