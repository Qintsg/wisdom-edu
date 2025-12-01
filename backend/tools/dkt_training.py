#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
DKT 训练管线。
从数据库或公开数据集中构建 DKT 训练数据，生成运行时模型与公开基线模型。
@Project : wisdom-edu
@File : dkt_training.py
@Author : Qintsg
@Date : 2026-03-23
"""

import os
import sys
import math
import random
import logging
import json
import csv
from collections import defaultdict
from pathlib import Path
from platform_ai.kt.datasets import (
    DEFAULT_PUBLIC_DATASET,
    get_public_dataset_info,
)
from platform_ai.kt.torch_device import resolve_torch_device

logger = logging.getLogger(__name__)

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_BASELINE_DIR = BASE_DIR / "models" / "DKT" / "public_baselines"
DEFAULT_TRAINING_DATA_PATH = BASE_DIR / "models" / "DKT" / "training_data.txt"
DEFAULT_RUNTIME_MODEL_PATH = BASE_DIR / "models" / "DKT" / "dkt_model.pt"
RUNTIME_METADATA_PATH = BASE_DIR / "models" / "DKT" / "dkt_model.meta.json"


def _build_onehot_batch(
    kp_seqs, correct_seqs, q_size, sequence_max_step, skip_out_of_range=False
):
    """
    将知识点序列编码为 DKT 可消费的 one-hot 批次。
    :param kp_seqs: 知识点序列列表。
    :param correct_seqs: 正误序列列表。
    :param q_size: 知识点总数。
    :param sequence_max_step: 单条序列最大长度。
    :param skip_out_of_range: 是否跳过越界知识点索引。
    :return: 编码后的 numpy 数组。
    """
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


def _evaluate_dkt_auc(
    model,
    all_kp_seqs,
    all_correct_seqs,
    test_idx,
    batch_size,
    q_size,
    max_step,
    device,
):
    """
    评估 DKT 模型在测试集上的 AUC。
    :param model: 已实例化的 DKT 模型。
    :param all_kp_seqs: 全部知识点序列。
    :param all_correct_seqs: 全部正误序列。
    :param test_idx: 测试样本索引列表。
    :param batch_size: 批大小。
    :param q_size: 知识点总数。
    :param max_step: 单条序列最大长度。
    :return: AUC 与有效评估样本数。
    """
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
                _build_onehot_batch(
                    batch_kp,
                    batch_correct,
                    q_size,
                    max_step,
                    skip_out_of_range=True,
                )
            ).to(device)
            pred = model(batch)
            probability_tensor, target_tensor = _gather_next_step_outputs(
                pred,
                batch_kp,
                batch_correct,
            )
            if probability_tensor is None or target_tensor is None:
                continue
            all_pred.extend(
                probability_tensor.detach().clamp(1e-6, 1 - 1e-6).cpu().tolist()
            )
            all_true.extend(target_tensor.detach().cpu().tolist())

    if not all_pred:
        return 0.0, 0

    try:
        auc = roc_auc_score(all_true, all_pred)
    except ValueError:
        auc = 0.5
    return auc, len(all_pred)


def _load_three_line_sequences(data_path):
    """
    加载标准三行格式的 DKT 数据。
    :param data_path: 数据文件路径。
    :return: 由知识点序列和正误序列组成的列表。
    """
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
    """
    尝试从公开 CSV 数据集中按用户聚合序列。
    :param data_path: CSV 数据文件路径。
    :return: 由知识点序列和正误序列组成的列表。
    """
    with open(data_path, "r", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        return []

    sample = rows[0]
    user_key = _find_first_matching_key(sample, ("user_id", "user", "student_id", "uid"))
    skill_key = _find_first_matching_key(
        sample,
        ("skill_id", "knowledge_point_id", "kc", "problem_id", "item_id"),
    )
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
        sequences[user_value].append(
            (order_value, skill_map[skill_value], 1 if correct else 0)
        )

    normalized_sequences = []
    for user_rows in sequences.values():
        user_rows.sort(key=lambda item: "" if item[0] is None else str(item[0]))
        kp_seq = [item[1] for item in user_rows]
        correct_seq = [item[2] for item in user_rows]
        normalized_sequences.append((kp_seq, correct_seq))
    return normalized_sequences


def _load_sequences_from_path(data_path):
    """
    根据文件后缀选择序列加载策略。
    :param data_path: 数据文件路径。
    :return: 统一格式的序列列表。
    """
    suffix = Path(data_path).suffix.lower()
    if suffix == ".csv":
        return _load_csv_sequences(data_path)
    return _load_three_line_sequences(data_path)


def _chunk_sequences(sequences, max_step):
    """
    按最大步长切分长序列。
    :param sequences: 原始序列列表。
    :param max_step: 单段序列最大长度。
    :return: 切分后的知识点序列列表与正误序列列表。
    """
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


def _write_runtime_metadata(**payload):
    """
    写入运行时模型元数据。
    :param payload: 需要持久化的元数据字段。
    :return: None。
    """
    RUNTIME_METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME_METADATA_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _to_project_relative_path(path_value):
    """将项目内路径规范为相对路径，便于跨环境复用。"""
    try:
        return str(Path(path_value).resolve().relative_to(BASE_DIR)).replace("\\", "/")
    except (OSError, RuntimeError, ValueError):
        return str(path_value).replace("\\", "/")


def _state_dict_to_cpu(model):
    """保存前将参数转回 CPU，确保运行时跨设备加载稳定。"""
    return {
        key: value.detach().cpu()
        for key, value in model.state_dict().items()
    }


def _build_batch_loss(prediction_tensor, batch_kp, batch_correct):
    """按 DKT 的下一步预测目标累积批次损失。"""
    import torch.nn.functional as functional

    probability_tensor, target_tensor = _gather_next_step_outputs(
        prediction_tensor,
        batch_kp,
        batch_correct,
    )
    if probability_tensor is None or target_tensor is None:
        return None
    return functional.binary_cross_entropy(
        probability_tensor.clamp(1e-6, 1 - 1e-6),
        target_tensor,
    )


def _train_dkt_epoch(
    model,
    optimizer,
    train_idx,
    all_kp_seqs,
    all_correct_seqs,
    batch_size,
    q_size,
    max_step,
    device,
):
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

        batch = torch.from_numpy(
            _build_onehot_batch(batch_kp, batch_correct, q_size, max_step)
        ).to(device)
        pred = model(batch)
        loss = _build_batch_loss(pred, batch_kp, batch_correct)
        if loss is None:
            continue

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 10.0)
        optimizer.step()
        total_loss += loss.item()
        n_batches += 1

    return total_loss / max(n_batches, 1), n_batches


def train_public_dataset_baseline(
    dataset_name,
    epochs=40,
    batch_size=64,
    lr=0.002,
    hidden_dim=200,
    max_step=50,
    use_gpu=None,
):
    """
    训练公开数据集基线模型。
    :param dataset_name: 公开数据集名称。
    :param epochs: 训练轮次。
    :param batch_size: 批大小。
    :param lr: 学习率。
    :param hidden_dim: 隐层维度。
    :param max_step: 单条序列最大长度。
    :param use_gpu: 是否优先使用 GPU 训练。
    :return: 基线训练结果字典，失败时返回 None。
    """
    try:
        import torch
        import torch.optim as optim
    except ImportError:
        print("[错误] PyTorch 未安装，请运行: pip install torch")
        return None

    dataset_info = get_public_dataset_info(dataset_name)
    if not dataset_info.is_available:
        raise FileNotFoundError(f"公开数据集不可用: {dataset_name}")

    runtime_device = resolve_torch_device(use_gpu)
    device = runtime_device.device

    train_path = dataset_info.train_path
    if not train_path:
        raise FileNotFoundError(f"公开数据集缺少训练文件路径: {dataset_name}")

    all_kp_seqs, all_correct_seqs = _load_chunked_sequences_from_path(train_path, max_step)
    if not all_kp_seqs:
        raise ValueError(f"公开数据集没有可用训练样本: {dataset_name}")

    q_size = max(max(sequence) for sequence in all_kp_seqs if sequence) + 1
    print(f"[公开基线] 数据集={dataset_name}, 样本={len(all_kp_seqs)}, Q={q_size}")

    train_idx, test_idx = _split_train_test_indices(len(all_kp_seqs))

    sys.path.insert(0, str(BASE_DIR / "models" / "DKT" / "KnowledgeTracing"))
    from model.RNNModel import DKT

    model = DKT(q_size * 2, hidden_dim, 1, q_size).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    best_auc = 0.0
    best_metrics = {"auc": 0.0, "samples": 0}
    PUBLIC_BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    baseline_model_path = PUBLIC_BASELINE_DIR / f"{dataset_name}.pt"

    print(
        f"[公开基线] 训练设备={runtime_device.label}, reason={runtime_device.reason}"
    )

    for epoch in range(epochs):
        _train_dkt_epoch(
            model,
            optimizer,
            train_idx,
            all_kp_seqs,
            all_correct_seqs,
            batch_size,
            q_size,
            max_step,
            device,
        )

        if (epoch + 1) % 10 != 0 and epoch != 0:
            continue

        auc, sample_count = _evaluate_dkt_auc(
            model,
            all_kp_seqs,
            all_correct_seqs,
            test_idx,
            batch_size,
            q_size,
            max_step,
            device,
        )
        if sample_count <= 0:
            continue
        if auc > best_auc:
            best_auc = auc
            best_metrics = {"auc": auc, "samples": sample_count}
            torch.save(_state_dict_to_cpu(model), baseline_model_path)

    if not baseline_model_path.exists():
        torch.save(_state_dict_to_cpu(model), baseline_model_path)

    return {
        "dataset": dataset_name,
        "model_path": str(baseline_model_path),
        "metrics": best_metrics,
        "q_size": q_size,
        "train_path": str(train_path),
        "training_device": runtime_device.label,
    }


def train_dkt_v2(
    data_path=None,
    course_id=None,
    epochs=100,
    batch_size=64,
    lr=0.002,
    hidden_dim=200,
    max_step=50,
    output_path=None,
    use_synthetic=False,
    public_dataset=None,
    blend_business_data=False,
    use_gpu=None,
):
    """
    执行增强版 DKT 训练入口。
    :param data_path: 自定义训练数据路径。
    :param course_id: 课程 ID。
    :param epochs: 训练轮次。
    :param batch_size: 批大小。
    :param lr: 学习率。
    :param hidden_dim: 隐层维度。
    :param max_step: 单条序列最大长度。
    :param output_path: 模型输出路径。
    :param use_synthetic: 是否使用合成数据。
    :param public_dataset: 公开基线数据集名称。
    :param blend_business_data: 是否拼接业务答题数据。
    :param use_gpu: 是否优先使用 GPU 训练。
    :return: 训练是否成功。
    """
    try:
        import torch
    except ImportError:
        print("[错误] PyTorch 未安装，请运行: pip install torch")
        return False

    dataset_name = (public_dataset or DEFAULT_PUBLIC_DATASET).strip().lower()
    baseline_epochs = max(20, min(int(epochs), 80))
    baseline_result = train_public_dataset_baseline(
        dataset_name=dataset_name,
        epochs=baseline_epochs,
        batch_size=batch_size,
        lr=lr,
        hidden_dim=hidden_dim,
        max_step=max_step,
        use_gpu=use_gpu,
    )
    if not baseline_result:
        print("[错误] DKT 公开数据基线训练失败")
        return False

    runtime_model_path = Path(output_path) if output_path else DEFAULT_RUNTIME_MODEL_PATH
    runtime_model_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_state = torch.load(baseline_result["model_path"], map_location="cpu", weights_only=True)
    torch.save(baseline_state, runtime_model_path)

    runtime_metadata = {
        "model_path": _to_project_relative_path(str(runtime_model_path)),
        "runtime_schema": "public_slot_adapter_v1",
        "slot_count": baseline_result["q_size"],
        "knowledge_point_count": baseline_result["q_size"],
        "epochs": baseline_epochs,
        "batch_size": batch_size,
        "learning_rate": lr,
        "hidden_dim": hidden_dim,
        "training_sources": [
            _to_project_relative_path(str(baseline_result["train_path"]))
        ],
        "public_dataset": dataset_name,
        "training_device": baseline_result.get("training_device"),
        "public_baseline": {
            **baseline_result,
            "model_path": _to_project_relative_path(str(baseline_result["model_path"])),
            "train_path": _to_project_relative_path(str(baseline_result["train_path"])),
        },
        "blend_business_data": False,
        "public_training_only": True,
        "blend_business_data_requested": bool(blend_business_data),
        "course_id_ignored": course_id is not None,
        "data_path_ignored": bool(data_path),
        "use_synthetic_ignored": bool(use_synthetic),
    }
    _write_runtime_metadata(**runtime_metadata)
    print(
        f"\n[训练完成] 已使用公开数据集 {dataset_name} 生成 DKT 运行时模型: {runtime_model_path}"
    )
    print(
        f"[适配说明] 运行时将通过 public_slot_adapter_v1 将课程题目/知识点映射到 {baseline_result['q_size']} 个公共槽位"
    )
    return True


def _get_num_kp(course_id=None):
    """获取知识点数量"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wisdom_edu_api.settings")
    import django

    django.setup()
    from knowledge.models import KnowledgePoint

    qs = KnowledgePoint.objects.all()
    if course_id:
        qs = qs.filter(course_id=course_id)
    return qs.count()


def _get_kp_mapping(course_id=None):
    """
    获取知识点ID到连续索引的映射

    Returns:
        (kp_to_idx, idx_to_kp): (dict, dict)
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wisdom_edu_api.settings")
    import django

    django.setup()
    from knowledge.models import KnowledgePoint

    qs = KnowledgePoint.objects.all()
    if course_id:
        qs = qs.filter(course_id=course_id)
    kp_ids = sorted(qs.values_list("id", flat=True))
    kp_to_idx = {kp_id: idx for idx, kp_id in enumerate(kp_ids)}
    idx_to_kp = {idx: kp_id for kp_id, idx in kp_to_idx.items()}
    return kp_to_idx, idx_to_kp


def _get_first_course_with_kps() -> int | None:
    """获取第一个包含知识点数据的课程 ID。"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wisdom_edu_api.settings")
    import django

    django.setup()
    from knowledge.models import KnowledgePoint

    return (
        KnowledgePoint.objects.order_by("course_id", "id")
        .values_list("course_id", flat=True)
        .first()
    )


def _get_kp_prerequisites(course_id=None):
    """
    获取知识点之间的先修关系，用于合成数据

    Returns:
        dict: {kp_id: [prerequisite_kp_ids]}
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wisdom_edu_api.settings")
    import django

    django.setup()
    from knowledge.models import KnowledgeRelation

    qs = KnowledgeRelation.objects.filter(relation_type="prerequisite")
    if course_id:
        qs = qs.filter(pre_point__course_id=course_id)
    prereqs = {}
    for rel in qs:
        prereqs.setdefault(rel.post_point_id, []).append(rel.pre_point_id)
    return prereqs


def _get_kp_metadata(course_id=None):
    """获取知识点元数据，用于构造更贴近真实情况的合成学习轨迹。"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wisdom_edu_api.settings")
    import django

    django.setup()

    from django.db.models import Count, Q as QueryExpression
    from assessments.models import Question
    from knowledge.models import KnowledgePoint

    qs = KnowledgePoint.objects.all()
    if course_id:
        qs = qs.filter(course_id=course_id)

    kp_ids = list(qs.values_list("id", flat=True))
    question_stats = {}
    if kp_ids:
        q_stats = (
            Question.objects.filter(knowledge_points__id__in=kp_ids)
            .values("knowledge_points")
            .annotate(
                total=Count("id", distinct=True),
                easy=Count("id", filter=QueryExpression(difficulty="easy"), distinct=True),
                medium=Count("id", filter=QueryExpression(difficulty="medium"), distinct=True),
                hard=Count("id", filter=QueryExpression(difficulty="hard"), distinct=True),
            )
        )
        question_stats = {
            row["knowledge_points"]: {
                "total": row["total"],
                "easy": row["easy"],
                "medium": row["medium"],
                "hard": row["hard"],
            }
            for row in q_stats
            if row["knowledge_points"] is not None
        }

    metadata = {}
    for kp in qs.iterator():
        metadata[kp.id] = {
            "name": kp.name,
            "order": kp.order or 0,
            "level": kp.level or 1,
            "chapter": (kp.chapter or "").strip(),
            "cognitive_dimension": (kp.cognitive_dimension or "").strip(),
            "category": (kp.category or "").strip(),
            "tags": kp.get_tags_list(),
            "question_stats": question_stats.get(
                kp.id,
                {"total": 0, "easy": 0, "medium": 0, "hard": 0},
            ),
        }
    return metadata


def _clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, value))


def _sigmoid(logit):
    logit = _clamp(logit, -12.0, 12.0)
    return 1 / (1 + math.exp(-logit))


def _mean(values, default=0.0):
    values = list(values)
    if not values:
        return default
    return sum(values) / len(values)


def _build_kp_profiles(kp_to_idx, prereqs, kp_metadata):
    """构建知识点画像：难度、章节、邻接关系与学习稳定度。"""
    children = defaultdict(list)
    for post_kp, pre_list in prereqs.items():
        for pre_kp in pre_list:
            if pre_kp in kp_to_idx and post_kp in kp_to_idx:
                children[pre_kp].append(post_kp)

    depth_cache = {}

    def calc_depth(current_kp_id, trail=None):
        """递归计算知识点在先修图中的深度。"""
        if current_kp_id in depth_cache:
            return depth_cache[current_kp_id]
        trail = trail or set()
        if current_kp_id in trail:
            return 0
        parents = [pre for pre in prereqs.get(current_kp_id, []) if pre in kp_to_idx]
        if not parents:
            depth_cache[current_kp_id] = 0
            return 0
        computed_depth = 1 + max(
            calc_depth(parent, trail | {current_kp_id}) for parent in parents
        )
        depth_cache[current_kp_id] = computed_depth
        return computed_depth

    cognitive_bonus = {
        "remember": -0.02,
        "understand": 0.0,
        "apply": 0.05,
        "analyze": 0.08,
        "evaluate": 0.1,
        "create": 0.12,
    }
    category_bonus = {
        "factual": -0.03,
        "conceptual": 0.02,
        "procedural": 0.06,
        "metacognitive": 0.1,
    }

    kp_profiles = {}
    for kp_id in kp_to_idx:
        meta = kp_metadata.get(kp_id, {})
        tags = set(meta.get("tags", []))
        q_stats = meta.get("question_stats", {})
        q_total = q_stats.get("total", 0)
        q_easy = q_stats.get("easy", 0)
        q_medium = q_stats.get("medium", 0)
        q_hard = q_stats.get("hard", 0)
        prereq_count = len([pre for pre in prereqs.get(kp_id, []) if pre in kp_to_idx])
        dependent_count = len(children.get(kp_id, []))
        depth = calc_depth(kp_id)
        level = max(1, int(meta.get("level") or 1))
        order = max(0, int(meta.get("order") or 0))

        difficulty = 0.26
        difficulty += min(depth, 4) * 0.07
        difficulty += min(prereq_count, 3) * 0.025
        difficulty += min(dependent_count, 4) * 0.015
        difficulty += min(level - 1, 5) * 0.035
        difficulty += cognitive_bonus.get(meta.get("cognitive_dimension", ""), 0.0)
        difficulty += category_bonus.get(meta.get("category", ""), 0.0)
        difficulty += q_hard * 0.035 + q_medium * 0.012 - q_easy * 0.01
        difficulty += min(order / max(len(kp_to_idx), 1), 1.0) * 0.05
        if "难点" in tags:
            difficulty += 0.06
        if "考点" in tags:
            difficulty += 0.03
        if "重点" in tags:
            difficulty += 0.02

        kp_profiles[kp_id] = {
            "difficulty": _clamp(difficulty, 0.18, 0.92),
            "depth": depth,
            "chapter": meta.get("chapter", ""),
            "level": level,
            "order": order,
            "prereqs": [pre for pre in prereqs.get(kp_id, []) if pre in kp_to_idx],
            "children": children.get(kp_id, []),
            "question_volume": q_total,
            "stability": _clamp(
                0.35 + q_total * 0.04 + prereq_count * 0.05, 0.35, 0.92
            ),
        }

    return kp_profiles, {kp_id: kp_profiles[kp_id]["children"] for kp_id in kp_profiles}


def _sample_student_profile(rng):
    """采样学生画像，让合成学生不再只有一个统一模板。"""
    archetype = rng.choices(
        ["struggling", "steady", "advanced"],
        weights=[0.26, 0.52, 0.22],
        k=1,
    )[0]

    if archetype == "struggling":
        base_ability = _clamp(rng.betavariate(2.0, 4.2) * 0.9 + 0.02, 0.08, 0.72)
        learning_rate = 0.045 + rng.random() * 0.06
        forgetting_rate = 0.035 + rng.random() * 0.045
        slip_rate = 0.08 + rng.random() * 0.08
        guess_rate = 0.05 + rng.random() * 0.08
        review_bias = 0.5 + rng.random() * 0.35
        persistence = 0.42 + rng.random() * 0.22
    elif archetype == "advanced":
        base_ability = _clamp(rng.betavariate(4.2, 2.1) * 0.92 + 0.04, 0.38, 0.96)
        learning_rate = 0.065 + rng.random() * 0.08
        forgetting_rate = 0.012 + rng.random() * 0.025
        slip_rate = 0.02 + rng.random() * 0.05
        guess_rate = 0.02 + rng.random() * 0.04
        review_bias = 0.2 + rng.random() * 0.25
        persistence = 0.62 + rng.random() * 0.28
    else:
        base_ability = _clamp(rng.betavariate(3.0, 3.0) * 0.9 + 0.03, 0.18, 0.88)
        learning_rate = 0.055 + rng.random() * 0.07
        forgetting_rate = 0.02 + rng.random() * 0.035
        slip_rate = 0.04 + rng.random() * 0.06
        guess_rate = 0.03 + rng.random() * 0.05
        review_bias = 0.3 + rng.random() * 0.3
        persistence = 0.5 + rng.random() * 0.25

    return {
        "archetype": archetype,
        "base_ability": base_ability,
        "learning_rate": learning_rate,
        "forgetting_rate": forgetting_rate,
        "slip_rate": slip_rate,
        "guess_rate": guess_rate,
        "review_bias": review_bias,
        "focus_bias": 0.48 + rng.random() * 0.35,
        "fatigue_sensitivity": 0.04 + rng.random() * 0.11,
        "persistence": persistence,
        "session_span": rng.randint(6, 14),
    }


def _choose_focus_kp(kp_profiles, mastery, attempts, review_queue, profile, rng):
    candidates = []
    weights = []
    for kp_id, kp_profile in kp_profiles.items():
        prereq_mastery = _mean(
            (
                mastery.get(pre, 0.25 + profile["base_ability"] * 0.25)
                for pre in kp_profile["prereqs"]
            ),
            default=0.9,
        )
        unlocked = (
            prereq_mastery >= 0.45
            or attempts.get(kp_id, 0) > 0
            or not kp_profile["prereqs"]
        )
        if not unlocked and attempts.get(kp_id, 0) == 0:
            continue
        weight = 0.1
        weight += (1 - mastery.get(kp_id, 0.25)) * 1.2
        weight += review_queue.get(kp_id, 0.0) * 0.5
        if attempts.get(kp_id, 0) == 0:
            weight += 0.3
        candidates.append(kp_id)
        weights.append(weight)
    if not candidates:
        return rng.choice(list(kp_profiles.keys()))
    return rng.choices(candidates, weights=weights, k=1)[0]


def _simulate_student_sequence(
    kp_to_idx, kp_profiles, children_map, rng, seq_len, student_profile=None
):
    """模拟单个学生的答题轨迹。"""
    profile = student_profile or _sample_student_profile(rng)
    kp_ids = list(kp_profiles.keys())
    mastery = {}
    attempts = defaultdict(int)
    recent_wrong = defaultdict(int)
    review_queue = defaultdict(float)
    last_seen = {}
    last_results = []

    for kp_id, kp_profile in kp_profiles.items():
        prereq_boost = 0.04 * len(kp_profile["prereqs"])
        base_ability = float(profile["base_ability"])
        difficulty_score = float(kp_profile["difficulty"])
        mastery[kp_id] = _clamp(
            base_ability
            - difficulty_score * 0.42
            + prereq_boost
            + rng.gauss(0, 0.05),
            0.04,
            0.78,
        )

    kp_indices = []
    correct_flags = []
    focus_kp = _choose_focus_kp(
        kp_profiles, mastery, attempts, review_queue, profile, rng
    )
    session_remaining = 0
    session_count = 0

    for step in range(seq_len):
        if session_remaining <= 0:
            session_count += 1
            focus_kp = _choose_focus_kp(
                kp_profiles, mastery, attempts, review_queue, profile, rng
            )
            session_remaining = min(
                seq_len - step, max(4, int(rng.gauss(profile["session_span"], 2)))
            )
            gap_scale = 1 + rng.random() * 1.2
            for kp_id, current_mastery in list(mastery.items()):
                if attempts[kp_id] <= 0:
                    continue
                age = max(step - last_seen.get(kp_id, step), 1)
                decay = profile["forgetting_rate"] * gap_scale * min(age / 8, 1.6)
                decay *= 1.1 - kp_profiles[kp_id]["stability"] * 0.45
                mastery[kp_id] = _clamp(current_mastery - decay, 0.02, 0.98)
                if mastery[kp_id] < 0.55 and attempts[kp_id] > 0:
                    review_queue[kp_id] += 0.1

        session_progress = 1 - (session_remaining / max(profile["session_span"], 1))
        if rng.random() < 0.18:
            focus_kp = _choose_focus_kp(
                kp_profiles, mastery, attempts, review_queue, profile, rng
            )

        weights = []
        for kp_id in kp_ids:
            kp_profile = kp_profiles[kp_id]
            prereq_mastery = _mean(
                (
                    mastery.get(pre, 0.25 + profile["base_ability"] * 0.25)
                    for pre in kp_profile["prereqs"]
                ),
                default=0.92,
            )
            unlocked = (
                prereq_mastery >= 0.45
                or attempts[kp_id] > 0
                or not kp_profile["prereqs"]
            )

            weight = 0.05
            weight += (1 - mastery[kp_id]) * 0.75
            weight += min(review_queue[kp_id], 1.8) * profile["review_bias"]
            if attempts[kp_id] == 0:
                weight += 0.32 if unlocked else 0.03
            else:
                weight += min(attempts[kp_id], 4) * 0.02
            if kp_id == focus_kp:
                weight *= 1.9 + profile["focus_bias"] * 0.25
            elif (
                kp_profiles[focus_kp]["chapter"]
                and kp_profile["chapter"] == kp_profiles[focus_kp]["chapter"]
            ):
                weight *= 1.35
            elif kp_id in kp_profiles[focus_kp]["prereqs"] or kp_id in children_map.get(
                focus_kp, []
            ):
                weight *= 1.2
            if not unlocked:
                weight *= 0.22
            if recent_wrong[kp_id] > 0:
                weight *= 1.25 + min(recent_wrong[kp_id], 2) * 0.1
            if attempts[kp_id] > 0 and mastery[kp_id] > 0.78:
                weight *= 0.65
            weights.append(max(weight, 0.001))

        kp_id = rng.choices(kp_ids, weights=weights, k=1)[0]
        kp_profile = kp_profiles[kp_id]
        prereq_mastery = _mean(
            (
                mastery.get(pre, 0.25 + profile["base_ability"] * 0.25)
                for pre in kp_profile["prereqs"]
            ),
            default=0.95,
        )

        challenge_shift = rng.gauss(0, 0.06)
        if session_progress > 0.55 and mastery[kp_id] > 0.55:
            challenge_shift += 0.03
        elif session_progress < 0.25:
            challenge_shift -= 0.02
        item_difficulty = _clamp(kp_profile["difficulty"] + challenge_shift, 0.15, 0.96)

        recent_momentum = (_mean(last_results[-4:], default=0.5) - 0.5) * 0.45
        fatigue_penalty = (
            profile["fatigue_sensitivity"] * session_progress * (0.8 + item_difficulty)
        )
        review_bonus = 0.06 if review_queue[kp_id] > 0.45 else 0.0
        focus_bonus = 0.08 if kp_id == focus_kp else 0.0
        struggle_penalty = min(recent_wrong[kp_id], 3) * 0.05
        readiness_penalty = max(0.0, 0.52 - prereq_mastery) * 0.9

        latent_mastery = (
            mastery[kp_id] * 0.58
            + profile["base_ability"] * 0.22
            + prereq_mastery * 0.2
        )
        logit = (latent_mastery - item_difficulty) * 5.4
        logit += review_bonus + focus_bonus + recent_momentum
        logit -= fatigue_penalty + struggle_penalty + readiness_penalty
        base_prob = _sigmoid(logit)
        correct_prob = (
            profile["guess_rate"]
            + (1 - profile["guess_rate"] - profile["slip_rate"]) * base_prob
        )
        correct = 1 if rng.random() < _clamp(correct_prob, 0.02, 0.98) else 0

        gain = profile["learning_rate"] * (0.45 + item_difficulty * 0.65)
        if correct:
            mastery[kp_id] = _clamp(
                mastery[kp_id]
                + gain * (1 - mastery[kp_id]) * (0.72 + prereq_mastery * 0.18),
                0.02,
                0.995,
            )
            review_queue[kp_id] = max(review_queue[kp_id] * 0.45 - 0.08, 0.0)
            recent_wrong[kp_id] = 0
        else:
            mastery[kp_id] = _clamp(
                mastery[kp_id] - 0.02 * (1 - profile["persistence"]) + gain * 0.22,
                0.01,
                0.96,
            )
            review_queue[kp_id] += 0.65
            recent_wrong[kp_id] += 1
            for pre in kp_profile["prereqs"]:
                review_queue[pre] += 0.18

        for child_kp in children_map.get(kp_id, []):
            mastery[child_kp] = _clamp(
                mastery[child_kp] + (0.012 if correct else -0.004) * prereq_mastery,
                0.01,
                0.96,
            )

        attempts[kp_id] += 1
        last_seen[kp_id] = step
        kp_indices.append(str(kp_to_idx[kp_id]))
        correct_flags.append(str(correct))
        last_results.append(correct)
        session_remaining -= 1

    unique_kps = len(set(kp_indices))
    accuracy = sum(int(flag) for flag in correct_flags) / max(len(correct_flags), 1)
    revisit_ratio = 1 - unique_kps / max(len(kp_indices), 1)
    return {
        "kp_indices": kp_indices,
        "correct_flags": correct_flags,
        "accuracy": accuracy,
        "revisit_ratio": revisit_ratio,
        "unique_kps": unique_kps,
        "sessions": session_count,
        "profile": profile,
    }


# ──────────────────────────────────────────────────────────
# 1. 从数据库导出训练数据
# ──────────────────────────────────────────────────────────


def export_training_data(course_id=None, output_path=None, max_step=50):
    """
    从 AnswerHistory 导出 DKT 训练格式数据

    格式: 每个学生 3 行
        行1: 答题数 n
        行2: 知识点索引 (逗号分隔)
        行3: 正确标记 (逗号分隔, 0/1)

    Returns:
        (output_path, num_students, num_records)
    """
    if max_step < 2:
        raise ValueError("max_step 必须至少为 2，才能形成有效的 DKT 序列")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wisdom_edu_api.settings")
    import django

    django.setup()
    from assessments.models import AnswerHistory

    kp_to_idx, _ = _get_kp_mapping(course_id)
    if not kp_to_idx:
        print("[错误] 没有知识点数据，无法导出")
        return None, 0, 0

    # 按用户和时间排序获取答题历史
    qs = AnswerHistory.objects.select_related("question")
    if course_id:
        qs = qs.filter(course_id=course_id)
    qs = qs.order_by("user_id", "answered_at")

    # 按用户分组
    from collections import defaultdict

    user_seqs = defaultdict(list)
    for record in qs.iterator():
        kp_id = record.knowledge_point_id
        if kp_id and kp_id in kp_to_idx:
            user_seqs[record.user_id].append(
                {
                    "kp_idx": kp_to_idx[kp_id],
                    "correct": 1 if record.is_correct else 0,
                }
            )

    if not user_seqs:
        print("[警告] 没有有效的答题历史记录")
        return None, 0, 0

    # 写入文件
    if output_path is None:
        output_path = str(DEFAULT_TRAINING_DATA_PATH)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    total_records = 0
    with open(output_path, "w") as f:
        for user_id, seq in user_seqs.items():
            n = len(seq)
            total_records += n
            kp_indices = ",".join(str(s["kp_idx"]) for s in seq)
            correct_flags = ",".join(str(s["correct"]) for s in seq)
            f.write(f"{n}\n")
            f.write(f"{kp_indices}\n")
            f.write(f"{correct_flags}\n")

    print(
        f"[导出成功] {len(user_seqs)} 个学生, {total_records} 条记录 → {output_path} "
        f"(建议训练 max_step={max_step})"
    )
    return output_path, len(user_seqs), total_records


# ──────────────────────────────────────────────────────────
# 2. 合成训练数据
# ──────────────────────────────────────────────────────────


def generate_synthetic_data(
    course_id=None,
    num_students=200,
    min_seq=10,
    max_seq=80,
    output_path=None,
    seed=None,
):
    """
    生成合成的 DKT 训练数据

    合成策略（增强版）:
    - 每个学生都有不同画像：基础能力、学习速率、遗忘率、失误率、猜对率、复习倾向
    - 知识点难度由先修深度、层级、认知维度、标签、题目难度共同决定
    - 轨迹按“学习会话”生成，带有聚焦章节、复习回看、先修解锁和疲劳效应
    - 正确概率同时受掌握度、先修掌握、题目波动、近期状态与疲劳影响

    Returns:
        (output_path, num_students, total_records)
    """
    kp_to_idx, _ = _get_kp_mapping(course_id)
    q_size = len(kp_to_idx)
    if q_size == 0:
        print("[错误] 没有知识点数据，无法生成合成数据")
        return None, 0, 0

    rng = random.Random(seed)

    # 先修关系与知识点画像共同决定合成轨迹的难度与解锁逻辑。
    prereqs = _get_kp_prerequisites(course_id)
    kp_metadata = _get_kp_metadata(course_id)
    kp_profiles, children_map = _build_kp_profiles(kp_to_idx, prereqs, kp_metadata)

    # 生成学生序列
    if output_path is None:
        output_path = str(DEFAULT_TRAINING_DATA_PATH)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    total_records = 0
    accuracy_stats = []
    revisit_stats = []
    session_stats = []

    with open(output_path, "w") as f:
        for _ in range(num_students):
            profile = _sample_student_profile(rng)
            preferred_len = rng.triangular(
                min_seq, max_seq, min(max_seq, min_seq + (max_seq - min_seq) * 0.42)
            )
            if profile["archetype"] == "advanced":
                preferred_len += rng.uniform(3, 10)
            elif profile["archetype"] == "struggling":
                preferred_len -= rng.uniform(0, 6)
            seq_len = max(min_seq, min(max_seq, int(round(preferred_len))))

            student_seq = _simulate_student_sequence(
                kp_to_idx=kp_to_idx,
                kp_profiles=kp_profiles,
                children_map=children_map,
                rng=rng,
                seq_len=seq_len,
                student_profile=profile,
            )
            kp_indices = student_seq["kp_indices"]
            correct_flags = student_seq["correct_flags"]
            accuracy_stats.append(student_seq["accuracy"])
            revisit_stats.append(student_seq["revisit_ratio"])
            session_stats.append(student_seq["sessions"])

            total_records += seq_len
            f.write(f"{seq_len}\n")
            f.write(f"{','.join(kp_indices)}\n")
            f.write(f"{','.join(correct_flags)}\n")

    avg_accuracy = _mean(accuracy_stats, default=0.0)
    avg_revisit = _mean(revisit_stats, default=0.0)
    avg_sessions = _mean(session_stats, default=0.0)
    print(
        f"[合成数据] {num_students} 个虚拟学生, {total_records} 条记录, {q_size} 个知识点 → {output_path} "
        f"(平均正确率={avg_accuracy:.2%}, 平均复习占比={avg_revisit:.2%}, 平均会话数={avg_sessions:.1f})"
    )
    return output_path, num_students, total_records


# ──────────────────────────────────────────────────────────
# 3. 训练 DKT 模型
# ──────────────────────────────────────────────────────────


def train_dkt(
    data_path=None,
    course_id=None,
    epochs=100,
    batch_size=64,
    lr=0.002,
    hidden_dim=200,
    max_step=50,
    output_path=None,
    use_synthetic=False,
    public_dataset=None,
    blend_business_data=False,
    use_gpu=None,
):
    """
    训练 DKT 模型

    Args:
        data_path: 训练数据文件路径 (DKT 3行格式)
        course_id: 课程ID (用于确定知识点数量)
        epochs: 训练轮次
        batch_size: 批大小
        lr: 学习率
        hidden_dim: 隐藏层维度
        max_step: 最大序列步长
        output_path: 模型保存路径
        use_synthetic: 是否先生成合成数据再训练
        public_dataset: 是否先训练公开数据基线
        blend_business_data: 是否拼接业务答题数据
        use_gpu: 是否优先使用 GPU 训练
    """
    try:
        import torch
        import torch.optim as optim
    except ImportError:
        print("[错误] PyTorch 未安装，请运行: pip install torch")
        return False

    # 确定知识点数量
    q_size = _get_num_kp(course_id)
    if q_size == 0:
        print("[错误] 没有知识点数据")
        return False
    runtime_device = resolve_torch_device(use_gpu)
    device = runtime_device.device
    print(f"[信息] 知识点数量 Q={q_size}")
    print(f"[信息] DKT 训练设备: {runtime_device.label} ({runtime_device.reason})")

    # 准备数据
    if public_dataset:
        try:
            train_public_dataset_baseline(
                public_dataset,
                epochs=min(epochs, 60),
                batch_size=batch_size,
                lr=lr,
                hidden_dim=hidden_dim,
                max_step=max_step,
                use_gpu=use_gpu,
            )
        except Exception as exc:
            print(f"[警告] 公开数据集基线训练失败，继续进行课程模型训练: {exc}")

    if data_path is None and public_dataset and blend_business_data:
        data_path, _, _ = export_training_data(
            course_id=course_id,
            output_path=str(DEFAULT_TRAINING_DATA_PATH),
        )

    if use_synthetic or data_path is None:
        data_path, _, _ = generate_synthetic_data(
            course_id=course_id,
            output_path=str(DEFAULT_TRAINING_DATA_PATH),
        )
        if not data_path:
            return False
    else:
        if not Path(data_path).exists():
            print(f"[错误] 数据文件不存在: {data_path}")
            return False

    print("[信息] 加载训练数据...")
    all_kp_seqs, all_correct_seqs = _load_chunked_sequences_from_path(
        data_path,
        max_step,
    )

    print(f"[信息] 训练样本数: {len(all_kp_seqs)}")
    train_idx, test_idx = _split_train_test_indices(len(all_kp_seqs))

    sys.path.insert(0, str(BASE_DIR / "models" / "DKT" / "KnowledgeTracing"))
    from model.RNNModel import DKT

    input_dim = q_size * 2
    output_dim = q_size
    model = DKT(input_dim, hidden_dim, 1, output_dim).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)

    print(
        f"[信息] 模型参数: input={input_dim}, hidden={hidden_dim}, output={output_dim}"
    )
    print(f"[训练开始] epochs={epochs}, batch_size={batch_size}, lr={lr}")

    # DKT 损失函数: 二元交叉熵
    best_auc = 0.0
    if output_path is None:
        output_path = str(DEFAULT_RUNTIME_MODEL_PATH)

    for epoch in range(epochs):
        avg_loss, _ = _train_dkt_epoch(
            model,
            optimizer,
            train_idx,
            all_kp_seqs,
            all_correct_seqs,
            batch_size,
            q_size,
            max_step,
            device,
        )

        # Evaluation (every 10 epochs)
        if (epoch + 1) % 10 == 0 or epoch == 0:
            auc, sample_count = _evaluate_dkt_auc(
                model,
                all_kp_seqs,
                all_correct_seqs,
                test_idx,
                batch_size,
                q_size,
                max_step,
                device,
            )

            if sample_count > 0:
                print(
                    f"  Epoch {epoch + 1}/{epochs}  loss={avg_loss:.4f}  AUC={auc:.4f}  samples={sample_count}"
                )

                if auc > best_auc:
                    best_auc = auc
                    torch.save(_state_dict_to_cpu(model), output_path)
                    print(f"  [OK] 最佳模型已保存 (AUC={auc:.4f})")
            else:
                print(
                    f"  Epoch {epoch + 1}/{epochs}  loss={avg_loss:.4f}  (无有效评估样本)"
                )

    # 确保最终模型也保存
    if best_auc == 0:
        torch.save(_state_dict_to_cpu(model), output_path)
        print(f"[保存] 模型权重 → {output_path}")

    print(f"\n[训练完成] 最佳 AUC={best_auc:.4f}, 模型文件: {output_path}")
    print(f"[提示] 设置环境变量后重启服务即可使用:")
    print(f"  KT_DKT_MODEL_PATH={output_path}")
    print(f"  KT_DKT_NUM_QUESTIONS={q_size}")
    return True


# ──────────────────────────────────────────────────────────
# 4. 模型状态查看
# ──────────────────────────────────────────────────────────


def dkt_status():
    """查看 DKT 模型状态"""
    print("\n── DKT 模型状态 ──")

    model_path = os.getenv("KT_DKT_MODEL_PATH", "")
    default_path = DEFAULT_RUNTIME_MODEL_PATH

    if model_path and Path(model_path).exists():
        size = Path(model_path).stat().st_size
        print(f"  模型文件: {model_path} ({size / 1024:.1f} KB)")
    elif default_path.exists():
        size = default_path.stat().st_size
        print(f"  模型文件: {default_path} ({size / 1024:.1f} KB) (默认路径)")
    else:
        print("  模型文件: 未找到")
        print("  提示: 运行 python tools.py dkt-train --synthetic 训练模型")
        return

    q_size = _get_num_kp()
    print(f"  知识点数: {q_size}")

    num_q_env = os.getenv("KT_DKT_NUM_QUESTIONS", "")
    if num_q_env:
        print(f"  KT_DKT_NUM_QUESTIONS: {num_q_env}")
        if int(num_q_env) != q_size:
            print(f"  ⚠ 环境变量与数据库不一致! 数据库={q_size}, 环境变量={num_q_env}")
    else:
        print(f"  KT_DKT_NUM_QUESTIONS: 未设置 (将自动从数据库获取)")

    data_path = DEFAULT_TRAINING_DATA_PATH
    if data_path.exists():
        with open(data_path) as f:
            lines = f.readlines()
        n_students = len(lines) // 3
        print(f"  训练数据: {data_path} ({n_students} 学生)")
    else:
        print("  训练数据: 无")

    # 尝试加载模型测试
    try:
        from ai_services.services.dkt_inference import dkt_predictor

        effective_path = model_path or str(default_path)
        ok = dkt_predictor.load_model(effective_path, q_size)
        if ok:
            print("  加载测试: OK 成功")
            # 快速推理测试
            runtime_mode = str(dkt_predictor.get_info().get("runtime_mode") or "")
            raw_course_id = _get_first_course_with_kps()
            sample_course_id = (
                int(raw_course_id)
                if runtime_mode == "public_slot_adapter" and raw_course_id is not None
                else None
            )
            _, idx_to_kp = _get_kp_mapping(course_id=sample_course_id)
            sample_kps = list(idx_to_kp.values())[:2]
            if runtime_mode == "public_slot_adapter" and sample_course_id is None:
                print("  推理测试: SKIP 公开数据适配模式未找到可用课程上下文")
            elif not sample_kps:
                print("  推理测试: SKIP 未找到可用知识点样本")
            else:
                test_result = dkt_predictor.predict(
                    [
                        {"knowledge_point_id": sample_kps[0], "correct": 1},
                        {"knowledge_point_id": sample_kps[-1], "correct": 0},
                    ],
                    course_id=sample_course_id,
                )
                print(f"  推理测试: OK 预测了 {len(test_result['predictions'])} 个知识点")
        else:
            print("  加载测试: FAIL 失败")
    except Exception as e:
        print(f"  加载测试: FAIL {e}")

    print()
