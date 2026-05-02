#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 在线运行时模型输入行构造。"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from ai_services.services.mefkt_runtime_types import (
    GraphStatisticsBundle,
    QuestionFeaturePreparation,
    QuestionFeatureScales,
    QuestionLike,
)

if TYPE_CHECKING:
    from torch import Tensor

NormalizeValues = Callable[[list[float], float], list[float]]
ClampValue = Callable[[float], float]


def build_neighbor_difficulty_tensor(
    adjacency_matrix: Tensor,
    difficulty_values_raw: list[float],
) -> Tensor:
    """根据邻接矩阵估计每道题的邻域平均难度。"""
    import torch

    difficulty_tensor = torch.tensor(difficulty_values_raw, dtype=torch.float32)
    degree = adjacency_matrix.sum(dim=1)
    return torch.where(
        degree > 0,
        torch.matmul(adjacency_matrix, difficulty_tensor.unsqueeze(1)).squeeze(1) / degree.clamp_min(1.0),
        difficulty_tensor,
    )


def build_relation_stats_matrix(
    graph_stats: GraphStatisticsBundle,
    normalize_values: NormalizeValues,
) -> Tensor:
    """构造关系统计张量。"""
    import torch

    knowledge_overlap_norm = torch.tensor(
        normalize_values(graph_stats.knowledge_overlap_scores, 0.0),
        dtype=torch.float32,
    )
    resource_overlap_norm = torch.tensor(
        normalize_values(graph_stats.resource_overlap_scores, 0.0),
        dtype=torch.float32,
    )
    return torch.stack(
        [
            graph_stats.degree_norm,
            graph_stats.two_hop_density,
            knowledge_overlap_norm,
            resource_overlap_norm,
        ],
        dim=1,
    )


def build_single_feature_row(
    *,
    question: QuestionLike,
    question_meta: dict[str, object],
    index: int,
    scales: QuestionFeatureScales,
    graph_stats: GraphStatisticsBundle,
    neighbor_difficulty_tensor: Tensor,
    clamp: ClampValue,
    question_type_vocab: dict[str, int],
    node_feature_schema: list[str],
) -> tuple[list[float], float, int]:
    """构造单题运行时特征行。"""
    difficulty_value = scales.difficulty_values_raw[index]
    response_time_proxy = clamp(
        0.35
        + difficulty_value * 0.35
        + (1.0 - float(question_meta["correct_rate"])) * 0.2
        + scales.content_norm[index] * 0.1,
    )
    feature_map = build_feature_value_map(
        question=question,
        question_meta=question_meta,
        index=index,
        scales=scales,
        graph_stats=graph_stats,
        neighbor_difficulty_tensor=neighbor_difficulty_tensor,
        difficulty_value=difficulty_value,
        response_time_proxy=response_time_proxy,
    )
    feature_row = [float(feature_map[column]) for column in node_feature_schema]
    type_index = int(question_type_vocab.get(str(question.question_type or "").strip(), 0))
    return feature_row, response_time_proxy, type_index


def build_feature_value_map(
    *,
    question: QuestionLike,
    question_meta: dict[str, object],
    index: int,
    scales: QuestionFeatureScales,
    graph_stats: GraphStatisticsBundle,
    neighbor_difficulty_tensor: Tensor,
    difficulty_value: float,
    response_time_proxy: float,
) -> dict[str, float]:
    """按 MEFKT 节点特征 schema 生成可索引的特征字典。"""
    return {
        "difficulty_proxy": difficulty_value,
        "response_time_proxy": response_time_proxy,
        "occurrence_proxy": scales.attempt_norm[index],
        "degree_norm": float(graph_stats.degree_norm[index].item()),
        "two_hop_density": float(graph_stats.two_hop_density[index].item()),
        "neighbor_difficulty": float(neighbor_difficulty_tensor[index].item()),
        "knowledge_count_norm": scales.kp_count_norm[index],
        "resource_count_norm": scales.resource_count_norm[index],
        "prerequisite_count_norm": scales.prereq_norm[index],
        "dependent_count_norm": scales.dependent_norm[index],
        "related_count_norm": scales.related_norm[index],
        "chapter_position_norm": scales.chapter_norm_map.get(str(question.chapter or "").strip(), 0.0),
        "content_length_norm": scales.content_norm[index],
        "analysis_length_norm": scales.analysis_norm[index],
        "question_score_norm": scales.score_norm[index],
        "historical_correct_rate": float(question_meta["correct_rate"]),
    }


def build_runtime_feature_rows(
    *,
    questions: list[QuestionLike],
    preparation: QuestionFeaturePreparation,
    graph_stats: GraphStatisticsBundle,
    normalize_values: NormalizeValues,
    clamp: ClampValue,
    question_type_vocab: dict[str, int],
    node_feature_schema: list[str],
) -> tuple[list[list[float]], Tensor, list[float], list[float], list[int]]:
    """把题目元特征整理成模型输入张量所需的列表。"""
    neighbor_difficulty_tensor = build_neighbor_difficulty_tensor(
        graph_stats.adjacency_matrix,
        preparation.scales.difficulty_values_raw,
    )
    relation_stats_matrix = build_relation_stats_matrix(graph_stats, normalize_values)
    row_builder = RuntimeFeatureRowCollector(relation_stats_matrix=relation_stats_matrix)
    for index, question in enumerate(questions):
        row_builder.add_row(
            question=question,
            question_meta=preparation.question_meta[index],
            index=index,
            scales=preparation.scales,
            graph_stats=graph_stats,
            neighbor_difficulty_tensor=neighbor_difficulty_tensor,
            clamp=clamp,
            question_type_vocab=question_type_vocab,
            node_feature_schema=node_feature_schema,
        )
    return row_builder.to_tuple(preparation.scales.difficulty_values_raw)


class RuntimeFeatureRowCollector:
    """保存模型输入行、题型索引与响应时间代理值。"""

    def __init__(self, *, relation_stats_matrix: Tensor) -> None:
        self.relation_stats_matrix = relation_stats_matrix
        self.response_time_proxy_values: list[float] = []
        self.feature_rows: list[list[float]] = []
        self.type_indices: list[int] = []

    def add_row(
        self,
        *,
        question: QuestionLike,
        question_meta: dict[str, object],
        index: int,
        scales: QuestionFeatureScales,
        graph_stats: GraphStatisticsBundle,
        neighbor_difficulty_tensor: Tensor,
        clamp: ClampValue,
        question_type_vocab: dict[str, int],
        node_feature_schema: list[str],
    ) -> None:
        """追加一道题的模型输入行。"""
        feature_row, response_time_proxy, type_index = build_single_feature_row(
            question=question,
            question_meta=question_meta,
            index=index,
            scales=scales,
            graph_stats=graph_stats,
            neighbor_difficulty_tensor=neighbor_difficulty_tensor,
            clamp=clamp,
            question_type_vocab=question_type_vocab,
            node_feature_schema=node_feature_schema,
        )
        self.response_time_proxy_values.append(response_time_proxy)
        self.feature_rows.append(feature_row)
        self.type_indices.append(type_index)

    def to_tuple(
        self,
        difficulty_values_raw: list[float],
    ) -> tuple[list[list[float]], Tensor, list[float], list[float], list[int]]:
        """按运行时调用方既有顺序返回特征元组。"""
        return (
            self.feature_rows,
            self.relation_stats_matrix,
            difficulty_values_raw,
            self.response_time_proxy_values,
            self.type_indices,
        )
