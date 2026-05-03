#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 推理模块。"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from .mefkt_legacy_runtime import LoadedMEFKTState, load_mefkt_state, predict_legacy_mastery
from .mefkt_question_online import QuestionOnlinePredictionInput, predict_question_online
from .mefkt_runtime import (
    CourseQuestionRuntimeBundle,
    _append_history_outcome,
    _build_sorted_history_records,
    build_course_runtime_bundle,
)

logger = logging.getLogger(__name__)
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent

if TYPE_CHECKING:
    from models.MEFKT.model import MEFKTSequenceModel
    from torch import Tensor


# 维护意图：运行时加载并执行 MEFKT 序列预测
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class MEFKTPredictor:
    """运行时加载并执行 MEFKT 序列预测。"""

    def __init__(self) -> None:
        self._model: MEFKTSequenceModel | None = None
        self._metadata: dict[str, object] = {}
        self._model_path: str | None = None
        self._metadata_path: str | None = None
        self._item_id_to_index: dict[int, int] = {}
        self._index_to_item_id: dict[int, int] = {}
        self._runtime_mode = "legacy"
        self._device = "cpu"
        self._torch_device = None
        self._sequence_state_dict: dict[str, Tensor] = {}
        self._graph_state_dict: dict[str, Tensor] = {}
        self._attribute_state_dict: dict[str, Tensor] = {}
        self._fusion_state_dict: dict[str, Tensor] = {}
        self._course_bundle_cache: dict[int, CourseQuestionRuntimeBundle] = {}

    # 维护意图：当前模型是否已加载
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @property
    def is_loaded(self) -> bool:
        """当前模型是否已加载。"""
        return self._model is not None or bool(self._sequence_state_dict)

    # 维护意图：加载保存好的 MEFKT 模型
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def load_model(self, model_path: str, metadata_path: str | None = None) -> bool:
        """加载保存好的 MEFKT 模型。"""
        loaded_state = load_mefkt_state(
            model_path=model_path,
            metadata_path=metadata_path,
            backend_root=BACKEND_ROOT,
        )
        if loaded_state is None:
            return False
        self._apply_loaded_state(loaded_state)
        return True

    # 维护意图：将 checkpoint 状态写入 predictor
    # 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
    # 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
    def _apply_loaded_state(self, loaded_state: LoadedMEFKTState) -> None:
        """将 checkpoint 状态写入 predictor。"""
        self._metadata = loaded_state.metadata
        self._model_path = loaded_state.model_path
        self._metadata_path = loaded_state.metadata_path
        self._device = loaded_state.device_label
        self._torch_device = loaded_state.torch_device
        self._course_bundle_cache.clear()
        self._runtime_mode = loaded_state.runtime_mode
        self._model = loaded_state.model
        self._item_id_to_index = loaded_state.item_id_to_index
        self._index_to_item_id = loaded_state.index_to_item_id
        self._sequence_state_dict = loaded_state.sequence_state_dict
        self._graph_state_dict = loaded_state.graph_state_dict
        self._attribute_state_dict = loaded_state.attribute_state_dict
        self._fusion_state_dict = loaded_state.fusion_state_dict

    # 维护意图：基于课程题目、知识图谱与资源关系构建题目级在线特征
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    def _build_course_runtime_bundle(self, course_id: int) -> CourseQuestionRuntimeBundle:
        """基于课程题目、知识图谱与资源关系构建题目级在线特征。"""
        if course_id in self._course_bundle_cache:
            return self._course_bundle_cache[course_id]
        bundle = build_course_runtime_bundle(course_id)
        self._course_bundle_cache[course_id] = bundle
        return bundle

    # 维护意图：将题目级或知识点级历史记录映射到课程题图节点
    # 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
    # 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
    def _resolve_runtime_history_index(
        self,
        bundle: CourseQuestionRuntimeBundle,
        record: dict[str, object],
    ) -> int | None:
        """将题目级或知识点级历史记录映射到课程题图节点。"""
        question_id_raw = record.get("question_id")
        if question_id_raw is not None:
            question_id = int(str(question_id_raw))
            if question_id in bundle.question_id_to_index:
                return bundle.question_id_to_index[question_id]
        point_id_raw = record.get("knowledge_point_id")
        if point_id_raw is not None:
            point_id = int(str(point_id_raw))
            return bundle.representative_question_index.get(point_id)
        return None

    # 维护意图：将题目级在线部署历史转成模型输入格式
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    def _build_history_tensors_runtime(
        self,
        answer_history: list[dict[str, object]],
        bundle: CourseQuestionRuntimeBundle,
    ) -> tuple[list[int], list[int], list[float], int]:
        """将题目级在线部署历史转成模型输入格式。"""
        sortable_records = _build_sorted_history_records(answer_history)

        history_indices: list[int] = []
        history_correct: list[int] = []
        history_gap_hours: list[float] = []
        recognized_count = 0
        previous_time: datetime | None = None
        for _, current_time, record in sortable_records:
            item_index = self._resolve_runtime_history_index(bundle, record)
            if item_index is None:
                continue
            recognized_count += 1
            history_indices.append(int(item_index))
            previous_time = _append_history_outcome(
                history_correct=history_correct,
                history_gap_hours=history_gap_hours,
                record=record,
                current_time=current_time,
                previous_time=previous_time,
            )
        return history_indices, history_correct, history_gap_hours, recognized_count

    # 维护意图：执行旧版知识点级 checkpoint 推理
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _predict_legacy(
        self,
        answer_history: list[dict[str, object]],
        knowledge_point_ids: list[int] | None = None,
    ) -> dict[str, object]:
        """执行旧版知识点级 checkpoint 推理。"""
        assert self._model is not None
        return predict_legacy_mastery(
            model=self._model,
            item_id_to_index=self._item_id_to_index,
            answer_history=answer_history,
            knowledge_point_ids=knowledge_point_ids,
            torch_device=self._torch_device,
        )

    # 维护意图：执行题目级在线部署预测，并聚合回知识点掌握度
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _predict_question_online(
        self,
        *,
        answer_history: list[dict[str, object]],
        knowledge_point_ids: list[int] | None,
        course_id: int,
    ) -> dict[str, object]:
        """执行题目级在线部署预测，并聚合回知识点掌握度。"""
        import torch

        device = self._torch_device or torch.device("cpu")
        bundle = self._build_course_runtime_bundle(course_id)
        history_indices, history_correct, history_gap_hours, recognized_count = self._build_history_tensors_runtime(answer_history, bundle)
        return predict_question_online(
            QuestionOnlinePredictionInput(
                answer_history=answer_history,
                knowledge_point_ids=knowledge_point_ids,
                metadata=self._metadata,
                sequence_state_dict=self._sequence_state_dict,
                graph_state_dict=self._graph_state_dict,
                attribute_state_dict=self._attribute_state_dict,
                fusion_state_dict=self._fusion_state_dict,
                bundle=bundle,
                history_indices=history_indices,
                history_correct=history_correct,
                history_gap_hours=history_gap_hours,
                recognized_count=recognized_count,
                device=device,
            )
        )

    # 维护意图：根据答题历史预测知识点掌握度
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def predict(
        self,
        answer_history: list[dict[str, object]],
        knowledge_point_ids: list[int] | None = None,
        course_id: int | None = None,
    ) -> dict[str, object]:
        """根据答题历史预测知识点掌握度。"""
        if not self.is_loaded:
            raise RuntimeError("MEFKT 模型未加载，请先调用 load_model()")
        if self._runtime_mode == "question_online":
            if course_id is None:
                raise ValueError("题目级在线部署模式需要传入 course_id")
            return self._predict_question_online(
                answer_history=answer_history,
                knowledge_point_ids=knowledge_point_ids,
                course_id=int(course_id),
            )
        assert self._model is not None
        return self._predict_legacy(answer_history, knowledge_point_ids)

    # 维护意图：输出当前加载状态与元数据摘要
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    def get_info(self) -> dict[str, object]:
        """输出当前加载状态与元数据摘要。"""
        return {
            "loaded": self.is_loaded,
            "runtime_mode": self._runtime_mode,
            "device": self._device,
            "model_path": self._model_path,
            "metadata_path": self._metadata_path,
            "training_mode": self._metadata.get("training_mode"),
            "training_dataset": self._metadata.get("training_dataset"),
            "runtime_schema": self._metadata.get("runtime_schema"),
            "item_count": self._metadata.get("item_count"),
            "best_metrics": self._metadata.get("best_metrics"),
            "paper_title": self._metadata.get("paper_title"),
            "paper_doi": self._metadata.get("paper_doi"),
        }


mefkt_predictor = MEFKTPredictor()


# 维护意图：从环境变量或默认路径自动加载 MEFKT 模型
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def auto_load_model() -> bool:
    """从环境变量或默认路径自动加载 MEFKT 模型。"""
    from .mefkt_loader import auto_load_mefkt_model

    return auto_load_mefkt_model(mefkt_predictor, BACKEND_ROOT, os.environ)
