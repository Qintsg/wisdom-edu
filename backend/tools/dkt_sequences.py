#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""DKT 训练序列加载、编码、评估与 epoch 训练辅助函数。"""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path


def _build_onehot_batch(kp_seqs, correct_seqs, q_size, sequence_max_step, skip_out_of_range=False):
    """将知识点序列编码为 DKT 可消费的 one-hot 批次。"""
    import numpy as np

    batch_size_local = len(kp_seqs)
    data = np.zeros((batch_size_local, sequence_max_step, 2 * q_size), dtype=np.float32)
    for batch_index in range(batch_size_local):
        for time_index in range(len(kp_seqs[batch_index])):
            kp_idx = kp_seqs[batch_index][time_index]
            if skip_out_of_range and (kp_idx < 0 or kp_idx >= q_size):
                continue
            if correct_seqs[batch_index][time_index] > 0:
                data[batch_index, time_index, kp_idx] = 1.0
            else:
                data[batch_index, time_index, q_size + kp_idx] = 1.0
    return data


def _build_next_step_targets(kp_seqs, correct_seqs, target_steps):
    """将变长序列整理为下一步预测所需的目标索引、标签与掩码。"""
    import torch

    batch_size_local = len(kp_seqs)
    next_kp_tensor = torch.full((batch_size_local, target_steps), -1, dtype=torch.long)
    next_correct_tensor = torch.zeros((batch_size_local, target_steps), dtype=torch.float32)
    valid_mask = torch.zeros((batch_size_local, target_steps), dtype=torch.bool)
    for batch_index in range(batch_size_local):
        effective_steps = min(len(kp_seqs[batch_index]) - 1, target_steps)
        if effective_steps <= 0:
            continue
        next_kp_tensor[batch_index, :effective_steps] = torch.tensor(
            kp_seqs[batch_index][1 : effective_steps + 1],
            dtype=torch.long,
        )
        next_correct_tensor[batch_index, :effective_steps] = torch.tensor(
            correct_seqs[batch_index][1 : effective_steps + 1],
            dtype=torch.float32,
        )
        valid_mask[batch_index, :effective_steps] = True
    return next_kp_tensor, next_correct_tensor, valid_mask


def _gather_next_step_outputs(prediction_tensor, batch_kp, batch_correct):
    """提取 DKT 针对下一步交互的预测概率与目标标签。"""
    target_steps = max(int(prediction_tensor.size(1)) - 1, 0)
    if target_steps <= 0:
        return None, None

    next_kp_tensor, next_correct_tensor, valid_mask = _build_next_step_targets(
        batch_kp,
        batch_correct,
        target_steps,
    )
    device = prediction_tensor.device
    next_kp_tensor = next_kp_tensor.to(device)
    next_correct_tensor = next_correct_tensor.to(device)
    valid_mask = valid_mask.to(device)

    valid_mask = valid_mask & (next_kp_tensor >= 0) & (next_kp_tensor < prediction_tensor.size(2))
    if not bool(valid_mask.any()):
        return None, None

    safe_next_kp = next_kp_tensor.clamp(min=0)
    next_probability_tensor = prediction_tensor[:, :-1, :].gather(
        dim=2,
        index=safe_next_kp.unsqueeze(2),
    ).squeeze(2)
    return next_probability_tensor[valid_mask], next_correct_tensor[valid_mask]


def _evaluate_dkt_auc(model, all_kp_seqs, all_correct_seqs, test_idx, batch_size, q_size, max_step, device):
    """评估 DKT 模型在测试集上的 AUC。"""
    import torch
    from sklearn.metrics import roc_auc_score

    all_pred = []
    all_true = []
    model.eval()
    with torch.no_grad():
        for batch_start in range(0, len(test_idx), batch_size):
            batch_indices = test_idx[batch_start : batch_start + batch_size]
            batch_kp = [all_kp_seqs[index] for index in batch_indices]
            batch_correct = [all_correct_seqs[index] for index in batch_indices]
            batch = torch.from_numpy(
                _build_onehot_batch(batch_kp, batch_correct, q_size, max_step, skip_out_of_range=True)
            ).to(device)
            probability_tensor, target_tensor = _gather_next_step_outputs(model(batch), batch_kp, batch_correct)
            if probability_tensor is None or target_tensor is None:
                continue
            all_pred.extend(probability_tensor.detach().clamp(1e-6, 1 - 1e-6).cpu().tolist())
            all_true.extend(target_tensor.detach().cpu().tolist())

    if not all_pred:
        return 0.0, 0
    try:
        auc = roc_auc_score(all_true, all_pred)
    except ValueError:
        auc = 0.5
    return auc, len(all_pred)


def _load_three_line_sequences(data_path):
    """加载标准三行格式的 DKT 数据。"""
    with open(data_path, "r", encoding="utf-8") as handle:
        lines = [line.strip() for line in handle.readlines() if line.strip()]

    sequences = []
    index = 0
    while index + 2 < len(lines):
        _ = int(lines[index])
        kp_seq = [int(item) for item in lines[index + 1].split(",") if item != ""]
        correct_seq = [int(item) for item in lines[index + 2].split(",") if item != ""]
        sequences.append((kp_seq, correct_seq))
        index += 3
    return sequences


def _find_first_matching_key(sample_row, candidate_keys):
    """在候选列名中找到当前 CSV 样本实际包含的第一列。"""
    for candidate_key in candidate_keys:
        if candidate_key in sample_row:
            return candidate_key
    return None


def _load_csv_sequences(data_path):
    """尝试从公开 CSV 数据集中按用户聚合序列。"""
    with open(data_path, "r", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        return []

    sample = rows[0]
    user_key = _find_first_matching_key(sample, ("user_id", "user", "student_id", "uid"))
    skill_key = _find_first_matching_key(sample, ("skill_id", "knowledge_point_id", "kc", "problem_id", "item_id"))
    correct_key = _find_first_matching_key(sample, ("correct", "is_correct", "label"))
    order_key = _find_first_matching_key(sample, ("timestamp", "order_id", "seq_idx", "event_id"))
    if not user_key or not skill_key or not correct_key:
        raise ValueError(f"CSV 数据集缺少必要列，无法解析: {data_path}")

    skill_map = {}
    sequences = defaultdict(list)
    for row in rows:
        user_value = str(row.get(user_key, "")).strip()
        skill_value = str(row.get(skill_key, "")).strip()
        correct_value = row.get(correct_key, "")
        if not user_value or not skill_value:
            continue
        if skill_value not in skill_map:
            skill_map[skill_value] = len(skill_map)
        try:
            correct = int(float(correct_value))
        except (TypeError, ValueError):
            continue
        order_value = row.get(order_key) if order_key else None
        sequences[user_value].append((order_value, skill_map[skill_value], 1 if correct else 0))

    normalized_sequences = []
    for user_rows in sequences.values():
        user_rows.sort(key=lambda item: "" if item[0] is None else str(item[0]))
        normalized_sequences.append(([item[1] for item in user_rows], [item[2] for item in user_rows]))
    return normalized_sequences


def _load_sequences_from_path(data_path):
    """根据文件后缀选择序列加载策略。"""
    if Path(data_path).suffix.lower() == ".csv":
        return _load_csv_sequences(data_path)
    return _load_three_line_sequences(data_path)


def _chunk_sequences(sequences, max_step):
    """按最大步长切分长序列。"""
    all_kp_seqs = []
    all_correct_seqs = []
    for kp_seq, correct_seq in sequences:
        for start in range(0, len(kp_seq), max_step):
            chunk_kp = kp_seq[start : start + max_step]
            chunk_correct = correct_seq[start : start + max_step]
            if len(chunk_kp) < 2:
                continue
            all_kp_seqs.append(chunk_kp)
            all_correct_seqs.append(chunk_correct)
    return all_kp_seqs, all_correct_seqs


def _load_chunked_sequences_from_path(data_path, max_step):
    """加载并按最大步长切分训练序列，统一训练入口的数据准备逻辑。"""
    return _chunk_sequences(_load_sequences_from_path(data_path), max_step)


def _split_train_test_indices(sample_count):
    """为 DKT 训练构建稳定的训练集与测试集索引。"""
    from sklearn.model_selection import train_test_split

    indices = list(range(sample_count))
    if len(indices) < 4:
        return indices, indices
    return train_test_split(indices, test_size=0.2, random_state=42)


def _build_batch_loss(prediction_tensor, batch_kp, batch_correct):
    """按 DKT 的下一步预测目标累积批次损失。"""
    import torch.nn.functional as functional

    probability_tensor, target_tensor = _gather_next_step_outputs(prediction_tensor, batch_kp, batch_correct)
    if probability_tensor is None or target_tensor is None:
        return None
    return functional.binary_cross_entropy(probability_tensor.clamp(1e-6, 1 - 1e-6), target_tensor)


def _train_dkt_epoch(model, optimizer, train_idx, all_kp_seqs, all_correct_seqs, batch_size, q_size, max_step, device):
    """执行一轮 DKT 训练并返回平均损失与有效批次数。"""
    import torch

    model.train()
    random.shuffle(train_idx)
    total_loss = 0.0
    n_batches = 0
    for batch_start in range(0, len(train_idx), batch_size):
        batch_indices = train_idx[batch_start : batch_start + batch_size]
        batch_kp = [all_kp_seqs[index] for index in batch_indices]
        batch_correct = [all_correct_seqs[index] for index in batch_indices]
        batch = torch.from_numpy(_build_onehot_batch(batch_kp, batch_correct, q_size, max_step)).to(device)
        loss = _build_batch_loss(model(batch), batch_kp, batch_correct)
        if loss is None:
            continue
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 10.0)
        optimizer.step()
        total_loss += loss.item()
        n_batches += 1
    return total_loss / max(n_batches, 1), n_batches
