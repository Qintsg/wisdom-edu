"""MEFKT checkpoint 加载与旧版知识点级推理。"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

from platform_ai.kt.torch_device import resolve_torch_device
from .mefkt_runtime import _append_history_outcome, _build_sorted_history_records

if TYPE_CHECKING:
    from models.MEFKT.model import MEFKTSequenceModel
    from torch import Tensor


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LoadedMEFKTState:
    """MEFKT checkpoint 加载后的 predictor 状态。"""

    runtime_mode: str
    model: "MEFKTSequenceModel | None"
    metadata: dict[str, object]
    model_path: str
    metadata_path: str
    device_label: str
    torch_device: object
    item_id_to_index: dict[int, int]
    index_to_item_id: dict[int, int]
    sequence_state_dict: dict[str, "Tensor"]
    graph_state_dict: dict[str, "Tensor"]
    attribute_state_dict: dict[str, "Tensor"]
    fusion_state_dict: dict[str, "Tensor"]


def resolve_backend_path(path_value: str | None, backend_root: Path) -> Path | None:
    """将环境变量中的模型路径统一解析为后端根目录下的绝对路径。"""
    if path_value is None:
        return None
    normalized = str(path_value).strip()
    if not normalized:
        return None
    candidate = Path(normalized)
    if candidate.is_absolute():
        return candidate
    return (backend_root / candidate).resolve()


def load_mefkt_state(
    *,
    model_path: str,
    metadata_path: str | None,
    backend_root: Path,
) -> LoadedMEFKTState | None:
    """加载 MEFKT checkpoint 并构造运行时状态。"""
    try:
        import torch
    except ImportError:
        logger.error("PyTorch 未安装，无法加载 MEFKT 模型")
        return None

    model_file = resolve_backend_path(model_path, backend_root)
    if model_file is None or not model_file.exists():
        logger.error("MEFKT 模型文件不存在: %s", model_path)
        return None

    metadata_file = resolve_metadata_path(model_file, metadata_path, backend_root)
    checkpoint = torch.load(str(model_file), map_location="cpu", weights_only=False)
    metadata_payload = load_metadata_payload(checkpoint, metadata_file)
    runtime_device = resolve_torch_device()
    if is_question_online_checkpoint(metadata_payload, checkpoint):
        return build_question_online_state(
            checkpoint=checkpoint,
            metadata_payload=metadata_payload,
            model_file=model_file,
            metadata_file=metadata_file,
            runtime_device=runtime_device,
        )
    return build_legacy_state(
        checkpoint=checkpoint,
        metadata_payload=metadata_payload,
        model_file=model_file,
        metadata_file=metadata_file,
        runtime_device=runtime_device,
    )


def resolve_metadata_path(model_file: Path, metadata_path: str | None, backend_root: Path) -> Path:
    """解析 MEFKT 元数据文件路径。"""
    return (
        resolve_backend_path(metadata_path, backend_root) if metadata_path else None
    ) or model_file.with_suffix(".meta.json")


def load_metadata_payload(checkpoint: dict[str, object], metadata_file: Path) -> dict[str, object]:
    """优先读取外部元数据，失败时回退 checkpoint 内嵌元数据。"""
    metadata_payload = dict(checkpoint.get("metadata") or {})
    if not metadata_file.exists():
        return metadata_payload
    try:
        return json.loads(metadata_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.warning("MEFKT 元数据解析失败，回退到 checkpoint 内嵌元数据")
        return metadata_payload


def is_question_online_checkpoint(
    metadata_payload: dict[str, object],
    checkpoint: dict[str, object],
) -> bool:
    """判断 checkpoint 是否为题目级在线运行时格式。"""
    runtime_schema = str(metadata_payload.get("runtime_schema") or "").strip()
    return runtime_schema == "question_online_v1" and bool(checkpoint.get("graph_state_dict"))


def build_question_online_state(
    *,
    checkpoint: dict[str, object],
    metadata_payload: dict[str, object],
    model_file: Path,
    metadata_file: Path,
    runtime_device,
) -> LoadedMEFKTState:
    """构造题目级在线 MEFKT 状态。"""
    state = LoadedMEFKTState(
        runtime_mode="question_online",
        model=None,
        metadata=metadata_payload,
        model_path=str(model_file),
        metadata_path=str(metadata_file),
        device_label=runtime_device.label,
        torch_device=runtime_device.device,
        item_id_to_index={},
        index_to_item_id={},
        sequence_state_dict=cast_tensor_state(
            checkpoint.get("sequence_state_dict") or checkpoint.get("state_dict") or {}
        ),
        graph_state_dict=cast_tensor_state(checkpoint.get("graph_state_dict") or {}),
        attribute_state_dict=cast_tensor_state(checkpoint.get("attribute_state_dict") or {}),
        fusion_state_dict=cast_tensor_state(checkpoint.get("fusion_state_dict") or {}),
    )
    logger.info(
        "MEFKT 题目级在线模型加载成功: dataset=%s, device=%s, path=%s",
        metadata_payload.get("training_dataset"),
        runtime_device.label,
        model_file,
    )
    return state


def build_legacy_state(
    *,
    checkpoint: dict[str, object],
    metadata_payload: dict[str, object],
    model_file: Path,
    metadata_file: Path,
    runtime_device,
) -> LoadedMEFKTState | None:
    """构造旧版知识点级 MEFKT 状态。"""
    from models.MEFKT.model import MEFKTSequenceModel

    item_ids = [int(item_id) for item_id in metadata_payload.get("item_ids", [])]
    item_count = int(metadata_payload.get("item_count") or len(item_ids))
    if item_count <= 0:
        logger.error("MEFKT 元数据缺少有效 item_count")
        return None
    if not item_ids:
        item_ids = list(range(item_count))

    model = MEFKTSequenceModel(
        item_count=item_count,
        item_embedding_dim=int(metadata_payload.get("embedding_dim") or 256),
        num_heads=int(metadata_payload.get("num_heads") or 4),
        head_dim=int(metadata_payload.get("head_dim") or 32),
    ).to(runtime_device.device)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    logger.info(
        "MEFKT 旧版模型加载成功: items=%d, device=%s, path=%s",
        item_count,
        runtime_device.label,
        model_file,
    )
    return LoadedMEFKTState(
        runtime_mode="legacy",
        model=model,
        metadata=metadata_payload,
        model_path=str(model_file),
        metadata_path=str(metadata_file),
        device_label=runtime_device.label,
        torch_device=runtime_device.device,
        item_id_to_index={int(item_id): index for index, item_id in enumerate(item_ids)},
        index_to_item_id={index: int(item_id) for index, item_id in enumerate(item_ids)},
        sequence_state_dict={},
        graph_state_dict={},
        attribute_state_dict={},
        fusion_state_dict={},
    )


def cast_tensor_state(raw_state: object) -> dict[str, "Tensor"]:
    """将 checkpoint state 字段收窄为 Tensor 字典。"""
    return cast(dict[str, "Tensor"], dict(raw_state or {}))


def predict_legacy_mastery(
    *,
    model: "MEFKTSequenceModel",
    item_id_to_index: dict[int, int],
    answer_history: list[dict[str, object]],
    knowledge_point_ids: list[int] | None,
    torch_device: object,
) -> dict[str, object]:
    """执行旧版知识点级 checkpoint 推理。"""
    import torch

    history_indices, history_correct, history_gap_hours, recognized_count = build_history_tensors_legacy(
        answer_history,
        item_id_to_index,
    )
    known_target_ids = resolve_legacy_target_ids(
        answer_history=answer_history,
        knowledge_point_ids=knowledge_point_ids,
        item_id_to_index=item_id_to_index,
    )
    if not known_target_ids:
        return empty_legacy_prediction()

    probability_tensor = predict_legacy_candidates(
        model=model,
        item_id_to_index=item_id_to_index,
        known_target_ids=known_target_ids,
        history_indices=history_indices,
        history_correct=history_correct,
        history_gap_hours=history_gap_hours,
        torch_device=torch_device or torch.device("cpu"),
        torch_module=torch,
    )
    predictions = {
        item_id: round(float(probability), 4)
        for item_id, probability in zip(known_target_ids, probability_tensor.detach().cpu().tolist(), strict=True)
    }
    confidence = legacy_confidence(
        recognized_count=recognized_count,
        history_count=len(history_indices),
        answer_count=len(answer_history),
    )
    return {
        "predictions": predictions,
        "confidence": confidence,
        "model_type": "mefkt_real",
        "analysis": f"MEFKT 推理完成：识别 {recognized_count}/{len(answer_history)} 条有效交互，输出 {len(predictions)} 个知识点掌握度",
    }


def build_history_tensors_legacy(
    answer_history: list[dict[str, object]],
    item_id_to_index: dict[int, int],
) -> tuple[list[int], list[int], list[float], int]:
    """将旧版知识点历史转成模型输入格式。"""
    history_indices: list[int] = []
    history_correct: list[int] = []
    history_gap_hours: list[float] = []
    recognized_count = 0
    previous_time = None
    for _, current_time, record in _build_sorted_history_records(answer_history):
        item_id_raw = record.get("knowledge_point_id")
        if item_id_raw is None:
            continue
        item_id = int(str(item_id_raw))
        if item_id not in item_id_to_index:
            continue
        recognized_count += 1
        history_indices.append(item_id_to_index[item_id])
        previous_time = _append_history_outcome(
            history_correct=history_correct,
            history_gap_hours=history_gap_hours,
            record=record,
            current_time=current_time,
            previous_time=previous_time,
        )
    return history_indices, history_correct, history_gap_hours, recognized_count


def resolve_legacy_target_ids(
    *,
    answer_history: list[dict[str, object]],
    knowledge_point_ids: list[int] | None,
    item_id_to_index: dict[int, int],
) -> list[int]:
    """解析旧版预测目标知识点。"""
    target_ids = set(int(item_id) for item_id in (knowledge_point_ids or []))
    if not target_ids:
        target_ids.update(
            int(str(record["knowledge_point_id"]))
            for record in answer_history
            if record.get("knowledge_point_id") is not None
        )
    return [item_id for item_id in sorted(target_ids) if item_id in item_id_to_index]


def empty_legacy_prediction() -> dict[str, object]:
    """旧版模型无法识别知识点时的稳定响应。"""
    return {
        "predictions": {},
        "confidence": 0.0,
        "model_type": "mefkt",
        "analysis": "MEFKT 未识别到可用知识点，无法输出掌握度预测",
    }


def predict_legacy_candidates(
    *,
    model: "MEFKTSequenceModel",
    item_id_to_index: dict[int, int],
    known_target_ids: list[int],
    history_indices: list[int],
    history_correct: list[int],
    history_gap_hours: list[float],
    torch_device: object,
    torch_module,
):
    """预测旧版候选知识点掌握概率。"""
    candidate_tensor = torch_module.tensor(
        [item_id_to_index[item_id] for item_id in known_target_ids],
        dtype=torch_module.long,
        device=torch_device,
    )
    if not history_indices:
        return torch_module.full(
            (len(known_target_ids),),
            0.25,
            dtype=torch_module.float32,
            device=torch_device,
        )
    return model.predict_candidate(
        history_item_indices=torch_module.tensor(history_indices, dtype=torch_module.long, device=torch_device),
        history_correct_flags=torch_module.tensor(history_correct, dtype=torch_module.long, device=torch_device),
        history_time_gaps=torch_module.tensor(history_gap_hours, dtype=torch_module.float32, device=torch_device),
        candidate_item_indices=candidate_tensor,
    )


def legacy_confidence(*, recognized_count: int, history_count: int, answer_count: int) -> float:
    """计算旧版 MEFKT 预测置信度。"""
    history_coverage = recognized_count / max(answer_count, 1)
    confidence = min(0.9, 0.42 + history_count / 30.0 * 0.28 + history_coverage * 0.2)
    return round(confidence, 3)
