#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
MEFKT 训练与状态管理工具。
@Project : wisdom-edu
@File : mefkt_training.py
@Author : Qintsg
@Date : 2026-04-04
"""

from __future__ import annotations

import csv
import json
import logging
import random
from dataclasses import dataclass
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
from platform_ai.kt.datasets import DEFAULT_PUBLIC_DATASET, get_public_dataset_info
from platform_ai.kt.torch_device import resolve_torch_device

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MEFKT_MODEL_PATH = BASE_DIR / "models" / "MEFKT" / "mefkt_model.pt"
MEFKT_META_PATH = BASE_DIR / "models" / "MEFKT" / "mefkt_model.meta.json"
MEFKT_PUBLIC_BASELINE_DIR = BASE_DIR / "models" / "MEFKT" / "public_baselines"
PAPER_TITLE = "融合多视角习题表征与遗忘机制的深度知识追踪"
PAPER_DOI = "10.11896/jsjkx.250700092"
RUNTIME_SCHEMA = "question_online_v1"


@dataclass(frozen=True)
class MEFKTTrainingBundle:
    """保存训练所需的静态图特征与序列数据。"""

    dataset_name: str
    item_ids: list[int]
    item_names: list[str]
    type_mapping: dict[str, int]
    sequences: list[tuple[list[int], list[int], list[float]]]
    node_feature_matrix: Tensor
    relation_stats_matrix: Tensor
    adjacency_matrix: Tensor
    difficulty_vector: Tensor
    response_time_vector: Tensor
    exercise_type_vector: Tensor
    training_mode: str
    training_sources: list[str]


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """将浮点值裁剪到闭区间内。"""
    return max(lower, min(upper, value))


def _relative_to_project(path_value: Path | str) -> str:
    """将路径尽量转成相对项目根目录的形式。"""
    path_obj = Path(path_value).resolve()
    try:
        return str(path_obj.relative_to(BASE_DIR)).replace("\\", "/")
    except ValueError:
        return str(path_obj).replace("\\", "/")


def _normalize_tensor(values: list[float], default_value: float = 0.5) -> Tensor:
    """将浮点数组归一化到 [0,1]。"""
    if not values:
        return torch.tensor([default_value], dtype=torch.float32)
    lower = min(values)
    upper = max(values)
    if abs(upper - lower) <= 1e-8:
        return torch.full((len(values),), default_value, dtype=torch.float32)
    return torch.tensor(
        [(value - lower) / (upper - lower) for value in values],
        dtype=torch.float32,
    )


def _load_three_line_sequences(data_path: Path) -> list[tuple[list[int], list[int]]]:
    """读取三行格式数据集。"""
    lines = [
        line.strip()
        for line in data_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    sequences: list[tuple[list[int], list[int]]] = []
    line_index = 0
    while line_index + 2 < len(lines):
        _ = int(lines[line_index])
        item_sequence = [
            int(part) for part in lines[line_index + 1].split(",") if part != ""
        ]
        correct_sequence = [
            int(part) for part in lines[line_index + 2].split(",") if part != ""
        ]
        if len(item_sequence) >= 2 and len(item_sequence) == len(correct_sequence):
            sequences.append((item_sequence, correct_sequence))
        line_index += 3
    return sequences


def _load_csv_sequences(data_path: Path) -> list[tuple[list[int], list[int]]]:
    """读取带 user / item / correct 字段的 CSV 公开数据。"""
    with data_path.open("r", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        return []

    sample = rows[0]
    user_key = next(
        (key for key in ("user_id", "user", "student_id", "uid") if key in sample),
        None,
    )
    item_key = next(
        (key for key in ("problem_id", "item_id", "skill_id", "kc") if key in sample),
        None,
    )
    correct_key = next(
        (key for key in ("correct", "is_correct", "label") if key in sample),
        None,
    )
    order_key = next(
        (key for key in ("timestamp", "order_id", "seq_idx", "event_id") if key in sample),
        None,
    )
    if not user_key or not item_key or not correct_key:
        raise ValueError(f"CSV 数据集缺少必要列，无法解析: {data_path}")

    item_mapping: dict[str, int] = {}
    grouped_rows: dict[str, list[tuple[str, int, int]]] = {}
    for row in rows:
        user_value = str(row.get(user_key, "")).strip()
        item_value = str(row.get(item_key, "")).strip()
        correct_value = row.get(correct_key, "")
        if not user_value or not item_value:
            continue
        if item_value not in item_mapping:
            item_mapping[item_value] = len(item_mapping)
        try:
            correct = int(float(correct_value))
        except (TypeError, ValueError):
            continue
        grouped_rows.setdefault(user_value, []).append(
            (str(row.get(order_key, "")) if order_key else "", item_mapping[item_value], 1 if correct else 0)
        )

    sequences: list[tuple[list[int], list[int]]] = []
    for user_rows in grouped_rows.values():
        user_rows.sort(key=lambda item: item[0])
        item_sequence = [item[1] for item in user_rows]
        correct_sequence = [item[2] for item in user_rows]
        if len(item_sequence) >= 2:
            sequences.append((item_sequence, correct_sequence))
    return sequences


def _load_public_sequences(data_path: Path) -> list[tuple[list[int], list[int]]]:
    """根据后缀读取公开数据序列。"""
    if data_path.suffix.lower() == ".csv":
        return _load_csv_sequences(data_path)
    return _load_three_line_sequences(data_path)


def _chunk_public_sequences(
    raw_sequences: list[tuple[list[int], list[int]]],
    sequence_max_step: int,
) -> list[tuple[list[int], list[int]]]:
    """将公开数据中的超长轨迹切成定长窗口，降低序列训练的显存峰值。"""
    if sequence_max_step <= 1:
        return [
            (item_sequence, correct_sequence)
            for item_sequence, correct_sequence in raw_sequences
            if len(item_sequence) >= 2 and len(item_sequence) == len(correct_sequence)
        ]

    chunked_sequences: list[tuple[list[int], list[int]]] = []
    for item_sequence, correct_sequence in raw_sequences:
        for start_index in range(0, len(item_sequence), sequence_max_step):
            current_items = item_sequence[start_index : start_index + sequence_max_step]
            current_correct = correct_sequence[start_index : start_index + sequence_max_step]
            if len(current_items) >= 2 and len(current_items) == len(current_correct):
                chunked_sequences.append((current_items, current_correct))
    return chunked_sequences


def _build_transition_matrices(
    sequence_items: list[list[int]],
    item_count: int,
) -> tuple[Tensor, Tensor, Tensor, list[int]]:
    """根据交互转移构建无向图、前驱/后继统计与出现次数。"""
    adjacency = torch.zeros(item_count, item_count, dtype=torch.float32)
    predecessor_matrix = torch.zeros(item_count, item_count, dtype=torch.float32)
    successor_matrix = torch.zeros(item_count, item_count, dtype=torch.float32)
    occurrence_count = [0 for _ in range(item_count)]
    for item_sequence in sequence_items:
        for current_item in item_sequence:
            occurrence_count[current_item] += 1
        for left_item, right_item in zip(item_sequence[:-1], item_sequence[1:], strict=False):
            adjacency[left_item, right_item] += 1.0
            adjacency[right_item, left_item] += 1.0
            successor_matrix[left_item, right_item] += 1.0
            predecessor_matrix[right_item, left_item] += 1.0
    adjacency = (adjacency > 0).float()
    predecessor_matrix = (predecessor_matrix > 0).float()
    successor_matrix = (successor_matrix > 0).float()
    return adjacency, predecessor_matrix, successor_matrix, occurrence_count


def _estimate_public_difficulty(
    sequence_items: list[list[int]],
    sequence_correct: list[list[int]],
    item_count: int,
) -> Tensor:
    """用错误率估计公开数据中的节点难度。"""
    total_counts = [0 for _ in range(item_count)]
    wrong_counts = [0 for _ in range(item_count)]
    for item_sequence, correct_sequence in zip(sequence_items, sequence_correct, strict=True):
        for item_index, correct_flag in zip(item_sequence, correct_sequence, strict=True):
            total_counts[item_index] += 1
            wrong_counts[item_index] += 0 if int(correct_flag) == 1 else 1
    difficulty_values = [
        wrong_counts[index] / max(total_counts[index], 1) for index in range(item_count)
    ]
    return torch.tensor(difficulty_values, dtype=torch.float32)


def _estimate_public_time_proxy(sequence_items: list[list[int]], item_count: int) -> Tensor:
    """用重访距离近似响应时长特征。"""
    revisit_distances: dict[int, list[float]] = {index: [] for index in range(item_count)}
    for item_sequence in sequence_items:
        last_position: dict[int, int] = {}
        for position, item_index in enumerate(item_sequence):
            if item_index in last_position:
                revisit_distances[item_index].append(float(position - last_position[item_index]))
            last_position[item_index] = position
    raw_values = []
    for item_index in range(item_count):
        distances = revisit_distances[item_index]
        raw_values.append(sum(distances) / len(distances) if distances else 1.0)
    return _normalize_tensor(raw_values, default_value=0.35)


def _build_public_features(
    adjacency: Tensor,
    predecessor_matrix: Tensor,
    successor_matrix: Tensor,
    difficulty_tensor: Tensor,
    response_time_tensor: Tensor,
    occurrence_count: list[int],
) -> tuple[Tensor, Tensor]:
    """将公开数据转成固定槽位特征，供课程题目级在线重建复用。"""
    item_count = int(adjacency.size(0))
    degree = adjacency.sum(dim=1)
    degree_norm = degree / degree.max().clamp_min(1.0)
    if item_count > 1:
        two_hop = (torch.matmul(adjacency, adjacency) > 0).float()
        two_hop_density = two_hop.sum(dim=1) / float(item_count - 1)
    else:
        two_hop_density = torch.zeros_like(degree_norm)

    neighbor_degree = torch.matmul(adjacency, degree_norm.unsqueeze(1)).squeeze(1)
    neighbor_degree /= degree.clamp_min(1.0)
    neighbor_difficulty = torch.matmul(adjacency, difficulty_tensor.unsqueeze(1)).squeeze(1)
    neighbor_difficulty /= degree.clamp_min(1.0)
    occurrence_tensor = _normalize_tensor([float(count) for count in occurrence_count], default_value=0.2)
    predecessor_norm = predecessor_matrix.sum(dim=1) / predecessor_matrix.sum(dim=1).max().clamp_min(1.0)
    successor_norm = successor_matrix.sum(dim=1) / successor_matrix.sum(dim=1).max().clamp_min(1.0)
    position_norm = torch.linspace(0.0, 1.0, max(item_count, 1), dtype=torch.float32)

    feature_columns: dict[str, Tensor] = {
        "difficulty_proxy": difficulty_tensor.float(),
        "response_time_proxy": response_time_tensor.float(),
        "occurrence_proxy": occurrence_tensor.float(),
        "degree_norm": degree_norm.float(),
        "two_hop_density": two_hop_density.float(),
        "neighbor_difficulty": neighbor_difficulty.float(),
        "knowledge_count_norm": torch.ones(item_count, dtype=torch.float32),
        "resource_count_norm": torch.zeros(item_count, dtype=torch.float32),
        "prerequisite_count_norm": predecessor_norm.float(),
        "dependent_count_norm": successor_norm.float(),
        "related_count_norm": neighbor_degree.float(),
        "chapter_position_norm": position_norm.float(),
        "content_length_norm": occurrence_tensor.float(),
        "analysis_length_norm": torch.zeros(item_count, dtype=torch.float32),
        "question_score_norm": torch.full((item_count,), 0.5, dtype=torch.float32),
        "historical_correct_rate": (1.0 - difficulty_tensor).float(),
    }
    node_feature_matrix = torch.stack(
        [feature_columns[column] for column in NODE_FEATURE_SCHEMA],
        dim=1,
    )
    relation_stats_matrix = torch.stack(
        [degree_norm, two_hop_density, predecessor_norm, successor_norm],
        dim=1,
    )
    return node_feature_matrix, relation_stats_matrix


def _build_public_bundle(
    dataset_name: str,
    sequence_max_step: int = 64,
) -> MEFKTTrainingBundle:
    """从公开数据构建固定特征维度的训练包。"""
    dataset_info = get_public_dataset_info(dataset_name)
    if not dataset_info.is_available or dataset_info.train_path is None:
        raise FileNotFoundError(f"公开数据集不可用: {dataset_name}")

    raw_sequences = _chunk_public_sequences(
        _load_public_sequences(dataset_info.train_path),
        sequence_max_step=sequence_max_step,
    )
    if not raw_sequences:
        raise ValueError(f"公开数据集没有可用样本: {dataset_name}")

    raw_item_ids = sorted({item_id for item_sequence, _ in raw_sequences for item_id in item_sequence})
    item_id_to_index = {item_id: index for index, item_id in enumerate(raw_item_ids)}
    mapped_sequences: list[tuple[list[int], list[int], list[float]]] = []
    for item_sequence, correct_sequence in raw_sequences:
        mapped_item_sequence = [item_id_to_index[item_id] for item_id in item_sequence if item_id in item_id_to_index]
        if len(mapped_item_sequence) != len(correct_sequence) or len(mapped_item_sequence) < 2:
            continue
        mapped_sequences.append(
            (mapped_item_sequence, list(correct_sequence), [1.0 for _ in mapped_item_sequence])
        )
    if not mapped_sequences:
        raise ValueError(f"公开数据集映射后没有可用样本: {dataset_name}")

    item_count = len(raw_item_ids)
    item_names = [f"public_item_{item_id}" for item_id in raw_item_ids]
    sequence_items = [item_sequence for item_sequence, _, _ in mapped_sequences]
    sequence_correct = [correct_sequence for _, correct_sequence, _ in mapped_sequences]
    adjacency, predecessor_matrix, successor_matrix, occurrence_count = _build_transition_matrices(
        sequence_items,
        item_count,
    )
    difficulty_tensor = _estimate_public_difficulty(sequence_items, sequence_correct, item_count)
    response_time_tensor = _estimate_public_time_proxy(sequence_items, item_count)
    node_feature_matrix, relation_stats_matrix = _build_public_features(
        adjacency=adjacency,
        predecessor_matrix=predecessor_matrix,
        successor_matrix=successor_matrix,
        difficulty_tensor=difficulty_tensor,
        response_time_tensor=response_time_tensor,
        occurrence_count=occurrence_count,
    )
    return MEFKTTrainingBundle(
        dataset_name=dataset_name,
        item_ids=raw_item_ids,
        item_names=item_names,
        type_mapping={key: value for key, value in QUESTION_TYPE_VOCAB.items()},
        sequences=mapped_sequences,
        node_feature_matrix=node_feature_matrix,
        relation_stats_matrix=relation_stats_matrix,
        adjacency_matrix=adjacency,
        difficulty_vector=difficulty_tensor,
        response_time_vector=response_time_tensor,
        exercise_type_vector=torch.zeros(item_count, dtype=torch.long),
        training_mode="public_pretrain_question_online",
        training_sources=[
            _relative_to_project(dataset_info.train_path),
            f"sequence_max_step={sequence_max_step}",
        ],
    )


def _collate_batch(
    batch_sequences: list[tuple[list[int], list[int], list[float]]],
) -> tuple[Tensor, Tensor, Tensor]:
    """将变长序列 padding 为张量批次。"""
    max_length = max(len(item_sequence) for item_sequence, _, _ in batch_sequences)
    batch_size = len(batch_sequences)
    item_tensor = torch.full((batch_size, max_length), -1, dtype=torch.long)
    correct_tensor = torch.zeros((batch_size, max_length), dtype=torch.long)
    time_gap_tensor = torch.ones((batch_size, max_length), dtype=torch.float32)
    for batch_index, (item_sequence, correct_sequence, time_gap_sequence) in enumerate(batch_sequences):
        seq_length = len(item_sequence)
        item_tensor[batch_index, :seq_length] = torch.tensor(item_sequence, dtype=torch.long)
        correct_tensor[batch_index, :seq_length] = torch.tensor(correct_sequence, dtype=torch.long)
        time_gap_tensor[batch_index, :seq_length] = torch.tensor(time_gap_sequence, dtype=torch.float32)
    return item_tensor, correct_tensor, time_gap_tensor


def _split_sequences(
    sequences: list[tuple[list[int], list[int], list[float]]],
    validation_ratio: float = 0.2,
    seed: int = 42,
) -> tuple[list[tuple[list[int], list[int], list[float]]], list[tuple[list[int], list[int], list[float]]]]:
    """划分训练集与验证集。"""
    shuffled_sequences = list(sequences)
    random.Random(seed).shuffle(shuffled_sequences)
    if len(shuffled_sequences) < 5:
        return shuffled_sequences, shuffled_sequences
    split_index = max(1, int(len(shuffled_sequences) * (1.0 - validation_ratio)))
    return shuffled_sequences[:split_index], shuffled_sequences[split_index:]


def _evaluate_sequence_model(
    model: MEFKTSequenceModel,
    sequences: list[tuple[list[int], list[int], list[float]]],
    batch_size: int,
    device: torch.device,
) -> dict[str, float]:
    """评估模型的 AUC 与准确率。"""
    from sklearn.metrics import roc_auc_score

    model.eval()
    all_probabilities: list[float] = []
    all_targets: list[int] = []
    with torch.no_grad():
        for start_index in range(0, len(sequences), batch_size):
            batch_sequences = sequences[start_index : start_index + batch_size]
            item_tensor, correct_tensor, time_gap_tensor = _collate_batch(batch_sequences)
            probability_tensor, valid_mask = model(
                item_tensor.to(device),
                correct_tensor.to(device),
                time_gap_tensor.to(device),
            )
            target_tensor = correct_tensor[:, 1:].to(device)
            for probability_value, target_value in zip(
                probability_tensor[valid_mask].detach().cpu().tolist(),
                target_tensor[valid_mask].detach().cpu().tolist(),
                strict=False,
            ):
                all_probabilities.append(float(probability_value))
                all_targets.append(int(target_value))
    if not all_targets:
        return {"auc": 0.0, "acc": 0.0, "samples": 0.0}
    predicted_labels = [1 if probability >= 0.5 else 0 for probability in all_probabilities]
    accuracy = sum(
        int(pred == gold) for pred, gold in zip(predicted_labels, all_targets, strict=False)
    ) / len(all_targets)
    auc = 0.5 if len(set(all_targets)) <= 1 else float(roc_auc_score(all_targets, all_probabilities))
    return {"auc": auc, "acc": accuracy, "samples": float(len(all_targets))}


def _write_mefkt_metadata(metadata_path: Path, payload: dict[str, object]) -> None:
    """持久化模型元数据。"""
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


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
        list(graph_encoder.parameters())
        + list(attribute_encoder.parameters())
        + list(fusion_layer.parameters()),
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
        total_loss = (
            contrastive_loss
            + attribute_result.difficulty_loss
            + similarity_weight * attribute_result.similarity_loss
            + 1e-4 * fused_embedding.pow(2).mean()
        )
        pretrain_optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(
            list(graph_encoder.parameters())
            + list(attribute_encoder.parameters())
            + list(fusion_layer.parameters()),
            max_norm=5.0,
        )
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
            probability_tensor, valid_mask = sequence_model(
                item_tensor.to(device),
                correct_tensor.to(device),
                time_gap_tensor.to(device),
            )
            target_tensor = correct_tensor[:, 1:].float().to(device)
            if not bool(valid_mask.any()):
                continue
            loss = torch.nn.functional.binary_cross_entropy(
                probability_tensor[valid_mask],
                target_tensor[valid_mask],
            )
            sequence_optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(sequence_model.parameters(), max_norm=5.0)
            sequence_optimizer.step()
            total_loss_value += float(loss.item())
            valid_batch_count += 1

        metrics = _evaluate_sequence_model(sequence_model, validation_sequences, batch_size, device)
        if metrics["auc"] >= best_metrics["auc"]:
            best_metrics = metrics
            best_sequence_state = {
                key: value.detach().cpu() for key, value in sequence_model.state_dict().items()
            }
        average_loss = total_loss_value / max(valid_batch_count, 1)
        print(
            f"[MEFKT] epoch={epoch_index + 1}/{max(epochs, 1)} loss={average_loss:.4f} "
            f"auc={metrics['auc']:.4f} acc={metrics['acc']:.4f} samples={int(metrics['samples'])}"
        )

    if best_sequence_state is None:
        best_sequence_state = {
            key: value.detach().cpu() for key, value in sequence_model.state_dict().items()
        }

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
    """
    训练 MEFKT 模型。

    兼容旧参数签名，但当前实现已按用户要求固定为“公开数据预训练 + 课程题目级在线部署”。
    因此 `course_id` / `use_synthetic` / `synthetic_students` 仅保留接口兼容，不再参与监督训练。
    """
    if course_id is not None or use_synthetic or synthetic_students != 96:
        logger.info(
            "MEFKT 训练已切换为公开数据优先模式，course_id/use_synthetic 参数仅保留兼容，不参与监督训练"
        )
    dataset_name = (public_dataset or DEFAULT_PUBLIC_DATASET).strip().lower()
    bundle = _build_public_bundle(
        dataset_name,
        sequence_max_step=sequence_max_step,
    )
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
    metadata_path = output.with_suffix(".meta.json")

    result = _train_mefkt_bundle(
        bundle=bundle,
        output_path=output,
        metadata_path=metadata_path,
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
    print(
        f"[MEFKT] 训练完成: dataset={result['training_dataset']}, auc={metrics_payload['auc']:.4f}, "
        f"acc={metrics_payload['acc']:.4f}, path={result['model_path']}"
    )
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
