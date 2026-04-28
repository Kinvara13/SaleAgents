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

## 2026-04-26 定价策略 P2-A / F11 推进

- **F11 多轮迭代博弈**:
  - 扩展 `backend-v2/app/schemas/bidding_game.py`：
    - `SimulationConfig.method` 新增 `iterative`
    - 新增 `iterative_rounds`、`learning_rate`、`exploration_rate`、`convergence_threshold`
    - 新增 `IterationRoundResult`、`AgentStrategyEvolution`、`IterativeGameResult`
    - `BiddingGameSimulateResponse` 正式启用 `iterative_result`
  - 扩展 `backend-v2/app/services/bidding_game_engine.py`：
    - 新增 `_run_iterative_game()` 多轮迭代博弈主流程
    - 新增 `_update_discount_anchor()`，按输赢、利润和策略偏好动态更新折扣锚点
    - `raw_simulation_data` 新增 `iterative_rounds`、`strategy_evolutions`
    - 修正我方总分计算逻辑，改为使用 `our_agent.tech_score`
    - 增加关键日志，便于后续联调定位
  - 扩展 `backend-v2/app/models/pricing.py` 与 `app/services/pricing_persistence.py`，支持保存 `iterative_result`
  - 新增 Alembic 迁移 `f11c2a8e9b7d_add_iterative_result_to_bidding_game.py`

- **前端接入**:
  - 扩展 `frontend-v2/src/services/biddingGame.ts` 的 iterative 请求/响应类型
  - 修改 `BiddingGameSimulator.vue`：
    - 新增 iterative 模式切换
    - 新增迭代参数配置区
    - 新增收敛摘要、策略演化表、轮次明细
  - 修改 `GameReplayCharts.vue`：
    - 新增多轮迭代趋势图
    - 新增策略演化轨迹图

- **文档同步**:
  - 更新 `specs/pricing-strategy-spec.md`：
    - 修正 F5 状态漂移
    - 将 F11 标记为“已完成”
    - 新增 Phase 3 / P2-A 实施进展、验证结果和后续计划
  - 更新 `FEATURE_MATRIX_V2.md`、`TASK_BOARD_V2.md`、`TEST_PLAN_V2.md`、`TEST_REPORT_V2.md`，登记 F11 联调结果与收口状态

- **验证记录**:
  - `python3 -m compileall app` 通过
  - `frontend-v2` 执行 `npm run build` 通过
  - IDE 诊断未发现新增错误
  - 补装最小依赖后，`python3.11` 直接调用 `simulate_bidding_game()` 成功，返回示例包含 `rounds=8`、`convergence_round=3`
  - 使用内存 SQLite 调用 `save_bidding_game_simulation()` 成功，`iterative_result` 已可持久化且 `rounds=8`
  - 直接调用 endpoint `simulate_bidding_game()` 成功，确认 route 处理层可返回结果并写库
  - 启动最小 FastAPI 服务后，`POST /api/v1/auth/login` + `POST /api/v1/bidding-game/simulate` 真实 HTTP 请求通过，确认 `iterative_result` 返回正常且可写入 `/tmp/saleagents_f11_http.db`
  - 正式环境仍需执行 Alembic 迁移，并补一次真实数据库发布后回归

## 2026-04-26 定价策略 P2-B+C / F13 + F14 推进

- **F13 历史数据学习**:
  - 扩展 `backend-v2/app/schemas/bidding_game.py`：新增 `BiddingGameHistoryLearningRequest` / `CompetitorHistoryProfile` / `BiddingGameHistoryLearningResponse`
  - 扩展 `backend-v2/app/services/pricing_persistence.py`：新增 `build_competitor_history_profiles()`，从 `competitor_predictions`（手工历史折扣 + 情报点估计）和 `bidding_game_simulations`（Agent 先验均值 + 迭代轮次样本）聚合四个来源的折扣样本，输出各竞对的 `discount_belief_mean` / `discount_belief_std` / `sample_count` / `source_breakdown`
  - 新增 `POST /api/v1/bidding-game/history-learning` 端点
  - 前端 `CompetitorIntelligence.vue` 新增"从历史数据学习"按钮，`PricingStrategy.vue` 传递 `project_id` 并将画像转发到博弈沙盘
  - `BiddingGameSimulator.vue` 新增 `applyHistoryProfiles()` 用于回填竞对 Agent 的先验参数
  - 验证：命令行直验返回 `records=2 matched=2 axin:5:0.2:0.02;zsoft:4:0.255:0.02`
  - 阻塞：完整 `pytest` 因环境缺 `python-docx` 依赖暂未通过

- **F14 协同博弈**:
  - 扩展 `backend-v2/app/schemas/bidding_game.py`：新增 `AllianceConfig` / `CoalitionConfig` / `CoalitionAgentEffect` / `CoalitionResult`；`BiddingGameSimulateRequest` 新增可选 `coalition_config`；`BiddingGameSimulateResponse` 新增 `coalition_result`
  - 扩展 `backend-v2/app/services/bidding_game_engine.py`：
    - 新增 `_resolve_alliance_map()` 解析联盟配置并标记 Agent 的 alliance_id/alliance_role
    - 新增 `_apply_coalition_to_discount()` 实现 3 种协同策略（`high_bid_escort` 高报价陪标 / `price_padding` 价格垫 / `bracket` 区间包裹）
    - `_run_single_simulation()`、`_monte_carlo_simulation()`、`_analyze_sensitivity()`、`_find_nash_equilibrium()` 全线穿透 alliance_map
    - `_run_iterative_game()` 每轮采样后协调联盟折扣 + 每轮锚点更新后重同步陪标方锚点
    - `simulate_bidding_game()` 统一构建联盟映射并产出 `CoalitionResult`
  - 扩展 `backend-v2/app/models/pricing.py`：`BiddingGameSimulation` 新增 `coalition_config` JSON 字段
  - `save_bidding_game_simulation()` 自动保存 `coalition_result`
  - Alembic 迁移：`a4e2d8f1b3c7_add_coalition_config_to_bidding_game.py`
  - 前端 `biddingGame.ts`：新增 AllianceConfig / CoalitionConfig / CoalitionAgentEffect / CoalitionResult 类型
  - 前端 `BiddingGameSimulator.vue`：新增可折叠"协同博弈配置"面板（多联盟管理、主攻方/陪标方选择、策略类型和折扣间距）、amber 色调联盟结果展示面板
  - 验证：`compileall` + `npm run build` 通过；最小运行态返回 `coalition_result.alliance_count=1, agent_effects 含 leader/supporter`；不带联盟配置时 `coalition_result=None` 向后兼容

- **文档同步**:
  - 更新 `specs/pricing-strategy-spec.md`：F13/F14 状态标记为"已完成"，新增 7.4.3 和 7.4.4 实施详情章节
  - 更新 `specs/api-contract-spec.md`：登记 `POST /api/v1/bidding-game/history-learning` 和 `coalition_config` 扩展
  - 更新 `FEATURE_MATRIX_V2.md`、`TASK_BOARD_V2.md`、`TEST_PLAN_V2.md`、`TEST_REPORT_V2.md`，登记 F13+F14 实现结论与验证结果

## 2026-04-26 定价策略 P2-B / F13 推进

- **F13 历史数据学习**:
  - 扩展 `backend-v2/app/schemas/bidding_game.py`：
    - 新增 `BiddingGameHistoryLearningRequest`
    - 新增 `CompetitorHistoryProfile`
    - 新增 `BiddingGameHistoryLearningResponse`
  - 扩展 `backend-v2/app/services/pricing_persistence.py`：
    - 新增 `_normalize_competitor_name()` 与 `_safe_discount_value()`
    - 新增 `build_competitor_history_profiles()`，聚合 `manual_historical_input` / `intel_prediction` / `agent_prior_mean` / `iterative_round`
    - 修正竞对识别逻辑，按 `agent_configs` 首项排除我方 Agent，避免名称变更导致己方样本串入历史学习
  - 扩展 `backend-v2/app/api/v1/endpoints/bidding_game.py`：
    - 新增 `POST /api/v1/bidding-game/history-learning`
    - 增加请求与完成日志，便于后续排查项目级样本聚合问题

- **前端接入**:
  - 扩展 `frontend-v2/src/services/biddingGame.ts` 的历史学习请求/响应类型与接口调用
  - 修改 `CompetitorIntelligence.vue`：
    - 新增“从历史数据学习”按钮
    - 将当前项目和竞对名单传入历史学习接口
  - 修改 `PricingStrategy.vue`：
    - 补齐 `project_id` 透传
    - 新增 `onApplyHistoryLearning()` 联动博弈沙盘
    - 修复 `window.setTimeout` 导致的 Vue 类型诊断问题
  - 修改 `BiddingGameSimulator.vue`：
    - 新增 `applyHistoryProfiles()`
    - 支持回填竞对 `discount_belief_mean` / `discount_belief_std`
    - 增加关键 debug 日志

- **验证记录**:
  - `frontend-v2` 执行 `npm run build` 通过
  - IDE 诊断未发现新增错误
  - 基于内存 SQLite 直接调用 `learn_bidding_game_history()` 成功，确认返回 `total_records_scanned=2`、`matched_competitor_count=2`
  - 新增 `backend-v2/tests/test_bidding_game_history_learning.py` 回归用例
  - 完整 `pytest` 当前受仓库缺少 `python-docx` 阻塞；该阻塞源于既有 `review` 模块依赖，不属于本次 F13 代码回归失败
