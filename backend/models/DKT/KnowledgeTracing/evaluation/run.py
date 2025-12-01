"""直接运行 DKT 基线训练与评估循环的入口脚本。"""

import sys
# 将上级目录加入搜索路径以访问模型、数据、常量模块
sys.path.append('../')

from model.RNNModel import DKT
from data.dataloader import getTrainLoader, getTestLoader, getLoader
# 常量模块包含数据集名称、学习率、隐藏维度等所有超参数
from Constant import Constants as C
import torch.optim as optim
# eval 模块提供训练循环、测试循环和损失函数
from evaluation import eval
import torch

# 打印当前运行配置以便日志追溯
print('Dataset: ' + C.DATASET + ', Learning Rate: ' + str(C.LR) + '\n')

# 实例化 DKT 模型：输入维度=2*题数（one-hot），输出维度=题数
model = DKT(C.INPUT, C.HIDDEN, C.LAYERS, C.OUTPUT)
# Adam 优化器（备选）
optimizer_adam = optim.Adam(model.parameters(), lr=C.LR)
# Adagrad 优化器（实际使用，适合稀疏特征场景）
optimizer_adgd = optim.Adagrad(model.parameters(), lr=C.LR)

# DKT 训练沿用原实现的序列级交叉熵损失。
loss_func = eval.lossFunc()

# 根据常量中配置的数据集名称加载训练和测试数据
trainLoaders, testLoaders = getLoader(C.DATASET)

# 主训练循环：每个 epoch 先训练后评估
for epoch in range(C.EPOCH):
    # 打印当前 epoch 编号
    print('epoch: ' + str(epoch))
    # 用 Adagrad 优化器执行一轮训练
    model, optimizer = eval.train(trainLoaders, model, optimizer_adgd, loss_func)
    # 在测试集上评估并打印 AUC、F1 等指标
    eval.test(testLoaders, model)
# 保存模型（注意：当前版本未实现持久化保存逻辑）
