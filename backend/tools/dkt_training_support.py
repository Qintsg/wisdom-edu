#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""DKT 训练与状态展示辅助工具。"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from platform_ai.kt.datasets import get_public_dataset_info
from platform_ai.kt.torch_device import resolve_torch_device
from tools.dkt_data_access import _get_first_course_with_kps, _get_kp_mapping, _get_num_kp
from tools.dkt_paths import BASE_DIR, DEFAULT_RUNTIME_MODEL_PATH, DEFAULT_TRAINING_DATA_PATH, PUBLIC_BASELINE_DIR, RUNTIME_METADATA_PATH
from tools.dkt_sequences import _evaluate_dkt_auc, _load_chunked_sequences_from_path, _split_train_test_indices, _train_dkt_epoch


@dataclass
class PublicBaselineTrainingContext:
    """公开数据集基线训练准备结果。"""

    dataset_name: str
    dataset_info: Any
    runtime_device: Any
    all_kp_seqs: list[list[int]]
    all_correct_seqs: list[list[int]]
    q_size: int
    train_idx: list[int]
    test_idx: list[int]
    baseline_model_path: Path


def write_runtime_metadata(**payload: object) -> None:
    """写入运行时模型元数据。"""
    RUNTIME_METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME_METADATA_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def to_project_relative_path(path_value: str | Path) -> str:
    """将项目内路径规范为相对路径，便于跨环境复用。"""
    try:
        return str(Path(path_value).resolve().relative_to(BASE_DIR)).replace("\\", "/")
    except (OSError, RuntimeError, ValueError):
        return str(path_value).replace("\\", "/")


def state_dict_to_cpu(model) -> dict[str, Any]:
    """保存前将参数转回 CPU，确保运行时跨设备加载稳定。"""
    return {key: value.detach().cpu() for key, value in model.state_dict().items()}


def import_torch_modules(*, with_optimizer: bool) -> tuple[Any, Any | None]:
    """导入 PyTorch 及可选优化器模块。"""
    try:
        import torch
        if with_optimizer:
            import torch.optim as optim
            return torch, optim
        return torch, None
    except ImportError:
        print("[错误] PyTorch 未安装，请运行: pip install torch")
        return None, None


def load_dkt_model_class():
    """按仓库路径加载 DKT 模型实现。"""
    sys.path.insert(0, str(BASE_DIR / "models" / "DKT" / "KnowledgeTracing"))
    from model.RNNModel import DKT

    return DKT


def prepare_public_baseline_training(
    *,
    dataset_name: str,
    max_step: int,
    use_gpu: bool | None,
) -> PublicBaselineTrainingContext:
    """准备公开数据基线训练上下文。"""
    dataset_info = get_public_dataset_info(dataset_name)
    if not dataset_info.is_available:
        raise FileNotFoundError(f"公开数据集不可用: {dataset_name}")
    if not dataset_info.train_path:
        raise FileNotFoundError(f"公开数据集缺少训练文件路径: {dataset_name}")

    runtime_device = resolve_torch_device(use_gpu)
    all_kp_seqs, all_correct_seqs = _load_chunked_sequences_from_path(dataset_info.train_path, max_step)
    if not all_kp_seqs:
        raise ValueError(f"公开数据集没有可用训练样本: {dataset_name}")

    q_size = max(max(sequence) for sequence in all_kp_seqs if sequence) + 1
    train_idx, test_idx = _split_train_test_indices(len(all_kp_seqs))
    PUBLIC_BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    return PublicBaselineTrainingContext(
        dataset_name=dataset_name,
        dataset_info=dataset_info,
        runtime_device=runtime_device,
        all_kp_seqs=all_kp_seqs,
        all_correct_seqs=all_correct_seqs,
        q_size=q_size,
        train_idx=list(train_idx),
        test_idx=list(test_idx),
        baseline_model_path=PUBLIC_BASELINE_DIR / f"{dataset_name}.pt",
    )


def run_public_baseline_training_loop(
    *,
    torch_module,
    model,
    optimizer,
    context: PublicBaselineTrainingContext,
    epochs: int,
    batch_size: int,
    max_step: int,
) -> dict[str, Any]:
    """执行公开数据集基线训练循环并返回最佳指标。"""
    best_auc = 0.0
    best_metrics = {"auc": 0.0, "samples": 0}
    for epoch in range(epochs):
        _train_dkt_epoch(
            model,
            optimizer,
            context.train_idx,
            context.all_kp_seqs,
            context.all_correct_seqs,
            batch_size,
            context.q_size,
            max_step,
            context.runtime_device.device,
        )
        if (epoch + 1) % 10 != 0 and epoch != 0:
            continue
        auc, sample_count = _evaluate_dkt_auc(
            model,
            context.all_kp_seqs,
            context.all_correct_seqs,
            context.test_idx,
            batch_size,
            context.q_size,
            max_step,
            context.runtime_device.device,
        )
        if sample_count <= 0:
            continue
        if auc > best_auc:
            best_auc = auc
            best_metrics = {"auc": auc, "samples": sample_count}
            torch_module.save(state_dict_to_cpu(model), context.baseline_model_path)
    if not context.baseline_model_path.exists():
        torch_module.save(state_dict_to_cpu(model), context.baseline_model_path)
    return best_metrics


def run_course_training_loop(
    *,
    torch_module,
    model,
    optimizer,
    train_idx,
    test_idx,
    all_kp_seqs,
    all_correct_seqs,
    batch_size: int,
    q_size: int,
    max_step: int,
    device,
    epochs: int,
    output_path: str,
) -> float:
    """执行课程范围 DKT 训练循环并返回最佳 AUC。"""
    best_auc = 0.0
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
        if sample_count > 0:
            print(f"  Epoch {epoch + 1}/{epochs}  loss={avg_loss:.4f}  AUC={auc:.4f}  samples={sample_count}")
            if auc > best_auc:
                best_auc = auc
                torch_module.save(state_dict_to_cpu(model), output_path)
                print(f"  [OK] 最佳模型已保存 (AUC={auc:.4f})")
        else:
            print(f"  Epoch {epoch + 1}/{epochs}  loss={avg_loss:.4f}  (无有效评估样本)")
    if best_auc == 0:
        torch_module.save(state_dict_to_cpu(model), output_path)
        print(f"[保存] 模型权重 → {output_path}")
    return best_auc


def build_public_runtime_metadata(
    *,
    runtime_model_path: Path,
    baseline_result: dict[str, Any],
    baseline_epochs: int,
    batch_size: int,
    learning_rate: float,
    hidden_dim: int,
    dataset_name: str,
    blend_business_data: bool,
    course_id,
    data_path,
    use_synthetic: bool,
) -> dict[str, Any]:
    """构造公开数据运行时模型元数据载荷。"""
    return {
        "model_path": to_project_relative_path(str(runtime_model_path)),
        "runtime_schema": "public_slot_adapter_v1",
        "slot_count": baseline_result["q_size"],
        "knowledge_point_count": baseline_result["q_size"],
        "epochs": baseline_epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "hidden_dim": hidden_dim,
        "training_sources": [to_project_relative_path(str(baseline_result["train_path"]))],
        "public_dataset": dataset_name,
        "training_device": baseline_result.get("training_device"),
        "public_baseline": {
            **baseline_result,
            "model_path": to_project_relative_path(str(baseline_result["model_path"])),
            "train_path": to_project_relative_path(str(baseline_result["train_path"])),
        },
        "blend_business_data": False,
        "public_training_only": True,
        "blend_business_data_requested": bool(blend_business_data),
        "course_id_ignored": course_id is not None,
        "data_path_ignored": bool(data_path),
        "use_synthetic_ignored": bool(use_synthetic),
    }


def resolve_status_model_path() -> tuple[Path | None, str]:
    """解析状态检查时的模型路径。"""
    model_path = Path(str(DEFAULT_RUNTIME_MODEL_PATH))
    env_model_path = Path(str(DEFAULT_RUNTIME_MODEL_PATH))
    raw_model_path = ""
    import os

    raw_model_path = os.getenv("KT_DKT_MODEL_PATH", "")
    if raw_model_path and Path(raw_model_path).exists():
        return Path(raw_model_path), raw_model_path
    if model_path.exists():
        return model_path, str(model_path)
    return None, raw_model_path


def build_status_probe_context():
    """构造 dkt_status 里推理探针需要的课程与知识点上下文。"""
    raw_course_id = _get_first_course_with_kps()
    sample_course_id = int(raw_course_id) if raw_course_id is not None else None
    _, idx_to_kp = _get_kp_mapping(course_id=sample_course_id)
    sample_kps = list(idx_to_kp.values())[:2]
    return sample_course_id, sample_kps


def count_training_sequences(data_path: Path) -> int:
    """统计标准三行训练数据包含的学生序列数。"""
    with open(data_path, encoding="utf-8") as handle:
        lines = handle.readlines()
    return len(lines) // 3


def print_status_model_info(model_file: Path, raw_model_path: str) -> None:
    """打印状态检查中的模型文件信息。"""
    size = model_file.stat().st_size
    if raw_model_path and Path(raw_model_path).exists():
        print(f"  模型文件: {raw_model_path} ({size / 1024:.1f} KB)")
    else:
        print(f"  模型文件: {model_file} ({size / 1024:.1f} KB) (默认路径)")


def run_status_probe(*, dkt_predictor, effective_path: str, q_size: int) -> None:
    """执行 dkt_status 的推理探针输出。"""
    ok = dkt_predictor.load_model(effective_path, q_size)
    if not ok:
        print("  加载测试: FAIL 失败")
        return

    print("  加载测试: OK 成功")
    runtime_mode = str(dkt_predictor.get_info().get("runtime_mode") or "")
    sample_course_id, sample_kps = build_status_probe_context()
    sample_course_id = sample_course_id if runtime_mode == "public_slot_adapter" else None
    if runtime_mode == "public_slot_adapter" and sample_course_id is None:
        print("  推理测试: SKIP 公开数据适配模式未找到可用课程上下文")
        return
    if not sample_kps:
        print("  推理测试: SKIP 未找到可用知识点样本")
        return

    test_result = dkt_predictor.predict(
        [
            {"knowledge_point_id": sample_kps[0], "correct": 1},
            {"knowledge_point_id": sample_kps[-1], "correct": 0},
        ],
        course_id=sample_course_id,
    )
    print(f"  推理测试: OK 预测了 {len(test_result['predictions'])} 个知识点")
