#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 训练与状态管理工具。"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import cast

from platform_ai.kt.datasets import DEFAULT_PUBLIC_DATASET
from tools.mefkt_paths import MEFKT_META_PATH, MEFKT_MODEL_PATH, MEFKT_PUBLIC_BASELINE_DIR
from tools.mefkt_public_data import MEFKTTrainingBundle, _build_public_bundle
from tools.mefkt_training_support import (
    MEFKTTrainingConfig,
    train_mefkt_bundle,
)


logger = logging.getLogger(__name__)


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
    """兼容旧私有入口，实际训练委托给 support 模块。"""
    return train_mefkt_bundle(
        bundle=bundle,
        output_path=output_path,
        metadata_path=metadata_path,
        config=MEFKTTrainingConfig(
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
        ),
    )


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
    bundle = build_training_bundle(dataset_name, sequence_max_step, max_sequences)
    output = resolve_mefkt_output_path(dataset_name, output_path)
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
    print_training_result(result)
    return result


def build_training_bundle(
    dataset_name: str,
    sequence_max_step: int,
    max_sequences: int | None,
) -> MEFKTTrainingBundle:
    """构建并按需裁剪公开训练包。"""
    bundle = _build_public_bundle(dataset_name, sequence_max_step=sequence_max_step)
    if not max_sequences or len(bundle.sequences) <= max_sequences:
        return bundle
    return MEFKTTrainingBundle(
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


def resolve_mefkt_output_path(dataset_name: str, output_path: str | None) -> Path:
    """解析 MEFKT 模型输出路径。"""
    if output_path:
        return Path(output_path)
    if dataset_name == DEFAULT_PUBLIC_DATASET:
        return MEFKT_MODEL_PATH
    return MEFKT_PUBLIC_BASELINE_DIR / f"mefkt_{dataset_name}.pt"


def print_training_result(result: dict[str, object]) -> None:
    """输出 MEFKT 训练摘要。"""
    metrics_payload = cast(dict[str, float], result["metrics"])
    print(
        f"[MEFKT] 训练完成: dataset={result['training_dataset']}, "
        f"auc={metrics_payload['auc']:.4f}, acc={metrics_payload['acc']:.4f}, "
        f"path={result['model_path']}"
    )


def mefkt_status() -> dict[str, object]:
    """查看当前运行时 MEFKT 模型状态。"""
    if not MEFKT_META_PATH.exists():
        return print_mefkt_status({
            "is_available": False,
            "model_path": str(MEFKT_MODEL_PATH),
            "metadata_path": str(MEFKT_META_PATH),
        })

    metadata = json.loads(MEFKT_META_PATH.read_text(encoding="utf-8"))
    return print_mefkt_status({
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
    })


def print_mefkt_status(status: dict[str, object]) -> dict[str, object]:
    """打印并返回 MEFKT 状态。"""
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return status


__all__ = ["MEFKTTrainingBundle", "mefkt_status", "train_mefkt_v2"]
