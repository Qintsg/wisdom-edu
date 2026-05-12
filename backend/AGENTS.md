# backend/AGENTS.md

## 1. 适用范围

- 本文件适用于 `backend/` 目录；工作时必须同时遵守根目录 `AGENTS.md`。

---

## 2. 后端专项规则

- 技术栈：`Python + Django + DRF + LangChain + PostgreSQL + Neo4j`。
- 分层保持清晰：`models`、`serializers`、`views`、`services`、`queries/selectors`、`graph/neo4j`、`rag`、`llm`、`kt`、`agent` 各司其职。
- 禁止在 View 里堆完整 LLM / RAG / KT / Agent 流程；禁止在 Serializer 中做复杂图谱查询；禁止在 Model `save()` 中触发复杂外部推理。
- 学习建议、知识点解释、练习推荐、路径规划、掌握度判断等输出应尽量基于业务数据、图谱关系、RAG 证据、KT 状态与明确规则，不把纯 LLM 猜测当事实。

---

- ## 3. Python专项注释要求

  - 使用PEP8标准完成注释，所有函数、类均需要有文档注释，所有.py文件均需要有文件头注释，Author固定为Qintsg

  ### 3.1 Python 函数注释

  默认模板：

  ```python
  def fun_name(var1: int, var2: List[double]) -> None | str:
      """
      函数功能描述
      :param var1: 变量1描述
      :param var2: 变量2描述
      :return: 返回值描述
      """
      pass
  ```

  要求：

  - 所有参数必须写类型注释
  - 所有返回值必须写类型注释
  - `-> None` 必须显式写出
  - 注释说明目的、参数语义、返回语义，必要时说明异常

  ### 3.2 Python 文件头

  默认模板：

  ```python
  #!/user/bin/env python
  # -*- coding: UTF-8 -*-
  '''
  文件内容描述
  @Project : ${PROJECT_NAME}
  @File : ${NAME}.py
  @Author : Qintsg
  @Date : ${DATE} ${TIME}
  '''
  ```


---

## 4. 数据与智能服务边界

- `PostgreSQL` 放事务型结构化数据；`Neo4j` 放知识图谱、依赖关系、路径推理等图结构数据。
- `GraphRAG` 至少要区分 query 重写、检索、上下文构造与答案组装，不要把所有步骤塞进一个黑盒函数。
- `LLM` 层要明确 prompt 输入、模型调用、输出解析、失败降级与重试 / fallback。
- `KT` 层要明确观测输入、状态更新规则、输出掌握度 / 预测值，以及与推荐链路的耦合点。
- `Agent` 仅在固定流程无法覆盖时使用；工具集合必须最小化，输出尽量结构化，不能绕过权限、审计与业务校验。

---

## 5. 验证与结果说明

- 提交前自查：API 契约是否稳定、分页与批量查询是否合理、是否存在循环查库、PostgreSQL / Neo4j 职责是否混淆、是否需要同步更新 API文档、`docs/CHANGELOG.md` 或其他说明文档。
- 完成后端任务时，说明中必须指出：改了哪些 Model / Serializer / View / Service / Query / RAG / LLM / KT / KG / Agent 模块，是否影响 API / 数据库 / 智能服务行为，做了哪些验证，当前块 commit 与剩余风险是什么。
