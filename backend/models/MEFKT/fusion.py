"""MEFKT 结构视角与属性视角融合层。"""

from __future__ import annotations

import torch
from torch import Tensor, nn


# 维护意图：将结构视角与属性视角嵌入线性对齐后再拼接
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class LinearAlignmentFusion(nn.Module):
    """将结构视角与属性视角嵌入线性对齐后再拼接。"""

    def __init__(self, struct_dim: int, side_dim: int, align_dim: int) -> None:
        """
        初始化对齐层。

        :param struct_dim: 结构嵌入维度。
        :param side_dim: 属性嵌入维度。
        :param align_dim: 对齐后的共同维度。
        """
        super().__init__()
        self.struct_projection = nn.Linear(struct_dim, align_dim)
        self.side_projection = nn.Linear(side_dim, align_dim)

    # 维护意图：对齐并输出最终融合嵌入。
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def forward(self, struct_embedding: Tensor, side_embedding: Tensor) -> Tensor:
        """
        对齐并输出最终融合嵌入。

        :return: 拼接后的融合嵌入。
        """
        aligned_struct = torch.tanh(self.struct_projection(struct_embedding))
        aligned_side = torch.tanh(self.side_projection(side_embedding))
        return torch.cat([aligned_struct, aligned_side], dim=1)


__all__ = ["LinearAlignmentFusion"]
