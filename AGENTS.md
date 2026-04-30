# SaleAgents 多 Agent 协同规范

> 本文档是所有 AI agent 的必读入口。无论你是 Claude、Codex、OpenCode 还是 Trae，开始工作前先读此文件。

## 1. 必读文件顺序

每次开始工作前，按以下顺序阅读：

1. **`tasks/TASK_BOARD_V2.md`** — 看当前迭代有哪些 open 任务，认领工作
2. **`specs/README.md`** — 看有哪些相关规范需要了解
3. **`CLAUDE.md`** — 看项目技术栈、常用命令和架构约定

## 2. 任务录入规范（Bug / 新需求）

**谁录入**：人类开发者（默认），或经授权的看板管理员 agent。

**何时录入**：
- 发现线上/本地 bug 时
- 新增需求或变更需求时
- Agent 在开发中发现阻塞性问题，经确认需要独立跟踪时

**怎么录入**：在 `tasks/TASK_BOARD_V2.md` 中新增一行，填写 9 列。

### Task ID 规则

| 前缀 | 用途 | 示例 |
|------|------|------|
| `BE-xxx` | 后端 feature / 重构 | `BE-018` |
| `FE-xxx` | 前端 feature / 重构 | `FE-011` |
| `QA-xxx` | 测试任务 | `QA-006` |
| `BUG-xxx` | Bug 修复（推荐独立前缀） | `BUG-001` |
| `SPEC-xxx` | 规范维护 | `SPEC-004` |
| `E2E-xxx` | 端到端验收 | `E2E-002` |

**编号递增**：在当前同类型最大编号 +1。例如当前最大 BUG 是 `BUG-003`，新 bug 就是 `BUG-004`。

### 录入模板（Bug）

```markdown
| BUG-004 | F082 | Bug修复 | ProposalEditor.vue 导出 docx 时文件名乱码 | 待认领 | todo | 无 | 导出文件名正确显示中文，smoke 通过 | `tasks/worklogs/<agent>.md` |
```

字段说明：

| 列 | 填写说明 |
|----|----------|
| `task_id` | 按规则生成，如 `BUG-004` |
| `来源功能点` | 关联的 feature_id（如 `F082`），无则填 `-` |
| `问题类型` | `Bug修复` / `后端` / `前端` / `测试` / `规范` / `端到端验收` |
| `目标结果` | 一句话描述要修复什么问题 |
| `owner` | 录入时填 `待认领`，agent 认领后改名字 |
| `status` | 录入时填 `todo` |
| `depends_on` | 阻塞依赖的任务 id，无则填 `无` |
| `验收标准` | 修复完成后如何验证（可运行、可观测的标准） |
| `记录文件` | `tasks/worklogs/<agent名字>.md` |

### 录入流程

```
发现 bug
  ↓
在 TASK_BOARD_V2.md 最后一行追加记录
  ↓
分配 task_id（查看同类型最大编号 +1）
  ↓
status = todo, owner = 待认领
  ↓
Agent 按下方"任务认领流程"接手
```

## 3. 任务认领流程

1. 在 `tasks/TASK_BOARD_V2.md` 中找一个状态为 `open` 或 `todo` 的任务
2. 将"负责人"列改为你的名字（`claude` / `codex` / `opencode` / `trae` / 其他）
3. 将"状态"改为 `in_progress`
4. 在 `tasks/worklogs/<你的名字>.md` 中新建或追加当日工作记录
5. 完成后将状态改为 `done`，并更新 `tasks/CHANGE_LOG_V2.md`

## 3. 工作输出规范

| 输出类型 | 存放位置 | 要求 |
|----------|----------|------|
| 代码修改 | `backend-v2/` / `frontend-v2/` | 正常提 commit，遵循 `specs/testing-spec.md` |
| 工作记录 | `tasks/worklogs/<你的名字>.md` | 按日期追加，记录做了什么、遇到什么问题 |
| API 契约变更 | 先改 `specs/api-contract-spec.md` | 再改代码，**禁止**先改代码后补规范 |
| 工程边界变更 | 先改 `specs/engineering-spec.md` | 再改代码 |
| 任务完成 | 更新 `tasks/CHANGE_LOG_V2.md` | 按日期追加变更条目 |

## 4. 目录速查

| 目录 | 内容 | 你应该做什么 |
|------|------|-------------|
| `specs/` | PRD、架构、API 契约、开发规范 | **读**，按需了解，不要直接修改（除非你是 spec-agent） |
| `tasks/` | 任务看板、变更日志、工作日志 | **读 + 写**，这是你每天工作的地方 |
| `backend-v2/` | 后端代码（FastAPI + SQLAlchemy） | **改** |
| `frontend-v2/` | 前端代码（Vue 3 + Vite + Tailwind） | **改** |
| `CLAUDE.md` | 项目技术规范与常用命令 | **读** |

## 5. 规范修改优先级

当工作需要修改规范时，遵循以下优先级：

1. **API 变化** → 先改 `specs/api-contract-spec.md`
2. **工程架构变化** → 先改 `specs/engineering-spec.md`
3. **前端样式/交互约束变化** → 先改 `specs/frontend-style-spec.md`
4. **后端模型/数据库变化** → 先改 `specs/backend-dev-spec.md`
5. **测试门槛变化** → 先改 `specs/testing-spec.md`
6. **任务流转规则变化** → 先改 `specs/task-governance-spec.md`

## 6. 状态词汇表

任务看板统一使用以下状态：

| 状态 | 含义 |
|------|------|
| `todo` | 待认领 |
| `in_progress` | 进行中 |
| `blocked` | 阻塞中（需标注阻塞原因和依赖） |
| `review` | 待评审 |
| `done` | 已完成 |
