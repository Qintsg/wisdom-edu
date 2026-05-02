#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 题目级在线推理运行时特征构建。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, cast

from ai_services.services.mefkt_runtime_support import (
    build_feature_sources,
    build_graph_statistics,
    build_runtime_feature_rows,
    load_runtime_source_data,
    prepare_question_features,
)

if TYPE_CHECKING:
    from torch import Tensor, device as TorchDevice

HistorySortRecord = tuple[int, datetime | None, dict[str, object]]


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


def build_course_runtime_bundle(course_id: int) -> CourseQuestionRuntimeBundle:
    """基于课程题目、知识图谱与资源关系构建题目级在线特征。"""
    import torch
    from models.MEFKT.model import NODE_FEATURE_SCHEMA, QUESTION_TYPE_VOCAB

    source_data = load_runtime_source_data(course_id)
    questions = source_data.questions
    if not questions:
        raise ValueError("当前课程没有可用于题目级在线部署的题目")
    feature_sources = build_feature_sources(source_data)
    prepared = prepare_question_features(
        questions=questions,
        sources=feature_sources,
        normalize_values=_normalize_values,
        difficulty_to_score=_difficulty_to_score,
    )
    graph_stats = build_graph_statistics(
        questions=questions,
        question_meta=prepared.question_meta,
        related_points=source_data.related_points,
    )
    feature_rows, relation_stats_matrix, difficulty_vector_values, response_time_proxy_values, type_indices = build_runtime_feature_rows(
        questions=questions,
        preparation=prepared,
        graph_stats=graph_stats,
        normalize_values=_normalize_values,
        clamp=_clamp,
        question_type_vocab=QUESTION_TYPE_VOCAB,
        node_feature_schema=NODE_FEATURE_SCHEMA,
    )
    return CourseQuestionRuntimeBundle(
        question_ids=prepared.question_ids,
        question_id_to_index=prepared.question_id_to_index,
        question_to_points=prepared.question_to_points,
        point_to_question_indices=prepared.point_to_question_indices,
        representative_question_index={
            point_id: indices[0] for point_id, indices in prepared.point_to_question_indices.items() if indices
        },
        node_feature_matrix=torch.tensor(feature_rows, dtype=torch.float32),
        relation_stats_matrix=relation_stats_matrix,
        adjacency_matrix=graph_stats.adjacency_matrix,
        difficulty_vector=torch.tensor(difficulty_vector_values, dtype=torch.float32),
        response_time_vector=torch.tensor(response_time_proxy_values, dtype=torch.float32),
        exercise_type_vector=torch.tensor(type_indices, dtype=torch.long),
    )
