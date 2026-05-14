# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

本仓库是“知识图谱驱动的个性化自适应学习系统”，包含学生、教师、管理员三端 Web 应用。前端位于 `frontend/`，使用 Vue 3、Vite、TypeScript、Pinia、Vue Router、Element Plus，并按 Fluent 2 风格维护界面；后端位于 `backend/`，使用 Python 3.12、Django、Django REST Framework、Channels、PostgreSQL、Neo4j、GraphRAG、MEFKT、LangChain 和兼容 OpenAI 的 LLM 客户端。

优先阅读并遵守 `AGENTS.md`；进入 `backend/` 或 `frontend/` 工作时，还要遵守对应子目录下的 `AGENTS.md`。`STYLE.md` 汇总代码、文档、API 契约和界面维护风格。

## 常用命令

### 后端环境与开发

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py runserver 127.0.0.1:8000
```

严格复现锁文件：

```bash
cd backend
uv sync --frozen
```

后端配置来自 `backend/.env` 与可选 `backend/config.ini`；首次运行基于 `backend/.env.example` 创建本地配置。默认开发服务地址为 `http://127.0.0.1:8000`。

### 后端验证与回归

```bash
cd backend
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python tools.py db-check
uv run python tools.py django-check
uv run python tools.py api-smoke
uv run python tools.py student-flow-smoke
uv run python tools.py api-regression --all --json
```

可按范围运行专项命令：

```bash
cd backend
uv run python tools.py test-business-logic
uv run python tools.py test-kt-service
uv run python tools.py test-llm-service
uv run python tools.py diagnose
```

当前仓库未配置独立 pytest/Vitest 测试脚本；后端回归主要通过 Django checks 与 `backend/tools.py` 子命令执行。查看全部可用工具命令：

```bash
cd backend
uv run python tools.py --help
```

### 数据、图谱、RAG 与 MEFKT 工具

```bash
cd backend
uv run python tools.py create-test-data
uv run python tools.py bootstrap-course-assets --course-name "大数据技术与应用"
uv run python tools.py preset-student1-demo-snapshot
uv run python tools.py neo4j-status
uv run python tools.py neo4j-sync-all
uv run python tools.py build-rag-index
uv run python tools.py refresh-rag-corpus
uv run python tools.py mefkt-status
uv run python tools.py train-mefkt --course-id <course_id>
```

浏览器巡检需要前后端服务都已启动：

```bash
cd backend
uv run python tools.py browser-audit --scenario audit --frontend-url http://127.0.0.1:3000 --api-base-url http://127.0.0.1:8000
```

### 前端环境与开发

```bash
cd frontend
npm install
npm run dev
```

默认开发地址为 `http://127.0.0.1:3000`。`frontend/vite.config.ts` 在开发环境把 `/api`、`/media`、`/static`、`/ws` 代理到 `127.0.0.1:8000`；可用 `VITE_DEV_BACKEND_ORIGIN` 临时切换后端，用 `VITE_DEV_PORT` 切换前端端口。

### 前端验证与构建

```bash
cd frontend
npm run typecheck
npm run build
npm run preview
npm run browser:audit
```

`npm run build` 会先执行 `vue-tsc --noEmit`，再执行 Vite 构建。生产包如需直连其他后端入口，设置 `VITE_BACKEND_ORIGIN` 后重新构建。

### OpenAPI 契约

API 契约源是 `docs/openapi/openapi.yaml` 和其引用的模块化文件，`docs/api.yaml` 是 Redocly CLI 打包产物。接口变化后先更新 `docs/openapi/`，再执行：

```bash
npx @redocly/cli lint wisdomedu@v1
npx @redocly/cli bundle wisdomedu@v1
```

运行态接口文档：

- Swagger：`http://127.0.0.1:8000/api/docs/`
- ReDoc：`http://127.0.0.1:8000/api/redoc/`
- OpenAPI Schema：`http://127.0.0.1:8000/api/schema/`

## 高层架构

### 后端结构

- `backend/wisdom_edu_api/` 是 Django 项目入口，`settings.py` 组装 Django、DRF、JWT、Channels、日志和本地 app，`urls.py` 汇总模块 API，`asgi.py` 同时接入 HTTP 与 WebSocket。
- 业务 app 按领域拆分：`users` 负责认证、权限与用户画像；`courses` 负责课程、班级、选课；`knowledge` 负责知识点、关系、资源与图谱；`assessments` 负责测评与能力评分；`learning` 负责学习路径、节点和进度；`exams` 负责作业考试与反馈报告；`ai_services` 负责 AI 能力入口与调用日志；`logs` 负责操作日志；`common` 放共享权限、工具和响应处理。
- `backend/platform_ai/` 是智能能力边界，集中维护 `rag`、`llm`、`kt`、`search`、`mcp` 等能力。不要把完整 LLM、RAG、KT、KG 或 Agent 流程堆在 View、Serializer 或 Model `save()` 中。
- `backend/tools.py` 是项目 CLI 入口，实际命令拆分在 `backend/tools/`。数据导入、课程资产初始化、Neo4j 同步、RAG 索引、MEFKT 训练、API 回归和浏览器巡检优先复用这里的子命令。
- PostgreSQL 保存用户、课程、题目、学习记录、评测、任务、权限和日志等事务数据；Neo4j 保存知识点、概念、依赖、先修和路径推理等图结构数据。学习建议、推荐、路径规划和掌握度解释应尽量可追溯到业务数据、图谱、RAG 证据、KT 状态或明确规则。

### 前端结构

- `frontend/src/main.ts` 挂载 Vue 应用；`frontend/src/router/` 按 auth、student、teacher、admin 模块拆分路由，并在 `guards.ts` 维护路由守卫。
- `frontend/src/layouts/` 提供认证、默认和空布局；`frontend/src/views/` 按角色和业务页面分组；`frontend/src/components/` 放共享展示组件和知识图谱组件；`frontend/src/stores/` 放 Pinia 状态；`frontend/src/composables/` 放可复用组合逻辑。
- `frontend/src/api/index.ts` 是 Axios 统一入口，负责 API envelope 解包、错误提示、JWT 附加、token refresh 与重放请求；`frontend/src/api/backend.ts` 负责后端 HTTP/WebSocket 地址拼接；角色相关接口位于 `frontend/src/api/student/`、`frontend/src/api/teacher/`、`frontend/src/api/admin/`。
- 用户可见 UI 保持 Fluent 2 风格。复杂状态映射、API 适配、图谱处理和业务编排应下沉到 composable、store、utils 或专门模块，不要堆在页面模板中。

### 文档与契约

- `README.md` 是项目入口说明，`docs/README.md` 是文档导航，`docs/使用说明.md` 面向角色使用路径，`docs/演示数据导入说明.md` 说明测试数据和演示资产。
- 涉及 API、配置、数据结构、部署、GraphRAG、KT、LLM、Agent 或关键前端交互的变更，需要同步相关 `docs/` 文档和 `docs/CHANGELOG.md`。
- 根目录只保留入口型文档；说明文档默认放入 `docs/`。

## 工作约定摘要

- 开始任务前检查 `git status`，注意保护用户未提交改动；未经明确要求不要主动 push、建分支、提交 PR 或改写远端历史。
- 根 `AGENTS.md` 要求每个独立可审查工作块提交一次，提交格式为 `type(scope): 中文摘要`；如果用户没有要求提交，先确认再 commit。
- 命名要表达业务语义，避免弱命名；单个源文件超过 500 行时优先拆分职责。
- 后端 Python 文件、类、函数注释要求见 `backend/AGENTS.md`；前端注释和 Fluent 2 风格要求见 `frontend/AGENTS.md`。
- 完成任务时说明改动范围、验证命令、文档同步情况、commit 情况和剩余风险。
