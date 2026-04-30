# SaleAgents

招投标智能体 MVP。活跃代码位于 `-v2` 目录，legacy `backend/` 和 `frontend/` 已废弃。

| 模块 | 技术栈 | 端口 |
|------|--------|------|
| Backend | FastAPI + SQLAlchemy + SQLite(本地)/PostgreSQL(生产) | 8000 |
| Frontend | Vue 3 + Vite + Tailwind CSS + TypeScript | 8081 |

## 目录结构

```text
SaleAgents/
├── AGENTS.md              # 多 Agent 协同入口（所有 AI agent 必读）
├── CLAUDE.md              # 项目技术规范与开发命令
├── specs/                 # 规范文档（PRD、架构、API 契约、开发规范）
│   ├── bid-agent-prd.md
│   ├── api-contract-spec.md
│   └── ...
├── tasks/                 # 任务与进度（任务看板、变更日志、工作日志）
│   ├── TASK_BOARD_V2.md
│   ├── CHANGE_LOG_V2.md
│   └── worklogs/
├── backend-v2/            # 后端代码（活跃）
└── frontend-v2/           # 前端代码（活跃）
```

## 快速开始

```bash
# 启动后端 + 前端（后台运行，日志输出到 logs/）
./start.sh

# 停止
./stop.sh
```

手动启动见 `CLAUDE.md` → Common Commands。

---

## Agent 协同开发指南

本项目采用**多 Agent 协同开发**模式。无论你是 Claude、Codex、OpenCode、Trae、Hermes 还是 OpenClaw，开始工作前必须先加载入口文件。

### 统一入口文件

| 文件 | 用途 | 是否必读 |
|------|------|----------|
| `AGENTS.md` | 协同规范：任务认领、工作输出、目录速查、状态词汇 | **是** |
| `CLAUDE.md` | 技术规范：技术栈、常用命令、架构约定 | **是** |
| `specs/README.md` | 规范索引：按需深入阅读具体规范 | 按需 |
| `tasks/TASK_BOARD_V2.md` | 任务看板：找 open 任务、认领、更新进度 | **是** |

### 标准工作流

1. **读入口** → 加载 `AGENTS.md` + `CLAUDE.md`
2. **看板认领** → 在 `tasks/TASK_BOARD_V2.md` 找状态为 `todo/open` 的任务，填名字，改状态为 `in_progress`
3. **读规范** → 根据任务涉及范围，读 `specs/` 下对应规范
4. **写代码** → 修改 `backend-v2/` 或 `frontend-v2/`
5. **写日志** → 在 `tasks/worklogs/<你的名字>.md` 按日期追加工作记录
6. **更新看板** → 任务完成后改状态为 `done`，更新 `tasks/CHANGE_LOG_V2.md`

---

## 统一加载方式（所有工具通用）

无论使用 Claude Code、Codex、OpenCode、Trae 还是其他 AI 工具，**统一按以下方式开始对话**：

### 第一步：加载入口文件

对话开头先让 agent 读取 `AGENTS.md`：

```
@AGENTS.md

请严格按照 AGENTS.md 中的规范执行任务。
```

**说明**：
- 如果工具支持 `@文件` 语法（如 Claude Code、Codex），直接用 `@AGENTS.md`
- 如果不支持 `@` 语法，把 `AGENTS.md` 的内容复制粘贴到对话开头即可
- Claude Code 启动时会自动读取 `CLAUDE.md` 和 `AGENTS.md`，不需要手动加载

### 第二步：给出具体指令

加载入口后，给出具体任务指令：

**示例 1：让 agent 自己认领任务**

```
@AGENTS.md

请读取 tasks/TASK_BOARD_V2.md，认领一个状态为 todo/open 的后端任务，
按照 AGENTS.md 的工作流规范实现它，完成后更新看板和变更日志。
```

**示例 2：指定具体任务**

```
@AGENTS.md

我要实现 BE-018：优化标书解析性能。
请按照 AGENTS.md 规范，先读相关 specs，然后改 backend-v2/ 代码，
完成后更新 tasks/worklogs/<你的名字>.md 和 tasks/CHANGE_LOG_V2.md。
```

**示例 3：纯前端任务**

```
@AGENTS.md

请在看板中找一个前端相关的 open 任务，读取 specs/frontend-style-spec.md，
在 frontend-v2/ 中实现，遵循代码规范，完成后更新进度文档。
```

---

## 规范修改优先级速查

当工作需要修改规范时，遵循以下顺序：

1. **API 变化** → 先改 `specs/api-contract-spec.md`，再改代码
2. **工程架构变化** → 先改 `specs/engineering-spec.md`，再改代码
3. **前端样式/交互约束变化** → 先改 `specs/frontend-style-spec.md`，再改代码
4. **后端模型/数据库变化** → 先改 `specs/backend-dev-spec.md`，再改代码
5. **测试门槛变化** → 先改 `specs/testing-spec.md`，再改代码

---

## 状态词汇表

任务看板统一使用以下状态：

| 状态 | 含义 |
|------|------|
| `todo` | 待认领 |
| `in_progress` | 进行中 |
| `blocked` | 阻塞中（需标注阻塞原因和依赖） |
| `review` | 待评审 |
| `done` | 已完成 |
