#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
MEFKT 共享模型组件。
@Project : wisdom-edu
@File : model.py
@Author : Qintsg
@Date : 2026-04-04
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn.functional as functional
from torch import Tensor, nn


QUESTION_TYPE_VOCAB: dict[str, int] = {
    "unknown": 0,
    "single_choice": 1,
    "multiple_choice": 2,
    "true_false": 3,
    "fill_blank": 4,
    "short_answer": 5,
    "code": 6,
}

NODE_FEATURE_SCHEMA: tuple[str, ...] = (
    "difficulty_proxy",
    "response_time_proxy",
    "occurrence_proxy",
    "degree_norm",
    "two_hop_density",
    "neighbor_difficulty",
    "knowledge_count_norm",
    "resource_count_norm",
    "prerequisite_count_norm",
    "dependent_count_norm",
    "related_count_norm",
    "chapter_position_norm",
    "content_length_norm",
    "analysis_length_norm",
    "question_score_norm",
    "historical_correct_rate",
)

RELATION_STAT_SCHEMA: tuple[str, ...] = (
    "degree_norm",
    "two_hop_density",
    "knowledge_overlap",
    "resource_overlap",
)


def normalize_dense_adjacency(adjacency_matrix: Tensor) -> Tensor:
    """
    归一化稠密邻接矩阵，避免图卷积时节点度差异过大。
    :param adjacency_matrix: 稠密邻接矩阵。
    :return: 对称归一化后的邻接矩阵。
    """
    device = adjacency_matrix.device
    identity = torch.eye(adjacency_matrix.size(0), device=device)
    matrix_with_self_loop = adjacency_matrix.float() + identity
    degree_vector = matrix_with_self_loop.sum(dim=1).clamp_min(1.0)
    inverse_sqrt_degree = torch.pow(degree_vector, -0.5)
    normalized = (
        inverse_sqrt_degree.unsqueeze(1)
        * matrix_with_self_loop
        * inverse_sqrt_degree.unsqueeze(0)
    )
    return normalized


def load_compatible_state(
    module: nn.Module,
    state_dict: dict[str, Tensor],
) -> dict[str, list[str]]:
    """
    仅加载键名与形状同时匹配的权重，便于运行时课程级重建后复用公共预训练参数。
    :param module: 待加载模块。
    :param state_dict: 外部权重字典。
    :return: 加载摘要。
    """
    current_state = module.state_dict()
    matched: dict[str, Tensor] = {}
    skipped: list[str] = []
    for key, value in state_dict.items():
        if key in current_state and tuple(current_state[key].shape) == tuple(value.shape):
            matched[key] = value
        else:
            skipped.append(key)
    current_state.update(matched)
    module.load_state_dict(current_state, strict=False)
    missing = [key for key in current_state.keys() if key not in matched]
    return {
        "loaded": sorted(matched.keys()),
        "skipped": sorted(skipped),
        "missing": sorted(missing),
    }


class GraphConvolutionLayer(nn.Module):
    """
    简化版 GCN 层。

    这里继续使用稠密邻接矩阵，是因为课程级题图规模通常在几百节点内，
    优先保证训练/在线推理共享同一套实现，避免维护两套图算子分支。
    """

    def __init__(self, input_dim: int, output_dim: int) -> None:
        """
        初始化单层图卷积。
        :param input_dim: 输入特征维度。
        :param output_dim: 输出特征维度。
        :return: None。
        """
        super().__init__()
        self.linear = nn.Linear(input_dim, output_dim)

    def forward(self, normalized_adjacency: Tensor, node_features: Tensor) -> Tensor:
        """
        执行一层图卷积。
        :param normalized_adjacency: 已归一化邻接矩阵。
        :param node_features: 节点特征矩阵。
        :return: 新的节点表示。
        """
        propagated = torch.matmul(normalized_adjacency, node_features)
        return self.linear(propagated)


class GraphContrastiveEncoder(nn.Module):
    """
    基于 DGI 风格目标的结构视角编码器。

    这部分继续承担“结构无监督预训练”的职责：
    - 公共数据阶段：学习交互转移图中的结构先验；
    - 课程在线阶段：将题目图重新编码到同一结构表征空间。
    """

    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int) -> None:
        """
        初始化结构编码器。
        :param input_dim: 初始特征维度。
        :param hidden_dim: 中间隐藏维度。
        :param output_dim: 输出嵌入维度。
        :return: None。
        """
        super().__init__()
        self.gcn_first = GraphConvolutionLayer(input_dim, hidden_dim)
        self.gcn_second = GraphConvolutionLayer(hidden_dim, output_dim)
        self.readout_gate = nn.Linear(output_dim, output_dim, bias=False)

    def encode(self, node_features: Tensor, adjacency_matrix: Tensor) -> Tensor:
        """
        根据图结构编码节点表示。
        :param node_features: 节点特征。
        :param adjacency_matrix: 邻接矩阵。
        :return: 节点嵌入。
        """
        normalized = normalize_dense_adjacency(adjacency_matrix)
        hidden = functional.relu(self.gcn_first(normalized, node_features))
        output = self.gcn_second(normalized, hidden)
        return output

    def contrastive_loss(
        self,
        node_features: Tensor,
        adjacency_matrix: Tensor,
    ) -> tuple[Tensor, Tensor]:
        """
        计算结构视角嵌入与 DGI 风格对比损失。
        :param node_features: 节点特征矩阵。
        :param adjacency_matrix: 邻接矩阵。
        :return: (节点嵌入, 对比损失)。
        """
        positive_embedding = self.encode(node_features, adjacency_matrix)
        shuffled_indices = torch.randperm(node_features.size(0), device=node_features.device)
        negative_embedding = self.encode(node_features[shuffled_indices], adjacency_matrix)

        graph_summary = torch.sigmoid(positive_embedding.mean(dim=0, keepdim=True))
        projected_summary = self.readout_gate(graph_summary)
        positive_logits = torch.sum(positive_embedding * projected_summary, dim=1)
        negative_logits = torch.sum(negative_embedding * projected_summary, dim=1)

        positive_loss = functional.binary_cross_entropy_with_logits(
            positive_logits,
            torch.ones_like(positive_logits),
        )
        negative_loss = functional.binary_cross_entropy_with_logits(
            negative_logits,
            torch.zeros_like(negative_logits),
        )
        return positive_embedding, positive_loss + negative_loss


@dataclass(frozen=True)
class AttributeEncodingResult:
    """保存属性视角编码及其损失分量。"""

    embedding: Tensor
    difficulty_loss: Tensor
    similarity_loss: Tensor


class MultiAttributeEncoder(nn.Module):
    """
    构建包含难度、类型、时距和关系统计的属性视角表示。

    与旧版“固定技能数矩阵”不同，这里改为“固定特征维度”设计：
    - 训练阶段使用公开数据构造统一特征槽位；
    - 在线阶段使用课程题目/知识图谱/资源关系填充同一槽位；
    - 这样模型参数不再绑定某个课程的知识点数量，可直接迁移到题目级部署。
    """

    def __init__(
        self,
        feature_dim: int,
        type_count: int,
        embed_dim: int,
        relation_dim: int | None = None,
    ) -> None:
        """
        初始化属性编码器。
        :param feature_dim: 节点特征维度。
        :param type_count: 类型数量。
        :param embed_dim: 嵌入维度。
        :param relation_dim: 关系统计维度。
        :return: None。
        """
        super().__init__()
        safe_type_count = max(1, type_count)
        safe_relation_dim = max(1, relation_dim or len(RELATION_STAT_SCHEMA))
        self.feature_projection = nn.Sequential(
            nn.Linear(feature_dim, embed_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(embed_dim, embed_dim),
            nn.LayerNorm(embed_dim),
        )
        self.type_embedding = nn.Embedding(safe_type_count, embed_dim)
        self.scalar_projection = nn.Sequential(
            nn.Linear(4, embed_dim),
            nn.ReLU(),
            nn.Linear(embed_dim, embed_dim),
        )
        self.relation_projection = nn.Sequential(
            nn.Linear(safe_relation_dim, embed_dim),
            nn.ReLU(),
            nn.Linear(embed_dim, embed_dim),
        )
        self.encoder = nn.Sequential(
            nn.Linear(embed_dim * 4, embed_dim * 2),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(embed_dim * 2, embed_dim),
            nn.LayerNorm(embed_dim),
        )
        self.difficulty_head = nn.Linear(embed_dim, 1)
        self.type_head = nn.Linear(embed_dim, safe_type_count)
        self.relation_head = nn.Linear(embed_dim, safe_relation_dim)

    def _build_default_relation_stats(
        self,
        node_feature_matrix: Tensor,
        exercise_adjacency: Tensor,
        auxiliary_similarity: Tensor | None,
    ) -> Tensor:
        """
        在旧调用方式下自动构造关系统计，保证兼容旧训练与测试代码。
        :param node_feature_matrix: 节点特征矩阵。
        :param exercise_adjacency: 节点邻接矩阵。
        :param auxiliary_similarity: 可选的辅助关系矩阵。
        :return: 关系统计矩阵。
        """
        node_count = max(int(exercise_adjacency.size(0)), 1)
        adjacency = (exercise_adjacency.float() > 0).float()
        degree = adjacency.sum(dim=1)
        degree_norm = degree / degree.max().clamp_min(1.0)
        if node_count > 1:
            two_hop = (torch.matmul(adjacency, adjacency) > 0).float()
            two_hop_density = two_hop.sum(dim=1) / float(node_count - 1)
        else:
            two_hop_density = torch.zeros_like(degree_norm)
        feature_overlap = node_feature_matrix.float().mean(dim=1)
        if auxiliary_similarity is None:
            relation_overlap = degree_norm
        else:
            relation_overlap = auxiliary_similarity.float().mean(dim=1)
        return torch.stack(
            [degree_norm, two_hop_density, feature_overlap, relation_overlap],
            dim=1,
        )

    def forward(
        self,
        node_feature_matrix: Tensor | None = None,
        difficulty_vector: Tensor | None = None,
        response_time_vector: Tensor | None = None,
        exercise_type_vector: Tensor | None = None,
        exercise_adjacency: Tensor | None = None,
        relation_stats_matrix: Tensor | None = None,
        exercise_skill_matrix: Tensor | None = None,
        skill_adjacency: Tensor | None = None,
    ) -> AttributeEncodingResult:
        """
        编码属性视角并返回难度/相似性损失。

        兼容策略：
        - 新版调用传入 `node_feature_matrix` 与 `relation_stats_matrix`；
        - 旧版调用仍可传入 `exercise_skill_matrix` / `skill_adjacency`，内部自动降级映射。
        """
        if node_feature_matrix is None:
            if exercise_skill_matrix is None:
                raise ValueError("MultiAttributeEncoder 缺少 node_feature_matrix")
            node_feature_matrix = exercise_skill_matrix.float()
        if exercise_adjacency is None:
            node_count = int(node_feature_matrix.size(0))
            exercise_adjacency = torch.eye(node_count, device=node_feature_matrix.device)
        if difficulty_vector is None:
            difficulty_vector = torch.zeros(node_feature_matrix.size(0), device=node_feature_matrix.device)
        if response_time_vector is None:
            response_time_vector = torch.zeros(node_feature_matrix.size(0), device=node_feature_matrix.device)
        if exercise_type_vector is None:
            exercise_type_vector = torch.zeros(
                node_feature_matrix.size(0),
                device=node_feature_matrix.device,
                dtype=torch.long,
            )
        if relation_stats_matrix is None:
            relation_stats_matrix = self._build_default_relation_stats(
                node_feature_matrix=node_feature_matrix,
                exercise_adjacency=exercise_adjacency,
                auxiliary_similarity=skill_adjacency,
            )

        resolved_node_feature_matrix = node_feature_matrix
        resolved_difficulty_vector = difficulty_vector
        resolved_response_time_vector = response_time_vector
        resolved_exercise_type_vector = exercise_type_vector
        resolved_exercise_adjacency = exercise_adjacency
        resolved_relation_stats_matrix = relation_stats_matrix

        adjacency = (resolved_exercise_adjacency.float() > 0).float()
        degree_norm = adjacency.sum(dim=1)
        degree_norm /= degree_norm.max().clamp_min(1.0)
        scalar_inputs = torch.stack(
            [
                resolved_difficulty_vector.float(),
                resolved_response_time_vector.float(),
                degree_norm,
                resolved_relation_stats_matrix[:, 0].float(),
            ],
            dim=1,
        )

        feature_vector = self.feature_projection(resolved_node_feature_matrix.float())
        type_vector = self.type_embedding(resolved_exercise_type_vector.long())
        scalar_vector = self.scalar_projection(scalar_inputs)
        relation_vector = self.relation_projection(resolved_relation_stats_matrix.float())
        encoded_input = torch.cat(
            [feature_vector, type_vector, scalar_vector, relation_vector],
            dim=1,
        )
        side_embedding = self.encoder(encoded_input)

        predicted_difficulty = torch.sigmoid(self.difficulty_head(side_embedding)).squeeze(1)
        difficulty_loss = functional.mse_loss(
            predicted_difficulty,
            resolved_difficulty_vector.float(),
        )

        adjacency_logits = torch.matmul(side_embedding, side_embedding.transpose(0, 1))
        adjacency_loss = functional.binary_cross_entropy_with_logits(
            adjacency_logits,
            adjacency,
        )
        relation_prediction = torch.sigmoid(self.relation_head(side_embedding))
        relation_loss = functional.mse_loss(
            relation_prediction,
            resolved_relation_stats_matrix.float().clamp(0.0, 1.0),
        )
        if self.type_head.out_features > 1:
            type_loss = functional.cross_entropy(
                self.type_head(side_embedding),
                resolved_exercise_type_vector.long(),
            )
        else:
            type_loss = side_embedding.new_tensor(0.0)
        similarity_loss = adjacency_loss + relation_loss + type_loss * 0.05
        return AttributeEncodingResult(
            embedding=side_embedding,
            difficulty_loss=difficulty_loss,
            similarity_loss=similarity_loss,
        )


class LinearAlignmentFusion(nn.Module):
    """将结构视角与属性视角嵌入线性对齐后再拼接。"""

    def __init__(self, struct_dim: int, side_dim: int, align_dim: int) -> None:
        """
        初始化对齐层。
        :param struct_dim: 结构嵌入维度。
        :param side_dim: 属性嵌入维度。
        :param align_dim: 对齐后的共同维度。
        :return: None。
        """
        super().__init__()
        self.struct_projection = nn.Linear(struct_dim, align_dim)
        self.side_projection = nn.Linear(side_dim, align_dim)

    def forward(self, struct_embedding: Tensor, side_embedding: Tensor) -> Tensor:
        """
        对齐并输出最终融合嵌入。
        :param struct_embedding: 结构视角嵌入。
        :param side_embedding: 属性视角嵌入。
        :return: 拼接后的融合嵌入。
        """
        aligned_struct = torch.tanh(self.struct_projection(struct_embedding))
        aligned_side = torch.tanh(self.side_projection(side_embedding))
        return torch.cat([aligned_struct, aligned_side], dim=1)


class MEFKTSequenceModel(nn.Module):
    """
    融合遗忘机制的序列预测模型。

    该模型继续承担最终序列决策，但 item_embedding 不再绑定训练课程：
    - 训练期用公开交互图生成“公共习题槽位”嵌入；
    - 在线期可用课程题目图重新生成嵌入，再加载兼容的序列层参数完成题目级部署。
    """

    def __init__(
        self,
        item_count: int,
        item_embedding_dim: int,
        num_heads: int = 4,
        head_dim: int = 32,
        pretrained_item_embedding: Tensor | None = None,
    ) -> None:
        """
        初始化 MEFKT 行为预测模型。
        :param item_count: 节点数量。
        :param item_embedding_dim: 节点嵌入维度。
        :param num_heads: 注意力头数。
        :param head_dim: 单头维度。
        :param pretrained_item_embedding: 预训练节点嵌入。
        :return: None。
        """
        super().__init__()
        self.item_embedding = nn.Embedding(item_count, item_embedding_dim)
        if pretrained_item_embedding is not None:
            self.item_embedding.weight.data.copy_(pretrained_item_embedding)
        self.answer_embedding = nn.Embedding(2, item_embedding_dim)
        self.query_projection = nn.Linear(item_embedding_dim, num_heads * head_dim)
        self.key_projection = nn.Linear(item_embedding_dim, num_heads * head_dim)
        self.value_projection = nn.Linear(item_embedding_dim, num_heads * head_dim)
        self.history_projection = nn.Linear(item_embedding_dim * 2, item_embedding_dim)
        self.output_layer = nn.Sequential(
            nn.Linear(num_heads * head_dim + item_embedding_dim, item_embedding_dim),
            nn.ReLU(),
            nn.Dropout(p=0.1),
            nn.Linear(item_embedding_dim, 1),
        )
        self.num_heads = num_heads
        self.head_dim = head_dim
        self.theta_raw = nn.Parameter(torch.zeros(num_heads))

    def _perceived_distance(
        self,
        history_time_gap: Tensor,
        relevance_score: Tensor,
    ) -> Tensor:
        """
        估计从历史位置到当前预测位置的可感知距离。
        :param history_time_gap: 历史时间间隔。
        :param relevance_score: 历史相关性分布。
        :return: 每个位置的感知距离。
        """
        step_distance = torch.arange(
            history_time_gap.size(0),
            0,
            -1,
            device=history_time_gap.device,
            dtype=history_time_gap.dtype,
        )
        normalized_gap = history_time_gap.clamp_min(1.0)
        reverse_gap = torch.flip(normalized_gap, dims=[0])
        cumulative_gap = torch.flip(torch.cumsum(reverse_gap, dim=0), dims=[0])

        reverse_relevance = torch.flip(relevance_score, dims=[0])
        cumulative_relevance = torch.flip(torch.cumsum(reverse_relevance, dim=0), dims=[0])
        return (
            step_distance.unsqueeze(1)
            * cumulative_gap.unsqueeze(1)
            * cumulative_relevance
        )

    def predict_candidate(
        self,
        history_item_indices: Tensor,
        history_correct_flags: Tensor,
        history_time_gaps: Tensor,
        candidate_item_indices: Tensor,
    ) -> Tensor:
        """
        基于历史序列为候选节点计算正确概率。
        :param history_item_indices: 历史节点索引。
        :param history_correct_flags: 历史正误标签。
        :param history_time_gaps: 历史时间间隔代理。
        :param candidate_item_indices: 候选节点索引。
        :return: 候选概率张量。
        """
        if history_item_indices.numel() <= 0:
            candidate_embedding = self.item_embedding(candidate_item_indices.long())
            base_logit = self.output_layer(
                torch.cat(
                    [
                        torch.zeros(
                            candidate_embedding.size(0),
                            self.num_heads * self.head_dim,
                            device=candidate_embedding.device,
                        ),
                        candidate_embedding,
                    ],
                    dim=1,
                )
            )
            return torch.sigmoid(base_logit.squeeze(1))

        history_embedding = self.item_embedding(history_item_indices.long())
        answer_embedding = self.answer_embedding(history_correct_flags.long())
        interaction_embedding = self.history_projection(
            torch.cat([history_embedding, answer_embedding], dim=1)
        )

        history_query = self.query_projection(history_embedding).view(
            -1,
            self.num_heads,
            self.head_dim,
        )
        history_key = self.key_projection(history_embedding).view(
            -1,
            self.num_heads,
            self.head_dim,
        )
        self_relevance = torch.sum(history_query * history_key, dim=2) / math.sqrt(self.head_dim)
        relevance_score = torch.softmax(self_relevance, dim=0)
        perceived_distance = self._perceived_distance(history_time_gaps.float(), relevance_score)

        theta = functional.softplus(self.theta_raw).view(1, self.num_heads) + 1e-4
        key_tensor = self.key_projection(history_embedding).view(-1, self.num_heads, self.head_dim)
        value_tensor = self.value_projection(interaction_embedding).view(-1, self.num_heads, self.head_dim)

        predicted_probabilities: list[Tensor] = []
        for candidate_index in candidate_item_indices.long():
            candidate_embedding = self.item_embedding(candidate_index)
            query_tensor = self.query_projection(candidate_embedding).view(self.num_heads, self.head_dim)
            raw_score = torch.sum(key_tensor * query_tensor.unsqueeze(0), dim=2) / math.sqrt(self.head_dim)
            decay_score = torch.exp(-theta * perceived_distance)
            attention_weight = torch.softmax(raw_score * decay_score, dim=0)
            context_vector = torch.sum(attention_weight.unsqueeze(2) * value_tensor, dim=0).reshape(-1)
            logit = self.output_layer(
                torch.cat([context_vector, candidate_embedding], dim=0)
            ).squeeze(0)
            predicted_probabilities.append(torch.sigmoid(logit))
        return torch.stack(predicted_probabilities, dim=0)

    def forward(
        self,
        sequence_item_indices: Tensor,
        sequence_correct_flags: Tensor,
        sequence_time_gaps: Tensor,
    ) -> tuple[Tensor, Tensor]:
        """
        对一批序列执行下一题预测。
        :param sequence_item_indices: 序列节点索引，padding 为 -1。
        :param sequence_correct_flags: 序列正误标签。
        :param sequence_time_gaps: 序列时间间隔。
        :return: (预测概率, 有效位置掩码)。
        """
        batch_size, sequence_length = sequence_item_indices.shape
        prediction = torch.zeros(
            batch_size,
            sequence_length - 1,
            device=sequence_item_indices.device,
        )
        valid_mask = torch.zeros(
            batch_size,
            sequence_length - 1,
            dtype=torch.bool,
            device=sequence_item_indices.device,
        )

        for batch_index in range(batch_size):
            valid_positions = torch.nonzero(
                sequence_item_indices[batch_index] >= 0,
                as_tuple=False,
            ).flatten()
            if valid_positions.numel() <= 1:
                continue
            last_position = int(valid_positions[-1].item())
            for target_position in range(1, last_position + 1):
                history_indices = sequence_item_indices[batch_index, :target_position]
                history_mask = history_indices >= 0
                history_indices = history_indices[history_mask]
                history_correct = sequence_correct_flags[batch_index, :target_position][history_mask]
                history_time_gap = sequence_time_gaps[batch_index, :target_position][history_mask]
                candidate_index = sequence_item_indices[
                    batch_index,
                    target_position : target_position + 1,
                ]
                probability = self.predict_candidate(
                    history_item_indices=history_indices,
                    history_correct_flags=history_correct,
                    history_time_gaps=history_time_gap,
                    candidate_item_indices=candidate_index,
                )[0]
                prediction[batch_index, target_position - 1] = probability
                valid_mask[batch_index, target_position - 1] = True
        return prediction, valid_mask