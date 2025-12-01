"""
DKT (Deep Knowledge Tracing) 推理模块。

当前实现同时兼容两类运行时：
1. 旧版知识点维度 checkpoint；
2. 公开数据训练得到的“公共槽位 + 项目内映射”适配模式。
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from platform_ai.kt.torch_device import resolve_torch_device

logger = logging.getLogger(__name__)
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_backend_path(path_value: str | None) -> Path | None:
    """将环境变量中的模型路径统一解析为后端根目录下的绝对路径。"""
    if path_value is None:
        return None
    normalized = str(path_value).strip()
    if not normalized:
        return None
    candidate = Path(normalized)
    if candidate.is_absolute():
        return candidate
    return (BACKEND_ROOT / candidate).resolve()


def _resolve_metadata_path(model_path: Path, metadata_path: str | None) -> Path:
    """解析元数据路径，空白输入回退到模型旁的默认 metadata 文件。"""
    resolved = _resolve_backend_path(metadata_path)
    if resolved is not None:
        return resolved
    return model_path.with_suffix(".meta.json")


def _coerce_optional_int(value: object) -> int | None:
    """将动态字典中的值安全转换为整数。"""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class CourseSlotBundle:
    """课程知识点/题目到公共槽位的稳定映射。"""

    question_to_slot: dict[int, int]
    point_to_slots: dict[int, list[int]]
    representative_slot: dict[int, int]


def _load_global_kp_mapping() -> tuple[dict[int, int], list[int]]:
    """使用训练时一致的全局知识点顺序映射知识点索引。"""
    from knowledge.models import KnowledgePoint

    ordered_ids = list(KnowledgePoint.objects.order_by("id").values_list("id", flat=True))
    return {kp_id: idx for idx, kp_id in enumerate(ordered_ids)}, ordered_ids


def _stable_slot_index(parts: list[str], slot_count: int) -> int:
    """为课程题目构建稳定的公开槽位索引。"""
    payload = "|".join(parts).encode("utf-8")
    digest = hashlib.md5(payload).hexdigest()
    return int(digest[:12], 16) % max(slot_count, 1)


class DKTPredictor:
    """DKT 模型推理器。"""

    def __init__(self):
        self._model = None
        self._model_path = None
        self._metadata_path = None
        self._metadata: dict[str, Any] = {}
        self._num_questions = 0
        self._hidden_dim = 200
        self._layer_dim = 1
        self._device = "cpu"
        self._torch_device = None
        self._runtime_mode = "legacy"
        self._course_bundle_cache: dict[int, CourseSlotBundle] = {}

    @property
    def is_loaded(self) -> bool:
        """模型是否已加载。"""
        return self._model is not None

    def load_model(
        self,
        model_path: str,
        num_questions: int | None = None,
        hidden_dim: int = 200,
        metadata_path: str | None = None,
    ) -> bool:
        """加载 DKT 模型权重。"""
        try:
            import torch
        except ImportError:
            logger.error("PyTorch 未安装，无法加载 DKT 模型")
            return False

        path = _resolve_backend_path(model_path)
        if path is None or not path.exists():
            logger.error("DKT 模型文件不存在: %s", model_path)
            return False

        metadata_file = _resolve_metadata_path(path, metadata_path)
        metadata_payload: dict[str, Any] = {}
        if metadata_file.exists():
            try:
                metadata_payload = json.loads(metadata_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                metadata_payload = {}

        try:
            from models.DKT.KnowledgeTracing.model.RNNModel import DKT

            runtime_device = resolve_torch_device()
            runtime_schema = str(metadata_payload.get("runtime_schema") or "").strip()
            slot_count = int(
                metadata_payload.get("slot_count")
                or metadata_payload.get("knowledge_point_count")
                or num_questions
                or 0
            )
            if slot_count <= 0:
                raise ValueError("DKT 缺少有效输入维度")

            self._num_questions = slot_count
            self._hidden_dim = int(metadata_payload.get("hidden_dim") or hidden_dim)
            input_dim = slot_count * 2
            output_dim = slot_count
            model = DKT(input_dim, self._hidden_dim, self._layer_dim, output_dim)

            state_dict = torch.load(str(path), map_location="cpu", weights_only=True)
            load_result = model.load_state_dict(state_dict, strict=False)
            if load_result.missing_keys or load_result.unexpected_keys:
                logger.warning(
                    "DKT 模型权重部分加载: 缺失键=%d个, 多余键=%d个 (当前Q=%d)",
                    len(load_result.missing_keys),
                    len(load_result.unexpected_keys),
                    slot_count,
                )
            model = model.to(runtime_device.device)
            model.eval()

            self._model = model
            self._model_path = str(path)
            self._metadata_path = str(metadata_file)
            self._metadata = metadata_payload
            self._device = runtime_device.label
            self._torch_device = runtime_device.device
            self._runtime_mode = "public_slot_adapter" if runtime_schema == "public_slot_adapter_v1" else "legacy"
            self._course_bundle_cache.clear()
            logger.info(
                "DKT 模型加载成功: runtime=%s, Q=%d, hidden=%d, device=%s, path=%s",
                self._runtime_mode,
                slot_count,
                self._hidden_dim,
                self._device,
                path,
            )
            return True
        except Exception as e:
            logger.error("DKT 模型加载失败: %s", e)
            self._model = None
            self._torch_device = None
            return False

    def _build_public_slot_bundle(self, course_id: int) -> CourseSlotBundle:
        """为课程构建稳定的公共槽位映射。"""
        if course_id in self._course_bundle_cache:
            return self._course_bundle_cache[course_id]

        from assessments.models import Question
        from knowledge.models import KnowledgePoint

        slot_count = max(int(self._num_questions), 1)
        question_to_slot: dict[int, int] = {}
        point_to_slots: dict[int, list[int]] = {}

        questions = list(
            Question.objects.filter(course_id=course_id, is_visible=True)
            .prefetch_related("knowledge_points")
            .order_by("id")
        )
        for question in questions:
            point_ids = [str(point_id) for point_id in question.knowledge_points.values_list("id", flat=True)]
            slot_index = _stable_slot_index(
                [
                    str(question.question_type or "unknown"),
                    str(question.difficulty or "medium"),
                    str(question.chapter or ""),
                    ",".join(sorted(point_ids)[:4]),
                    str(len(question.content or "")),
                ],
                slot_count,
            )
            question_to_slot[int(question.id)] = slot_index
            for point_id in point_ids:
                point_to_slots.setdefault(int(point_id), []).append(slot_index)

        for point_id in KnowledgePoint.objects.filter(course_id=course_id).values_list("id", flat=True):
            current_point_id = int(point_id)
            if current_point_id not in point_to_slots:
                point_to_slots[current_point_id] = [
                    _stable_slot_index(["kp", str(course_id), str(current_point_id)], slot_count)
                ]

        representative_slot = {
            point_id: slots[0]
            for point_id, slots in point_to_slots.items()
            if slots
        }
        bundle = CourseSlotBundle(
            question_to_slot=question_to_slot,
            point_to_slots=point_to_slots,
            representative_slot=representative_slot,
        )
        self._course_bundle_cache[course_id] = bundle
        return bundle

    def _predict_legacy(
        self,
        answer_history: List[Dict[str, Any]],
        knowledge_point_ids: List[int] | None = None,
    ) -> Dict[str, Any]:
        """执行旧版知识点维度推理。"""
        import torch

        device = self._torch_device or torch.device("cpu")
        kp_to_idx, _ = _load_global_kp_mapping()
        if not kp_to_idx:
            return {
                "predictions": {},
                "confidence": 0,
                "model_type": "dkt_real",
                "analysis": "无有效知识点数据",
            }

        target_kp_ids = set()
        for record in answer_history:
            current_kp_id = _coerce_optional_int(record.get("knowledge_point_id"))
            if current_kp_id is not None:
                target_kp_ids.add(current_kp_id)
        if knowledge_point_ids:
            target_kp_ids.update(int(k) for k in knowledge_point_ids)
        if not target_kp_ids:
            return {
                "predictions": {},
                "confidence": 0,
                "model_type": "dkt_real",
                "analysis": "无有效知识点数据",
            }

        q_size = self._num_questions
        seq_length = len(answer_history)
        input_seq = np.zeros((1, seq_length, 2 * q_size), dtype=np.float32)
        for time_index, record in enumerate(answer_history):
            current_kp_id = _coerce_optional_int(record.get("knowledge_point_id"))
            if current_kp_id is None:
                continue
            idx = kp_to_idx.get(current_kp_id)
            if idx is None or idx >= q_size:
                continue
            is_correct = _coerce_optional_int(record.get("correct")) == 1
            input_seq[0, time_index, idx if is_correct else q_size + idx] = 1.0

        with torch.no_grad():
            output = self._model(torch.from_numpy(input_seq).to(device))
        last_output = output[0, -1, :].detach().cpu().numpy()
        predictions = {}
        for kp_id in sorted(target_kp_ids):
            idx = kp_to_idx.get(kp_id, -1)
            if 0 <= idx < q_size:
                predictions[kp_id] = round(float(last_output[idx]), 4)
        if knowledge_point_ids:
            for kp_id in knowledge_point_ids:
                current_point_id = int(kp_id)
                if current_point_id not in predictions:
                    predictions[current_point_id] = 0.5
        return {
            "predictions": predictions,
            "confidence": 0.85,
            "model_type": "dkt_real",
            "analysis": f"DKT模型推理: 基于{seq_length}步答题序列预测{len(predictions)}个知识点掌握度",
        }

    def _predict_public_slot_adapter(
        self,
        answer_history: List[Dict[str, Any]],
        knowledge_point_ids: List[int] | None,
        course_id: int,
    ) -> Dict[str, Any]:
        """执行公开数据槽位适配模式推理。"""
        import torch

        device = self._torch_device or torch.device("cpu")
        bundle = self._build_public_slot_bundle(course_id)
        target_kp_ids = set(int(kp_id) for kp_id in (knowledge_point_ids or []))
        for record in answer_history:
            current_kp_id = _coerce_optional_int(record.get("knowledge_point_id"))
            if current_kp_id is not None:
                target_kp_ids.add(current_kp_id)
            current_question_id = _coerce_optional_int(record.get("question_id"))
            if current_question_id is not None:
                question_slot = bundle.question_to_slot.get(current_question_id)
                if question_slot is not None:
                    for point_id, slots in bundle.point_to_slots.items():
                        if question_slot in slots:
                            target_kp_ids.add(int(point_id))
        if not target_kp_ids:
            target_kp_ids.update(bundle.point_to_slots.keys())

        q_size = self._num_questions
        seq_length = len(answer_history)
        input_seq = np.zeros((1, seq_length, 2 * q_size), dtype=np.float32)
        recognized_count = 0
        used_slots: set[int] = set()
        for time_index, record in enumerate(answer_history):
            slot_index = None
            current_question_id = _coerce_optional_int(record.get("question_id"))
            if current_question_id is not None:
                slot_index = bundle.question_to_slot.get(current_question_id)
            if slot_index is None:
                current_point_id = _coerce_optional_int(record.get("knowledge_point_id"))
                if current_point_id is not None:
                    slot_index = bundle.representative_slot.get(current_point_id)
            if slot_index is None:
                continue
            recognized_count += 1
            used_slots.add(int(slot_index))
            correct = 1 if _coerce_optional_int(record.get("correct")) == 1 else 0
            input_seq[0, time_index, slot_index if correct else q_size + slot_index] = 1.0

        with torch.no_grad():
            output = self._model(torch.from_numpy(input_seq).to(device))
        last_output = output[0, -1, :].detach().cpu().numpy()

        predictions: dict[int, float] = {}
        for point_id in sorted(target_kp_ids):
            slots = bundle.point_to_slots.get(int(point_id), [])
            if not slots:
                continue
            probabilities = [float(last_output[slot]) for slot in slots]
            predictions[int(point_id)] = round(sum(probabilities) / max(len(probabilities), 1), 4)

        history_coverage = recognized_count / max(len(answer_history), 1)
        slot_coverage = len(used_slots) / max(len(bundle.point_to_slots), 1)
        confidence = min(0.88, 0.48 + history_coverage * 0.18 + slot_coverage * 0.14)
        return {
            "predictions": predictions,
            "confidence": round(confidence, 3),
            "model_type": "dkt_public_adapted",
            "analysis": f"DKT 公开数据适配推理: 基于{seq_length}步答题序列映射到{len(used_slots)}个公共槽位，输出{len(predictions)}个知识点掌握度",
        }

    def predict(
        self,
        answer_history: List[Dict[str, Any]],
        knowledge_point_ids: List[int] = None,
        course_id: int | None = None,
    ) -> Dict[str, Any]:
        """执行 DKT 推理。"""
        if not self.is_loaded:
            raise RuntimeError("DKT 模型未加载，请先调用 load_model()")
        if self._runtime_mode == "public_slot_adapter":
            if course_id is None:
                raise ValueError("公开数据适配模式需要传入 course_id")
            return self._predict_public_slot_adapter(answer_history, knowledge_point_ids, int(course_id))
        return self._predict_legacy(answer_history, knowledge_point_ids)

    def get_info(self) -> Dict[str, Any]:
        """获取模型信息。"""
        return {
            "loaded": self.is_loaded,
            "runtime_mode": self._runtime_mode,
            "model_path": self._model_path,
            "metadata_path": self._metadata_path,
            "num_questions": self._num_questions,
            "hidden_dim": self._hidden_dim,
            "layer_dim": self._layer_dim,
            "device": self._device,
            "runtime_schema": self._metadata.get("runtime_schema"),
            "training_dataset": self._metadata.get("public_dataset"),
        }


dkt_predictor = DKTPredictor()


def auto_load_model():
    """自动加载 DKT 模型（从环境变量或默认路径）。"""
    model_path = os.getenv("KT_DKT_MODEL_PATH", "")
    if not model_path:
        default_path = BACKEND_ROOT / "models" / "DKT" / "dkt_model.pt"
        if default_path.exists():
            model_path = str(default_path)
        else:
            logger.debug("未配置 DKT 模型路径且默认路径不存在，跳过自动加载")
            return False

    metadata_path = os.getenv("KT_DKT_META_PATH", "") or None
    num_questions_str = os.getenv("KT_DKT_NUM_QUESTIONS", "") or ""
    num_questions = int(num_questions_str) if num_questions_str.strip() else None
    hidden_dim_str = os.getenv("KT_DKT_HIDDEN_DIM", "") or ""
    hidden_dim = int(hidden_dim_str) if hidden_dim_str.strip() else 200
    return dkt_predictor.load_model(
        model_path,
        num_questions=num_questions,
        hidden_dim=hidden_dim,
        metadata_path=metadata_path,
    )
