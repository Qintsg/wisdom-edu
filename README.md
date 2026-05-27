# 知识图谱驱动的个性化自适应学习系统

本项目是面向课程教学、学习诊断与个性化辅导的一体化 Web 平台。系统以知识图谱为课程结构底座，结合学习画像、MEFKT 知识追踪、GraphRAG 检索增强生成、在线测评与 AI 学习助手，为学生提供可追溯的学习路径、资源推荐、阶段反馈与问答支持，同时为教师和管理员提供课程、题库、班级、资源与账号治理能力。

## 项目元信息

| 项目 | 内容 |
| --- | --- |
| 开发者 | 饶弘玮，上海第二工业大学 25网工A2 |
| 单位 | 上海第二工业大学 / 计算机与信息工程学院 |
| 上海市大学生计算机应用能力大赛 | 2026 年第十八届，参赛编号 `20260235`，参赛组别 Web 网站设计，作品名称“知识图谱驱动的个性化自适应学习系统” |
| 超星杯“AI+教育”创新应用大赛 | 上海第二工业大学 2026 年超星杯“AI+教育”创新应用大赛，赛道一：AI 赋能学生学业，作品名称“个性化自适应学习系统” |
| 大学生创新创业训练计划 | 2026 年度大学生创新创业训练计划项目，项目编号 `2026-G12044-038`，创新训练项目，国家级，项目名称“智慧教育——基于知识图谱的个性化教学辅助平台” |

由上海市大学生创新创业训练计划项目 `2026-G12044-038` 资助。

Supported by the Shanghai Undergraduate Training Program on Innovation and Entrepreneurship (SUTPIE) grant `2026-G12044-038`.

## 核心能力

- 学生、教师、管理员三端统一 Web 应用，覆盖学习、教学与平台治理。
- 课程知识图谱可视化，支持知识点详情、关系查询、课程资源与学习状态联动。
- 个性化学习路径、任务学习、初始测评、阶段测试、在线作业与反馈报告闭环。
- 学习画像、资源推荐、课程问答、图谱增强解释和 GraphRAG 证据召回。
- MEFKT 知识追踪与规则兜底并行，输出掌握度、薄弱点和学习建议。
- 基础测试数据、课程资产导入、API 回归和浏览器巡检覆盖开发与验收场景。

## 技术架构

- 前端：`frontend/`
  - Vue 3、Vite、TypeScript、Pinia、Vue Router。
  - Element Plus 组件基础，界面规范按 Fluent 2 风格收口。
  - D3.js / ECharts 用于知识图谱、画像和统计可视化。
- 后端：`backend/`
  - Python 3.12、Django、Django REST Framework、Channels。
  - PostgreSQL 保存用户、课程、题目、学习记录、测评、任务与日志等事务数据。
  - Neo4j 保存知识点、概念、依赖、先修和路径推理等图结构数据。
  - Qdrant、Neo4j GraphRAG、LangChain、DeepSeek / 通义千问兼容客户端支撑 AI 能力。
  - `backend/platform_ai` 汇聚 RAG、LLM、KT、搜索与 Agent 边界实现。
- 文档与契约：`docs/`
  - API 契约源以 `docs/openapi/openapi.yaml` 为准，`docs/api.yaml` 为 Redocly CLI 打包产物，旧 Markdown API 文档已移除。
  - 使用说明、OpenAPI 契约、变更记录和项目材料集中维护；旧专题说明文档已清理。

## 快速启动

### 后端

首次运行前基于 `backend/.env.example` 创建 `backend/.env`，填写 PostgreSQL、Neo4j、LLM、GraphRAG、KT 和 Django 配置。

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py runserver 127.0.0.1:8000
```

后端依赖由 `backend/pyproject.toml` 与 `backend/uv.lock` 锁定。需要严格复现锁文件时使用：

```bash
cd backend
uv sync --frozen
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

默认开发地址：

- 前端：`http://127.0.0.1:3000`
- 后端：`http://127.0.0.1:8000`
- Swagger：`http://127.0.0.1:8000/api/docs/`
- ReDoc：`http://127.0.0.1:8000/api/redoc/`
- OpenAPI Schema：`http://127.0.0.1:8000/api/schema/`

本地开发默认通过 `frontend/vite.config.ts` 将 `/api`、`/media`、`/static`、`/ws` 代理到 `127.0.0.1:8000`，不需要额外配置 Nginx、Caddy 或其他反向代理。需要临时联调远端后端时设置 `VITE_DEV_BACKEND_ORIGIN`；需要切换开发端口时设置 `VITE_DEV_PORT`；生产包需要直连其他后端入口时设置 `VITE_BACKEND_ORIGIN` 后重新构建。

## 常用命令

### 后端验证

```bash
cd backend
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python tools.py db-check
uv run python tools.py django-check
```

### 前端验证

```bash
cd frontend
npm run typecheck
npm run build
```

### 测试数据、课程资产与浏览器巡检

```bash
cd backend
uv run python tools.py create-test-data
uv run python tools.py bootstrap-course-assets --course-name "大数据技术与应用"
uv run python tools.py browser-audit --scenario audit --frontend-url http://127.0.0.1:3000 --api-base-url http://127.0.0.1:8000
```

## 目录结构

```text
backend/   Django + DRF + Channels + GraphRAG + MEFKT + LLM 服务
frontend/  Vue 3 + Vite + TypeScript + Fluent 2 风格界面
docs/      使用说明、OpenAPI 契约、变更记录与项目材料
```

## 文档导航

- `docs/README.md`：文档总览和推荐阅读顺序。
- `docs/使用说明.md`：学生、教师、管理员三端使用路径。
- `docs/openapi/openapi.yaml`：模块化 OpenAPI 契约源文件。
- `docs/api.yaml`：Redocly CLI 打包后的单文件 OpenAPI 产物。
- `docs/CHANGELOG.md`：项目变更记录。
- `LICENSE`：Academic Free License version 3.0（AFL-3.0）。

## 维护边界

- 运行配置、密钥、缓存、依赖目录、Playwright 产物和本地代理状态不进入版本库。
- 后端依赖以 `backend/pyproject.toml` 与 `backend/uv.lock` 为准，不再维护 `requirements.txt`。
- 前端依赖以 `frontend/package.json` 与 `frontend/package-lock.json` 为准，`node_modules/` 仅本地生成。
- API 契约源以 `docs/openapi/openapi.yaml` 为准；接口变化后优先更新 `docs/openapi/`，再打包生成 `docs/api.yaml` 并同步相关说明和 `docs/CHANGELOG.md`。
- 涉及 RAG / KT / KG / LLM / Agent、数据库结构、配置、部署或关键交互的改动必须同步文档并完成验证。

## 许可证

本项目源代码版权归 Qintsg(饶弘玮) 所有，使用 Academic Free License version 3.0（AFL-3.0）授权，详见 `LICENSE`。

Licensed under the Academic Free License version 3.0.

除非另有明确声明，课程资源、论文、演示素材、媒体文件、数据集和第三方素材不随源代码许可证自动授权；使用这些非代码资产时应分别确认其权利来源与授权范围。

Copyright (c) 2026 Qintsg(饶弘玮)
