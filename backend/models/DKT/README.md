# DKT 模型目录说明

本目录存放自适应学习系统中知识追踪（DKT）相关模型文件。

## 目录结构

```text
models/DKT/
├── KnowledgeTracing/          # 第三方 DKT 参考实现
├── training_data/             # 训练数据导出目录
└── dkt_model.pt               # 训练后的模型权重（运行后生成）
```

## 与项目的关系

- 训练入口：`backend/tools/dkt_training.py`
- 推理入口：`backend/ai_services/services/dkt_inference.py`
- 统一命令：`python tools.py dkt-status | train-dkt | export-training-data`

## 快速使用

在 `backend/` 目录执行：

```bash
python tools.py dkt-status
python tools.py train-dkt --synthetic --epochs 100
python tools.py export-training-data
```

## 注意事项

1. 首次部署若答题数据不足，建议先使用 `--synthetic` 训练。
2. 若不存在 `dkt_model.pt`，系统会触发降级预测逻辑。
3. 训练前请确保数据库中已有知识点数据（用于确定题目维度）。
