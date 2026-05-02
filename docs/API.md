# API 变更记录

## 2026-05-02

### 知识追踪（KT）

- `GET /api/ai/kt/model-info`
  - `models` 现在只暴露 `mefkt`，不再返回旧版 `dkt` 模型配置和运行时状态。
  - `enabled_models` 默认值调整为 `["mefkt"]`，`fusion_weights` 默认值调整为 `{"mefkt": 1.0}`。

- `POST /api/ai/kt/predict`
  - KT 服务只调用 MEFKT 运行时；本地 MEFKT 模型不可用时继续回退到内置统计算法。
  - 旧环境变量中的 `dkt` 会被过滤，不再触发 DKT 模型加载或推理。

## 2026-04-30

### 学生端班级

- `GET /api/student/classes`
  - 学生端“我的班级”页直接使用该接口获取已加入班级，不再依赖 `GET /api/auth/userinfo` 的 `classes` 字段。
  - 返回的每个班级项包含 `class_id`、`class_name`、`teacher_name`、`teacher_username`、`student_count`、`courses`、`course_id`、`course_name` 与 `enrolled_at`。
  - `courses` 会合并班级默认课程与已发布课程，兼容没有默认课程但通过 `ClassCourse` 发布课程的班级。

- `POST /api/student/classes/join`
  - 输入：`code`，即教师端生成的邀请码；前端会自动 trim 并转为大写后提交。
  - 成功后返回与班级列表一致的班级摘要，便于学生端立即刷新班级列表和课程选择状态。
  - 若班级已停用、邀请码不存在、邀请码过期或学生已在班级中，继续返回统一错误响应。

### 教师端班级邀请

- `POST /api/teacher/invitations/generate`
  - 输入继续包含 `class_id`，并支持 `max_uses` 与 `expires_days` 配置；`max_uses=0` 表示不限次数，`expires_days` 范围为 `1..365`。
  - 后端会校验配置格式并返回 `use_count`、`is_active`、`is_valid`、`created_at`，便于教师端展示邀请码状态。

- `GET /api/teacher/classes/{class_id}/invitations`
  - 邀请码列表按 `created_at` 倒序返回，教师端用于展示可用状态、使用次数、到期时间与删除操作。

### 学生端推荐资源 MCP

- `GET /api/student/path-nodes/{node_id}/ai-resources`
  - 内部资源召回改为通过自研项目内资源 MCP 工具统一检索节点绑定资源、知识点绑定资源和课程内文本匹配资源。
  - 外部资源优先使用 Exa 语义搜索召回，并在配置 Firecrawl 后抓取页面正文摘要作为 `description` 和推荐依据。
  - 外部资源项可能新增 `provider`、`source` 字段；`provider=exa_firecrawl` 表示已完成 Exa 搜索和 Firecrawl 摘要增强，未配置外部密钥时继续回退到原 LLM 联网推荐链路。

## 2026-04-24

### 统一错误响应

- 所有通过 `common.responses.error_response()` 返回的业务错误继续保持 `code`、`msg`、`data` 三段式结构。
- 当 HTTP 状态码或业务 `code` 表示错误时，响应会额外包含：
  - `error.type`：稳定错误类型，默认形如 `HTTP_400`，DRF 异常会使用异常类名。
  - `error.details`：字段级或结构化错误详情。
- DRF 全局异常处理会把序列化校验错误归一化到 `data.errors`，前端可直接从 `msg` 展示首条用户可读错误，也可读取 `error.details` 做字段定位。

示例：

```json
{
  "code": 400,
  "msg": "username: 该字段不能为空。",
  "data": {
    "errors": {
      "username": ["该字段不能为空。"]
    }
  },
  "error": {
    "type": "ValidationError",
    "details": {
      "username": ["该字段不能为空。"]
    }
  }
}
```

## 2026-04-04

### GraphRAG / 知识图谱

- `GET /api/student/knowledge-points/{point_id}`
  - 新增 `graph_rag_summary`、`graph_rag_sources`、`graph_rag_mode` 字段。
  - 知识图谱详情页现在可直接复用课程级 GraphRAG 证据摘要，而不必重复调用 AI 助手接口。
  - `graph_rag_mode` 现在可能返回 `neo4j_graphrag_tools`，表示该知识点详情额外命中了官方 `ToolsRetriever + Text2CypherRetriever` 图查询增强链路。

- `POST /api/student/ai/graph-rag/search`
  - `retrieval_mode` 现在可能返回 `neo4j_graphrag_qdrant`，表示命中了 Neo4j GraphRAG Python + Qdrant 混合检索链路。
  - `matched_points[]` 可能附带 `graph_rag_score` 与 `supporting_sources`，便于前端展示命中依据。

- `POST /api/student/ai/chat`
  - 课程上下文命中知识点后，`mode` 现在可能返回 `neo4j_graphrag_tools`。
  - `query_modes` 现在可能附加 `graph_tools`，表示该回答额外融合了官方图工具查询结果。

- `POST /api/student/ai/graph-rag/ask`
  - `mode` 现在可能返回 `neo4j_graphrag_tools`。
  - `query_modes` 现在可能附加 `graph_tools`，表示该回答使用了官方 `ToolsRetriever + Text2CypherRetriever` 做结构化图查询补充。

### 知识追踪（KT）

- `GET /api/ai/kt/model-info`
  - `models.mefkt` 新增论文元信息：`paper_title`、`paper_doi`。
  - `models.*.runtime_info` 新增运行时状态摘要，便于前端识别本地模型是否已加载。
  - 当仓库默认路径存在本地模型文件时，`is_available` 现在会正确返回 `true`，不再误报为降级模式。

- `POST /api/ai/kt/predict`
  - 在启用 `MEFKT` 时，`model_type` 可能返回 `mefkt_real`（成功命中运行时模型）或 `mefkt`（回退到统计推断）。
  - 返回继续包含 `prediction_mode`、`answer_count`、`knowledge_point_count`，用于前端展示模型运行上下文。

- `POST /api/ai/kt/batch-predict`
  - 教师端批量预测链路现可复用 `MEFKT` 运行时模型，支持对多个学生历史轨迹做统一知识点掌握度输出。

- `POST /api/ai/kt/recommendations`
  - 保持原接口契约不变，但可直接消费 `MEFKT` 输出的掌握度结果生成学习建议。

## 2026-03-27

### 教师端课程

- `POST /api/teacher/courses/create`
  - 新增 `publish_class_id` 入参，支持教师在导入建课时直接发布到指定班级。
  - 上传课程压缩包时，后端会优先定位压缩包中的真实资源根目录，不再把原始 ZIP 文件本身误判为导入目录内容。
  - 返回新增 `published_class_id` 字段，便于前端确认本次创建是否已同步发布到班级。

### 学习路径与答辩预置

- `GET /api/student/learning-path`
  - 对答辩预置账号新增固定可见节点策略：阶段测试通过前仅返回当前演示所需的前置节点，通过后再返回后续预置节点。

- `GET /api/student/path-nodes/{node_id}`
  - 返回新增 `knowledge_point_id`，便于学习节点页在无路由查询参数时也能稳定定位知识点介绍。

- `GET /api/student/path-nodes/{node_id}/ai-resources`
  - 答辩预置账号命中固定资源时，`service_status` 将返回 `preset`。

- `POST /api/student/ai/node-intro`
  - 答辩预置账号会优先返回课程配置中的固定知识点介绍，不再依赖现场 LLM 输出。

- `GET /api/student/path-nodes/{node_id}/stage-test`
  - 当节点已显式绑定试卷时，优先按节点试卷顺序返回阶段测试题目。

### 知识图谱

- `GET /api/student/knowledge-map`
  - Neo4j 不可用或图数据为空时，接口会自动回退到 PostgreSQL 图谱数据，并在 `stats.data_source` 中标记为 `postgresql`。

- `GET /api/student/knowledge-points/{point_id}`
  - Neo4j 不可用时，前置知识与后续知识关系将回退到 PostgreSQL 关系数据。

## 2026-03-23

### 学习路径

- `GET /api/student/learning-path`
  - 不再依赖 `ai_reason` 作为学生端头部展示文案。
  - 返回的 `nodes` 改为未完成节点优先，仍保留原始 `order_index` 字段。

- `POST /api/student/path-nodes/{node_id}/complete`
  - 新增 `path_refreshed` 字段，表示节点完成后已自动触发路径刷新。

- `POST /api/student/path-nodes/{node_id}/skip`
  - 新增 `path_refreshed` 字段，表示节点跳过后已自动触发路径刷新。

- `GET /api/student/path-nodes/{node_id}`
  - `mastery_before` 缺失时改为回填当前知识点掌握度，不再默认展示为 `0`。

### AI 学习能力

- `POST /api/student/ai/node-intro`
  - 新增支持 `course_id` 与 `point_id`，用于多课程场景下精确定位知识点。
  - 知识点简介优先读取数据库缓存，缺失时才生成并写回。

- `GET /api/student/path-nodes/{node_id}/ai-resources`
  - 资源推荐统一走课程语料 + 图谱检索链路。
  - 新增 `service_status` 字段。

- `POST /api/student/ai/chat`
  - 当传入 `course_id` 时，优先走 GraphRAG 课程问答。
  - 若同时传入 `point_id`，会围绕该知识点进行图谱增强回答。
  - 返回新增 `mode`、`matched_point`、`related_points`、`sources`。

- `POST /api/student/ai/graph-rag/search`
  - 输入：`course_id`、`query`、`limit`
  - 输出：`matched_points`、`retrieval_mode`
  - 用于独立 AI助手页面的知识图谱检索。

- `POST /api/student/ai/graph-rag/ask`
  - 输入：`course_id`、`question`、可选 `point_id`
  - 输出：`reply`、`sources`、`mode`、`matched_point`、`related_points`
  - 用于独立 AI助手页面的 GraphRAG 问答。

### 作业反馈

- `POST /api/student/exams/{exam_id}/submit`
  - 新增 `mastery_changes` 字段，返回本次提交导致的知识掌握度变化。

- `GET /api/student/feedback/{exam_id}`
  - 新增 `mastery_changes` 字段，供前端报告页展示掌握度变化。

- `POST /api/student/path-nodes/{node_id}/stage-test/submit`
  - 新增 `mastery_changes` 字段。
  - 新增 `path_refreshed` 字段，测试通过后会自动刷新学习路径。
