# Style Guide

本文件约束项目代码、文档、API 契约和界面维护风格。若与更深层目录约定冲突，以更深层约定和具体任务要求为准。

## 通用原则

- 命名表达业务语义，不使用 `tmp`、`foo`、`bar`、`data`、`obj`、`var` 等弱命名。
- 单个源文件超过 500 行时优先拆分职责，避免继续堆叠实现。
- 注释解释意图、约束、边界和风险，不复述代码表面行为。
- 不保留空实现、假成功逻辑、未接线入口或一次性调试代码。
- 涉及 API、配置、数据结构、部署、GraphRAG、KT、LLM、Agent 或关键交互的变更必须同步文档。

## Python / Django

- 遵循 PEP 8、Django / DRF 官方实践和仓库既有分层。
- View 只负责请求校验、权限、编排和响应，不承载完整 LLM / RAG / KT / Agent 流程。
- Serializer 不执行复杂图查询、外部模型调用或长耗时业务编排。
- Service 层负责可测试的业务逻辑，GraphRAG、LLM、KT、KG 和 Agent 边界保持独立。
- 函数参数和返回值尽量显式标注类型，避免不必要的 `Any`。

## TypeScript / Vue

- 使用 Vue 3 Composition API、TypeScript、Pinia 和 Vue Router 的既有模式。
- 页面负责展示和轻量编排，复杂状态映射、API 适配和图谱处理应下沉到 composable、store、utils 或专门模块。
- 可复用视觉结构优先抽成共享组件，避免在页面层重复硬编码颜色、间距、圆角和状态样式。
- 用户可见界面保持 Fluent 2 风格一致性；依赖 Element Plus 时也应统一视觉密度、层级、动效和反馈方式。
- 前端错误提示优先展示后端返回的用户可读信息，并保留必要的失败状态。

## API

- API 契约以 `docs/api.yaml` 为准。
- 新增接口时明确认证要求、角色边界、请求体、响应体、错误结构和分页约定。
- 错误响应保持 `code`、`msg`、`data`，结构化错误补充 `error.type` 与 `error.details`。
- 前端调用和回归脚本应与 `docs/api.yaml` 同步，不保留旧路径兼容假设。

## 文档

- 文档统一放在 `docs/`，根目录只保留入口型文件，如 `README.md`、`STYLE.md`、`LICENSE`。
- 文档只描述当前已实现能力，不用“计划中”内容填补功能空缺。
- 命令示例优先使用当前真实工具链：后端 `uv sync` / `uv run`，前端 `npm install` / `npm run ...`。
- 配置项说明应写清来源、默认值、用途和泄密风险。
- 历史变更写入 `docs/CHANGELOG.md`，不要把一次性运行日志当正文文档维护。

## Git 与仓库卫生

- 缓存、依赖目录、运行日志、浏览器巡检输出、代理状态和私有配置不进入版本库。
- 后端不再维护 `requirements.txt`；前端不提交 `node_modules/`。
- 每个独立工作块单独提交，提交信息使用 `type(scope): 中文摘要`。
- 提交前至少执行与改动范围匹配的验证，并运行 `git diff --check`。
