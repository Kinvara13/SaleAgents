# SaleAgents v2 变更留痕

## 2026-04-21

### 23:20 初始审计落地

- 创建根目录统一事实源：
  - `FEATURE_MATRIX_V2.md`
  - `PAGE_COVERAGE_V2.md`
  - `TASK_BOARD_V2.md`
  - `TEST_PLAN_V2.md`
  - `TEST_REPORT_V2.md`
  - `AGENT_WORKFLOW.md`
- 创建 `specs/` 规范目录和 `memory-bank/agent-worklogs/`
- 将 `frontend-v2/SPEC.md`、`frontend-v2/memory-bank/PROGRESS.md`、`frontend-v2/memory-bank/ARCHITECTURE.md` 标记为历史参考

### 23:28 运行态验证结论

- 默认 `python3` 为 `3.9`，`backend-v2` 因 `str | None` 注解在导入阶段启动失败
- 使用 `python3.11` 启动 `backend-v2` 后，确认以下接口可用：
  - `/api/v1/auth/login`
  - `DELETE /api/v1/chat/{project_id}/history`
  - `POST /api/v1/settings/rules`
  - `POST /api/v1/users`
  - `GET /api/v1/projects`
  - `GET /api/v1/tenders`
  - `GET /api/v1/users/roles/list`
  - `GET /api/v1/projects/{id}/business-documents`
  - `GET /api/v1/projects/{id}/technical-documents`
  - `GET /api/v1/projects/{id}/proposal-plans`
  - `POST /api/v1/proposal-editor/{id}/generate`
  - `POST /api/v1/proposal-editor/{id}/score`
  - `POST /api/v1/pricing/calculate`

### 23:33 运行态阻塞与漂移修正

- 修正旧结论：聊天清空接口并非 405，而是 200 正常返回
- 修正旧结论：用户创建接口并非 bcrypt 500，在 Python 3.11 环境下可正常创建
- 修正旧结论：技术建议书生成接口当前可返回章节数据，并非固定 500
- 新发现：`/api/v1/settings/ai-config` 和 `/api/v1/settings/ai-configs` 同为 500，根因是 SQLite 表 `ai_configs` 缺少 `name` 列
- 新发现：`health.py` 定义了 `/health`，但 `backend-v2/app/api/router.py` 未注册 `health.router`，因此 `/api/v1/health` 当前 404

### 23:37 前端静态问题确认

- `ProposalEditor.vue` 把 axios 当 fetch 使用，包含：
  - `res.ok`
  - `res.json()`
  - 错误的普通字符串动态路径
- `UserManagement.vue`、`RoleManagement.vue` 存在同类 axios/fetch 混用问题
- `vite build` 可通过，但不代表这些页面运行态可用
