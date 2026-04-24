# 知识图谱驱动的个性化自适应学习系统文档总览

> 最后更新：2026-04-24

当前文档已按仓库中的**真实实现**重新整理，下面列出的文件均存在于当前工作树中，可直接阅读或继续维护。

## 建议阅读顺序

1. `安装说明.md`：本地开发环境搭建与一键安装
2. `使用说明.md`：学生、教师、管理员三端的主要使用路径
3. `演示数据导入说明.md`：评委演示 / 答辩所需账号与数据重建方法
4. `服务器部署说明.md`：前端独立服务器 + `1Panel` 后端服务器的推荐部署方案
5. `GraphRAG实现说明.md`：课程级 GraphRAG 的离线索引、Qdrant 和 Neo4j 投影
6. `MEFKT实现说明.md`：MEFKT 训练、题目级在线部署与 KT 融合
7. `LangChain智能体说明.md`：LangChain agent 的边界和工具集
8. `大模型接入说明.md`：通义千问 / DeepSeek 接入方式与 fallback 机制

## 文档索引

- `README.md`：当前文档总导航
- `安装说明.md`：本地安装与开发启动
- `使用说明.md`：三端页面与使用流程
- `演示数据导入说明.md`：演示账号、课程与答辩环境数据导入说明
- `服务器部署说明.md`：双机分离部署与生产 / 演示环境部署
- `GraphRAG实现说明.md`：GraphRAG 实现细节
- `MEFKT实现说明.md`：MEFKT 与 KT 实现细节
- `LangChain智能体说明.md`：LangChain agent 说明
- `大模型接入说明.md`：LLM 提供方配置与排障
- `API.md`：后端接口说明
- `api.yaml`：OpenAPI 描述文件
- `CHANGELOG.md`：项目变更记录
- `论文.pdf`：项目论文材料
- `饶弘玮 25网工A2 个性化自适应学习系统 AI赋能方案.pptx`：项目方案材料

## 当前实现的关键事实

- 后端默认从 `backend/.env` 读取运行配置。
- `install.py` 默认生成：
  - `backend/.env`
- 前端本地开发默认通过 `frontend/vite.config.ts` 代理 `/api`、`/media`、`/static`、`/ws`，当前代理目标默认为 `http://127.0.0.1:8000`，并监听 `0.0.0.0:3000`；如需联调远端环境，可通过 `VITE_DEV_BACKEND_ORIGIN` 覆盖，如需覆盖开发端口，可设置 `VITE_DEV_PORT`。
- 前端生产构建默认通过 `frontend/src/api/backend.ts` 走同域 `/api`、`/media`、`/static`、`/ws`；如需切换为直连其他后端入口，可设置 `VITE_BACKEND_ORIGIN` 后重新构建。
- 默认 LLM 提供方为 `deepseek`，默认模型为 `deepseek-v4-pro`，并通过 `LLM_EXTRA_BODY_JSON={"enable_thinking":false}` 关闭兼容网关的思考输出。
- 本地开发默认地址：
  - 前端：`http://127.0.0.1:3000`
  - 后端：`http://127.0.0.1:8000`
- GraphRAG 课程索引默认位于：
  - `backend/runtime_logs/rag/course_{course_id}.json`
- GraphRAG 本地向量库默认位于：
  - `backend/runtime_logs/rag/qdrant/`
- KT 当前支持：
  - `DKT`
  - `MEFKT`
  - `fusion / single / ensemble`

## 常用命令

### 一键安装

```bash
python install.py
```

Windows 也可以直接执行：

```bash
install.bat
```

### 后端健康检查

```bash
cd backend
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe tools.py db-check
.venv\Scripts\python.exe tools.py django-check
```

### GraphRAG / KT / 回归

```bash
cd backend
.venv\Scripts\python.exe tools.py build-rag-index
.venv\Scripts\python.exe tools.py mefkt-status
.venv\Scripts\python.exe tools.py api-regression --all --json
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
.venv\Scripts\python.exe tools.py rebuild-demo-data --course-name "大数据技术与应用"
.venv\Scripts\python.exe tools.py browser-audit --scenario audit --frontend-url http://127.0.0.1:3000 --api-base-url http://127.0.0.1:8000
```

## 维护原则

后续如继续更新文档，请优先遵循以下原则：

1. 只引用当前仓库中真实存在的文件。
2. 只写当前代码已实现的能力，不为“未来计划”补虚构说明。
3. 遇到路径、命令、环境变量变更时，优先同步 `README.md`、`docs/README.md`、`docs/安装说明.md`、`backend/.env.example` 与 `frontend/vite.config.ts`。
