# SaleAgents v2 测试报告

生成日期：2026-04-21  
测试范围：根目录统一审计产物对应的静态检查 + 最小运行态烟测  
测试基线：`backend-v2`、`frontend-v2`

> 注：本报告为 2026-04-21 基线版本。后续修正见 "7. 2026-04-23 运行态验证"。

## 1. 环境结论

- 默认 `python3`：`3.9`
- 可用运行版本：`python3.11`
- 前端构建：`npm run build` 通过
- 浏览器自动化：仓库中未发现现成框架

关键环境发现：

- 使用默认 `python3` 启动 `backend-v2` 会在导入阶段失败，因为代码使用了 Python 3.10+ 的联合类型语法 `str | None`
- 使用 `python3.11` 启动后，后端可正常提供大部分 API

## 2. 修正历史结论

相较于旧的 `memory-bank/TEST_REPORT.md`，本轮确认以下结论已经变化：

- `DELETE /api/v1/chat/{project_id}/history`：当前返回 `200`，旧报告中的 `405` 已失效
- `POST /api/v1/users`：当前返回 `201`，旧报告中的 bcrypt 500 结论已失效
- `POST /api/v1/proposal-editor/{project_id}/generate`：当前可返回章节列表，旧报告中的固定 500 结论已失效
- `POST /api/v1/settings/rules`：当前可返回 `201`，旧报告中“接口设计异常”的结论已过时

## 3. 后端运行态烟测

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| `POST /api/v1/auth/login` | 通过 | 返回 access_token / refresh_token |
| `DELETE /api/v1/chat/test_project/history` | 通过 | 返回 `{"message":"Chat history cleared"}` |
| `GET /api/v1/projects` | 通过 | 返回项目列表 |
| `POST /api/v1/projects` | 通过 | 返回新建项目 `proj_9e7d...` |
| `GET /api/v1/tenders` | 通过 | 返回招标信息列表 |
| `GET /api/v1/users/roles/list` | 通过 | 返回角色与权限列表 |
| `POST /api/v1/users` | 通过 | 返回新建用户对象 |
| `POST /api/v1/settings/rules` | 通过 | 返回新规则对象 |
| `GET /api/v1/projects/{id}/business-documents` | 通过 | 返回 13 个商务文档模板 |
| `GET /api/v1/projects/{id}/technical-documents` | 通过 | 返回技术文档模板列表 |
| `GET /api/v1/projects/{id}/proposal-plans` | 通过 | 返回 4 个方案建议书模板 |
| `GET /api/v1/projects/{id}/technical-cases` | 通过 | 返回空列表，接口可调用 |
| `POST /api/v1/proposal-editor/{id}/generate` | 通过 | 返回生成章节列表 |
| `POST /api/v1/proposal-editor/{id}/score` | 通过 | 返回 `sections` + `total_score` |
| `POST /api/v1/pricing/calculate` | 通过 | 使用符合 schema 的 payload 成功返回报价结果 |

## 4. 当前失败/阻塞项

| 检查项 | 结果 | 根因 |
| --- | --- | --- |
| `GET /api/v1/health` | 失败，404 | `health.py` 定义了路由，但 `backend-v2/app/api/router.py` 未注册 `health.router` |
| `GET /api/v1/settings/ai-config` | 失败，500 | SQLite 表 `ai_configs` 缺少 `name` 列，属于数据库 schema 漂移 |
| `GET /api/v1/settings/ai-configs` | 失败，500 | 同上 |
| `python3 -m uvicorn app.main:app` | 失败 | 默认 `python3` 为 3.9，不满足代码语法要求 |

## 5. 前端静态检查结果

### 通过项

- `frontend-v2` 构建通过
- 路由表存在并可覆盖主流程页面
- 大多数核心页面已经有对应 service 或 API 调用入口

### 关键问题

#### `ProposalEditor.vue`

- 把 axios 响应当作 fetch `Response` 使用：
  - 读取 `res.ok`
  - 调用 `res.json()`
- 多处动态路径写成普通字符串，如 `'/proposal-editor/${projectId}/score'`
- 影响：技术建议书生成、评分、重评分、确认、详情获取在页面侧大概率失效

#### `UserManagement.vue`

- `PATCH /users/${id}`、`DELETE /users/${id}` 等路径写成普通字符串
- 同样把 axios 响应当作 fetch 使用
- 影响：用户编辑、删除、启停用在页面侧不可靠

#### `RoleManagement.vue`

- 仍按 fetch 风格处理 axios 响应
- 影响：角色列表页面数据加载逻辑不可靠

#### `SystemSettings.vue`

- 页面契约对的是 `/settings/ai-configs`，但当前接口被数据库 schema 阻塞
- 规则区基本可用，AI 配置区当前不可用

## 6. 覆盖边界

本轮已经完成：

- 根目录审计文档落地
- 当前代码静态覆盖梳理
- Python 3.11 环境下的后端最小烟测
- 前端构建验证

本轮未完成：

- 页面级人工走查
- 浏览器自动化验证
- 文件上传类真实样本回归
- 解析章节、星标项、素材库自动填充和人工确认节点的端到端回归

## 7. 2026-04-23 运行态验证

本轮验证基于 2026-04-21 基线，补充了 BE-001 至 QA-004 的修复验收。

### 7.1 修正的失败/阻塞项

| 检查项 | 结果 | 修复记录 |
| --- | --- | --- |
| `GET /api/v1/health` | 已通过，200 | BE-001：在 `router.py` 注册了 `health.router`，并在 `test_api_v2.py` 补 smoke 用例 |
| `GET /api/v1/settings/ai-config` | 已通过，200 | BE-002：执行 `ALTER TABLE ai_configs ADD COLUMN name VARCHAR(128) NOT NULL DEFAULT '未命名配置'` 修复 schema 漂移 |
| `GET /api/v1/settings/ai-configs` | 已通过，200 | 同上 |

### 7.2 页面级走查结果（QA-002）

| 页面 | 检查项 | 结果 | 备注 |
| --- | --- | --- | --- |
| 用户管理 (`/users`) | 新增、编辑角色、启用/禁用、删除功能正常，表格渲染无报错 | Passed | Axios/Fetch 混用修复完成（FE-002） |
| 角色管理 (`/roles`) | 列表加载成功，角色权限展示正确 | Passed | API 返回解析修复完成（FE-002） |
| 系统设置 (`/settings`) | AI配置（含默认激活）、规则管理、素材库的增删改查及错误态 | Passed | 已补充字段非空校验与 alert 错误反馈（FE-003） |
| 标前评估 (`/tender-info/:id`) | "投标"功能（保证金、项目类型填写）正常，支持上传标书文件并创建项目 | Passed | 填写的字段正确存入 `tenders` 表 |
| 项目详情 (`/project/:id`) | "商务文档"、"技术文档"、"方案建议书" Tab 下的 `AI 自动填充` 可用，加载态正常 | Passed | Vue Linter 问题修复，接口联调成功（FE-005） |
| 标书列表 (`/bid-list`) | 列表展示最新生成的项目，跳转路由不再报 404 | Passed | 原 `/projects` 路由跳转已修复为 `/bid-list`（FE-004） |

### 7.3 新增后端能力验收

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| `python -c "from app.main import app"` | 通过 | 导入无报错（QA-004） |
| `GET /api/v1/health` | 通过 | 返回 200，`{"status":"ok"}`（QA-004） |
| `项目工作台列表` | 通过 | `get_projects_list` 基于真实 DB 数据返回，无 FAKE_PROJECTS（BE-010） |
| `商务文档生成` | 通过 | 生成参数从 Project/Tender/ParsingSection 实时抽取，无 `str` 占位符（BE-011） |

### 7.4 仍然未覆盖

- 浏览器自动化验证（QA-003 选型 Playwright，尚未实施）
- 文件上传类真实样本回归（需任务 3 补充）
- 解析章节、星标项、素材库自动填充和人工确认节点的端到端回归

## 8. 2026-04-26 F11 多轮迭代博弈验证

本轮补充验证 `F11` 多轮迭代博弈，覆盖服务层、持久化层、路由处理层和真实 HTTP 请求。

### 8.1 验证结果

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| `simulate_bidding_game()` 服务层调用 | 通过 | `python3.11` 直接调用后返回 `iterative_result`，示例包含 `rounds=8`、`convergence_round=3` |
| `save_bidding_game_simulation()` 持久化 | 通过 | 基于内存 SQLite 保存成功，`iterative_result` 已落库且 `rounds=8` |
| endpoint `simulate_bidding_game()` | 通过 | 直接调用路由处理函数后返回结果，并成功写入 `bidding_game_simulations` |
| `POST /api/v1/auth/login` | 通过 | 最小 FastAPI 服务下成功返回 bearer token |
| `POST /api/v1/bidding-game/simulate` | 通过 | 真实 HTTP 请求返回 `iterative_result.rounds=8`、`convergence_round=3`，并写入 `/tmp/saleagents_f11_http.db` |

### 8.2 本轮结论

- F11 多轮迭代博弈的前后端接入、运行态验证和 SQLite 持久化验证已完成
- 当前仅剩正式环境 Alembic 迁移执行与发布后回归，属于环境发布动作，不再阻塞功能完成状态

## 9. 2026-04-26 F13 历史数据学习验证

本轮补充验证 `F13` 历史数据学习，覆盖前端构建、最小路由处理层和历史样本聚合规则。

### 9.1 验证结果

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| `frontend-v2 npm run build` | 通过 | 新增历史学习入口、参数回填和类型调整后构建成功 |
| IDE 诊断 | 通过 | `CompetitorIntelligence.vue`、`BiddingGameSimulator.vue`、`PricingStrategy.vue`、`biddingGame.ts`、`bidding_game.py`、`pricing_persistence.py` 无新增诊断错误 |
| endpoint `learn_bidding_game_history()` | 通过 | 基于内存 SQLite 直接调用路由处理函数后，返回 `total_records_scanned=2`、`matched_competitor_count=2` |
| 历史样本聚合规则 | 通过 | 已覆盖 `manual_historical_input`、`intel_prediction`、`agent_prior_mean`、`iterative_round` 四类来源，并输出 `sample_count` 与 `source_breakdown` |
| 回归测试文件 | 已新增 | 新增 `backend-v2/tests/test_bidding_game_history_learning.py`，用于锁定均值、标准差和来源统计 |

### 9.2 环境阻塞

| 检查项 | 结果 | 根因 |
| --- | --- | --- |
| `PYTHONPATH=... pytest tests/test_bidding_game_history_learning.py tests/test_smoke.py` | 阻塞 | 仓库当前环境缺少 `python-docx`，`pytest` 在加载 `app.main` 时被既有 `review` 模块依赖阻塞，非 F13 代码回归失败 |

### 9.3 本轮结论

- F13 历史数据学习已完成并经验证，完整 `pytest` 仍受 `python-docx` 环境依赖阻塞

## 10. 2026-04-26 F14 协同博弈验证

本轮补充验证 `F14` 协同博弈，覆盖 schema、引擎、持久化和前端入口。

### 10.1 验证结果

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| `POST /api/v1/bidding-game/history-learning` | 通过 | 最小运行态验证：内存 SQLite 插入 `CompetitorPrediction` + `BiddingGameSimulation` 后调端点，返回 `records=2 matched=2`，profiles 含 `sample_count/source_breakdown` |
| `POST /api/v1/bidding-game/simulate` (coalition) | 通过 | 带 `coalition_config` (alliance_count=1, high_bid_escort) 的编译后直调成功，返回 `coalition_result.alliance_count=1`，agent_effects 含 leader/supporter 角色标注；不带 `coalition_config` 时 `coalition_result=None`，向后兼容 |

### 10.2 本轮结论

- F14 协同博弈的 schema、引擎、持久化和前端入口已完成并经验证
- F13 历史数据学习已完成并经验证，完整 `pytest` 仍受 `python-docx` 环境依赖阻塞
