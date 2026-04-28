# SaleAgents v2 API 契约规范

更新日期：2026-04-26  
真实注册入口：`backend-v2/app/api/router.py`

## 1. 契约原则

- 以当前已注册路由为准
- 任何公开 API 变更先更新本文件
- 兼容接口必须明确标注 `legacy`

## 2. 主要接口分组

### 认证

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

当前结论：

- `login` 已运行态通过

### 项目

- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`
- `PATCH /api/v1/projects/{project_id}`
- `DELETE /api/v1/projects/{project_id}`
- `POST /api/v1/projects/{project_id}/confirm`

当前结论：

- 列表、创建已运行态通过

### 招标信息

- `GET /api/v1/tenders`
- `POST /api/v1/tenders`
- `GET /api/v1/tenders/{tender_id}`
- `POST /api/v1/tenders/{tender_id}/decision`
- `POST /api/v1/tenders/{tender_id}/upload`

当前结论：

- 列表已运行态通过
- 决策与上传待补运行态验证

### 解析

- `POST /api/v1/parsing/{project_id}/upload`
- `GET /api/v1/parsing/{project_id}/sections`
- `GET /api/v1/parsing/{project_id}/sections/{section_id}`
- `PATCH /api/v1/parsing/{project_id}/sections/{section_id}`

当前结论：

- `sections` 列表已返回空数组
- 真实样本上传与章节详情待回归

### 商务文档

- `GET /api/v1/projects/{project_id}/business-documents`
- `GET /api/v1/projects/{project_id}/business-documents/{doc_id}`
- `PATCH /api/v1/projects/{project_id}/business-documents/{doc_id}`

### 技术文档

- `GET /api/v1/projects/{project_id}/technical-documents`
- `GET /api/v1/projects/{project_id}/technical-documents/{doc_id}`
- `PATCH /api/v1/projects/{project_id}/technical-documents/{doc_id}`

### 方案建议书

- `GET /api/v1/projects/{project_id}/proposal-plans`
- `GET /api/v1/projects/{project_id}/proposal-plans/{doc_id}`
- `PATCH /api/v1/projects/{project_id}/proposal-plans/{doc_id}`

### 技术案例

- `GET /api/v1/projects/{project_id}/technical-cases`
- `GET /api/v1/projects/{project_id}/technical-cases/{case_id}`
- `POST /api/v1/projects/{project_id}/technical-cases`
- `PATCH /api/v1/projects/{project_id}/technical-cases/{case_id}`
- `DELETE /api/v1/projects/{project_id}/technical-cases/{case_id}`
- `GET /api/v1/projects/{project_id}/technical-cases-search/search`

### 技术建议书

- `POST /api/v1/proposal-editor/{project_id}/generate`
- `GET /api/v1/proposal-editor/{project_id}/sections`
- `GET /api/v1/proposal-editor/{project_id}/sections/{section_id}`
- `PATCH /api/v1/proposal-editor/{project_id}/sections/{section_id}`
- `POST /api/v1/proposal-editor/{project_id}/score`
- `POST /api/v1/proposal-editor/{project_id}/rescore`
- `POST /api/v1/proposal-editor/{project_id}/confirm`
- `GET /api/v1/proposal-editor/{project_id}/scoring-rules`

当前结论：

- `generate`、`score` 已运行态通过

### 报价

- `POST /api/v1/pricing/calculate`
- `POST /api/v1/bidding-game/simulate`
- `POST /api/v1/bidding-game/history-learning`
- `POST /api/v1/tech-score/evaluate`
- `POST /api/v1/competitor-intel/predict`

当前结论：

- 运行态通过
- `tax_rate` 当前要求 `<= 1`
- `risk_factor` 当前按整数校验
- `bidding-game/simulate` 已支持 `simulation_config.method = iterative`
- `bidding-game/history-learning` 已支持按 `project_id` 聚合历史样本并返回竞对先验画像

#### `POST /api/v1/bidding-game/simulate`

请求关键字段：

- `scenario`
- `our_agent`
- `competitor_agents`
- `simulation_config.n_simulations`
- `simulation_config.method`: `monte_carlo | bayesian | iterative`
- `simulation_config.iterative_rounds`: iterative 模式有效，范围 `5-100`
- `simulation_config.learning_rate`: iterative 模式有效，范围 `0.01-1`
- `simulation_config.exploration_rate`: iterative 模式有效，范围 `0-0.5`
- `simulation_config.convergence_threshold`: iterative 模式有效，范围 `0.001-0.1`

响应新增字段：

- `iterative_result.rounds`
- `iterative_result.strategy_evolutions`
- `iterative_result.convergence_round`
- `iterative_result.final_optimal_discount`
- `iterative_result.final_win_probability`
- `iterative_result.final_expected_profit`
- `raw_simulation_data.iterative_rounds`
- `raw_simulation_data.strategy_evolutions`

当前结论：

- 契约层与前端 TypeScript 类型已同步
- 代码层已接入持久化字段 `bidding_game_simulations.iterative_result`
- `python3.11` 服务层烟测已通过，`simulate_bidding_game()` 可返回 `iterative_result`
- 内存 SQLite 持久化烟测已通过，`iterative_result` 可成功写入 `bidding_game_simulations`
- 真实 HTTP 烟测已通过：`POST /api/v1/auth/login` + `POST /api/v1/bidding-game/simulate` 可完成鉴权、返回 `iterative_result`，并写入 `/tmp/saleagents_f11_http.db`

#### `POST /api/v1/bidding-game/history-learning`

请求关键字段：

- `project_id`: 可选；传入后仅聚合当前项目下的历史记录
- `competitor_names`: 目标竞对列表；为空时返回全部匹配竞对画像
- `limit`: 单类历史记录扫描上限，范围 `1-200`

响应关键字段：

- `profiles[].name`
- `profiles[].discount_belief_mean`
- `profiles[].discount_belief_std`
- `profiles[].sample_count`
- `profiles[].source_breakdown`
- `total_records_scanned`
- `matched_competitor_count`
- `message`

当前结论：

- 契约层与前端 TypeScript 类型已同步
- 后端会同时聚合 `competitor_predictions` 与 `bidding_game_simulations` 两类历史记录
- 输出样本来源已细分为 `manual_historical_input` / `intel_prediction` / `agent_prior_mean` / `iterative_round`
- 最小路由处理层烟测已通过：基于内存 SQLite 直接调用 `learn_bidding_game_history()`，可返回 `matched_competitor_count=2`
- 仓库当前缺少 `python-docx`，完整 `pytest` 回归会在加载 `app.main` 时被现有 review 模块依赖阻塞，需补环境后再执行

### 用户与角色

- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`
- `GET /api/v1/users/roles/list`

当前结论：

- 用户创建、角色列表已运行态通过

### 聊天

- `POST /api/v1/chat/{project_id}/message`
- `GET /api/v1/chat/{project_id}/history`
- `POST /api/v1/chat/{project_id}/context`
- `DELETE /api/v1/chat/{project_id}/history`

当前结论：

- `DELETE history` 已运行态通过

### 系统设置

#### legacy 单配置

- `GET /api/v1/settings/ai-config`
- `PATCH /api/v1/settings/ai-config`

#### 当前多配置

- `GET /api/v1/settings/ai-configs`
- `POST /api/v1/settings/ai-configs`
- `PATCH /api/v1/settings/ai-configs/{config_id}`
- `DELETE /api/v1/settings/ai-configs/{config_id}`
- `POST /api/v1/settings/ai-configs/{config_id}/activate`

#### 素材与规则

- `GET /api/v1/settings/materials`
- `POST /api/v1/settings/materials/upload`
- `GET /api/v1/settings/rules`
- `POST /api/v1/settings/rules`

当前结论：

- `rules` 创建已通过
- `ai-config` 与 `ai-configs` 目前都被数据库 schema 漂移阻塞

## 3. 已知契约漂移

- 历史文档中未登记 `pricing` 域的 `tech-score` / `competitor-intel` / `bidding-game` 三条接口，现已补录
- `bidding-game/simulate` 已完成真实 HTTP 联调；正式环境仍需执行 Alembic 迁移并做一次环境回归

## 4. 契约变更流程

1. 先修改本文件
2. 再修改后端代码
3. 再修改前端调用
4. 最后更新 `TEST_PLAN_V2.md` 与 `TEST_REPORT_V2.md`
