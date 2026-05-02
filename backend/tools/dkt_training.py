#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""DKT 训练管线与兼容入口。"""

from __future__ import annotations

import json
import os
from pathlib import Path

from platform_ai.kt.datasets import DEFAULT_PUBLIC_DATASET
from platform_ai.kt.torch_device import resolve_torch_device
from tools.dkt_data_access import (
    _get_num_kp,
    export_training_data,
)
from tools.dkt_paths import (
    DEFAULT_RUNTIME_MODEL_PATH,
    DEFAULT_TRAINING_DATA_PATH,
)
from tools.dkt_sequences import _load_chunked_sequences_from_path, _split_train_test_indices
from tools.dkt_synthetic import (
    _build_kp_profiles,
    _simulate_student_sequence,
    generate_synthetic_data,
)
from tools.dkt_training_support import (
    build_public_runtime_metadata,
    count_training_sequences,
    import_torch_modules,
    load_dkt_model_class,
    print_status_model_info,
    prepare_public_baseline_training,
    resolve_status_model_path,
    run_course_training_loop,
    run_public_baseline_training_loop,
    run_status_probe,
    state_dict_to_cpu,
    write_runtime_metadata,
)


def train_public_dataset_baseline(dataset_name, epochs=40, batch_size=64, lr=0.002, hidden_dim=200, max_step=50, use_gpu=None):
    """训练公开数据集基线模型。"""
    torch, optim = import_torch_modules(with_optimizer=True)
    if torch is None or optim is None:
        return None

    context = prepare_public_baseline_training(
        dataset_name=dataset_name,
        max_step=max_step,
        use_gpu=use_gpu,
    )
    print(f"[公开基线] 数据集={dataset_name}, 样本={len(context.all_kp_seqs)}, Q={context.q_size}")
    DKT = load_dkt_model_class()
    model = DKT(context.q_size * 2, hidden_dim, 1, context.q_size).to(context.runtime_device.device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    print(f"[公开基线] 训练设备={context.runtime_device.label}, reason={context.runtime_device.reason}")
    best_metrics = run_public_baseline_training_loop(
        torch_module=torch,
        model=model,
        optimizer=optimizer,
        context=context,
        epochs=epochs,
        batch_size=batch_size,
        max_step=max_step,
    )

    return {
        "dataset": dataset_name,
        "model_path": str(context.baseline_model_path),
        "metrics": best_metrics,
        "q_size": context.q_size,
        "train_path": str(context.dataset_info.train_path),
        "training_device": context.runtime_device.label,
    }


def train_dkt_v2(data_path=None, course_id=None, epochs=100, batch_size=64, lr=0.002, hidden_dim=200, max_step=50, output_path=None, use_synthetic=False, public_dataset=None, blend_business_data=False, use_gpu=None):
    """执行增强版 DKT 训练入口，默认生成公开数据运行时适配模型。"""
    torch, _ = import_torch_modules(with_optimizer=False)
    if torch is None:
        return False

    dataset_name = (public_dataset or DEFAULT_PUBLIC_DATASET).strip().lower()
    baseline_epochs = max(20, min(int(epochs), 80))
    baseline_result = train_public_dataset_baseline(dataset_name, baseline_epochs, batch_size, lr, hidden_dim, max_step, use_gpu)
    if not baseline_result:
        print("[错误] DKT 公开数据基线训练失败")
        return False

    runtime_model_path = Path(output_path) if output_path else DEFAULT_RUNTIME_MODEL_PATH
    runtime_model_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_state = torch.load(baseline_result["model_path"], map_location="cpu", weights_only=True)
    torch.save(baseline_state, runtime_model_path)
    write_runtime_metadata(
        **build_public_runtime_metadata(
            runtime_model_path=runtime_model_path,
            baseline_result=baseline_result,
            baseline_epochs=baseline_epochs,
            batch_size=batch_size,
            learning_rate=lr,
            hidden_dim=hidden_dim,
            dataset_name=dataset_name,
            blend_business_data=blend_business_data,
            course_id=course_id,
            data_path=data_path,
            use_synthetic=use_synthetic,
        )
    )
    print(f"\n[训练完成] 已使用公开数据集 {dataset_name} 生成 DKT 运行时模型: {runtime_model_path}")
    print(f"[适配说明] 运行时将通过 public_slot_adapter_v1 将课程题目/知识点映射到 {baseline_result['q_size']} 个公共槽位")
    return True


def train_dkt(data_path=None, course_id=None, epochs=100, batch_size=64, lr=0.002, hidden_dim=200, max_step=50, output_path=None, use_synthetic=False, public_dataset=None, blend_business_data=False, use_gpu=None):
    """训练传统课程范围 DKT 模型。"""
    torch, optim = import_torch_modules(with_optimizer=True)
    if torch is None or optim is None:
        return False

    q_size = _get_num_kp(course_id)
    if q_size == 0:
        print("[错误] 没有知识点数据")
        return False
    runtime_device = resolve_torch_device(use_gpu)
    print(f"[信息] 知识点数量 Q={q_size}")
    print(f"[信息] DKT 训练设备: {runtime_device.label} ({runtime_device.reason})")

    if public_dataset:
        try:
            train_public_dataset_baseline(public_dataset, min(epochs, 60), batch_size, lr, hidden_dim, max_step, use_gpu)
        except Exception as exc:
            print(f"[警告] 公开数据集基线训练失败，继续进行课程模型训练: {exc}")

    if data_path is None and public_dataset and blend_business_data:
        data_path, _, _ = export_training_data(course_id=course_id, output_path=str(DEFAULT_TRAINING_DATA_PATH))
    if use_synthetic or data_path is None:
        data_path, _, _ = generate_synthetic_data(course_id=course_id, output_path=str(DEFAULT_TRAINING_DATA_PATH))
        if not data_path:
            return False
    elif not Path(data_path).exists():
        print(f"[错误] 数据文件不存在: {data_path}")
        return False

    print("[信息] 加载训练数据...")
    all_kp_seqs, all_correct_seqs = _load_chunked_sequences_from_path(data_path, max_step)
    print(f"[信息] 训练样本数: {len(all_kp_seqs)}")
    train_idx, test_idx = _split_train_test_indices(len(all_kp_seqs))

    DKT = load_dkt_model_class()
    model = DKT(q_size * 2, hidden_dim, 1, q_size).to(runtime_device.device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    print(f"[信息] 模型参数: input={q_size * 2}, hidden={hidden_dim}, output={q_size}")
    print(f"[训练开始] epochs={epochs}, batch_size={batch_size}, lr={lr}")
    output_path = output_path or str(DEFAULT_RUNTIME_MODEL_PATH)
    best_auc = run_course_training_loop(
        torch_module=torch,
        model=model,
        optimizer=optimizer,
        train_idx=train_idx,
        test_idx=test_idx,
        all_kp_seqs=all_kp_seqs,
        all_correct_seqs=all_correct_seqs,
        batch_size=batch_size,
        q_size=q_size,
        max_step=max_step,
        device=runtime_device.device,
        epochs=epochs,
        output_path=output_path,
    )

    print(f"\n[训练完成] 最佳 AUC={best_auc:.4f}, 模型文件: {output_path}")
    print("[提示] 设置环境变量后重启服务即可使用:")
    print(f"  KT_DKT_MODEL_PATH={output_path}")
    print(f"  KT_DKT_NUM_QUESTIONS={q_size}")
    return True


def dkt_status():
    """查看 DKT 模型状态。"""
    print("\n── DKT 模型状态 ──")
    model_file, raw_model_path = resolve_status_model_path()
    if model_file and model_file.exists():
        print_status_model_info(model_file, raw_model_path)
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
        print("  KT_DKT_NUM_QUESTIONS: 未设置 (将自动从数据库获取)")

    data_path = DEFAULT_TRAINING_DATA_PATH
    if data_path.exists():
        print(f"  训练数据: {data_path} ({count_training_sequences(data_path)} 学生)")
    else:
        print("  训练数据: 无")

    try:
        from ai_services.services.dkt_inference import dkt_predictor

        effective_path = raw_model_path or str(DEFAULT_RUNTIME_MODEL_PATH)
        run_status_probe(dkt_predictor=dkt_predictor, effective_path=effective_path, q_size=q_size)
    except Exception as exc:
        print(f"  加载测试: FAIL {exc}")
    print()


__all__ = [
    "dkt_status",
    "export_training_data",
    "generate_synthetic_data",
    "train_dkt",
    "train_dkt_v2",
    "train_public_dataset_baseline",
    "_build_kp_profiles",
    "_simulate_student_sequence",
]
