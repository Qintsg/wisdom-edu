# AGENTS.md

## 适用范围

- 本文件适用于全仓；进入 `backend/` 或 `frontend/` 工作时，先读对应子目录 `AGENTS.md`，以子目录专项规则为准。
- 默认使用简体中文；仓库文本按 `.gitattributes` 统一为 UTF-8 + CRLF。

## 先读事实

- 当前没有 `.github/workflows/`、`.pre-commit-config.*`、根 `opencode.json`；本地验证以本文命令为准。
- 若根目录出现 `AGENT_TODO.md`，先按其顺序推进；该文件被 `.gitignore` 忽略，可能是本地任务清单。
- 后端依赖只认 `backend/pyproject.toml` + `backend/uv.lock`，前端依赖只认 `frontend/package.json` + `frontend/package-lock.json`；不要补 `requirements.txt`、pnpm 或 yarn 配置。
- 不要读取或提交 `backend/.env`、`backend/runtime_logs/`、`frontend/dist/`、`node_modules/`；后端配置模板是 `backend/.env.example`，非敏感默认值在 `backend/config.ini`。

## 架构边界

- `backend/wisdom_edu_api/settings.py` 是 Django 配置入口，会加载 `backend/.env` 并用环境变量覆盖 `config.ini` 默认值；`urls.py` 聚合各 app 路由，`asgi.py` 承载 WebSocket。
- Django apps 为 `users`、`courses`、`knowledge`、`assessments`、`learning`、`exams`、`ai_services`、`logs`、`common`；角色 API 多在各 app 的 `api/` 子包和 `urls.py` 中。
- AI/智能能力不要塞进 View、Serializer 或 Model：`platform_ai/rag` 管检索和 GraphRAG，`platform_ai/kt` 管 MEFKT，`platform_ai/llm` 管 LLM/Agent，`platform_ai/mcp` 管资源 MCP，`ai_services` 只暴露 HTTP/WebSocket/API 编排。
- PostgreSQL 是用户、课程、题目、学习记录、评测、任务、日志等事务数据源；Neo4j 可用于知识图谱与路径查询，但未配置时已有 PostgreSQL 图谱回退，别把 Neo4j 当必需前提。
- GraphRAG/Qdrant 运行产物默认在 `backend/runtime_logs/rag/`，MEFKT 默认模型路径在 `backend/models/MEFKT/`；修改这些链路时说明索引或模型是否需要重建。
- 统一 API 响应来自 `common.http.responses`：`{code,msg,data}`，错误可带 `error`；前端 Axios 会自动解包 `data` 并处理 JWT 刷新，不要在业务 API 里返回裸 DRF 格式破坏契约。

## 后端命令

- 后端命令均在 `backend/` 执行；安装依赖用 `uv sync`，严格复现锁文件用 `uv sync --frozen`。
- 启动后端：先 `uv run python manage.py migrate`，再 `uv run python manage.py runserver 127.0.0.1:8000`。
- 快速检查顺序：`uv run python manage.py check` -> `uv run python manage.py makemigrations --check --dry-run` -> `uv run python tools.py django-check` -> `uv run python tools.py db-check`。
- Django 单测示例：`uv run python manage.py test users.tests.test_auth_api --verbosity 2`；按模块路径缩小范围，不用 pytest。
- API/链路回归需要后端服务已启动且有基础账号：`uv run python tools.py api-smoke --json`、`uv run python tools.py student-flow-smoke --json`、`uv run python tools.py api-regression --all --json`。
- 数据和智能工具入口都在 `backend/tools.py`：`create-test-data` 只建基础账号/课程/班级；课程资产用 `bootstrap-course-assets --course-name "大数据技术与应用"`；GraphRAG 用 `build-rag-index` / `refresh-rag-corpus`；KT 用 `mefkt-status` / `train-mefkt`；Neo4j 用 `neo4j-status` / `sync-neo4j`。
- `pg-bootstrap` 会迁移、清库、创建测试数据并尝试导入课程资产，属于破坏性初始化；除非任务明确要求重建本地样例库，不要运行。

## 前端命令和约定

- 前端命令均在 `frontend/` 执行；安装/启动用 `npm install`、`npm run dev`；开发代理在 `vite.config.ts` 中把 `/api`、`/media`、`/static`、`/ws` 转到 `VITE_DEV_BACKEND_ORIGIN` 或默认 `http://127.0.0.1:8000`，端口用 `VITE_DEV_PORT` 覆盖。
- 验证：`npm run typecheck`；发布验证用 `npm run build`，该命令已包含 `vue-tsc --noEmit`，并会生成 `dist/404.html`、`dist/_redirects` 的 SPA fallback。
- 生产构建默认同源访问后端；只有确需跨域直连时设置 `VITE_BACKEND_ORIGIN` 后重建。
- 浏览器巡检需后端 `/health/` 正常且前端已启动；在 `backend/` 执行 `uv run python tools.py browser-audit --scenario audit --frontend-url http://127.0.0.1:3000 --api-base-url http://127.0.0.1:8000`。
- `npm run browser:audit` 底层脚本默认指向 `http://edu.qintsg.xyz`；本地巡检必须显式传 `--frontend-url` 和 `--api-base-url`，或使用上面的后端包装命令。
- 前端入口：`src/main.ts` 注册 Element Plus、Pinia、Router；路由在 `src/router/`，角色路由拆到 `routes/{student,teacher,admin}.ts`；请求入口是 `src/api/index.ts`，后端地址逻辑在 `src/api/backend.ts`。
- 学生页受 `router/guards.ts` 的课程选择门禁影响；新增无需课程的学生路由要设置 `meta.skipCourseCheck`，否则会跳转 `/student/course-select`。
- 课程上下文在 `src/stores/course.ts`，会把当前课程写入 `localStorage.current_course`；改课程、入班或退出班级后要刷新 store 缓存。
- UI 维持现有 Element Plus 组件与 Fluent 2 风格，不重新发明视觉体系；共享壳层/卡片优先复用 `components/common` 与 `layouts`。

## OpenAPI 与文档

- API 契约源只改 `docs/openapi/openapi.yaml` 和其 `$ref` 子文件；`docs/api.yaml` 是 Redocly 打包产物。
- 校验/打包从仓库根执行：`npx @redocly/cli lint wisdomedu@v1`，`npx @redocly/cli bundle wisdomedu@v1`。
- 接口、配置、数据结构、RAG/KT/KG/LLM/Agent 行为或关键前端流程变更时，同步 `docs/使用说明.md`、`docs/README.md`、`docs/CHANGELOG.md` 中相关段落。
- `docs/API.md` 已删除；当前检出中 `docs/演示数据导入说明.md` 和 `STYLE.md` 也不存在，除非先补齐文件，否则不要新增引用。

## 工作流

- 开始先看 `git status --short --branch`；当前仓库常有被 `.gitignore` 忽略的本地状态，别清理不相关改动。
- 若需要提交，commit 格式用 `type(scope): 中文摘要`；未经用户明确要求不 `push`、不切分支、不改写历史。
- 根目录只放仓库级说明；`backend/`、`frontend/` 的详细注释模板和专项规则维护在各自 `AGENTS.md`。
