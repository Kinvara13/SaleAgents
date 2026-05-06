# SaleAgents v2 变更留痕

## 2026-04-30

### 修复 BUG-007（Backend）

- `bid_template.py` → `preview_template_file()`：增加递归搜索兜底逻辑
- 原逻辑只在 `bid_templates/` 和 `bid_templates/extracted/` 根目录查找文件，但解压后的模板文件可能存放在子目录（如 `extracted/1、商务文件/`）下
- 新增：按优先级搜索（精确路径 → 根目录 → extracted/ → 递归搜索所有子目录），通过 `rglob("*")` 遍历并匹配文件名
- `python3.11 -m py_compile` 通过

### 修复 BUG-005 / BUG-006（Frontend）

**BUG-005**：回标文件页面顶部项目名称使用解析后字段
- `BidList.vue` → `selectProject()`：引入 `getExtractedFieldMap()`，优先从 `extracted_fields` 中取"项目名称"，与 `TenderList.vue` 的展示逻辑保持一致

**BUG-006**：编辑模式下切换文件时编辑内容同步更新
- `BidList.vue` → `handleSelectFile()`：增加 `isEditing.value` 判断，若处于编辑模式则同步更新 `editableContent.value`，确保切换文件后编辑区域显示正确内容

**验证**：`npm run build` 通过

### 修复 BUG-008 / BUG-009（Frontend）

**BUG-008**：回标文件编写页面右侧区域滚动与布局
- `BidList.vue` → 三栏布局容器及面板：
  - 左侧 AI 生成预览面板、中间模板原文件面板、右侧 AI 对话框面板统一添加 `h-full overflow-hidden min-w-0`
  - 修复 flex 高度链断裂问题，确保各面板内部溢出时可滚动
  - 调整宽度分配：`w-1/2`+`w-1/3`+`w-1/6` → `w-5/12`+`w-4/12`+`w-3/12`，避免 AI 面板过窄导致内容挤压

**BUG-009**：AI 助手对话框样式与消息展示
- `BidList.vue` → `input-suffix` 槽：
  - select 元素增加 `w-full max-w-full truncate`，移除 `space-x-2` 避免窄宽下溢出
  - 外层容器增加 `min-w-0` 防止 flex 子项被压缩到 0
- 布局修复后消息区域的 `flex-1 overflow-y-auto` 可正确计算高度，流式消息应能正常展示

**追加修复（滚动条未生效）**：
- `MainLayout.vue` → `<main>`：`overflow-auto` 改为 `overflow-hidden`，并在 `<router-view>` 外包一层 `<div class="h-full">`
- 根因：`main` 的 `overflow-auto` 使 `h-full` 子元素失去明确的高度参考，整个 flex 高度链断裂，面板内容溢出时无法触发内部滚动

**验证**：`npm run build` 通过

## 2026-07-09

### 修复 BUG-001 ~ BUG-004

**BUG-001 / BUG-002（Backend）**

- 新增 `project_service.py`：
  - `extracted_fields_to_map()`：将 `extracted_fields`（list 格式）转换为 label→value 字典
  - `_pick_first_non_empty()`：按优先级返回第一个非空值
  - `sync_project_core_fields()`：统一回填 `name / client / deadline / amount / bidding_company`
- `tenders.py` → `upload_bid_document`：创建项目后立即调用 `sync_project_core_fields`
- `parsing_service.py`：标书解析完成后再次调用 `sync_project_core_fields`，确保字段被持久化
- `parsing.py`：在解析完成路由中补充 `sync_project_core_fields` 调用

**BUG-001 / BUG-002（Frontend）**

- `TenderList.vue`：
  - 新增 `getProjectName / getClientName / getBidderName / getBudgetAmount / getDeadline / formatAmount` 计算属性
  - 卡片展示优先使用解析字段兜底，修复应标方字段来源（`bidding_company`）
  - 新增 `mineFilter` 状态和 `toggleMineFilter` 切换函数
- `TenderDetail.vue`：同样增加解析字段优先的 `displayProject` computed

**BUG-003（Frontend）**

- `ProjectCreate.vue`：生成回标文件完成后，通过 `router.push({ path: '/bid-list', query: { projectId } })` 跳转
- `BidList.vue`：读取 `route.query.projectId`，自动选中项目并触发 `loadSections` 展示模板清单
- `TenderDetail.vue`：补充 `job` 空值保护

**BUG-004（Frontend）**

- `BidList.vue`：`loadSections` 重构为仅加载模板文件（不再拉取原投标解析章节），`fileTree` 仅展示 `section_type === '模板'` 的节点
- 移除 `getTenderSections` 在 `loadSections` 中的调用，消除投标文件混入问题

**测试覆盖**

- 新增 `tests/test_project_service.py`：验证 `extracted_fields_to_map` 和 `sync_project_core_fields` 逻辑

## 2026-04-21

### 23:20 初始审计落地

- 创建根目录统一事实源：
  - `FEATURE_MATRIX_V2.md`
  - `PAGE_COVERAGE_V2.md`
  - `TASK_BOARD_V2.md`
  - `TEST_PLAN_V2.md`
  - `TEST_REPORT_V2.md`
  - `AGENT_WORKFLOW.md`
- 创建 `specs/` 规范目录和 `tasks/worklogs/`
- 将 `frontend-v2/SPEC.md`、`frontend-v2/tasks/PROGRESS.md`、`frontend-v2/tasks/ARCHITECTURE.md` 标记为历史参考

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

## 2026-04-30 FULL-001 回标文件与技术建议书闭环

- 新增 `bid_template_service.py`：统一清洗回标模板文件，按文件名/模板包路径归类为商务、技术、方案/报价或其他，过滤招标文件并去除重复路径。
- 修改 `bid_template.py` 与 `project_service.get_project_bid_progress`：上传和读取模板清单时均执行清洗；回标完成情况优先展示 `Project.bid_template_files`，不再把招标文件和业务文档模板混入文件目录。
- 修改 `proposal_editor.py` / `proposal_service.py`：新增 `GET /api/v1/proposal-editor/{project_id}/export/docx`，支持技术建议书 Word 导出；LLM 不可用时使用结构化兜底内容保证生成链路可闭环。
- 修改 `ProposalEditor.vue` / `proposal.ts`：补齐生成任务轮询、草稿保存、重新打分、一键确认、Word 导出、项目路由自动选择和错误/成功反馈。
- 修改 `TenderDetail.vue`：一键下载接入最新回标生成任务 Word 导出。
- 验证：`py_compile` 通过；`npm run build` 通过；临时 SQLite smoke 覆盖回标模板过滤去重、技术建议书生成/编辑/rescore/confirm/export。
