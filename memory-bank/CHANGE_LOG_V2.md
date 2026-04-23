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

### 2026-04-21 (继续) 任务 BE-001 & BE-002 完成

- **BE-001**: 在 `backend-v2/app/api/router.py` 注册了 `health.router`，修复了 `/api/v1/health` 404 问题。并在 `test_api_v2.py` 中补充了健康检查的 smoke 用例。
- **BE-002**: 通过执行 `ALTER TABLE ai_configs ADD COLUMN name VARCHAR(128) NOT NULL DEFAULT '未命名配置';` 修复了 `ai_configs` 表的 schema 漂移问题，恢复了 `/api/v1/settings/ai-config` 接口的正常响应。
- **FE-001**: 修复了 `ProposalEditor.vue` 中的静态问题，将普通字符串改为模板字符串，将 fetch 的 `.json()` 和 `.ok` 访问方式改为基于 AxiosResponse 的 `.data`。

### 2026-04-23 项目工作台 + 文档真实填充链路

- **BE-010** (项目工作台真实数据驱动):
  - 扩展 `Project` 模型：新增 `tender_id`, `parse_status`, `file_list`, `node_status`, `extracted_fields` 字段，使项目能关联招标信息并跟踪处理状态。
  - 扩展 `ProjectSummary` schema：新增 `client_name`, `amount`, `risk_level`, `module_progress`, `parse_status`, `node_status`, `extracted_fields`。
  - 修复 `workspace_service.py` ：`get_projects_list` 、 `get_project_detail` 、 `get_project_progress` 、 `get_project_statistics` 全部改为基于真实 `Project` + `Tender` 数据动态构建，彻底淘汰 `FAKE_PROJECTS`。
  - 修复 `tenders.py` `upload_bid_document` ：上传文件后自动创建项目并触发解析，解析完成后自动更新 `parse_status = completed`。

- **BE-011** (商务文档真实参数填充):
  - 修改 `business_document_service.py` ：`generate_business_document` 现在从 `Project` + `Tender` + `ParsingSection` 实时抽取：
    - `project_summary` → 项目名称/类型/行业等
    - `tender_requirements` → 招标文件中的技术要求/合同条款/服务承诺
    - `delivery_deadline` → `project.deadline` 或 `tender.bid_deadline`
    - `service_commitment` → `tender.service_commitment`
  - 彻底淘汰所有 `str` 占位符。

- **FE-007** (前端契约对齐):
  - 扩展 `types/index.ts` `Project` 接口：新增 `parse_status`, `node_status`, `extracted_fields`。
  - 修改 `BidList.vue` ：列表增加 “解析状态” 和 “节点工作台” 列，展示真实解析/节点状态并提供快捷跳转。

- **QA-004** (烟雾测试):
  - `python -c "from app.main import app; print('Import OK')"` 通过。
  - 服务启动后 `/api/v1/health` 返回 200。
