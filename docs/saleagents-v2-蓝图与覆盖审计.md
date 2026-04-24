# SaleAgents v2 蓝图与覆盖审计

更新时间：2026-04-24  
审计范围：`backend-v2/`、`frontend-v2/`、`specs/`、`memory-bank/`  
证据优先级：运行态验证 > 当前代码 > 历史文档

---

## 1. 功能蓝图（v2）

### 1.1 主流程蓝图

```text
招标信息进入
-> 投标判断（投/不投、保证金、项目类型）
-> 上传标书并触发解析
-> 项目台账与工作台
-> 商务文档/技术文档/方案建议书处理
-> 技术建议书生成与评分（generate/score/rescore/confirm）
-> 报价计算
-> 人工确认与导出
```

### 1.2 能力域拆分

- 招标信息域（F049-F051）：列表、详情、投标决策、上传触发项目。
- 项目与标书域（F052-F053）：项目 CRUD、我的项目、节点工作台。
- 商务文档域（F054-F066）：商务模板清单、详情、编辑回写。
- 技术文档域（F067-F075）：技术模板清单、详情、编辑回写。
- 方案建议书域（F076-F079）：方案清单、详情、二次计算入口。
- 报价域（F080）：报价计算接口和页面联动。
- 技术案例域（F081）：技术案例 CRUD + 搜索。
- 技术建议书域（F082）：生成、评分、重评分、确认闭环。
- 平台支撑域：认证、用户角色、系统设置、聊天、健康检查、标前评估。

### 1.3 当前完成度（按功能矩阵）

来源：`memory-bank/FEATURE_MATRIX_V2.md`

- 非 demo 功能项共 `34` 条。
- `已完成`：`1`（F080 报价策略）。
- `部分完成`：`33`。
- 闭环完成率（严格口径）约 `2.9%`（`1/34`）。

### 1.4 当前主缺口（P0/P1）

- P0 高优先缺口集中在：真实样本上传解析、人工确认节点、重算链路、素材自动回填、页面级端到端验收。
- 多数模块“接口可调用 + 页面可进入”，但“业务闭环可验收”证据不足。
- 结论上不建议以“页面存在或接口存在”替代“功能完成”。

---

## 2. 模块路径与职责

## 2.1 后端路径（FastAPI）

- 路由注册中心：`backend-v2/app/api/router.py`
- endpoint 层：`backend-v2/app/api/v1/endpoints/*.py`
- service 层：`backend-v2/app/services/*.py`
- schema 层：`backend-v2/app/schemas/*.py`
- model 层：`backend-v2/app/models/*.py`
- DB 与迁移：`backend-v2/app/db/`、`backend-v2/alembic/`

关键路由分组（已注册）：

- `health`、`auth`
- `projects`
- `tenders`
- `parsing`
- `business-documents`
- `technical-documents`
- `proposal-plans`
- `proposal-editor`
- `technical-cases`
- `pricing`
- `users`
- `settings`
- `chat`
- `review`
- `pre-evaluation`

## 2.2 前端路径（Vue3 + Vite）

- 路由入口：`frontend-v2/src/router/index.ts`
- 页面目录：`frontend-v2/src/views/*.vue`
- 服务封装：`frontend-v2/src/services/*.ts`
- 全局 API 客户端：`frontend-v2/src/services/api.ts`
- 布局与组件：`frontend-v2/src/layouts/`、`frontend-v2/src/components/`
- 鉴权状态：`frontend-v2/src/store/auth.ts`

核心页面分组：

- 招标入口：`TenderInfoList.vue`、`TenderInfoDetail.vue`
- 项目工作台：`BidList.vue`、`ProjectCreate.vue`、`TenderDetail.vue`
- 技术建议书：`ProposalEditor.vue`
- 报价：`PricingStrategy.vue`
- 系统能力：`Login.vue`、`UserManagement.vue`、`RoleManagement.vue`、`SystemSettings.vue`

## 2.3 工程与规范路径

- 规范入口：`specs/README.md`
- 契约规范：`specs/api-contract-spec.md`
- 工程规范：`specs/engineering-spec.md`
- 测试规范：`specs/testing-spec.md`
- 治理规范：`specs/task-governance-spec.md`
- 事实矩阵与测试记录：`memory-bank/FEATURE_MATRIX_V2.md`、`memory-bank/PAGE_COVERAGE_V2.md`、`memory-bank/TEST_REPORT_V2.md`

---

## 3. 测试完整度评估

## 3.1 已覆盖内容

来源：`memory-bank/TEST_REPORT_V2.md`、`memory-bank/PAGE_COVERAGE_V2.md`

- 环境基线：Python 3.11 可运行，前端可构建。
- 后端 smoke：认证、项目、招标、文档列表、技术建议书 generate/score、报价等关键接口已有通过记录。
- 修复项复验：健康检查与 AI 配置 schema 漂移问题已有修复验证记录（2026-04-23）。
- 页面走查：用户管理、角色管理、系统设置、标前评估、项目详情、标书列表有一轮人工走查记录。

## 3.2 未覆盖内容（当前风险）

- 浏览器自动化尚未落地（仅有选型，没有稳定自动回归）。
- 文件上传/解析类“真实样本”端到端回归不足。
- 解析章节、星标项、素材库自动填充、人工确认节点等关键链路缺系统性验收。
- 页面覆盖矩阵大量仍为“部分覆盖”，说明静态接线多、闭环验收少。

## 3.3 完整度结论（分层）

- API 烟测完整度：中等（关键主干已测，但非 happy path 与复杂业务链不足）。
- 页面交互完整度：偏低（多数为部分覆盖）。
- 端到端业务完整度：偏低（真实样本+人工确认闭环缺口较大）。
- 自动化完整度：低（尚未建立稳定自动化回归体系）。

## 3.4 建议的下一轮测试优先级

1. 真实样本上传 -> 解析 -> 文档填充 -> 评分/重评分 -> 确认 全链路回归（P0）。
2. 招标处理与项目工作台节点闭环（保证金、项目类型、确认节点）回归（P0）。
3. 页面错误态与异常态（接口失败、鉴权过期、空数据）系统走查（P1）。
4. 固化最小自动化：登录、项目创建、报价、建议书生成评分四条主路径（P1）。

---

## 4. 对齐口径说明

- 本文口径优先采用 v2 规范与 `memory-bank` 证据，不以历史 `docs` 的设计态“应有能力”直接判定“已完成”。
- 若后续发生公开 API、页面主流程、数据库 schema、测试门槛变更，需同步更新：
  - `specs/` 对应规范文件
  - `memory-bank/CHANGE_LOG_V2.md`
  - 本文档

