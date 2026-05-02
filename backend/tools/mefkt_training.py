#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 训练与状态管理工具。"""

from __future__ import annotations

import json
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import cast

import torch
from torch import Tensor

from models.MEFKT.model import (
    GraphContrastiveEncoder,
    LinearAlignmentFusion,
    MEFKTSequenceModel,
    MultiAttributeEncoder,
    NODE_FEATURE_SCHEMA,
    QUESTION_TYPE_VOCAB,
    RELATION_STAT_SCHEMA,
)
from platform_ai.kt.datasets import DEFAULT_PUBLIC_DATASET
from platform_ai.kt.torch_device import resolve_torch_device
from tools.mefkt_paths import (
    MEFKT_META_PATH,
    MEFKT_MODEL_PATH,
    MEFKT_PUBLIC_BASELINE_DIR,
    PAPER_DOI,
    PAPER_TITLE,
    RUNTIME_SCHEMA,
)
from tools.mefkt_public_data import (
    MEFKTTrainingBundle,
    _build_public_bundle,
    _collate_batch,
    _evaluate_sequence_model,
    _relative_to_project,
    _split_sequences,
)

logger = logging.getLogger(__name__)


def _write_mefkt_metadata(metadata_path: Path, payload: dict[str, object]) -> None:
    """持久化模型元数据。"""
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _train_mefkt_bundle(
    bundle: MEFKTTrainingBundle,
    output_path: Path,
    metadata_path: Path,
    *,
    epochs: int,
    pretrain_epochs: int,
    batch_size: int,
    lr: float,
    hidden_dim: int,
    align_dim: int,
    similarity_weight: float,
    num_heads: int,
    head_dim: int,
    use_gpu: bool | None = None,
) -> dict[str, object]:
    """针对公开训练包训练可在线重建的 MEFKT 模型。"""
    runtime_device = resolve_torch_device(use_gpu)
    device = runtime_device.device
    item_count = len(bundle.item_ids)
    feature_dim = int(bundle.node_feature_matrix.size(1))
    relation_dim = int(bundle.relation_stats_matrix.size(1))
    type_count = max(bundle.type_mapping.values(), default=0) + 1

    graph_encoder = GraphContrastiveEncoder(feature_dim, hidden_dim, align_dim).to(device)
    attribute_encoder = MultiAttributeEncoder(feature_dim, type_count, align_dim, relation_dim=relation_dim).to(device)
    fusion_layer = LinearAlignmentFusion(align_dim, align_dim, align_dim).to(device)
    print(f"[MEFKT] 训练设备={runtime_device.label}, reason={runtime_device.reason}")

    feature_matrix = bundle.node_feature_matrix.to(device)
    relation_stats = bundle.relation_stats_matrix.to(device)
    adjacency = bundle.adjacency_matrix.to(device)
    difficulty_vector = bundle.difficulty_vector.to(device)
    response_time_vector = bundle.response_time_vector.to(device)
    type_vector = bundle.exercise_type_vector.to(device)

    pretrain_optimizer = torch.optim.Adam(
        list(graph_encoder.parameters()) + list(attribute_encoder.parameters()) + list(fusion_layer.parameters()),
        lr=lr,
    )
    fused_embedding = None
    for _ in range(max(pretrain_epochs, 1)):
        graph_encoder.train()
        attribute_encoder.train()
        fusion_layer.train()
        struct_embedding, contrastive_loss = graph_encoder.contrastive_loss(feature_matrix, adjacency)
        attribute_result = attribute_encoder(
            node_feature_matrix=feature_matrix,
            difficulty_vector=difficulty_vector,
            response_time_vector=response_time_vector,
            exercise_type_vector=type_vector,
            exercise_adjacency=adjacency,
            relation_stats_matrix=relation_stats,
        )
        fused_embedding = fusion_layer(struct_embedding, attribute_result.embedding)
        total_loss = contrastive_loss + attribute_result.difficulty_loss + similarity_weight * attribute_result.similarity_loss + 1e-4 * fused_embedding.pow(2).mean()
        pretrain_optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(list(graph_encoder.parameters()) + list(attribute_encoder.parameters()) + list(fusion_layer.parameters()), max_norm=5.0)
        pretrain_optimizer.step()
    if fused_embedding is None:
        raise RuntimeError("MEFKT 预训练未产生融合嵌入")

    ready_embedding = fused_embedding
    train_sequences, validation_sequences = _split_sequences(bundle.sequences)
    sequence_model = MEFKTSequenceModel(
        item_count=item_count,
        item_embedding_dim=int(ready_embedding.size(1)),
        num_heads=num_heads,
        head_dim=head_dim,
        pretrained_item_embedding=ready_embedding.detach().cpu(),
    ).to(device)
    sequence_optimizer = torch.optim.Adam(sequence_model.parameters(), lr=lr)

    best_metrics = {"auc": 0.0, "acc": 0.0, "samples": 0.0}
    best_sequence_state: dict[str, Tensor] | None = None
    for epoch_index in range(max(epochs, 1)):
        random.shuffle(train_sequences)
        sequence_model.train()
        total_loss_value = 0.0
        valid_batch_count = 0
        for start_index in range(0, len(train_sequences), batch_size):
            batch_sequences = train_sequences[start_index : start_index + batch_size]
            item_tensor, correct_tensor, time_gap_tensor = _collate_batch(batch_sequences)
            probability_tensor, valid_mask = sequence_model(item_tensor.to(device), correct_tensor.to(device), time_gap_tensor.to(device))
            target_tensor = correct_tensor[:, 1:].float().to(device)
            if not bool(valid_mask.any()):
                continue
            loss = torch.nn.functional.binary_cross_entropy(probability_tensor[valid_mask], target_tensor[valid_mask])
            sequence_optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(sequence_model.parameters(), max_norm=5.0)
            sequence_optimizer.step()
            total_loss_value += float(loss.item())
            valid_batch_count += 1

        metrics = _evaluate_sequence_model(sequence_model, validation_sequences, batch_size, device)
        if metrics["auc"] >= best_metrics["auc"]:
            best_metrics = metrics
            best_sequence_state = {key: value.detach().cpu() for key, value in sequence_model.state_dict().items()}
        average_loss = total_loss_value / max(valid_batch_count, 1)
        print(f"[MEFKT] epoch={epoch_index + 1}/{max(epochs, 1)} loss={average_loss:.4f} auc={metrics['auc']:.4f} acc={metrics['acc']:.4f} samples={int(metrics['samples'])}")

    if best_sequence_state is None:
        best_sequence_state = {key: value.detach().cpu() for key, value in sequence_model.state_dict().items()}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_payload: dict[str, object] = {
        "model_name": "MEFKT",
        "paper_title": PAPER_TITLE,
        "paper_doi": PAPER_DOI,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "runtime_schema": RUNTIME_SCHEMA,
        "training_mode": bundle.training_mode,
        "training_dataset": bundle.dataset_name,
        "public_training_only": True,
        "question_online_enabled": True,
        "item_count": item_count,
        "item_ids": bundle.item_ids,
        "item_names": bundle.item_names,
        "feature_dim": feature_dim,
        "relation_dim": relation_dim,
        "embedding_dim": int(ready_embedding.size(1)),
        "num_heads": num_heads,
        "head_dim": head_dim,
        "hidden_dim": hidden_dim,
        "align_dim": align_dim,
        "epochs": epochs,
        "pretrain_epochs": pretrain_epochs,
        "learning_rate": lr,
        "batch_size": batch_size,
        "similarity_weight": similarity_weight,
        "training_device": runtime_device.label,
        "training_sources": bundle.training_sources,
        "type_mapping": bundle.type_mapping,
        "question_type_vocab": QUESTION_TYPE_VOCAB,
        "node_feature_schema": list(NODE_FEATURE_SCHEMA),
        "relation_stat_schema": list(RELATION_STAT_SCHEMA),
        "best_metrics": best_metrics,
        "model_path": _relative_to_project(output_path),
        "response_time_proxy": "公开数据使用重访距离代理，在线课程题图使用题目难度、长度、历史正确率与图结构统计综合近似",
        "difficulty_proxy": "公开数据使用错误率，在线课程题图使用题目难度与历史表现联合编码",
    }
    checkpoint = {
        "state_dict": best_sequence_state,
        "sequence_state_dict": best_sequence_state,
        "graph_state_dict": {key: value.detach().cpu() for key, value in graph_encoder.state_dict().items()},
        "attribute_state_dict": {key: value.detach().cpu() for key, value in attribute_encoder.state_dict().items()},
        "fusion_state_dict": {key: value.detach().cpu() for key, value in fusion_layer.state_dict().items()},
        "metadata": metadata_payload,
    }
    torch.save(checkpoint, output_path)
    _write_mefkt_metadata(metadata_path, metadata_payload)
    return {
        "model_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metrics": best_metrics,
        "training_mode": bundle.training_mode,
        "item_count": item_count,
        "training_dataset": bundle.dataset_name,
        "training_device": runtime_device.label,
    }


def train_mefkt_v2(
    course_id: int | None = None,
    epochs: int = 16,
    pretrain_epochs: int = 8,
    batch_size: int = 32,
    lr: float = 0.001,
    hidden_dim: int = 128,
    align_dim: int = 128,
    similarity_weight: float = 0.5,
    num_heads: int = 4,
    head_dim: int = 32,
    public_dataset: str | None = None,
    use_synthetic: bool = False,
    synthetic_students: int = 96,
    max_sequences: int | None = None,
    output_path: str | None = None,
    use_gpu: bool | None = None,
    sequence_max_step: int = 64,
) -> dict[str, object]:
    """训练 MEFKT 模型，保持旧参数签名兼容。"""
    if course_id is not None or use_synthetic or synthetic_students != 96:
        logger.info("MEFKT 训练已切换为公开数据优先模式，course_id/use_synthetic 参数仅保留兼容，不参与监督训练")
    dataset_name = (public_dataset or DEFAULT_PUBLIC_DATASET).strip().lower()
    bundle = _build_public_bundle(dataset_name, sequence_max_step=sequence_max_step)
    if max_sequences and len(bundle.sequences) > max_sequences:
        bundle = MEFKTTrainingBundle(
            dataset_name=bundle.dataset_name,
            item_ids=bundle.item_ids,
            item_names=bundle.item_names,
            type_mapping=bundle.type_mapping,
            sequences=bundle.sequences[:max_sequences],
            node_feature_matrix=bundle.node_feature_matrix,
            relation_stats_matrix=bundle.relation_stats_matrix,
            adjacency_matrix=bundle.adjacency_matrix,
            difficulty_vector=bundle.difficulty_vector,
            response_time_vector=bundle.response_time_vector,
            exercise_type_vector=bundle.exercise_type_vector,
            training_mode=bundle.training_mode,
            training_sources=bundle.training_sources + [f"max_sequences={max_sequences}"],
        )

    if output_path:
        output = Path(output_path)
    elif dataset_name == DEFAULT_PUBLIC_DATASET:
        output = MEFKT_MODEL_PATH
    else:
        output = MEFKT_PUBLIC_BASELINE_DIR / f"mefkt_{dataset_name}.pt"

    result = _train_mefkt_bundle(
        bundle=bundle,
        output_path=output,
        metadata_path=output.with_suffix(".meta.json"),
        epochs=epochs,
        pretrain_epochs=pretrain_epochs,
        batch_size=batch_size,
        lr=lr,
        hidden_dim=hidden_dim,
        align_dim=align_dim,
        similarity_weight=similarity_weight,
        num_heads=num_heads,
        head_dim=head_dim,
        use_gpu=use_gpu,
    )
    metrics_payload = cast(dict[str, float], result["metrics"])
    print(f"[MEFKT] 训练完成: dataset={result['training_dataset']}, auc={metrics_payload['auc']:.4f}, acc={metrics_payload['acc']:.4f}, path={result['model_path']}")
    return result


def mefkt_status() -> dict[str, object]:
    """查看当前运行时 MEFKT 模型状态。"""
    if not MEFKT_META_PATH.exists():
        status = {
            "is_available": False,
            "model_path": str(MEFKT_MODEL_PATH),
            "metadata_path": str(MEFKT_META_PATH),
        }
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return status

    metadata = json.loads(MEFKT_META_PATH.read_text(encoding="utf-8"))
    status = {
        "is_available": MEFKT_MODEL_PATH.exists(),
        "model_path": str(MEFKT_MODEL_PATH),
        "metadata_path": str(MEFKT_META_PATH),
        "training_mode": metadata.get("training_mode"),
        "runtime_schema": metadata.get("runtime_schema"),
        "training_dataset": metadata.get("training_dataset"),
        "question_online_enabled": metadata.get("question_online_enabled", False),
        "best_metrics": metadata.get("best_metrics"),
        "item_count": metadata.get("item_count"),
        "paper_title": metadata.get("paper_title"),
    }
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return status


__all__ = ["MEFKTTrainingBundle", "mefkt_status", "train_mefkt_v2"]
