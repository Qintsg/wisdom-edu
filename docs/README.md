# 知识图谱驱动的个性化自适应学习系统文档总览

> 最后更新：2026-05-11

本文档目录面向开发、答辩演示、部署运维和后续维护。文档内容以当前仓库真实实现为准，API 契约统一维护在 `docs/api.yaml`。

## 推荐阅读顺序

1. `安装说明.md`：本地开发环境、uv 后端依赖同步、前端依赖安装与首次验证。
2. `使用说明.md`：学生、教师、管理员三端页面和主要业务流程。
3. `演示数据导入说明.md`：答辩账号、演示课程、数据重建与浏览器巡检。
4. `服务器部署说明.md`：前后端分离部署、Daphne、Nginx / OpenResty 与静态资源托管。
5. `维护说明.md`：日常维护、依赖更新、API 契约、数据迁移和发布检查。
6. `api.yaml`：OpenAPI 契约源文件。
7. `GraphRAG实现说明.md`：课程级 GraphRAG、Qdrant 和 Neo4j 投影。
8. `MEFKT实现说明.md`：MEFKT 训练、在线部署与 KT 服务接入。
9. `LangChain智能体说明.md`：LangChain agent 的职责边界与工具集。
10. `大模型接入说明.md`：通义千问 / DeepSeek / 兼容网关接入与排障。

## 文档索引

- `README.md`：当前文档总导航。
- `安装说明.md`：本地安装、开发启动与验证命令。
- `使用说明.md`：三端页面、典型流程和常用接口入口。
- `维护说明.md`：维护职责、依赖、配置、API、数据、验证和发布流程。
- `演示数据导入说明.md`：演示账号、课程与答辩环境数据导入说明。
- `服务器部署说明.md`：双机分离部署与生产 / 演示环境部署。
- `GraphRAG实现说明.md`：GraphRAG 实现细节。
- `MEFKT实现说明.md`：MEFKT 与 KT 实现细节。
- `LangChain智能体说明.md`：LangChain agent 说明。
- `大模型接入说明.md`：LLM 提供方配置与排障。
- `api.yaml`：OpenAPI 描述文件和接口契约源。
- `CHANGELOG.md`：项目变更记录。
- `论文.pdf`：项目论文材料。
- `饶弘玮 25网工A2 个性化自适应学习系统 AI赋能方案.pptx`：项目方案材料。
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
- API 契约以 `docs/api.yaml` 为准，后端运行态 Schema 地址为 `http://127.0.0.1:8000/api/schema/`。
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

### 前端验证

```bash
cd frontend
npm run typecheck
npm run build
```

### 演示数据与浏览器巡检

```bash
cd backend
uv run python tools.py rebuild-demo-data --course-name "大数据技术与应用"
uv run python tools.py browser-audit --scenario audit --frontend-url http://127.0.0.1:3000 --api-base-url http://127.0.0.1:8000
```

## 维护原则

1. 只引用当前仓库中真实存在的文件。
2. 只写当前代码已实现的能力，不用文档承诺未接线功能。
3. 接口变化时优先更新 `docs/api.yaml`，再同步使用说明、维护说明和 `docs/CHANGELOG.md`。
4. 路径、命令、环境变量变更时同步根 `README.md`、`docs/README.md`、`docs/安装说明.md`、`backend/.env.example` 与相关部署说明。
5. 缓存、依赖目录、测试输出、代理状态和私有配置只进入 `.gitignore`，不进入版本库。
