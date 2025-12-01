#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
MEFKT 推理模块。
@Project : wisdom-edu
@File : mefkt_inference.py
@Author : Qintsg
@Date : 2026-04-04
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, cast

from platform_ai.kt.torch_device import resolve_torch_device

logger = logging.getLogger(__name__)
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent

if TYPE_CHECKING:
    from models.MEFKT.model import MEFKTSequenceModel
    from torch import Tensor, device as TorchDevice


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


@dataclass(frozen=True)
class CourseQuestionRuntimeBundle:
    """课程题目级在线部署所需的静态特征与映射。"""

    question_ids: list[int]
    question_id_to_index: dict[int, int]
    question_to_points: dict[int, list[int]]
    point_to_question_indices: dict[int, list[int]]
    representative_question_index: dict[int, int]
    node_feature_matrix: Tensor
    relation_stats_matrix: Tensor
    adjacency_matrix: Tensor
    difficulty_vector: Tensor
    response_time_vector: Tensor
    exercise_type_vector: Tensor


HistorySortRecord = tuple[int, datetime | None, dict[str, object]]


def _coerce_float(value: object, default: float = 0.0) -> float:
    """将元数据或动态字典中的值安全转换为浮点数。"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_int(value: object, default: int) -> int:
    """将元数据中的值安全转换为整数。"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _build_sorted_history_records(answer_history: list[dict[str, object]]) -> list[HistorySortRecord]:
    """按时间优先、原顺序兜底的方式整理历史作答记录。"""
    sortable_records: list[HistorySortRecord] = []
    for order_index, record in enumerate(answer_history):
        sortable_records.append((order_index, _parse_timestamp(str(record.get("timestamp") or "")), record))
    sortable_records.sort(key=lambda item: item[1] or datetime.min)
    if not any(record_time is not None for _, record_time, _ in sortable_records):
        sortable_records.sort(key=lambda item: item[0])
    return sortable_records


def _append_history_outcome(
    history_correct: list[int],
    history_gap_hours: list[float],
    record: dict[str, object],
    current_time: datetime | None,
    previous_time: datetime | None,
) -> datetime | None:
    """追加答题正确性与相邻时间间隔特征。"""
    history_correct.append(1 if _coerce_int(record.get("correct", 0), 0) == 1 else 0)
    if current_time is None or previous_time is None:
        history_gap_hours.append(1.0)
    else:
        gap_seconds = max((current_time - previous_time).total_seconds(), 60.0)
        history_gap_hours.append(gap_seconds / 3600.0)
    return current_time or previous_time


def _move_bundle_tensors_to_device(
    bundle: CourseQuestionRuntimeBundle,
    device: TorchDevice | str,
) -> tuple[Tensor, Tensor, Tensor, Tensor, Tensor, Tensor]:
    """将课程运行时张量批量迁移到指定设备。"""
    return (
        bundle.node_feature_matrix.to(device),
        bundle.relation_stats_matrix.to(device),
        bundle.adjacency_matrix.to(device),
        bundle.difficulty_vector.to(device),
        bundle.response_time_vector.to(device),
        bundle.exercise_type_vector.to(device),
    )


def _parse_timestamp(timestamp_text: str | None) -> datetime | None:
    """尝试解析接口层传入的时间文本。"""
    if not timestamp_text:
        return None
    normalized = str(timestamp_text).strip()
    if not normalized:
        return None
    try:
        return datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        return None


def _normalize_values(values: list[float], default_value: float = 0.5) -> list[float]:
    """将一维数值归一化到 [0,1]。"""
    if not values:
        return [default_value]
    lower = min(values)
    upper = max(values)
    if abs(upper - lower) <= 1e-8:
        return [default_value for _ in values]
    return [(value - lower) / (upper - lower) for value in values]


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """将运行时特征值裁剪到闭区间内，避免异常值放大。"""
    return max(lower, min(upper, value))


def _difficulty_to_score(difficulty: str | None) -> float:
    """将题目难度枚举转换成数值特征。"""
    return {
        "easy": 0.25,
        "medium": 0.5,
        "hard": 0.75,
    }.get(str(difficulty or "").strip(), 0.5)


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

    @property
    def is_loaded(self) -> bool:
        """当前模型是否已加载。"""
        return self._model is not None or bool(self._sequence_state_dict)

    def load_model(self, model_path: str, metadata_path: str | None = None) -> bool:
        """加载保存好的 MEFKT 模型。"""
        try:
            import torch
            from torch import Tensor as TorchTensor
        except ImportError:
            logger.error("PyTorch 未安装，无法加载 MEFKT 模型")
            return False

        from models.MEFKT.model import MEFKTSequenceModel

        model_file = _resolve_backend_path(model_path)
        if model_file is None or not model_file.exists():
            logger.error("MEFKT 模型文件不存在: %s", model_path)
            return False

        metadata_file = (
            _resolve_backend_path(metadata_path) if metadata_path else None
        ) or model_file.with_suffix(".meta.json")
        checkpoint = torch.load(str(model_file), map_location="cpu", weights_only=False)
        metadata_payload = dict(checkpoint.get("metadata") or {})
        runtime_device = resolve_torch_device()
        if metadata_file.exists():
            try:
                metadata_payload = json.loads(metadata_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                logger.warning("MEFKT 元数据解析失败，回退到 checkpoint 内嵌元数据")

        self._metadata = metadata_payload
        self._model_path = str(model_file)
        self._metadata_path = str(metadata_file)
        self._device = runtime_device.label
        self._torch_device = runtime_device.device
        self._course_bundle_cache.clear()

        runtime_schema = str(metadata_payload.get("runtime_schema") or "").strip()
        if runtime_schema == "question_online_v1" and checkpoint.get("graph_state_dict"):
            self._runtime_mode = "question_online"
            self._model = None
            self._item_id_to_index = {}
            self._index_to_item_id = {}
            self._sequence_state_dict = cast(
                dict[str, TorchTensor],
                dict(checkpoint.get("sequence_state_dict") or checkpoint.get("state_dict") or {}),
            )
            self._graph_state_dict = cast(dict[str, TorchTensor], dict(checkpoint.get("graph_state_dict") or {}))
            self._attribute_state_dict = cast(dict[str, TorchTensor], dict(checkpoint.get("attribute_state_dict") or {}))
            self._fusion_state_dict = cast(dict[str, TorchTensor], dict(checkpoint.get("fusion_state_dict") or {}))
            logger.info(
                "MEFKT 题目级在线模型加载成功: dataset=%s, device=%s, path=%s",
                metadata_payload.get("training_dataset"),
                self._device,
                model_file,
            )
            return True

        item_ids = [int(item_id) for item_id in metadata_payload.get("item_ids", [])]
        item_count = int(metadata_payload.get("item_count") or len(item_ids))
        embedding_dim = int(metadata_payload.get("embedding_dim") or 256)
        num_heads = int(metadata_payload.get("num_heads") or 4)
        head_dim = int(metadata_payload.get("head_dim") or 32)
        if item_count <= 0:
            logger.error("MEFKT 元数据缺少有效 item_count")
            return False
        if not item_ids:
            item_ids = list(range(item_count))

        model = MEFKTSequenceModel(
            item_count=item_count,
            item_embedding_dim=embedding_dim,
            num_heads=num_heads,
            head_dim=head_dim,
        ).to(runtime_device.device)
        model.load_state_dict(checkpoint["state_dict"])
        model.eval()

        self._runtime_mode = "legacy"
        self._model = model
        self._item_id_to_index = {int(item_id): index for index, item_id in enumerate(item_ids)}
        self._index_to_item_id = {index: int(item_id) for index, item_id in enumerate(item_ids)}
        self._sequence_state_dict = {}
        self._graph_state_dict = {}
        self._attribute_state_dict = {}
        self._fusion_state_dict = {}
        logger.info(
            "MEFKT 旧版模型加载成功: items=%d, device=%s, path=%s",
            item_count,
            self._device,
            model_file,
        )
        return True

    def _build_history_tensors_legacy(
        self,
        answer_history: list[dict[str, object]],
    ) -> tuple[list[int], list[int], list[float], int]:
        """将旧版知识点历史转成模型输入格式。"""
        sortable_records = _build_sorted_history_records(answer_history)

        history_indices: list[int] = []
        history_correct: list[int] = []
        history_gap_hours: list[float] = []
        recognized_count = 0
        previous_time: datetime | None = None
        for _, current_time, record in sortable_records:
            item_id_raw = record.get("knowledge_point_id")
            if item_id_raw is None:
                continue
            item_id = int(str(item_id_raw))
            if item_id not in self._item_id_to_index:
                continue
            recognized_count += 1
            history_indices.append(self._item_id_to_index[item_id])
            previous_time = _append_history_outcome(
                history_correct=history_correct,
                history_gap_hours=history_gap_hours,
                record=record,
                current_time=current_time,
                previous_time=previous_time,
            )
        return history_indices, history_correct, history_gap_hours, recognized_count

    def _build_course_runtime_bundle(self, course_id: int) -> CourseQuestionRuntimeBundle:
        """基于课程题目、知识图谱与资源关系构建题目级在线特征。"""
        if course_id in self._course_bundle_cache:
            return self._course_bundle_cache[course_id]

        import torch
        from assessments.models import AnswerHistory, Question
        from knowledge.models import KnowledgeRelation, Resource
        from models.MEFKT.model import NODE_FEATURE_SCHEMA, QUESTION_TYPE_VOCAB

        questions = list(
            Question.objects.filter(course_id=course_id, is_visible=True)
            .prefetch_related("knowledge_points")
            .order_by("id")
        )
        if not questions:
            raise ValueError("当前课程没有可用于题目级在线部署的题目")

        resources = list(
            Resource.objects.filter(course_id=course_id, is_visible=True).prefetch_related("knowledge_points")
        )
        point_to_resources: dict[int, set[int]] = {}
        for resource in resources:
            for point_id in resource.knowledge_points.values_list("id", flat=True):
                point_to_resources.setdefault(int(point_id), set()).add(int(resource.id))

        prereq_points: dict[int, set[int]] = {}
        dependent_points: dict[int, set[int]] = {}
        related_points: dict[int, set[int]] = {}
        for relation in KnowledgeRelation.objects.filter(course_id=course_id).values_list(
            "pre_point_id",
            "post_point_id",
            "relation_type",
        ):
            pre_point_id, post_point_id, relation_type = relation
            pre_point_id = int(pre_point_id)
            post_point_id = int(post_point_id)
            if relation_type == "prerequisite":
                prereq_points.setdefault(post_point_id, set()).add(pre_point_id)
                dependent_points.setdefault(pre_point_id, set()).add(post_point_id)
            else:
                related_points.setdefault(pre_point_id, set()).add(post_point_id)
                related_points.setdefault(post_point_id, set()).add(pre_point_id)

        answer_stats = {}
        for question_id_raw, is_correct in AnswerHistory.objects.filter(course_id=course_id).values_list(
            "question_id",
            "is_correct",
        ):
            question_id = int(question_id_raw)
            stats = answer_stats.setdefault(question_id, {"total": 0.0, "correct": 0.0})
            stats["total"] += 1.0
            stats["correct"] += 1.0 if bool(is_correct) else 0.0

        chapter_values = sorted({str(question.chapter or "").strip() for question in questions})
        chapter_mapping = {
            chapter: index for index, chapter in enumerate(chapter_values)
        }
        chapter_norm = _normalize_values([float(chapter_mapping[chapter]) for chapter in chapter_values], default_value=0.0)
        chapter_norm_map = {
            chapter: chapter_norm[index] for index, chapter in enumerate(chapter_values)
        }

        score_values = []
        content_lengths = []
        analysis_lengths = []
        attempt_counts = []
        correct_rates = []
        question_kp_counts = []
        question_resource_counts = []
        difficulty_values_raw = []
        question_meta: list[dict[str, object]] = []
        question_to_points: dict[int, list[int]] = {}
        point_to_question_indices: dict[int, list[int]] = {}
        question_ids = [int(question.id) for question in questions]
        question_id_to_index = {question_id: index for index, question_id in enumerate(question_ids)}

        for question in questions:
            point_ids = [int(point_id) for point_id in question.knowledge_points.values_list("id", flat=True)]
            question_to_points[int(question.id)] = point_ids
            for point_id in point_ids:
                point_to_question_indices.setdefault(point_id, []).append(question_id_to_index[int(question.id)])
            resource_ids = sorted({resource_id for point_id in point_ids for resource_id in point_to_resources.get(point_id, set())})
            prereq_count = len({pre for point_id in point_ids for pre in prereq_points.get(point_id, set())})
            dependent_count = len({post for point_id in point_ids for post in dependent_points.get(point_id, set())})
            related_count = len({rel for point_id in point_ids for rel in related_points.get(point_id, set())})
            stats = answer_stats.get(int(question.id), {"total": 0.0, "correct": 0.0})
            attempt_count = float(stats["total"])
            correct_rate = float(stats["correct"] / stats["total"]) if stats["total"] > 0 else 0.5
            score_value = float(question.score or 1.0)

            score_values.append(score_value)
            content_lengths.append(float(len(question.content or "")))
            analysis_lengths.append(float(len(question.analysis or "")))
            attempt_counts.append(attempt_count)
            correct_rates.append(correct_rate)
            question_kp_counts.append(float(len(point_ids)))
            question_resource_counts.append(float(len(resource_ids)))
            difficulty_values_raw.append(_difficulty_to_score(question.difficulty))
            question_meta.append(
                {
                    "question": question,
                    "point_ids": point_ids,
                    "resource_ids": set(resource_ids),
                    "prereq_count": float(prereq_count),
                    "dependent_count": float(dependent_count),
                    "related_count": float(related_count),
                    "attempt_count": attempt_count,
                    "correct_rate": correct_rate,
                    "score_value": score_value,
                }
            )

        score_norm = _normalize_values(score_values)
        content_norm = _normalize_values(content_lengths, default_value=0.3)
        analysis_norm = _normalize_values(analysis_lengths, default_value=0.2)
        attempt_norm = _normalize_values(attempt_counts, default_value=0.0)
        kp_count_norm = _normalize_values(question_kp_counts, default_value=0.2)
        resource_count_norm = _normalize_values(question_resource_counts, default_value=0.0)
        prereq_norm = _normalize_values([
            _coerce_float(item["prereq_count"]) for item in question_meta
        ], default_value=0.0)
        dependent_norm = _normalize_values([
            _coerce_float(item["dependent_count"]) for item in question_meta
        ], default_value=0.0)
        related_norm = _normalize_values([
            _coerce_float(item["related_count"]) for item in question_meta
        ], default_value=0.0)

        question_count = len(questions)
        adjacency_matrix = torch.zeros((question_count, question_count), dtype=torch.float32)
        knowledge_overlap_scores = [0.0 for _ in range(question_count)]
        resource_overlap_scores = [0.0 for _ in range(question_count)]
        for left_index in range(question_count):
            left_points = set(cast(list[int], question_meta[left_index]["point_ids"]))
            left_resources = cast(set[int], question_meta[left_index]["resource_ids"])
            left_question = questions[left_index]
            shared_kp_total = 0.0
            shared_resource_total = 0.0
            for right_index in range(left_index + 1, question_count):
                right_points = set(cast(list[int], question_meta[right_index]["point_ids"]))
                right_resources = cast(set[int], question_meta[right_index]["resource_ids"])
                share_points = float(len(left_points & right_points))
                share_resources = float(len(left_resources & right_resources))
                related_bridge = 0.0
                if not share_points:
                    left_neighbors = {rel for point_id in left_points for rel in related_points.get(point_id, set())}
                    left_dependents = {rel for point_id in left_points for rel in dependent_points.get(point_id, set())}
                    left_prereqs = {rel for point_id in left_points for rel in prereq_points.get(point_id, set())}
                    if right_points & (left_neighbors | left_dependents | left_prereqs):
                        related_bridge = 1.0
                same_chapter = 1.0 if str(left_question.chapter or "").strip() == str(questions[right_index].chapter or "").strip() else 0.0
                same_type = 1.0 if str(left_question.question_type or "") == str(questions[right_index].question_type or "") else 0.0
                weight = share_points * 2.0 + share_resources * 0.5 + related_bridge * 1.25 + same_chapter * 0.5 + same_type * 0.2
                if weight > 0:
                    adjacency_matrix[left_index, right_index] = weight
                    adjacency_matrix[right_index, left_index] = weight
                    shared_kp_total += share_points
                    shared_resource_total += share_resources
                    knowledge_overlap_scores[right_index] += share_points
                    resource_overlap_scores[right_index] += share_resources
            knowledge_overlap_scores[left_index] += shared_kp_total
            resource_overlap_scores[left_index] += shared_resource_total

        degree = adjacency_matrix.sum(dim=1)
        degree_norm = degree / degree.max().clamp_min(1.0)
        if question_count > 1:
            two_hop = (torch.matmul((adjacency_matrix > 0).float(), (adjacency_matrix > 0).float()) > 0).float()
            two_hop_density = two_hop.sum(dim=1) / float(question_count - 1)
        else:
            two_hop_density = torch.zeros_like(degree_norm)
        knowledge_overlap_norm = torch.tensor(
            _normalize_values(knowledge_overlap_scores, default_value=0.0),
            dtype=torch.float32,
        )
        resource_overlap_norm = torch.tensor(
            _normalize_values(resource_overlap_scores, default_value=0.0),
            dtype=torch.float32,
        )
        difficulty_tensor = torch.tensor(difficulty_values_raw, dtype=torch.float32)
        neighbor_difficulty_tensor = torch.where(
            degree > 0,
            torch.matmul(adjacency_matrix, difficulty_tensor.unsqueeze(1)).squeeze(1) / degree.clamp_min(1.0),
            difficulty_tensor,
        )

        difficulty_vector_values = [float(value) for value in difficulty_values_raw]
        response_time_proxy_values = []
        feature_rows = []
        type_indices = []
        for index, question in enumerate(questions):
            difficulty_value = difficulty_vector_values[index]
            response_time_proxy = _clamp(
                0.35
                + difficulty_value * 0.35
                + (1.0 - correct_rates[index]) * 0.2
                + content_norm[index] * 0.1,
            )
            response_time_proxy_values.append(response_time_proxy)
            feature_map = {
                "difficulty_proxy": difficulty_value,
                "response_time_proxy": response_time_proxy,
                "occurrence_proxy": attempt_norm[index],
                "degree_norm": float(degree_norm[index].item()),
                "two_hop_density": float(two_hop_density[index].item()),
                "neighbor_difficulty": float(neighbor_difficulty_tensor[index].item()),
                "knowledge_count_norm": kp_count_norm[index],
                "resource_count_norm": resource_count_norm[index],
                "prerequisite_count_norm": prereq_norm[index],
                "dependent_count_norm": dependent_norm[index],
                "related_count_norm": related_norm[index],
                "chapter_position_norm": chapter_norm_map.get(str(question.chapter or "").strip(), 0.0),
                "content_length_norm": content_norm[index],
                "analysis_length_norm": analysis_norm[index],
                "question_score_norm": score_norm[index],
                "historical_correct_rate": correct_rates[index],
            }
            feature_rows.append([float(feature_map[column]) for column in NODE_FEATURE_SCHEMA])
            type_indices.append(int(QUESTION_TYPE_VOCAB.get(str(question.question_type or "").strip(), 0)))

        relation_stats_matrix = torch.stack(
            [degree_norm, two_hop_density, knowledge_overlap_norm, resource_overlap_norm],
            dim=1,
        )
        bundle = CourseQuestionRuntimeBundle(
            question_ids=question_ids,
            question_id_to_index=question_id_to_index,
            question_to_points=question_to_points,
            point_to_question_indices=point_to_question_indices,
            representative_question_index={
                point_id: indices[0] for point_id, indices in point_to_question_indices.items() if indices
            },
            node_feature_matrix=torch.tensor(feature_rows, dtype=torch.float32),
            relation_stats_matrix=relation_stats_matrix,
            adjacency_matrix=adjacency_matrix,
            difficulty_vector=torch.tensor(difficulty_vector_values, dtype=torch.float32),
            response_time_vector=torch.tensor(response_time_proxy_values, dtype=torch.float32),
            exercise_type_vector=torch.tensor(type_indices, dtype=torch.long),
        )
        self._course_bundle_cache[course_id] = bundle
        return bundle

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

    def _predict_legacy(
        self,
        answer_history: list[dict[str, object]],
        knowledge_point_ids: list[int] | None = None,
    ) -> dict[str, object]:
        """执行旧版知识点级 checkpoint 推理。"""
        import torch

        assert self._model is not None
        device = self._torch_device or torch.device("cpu")
        history_indices, history_correct, history_gap_hours, recognized_count = self._build_history_tensors_legacy(answer_history)
        target_ids = set(int(item_id) for item_id in (knowledge_point_ids or []))
        if not target_ids:
            for record in answer_history:
                current_item_id = record.get("knowledge_point_id")
                if current_item_id is not None:
                    target_ids.add(int(str(current_item_id)))
        known_target_ids = [item_id for item_id in sorted(target_ids) if item_id in self._item_id_to_index]
        if not known_target_ids:
            return {
                "predictions": {},
                "confidence": 0.0,
                "model_type": "mefkt",
                "analysis": "MEFKT 未识别到可用知识点，无法输出掌握度预测",
            }

        candidate_tensor = torch.tensor(
            [self._item_id_to_index[item_id] for item_id in known_target_ids],
            dtype=torch.long,
            device=device,
        )
        if history_indices:
            history_index_tensor = torch.tensor(history_indices, dtype=torch.long, device=device)
            history_correct_tensor = torch.tensor(history_correct, dtype=torch.long, device=device)
            history_gap_tensor = torch.tensor(history_gap_hours, dtype=torch.float32, device=device)
            probability_tensor = self._model.predict_candidate(
                history_item_indices=history_index_tensor,
                history_correct_flags=history_correct_tensor,
                history_time_gaps=history_gap_tensor,
                candidate_item_indices=candidate_tensor,
            )
        else:
            probability_tensor = torch.full((len(known_target_ids),), 0.25, dtype=torch.float32, device=device)

        predictions = {
            item_id: round(float(probability), 4)
            for item_id, probability in zip(known_target_ids, probability_tensor.detach().cpu().tolist(), strict=True)
        }
        history_coverage = recognized_count / max(len(answer_history), 1)
        confidence = min(0.9, 0.42 + len(history_indices) / 30.0 * 0.28 + history_coverage * 0.2)
        return {
            "predictions": predictions,
            "confidence": round(confidence, 3),
            "model_type": "mefkt_real",
            "analysis": f"MEFKT 推理完成：识别 {recognized_count}/{len(answer_history)} 条有效交互，输出 {len(predictions)} 个知识点掌握度",
        }

    def _predict_question_online(
        self,
        *,
        answer_history: list[dict[str, object]],
        knowledge_point_ids: list[int] | None,
        course_id: int,
    ) -> dict[str, object]:
        """执行题目级在线部署预测，并聚合回知识点掌握度。"""
        import torch
        from models.MEFKT.model import (
            GraphContrastiveEncoder,
            LinearAlignmentFusion,
            MEFKTSequenceModel,
            MultiAttributeEncoder,
            load_compatible_state,
        )

        device = self._torch_device or torch.device("cpu")
        bundle = self._build_course_runtime_bundle(course_id)
        feature_dim = _coerce_int(self._metadata.get("feature_dim"), int(bundle.node_feature_matrix.size(1)))
        relation_dim = _coerce_int(self._metadata.get("relation_dim"), int(bundle.relation_stats_matrix.size(1)))
        align_dim = _coerce_int(self._metadata.get("align_dim"), 128)
        hidden_dim = _coerce_int(self._metadata.get("hidden_dim"), 128)
        num_heads = _coerce_int(self._metadata.get("num_heads"), 4)
        head_dim = _coerce_int(self._metadata.get("head_dim"), 32)
        embedding_dim = _coerce_int(self._metadata.get("embedding_dim"), align_dim * 2)
        type_mapping = cast(dict[str, int], self._metadata.get("type_mapping") or {"unknown": 0})

        graph_encoder = GraphContrastiveEncoder(feature_dim, hidden_dim, align_dim).to(device)
        attribute_encoder = MultiAttributeEncoder(feature_dim, max(type_mapping.values(), default=0) + 1, align_dim, relation_dim=relation_dim).to(device)
        fusion_layer = LinearAlignmentFusion(align_dim, align_dim, align_dim).to(device)
        load_compatible_state(graph_encoder, self._graph_state_dict)
        load_compatible_state(attribute_encoder, self._attribute_state_dict)
        load_compatible_state(fusion_layer, self._fusion_state_dict)
        graph_encoder.eval()
        attribute_encoder.eval()
        fusion_layer.eval()

        (
            node_feature_matrix,
            relation_stats_matrix,
            adjacency_matrix,
            difficulty_vector,
            response_time_vector,
            exercise_type_vector,
        ) = _move_bundle_tensors_to_device(bundle, device)

        with torch.no_grad():
            struct_embedding = graph_encoder.encode(node_feature_matrix, adjacency_matrix)
            attribute_result = attribute_encoder(
                node_feature_matrix=node_feature_matrix,
                difficulty_vector=difficulty_vector,
                response_time_vector=response_time_vector,
                exercise_type_vector=exercise_type_vector,
                exercise_adjacency=adjacency_matrix,
                relation_stats_matrix=relation_stats_matrix,
            )
            fused_embedding = fusion_layer(struct_embedding, attribute_result.embedding)

        sequence_embedding_dim = int(fused_embedding.size(1))
        if embedding_dim != sequence_embedding_dim:
            logger.warning(
                "MEFKT 运行时融合维度与元数据不一致，将使用运行时维度: metadata=%d, runtime=%d",
                embedding_dim,
                sequence_embedding_dim,
            )

        sequence_model = MEFKTSequenceModel(
            item_count=len(bundle.question_ids),
            item_embedding_dim=sequence_embedding_dim,
            num_heads=num_heads,
            head_dim=head_dim,
            pretrained_item_embedding=fused_embedding.detach().cpu(),
        ).to(device)
        load_compatible_state(sequence_model, self._sequence_state_dict)
        sequence_model.eval()

        history_indices, history_correct, history_gap_hours, recognized_count = self._build_history_tensors_runtime(answer_history, bundle)
        target_point_ids = set(int(point_id) for point_id in (knowledge_point_ids or []))
        if not target_point_ids:
            for record in answer_history:
                point_id_raw = record.get("knowledge_point_id")
                if point_id_raw is not None:
                    target_point_ids.add(int(str(point_id_raw)))
                question_id_raw = record.get("question_id")
                if question_id_raw is not None:
                    target_point_ids.update(bundle.question_to_points.get(int(str(question_id_raw)), []))
        if not target_point_ids:
            target_point_ids.update(bundle.point_to_question_indices.keys())
        candidate_question_indices = sorted(
            {
                question_index
                for point_id in target_point_ids
                for question_index in bundle.point_to_question_indices.get(int(point_id), [])
            }
        )
        if not candidate_question_indices:
            return {
                "predictions": {},
                "confidence": 0.0,
                "model_type": "mefkt_question_online",
                "analysis": "当前课程题图中未找到可关联到目标知识点的题目节点",
            }

        candidate_tensor = torch.tensor(candidate_question_indices, dtype=torch.long, device=device)
        if history_indices:
            probability_tensor = sequence_model.predict_candidate(
                history_item_indices=torch.tensor(history_indices, dtype=torch.long, device=device),
                history_correct_flags=torch.tensor(history_correct, dtype=torch.long, device=device),
                history_time_gaps=torch.tensor(history_gap_hours, dtype=torch.float32, device=device),
                candidate_item_indices=candidate_tensor,
            )
        else:
            probability_tensor = torch.full((len(candidate_question_indices),), 0.28, dtype=torch.float32, device=device)

        per_question_predictions = {
            bundle.question_ids[question_index]: float(probability)
            for question_index, probability in zip(
                candidate_question_indices,
                probability_tensor.detach().cpu().tolist(),
                strict=True,
            )
        }
        predictions: dict[int, float] = {}
        for point_id in sorted(target_point_ids):
            point_question_indices = bundle.point_to_question_indices.get(int(point_id), [])
            if not point_question_indices:
                continue
            probabilities = [
                per_question_predictions.get(bundle.question_ids[question_index])
                for question_index in point_question_indices
                if bundle.question_ids[question_index] in per_question_predictions
            ]
            if not probabilities:
                representative_index = bundle.representative_question_index.get(int(point_id))
                if representative_index is not None:
                    representative_question_id = bundle.question_ids[representative_index]
                    representative_probability = per_question_predictions.get(representative_question_id, 0.35)
                    probabilities = [representative_probability]
            predictions[int(point_id)] = round(sum(probabilities) / max(len(probabilities), 1), 4)

        history_coverage = recognized_count / max(len(answer_history), 1)
        candidate_coverage = len(candidate_question_indices) / max(len(bundle.question_ids), 1)
        confidence = min(0.93, 0.46 + len(history_indices) / 24.0 * 0.24 + history_coverage * 0.14 + candidate_coverage * 0.08)
        return {
            "predictions": predictions,
            "confidence": round(confidence, 3),
            "model_type": "mefkt_question_online",
            "question_predictions": {
                question_id: round(probability, 4) for question_id, probability in per_question_predictions.items()
            },
            "analysis": f"MEFKT 题目级在线部署完成：课程题图 {len(bundle.question_ids)} 题，识别 {recognized_count}/{len(answer_history)} 条有效交互，聚合输出 {len(predictions)} 个知识点掌握度",
        }

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


def auto_load_model() -> bool:
    """从环境变量或默认路径自动加载 MEFKT 模型。"""
    model_path = os.getenv("KT_MEFKT_MODEL_PATH", "").strip()
    metadata_path = os.getenv("KT_MEFKT_META_PATH", "").strip()
    if not model_path:
        default_model_path = BACKEND_ROOT / "models" / "MEFKT" / "mefkt_model.pt"
        if not default_model_path.exists():
            logger.debug("未配置 KT_MEFKT_MODEL_PATH 且默认模型不存在，跳过自动加载")
            return False
        model_path = str(default_model_path)
    effective_metadata_path = metadata_path if metadata_path else None
    return mefkt_predictor.load_model(model_path=model_path, metadata_path=effective_metadata_path)
