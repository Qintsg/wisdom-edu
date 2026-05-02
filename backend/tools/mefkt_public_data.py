#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 公开数据加载、特征构造与评估辅助逻辑。"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import Tensor

from models.MEFKT.model import NODE_FEATURE_SCHEMA, QUESTION_TYPE_VOCAB
from platform_ai.kt.datasets import get_public_dataset_info
from tools.mefkt_paths import BASE_DIR


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
    return torch.tensor([(value - lower) / (upper - lower) for value in values], dtype=torch.float32)


def _load_three_line_sequences(data_path: Path) -> list[tuple[list[int], list[int]]]:
    """读取三行格式数据集。"""
    lines = [line.strip() for line in data_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    sequences: list[tuple[list[int], list[int]]] = []
    line_index = 0
    while line_index + 2 < len(lines):
        _ = int(lines[line_index])
        item_sequence = [int(part) for part in lines[line_index + 1].split(",") if part != ""]
        correct_sequence = [int(part) for part in lines[line_index + 2].split(",") if part != ""]
        if len(item_sequence) >= 2 and len(item_sequence) == len(correct_sequence):
            sequences.append((item_sequence, correct_sequence))
        line_index += 3
    return sequences


def _load_csv_sequences(data_path: Path) -> list[tuple[list[int], list[int]]]:
    """读取带 user / item / correct 字段的 CSV 公开数据。"""
    with data_path.open("r", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return []

    sample = rows[0]
    user_key = next((key for key in ("user_id", "user", "student_id", "uid") if key in sample), None)
    item_key = next((key for key in ("problem_id", "item_id", "skill_id", "kc") if key in sample), None)
    correct_key = next((key for key in ("correct", "is_correct", "label") if key in sample), None)
    order_key = next((key for key in ("timestamp", "order_id", "seq_idx", "event_id") if key in sample), None)
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


def _chunk_public_sequences(raw_sequences: list[tuple[list[int], list[int]]], sequence_max_step: int) -> list[tuple[list[int], list[int]]]:
    """将公开数据中的超长轨迹切成定长窗口，降低序列训练的显存峰值。"""
    if sequence_max_step <= 1:
        return [(items, correct) for items, correct in raw_sequences if len(items) >= 2 and len(items) == len(correct)]

    chunked_sequences: list[tuple[list[int], list[int]]] = []
    for item_sequence, correct_sequence in raw_sequences:
        for start_index in range(0, len(item_sequence), sequence_max_step):
            current_items = item_sequence[start_index : start_index + sequence_max_step]
            current_correct = correct_sequence[start_index : start_index + sequence_max_step]
            if len(current_items) >= 2 and len(current_items) == len(current_correct):
                chunked_sequences.append((current_items, current_correct))
    return chunked_sequences


def _build_transition_matrices(sequence_items: list[list[int]], item_count: int) -> tuple[Tensor, Tensor, Tensor, list[int]]:
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
    return (adjacency > 0).float(), (predecessor_matrix > 0).float(), (successor_matrix > 0).float(), occurrence_count


def _estimate_public_difficulty(sequence_items: list[list[int]], sequence_correct: list[list[int]], item_count: int) -> Tensor:
    """用错误率估计公开数据中的节点难度。"""
    total_counts = [0 for _ in range(item_count)]
    wrong_counts = [0 for _ in range(item_count)]
    for item_sequence, correct_sequence in zip(sequence_items, sequence_correct, strict=True):
        for item_index, correct_flag in zip(item_sequence, correct_sequence, strict=True):
            total_counts[item_index] += 1
            wrong_counts[item_index] += 0 if int(correct_flag) == 1 else 1
    return torch.tensor([wrong_counts[index] / max(total_counts[index], 1) for index in range(item_count)], dtype=torch.float32)


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


def _build_public_features(adjacency: Tensor, predecessor_matrix: Tensor, successor_matrix: Tensor, difficulty_tensor: Tensor, response_time_tensor: Tensor, occurrence_count: list[int]) -> tuple[Tensor, Tensor]:
    """将公开数据转成固定槽位特征，供课程题目级在线重建复用。"""
    item_count = int(adjacency.size(0))
    degree = adjacency.sum(dim=1)
    degree_norm = degree / degree.max().clamp_min(1.0)
    if item_count > 1:
        two_hop = (torch.matmul(adjacency, adjacency) > 0).float()
        two_hop_density = two_hop.sum(dim=1) / float(item_count - 1)
    else:
        two_hop_density = torch.zeros_like(degree_norm)

    neighbor_degree = torch.matmul(adjacency, degree_norm.unsqueeze(1)).squeeze(1) / degree.clamp_min(1.0)
    neighbor_difficulty = torch.matmul(adjacency, difficulty_tensor.unsqueeze(1)).squeeze(1) / degree.clamp_min(1.0)
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
    node_feature_matrix = torch.stack([feature_columns[column] for column in NODE_FEATURE_SCHEMA], dim=1)
    relation_stats_matrix = torch.stack([degree_norm, two_hop_density, predecessor_norm, successor_norm], dim=1)
    return node_feature_matrix, relation_stats_matrix


def _build_public_bundle(dataset_name: str, sequence_max_step: int = 64) -> MEFKTTrainingBundle:
    """从公开数据构建固定特征维度的训练包。"""
    dataset_info = get_public_dataset_info(dataset_name)
    if not dataset_info.is_available or dataset_info.train_path is None:
        raise FileNotFoundError(f"公开数据集不可用: {dataset_name}")

    raw_sequences = _chunk_public_sequences(_load_public_sequences(dataset_info.train_path), sequence_max_step=sequence_max_step)
    if not raw_sequences:
        raise ValueError(f"公开数据集没有可用样本: {dataset_name}")

    raw_item_ids = sorted({item_id for item_sequence, _ in raw_sequences for item_id in item_sequence})
    item_id_to_index = {item_id: index for index, item_id in enumerate(raw_item_ids)}
    mapped_sequences: list[tuple[list[int], list[int], list[float]]] = []
    for item_sequence, correct_sequence in raw_sequences:
        mapped_item_sequence = [item_id_to_index[item_id] for item_id in item_sequence if item_id in item_id_to_index]
        if len(mapped_item_sequence) != len(correct_sequence) or len(mapped_item_sequence) < 2:
            continue
        mapped_sequences.append((mapped_item_sequence, list(correct_sequence), [1.0 for _ in mapped_item_sequence]))
    if not mapped_sequences:
        raise ValueError(f"公开数据集映射后没有可用样本: {dataset_name}")

    item_count = len(raw_item_ids)
    sequence_items = [item_sequence for item_sequence, _, _ in mapped_sequences]
    sequence_correct = [correct_sequence for _, correct_sequence, _ in mapped_sequences]
    adjacency, predecessor_matrix, successor_matrix, occurrence_count = _build_transition_matrices(sequence_items, item_count)
    difficulty_tensor = _estimate_public_difficulty(sequence_items, sequence_correct, item_count)
    response_time_tensor = _estimate_public_time_proxy(sequence_items, item_count)
    node_feature_matrix, relation_stats_matrix = _build_public_features(adjacency, predecessor_matrix, successor_matrix, difficulty_tensor, response_time_tensor, occurrence_count)
    return MEFKTTrainingBundle(
        dataset_name=dataset_name,
        item_ids=raw_item_ids,
        item_names=[f"public_item_{item_id}" for item_id in raw_item_ids],
        type_mapping={key: value for key, value in QUESTION_TYPE_VOCAB.items()},
        sequences=mapped_sequences,
        node_feature_matrix=node_feature_matrix,
        relation_stats_matrix=relation_stats_matrix,
        adjacency_matrix=adjacency,
        difficulty_vector=difficulty_tensor,
        response_time_vector=response_time_tensor,
        exercise_type_vector=torch.zeros(item_count, dtype=torch.long),
        training_mode="public_pretrain_question_online",
        training_sources=[_relative_to_project(dataset_info.train_path), f"sequence_max_step={sequence_max_step}"],
    )


def _collate_batch(batch_sequences: list[tuple[list[int], list[int], list[float]]]) -> tuple[Tensor, Tensor, Tensor]:
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


def _split_sequences(sequences: list[tuple[list[int], list[int], list[float]]], validation_ratio: float = 0.2, seed: int = 42) -> tuple[list[tuple[list[int], list[int], list[float]]], list[tuple[list[int], list[int], list[float]]]]:
    """划分训练集与验证集。"""
    shuffled_sequences = list(sequences)
    random.Random(seed).shuffle(shuffled_sequences)
    if len(shuffled_sequences) < 5:
        return shuffled_sequences, shuffled_sequences
    split_index = max(1, int(len(shuffled_sequences) * (1.0 - validation_ratio)))
    return shuffled_sequences[:split_index], shuffled_sequences[split_index:]


def _evaluate_sequence_model(model, sequences: list[tuple[list[int], list[int], list[float]]], batch_size: int, device: torch.device) -> dict[str, float]:
    """评估模型的 AUC 与准确率。"""
    from sklearn.metrics import roc_auc_score

    model.eval()
    all_probabilities: list[float] = []
    all_targets: list[int] = []
    with torch.no_grad():
        for start_index in range(0, len(sequences), batch_size):
            batch_sequences = sequences[start_index : start_index + batch_size]
            item_tensor, correct_tensor, time_gap_tensor = _collate_batch(batch_sequences)
            probability_tensor, valid_mask = model(item_tensor.to(device), correct_tensor.to(device), time_gap_tensor.to(device))
            target_tensor = correct_tensor[:, 1:].to(device)
            for probability_value, target_value in zip(probability_tensor[valid_mask].detach().cpu().tolist(), target_tensor[valid_mask].detach().cpu().tolist(), strict=False):
                all_probabilities.append(float(probability_value))
                all_targets.append(int(target_value))
    if not all_targets:
        return {"auc": 0.0, "acc": 0.0, "samples": 0.0}
    predicted_labels = [1 if probability >= 0.5 else 0 for probability in all_probabilities]
    accuracy = sum(int(pred == gold) for pred, gold in zip(predicted_labels, all_targets, strict=False)) / len(all_targets)
    auc = 0.5 if len(set(all_targets)) <= 1 else float(roc_auc_score(all_targets, all_probabilities))
    return {"auc": auc, "acc": accuracy, "samples": float(len(all_targets))}
