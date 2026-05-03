"""MEFKT 图结构编码组件。"""

from __future__ import annotations

import torch
import torch.nn.functional as functional
from torch import Tensor, nn


# 维护意图：归一化稠密邻接矩阵，避免图卷积时节点度差异过大。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
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


# 维护意图：仅加载键名与形状同时匹配的权重。
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_compatible_state(
    module: nn.Module,
    state_dict: dict[str, Tensor],
) -> dict[str, list[str]]:
    """
    仅加载键名与形状同时匹配的权重。

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


# 维护意图：课程级稠密题图使用的简化版 GCN 层
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class GraphConvolutionLayer(nn.Module):
    """课程级稠密题图使用的简化版 GCN 层。"""

    def __init__(self, input_dim: int, output_dim: int) -> None:
        """
        初始化单层图卷积。

        :param input_dim: 输入特征维度。
        :param output_dim: 输出特征维度。
        """
        super().__init__()
        self.linear = nn.Linear(input_dim, output_dim)

    # 维护意图：执行一层图卷积。
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def forward(self, normalized_adjacency: Tensor, node_features: Tensor) -> Tensor:
        """
        执行一层图卷积。

        :param normalized_adjacency: 已归一化邻接矩阵。
        :param node_features: 节点特征矩阵。
        :return: 新的节点表示。
        """
        propagated = torch.matmul(normalized_adjacency, node_features)
        return self.linear(propagated)


# 维护意图：基于 DGI 风格目标的结构视角编码器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class GraphContrastiveEncoder(nn.Module):
    """基于 DGI 风格目标的结构视角编码器。"""

    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int) -> None:
        """
        初始化结构编码器。

        :param input_dim: 初始特征维度。
        :param hidden_dim: 中间隐藏维度。
        :param output_dim: 输出嵌入维度。
        """
        super().__init__()
        self.gcn_first = GraphConvolutionLayer(input_dim, hidden_dim)
        self.gcn_second = GraphConvolutionLayer(hidden_dim, output_dim)
        self.readout_gate = nn.Linear(output_dim, output_dim, bias=False)

    # 维护意图：根据图结构编码节点表示。
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    # 维护意图：计算结构视角嵌入与 DGI 风格对比损失。
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def contrastive_loss(
        self,
        node_features: Tensor,
        adjacency_matrix: Tensor,
    ) -> tuple[Tensor, Tensor]:
        """
        计算结构视角嵌入与 DGI 风格对比损失。

        :return: `(节点嵌入, 对比损失)`。
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


__all__ = [
    "normalize_dense_adjacency",
    "load_compatible_state",
    "GraphConvolutionLayer",
    "GraphContrastiveEncoder",
]
