"""Vanilla RNN implementation used by the legacy DKT trainer."""

import torch
import torch.nn as nn
# PyTorch 深度学习框架
from torch.autograd import Variable
from sklearn.model_selection import train_test_split


class DKT(nn.Module):
    """Predict next-question correctness from historical interaction sequences."""

    def __init__(self, input_dim, hidden_dim, layer_dim, output_dim):
        """Create the recurrent encoder and output projection layers."""
        super(DKT, self).__init__()
        # 保存隐藏层维度，用于初始化零向量
        self.hidden_dim = hidden_dim
        # RNN 堆叠层数（深层 RNN 能捕获更复杂的时序模式）
        self.layer_dim = layer_dim
        # 输出维度 = 题目数量，每个维度代表对应题目的掌握概率
        self.output_dim = output_dim
        # RNN 编码器：tanh 激活函数，batch_first=True 使输入形状为 (batch, seq, feat)
        self.rnn = nn.RNN(input_dim, hidden_dim, layer_dim, batch_first=True, nonlinearity='tanh')
        # 全连接投影层：将 hidden_dim 映射到 output_dim（题目数量）
        self.fc = nn.Linear(self.hidden_dim, self.output_dim)
        # Sigmoid 将 logits 压缩到 [0,1] 概率区间
        self.sig = nn.Sigmoid()

    def forward(self, x):
        """Run the interaction sequence through the RNN and squash logits to probabilities."""
        # 每个批次重置隐状态——每个学生序列独立，不共享历史
        h0 = Variable(
            torch.zeros(
                self.layer_dim,
                x.size(0),
                self.hidden_dim,
                device=x.device,
            )
        )
        # RNN 前向传播：out 形状 (batch, seq_len, hidden_dim)
        out, hn = self.rnn(x, h0)
        # 投影到题目空间并用 Sigmoid 得到掌握概率
        res = self.sig(self.fc(out))
        return res
