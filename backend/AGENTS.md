# backend/AGENTS.md

## 1. 适用范围

- 本文件适用于 `backend/` 目录；工作时必须同时遵守根目录 `AGENTS.md`。
- 权限只看根目录中的 `AI_PERMISSION_LEVEL: DANGEROUS`。

---

## 2. 后端专项规则

- 技术栈：`Python + Django + DRF + LangChain + PostgreSQL + Neo4j`。
- 分层保持清晰：`models`、`serializers`、`views`、`services`、`queries/selectors`、`graph/neo4j`、`rag`、`llm`、`kt`、`agent` 各司其职。
- 禁止在 View 里堆完整 LLM / RAG / KT / Agent 流程；禁止在 Serializer 中做复杂图谱查询；禁止在 Model `save()` 中触发复杂外部推理。
- 学习建议、知识点解释、练习推荐、路径规划、掌握度判断等输出应尽量基于业务数据、图谱关系、RAG 证据、KT 状态与明确规则，不把纯 LLM 猜测当事实。

---

## 3. Python 与实现规范

- 优先遵循 `PEP 8`、Django / DRF 官方实践与仓库既有约定。
- 所有函数参数与返回值都应显式标注类型；非必要禁止 `Any`、过宽泛的 `object` 与无语义命名。
- Python 文件头与函数注释沿用仓库当前模板；注释除遵守根目录注释率要求外，还要写清目的、参数语义、返回语义与必要异常。
- 默认不保留 `pass`、空 service / chain / agent、假召回、假推理或未接线逻辑；确需保留时只能使用 `TODO:` / `FIXME:` 并说明原因与影响。

---

## 4. 数据与智能服务边界

- `PostgreSQL` 放事务型结构化数据；`Neo4j` 放知识图谱、依赖关系、路径推理等图结构数据。
- `GraphRAG` 至少要区分 query 重写、检索、上下文构造与答案组装，不要把所有步骤塞进一个黑盒函数。
- `LLM` 层要明确 prompt 输入、模型调用、输出解析、失败降级与重试 / fallback。
- `KT` 层要明确观测输入、状态更新规则、输出掌握度 / 预测值，以及与推荐链路的耦合点。
- `Agent` 仅在固定流程无法覆盖时使用；工具集合必须最小化，输出尽量结构化，不能绕过权限、审计与业务校验。

---

## 5. 验证与结果说明

- 提交前自查：API 契约是否稳定、分页与批量查询是否合理、是否存在循环查库、PostgreSQL / Neo4j 职责是否混淆、是否需要同步更新 `docs/API.md`、`docs/CHANGELOG.md` 或其他说明文档。
- 完成后端任务时，说明中必须指出：改了哪些 Model / Serializer / View / Service / Query / RAG / LLM / KT / KG / Agent 模块，是否影响 API / 数据库 / 智能服务行为，做了哪些验证，当前块 commit 与剩余风险是什么。
