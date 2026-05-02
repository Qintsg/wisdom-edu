# 知识图谱驱动的个性化自适应学习系统

基于 `Vue 3 + Django + DRF + PostgreSQL + Neo4j + Qdrant + LangChain` 的课程级自适应学习平台，围绕知识图谱、学习画像、学习路径、在线测评、知识追踪与 AI 学习辅助构建完整闭环。

## 当前重点能力

- 学生、教师、管理员三端统一 Web 应用
- 课程知识图谱可视化与知识点详情联动
- 个性化学习路径、任务学习、阶段测试与在线考试
- AI 学习画像、学习建议、反馈报告、课程内外资源推荐
- Neo4j GraphRAG + Qdrant 混合检索、MEFKT、LLM、外部搜索统一封装在 `backend/platform_ai`
- 浏览器自动巡检、演示数据重建与 API 回归工具

## 技术架构

- 前端：`frontend/`
  - Vue 3
  - Element Plus
  - Pinia / Vue Router
  - D3.js 知识图谱
- 后端：`backend/`
  - Django 6
  - Django REST Framework
  - PostgreSQL
  - Neo4j
  - Neo4j GraphRAG Python + Qdrant
  - LangChain agent + 通义千问 / DeepSeek 兼容聊天客户端
- 文档：`docs/`

## 快速启动

### 推荐：一键安装

```bash
python install.py
```

Windows 也可以直接执行：

```bash
install.bat
```

脚本会引导生成 `backend/.env`，并可按需完成依赖安装、迁移、静态资源收集与前端构建。前端开发期统一通过 `frontend/vite.config.ts` 代理 `/api`、`/media`、`/ws`。
当前开发代理默认联调 `http://127.0.0.1:8000`，并监听 `0.0.0.0:3000`，因此本地 `npm run dev` 无需额外配置 Nginx、Caddy 或其他反向代理；如需临时联调远端后端，可通过 `VITE_DEV_BACKEND_ORIGIN` 覆盖开发代理目标，通过 `VITE_DEV_PORT` 覆盖开发端口。生产构建默认直连 `http://127.0.0.1:8000`，如需让生产包改连其他后端入口，可通过 `VITE_BACKEND_ORIGIN` 覆盖后重新构建。

### 后端

```bash
cd backend
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

后端本地开发环境当前以 **Python 3.12** 为基线版本。

### 前端

```bash
cd frontend
npm install
npm run dev
```

默认开发地址：

- 前端：`http://0.0.0.0:3000`（局域网访问时使用宿主机实际 IP）
- 后端：`http://127.0.0.1:8000`

本地开发默认无需额外前端环境变量，也无需配置额外反向代理；`npm run dev` 会直接把 `/api`、`/media`、`/static`、`/ws` 代理到 `127.0.0.1:8000`。如需联调到其他后端地址，请调整 `frontend/vite.config.ts` 中对应代理目标或设置 `VITE_DEV_BACKEND_ORIGIN`；如需避开端口占用，可设置 `VITE_DEV_PORT`。若要让生产包请求其他域名/端口，则需要设置 `VITE_BACKEND_ORIGIN` 后重新构建。

## 常用入口

- 登录：`/login`
- 注册：`/register`
- 学生端：`/student/*`
- 教师端：`/teacher/*`
- 管理端：`/admin/*`
- Swagger：`http://127.0.0.1:8000/api/docs/`
- ReDoc：`http://127.0.0.1:8000/api/redoc/`

## 常用命令

### 演示数据重建

```bash
cd backend
.venv\Scripts\python.exe tools.py rebuild-demo-data --course-name "大数据技术与应用"
```

### 浏览器巡检

```bash
cd backend
.venv\Scripts\python.exe tools.py browser-audit --scenario audit --frontend-url http://127.0.0.1:3000 --api-base-url http://127.0.0.1:8000
```

说明：

- `audit` 会优先使用学生账号已完成提交的考试作为反馈报告入口，避免把未提交考试误判为反馈页异常。
- 执行 `rebuild-demo-data` 或 `ensure_defense_demo_environment` 后，`student1` 会自动带有真实阶段测试提交与完成态反馈报告，便于直接验收学生端反馈链路。

### 前端构建

```bash
cd frontend
npm run build
```

## 文档导航

- `docs/README.md`
- `docs/安装说明.md`
- `docs/使用说明.md`
- `docs/服务器部署说明.md`
- `docs/GraphRAG实现说明.md`
- `docs/MEFKT实现说明.md`
- `docs/LangChain智能体说明.md`
- `docs/大模型接入说明.md`
- `docs/API.md`

## 目录结构

```text
backend/   Django + DRF + Channels + GraphRAG + KT
frontend/  Vue 3 + Vite + Element Plus
docs/      安装、使用、部署与 AI/KT 实现说明
```
