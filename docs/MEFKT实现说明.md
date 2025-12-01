# MEFKT 实现说明

## 定位

本项目的知识追踪（KT）服务由 `backend/ai_services/services/kt_service.py` 统一编排，当前支持：

- `DKT`
- `MEFKT`
- `fusion / single / ensemble` 三种预测模式

其中，MEFKT 负责提供“多视角习题表征 + 遗忘机制”的深度知识追踪能力，并通过课程题目级在线部署结果重新聚合回知识点掌握度。

## 关键文件

| 文件 | 作用 |
| --- | --- |
| `backend/tools/mefkt_training.py` | 训练与模型状态命令入口 |
| `backend/ai_services/services/mefkt_inference.py` | 推理与题目级在线部署 |
| `backend/ai_services/services/kt_service.py` | KT 融合、模型切换与降级逻辑 |
| `backend/platform_ai/kt/datasets.py` | 公开数据集发现与默认数据集定义 |

## 当前训练策略

### 默认训练模式

`train_mefkt_v2()` 当前固定采用：

- **公开数据预训练**
- **课程题目级在线部署**

默认公开数据集来自 `backend/platform_ai/kt/datasets.py`：

- `DEFAULT_PUBLIC_DATASET = "assist2017"`

当前支持的数据集包括：

- `assist2009`
- `assist2015`
- `assist2017`
- `kddcup2010`
- `statics2011`

### 兼容但已不主导训练的参数

为了兼容旧命令签名，以下参数仍然保留，但在当前实现中不再参与监督训练主流程：

- `course_id`
- `use_synthetic`
- `synthetic_students`

也就是说，当前 MEFKT 不是“直接拿业务课程答题日志从零训练”，而是：

1. 先在公开数据上完成预训练。
2. 再用课程题图和业务侧静态特征做在线部署推理。

## 训练产物

默认产物位于：

- `backend/models/MEFKT/mefkt_model.pt`
- `backend/models/MEFKT/mefkt_model.meta.json`

公开数据烟测或额外基线可输出到：

- `backend/models/MEFKT/public_baselines/`

元数据中会记录：

- `runtime_schema`
- `training_mode`
- `training_dataset`
- `best_metrics`
- `paper_title`
- `paper_doi`

当前运行时 schema 为：

- `question_online_v1`

## 运行时模式

### legacy

旧版模式把序列项目直接当作知识点 / item 处理，适配历史 checkpoint。

### question_online

当前项目主推的运行时模式。其核心思路是：

1. 从课程题目、资源、知识点关系和答题历史中，构建课程级题图运行时特征。
2. 先对题目节点做概率预测。
3. 再按题目与知识点映射，把题目概率聚合回知识点掌握度。

题目级运行时 bundle 会动态构造以下内容：

- `question_ids`
- `question_to_points`
- `point_to_question_indices`
- `node_feature_matrix`
- `relation_stats_matrix`
- `adjacency_matrix`
- `difficulty_vector`
- `response_time_vector`
- `exercise_type_vector`

这些特征来自：

- `Question`
- `Resource`
- `KnowledgeRelation`
- `AnswerHistory`

## 训练结构

当前训练会组合以下组件：

- `GraphContrastiveEncoder`
- `MultiAttributeEncoder`
- `LinearAlignmentFusion`
- `MEFKTSequenceModel`

训练流程可以概括为：

1. 用图结构与属性视角做预训练。
2. 生成融合后的题目嵌入。
3. 将融合嵌入喂给序列模型进行知识追踪训练。
4. 保存序列、图编码器、属性编码器与融合层状态。

## KT 服务中的接入方式

`KnowledgeTracingService` 会根据配置选择：

- `single`
- `fusion`
- `ensemble`

相关配置位于 `backend/.env`：

- `KT_PREDICTION_MODE`
- `KT_ENABLED_MODELS`
- `KT_FUSION_WEIGHTS`
- `KT_MEFKT_MODEL_PATH`
- `KT_MEFKT_META_PATH`
- `KT_USE_GPU`

当 `prediction_mode=fusion` 时，MEFKT 与 DKT 的预测结果会按权重加权融合。

## 对外接口

KT 相关 API 主要包括：

- `/api/ai/kt/predict`
- `/api/ai/kt/model-info`
- `/api/ai/kt/batch-predict`
- `/api/ai/kt/recommendations`

其中 `/api/ai/kt/model-info` 会回传运行时模式、模型可用性以及论文元数据，便于前端和运维排查。

## 命令行入口

```bash
cd backend
.venv\Scripts\python.exe tools.py train-mefkt --dataset assist2017 --epochs 16 --pretrain-epochs 8
.venv\Scripts\python.exe tools.py mefkt-status
```

## 降级行为

如果本地 MEFKT checkpoint 不可用，KT 服务不会直接报废，而是会：

1. 尝试自动加载模型。
2. 如果仍不可用，则回退到内置统计算法。
3. 在 `fusion` 模式下，只融合成功返回结果的模型。

这意味着：

- 没有 MEFKT 模型时，KT 接口仍然可用。
- 但掌握度预测的解释性与精细度会下降。

## 项目内的实际作用

当前 MEFKT 在项目中承担两个角色：

1. 为 KT 接口提供更强的深度知识追踪预测。
2. 与 DKT 一起构成 `fusion` 模式下的双模型掌握度估计。

因此，MEFKT 既是独立模型能力，也是整个学习路径、反馈报告和推荐链路的上游信号来源之一。
