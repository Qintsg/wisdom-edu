# LangChain 智能体说明

## 当前定位

本项目中的 LangChain 智能体不是一个“全能自治代理”，而是一个**轻量、受控、面向结构化输出**的编排层。

它的目标很明确：

- 在需要额外事实支撑时调用少量工具。
- 尽量产出可直接解析的 JSON。
- 与现有 `LLMService` 保持兼容，不改动业务层返回结构。

核心实现位于：

- `backend/platform_ai/llm/agent.py`

## 调用链路

业务层通常不会直接操作 LangChain agent，而是通过以下调用链进入：

1. `platform_ai.llm.llm_facade`
2. `ai_services.services.llm_service.LLMService`
3. `LangChainAgentService.invoke_json()`

也就是说，LangChain agent 是 `LLMService._call_with_fallback()` 的一条优先尝试分支，而不是独立暴露给前端的服务。

## 运行前提

只有在以下条件满足时，LangChain agent 才会真正启用：

- 已配置可用的大模型 API Key
- `langchain_openai` 等依赖可正常导入
- 兼容协议模型客户端初始化成功

如果任一条件不满足，`LLMService` 会回退到普通 LLM 调用，再不行则回退到业务层预设的 fallback JSON。

## 当前暴露给智能体的工具

当前暴露了四类最小工具，全部定义在 `agent.py` 内：

| 工具名 | 作用 |
| --- | --- |
| `lookup_course_context` | 查询课程与可选知识点上下文，并在有知识点时附带一段 GraphRAG 摘要 |
| `query_course_graphrag` | 直接调用课程级 GraphRAG 证据检索与图查询增强 |
| `search_learning_resources` | 调用外部资源搜索提供方 |
| `summarize_mastery` | 汇总学生在课程内的知识掌握度 |

设计上刻意保持克制：

- 不直接暴露任意数据库写操作
- 不允许智能体自行改变业务状态
- 只提供对结构化回答有帮助的最小事实工具集

其中新增的 `query_course_graphrag` 是这次扩展的关键：

- 课程级问题可以先拿到 GraphRAG 的课程证据、图关系与查询模式；
- 前端无需新增按钮或切换开关；
- Agent 仍然只做“结构化增强”，不直接绕开原有 GraphRAG 问答 API。

## 输出约束

LangChain agent 的系统约束是：

- 尽量只返回合法 JSON
- 仅在能提升事实支撑时使用工具
- 输出尽量贴近业务层期待的结构

`invoke_json()` 的处理流程是：

1. 构造带 `call_type` 的用户提示。
2. 强调“只输出 JSON”。
3. 调用 `agent.invoke()`。
4. 对最后一条消息做 JSON 抽取。
5. 如果失败，则回退到调用方提供的 fallback。

这也是为什么业务层通常还能拿到稳定结构，即使模型偶尔“说人话过了头”。

## 当前使用场景

LangChain agent 主要服务于以下结构化 AI 能力：

- 学习画像分析
- 学习路径规划
- 资源推荐理由
- 外部资源推荐
- 反馈报告生成
- 阶段测试题目选择

这些能力都依赖 `LLMService` 的统一入口，因此具备共同的降级和 JSON 修复策略。

## 与 GraphRAG 路由的关系

需要特别区分：

- **LangChain 智能体**：位于 `backend/platform_ai/llm/agent.py`
- **GraphRAG 图查询路由器**：位于 `backend/platform_ai/rag/runtime.py` 的 `FacadeGraphRAGLLM`

后者虽然也会做工具选择和结构化输出，但它不是 LangChain agent，而是 Neo4j GraphRAG 检索器专用的 LLM 适配层。

现在两者的关系比之前更紧一些：

- 业务侧结构化分析仍优先走 LangChain agent；
- 当问题明确落在某门课程 / 某个知识点上时，agent 可以通过 `query_course_graphrag` 先取课程证据；
- 图谱增强检索、Cypher 生成与课程级证据编排仍由 GraphRAG 运行时负责。

简单说：

- 业务侧结构化分析，优先走 LangChain agent。
- 图谱增强检索和 Cypher 生成，仍走 GraphRAG 专用门面。
- Agent 只是把 GraphRAG 作为一个可控工具接进来，而不是重写 GraphRAG 本身。

## 失败与回退策略

当前回退链路如下：

1. 尝试 LangChain agent。
2. 失败后尝试直接调用底层聊天模型。
3. 如果模型输出不是合法 JSON，继续做 JSON 修复。
4. 仍失败时，返回业务层提供的 fallback 结构。

因此，LangChain agent 在本项目中的定位不是“提高可用性的单点依赖”，而是“尽量提升结构化回答质量的一层增强”。

## 设计边界

当前实现刻意保持以下边界：

- 不做多轮长链自治任务
- 不开放高风险工具
- 不绕开业务层返回格式
- 不替代 GraphRAG 专用检索器

这意味着它更像“结构化工具调用器”，而不是一个会无限规划和执行的重型 Agent 框架。

## 当前适合演示的场景

在不增加前端操作复杂度的前提下，当前最适合现场演示的几类问题是：

- “某个知识点的前置知识是什么？”
- “围绕这个知识点，课程里有哪些证据或资源值得先看？”
- “结合当前掌握度，接下来应该先补哪个主题？”

这些问题会命中课程上下文、GraphRAG 证据或掌握度摘要工具，能够更稳定地展示“结构化 LLM + GraphRAG”联动，而不是纯自由发挥式聊天。
