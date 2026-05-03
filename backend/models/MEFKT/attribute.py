"""MEFKT 属性视角编码组件。"""

from __future__ import annotations

from dataclasses import dataclass

import torch
import torch.nn.functional as functional
from torch import Tensor, nn

from .constants import RELATION_STAT_SCHEMA


# 维护意图：保存属性视角编码及其损失分量
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class AttributeEncodingResult:
    """保存属性视角编码及其损失分量。"""

    embedding: Tensor
    difficulty_loss: Tensor
    similarity_loss: Tensor


# 维护意图：构建包含难度、类型、时距和关系统计的属性视角表示
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class MultiAttributeEncoder(nn.Module):
    """构建包含难度、类型、时距和关系统计的属性视角表示。"""

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

    # 维护意图：在旧调用方式下自动构造关系统计。
    # 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
    # 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
    def _build_default_relation_stats(
        self,
        node_feature_matrix: Tensor,
        exercise_adjacency: Tensor,
        auxiliary_similarity: Tensor | None,
    ) -> Tensor:
        """
        在旧调用方式下自动构造关系统计。

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

    # 维护意图：编码属性视角并返回难度/相似性损失。
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

        兼容旧版 `exercise_skill_matrix` / `skill_adjacency` 调用。
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

        adjacency = (exercise_adjacency.float() > 0).float()
        degree_norm = adjacency.sum(dim=1)
        degree_norm /= degree_norm.max().clamp_min(1.0)
        scalar_inputs = torch.stack(
            [
                difficulty_vector.float(),
                response_time_vector.float(),
                degree_norm,
                relation_stats_matrix[:, 0].float(),
            ],
            dim=1,
        )

        feature_vector = self.feature_projection(node_feature_matrix.float())
        type_vector = self.type_embedding(exercise_type_vector.long())
        scalar_vector = self.scalar_projection(scalar_inputs)
        relation_vector = self.relation_projection(relation_stats_matrix.float())
        encoded_input = torch.cat(
            [feature_vector, type_vector, scalar_vector, relation_vector],
            dim=1,
        )
        side_embedding = self.encoder(encoded_input)

        predicted_difficulty = torch.sigmoid(self.difficulty_head(side_embedding)).squeeze(1)
        difficulty_loss = functional.mse_loss(
            predicted_difficulty,
            difficulty_vector.float(),
        )

        adjacency_logits = torch.matmul(side_embedding, side_embedding.transpose(0, 1))
        adjacency_loss = functional.binary_cross_entropy_with_logits(
            adjacency_logits,
            adjacency,
        )
        relation_prediction = torch.sigmoid(self.relation_head(side_embedding))
        relation_loss = functional.mse_loss(
            relation_prediction,
            relation_stats_matrix.float().clamp(0.0, 1.0),
        )
        if self.type_head.out_features > 1:
            type_loss = functional.cross_entropy(
                self.type_head(side_embedding),
                exercise_type_vector.long(),
            )
        else:
            type_loss = side_embedding.new_tensor(0.0)
        similarity_loss = adjacency_loss + relation_loss + type_loss * 0.05
        return AttributeEncodingResult(
            embedding=side_embedding,
            difficulty_loss=difficulty_loss,
            similarity_loss=similarity_loss,
        )


__all__ = ["AttributeEncodingResult", "MultiAttributeEncoder"]
