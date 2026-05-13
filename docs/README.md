# 知识图谱驱动的个性化自适应学习系统文档总览

> 最后更新：2026-05-13

本文档目录面向开发、验收、接口契约维护和项目材料归档。文档内容以当前仓库真实实现为准，API 契约源文件统一维护在 `docs/openapi/openapi.yaml`，`docs/api.yaml` 为 Redocly CLI 打包后的单文件产物。

## 推荐阅读顺序

1. `使用说明.md`：学生、教师、管理员三端页面、主要业务流程和常用命令。
2. `演示数据导入说明.md`：基础账号、默认入班、课程资产导入与浏览器巡检。
3. `openapi/openapi.yaml`：模块化 OpenAPI 契约入口；`api.yaml` 为打包产物。
4. `CHANGELOG.md`：项目变更记录。

## 文档索引

- `README.md`：当前文档总导航。
- `使用说明.md`：三端页面、典型流程和常用接口入口。
- `演示数据导入说明.md`：基础账号、课程资产、默认入班与浏览器巡检说明。
- `openapi/openapi.yaml`：模块化 OpenAPI 描述文件和接口契约源，入口只保留全局信息和 `$ref`。
- `api.yaml`：由 Redocly CLI 从 `docs/openapi/openapi.yaml` 打包生成的单文件 OpenAPI 描述。
- `CHANGELOG.md`：项目变更记录。
- `论文.pdf`：项目论文材料。
- `../STYLE.md`：代码、文档、API 与界面风格约定。
- `../LICENSE`：MIT License。

## 项目与参赛信息

- 开发者：饶弘玮，上海第二工业大学 25网工A2。
- 单位：上海第二工业大学 / 计算机与信息工程学院。
- 2026 年第十八届上海市大学生计算机应用能力大赛参赛作品，参赛编号 `20260235`，参赛组别 Web 网站设计，作品名称“知识图谱驱动的个性化自适应学习系统”。
- 上海第二工业大学 2026 年超星杯“AI+教育”创新应用大赛，参赛类别为赛道一：AI 赋能学生学业，作品名称“个性化自适应学习系统”。
- 2026 年度大学生创新创业训练计划项目，项目编号 `2026-G12044-038`，项目类型为创新训练项目，项目名称“智慧教育——基于知识图谱的个性化教学辅助平台”，项目级别为国家级。
- 本项目由上海市大学生创新创业训练计划项目 `2026-G12044-038` 资助。

## 当前实现的关键事实

- 后端默认从 `backend/.env` 读取运行配置，配置模板为 `backend/.env.example`。
- 后端依赖由 `backend/pyproject.toml` 与 `backend/uv.lock` 管理，使用 `uv sync` 创建或更新 `backend/.venv`。
- 前端本地开发默认通过 `frontend/vite.config.ts` 代理 `/api`、`/media`、`/static`、`/ws` 到 `http://127.0.0.1:8000`，并监听 `0.0.0.0:3000`。
- 前端生产构建默认走同域 `/api`、`/media`、`/static`、`/ws`；确需直连其他后端入口时使用 `VITE_BACKEND_ORIGIN` 后重新构建。
- 默认 LLM 提供方为 `deepseek`，默认模型为 `deepseek-v4-flash`，并通过 `LLM_EXTRA_BODY_JSON={"enable_thinking":false}` 关闭兼容网关的思考输出。
- API 契约源以 `docs/openapi/openapi.yaml` 为准，`docs/api.yaml` 为打包产物；后端运行态 Schema 地址为 `http://127.0.0.1:8000/api/schema/`。
- GraphRAG 课程索引默认位于 `backend/runtime_logs/rag/course_{course_id}.json`。
- GraphRAG 本地向量库默认位于 `backend/runtime_logs/rag/qdrant/`。
- KT 当前只保留 `MEFKT`，默认 `single` 模式；`fusion / ensemble` 响应结构保留用于后续扩展。

## 常用命令

### 后端依赖同步

```bash
cd backend
uv sync
```

### 后端健康检查

```bash
cd backend
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python tools.py db-check
uv run python tools.py django-check
```

### GraphRAG / KT / 回归

```bash
cd backend
uv run python tools.py build-rag-index
uv run python tools.py mefkt-status
uv run python tools.py api-regression --all --json
```

### API 契约校验和打包

```bash
npx @redocly/cli lint wisdomedu@v1
npx @redocly/cli bundle wisdomedu@v1
```

### 前端验证

```bash
cd frontend
npm run typecheck
npm run build
```

### 测试数据与浏览器巡检

```bash
cd backend
uv run python tools.py create-test-data
uv run python tools.py bootstrap-course-assets --course-name "大数据技术与应用"
uv run python tools.py browser-audit --scenario audit --frontend-url http://127.0.0.1:3000 --api-base-url http://127.0.0.1:8000
```

## 维护原则

1. 只引用当前仓库中真实存在的文件。
2. 只写当前代码已实现的能力，不用文档承诺未接线功能。
3. 接口变化时优先更新 `docs/openapi/` 下的模块化源文件，再用 Redocly CLI 校验并打包 `docs/api.yaml`，最后同步使用说明和 `docs/CHANGELOG.md`。
4. 路径、命令、环境变量变更时同步根 `README.md`、`docs/README.md`、`docs/使用说明.md`、`backend/.env.example` 与相关说明。
5. 缓存、依赖目录、测试输出、代理状态和私有配置只进入 `.gitignore`，不进入版本库。
