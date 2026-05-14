# Changelog

## 2026-05-14

### Docs / License — 迁移到 AFL-3.0

- 项目源代码许可证从 MIT License 迁移为 Academic Free License version 3.0（AFL-3.0）。
- 根 `README.md`、`docs/README.md` 与前后端包元数据同步更新许可证声明。
- 根 `README.md` 补充非代码资产授权边界，明确课程资源、论文、演示素材、媒体文件、数据集和第三方素材不随源代码许可证自动授权。

### Backend / Tools — student1 内置快照补全

- `preset-student1-demo-snapshot` 改为完全使用脚本内置的 student1 大数据桌面快照，运行时不再读取桌面 HTML、课程资源 Excel 或外部快照文件。
- 内置 50 道初始评测题的题干、选项文本、学生答案、正确答案、正误状态、解析和知识点绑定，并保持 80 分、答对 40 / 50 题的初测结果。
- 内置 74 个知识点掌握度、学习画像总结、薄弱环节、AI 学习建议和完整反馈报告文本，避免模板兜底总结覆盖桌面展示内容。
- 学习路径改为 9 个显式节点快照，前 8 个节点完成、最后阶段测试为当前激活节点，并在课程配置中记录快照版本、题目数、掌握度数、路径节点数和完成节点数。

## 2026-05-13

### Backend / KT — MEFKT 初测题目级历史与大数据内容绑定

- 知识测评提交现在会把无知识点绑定但有题目 ID 的作答一并传入 MEFKT，并持久化为 `knowledge_point=null` 的初始答题历史，避免题目级在线模型只看到少量已绑定题。
- 知识测评结果轮询优先返回本次 `AssessmentResult` 掌握度快照，不再把异步路径/画像刷新补出的课程全量 0.40 基线混入初测报告。
- 新增 `bind_course_content` 管理命令，可按题干、资源标题和课程知识点为“大数据技术与应用”等课程补齐题目/资源/知识点绑定，并可同步补齐既有初始评测历史。
- `bind_course_content` 增加既有知识测评结果快照刷新能力，后补绑定后可重算旧 `AssessmentResult` 中的题目知识点和掌握度快照。
- 初测融合在真实 MEFKT 输出下提高单题知识点的 KT 权重，避免一题对错继续被固定压到 28% / 61% 附近。
- `bootstrap-course-assets` 导入演示课程资产时会自动写入题目/资源与知识点绑定，避免新建演示库还需要额外执行绑定修复命令。
- 学习路径生成和学习者画像刷新现在会保留初始知识测评的直接作答证据，避免异步 KT 刷新把 `KnowledgeMastery` 覆盖成 MEFKT 原始 0.5 附近的平坦分布。
- `bootstrap-course-assets` 和 `pg-bootstrap` 的课程资源导入收尾曾解析桌面的测评报告、学习画像、学习路径 HTML 及 `_files` 资源目录，为 `student1` 的“大数据技术与应用”自动补齐知识测评结果、初始答题历史、知识点掌握度、画像门禁状态和学习路径；该外部解析路径已在 2026-05-14 改为脚本内置快照。
- 新增 `preset-student1-demo-snapshot` 工具命令，可在不重新导入课程资产的情况下单独重放桌面快照预置。

### Backend / Tools — 删除答辩预置代码与命令入口

- 删除 `common/defense_demo/`、`tools/rebuild_demo/`、`tools/db_demo_preset/`、答辩阶段测试提交流程、答辩预置测试和答辩课程导入包生成工具。
- `tools.py` 不再提供 `rebuild-demo-data`、`generate-demo-course-archive`、`prepare-defense-demo` 或 `simulate-defense-demo`；普通 `create-test-data`、`pg-bootstrap`、`bootstrap-course-assets` 与 `browser-audit --scenario audit` 保留。
- 学习路径、节点完成/跳过、知识点介绍、资源推荐和阶段测试提交均移除固定答辩分支，回到基于掌握度、知识点关系、GraphRAG/RAG 和标准阶段测试的真实链路。
- 基础账号、班级、邀请码和学生默认入班关系继续由 `backend/tools/testdata.json5` 创建；`student1` 默认加入所有基础班级的行为保留。
- `大数据技术与应用` 的知识点、题库和资源统一通过 `backend/tools/自适应学习系统-课程资源` 导入，基础种子不再为该课程额外写入内联课程内容。

### Frontend — 学生设置页新增邀请码入班

- `/student/settings` 新增“加入班级”卡片，复用 `POST /api/student/classes/join`。
- 加入成功后刷新用户信息、课程列表和课程缓存，保证课程选择、我的班级和顶部课程上下文立即读取最新班级关系。
- 前端浏览器巡检入口移除答辩专用场景，保留普通 `audit`、`prepare-demo` 和 `simulate-demo` 场景。

### Frontend — 学生画像与 AI 助手页面布局修正

- `/student/profile` 的能力画像与知识掌握度首行卡片在桌面并排布局下固定等高，能力画像内部图表和洞察区收紧宽度约束，避免内容撑出卡片形成横向滚动。
- 画像总结中的学习优势与薄弱环节改为匹配总结区域的单列满宽展示。
- `/student/ai-assistant` 移除顶部命令卡片，图谱增强问答标题旁不再显示“流式输出”相关空闲状态文案。

### Frontend / Backend — 学生端 AI 流式降级兜底

- `/ws/student/ai/chat` 在已完成 GraphRAG 计划构建但模型流式无输出或生成异常时，会发送计划内 `fallback_reply` 的 `chunk` 与 `done(streamed=false)`，保留来源、命中知识点和模式元数据；只有计划构建失败才复用 HTTP 完整回答链路。
- 学生端 AI 助手页与学习节点侧边 AI 问答在 WebSocket 建连、发送或异常关闭且尚未收到有效回答时，会自动切换到 `/api/student/ai/chat` HTTP 降级，不再优先展示泛化连接失败文案。

## 2026-05-12

### Backend / Repository Hygiene — 代码目录结构收口

- 删除代码文件中批量生成的 `维护意图`、`边界说明`、`风险说明` 模板注释，保留实际业务注释和文档变更记录。
- 将大解耦后平铺的同前缀模块收口为包目录，包括 `common/defense_demo/`、`tools/api_regression/`、`tools/question_import/`、`tools/kt_synthetic/`、`tools/db_demo_preset/`、`tools/mefkt/`、`tools/exam_sets/`、`tools/rebuild_demo/` 与 `learning/stage_test/`。
- 继续按业务边界整合各后端模块：`assessments` 收口到 `api/`、`entities/`、`services/`、`defaults/`，`courses`、`exams`、`knowledge`、`learning`、`users` 按角色 API、领域服务、报告、路径、画像和认证子包拆分实现文件。
- `ai_services`、`platform_ai/rag`、`common` 与 `logs` 的横铺实现文件收口到 KT、LLM、MEFKT、Path、Student GraphRAG、Neo4j、HTTP、domain、runtime 等子包，原公共导入路径保留轻量兼容入口。
- `ai_services/tests` 按 KT、LLM、search、student 与 Student GraphRAG 夹具继续收口，纯测试夹具不再使用 `test_*.py` 文件名，减少 Django 测试发现噪声。
- 保留原有聚合入口和学生端阶段测试路由导出，避免上层 API、CLI 与测试调用方感知内部目录调整。
- 删除后端各 Django app 根目录下已废弃的 `views.py` 兼容入口和旧 support 兼容文件，URL 层改为直接引用实际 API / service 子模块。
- 将 `logs` 应用的 `0001_initial` 与 `0002_alter_operationlog_module` 合并为 squashed 初始迁移，保留 `replaces` 映射以兼容已应用旧迁移的数据库。

### Backend / KT — 学生端初始评测掌握度写回修复

- 学生端 `/api/student/assessments/initial/submit` 初始评测提交入口改用统一弱先验基线，不再按裸正确率把小样本知识点压到少数固定掌握度。
- 初始评测 KT 修正现在复用 MEFKT 来源判定：只有真实 MEFKT 输出可以写入未直接作答的已发布知识点，统计/default 回退只更新有答题证据的知识点。
- 初始评测提交在 KT 空结果或异常降级时也会统一施加前置知识点约束，避免后续路径与画像读取到前置薄弱但后置过高的掌握度。

### Backend / Demo Data — 预置数据真实 URL 与链路记录

- 测试数据与演示账号邮箱从 `example.com` 占位域切换到 `edu.qintsg.xyz`，课程种子资源补充 Hadoop、Spark、scikit-learn、D3、ECharts 与 Tableau 等真实文档入口。
- `create-test-data` 的课程资源兜底 URL 改为 `https://edu.qintsg.xyz/resources/...`，避免重新导入时继续生成 `example.com` 占位资源。
- 重新全量导入开发库并使用空学生账号完成大数据课程初始评测、学习路径推进与 GraphRAG 问答，链路记录和数据库快照保存在本地 `output/` 目录。

### Docs / Repository Hygiene — 清理旧专题文档

- 删除已不再维护的安装、部署、维护、GraphRAG、MEFKT、LangChain、大模型接入、答辩执行清单和旧 PPT 专题材料，文档目录收口到使用说明、演示数据、OpenAPI 契约、变更记录和论文材料。
- 根 `README.md`、`docs/README.md` 与 `docs/使用说明.md` 同步移除已删除文档入口，避免保留导航指向不存在的旧文件。

### Docs / API — 模块化 OpenAPI 契约重构

- 新增 `docs/openapi/` 模块化 OpenAPI 文档树，入口 `docs/openapi/openapi.yaml` 仅保留全局信息、tag、security 与 `$ref` 汇总。
- 按后端 `urls.py`、view、support、serializer 与 model 人工逐项整理认证、用户画像、课程班级、知识图谱、测评、学习路径、作业考试、AI / KT、日志和公共菜单接口，不复用旧 `docs/api.yaml` 或已删除的 Markdown API 文档作为接口来源。
- 新增 `redocly.yaml`，使用 Redocly CLI 校验模块化契约并打包生成 `docs/api.yaml`。
- `docs/README.md` 与 `docs/维护说明.md` 同步更新 API 契约源、打包产物和维护命令。

## 2026-05-11

### Backend / KT — 初始评测掌握度异常聚集修复

- 修复初始知识评测后掌握度大量集中在 25% / 30% / 50% 左右的问题，KT 统计回退统一使用初测弱先验基线，不再硬编码旧 0.25 默认值。
- 学习路径生成、手动路径刷新与学习者画像刷新现在优先保留真实 MEFKT 推断结果；只有真实 MEFKT 输出可推断未直接作答知识点，统计/default 回退只更新有答题证据的知识点。
- 新增 `repair_initial_mastery` 管理命令，用于按初测作答历史与 MEFKT 预测修复开发库中已存在的异常 `KnowledgeMastery` 数据。

### Frontend / Backend — 学生端 AI 流式问答与画像布局优化

- `/ws/student/ai/chat` 新增真实流式优先的学生端 AI 问答链路，WebSocket 现在会发送 `stage`、`chunk` 与包含 `reply / streamed / mode / sources / matched_point / query_modes / key_points` 的 `done` 事件；模型流式不可用时会回退到原完整回答再分块推送。
- `/student/ai-assistant` 与学习节点侧边 AI 问答统一接入共享流式聊天状态机，保留 GraphRAG 来源、命中知识点和 HTTP 降级能力。
- AI助手页调整为更稳定的图谱上下文 + 对话主工作区布局；学习画像页收紧 hero 与指标区，并把能力、掌握度、画像总结和 AI 建议组织为更紧凑的分析网格。
- `docs/大模型接入说明.md` 与 `docs/服务器部署说明.md` 已同步补充 WebSocket 流式协议和 ASGI 长连接排查口径。

### Backend / AI — 学习资源 MCP 切换 Tavily

- 学生端外部学习资源 MCP 从 Exa + Firecrawl 切换为 Tavily Search API，`.env` 只需填写 `TAVILY_API_KEY`。
- Tavily 未配置、请求失败或没有返回有效结果时，会保持课程内资源推荐，并继续回退到当前模型提供方的联网推荐链路。
- `backend/config.ini`、`backend/.env.example` 与大模型接入说明已同步删除 Exa / Firecrawl 配置口径。

### Docs / Repository Hygiene — 仓库整理与文档补全

- 删除旧版 `docs/API.md`，API 契约统一收口到 `docs/api.yaml`。
- `.gitignore` 补充本地代理、Playwright、Python 缓存、`.oms/`、`AGENTS.md`、`DESIGN.md`、`AGENT_TODO.md`、`requirements*.txt` 与通用 `node_modules/` 规则，防止本地产物重新进入版本库。
- 清理本地 `frontend/node_modules/` 与空目录，保留可重新生成的依赖产物和缓存不入库的维护口径。
- 根 `README.md`、`docs/README.md`、`docs/安装说明.md` 与 `docs/使用说明.md` 已同步项目元信息、资助声明、API YAML 入口、启动命令和维护边界。
- 新增 `docs/维护说明.md`、`STYLE.md` 与 MIT `LICENSE`，补齐后续维护、风格和许可说明。

## 2026-05-09

### Backend / Demo Data — 数据导入与状态检查修复

- 测试数据导入在问卷配置为空数组时会显式写入内置习惯问卷和能力评测默认题，避免 `db-check` 与首次访问接口的懒初始化状态不一致。
- `neo4j-status` 改为读取当前 Neo4j 统计契约中的 `node_count` / `relation_count`，命令行输出与学生端知识图谱接口返回保持一致。

### Backend / API Regression — 教师、学生与管理员链路修复

- 教师端作业创建规范化不再把省略的 `start_time`、`end_time`、`target_class` 写成 `null`，并补强回归脚本中的作业时间窗与班级载荷。
- 学生端 AI / RAG 回归脚本补齐 `node-intro` 所需课程与知识点上下文，并给长耗时 AI / GraphRAG 接口使用更合理的超时预算。
- 公开 API 全量回归重新接入已有临时数据清理链路，避免测试结束后留下 `[API回归]` 课程、班级、题目、作业、邀请码或用户。
- 管理员创建和导入用户时会把空 `email` / `phone` 统一落为 `NULL`，重复非空联系方式返回用户可读 `400`，避免唯一索引异常变成 `500`。
- 管理员激活码生成响应补充 `codes[].id`，使前端和回归工具能直接定位新建激活码。
- 新增回归测试覆盖默认问卷种子、Neo4j 统计字段、教师端作业创建可选字段，以及管理员用户空邮箱与重复邮箱边界。

### Backend / Student Regression — 学生端回归修复

- 学生画像测试与后端注释统一切换到 `/api/student/profile*`，旧 `/api/profile*` 路径不再被日志模块或测试用例保留为兼容入口。
- 学生端知识图谱在 Neo4j 可用但课程图谱为空时回退 PostgreSQL 图谱数据，避免空图导致页面不可用。
- 考试提交反馈中的 KT 分析会在模型结果缺少 `answer_count` 时使用本次有效答题历史数量兜底，保证报告上下文稳定展示。
- 学习路径刷新在已完成知识点重新跌破补强阈值时，会为该知识点保留补强节点配额；前置掌握度约束也会覆盖 KT 预测中出现但未发布的知识点。
- 新增回归测试覆盖旧画像路径删除、知识图谱 PostgreSQL 回退、KT `answer_count` 兜底、路径上限下补强节点重插入、未发布知识点前置约束和邀请码纯数字随机值边界。

## 2026-05-02

### Backend / Tooling — uv 环境管理

- 后端依赖从 `requirements.txt` 迁移到 `pyproject.toml` 与 `uv.lock`，由 `uv sync` 创建和更新 `backend/.venv`。
- README、安装说明、使用说明、演示说明、服务器部署说明与内置接口文档中的后端命令同步为 `uv sync` / `uv run python ...`。
- 移除仓库内旧版 `requirements.txt`，依赖版本以锁文件为准。

### Quality — 报告评分权重与高扣分模块解耦

- 拆分 MEFKT 在线运行时、学习路径节点计划、阶段测试提交、题库导入、知识图谱学生端视图与浏览器审计脚本，保留原入口兼容导出。
- 拆分考试反馈报告生成、教师端题库视图、GraphRAG Text2Cypher 降级查询与课程图社区报告构建逻辑，降低长函数和跨职责耦合。
- 补强后端函数/类级维护意图、边界和风险说明注释，提升默认评分口径下的文档覆盖质量。
- 移除仓库内本地评分配置与生成报告产物，避免将一次性质量报告继续纳入版本库维护。

### Backend / AI — LangChain Agent GraphRAG 工具拆分

- 拆分 LangChain agent 的 JSON 解析、消息提取与 GraphRAG 工具载荷构建逻辑，保留原 `agent_support` 兼容导出入口。
- 修复 `query_course_graphrag` 工具误调用旧私有 helper 名称的问题，确保 Agent 能按课程或知识点拉取 GraphRAG 证据。

### Backend / AI — KT 仅保留 MEFKT

- 移除旧版 DKT 训练、推理、CLI 命令与模型目录，KT 服务默认只启用 `mefkt`。
- 公开训练数据从 `backend/models/DKT/KTDataset/` 迁移到 `backend/models/MEFKT/public_datasets/`，MEFKT 默认训练与状态命令保持可用。
- `backend/.env.example`、`docs/API.md`、`docs/api.yaml` 与 MEFKT 说明文档同步为 MEFKT-only 配置口径。

## 2026-04-30

### Frontend / Backend — 学生端加入班级入口

- 学生端课程选择空态新增“加入班级”入口，新学生可先用教师邀请码入班，再选择班级发布课程。
- “我的班级”页放行未选课访问，并在加入或退出班级后刷新用户课程上下文。
- `POST /api/student/classes/join` 与 `GET /api/student/classes` 统一返回班级摘要和已发布课程列表，兼容无默认课程但已发布课程的班级。
- 教师端班级详情页新增邀请码管理面板，可配置有效期和使用次数、复制邀请说明、查看使用状态并删除旧邀请码。
- 学生端课程选择改为按“课程 ID + 班级 ID”识别选项，修复同一课程在多个班级中出现时会被同时选中的问题。

### Backend — 学生端推荐资源 MCP

- 学习节点推荐资源新增自研内部资源 MCP 工具，统一召回节点绑定、知识点绑定和课程内文本匹配资源。
- 外部推荐资源优先接入 Exa 语义搜索，并可用 Firecrawl 抓取正文摘要；未配置外部密钥时保留原 LLM 联网推荐兜底。
- `backend/config.ini` 与 `backend/.env.example` 新增 `RESOURCE_MCP_*`、`EXA_*`、`FIRECRAWL_*` 配置项。

## 2026-04-28

### Backend / AI — DeepSeek v4 Flash 非思考模式

- 默认 LLM 模型调整为 `deepseek-v4-flash`，并保持 `LLM_REASONING_ENABLED=false` 与 `LLM_EXTRA_BODY_JSON={"enable_thinking":false}`，确保继续使用非思考模式。

### Backend / Learning — 本地课程资源推荐兜底

- 学习节点资源推荐在节点/知识点未直接绑定资源时，会回退到同课程可见资源，并按资源标题、描述、章节与知识点上下文匹配，避免只返回外部资源或空内部资源。
- 外部学习资源推荐改为调用 DeepSeek / 当前模型提供方的原生联网搜索能力，并随请求透传 `enable_search=true`；不再先通过后端 `web_search_service` 脚本抓取候选资源。

### Backend / Demo Data — 课程资源初始评测题量对齐

- 课程资源导入完成后会把 `Course.initial_assessment_count` 同步为真实初始评测题数，避免前端仍按旧默认题数展示。
- `student1` 与答辩演示预置会优先复用课程资源导入的初始评测题，不再把演示状态固定到 3 道或 6 道兜底题。
- `COURSE_RESOURCES_DIR` 配置不可用时，批量导入会回退到代码内置课程资源目录，降低生产 `.env` 中文路径乱码导致导入出错的风险。

## 2026-04-27

### Deploy — 双域名生产部署与同源反代收口

- 后端已部署到 `47.103.44.104`，使用 `wisdom-edu.service` 运行 Daphne ASGI，后端本机 Nginx 代理到 `127.0.0.1:8000` 并托管 `/media/`、`/static/`。
- 前端已重新部署到 `106.14.209.7` 的 1Panel OpenResty 站点，`edu.qintsg.xyz` 与 `edu.qintsg.cn` 均通过同源 `/api/`、`/ws/`、`/media/`、`/static/`、`/health/` 访问后端。
- `frontend/src/api/backend.ts` 改为生产默认同源，避免 `edu.qintsg.cn` 访问时仍固定请求 `edu.qintsg.xyz`。
- `backend/wisdom_edu_api/asgi.py` 调整 Django 初始化顺序，修复 Daphne 启动时 settings/apps 尚未加载导致的失败。
- `backend/.env.example` 与 `docs/服务器部署说明.md` 已补齐 `edu.qintsg.cn`、`47.103.44.104` 和当前生产拓扑说明。

## 2026-04-24

### Backend / AI — DeepSeek v4 默认模型与非思考模式收口

- 后端默认 LLM 提供方调整为 `deepseek`，默认模型调整为 `deepseek-v4-pro`，`backend/config.ini`、`backend/.env.example` 与运行时配置读取逻辑保持一致。
- 新增 `LLM_REASONING_ENABLED`、`LLM_REASONING_EFFORT`、`LLM_EXTRA_BODY_JSON` 配置入口，默认向兼容网关透传 `enable_thinking=false`，避免 DeepSeek v4 / reasoning 类模型把推理片段混入业务 JSON。
- `LLMService` 与 `LangChainAgentService` 共享 reasoning 与 `extra_body` 配置，并在 JSON 解析前剥离 `<think>...</think>` 片段。

### Backend / Frontend — API 错误详情透传与前端提示对齐

- `common.responses` 与 DRF 全局异常处理现在会在保持 `code/msg/data` 旧契约的同时，补充 `error.type` 与 `error.details`，并将字段级错误归一化到 `data.errors`。
- 前端 Axios 客户端新增 `ApiClientError` 与 `extractApiErrorMessage()`，登录页和学生 AI 助手页会优先展示后端返回的具体错误原因。

### Frontend / Local Dev — 开发端口与后端代理可配置

- `frontend/vite.config.ts` 继续默认代理到 `http://127.0.0.1:8000`，新增 `VITE_DEV_PORT` 用于覆盖开发服务器端口，并关闭严格端口占用失败。
- `docs/API.md`、`docs/大模型接入说明.md`、`docs/安装说明.md`、`docs/服务器部署说明.md`、`docs/README.md` 与根 `README.md` 已同步更新。

## 2026-04-08

### Backend / AI — LLM 代理配置与聊天链路快失败

- `backend/wisdom_edu_api/settings.py` 与 `backend/.env.example` 新增 `HTTP_PROXY`、`HTTPS_PROXY`、`LLM_HTTP_PROXY`、`LLM_HTTPS_PROXY` 配置入口，支持将通义千问 / DeepSeek / 豆包 / 智谱 / Kimi 等兼容网关调用统一走代理。
- `LLMService` 现会基于网关协议自动解析合适的代理地址，并在初始化 `ChatOpenAI` 时通过 `openai_proxy` 透传；`LangChainAgentService` 复用同一套代理解析结果。
- `call_type="chat"` 已纳入快失败策略，聊天回退链路不再沿用 120 秒超时 + 默认重试预算，避免无课程上下文问答卡住整条请求。
- `backend/ai_services/tests.py` 新增代理透传与 `chat` 延迟预算回归测试，锁定代理优先级和快失败策略。

### Frontend / Local Dev — 开发代理默认回切 localhost

- `frontend/vite.config.ts` 的开发代理默认后端已回切为 `http://127.0.0.1:8000`，便于本地直接拉起 Django 服务进行联调与页面采样。
- 新增 `VITE_DEV_BACKEND_ORIGIN` 作为开发态可选覆盖入口；若需临时接回 `edu.qintsg.xyz:28000` 或其他远端后端，无需再次改代码。
- `README.md`、`docs/README.md` 与 `docs/服务器部署说明.md` 已同步更新为“本地优先、远端可覆盖”的最新口径。

### Frontend / Deploy — 静态部署默认同域访问并适配 edu.qintsg.xyz

- `frontend/src/api/backend.ts` 现改为生产环境默认使用与静态站点同域的 `/api`、`/media`、`/static`、`/ws`，不再默认把 `dist` 固定直连到某个 IP 或端口。
- 新增 `VITE_BACKEND_ORIGIN` 可选覆盖入口，便于在确需跨域直连其他后端时重新构建前端。
- `frontend/vite.config.ts` 现默认监听 `0.0.0.0:3000`，开发代理目标切换为 `http://edu.qintsg.xyz:28000`，并补齐 `/static` 代理与 WebSocket 代理配置。

### Backend / Deploy — frps 域名接入所需主机、跨域与代理信任配置

- `backend/wisdom_edu_api/settings.py` 新增逗号列表解析工具，并为 `ALLOWED_HOSTS`、`CORS_ALLOWED_ORIGINS`、`CSRF_TRUSTED_ORIGINS` 统一做空白清洗。
- 后端默认开启 `USE_X_FORWARDED_HOST` 与 `SECURE_PROXY_SSL_HEADER`，以适配 `edu.qintsg.xyz` 经 Nginx / frps 转发后的 HTTPS 与主机头识别。
- `backend/.env.example` 与本地 `backend/.env` 已同步补齐 `edu.qintsg.xyz`、`106.14.209.7`、`CSRF_TRUSTED_ORIGINS` 与生产跨域白名单示例，便于直接部署。

### Docs / Deploy — 106 公网入口 + frps + 同域反代部署说明更新

- `README.md`、`docs/README.md` 与 `docs/服务器部署说明.md` 已统一为“`edu.qintsg.xyz` 静态部署 + Nginx 同域反代 frps 28000 上游”的最新口径。
- 部署文档新增 `edu.qintsg.xyz` 的 Nginx 站点示例，补齐 `/api`、`/media`、`/static`、`/ws` 转发与 SPA 刷新回落配置。

## 2026-04-07

### Frontend / Backend / Docs — 用户可见“考试”文案统一为“作业”

- 教师端菜单、课程工作区、仪表盘欢迎语、课程详情统计、设置页和作业管理页的用户可见“考试”文案已统一改为“作业”，并同步调整期中/期末类型标签、发布/删除确认文案与成功失败提示。
- 学生端与教师端相关接口返回消息、AI 反馈摘要兜底文案、反馈报告默认类型，以及班级通知中的“新考试”提示均已改为“作业”口径。
- 作业成绩导出文件名已从 `exam_*.csv` 改为 `homework_*.csv`，并同步更新 `docs/使用说明.md`、`docs/答辩演示执行清单.md` 与 `docs/api.yaml` 中的用户可见描述。

### Docs / Browser Audit — 答辩标准链路切换为 teacher -> student2 -> student

- 新增 `docs/8分钟答辩演示稿.md`，基于当前真实页面与真实演示数据重写 8 分钟讲稿，不再使用 `student1` 作为正式讲解账号。
- 新增 `docs/答辩演示执行清单.md`，补齐现场启动顺序、演练命令、关键页面数据、标准点击顺序与注意事项。
- `frontend/scripts/browser-audit.mjs` 的 `prepare-defense-demo` / `simulate-defense-demo` 场景现已同步改为 `teacher -> student2 -> student`，并在报告中保留 `student2` 的“零轨迹新生入口”截图。
- `docs/README.md`、`docs/演示数据导入说明.md` 已同步更新文档索引与标准答辩口径，明确正式演示不再使用 `student1`。

### Backend / Demo / Testdata — 答辩重建链路补齐 student2~5 新生账号

- `ensure_defense_demo_accounts()` 现会同步确保 `student2~5` 存在，避免答辩重建命令只补齐 `teacher / student / student1` 后仍缺少新生演示账号。
- `ensure_defense_demo_environment()` 新增“仅入班无轨迹”收口逻辑：`student2~5` 会被统一加入答辩班级 `2024级大数据技术1班`，并清空主演示课程下的评测、画像、学习路径、作业与反馈数据。
- `tools/db_management.py` 中 `student1` 预置逻辑已按当前模型重写，现会稳定生成初始评测、能力分、画像摘要、知识掌握度、3 节点学习路径、阶段作业提交与反馈报告。
- 修复 `courses.signals.cleanup_deleted_course_artifacts()` 的信号参数名错误，避免 `rebuild-demo-data` 在清库删课阶段直接崩溃。
- `rebuild_demo_data` 输出摘要现在会显示 `student2~5` 是否已加入答辩班级，便于重建后快速核对“新生账号”是否真的可用。
- `backend/common/tests.py` 新增回归断言，锁定 `student2~5` 在主演示课程中“有班级、无轨迹”的稳定状态。

### Docs — 演示数据导入文档更新

- `docs/演示数据导入说明.md` 已同步更新答辩专用账号表、推荐演示链路和 `rebuild-demo-data` 的真实效果说明。
- `docs/README.md` 新增 `演示数据导入说明.md` 导航，便于后续快速定位演示账号与数据重建方法。

## 2026-04-06

### Frontend / Deploy — 固定后端地址并重打前端包

- 新增 `frontend/src/api/backend.ts` 作为前端生产构建的统一后端入口配置，当前固定指向 `http://127.0.0.1:8000`。
- Axios 主请求、Token 刷新、学生端 AI WebSocket、头像地址、课程资源链接与知识图谱资源链接都已统一走该固定后端入口，不再依赖生产环境同源 `/api` 反向代理。
- `README.md`、`docs/README.md`、`docs/安装说明.md`、`docs/服务器部署说明.md` 已同步改为“开发期仍可用 Vite 代理，生产包改后端地址需修改 `frontend/src/api/backend.ts` 后重新构建”的最新口径。

### Docs / Deploy — 双服务器分离部署文档

- `docs/服务器部署说明.md` 改为面向“`2核4G` 后端 + 数据库 + `1Panel`”与“`2核2G` 前端静态资源服务器”的双机部署方案，明确前端统一入口、后端 `api` 子域、WebSocket 反代和数据库端口边界。
- 文档补充了 `1Panel` 在线安装入口、后端站点反向代理建议、前端 Nginx 转发示例，以及 `backend/.env` 中与双机部署直接相关的关键配置项。
- `docs/README.md` 已同步调整文档导航，突出分服务器部署入口。

### Backend / Docs / Demo — 多提供方 LLM 配置与 Agent-GraphRAG 联动

- `LLMService`、LangChain agent、GraphRAG runtime 与 `install.py` 统一切到同一套多提供方配置入口，新增 `qwen / deepseek / doubao / zhipu / kimi / custom` 支持，并引入 `LLM_PROVIDER`、`LLM_API_FORMAT`、`LLM_REQUEST_TIMEOUT`、`LLM_MAX_RETRIES` 等统一配置项。
- `backend/config.ini` 新增 `[llm]` 与 `[graphrag]` 段，负责保存默认模型、兼容接口格式、请求超时与 GraphRAG 向量参数；`backend/.env` 继续承载敏感密钥与环境级覆盖值。
- `LangChainAgentService` 新增课程级 `query_course_graphrag` 工具，并让 `lookup_course_context` 在知识点场景附带 GraphRAG 摘要，实现“不增加前端操作复杂度”的 Agent + GraphRAG 联动。
- 演示数据预置新增 AI 助手示例提问脚本，`rebuild_demo_data` 输出会直接打印推荐问句，便于现场验证图谱关系问答、课程证据追问和课程级学习建议链路。
- `docs/大模型接入说明.md`、`docs/LangChain智能体说明.md`、`docs/GraphRAG实现说明.md`、`docs/安装说明.md` 已同步更新为新的多提供方与联动口径。

### Tooling / Install — Windows 一键安装兼容性补丁

- `install.py` 现在会在 Windows 下将 `npm`、`npx` 自动解析到真实的 `*.cmd` / `*.bat` / `*.exe` 路径，避免 `subprocess` 调用前端安装链路时触发 `FileNotFoundError`。
- 基于保留现有 `backend/.env` 的真实安装回归已重新跑通：后端依赖安装、`migrate`、`collectstatic`、`manage.py check`、`tools.py diagnose`、前端 `npm install`、Playwright Chromium 安装与 `npm run build` 均完成验证。

### Frontend / Tooling / Docs — 前端 `.env` 支持移除与后端运行配置补齐

- 前端 API、媒体资源与学生端 AI WebSocket 统一改为同源相对路径访问，本地开发完全依赖 `frontend/vite.config.ts` 代理 `/api`、`/media`、`/ws`。
- `install.py` 不再生成 `frontend/.env.local`，并补齐 `KT_DKT_META_PATH`、`COURSE_RESOURCES_DIR` 等后端真实运行配置项。
- `backend/.env` 与 `backend/.env.example` 同步补齐 GraphRAG、DKT 元数据和课程资源目录配置，并移除未接线的提供方专用 URL 示例项。
- `README.md`、`docs/README.md`、`docs/安装说明.md`、`docs/服务器部署说明.md` 全部改为“开发期靠 Vite 代理、生产期靠同域反向代理”的统一口径。

### Backend / Demo — 演示账号预置数据补齐

- `defense_demo.py` 现在会同时为 `student1` 与 `student` 补齐完整的初始评测、画像摘要、掌握度、学习路径和阶段测试相关预置，不再只有主演示账号具备完整学习闭环。
- 预热账号 `student1` 的学习路径会直接落到“已完成阶段测试、已生成反馈、已解锁后续节点”的稳定状态，可直接用于教师端或学生端演示切换。
- 演示答题历史改为可重复执行的幂等写入，重复运行演示环境补齐流程时不会继续堆积同一批 `practice / exam` 记录。
- `rebuild_demo_data` 输出新增 `assessment_results`、`answer_history`、`assessment_reports`、`exam_reports` 等摘要字段，便于重建后快速核对演示账号完整性。

## 2026-04-05

### Docs / Config — 文档体系重建与命名统一

- 重写 `docs/README.md` 与根 `README.md` 的文档导航，移除指向不存在文件的旧链接，并补齐当前真实可维护的文档入口。
- 新增 `使用说明.md`、`服务器部署说明.md`、`GraphRAG实现说明.md`、`MEFKT实现说明.md`、`LangChain智能体说明.md`、`大模型接入说明.md`，分别覆盖三端使用、ASGI 部署、GraphRAG、MEFKT、LangChain agent 与 LLM 接入。
- 重写 `docs/安装说明.md`，对齐 Python 3.12、本地 `backend/.env`、`frontend/.env.local`、`vite.config.ts` 代理和当前浏览器巡检命令。
- 统一 `backend/.env.example`、`frontend/.env.example`、`install.py` 与 Swagger 标题中的项目名称表述，并修正 `.env.example` 中的日志键名缩进问题。

### Frontend / Backend — 依赖升级与安全收敛

- 前端直接依赖升级到最新稳定版本：`vite 8.0.3`、`vue-router 5.0.4`、`typescript 6.0.2`、`vue-tsc 3.2.6`、`vue 3.5.32`、`element-plus 2.13.6`、`axios 1.14.0`、`playwright 1.59.1` 等均已落地。
- `frontend/vite.config.ts` 的 `manualChunks` 调整为函数式写法，以适配 Vite 8 / Rolldown 的类型约束；升级后前端 `npm run build` 继续通过。
- 前端新增 `overrides`，将 `lodash` 与 `lodash-es` 强制提升到 `4.18.1`，`npm audit` 已清零为 `0 vulnerabilities`。
- 后端直接依赖 `torch` 升级到 `2.11.0`，并通过 `manage.py check`、`pip check` 与 `ai_services.tests.DKTSyntheticDataRealismTests` 回归验证；其余仍显示过时的 Python 包属于上游显式约束的传递依赖，未做破坏性强升。

### Backend / Tooling — backend/.venv Python 3.12 基线对齐

- `install.py` 现在会显式解析并使用 Python `3.12` 创建 `backend/.venv`，不再直接跟随 PATH 中默认的其他 Python 版本。
- `backend/requirements.txt` 明确记录后端虚拟环境以 Python `3.12` 为基线，并补充说明 `csv` 依赖使用标准库实现，无需额外 `pip install`。
- `README.md` 与 `docs/安装说明.md` 的建虚拟环境命令已同步到 Python `3.12`，避免文档与实际环境版本漂移。

### Frontend / Backend / Tooling — IDE 检查清单收尾与 TypeScript 严格模式启用

- 清理根目录 `index.html` 导出的剩余 IDE 检查项：补齐 `common`、`DKT`、`platform_ai`、`tools`、`exams`、`logs`、`courses` 等后端文件缺失的模块/函数/内部 `Meta` docstring，并在所有条目处理完毕后删除清单文件本体。
- `frontend/tsconfig.json` 启用 `strict` 与 `forceConsistentCasingInFileNames`，移除已弃用的 `baseUrl`，并将 `paths` 映射调整为无需 `baseUrl` 的相对写法。
- 前端 API 与状态层补充了课程选择、测评流程、认证重试等关键链路的显式类型定义，`npm run typecheck` 与 `npm run build` 现已通过，确保严格模式切换后仍可正常构建。

## 2026-04-04

### Frontend / Backend / Tooling — 无点位 GraphRAG 命中优化、删课清理与一键安装

- `student_graph_rag_service.py` 新增问题文本知识点显式匹配与结构关系问题识别；学生端在**未先选知识点**时，会优先走课程级 GraphRAG 证据问答，并自动回填命中的知识点上下文。
- `student.py` 新增 `answer_course_question()`，用于在无焦点知识点时复用课程级 `query_graph + local/global/drift` 混合证据回答问题。
- 删除课程时现在会自动清理课程 GraphRAG JSON 索引、Qdrant 本地集合与 Neo4j `CourseDocument` 投影；新增 `tools.py delete-course --course-id <id> --yes` 受控清理命令。
- 学生端 AI 助手页面统一改为基于实际 `mode` 判断“图谱增强回答”，并完成 Fluent 2 基线下的全局主题、布局壳层与高频组件视觉升级。
- 新增仓库根目录 `install.py` 与 `install.bat`，支持从 0 开始交互式写入敏感配置、安装前后端依赖、迁移数据库、构建前端并生成本地环境文件。

### Backend — Neo4j GraphRAG + Qdrant 混合检索升级

- 新增 `platform_ai/rag/runtime.py`，接入 Neo4j 官方 `neo4j-graphrag-python` 与 Qdrant 本地持久化向量库。
- 新增 `StructuredCourseGraphExtractor`、`TokenHashEmbedder` 与 `SafeSentenceTransformerEmbedder`，实现课程级自定义抽取与可切换向量策略。
- `student_learning_rag` 的 Local Search 现在会优先融合向量命中，再叠加原有社区报告与 DRIFT 图扩展。
- 新增 `FacadeGraphRAGLLM`、官方 `ToolsRetriever` 与 `Text2CypherRetriever` 集成，AI 助手与知识图谱详情现在支持课程内自然语言图查询增强。
- 学生端 `graph-rag/search` 改为优先走 `neo4j_graphrag_qdrant` 混合检索模式，并透出 `supporting_sources`。
- 学生端知识图谱详情接口新增 `graph_rag_summary` 与 `graph_rag_sources`，并可在 `graph_rag_mode = neo4j_graphrag_tools` 时透出图工具增强证据。
- `neo4j_service.py` 新增 `CourseDocument` 图投影同步能力，用于把向量命中文档回接到真实 `KnowledgePoint` 图谱。

### Backend — MEFKT 知识追踪模型接入

- 新增 `MEFKT` 训练与推理链路，支持 `GCN 结构视角 + 属性视角编码 + 线性对齐融合 + 遗忘感知预测` 的工程化实现。
- `kt_service.py` 注册 `mefkt` 可选模型，`/api/ai/kt/model-info` 现可返回论文标题、DOI 与运行时模型元数据。
- 新增 `tools.py train-mefkt` 与 `tools.py mefkt-status`，支持公开数据烟测与业务运行时模型训练。
- 修复 KT 本地模型存在时仍被误判为降级不可用的问题。

### Backend — LLM / KT 配置入口收口

- 删除项目根目录 `.env`，运行配置统一收敛到 `backend/.env`。
- 删除项目根目录 `.venv`，后端运行环境统一收敛到 `backend/.venv`。
- 移除对 `OPENAI_API_KEY`、`LLM_API_KEY`、`KT_SERVICE_URL`、`KT_SERVICE_KEY` 的对外配置支持。
- `LLMService` 与 LangChain agent 默认只解析通义千问 / DeepSeek 提供方配置，并继续通过兼容聊天客户端访问已配置模型。
- 将运行时 `MEFKT` 权重与元数据迁移到 `backend/models/MEFKT/`，与训练工具和推理默认路径保持一致。

### Backend — tools 入口与菜单对齐

- `tools.py` 示例命令改为当前生效的 kebab-case 子命令写法，移除过期示例。
- `tools/cli.py` 交互式菜单补齐 `MEFKT` 训练、GraphRAG 索引、演示数据重建、答辩导入包与浏览器巡检入口。
- `tools/__init__.py` 统一导出 `browser_audit`、`generate_demo_course_archive`、`rebuild_demo_data`、`build_rag_index`、`refresh_rag_corpus` 等新版工具。

### Backend — 演示预置数据时序真实化

- `defense_demo.py` 为 `student` / `student1` 补充练习与阶段测试 `AnswerHistory`，并回填离散的 `answered_at` 时间戳。
- 演示账号现在同时具备 `initial / practice / exam` 多来源轨迹，KT 与推荐链路读取到的是更接近真实学习过程的时序数据。

### Frontend / Demo — 反馈报告与巡检稳定性修复

- `KnowledgeManageView.vue` 修复 `buildRagIndex` 被误写到样式块之后的问题，教师知识图谱页不再出现未定义渲染告警。
- `browser-audit.mjs` 现在会优先选择学生已提交的作业作为反馈报告路由，避免把未提交作业误当作反馈页入口。
- `defense_demo.py` 为预热账号 `student1` 补齐真实阶段测试提交与完成态反馈报告，浏览器巡检可直接验证 `/student/feedback/:examId` 真链路。
- 重新执行三端浏览器巡检后，学生 / 教师 / 管理员报告均无控制台错误和失败请求。

### Backend / Validation — 真实课程联调与图问答模式对齐

- `student_graph_rag_service.py` 透传 `student_learning_rag.answer_graph_question()` 返回的 `mode / query_modes / key_points`，`/api/student/ai/graph-rag/ask` 与 AI 助手接口现在可以正确暴露 `neo4j_graphrag_tools` 与 `graph_tools` 增强模式。
- `ai_services/tests.py` 新增接口级回归测试，覆盖图问答增强模式在 HTTP 响应中的保留行为。
- `platform_ai/rag/runtime.py` 改为为 Qdrant 本地点位生成稳定 UUID，并继续把课程文档真实 `external_id` 写入 payload，修复 `build-rag-index` 时 `Point id kp:* is not a valid UUID` 告警。
- 使用真实课程 `大数据技术与应用`、答辩账号 `teacher / student1 / student` 完成 API 烟测、答辩链路预检与完整浏览器模拟，最新 `output/playwright` 报告与截图已刷新到课程 `72` 的真实联调结果。

### Validation — 论文接入验证

- 执行 `manage.py test ai_services.tests.MEFKTServiceTests ai_services.tests.DKTSyntheticDataRealismTests --verbosity 2`，`5/5` 通过。
- 完成 `assist2009` 公开数据烟测训练，生成 `mefkt_assist2009_smoke.pt`。
- 完成重建后业务运行时模型训练，生成 `backend/models/MEFKT/mefkt_model.pt` 与元数据。
- 使用重建后的课程与账号，验证 `model-info / predict / recommendations / batch-predict` 四条 KT 接口链路均返回 `200`。

## 2026-03-28

### Backend — 初始评测预置数据对齐真实流程

- `defense_demo.py` 评测链路全量重写：新增 `AssessmentQuestion` 中间表关联、`AnswerHistory` 记录（`source=initial`）、贝叶斯掌握率计算、动态评测分数。
- `FeedbackReport.overview` 补全 `score` / `total_score` / `correct_count` / `total_count` / `accuracy` 数值字段，`exam` 显式设为 `None`。
- `question_details` 中 `student_answer` 与 `correct_answer` 使用原始值，与真实提交流程一致。
- `HabitPreference` 补齐全部 11 个调查字段。
- 修复题目内容字符串中中文引号导致的 `SyntaxError`。

### Backend — 演示预置数据真实化

- `defense_demo.py` 全量修订用户可见数据：课程名、班级名、资源标题/URL/描述、章节编号、学生偏好、知识评测描述、学习路径理由、节点标题与建议、作业信息、intro 文本与来源标注均改为真实教学风格内容。
- 资源 URL 从 `example.com` 占位地址改为 `/media/resources/` 本地路径。
- 移除所有"答辩演示"前缀与标识性措辞，仅保留系统标记字段（`defense_demo_preset`）用于后端逻辑识别。

### Frontend — 答辩演示体验优化

- 新增 `useAIProgress` composable（`DEMO_EMBED`），为所有 AI 调用页面提供伪造加载进度条与阶段提示文本。
- `AssessmentReportView` 集成 AI 进度条，轮询间隔从 3s 缩短至 1.5s。
- `LearningPathView` 集成 AI 进度条，新增生成中 2s 间隔自动轮询（最多 60 次）。
- 课程列表 Store 新增 15s 缓存，避免重复加载。
- 评测状态 Store 新增 15s 按课程缓存，避免重复请求。

### Docs — 演示文档同步

- 答辩演示稿更新操作描述，增加 AI 进度条、阶段提示、自动刷新等新功能说明。
- 执行清单新增"前端演示优化说明"章节，记录 `DEMO_EMBED` 标记与清理方式。

## 2026-03-27

### Changed — 2026-03-27

- 新增答辩专用 `teacher / student1 / student` 账号及固定学习链路，支持本地一键重建演示环境。
- 新增 8 分钟答辩演示稿、执行清单与课程导入样例压缩包生成命令。
- 教师端课程管理新增“导入建课”入口，支持新页面打开建课页，并在创建时直接发布到班级。
- 课程详情页题库入口改为课程工作区路由，便于现场直接编辑刚导入课程的题目。
- 新增答辩浏览器场景 `prepare-defense-demo` 与 `simulate-defense-demo`，输出教师/学生链路截图与 JSON 报告。

### Backend — 2026-03-27

- 学习路径新增答辩预置分支：学习节点、知识点介绍、资源推荐、阶段测试反馈与后续节点刷新均可按固定脚本返回。
- 阶段测试接口新增“优先使用节点显式绑定试卷”的策略，便于教师和演示环境稳定控制题目顺序。
- 教师建课接口新增 `publish_class_id` 支持，压缩包导入时会自动过滤上传 ZIP 文件本身并定位资源根目录。
- 学生知识图谱接口新增 PostgreSQL 回退路径，Neo4j 不可用时仍可完成页面展示。

## 2026-03-23

### Changed — 2026-03-23

- 学生端学习路径页改为仅展示核心统计信息，移除头部说明文案区域。
- 学习路径与首页节点预览改为未完成节点优先展示。
- 学习节点与反馈报告补充知识掌握度变化展示。
- 学生端与教师端主要作业文案统一为“作业”。
- 学习画像页收紧图表与占位高度，减少大面积空白。
- 课程编辑页新增“前往资源导入”入口，便于教师快速进入资源工作区。
- 新增学生端独立 `AI助手` 页面，支持 GraphRAG 图谱检索与图谱增强问答。

### Backend — 2026-03-23

- 知识点新增数据库级简介缓存字段，首次生成后可复用。
- 学习资源推荐统一走课程语料与图谱检索链路，减少静默降级。
- 节点完成、跳过、阶段测试通过后自动刷新学习路径。
- 反馈报告新增掌握度变化明细。
- 学生端 `ai/chat` 在课程上下文下优先走 GraphRAG，新增独立 `graph-rag/search` 与 `graph-rag/ask` 接口。
- Neo4j 知识点前置、后继、路径、详情查询补充课程隔离，减少多课程串图问题。
- 调整调试请求日志输出，成功请求改为紧凑单行格式，错误请求仅保留必要上下文与参数摘要。
- 降低控制台中的 Neo4j、LLM、KT 正常运行日志级别，减少开发环境噪音。
