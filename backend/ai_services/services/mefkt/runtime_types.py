#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 在线运行时共享类型。"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from torch import Tensor


class KnowledgePointAccessor(Protocol):
    """Django 关系管理器在运行时只依赖 values_list 能力。"""

    def values_list(self, *fields: str, flat: bool = False) -> Iterable[object]:
        """返回题目或资源关联知识点的字段值。"""


class QuestionLike(Protocol):
    """题目特征构建阶段使用的 Question 最小字段集合。"""

    id: int
    chapter: str | None
    content: str | None
    analysis: str | None
    score: float | None
    difficulty: str | None
    question_type: str | None
    knowledge_points: KnowledgePointAccessor


class ResourceLike(Protocol):
    """资源关系构建阶段使用的 Resource 最小字段集合。"""

    id: int
    knowledge_points: KnowledgePointAccessor


@dataclass
class RuntimeSourceData:
    """构建课程运行时 bundle 前收集到的源数据。"""

    questions: list[QuestionLike]
    resources: list[ResourceLike]
    point_to_resources: dict[int, set[int]]
    prereq_points: dict[int, set[int]]
    dependent_points: dict[int, set[int]]
    related_points: dict[int, set[int]]
    answer_stats: dict[int, dict[str, float]]


@dataclass
class RuntimeFeatureSources:
    """题目特征提取时需要共享的关系与答题统计源。"""

    point_to_resources: dict[int, set[int]]
    prereq_points: dict[int, set[int]]
    dependent_points: dict[int, set[int]]
    related_points: dict[int, set[int]]
    answer_stats: dict[int, dict[str, float]]


@dataclass
class QuestionFeatureScales:
    """题目特征归一化后的数值集合。"""

    chapter_norm_map: dict[str, float]
    score_norm: list[float]
    content_norm: list[float]
    analysis_norm: list[float]
    attempt_norm: list[float]
    kp_count_norm: list[float]
    resource_count_norm: list[float]
    prereq_norm: list[float]
    dependent_norm: list[float]
    related_norm: list[float]
    difficulty_values_raw: list[float]


@dataclass
class QuestionFeaturePreparation:
    """题目级运行时特征准备结果。"""

    question_meta: list[dict[str, object]]
    question_to_points: dict[int, list[int]]
    point_to_question_indices: dict[int, list[int]]
    question_ids: list[int]
    question_id_to_index: dict[int, int]
    scales: QuestionFeatureScales


@dataclass
class GraphStatisticsBundle:
    """题目图邻接矩阵与衍生统计。"""

    adjacency_matrix: Tensor
    degree: Tensor
    degree_norm: Tensor
    two_hop_density: Tensor
    knowledge_overlap_scores: list[float]
    resource_overlap_scores: list[float]
