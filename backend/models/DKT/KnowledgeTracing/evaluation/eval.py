"""Training and evaluation helpers for the legacy DKT implementation."""

import sys
# 添加父目录到搜索路径，使得 Constant 模块可被跨目录导入
sys.path.append('../')

import tqdm
import torch
import torch.nn as nn
from sklearn import metrics
# 常量模块提供 NUM_OF_QUESTIONS、MAX_STEP 等全局超参数
from Constant import Constants as constants


def performance(ground_truth, prediction):
    """Print common binary classification metrics for a full evaluation pass."""
    # 计算 ROC 曲线的假阳性率、真阳性率和阈值序列
    fpr, tpr, thresholds = metrics.roc_curve(
        ground_truth.detach().numpy(),
        prediction.detach().numpy()
    )
    # 通过数值积分求 AUC（ROC 曲线下面积）
    auc = metrics.auc(fpr, tpr)

    # 将概率四舍五入为 0/1 二值标签后计算 F1
    f1 = metrics.f1_score(
        ground_truth.detach().numpy(),
        torch.round(prediction).detach().numpy()
    )
    # 召回率 = TP / (TP + FN)
    recall = metrics.recall_score(
        ground_truth.detach().numpy(),
        torch.round(prediction).detach().numpy()
    )
    # 精确率 = TP / (TP + FP)
    precision = metrics.precision_score(
        ground_truth.detach().numpy(),
        torch.round(prediction).detach().numpy()
    )

    # 输出所有指标到控制台供人工检查
    print('auc:' + str(auc) + ' f1: ' + str(f1) +
          ' recall: ' + str(recall) + ' precision: ' + str(precision) + '\n')


def _extract_student_predictions(prediction_tensor, batch_tensor, student_index):
    """提取单个学生每个时间步对应的下一题预测值与真实标签。"""
    delta = (
        batch_tensor[student_index][:, 0:constants.NUM_OF_QUESTIONS]
        + batch_tensor[student_index][:, constants.NUM_OF_QUESTIONS:]
    )
    temp = prediction_tensor[student_index][: constants.MAX_STEP - 1].mm(delta[1:].t())
    diagonal_index = torch.LongTensor([[i for i in range(constants.MAX_STEP - 1)]])
    probabilities = temp.gather(0, diagonal_index)[0]
    answers = (
        (
            batch_tensor[student_index][:, 0:constants.NUM_OF_QUESTIONS]
            - batch_tensor[student_index][:, constants.NUM_OF_QUESTIONS:]
        ).sum(1)
        + 1
    ) // 2
    return probabilities, answers[1:]


class LossFunc(nn.Module):
    """Custom negative log-likelihood loss used by the original DKT paper code."""

    def __init__(self):
        """Initialize the stateless DKT loss wrapper."""
        super().__init__()

    def forward(self, pred, batch):
        """Accumulate sequence loss over the next-question predictions in a batch."""
        loss = torch.Tensor([0.0])

        # 逐学生累加有效时间步的序列损失。
        for student in range(pred.shape[0]):
            probabilities, answers = _extract_student_predictions(pred, batch, student)
            # 逐时间步累加二元交叉熵损失（仅对有效预测位 p>0）
            for index in range(len(probabilities)):
                if probabilities[index] > 0:
                    loss = loss - (
                        answers[index] * torch.log(probabilities[index])
                        + (1 - answers[index]) * torch.log(1 - probabilities[index])
                    )
        return loss


def train_epoch(model, train_loader, optimizer, loss_func):
    """Run one optimization epoch over every training batch."""
    # 使用 tqdm 显示训练进度条
    for batch in tqdm.tqdm(train_loader, desc='Training:    ', mininterval=2):
        # 前向传播：模型输出每步每题的掌握概率
        pred = model(batch)
        # 计算序列级损失
        loss = loss_func(pred, batch)
        # 梯度清零→反向传播→参数更新
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    return model, optimizer


def test_epoch(model, test_loader):
    """Collect predictions and labels for every valid timestep in one loader."""
    gold_epoch = torch.Tensor([])
    pred_epoch = torch.Tensor([])

    # 按批次扫描测试集并展示进度条。
    for batch in tqdm.tqdm(test_loader, desc='Testing:    ', mininterval=2):
        # 前向传播获取预测概率矩阵
        pred = model(batch)
        # 逐学生提取有效预测
        for student in range(pred.shape[0]):
            temp_pred = torch.Tensor([])
            temp_gold = torch.Tensor([])
            probabilities, answers = _extract_student_predictions(pred, batch, student)
            # 只收集有效预测位（p>0 表示该时间步存在实际交互）
            for index in range(len(probabilities)):
                if probabilities[index] > 0:
                    temp_pred = torch.cat([temp_pred, probabilities[index:index + 1]])
                    temp_gold = torch.cat([temp_gold, answers[index:index + 1]])
            # 将当前学生的结果追加到 epoch 级汇总张量
            pred_epoch = torch.cat([pred_epoch, temp_pred])
            gold_epoch = torch.cat([gold_epoch, temp_gold])
    return pred_epoch, gold_epoch


def train(train_loaders, model, optimizer, loss_func):
    """Iterate through all configured training loaders in sequence."""
    # 依次遍历所有训练加载器（通常只有一个；多数据集时可扩展）
    for i in range(len(train_loaders)):
        model, optimizer = train_epoch(model, train_loaders[i], optimizer, loss_func)
    return model, optimizer


def test(test_loaders, model):
    """Aggregate predictions across all test loaders and print summary metrics."""
    # 累积所有测试加载器的预测和真实标签
    ground_truth = torch.Tensor([])
    prediction = torch.Tensor([])
    # 逐个测试加载器聚合预测结果
    for i in range(len(test_loaders)):
        pred_epoch, gold_epoch = test_epoch(model, test_loaders[i])
        # 合并当前加载器结果到全局张量
        prediction = torch.cat([prediction, pred_epoch])
        ground_truth = torch.cat([ground_truth, gold_epoch])
    # 统一打印最终评估指标
    performance(ground_truth, prediction)


LEGACY_EXPORTS = {
    'lossFunc': LossFunc,
}


def __getattr__(name):
    """Expose the legacy camelCase loss class for untouched training scripts."""
    try:
        return LEGACY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}') from exc
