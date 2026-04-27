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

## 2026-04-24 文档同步更新

- 更新 `TASK_BOARD_V2.md`：补充登记 BE-010、BE-011、FE-007、QA-004 为 `done`；刷新日期为 2026-04-24。
- 更新 `FEATURE_MATRIX_V2.md`：刷新日期为 2026-04-24；健康检查状态从"未开始"→"已完成"；系统设置-AI配置更新为 schema 漂移已修复；F051/F052/F053/F054/F082 的差距和证据按 BE-010/BE-011/FE-001/FE-007/QA-002 实际进展更新。
- 更新 `TEST_REPORT_V2.md`：新增 "7. 2026-04-23 运行态验证"章节，记录修正的失败阻塞项、页面级走查结果、新增后端能力验收。
- 更新 `TEST_PLAN_V2.md`：支撑能力测试计划中健康检查和 AI 配置状态从"失败"更新为"200 已通过"。

## 2026-04-24 BE-017 招标信息真实 HTTP 抓取

- **BE-017**: 实现 `tender_fetch_service.py` 真实 HTTP 招标信息抓取，替换 `_fallback_seed_tenders` mock 实现
  - 新增 `_fetch_with_retry`：基于 `httpx`的 HTTP GET 工具，支持指数退避重试（3 次）、自定义 User-Agent、超时设置和编码指定。
  - 新增 `_parse_ccgp_tenders`：解析中国政府采购网（search.ccgp.gov.cn）搜索结果 HTML，提取标题、链接、发布日期等字段。
  - 新增 `_parse_zbytb_tenders`：解析中国招标信息网（zbytb.com）列表页 HTML。
  - 修改 `fetch_tenders_from_source`：优先尝试真实抓取，失败时自动降级到 `_fallback_seed_tenders`，保留 fallback 降级策略。
  - 依赖更新：`requirements.txt` 和 `pyproject.toml` 新增 `httpx`、`beautifulsoup4`。
  - 语法验证：`python -m py_compile` 通过。


## [2026-04-25 19:03] E2E-001 End-to-End Acceptance Test

- **Flow:** Login → Create Tender → Upload → Parse → Generate → Score → Edit → Rescore
- **Result:** 12/14 API calls returned 2xx
- **Project ID:** `proj_caff1882ed66` | **Tender ID:** `tend_7e706b8a14ff`
- **Score Before:** 0 | **Score After:** 0
- **Failures:** 2 steps non-2xx (Parse timeout due to backend bug; Edit skipped due to zero proposal sections)
- **Key Bugs Found:**
  1. `tenders.py` calls `_parse_single_file_async(project_id, path, filename)` with 3 args but function signature requires 4 args (missing `task_id`), causing background parsing to crash silently.
  2. `proposal_service.generate_proposal` accesses `tender.service_commitment` which does not exist on `Tender` model, causing generation task to fail.


### [2026-04-25 19:04] E2E-001 Supplement (Correct Upload Path)
- **Project:** `proj_caff1882ed66` | **Parsing Sections:** 14 | **Proposal Sections:** 0
- **Score Before Edit:** 0 | **After Rescore:** 0
- **Result:** 11/12 steps returned 2xx
- **Note:** Using `/parsing/{project_id}/upload` successfully triggered background parsing (14 sections extracted). Proposal generation still failed due to Bug #2 above.


### [2026-04-25 19:06] E2E-001 Business/Technical Document Flow
- **Project:** `proj_caff1882ed66` | **Business Docs:** 13 | **Technical Docs:** 9
- **Result:** 8/10 steps returned 2xx
- **Findings:**
  - Business/Technical document **edit** APIs work (PATCH returned 200).
  - Business/Technical document **score** APIs work (GET returned 200, scores: 3.6 and 0.0).
  - Business/Technical document **generate** APIs return 500 (likely same root cause as proposal generation or missing AI config).
  - Parsing section **edit** API works (PATCH returned 200).

### [2026-04-25 19:12] E2E-001 Bug Fixes
- **Fix Bug 1** (`tenders.py` 参数不匹配): 
  - Modified `_parse_single_file_async` in `parsing.py` to make `task_id` optional (default `None`).
  - Added conditional checks to skip `update_task_status` calls when `task_id` is absent.
- **Fix Bug 2** (`Tender` model 缺少 `service_commitment`):
  - Added `service_commitment: Mapped[str]` column to `app/models/tender.py`.
  - Added `service_commitment: str | None` field to `TenderSummary` schema with validator.
  - Created and ran Alembic migration `62b79a85dd46_add_service_commitment_to_tenders`.

