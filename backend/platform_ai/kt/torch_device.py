"""KT 运行时与训练流程共享的 PyTorch 设备选择工具。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import torch


TRUTHY_VALUES = {"1", "true", "yes", "y", "on"}


# 维护意图：统一描述当前 KT 训练/推理使用的设备决策结果
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class TorchRuntimeDevice:
    """统一描述当前 KT 训练/推理使用的设备决策结果。"""

    device: "torch.device"
    requested_gpu: bool
    using_gpu: bool
    label: str
    reason: str


# 维护意图：将环境变量解析成布尔值，避免各处重复手写真假判断
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _parse_bool_env(name: str, default: bool = False) -> bool:
    """将环境变量解析成布尔值，避免各处重复手写真假判断。"""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in TRUTHY_VALUES


# 维护意图：根据显式参数与 KT_USE_GPU 环境变量解析 PyTorch 设备
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_torch_device(use_gpu: bool | None = None) -> TorchRuntimeDevice:
    """根据显式参数与 KT_USE_GPU 环境变量解析 PyTorch 设备。"""
    import torch

    requested_gpu = _parse_bool_env("KT_USE_GPU") if use_gpu is None else bool(use_gpu)
    if requested_gpu and torch.cuda.is_available():
        current_index = torch.cuda.current_device()
        return TorchRuntimeDevice(
            device=torch.device("cuda"),
            requested_gpu=True,
            using_gpu=True,
            label=f"cuda:{current_index}",
            reason=torch.cuda.get_device_name(current_index),
        )
    if requested_gpu:
        return TorchRuntimeDevice(
            device=torch.device("cpu"),
            requested_gpu=True,
            using_gpu=False,
            label="cpu",
            reason="cuda_unavailable",
        )
    return TorchRuntimeDevice(
        device=torch.device("cpu"),
        requested_gpu=False,
        using_gpu=False,
        label="cpu",
        reason="gpu_disabled",
    )
