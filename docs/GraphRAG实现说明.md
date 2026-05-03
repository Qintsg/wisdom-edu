# GraphRAG 实现说明

## 设计目标

本项目的 GraphRAG 不是“单一向量检索器”，而是一个由三层组成的课程级混合检索体系：

1. **原生课程 GraphRAG JSON 索引**：把知识点、资源、题目、章节、社区报告统一抽取到课程级索引中。
2. **Qdrant 本地向量库**：把课程文档嵌入后写入本地持久化向量集合。
3. **Neo4j 图投影 + 官方 Retriever**：将课程文档以 `CourseDocument` 形式回接到知识点图谱，支持 `ToolsRetriever` 与 `Text2CypherRetriever` 做结构化图查询。

因此，当前实现既保留了仓库原有的 `local / global / drift` 检索方式，也接入了 Neo4j 官方 GraphRAG 检索器。它更像“课程知识图谱 + 向量检索 + 图查询增强”的组合，而不是单点替换。

## 核心文件

| 文件 | 作用 |
| --- | --- |
| `backend/platform_ai/rag/corpus.py` | 构建课程原生 GraphRAG JSON 索引 |
| `backend/platform_ai/rag/runtime.py` | Qdrant 物化、Neo4j 投影、官方 Retriever 接入 |
| `backend/platform_ai/rag/student.py` | 学生端 Local / Global / DRIFT 组合与问答编排 |
| `backend/tools/rag_index.py` | GraphRAG 索引构建命令入口 |
| `backend/common/neo4j_service.py` | `CourseDocument` 投影写入与图查询支撑 |
| `backend/ai_services/urls.py` | GraphRAG 对外接口挂载位置 |

## 离线索引构建

### 原生课程索引内容

`build_course_graph_index(course_id)` 会从课程数据中生成一个 JSON 载荷，主要包含：

- `entities`
  - `knowledge_point`
  - `resource`
  - `question`
  - `chapter`
- `relationships`
  - 知识点前置关系
  - 知识点与资源 / 题目的支撑关系
  - 章节包含关系
- `communities`
  - 基于 `networkx` 社区发现生成的实体簇
- `community_reports`
  - 面向 Global Search 的高层摘要
- `documents`
  - 用于检索的统一文档单元

索引会持久化到：

- `backend/runtime_logs/rag/course_{course_id}.json`

### 文档单元来源

文档单元不是只来自资源文本，而是混合来源：

- 知识点介绍与描述
- 课程资源摘要
- 题目与解析摘要（题目文档会标记 `answer_hidden=True`）
- 章节汇总
- 社区报告摘要

这意味着 GraphRAG 的召回对象既可以是课程资源，也可以是知识点、题目或社区报告。

## 向量库与 Neo4j 投影

### Qdrant 物化

`CourseGraphRAGRuntime.materialize_course_payload()` 会把 `documents` 转成向量点并写入本地 Qdrant：

- Qdrant 目录：`backend/runtime_logs/rag/qdrant`
- 集合命名：`course_{course_id}_documents_v2`

默认嵌入器由 `backend/config.ini` + `backend/.env` 共同控制：

- `GRAPHRAG_EMBEDDER_PROVIDER=hash`：离线哈希向量器，适合本地开发、测试和演示
- `GRAPHRAG_EMBEDDER_PROVIDER=sentence_transformer`：本地句向量模型
- `GRAPHRAG_SENTENCE_MODEL`：句向量模型名
- `GRAPHRAG_VECTOR_DIMENSION`：向量维度

对应的 `config.ini` 段为：

```ini
[graphrag]
embedder_provider = hash
sentence_model = sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
vector_dimension = 256
qdrant_path = runtime_logs/rag/qdrant
```

如果 `.env` 中也配置了同名变量，则环境变量优先。

### Neo4j 投影

同一次物化过程还会把课程文档写入 Neo4j：

- 节点标签：`CourseDocument`
- 关系：`(CourseDocument)-[:ABOUT]->(KnowledgePoint)`

这样做的目的，是让向量命中的课程文档重新回到真实知识图谱里，继续做前置知识、后续知识和路径类查询，而不是停留在“只返回一段文本”。

## 查询链路

### 1. Local Search

`StudentLearningRAG._build_local_context()` 会组合以下信息：

- Qdrant / Neo4j 混合命中的证据文档
- 相关实体排序结果
- 一跳邻居关系
- 局部社区报告
- 局部证据文档

返回内容用于回答“这个知识点是什么”“有哪些资源”“有哪些题目”等局部问题。

### 2. Global Search

`_build_global_context()` 直接基于 `community_reports` 做高层主题摘要，更适合：

- 某章主要讲什么
- 当前课程有哪些主题块
- 某个问题在课程全局里处于什么位置

### 3. DRIFT Search

`_build_drift_context()` 会从 Local Search 命中的实体继续扩展到关联社区，再回收一批扩展实体和文档，适合：

- 从一个知识点向周边知识扩展
- 从一个问题跳到相关资源和相关题目

### 4. 图查询增强

`student_graphrag_runtime.query_graph()` 通过官方 `ToolsRetriever` 组合两个工具：

- `semantic_course_search`
- `graph_structure_query`

其中 `graph_structure_query` 底层使用 `Text2CypherRetriever`，并配合自定义 prompt 强制：

- 只查当前课程
- 只使用 `KnowledgePoint` 与 `CourseDocument`
- 只使用 `PREREQUISITE`、`ABOUT` 两类关系
- 固定返回结构化字段

它更适合回答：

- 这个知识点的前置知识是什么
- 学完这个知识点后该继续学什么
- 这个知识点有哪些课程证据

## 对外接口

当前与 GraphRAG 直接相关的入口主要有：

- `/api/student/ai/chat`
- `/api/student/ai/graph-rag/search`
- `/api/student/ai/graph-rag/ask`

同时，知识点详情与学习路径规划也会通过 `StudentLearningRAG` 间接复用 GraphRAG 上下文。

## 与 LangChain agent 的联动

本轮调整后，GraphRAG 不再只是学生端独立问答链路的一部分，也成为 LangChain agent 可调用的事实工具之一：

- `agent.py` 中的 `query_course_graphrag` 工具会直接调用 `student_graphrag_runtime.query_graph()`；
- `lookup_course_context` 在传入 `point_id` 时，会额外附带该知识点的 GraphRAG 摘要；
- Agent 因此可以在“路径规划、画像分析、资源推荐理由”等结构化场景中先拉取课程证据，再输出 JSON。

这样做的边界仍然很明确：

- GraphRAG 负责检索、图查询和证据组装；
- Agent 负责工具编排与结构化回答；
- 前端不需要新增“启用 agent / 启用 GraphRAG”的复杂配置。

## 回退策略

当前实现非常强调“能回答就尽量回答”，因此做了多层降级：

| 场景 | 回退行为 |
| --- | --- |
| 没有句向量模型或模型初始化失败 | 自动回退到哈希向量器 |
| Neo4j 不可用 | 文档检索回退为 Qdrant-only，图查询增强回退为语义证据模式 |
| LLM 不可用 | `FacadeGraphRAGLLM` 使用启发式工具选择或启发式 Cypher |
| 当前课程没有现成索引 | 自动重建 `course_{course_id}.json` 并重新物化 |

所以 GraphRAG 在本项目里并不是“全有或全无”，而是按能力逐级退化。

## 常用命令

```bash
cd backend
uv run python tools.py build-rag-index --course-id 72
uv run python tools.py refresh-rag-corpus --course-id 72
```

省略 `--course-id` 时会对全部课程构建索引。

## 配置项

`backend/.env` / `backend/.env.example` 中与 GraphRAG 直接相关的配置包括：

- `NEO4J_BOLT_URL`
- `NEO4J_USERNAME`
- `NEO4J_PASSWORD`
- `GRAPHRAG_EMBEDDER_PROVIDER`
- `GRAPHRAG_SENTENCE_MODEL`
- `GRAPHRAG_VECTOR_DIMENSION`
- `GRAPHRAG_QDRANT_PATH`

同时，`backend/config.ini` 中的 `[graphrag]` 段会提供默认值，便于在不泄露敏感信息的前提下把 GraphRAG 的运行参数纳入版本管理。

## 项目内的实际定位

当前 GraphRAG 实现承担三类职责：

1. 为学生 AI 助手提供课程内证据。
2. 为知识图谱详情提供“图谱增强解释”。
3. 为学习路径规划、课程问答等场景提供可追溯上下文。

因此它不是独立子系统，而是学生学习体验与课程图谱能力之间的共享中枢。
