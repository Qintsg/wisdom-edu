"""Torch dataset wrapper for one-hot encoded DKT interaction sequences."""

import numpy as np
# PyTorch 深度学习框架
from torch.utils.data.dataset import Dataset
# 常量模块定义了 MAX_STEP（序列最大长度）和 NUM_OF_QUESTIONS（题目总数）
from Constant import Constants as constants
import torch


class DKTDataSet(Dataset):
    """Expose question and answer sequences in the format expected by the DKT model."""

    def __init__(self, ques, ans):
        """Store aligned question and answer matrices."""
        # 题目编号矩阵，形状 (num_students, max_step)
        self.ques = ques
        # 对应作答矩阵，0=错误 1=正确 -1=填充
        self.ans = ans

    def __len__(self):
        """Return the number of student interaction sequences."""
        # 每行对应一条学生子序列
        return len(self.ques)

    def __getitem__(self, index):
        """Convert one student sequence into a float tensor for model consumption."""
        # 取出第 index 个学生的题号和作答序列
        questions = self.ques[index]
        answers = self.ans[index]
        # 执行 one-hot 编码转换为 2*NUM_OF_QUESTIONS 宽的特征向量
        onehot = self.onehot(questions, answers)
        # 转为 FloatTensor 以满足 RNN 输入要求
        return torch.FloatTensor(onehot.tolist())

    @staticmethod
    def onehot(questions, answers):
        """Encode correct and incorrect attempts into separate question slots."""
        # 构造全零矩阵：每行=一个时间步，列宽=2*题目数。
        # 前半段 [0, NUM_OF_QUESTIONS) 存放正确回答的 one-hot
        # 后半段 [NUM_OF_QUESTIONS, 2*NUM_OF_QUESTIONS) 存放错误回答的 one-hot
        result = np.zeros(shape=[constants.MAX_STEP, 2 * constants.NUM_OF_QUESTIONS])
        for i in range(constants.MAX_STEP):
            if answers[i] > 0:
                # 正确回答：在前半段对应题号位置置 1
                result[i][questions[i]] = 1
            elif answers[i] == 0:
                # 错误回答：在后半段对应题号位置置 1（偏移 constants.NUM_OF_QUESTIONS）
                result[i][questions[i] + constants.NUM_OF_QUESTIONS] = 1
            # answers[i] == -1 时为填充位，保持全零（模型自动忽略）
        return result
