#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 题目级在线运行时辅助工具。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RuntimeSourceData:
    """构建课程运行时 bundle 前收集到的源数据。"""

    questions: list[Any]
    resources: list[Any]
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

    adjacency_matrix: Any
    degree: Any
    degree_norm: Any
    two_hop_density: Any
    knowledge_overlap_scores: list[float]
    resource_overlap_scores: list[float]


def load_runtime_source_data(course_id: int) -> RuntimeSourceData:
    """加载课程题目、资源、关系和答题统计。"""
    from assessments.models import AnswerHistory, Question
    from knowledge.models import KnowledgeRelation, Resource

    questions = list(
        Question.objects.filter(course_id=course_id, is_visible=True)
        .prefetch_related("knowledge_points")
        .order_by("id")
    )
    resources = list(
        Resource.objects.filter(course_id=course_id, is_visible=True)
        .prefetch_related("knowledge_points")
    )

    point_to_resources: dict[int, set[int]] = {}
    for resource in resources:
        for point_id in resource.knowledge_points.values_list("id", flat=True):
            point_to_resources.setdefault(int(point_id), set()).add(int(resource.id))

    prereq_points: dict[int, set[int]] = {}
    dependent_points: dict[int, set[int]] = {}
    related_points: dict[int, set[int]] = {}
    for pre_point_id, post_point_id, relation_type in KnowledgeRelation.objects.filter(course_id=course_id).values_list(
        "pre_point_id",
        "post_point_id",
        "relation_type",
    ):
        pre_point_id = int(pre_point_id)
        post_point_id = int(post_point_id)
        if relation_type == "prerequisite":
            prereq_points.setdefault(post_point_id, set()).add(pre_point_id)
            dependent_points.setdefault(pre_point_id, set()).add(post_point_id)
        else:
            related_points.setdefault(pre_point_id, set()).add(post_point_id)
            related_points.setdefault(post_point_id, set()).add(pre_point_id)

    answer_stats: dict[int, dict[str, float]] = {}
    for question_id_raw, is_correct in AnswerHistory.objects.filter(course_id=course_id).values_list(
        "question_id",
        "is_correct",
    ):
        question_id = int(question_id_raw)
        stats = answer_stats.setdefault(question_id, {"total": 0.0, "correct": 0.0})
        stats["total"] += 1.0
        stats["correct"] += 1.0 if bool(is_correct) else 0.0

    return RuntimeSourceData(
        questions=questions,
        resources=resources,
        point_to_resources=point_to_resources,
        prereq_points=prereq_points,
        dependent_points=dependent_points,
        related_points=related_points,
        answer_stats=answer_stats,
    )


def _build_feature_sources(source_data: RuntimeSourceData) -> RuntimeFeatureSources:
    """将课程源数据收敛为题目特征提取的输入。"""
    return RuntimeFeatureSources(
        point_to_resources=source_data.point_to_resources,
        prereq_points=source_data.prereq_points,
        dependent_points=source_data.dependent_points,
        related_points=source_data.related_points,
        answer_stats=source_data.answer_stats,
    )


def _build_chapter_norm_map(questions: list[Any], normalize_values) -> dict[str, float]:
    """为章节顺序生成归一化映射。"""
    chapter_values = sorted({str(question.chapter or "").strip() for question in questions})
    chapter_mapping = {chapter: index for index, chapter in enumerate(chapter_values)}
    chapter_norm = normalize_values(
        [float(chapter_mapping[chapter]) for chapter in chapter_values],
        default_value=0.0,
    )
    return {chapter: chapter_norm[index] for index, chapter in enumerate(chapter_values)}


def _collect_question_feature_entry(
    *,
    question,
    sources: RuntimeFeatureSources,
    question_id_to_index: dict[int, int],
    difficulty_to_score,
) -> tuple[dict[str, object], list[float], dict[int, list[int]]]:
    """收集单题题图和答题统计特征。"""
    point_ids = [int(point_id) for point_id in question.knowledge_points.values_list("id", flat=True)]
    point_index_map = {
        point_id: [question_id_to_index[int(question.id)]]
        for point_id in point_ids
    }
    resource_ids = sorted(
        {
            resource_id
            for point_id in point_ids
            for resource_id in sources.point_to_resources.get(point_id, set())
        }
    )
    prereq_count = len({pre for point_id in point_ids for pre in sources.prereq_points.get(point_id, set())})
    dependent_count = len({post for point_id in point_ids for post in sources.dependent_points.get(point_id, set())})
    related_count = len({rel for point_id in point_ids for rel in sources.related_points.get(point_id, set())})
    stats = sources.answer_stats.get(int(question.id), {"total": 0.0, "correct": 0.0})
    attempt_count = float(stats["total"])
    correct_rate = float(stats["correct"] / stats["total"]) if stats["total"] > 0 else 0.5
    score_value = float(question.score or 1.0)
    meta = {
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
    raw_values = [
        score_value,
        float(len(question.content or "")),
        float(len(question.analysis or "")),
        attempt_count,
        correct_rate,
        float(len(point_ids)),
        float(len(resource_ids)),
        difficulty_to_score(question.difficulty),
    ]
    return meta, raw_values, point_index_map


def _normalize_question_feature_scales(
    *,
    normalize_values,
    chapter_norm_map: dict[str, float],
    score_values: list[float],
    content_lengths: list[float],
    analysis_lengths: list[float],
    attempt_counts: list[float],
    question_kp_counts: list[float],
    question_resource_counts: list[float],
    difficulty_values_raw: list[float],
    question_meta: list[dict[str, object]],
) -> QuestionFeatureScales:
    """统一计算题目特征归一化结果。"""
    return QuestionFeatureScales(
        chapter_norm_map=chapter_norm_map,
        score_norm=normalize_values(score_values),
        content_norm=normalize_values(content_lengths, default_value=0.3),
        analysis_norm=normalize_values(analysis_lengths, default_value=0.2),
        attempt_norm=normalize_values(attempt_counts, default_value=0.0),
        kp_count_norm=normalize_values(question_kp_counts, default_value=0.2),
        resource_count_norm=normalize_values(question_resource_counts, default_value=0.0),
        prereq_norm=normalize_values([float(item["prereq_count"]) for item in question_meta], default_value=0.0),
        dependent_norm=normalize_values([float(item["dependent_count"]) for item in question_meta], default_value=0.0),
        related_norm=normalize_values([float(item["related_count"]) for item in question_meta], default_value=0.0),
        difficulty_values_raw=difficulty_values_raw,
    )


def prepare_question_features(
    *,
    questions: list[Any],
    sources: RuntimeFeatureSources,
    normalize_values,
    difficulty_to_score,
) -> QuestionFeaturePreparation:
    """为题目级运行时构造元信息和归一化特征。"""
    chapter_norm_map = _build_chapter_norm_map(questions, normalize_values)

    score_values: list[float] = []
    content_lengths: list[float] = []
    analysis_lengths: list[float] = []
    attempt_counts: list[float] = []
    correct_rates: list[float] = []
    question_kp_counts: list[float] = []
    question_resource_counts: list[float] = []
    difficulty_values_raw: list[float] = []
    question_meta: list[dict[str, object]] = []
    question_to_points: dict[int, list[int]] = {}
    point_to_question_indices: dict[int, list[int]] = {}
    question_ids = [int(question.id) for question in questions]
    question_id_to_index = {question_id: index for index, question_id in enumerate(question_ids)}

    for question in questions:
        meta, raw_values, point_index_map = _collect_question_feature_entry(
            question=question,
            sources=sources,
            question_id_to_index=question_id_to_index,
            difficulty_to_score=difficulty_to_score,
        )
        point_ids = meta["point_ids"]
        question_to_points[int(question.id)] = point_ids
        for point_id, indices in point_index_map.items():
            point_to_question_indices.setdefault(point_id, []).extend(indices)

        score_values.append(raw_values[0])
        content_lengths.append(raw_values[1])
        analysis_lengths.append(raw_values[2])
        attempt_counts.append(raw_values[3])
        correct_rates.append(raw_values[4])
        question_kp_counts.append(raw_values[5])
        question_resource_counts.append(float(len(meta["resource_ids"])))
        difficulty_values_raw.append(raw_values[7])
        question_meta.append(meta)

    scales = _normalize_question_feature_scales(
        normalize_values=normalize_values,
        chapter_norm_map=chapter_norm_map,
        score_values=score_values,
        content_lengths=content_lengths,
        analysis_lengths=analysis_lengths,
        attempt_counts=attempt_counts,
        question_kp_counts=question_kp_counts,
        question_resource_counts=question_resource_counts,
        difficulty_values_raw=difficulty_values_raw,
        question_meta=question_meta,
    )

    return QuestionFeaturePreparation(
        question_meta=question_meta,
        question_to_points=question_to_points,
        point_to_question_indices=point_to_question_indices,
        question_ids=question_ids,
        question_id_to_index=question_id_to_index,
        scales=scales,
    )


def _pairwise_graph_weight(
    *,
    left_points: set[int],
    right_points: set[int],
    left_resources: set[int],
    right_resources: set[int],
    left_question,
    right_question,
    related_points: dict[int, set[int]],
) -> tuple[float, float, float]:
    """计算两道题之间的图权重及重叠贡献。"""
    share_points = float(len(left_points & right_points))
    share_resources = float(len(left_resources & right_resources))
    related_bridge = 0.0
    if not share_points:
        left_neighbors = {rel for point_id in left_points for rel in related_points.get(point_id, set())}
        if right_points & left_neighbors:
            related_bridge = 1.0
    same_chapter = 1.0 if str(left_question.chapter or "").strip() == str(right_question.chapter or "").strip() else 0.0
    same_type = 1.0 if str(left_question.question_type or "") == str(right_question.question_type or "") else 0.0
    weight = share_points * 2.0 + share_resources * 0.5 + related_bridge * 1.25 + same_chapter * 0.5 + same_type * 0.2
    return weight, share_points, share_resources


def build_graph_statistics(
    *,
    questions: list[Any],
    question_meta: list[dict[str, object]],
    related_points: dict[int, set[int]],
) -> GraphStatisticsBundle:
    """构造题目图邻接矩阵及衍生统计。"""
    import torch

    question_count = len(questions)
    adjacency_matrix = torch.zeros((question_count, question_count), dtype=torch.float32)
    knowledge_overlap_scores = [0.0 for _ in range(question_count)]
    resource_overlap_scores = [0.0 for _ in range(question_count)]

    for left_index in range(question_count):
        left_points = set(question_meta[left_index]["point_ids"])
        left_resources = question_meta[left_index]["resource_ids"]
        left_question = questions[left_index]
        shared_kp_total = 0.0
        shared_resource_total = 0.0
        for right_index in range(left_index + 1, question_count):
            right_points = set(question_meta[right_index]["point_ids"])
            right_resources = question_meta[right_index]["resource_ids"]
            weight, share_points, share_resources = _pairwise_graph_weight(
                left_points=left_points,
                right_points=right_points,
                left_resources=left_resources,
                right_resources=right_resources,
                left_question=left_question,
                right_question=questions[right_index],
                related_points=related_points,
            )
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
    return GraphStatisticsBundle(
        adjacency_matrix=adjacency_matrix,
        degree=degree,
        degree_norm=degree_norm,
        two_hop_density=two_hop_density,
        knowledge_overlap_scores=knowledge_overlap_scores,
        resource_overlap_scores=resource_overlap_scores,
    )


def _build_neighbor_difficulty_tensor(adjacency_matrix, difficulty_values_raw: list[float]):
    """根据邻接矩阵估计每道题的邻域平均难度。"""
    import torch

    difficulty_tensor = torch.tensor(difficulty_values_raw, dtype=torch.float32)
    degree = adjacency_matrix.sum(dim=1)
    return torch.where(
        degree > 0,
        torch.matmul(adjacency_matrix, difficulty_tensor.unsqueeze(1)).squeeze(1) / degree.clamp_min(1.0),
        difficulty_tensor,
    )


def _build_relation_stats_matrix(graph_stats: GraphStatisticsBundle, normalize_values):
    """构造关系统计张量。"""
    import torch

    knowledge_overlap_norm = torch.tensor(
        normalize_values(graph_stats.knowledge_overlap_scores, default_value=0.0),
        dtype=torch.float32,
    )
    resource_overlap_norm = torch.tensor(
        normalize_values(graph_stats.resource_overlap_scores, default_value=0.0),
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


def _build_single_feature_row(
    *,
    question,
    question_meta: dict[str, object],
    index: int,
    scales: QuestionFeatureScales,
    graph_stats: GraphStatisticsBundle,
    neighbor_difficulty_tensor,
    clamp,
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
    feature_map = {
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
    feature_row = [float(feature_map[column]) for column in node_feature_schema]
    type_index = int(question_type_vocab.get(str(question.question_type or "").strip(), 0))
    return feature_row, response_time_proxy, type_index


def build_runtime_feature_rows(
    *,
    questions: list[Any],
    preparation: QuestionFeaturePreparation,
    graph_stats: GraphStatisticsBundle,
    normalize_values,
    clamp,
    question_type_vocab: dict[str, int],
    node_feature_schema: list[str],
) -> tuple[list[list[float]], Any, list[float], list[float], list[int]]:
    """把题目元特征整理成模型输入张量所需的列表。"""
    neighbor_difficulty_tensor = _build_neighbor_difficulty_tensor(
        graph_stats.adjacency_matrix,
        preparation.scales.difficulty_values_raw,
    )
    relation_stats_matrix = _build_relation_stats_matrix(graph_stats, normalize_values)

    response_time_proxy_values: list[float] = []
    feature_rows: list[list[float]] = []
    type_indices: list[int] = []
    for index, question in enumerate(questions):
        feature_row, response_time_proxy, type_index = _build_single_feature_row(
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
        response_time_proxy_values.append(response_time_proxy)
        feature_rows.append(feature_row)
        type_indices.append(type_index)

    return (
        feature_rows,
        relation_stats_matrix,
        preparation.scales.difficulty_values_raw,
        response_time_proxy_values,
        type_indices,
    )
