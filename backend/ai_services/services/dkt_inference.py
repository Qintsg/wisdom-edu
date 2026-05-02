"""
DKT (Deep Knowledge Tracing) 推理模块。

当前实现同时兼容两类运行时：
1. 旧版知识点维度 checkpoint；
2. 公开数据训练得到的“公共槽位 + 项目内映射”适配模式。
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

from platform_ai.kt.torch_device import resolve_torch_device
from .dkt_inference_support import (
    BACKEND_ROOT,
    CourseSlotBundle,
    build_legacy_input_sequence,
    build_public_slot_bundle,
    build_public_slot_input_sequence,
    collect_legacy_target_kp_ids,
    collect_public_slot_target_kp_ids,
    load_global_kp_mapping,
    resolve_backend_path,
    resolve_metadata_path,
)

logger = logging.getLogger(__name__)


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

        path = resolve_backend_path(model_path)
        if path is None or not path.exists():
            logger.error("DKT 模型文件不存在: %s", model_path)
            return False

        metadata_file = resolve_metadata_path(path, metadata_path)
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

        slot_count = max(int(self._num_questions), 1)
        bundle = build_public_slot_bundle(course_id=course_id, slot_count=slot_count)
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
        kp_to_idx, _ = load_global_kp_mapping()
        if not kp_to_idx:
            return {
                "predictions": {},
                "confidence": 0,
                "model_type": "dkt_real",
                "analysis": "无有效知识点数据",
            }

        target_kp_ids = collect_legacy_target_kp_ids(answer_history, knowledge_point_ids)
        if not target_kp_ids:
            return {
                "predictions": {},
                "confidence": 0,
                "model_type": "dkt_real",
                "analysis": "无有效知识点数据",
            }

        q_size = self._num_questions
        input_seq = build_legacy_input_sequence(
            answer_history=answer_history,
            kp_to_idx=kp_to_idx,
            q_size=q_size,
        )

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
        target_kp_ids = collect_public_slot_target_kp_ids(
            answer_history=answer_history,
            bundle=bundle,
            explicit_point_ids=knowledge_point_ids,
        )
        q_size = self._num_questions
        input_seq, recognized_count, used_slots = build_public_slot_input_sequence(
            answer_history=answer_history,
            bundle=bundle,
            q_size=q_size,
        )

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
