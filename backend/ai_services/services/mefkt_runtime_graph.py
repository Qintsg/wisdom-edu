#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""MEFKT 在线运行时题目图统计。"""

from __future__ import annotations

from ai_services.services.mefkt_runtime_types import GraphStatisticsBundle, QuestionLike


# 维护意图：计算两道题之间的图权重及重叠贡献
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def pairwise_graph_weight(
    *,
    left_points: set[int],
    right_points: set[int],
    left_resources: set[int],
    right_resources: set[int],
    left_question: QuestionLike,
    right_question: QuestionLike,
    related_points: dict[int, set[int]],
) -> tuple[float, float, float]:
    """计算两道题之间的图权重及重叠贡献。"""
    share_points = float(len(left_points & right_points))
    share_resources = float(len(left_resources & right_resources))
    related_bridge = compute_related_bridge_score(
        left_points=left_points,
        right_points=right_points,
        related_points=related_points,
        share_points=share_points,
    )
    same_chapter = 1.0 if str(left_question.chapter or "").strip() == str(right_question.chapter or "").strip() else 0.0
    same_type = 1.0 if str(left_question.question_type or "") == str(right_question.question_type or "") else 0.0
    weight = share_points * 2.0 + share_resources * 0.5 + related_bridge * 1.25 + same_chapter * 0.5 + same_type * 0.2
    return weight, share_points, share_resources


# 维护意图：当两题无直接知识点重叠时，检查相关关系是否形成桥接
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def compute_related_bridge_score(
    *,
    left_points: set[int],
    right_points: set[int],
    related_points: dict[int, set[int]],
    share_points: float,
) -> float:
    """当两题无直接知识点重叠时，检查相关关系是否形成桥接。"""
    if share_points:
        return 0.0
    left_neighbors = {rel for point_id in left_points for rel in related_points.get(point_id, set())}
    return 1.0 if right_points & left_neighbors else 0.0


# 维护意图：构造题目图邻接矩阵及衍生统计
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_graph_statistics(
    *,
    questions: list[QuestionLike],
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
        accumulate_left_question_edges(
            questions=questions,
            question_meta=question_meta,
            related_points=related_points,
            adjacency_matrix=adjacency_matrix,
            knowledge_overlap_scores=knowledge_overlap_scores,
            resource_overlap_scores=resource_overlap_scores,
            left_index=left_index,
        )

    degree = adjacency_matrix.sum(dim=1)
    degree_norm = degree / degree.max().clamp_min(1.0)
    two_hop_density = build_two_hop_density(adjacency_matrix, degree_norm, question_count)
    return GraphStatisticsBundle(
        adjacency_matrix=adjacency_matrix,
        degree=degree,
        degree_norm=degree_norm,
        two_hop_density=two_hop_density,
        knowledge_overlap_scores=knowledge_overlap_scores,
        resource_overlap_scores=resource_overlap_scores,
    )


# 维护意图：累计指定左侧题目与后续题目的无向边权重
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def accumulate_left_question_edges(
    *,
    questions: list[QuestionLike],
    question_meta: list[dict[str, object]],
    related_points: dict[int, set[int]],
    adjacency_matrix,
    knowledge_overlap_scores: list[float],
    resource_overlap_scores: list[float],
    left_index: int,
) -> None:
    """累计指定左侧题目与后续题目的无向边权重。"""
    left_points = set(question_meta[left_index]["point_ids"])
    left_resources = question_meta[left_index]["resource_ids"]
    shared_kp_total = 0.0
    shared_resource_total = 0.0
    for right_index in range(left_index + 1, len(questions)):
        weight, share_points, share_resources = pairwise_graph_weight(
            left_points=left_points,
            right_points=set(question_meta[right_index]["point_ids"]),
            left_resources=left_resources,
            right_resources=question_meta[right_index]["resource_ids"],
            left_question=questions[left_index],
            right_question=questions[right_index],
            related_points=related_points,
        )
        if weight <= 0:
            continue
        adjacency_matrix[left_index, right_index] = weight
        adjacency_matrix[right_index, left_index] = weight
        shared_kp_total += share_points
        shared_resource_total += share_resources
        knowledge_overlap_scores[right_index] += share_points
        resource_overlap_scores[right_index] += share_resources
    knowledge_overlap_scores[left_index] += shared_kp_total
    resource_overlap_scores[left_index] += shared_resource_total


# 维护意图：计算每道题可经两跳到达的题目比例
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_two_hop_density(adjacency_matrix, degree_norm, question_count: int):
    """计算每道题可经两跳到达的题目比例。"""
    import torch

    if question_count <= 1:
        return torch.zeros_like(degree_norm)
    connected_matrix = (adjacency_matrix > 0).float()
    two_hop = (torch.matmul(connected_matrix, connected_matrix) > 0).float()
    return two_hop.sum(dim=1) / float(question_count - 1)
