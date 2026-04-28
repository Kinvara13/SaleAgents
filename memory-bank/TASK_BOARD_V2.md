# SaleAgents v2 任务看板

更新日期：2026-04-26  
说明：所有后续工作先在本表认领，再进入实现。状态建议使用：`todo` / `in_progress` / `blocked` / `review` / `done`

| task_id | 来源功能点 | 问题类型 | 目标结果 | owner | status | depends_on | 验收标准 | 记录文件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUDIT-001 | F049-F082 | 审计 | 建立 34 行功能矩阵、页面覆盖矩阵、测试计划/报告 | Audit Agent | done | 无 | 根目录文档落地并可追溯到代码/运行态证据 | `memory-bank/agent-worklogs/audit-agent.md` |
| SPEC-001 | 全局 | 规范 | 创建 `specs/` 目录及 6 份规范文件 | Spec Agent | done | AUDIT-001 | `specs/` 首批规范齐全，可直接指导实现 | `memory-bank/agent-worklogs/spec-agent.md` |
| SPEC-002 | 全局 | 规范 | 将 `frontend-v2/SPEC.md` 与 `frontend-v2/memory-bank/*` 标记为历史参考 | Spec Agent | done | SPEC-001 | 旧文档文件头清楚标记迁移入口 | `memory-bank/agent-worklogs/spec-agent.md` |
| BE-001 | 支撑能力-健康检查 | 后端 | 在 `backend-v2/app/api/router.py` 注册健康检查路由并补 smoke 用例 | Backend Agent | done | AUDIT-001 | `GET /api/v1/health` 返回 200 且纳入测试报告 | `memory-bank/agent-worklogs/backend-agent.md` |
| BE-002 | 支撑能力-系统设置 | 后端 | 修复 `ai_configs` 数据库 schema 漂移，恢复 `/settings/ai-config*` | Backend Agent | done | AUDIT-001 | `/settings/ai-config` 与 `/settings/ai-configs` 均返回 200；旧数据可兼容 | `memory-bank/agent-worklogs/backend-agent.md` |
| FE-001 | F082 | 前端 | 修复 `ProposalEditor.vue` 中 axios/fetch 混用和动态路径问题 | Frontend Agent | done | AUDIT-001 | 页面可拉取章节、生成、评分、重评分、确认并正确展示结果 | `memory-bank/agent-worklogs/frontend-agent.md` |
| FE-002 | 支撑能力-用户/角色 | 前端 | 修复 `UserManagement.vue`、`RoleManagement.vue` 的 axios 用法与动态路径错误 | Frontend Agent | done | AUDIT-001 | 用户 CRUD 与角色列表在页面可正常工作 | `memory-bank/agent-worklogs/frontend-agent.md` |
| FE-003 | 支撑能力-系统设置 | 前端 | 对齐 `SystemSettings.vue` 与当前后端契约，补错误态和兼容提示 | Frontend Agent | done | BE-002 | AI 配置、规则、素材区的成功/失败态可见且可回归 | `memory-bank/agent-worklogs/frontend-agent.md` |
| FE-004 | F052-F053 | 前端 | 把 `ProjectCreate.vue` 和 `BidList.vue` 提升为真实项目工作台，而非仅基础 CRUD | Frontend Agent | done | AUDIT-001 | 页面展示项目重点字段、确认状态、文件清单和节点工作台 | `memory-bank/agent-worklogs/frontend-agent.md` |
|| FE-005 | F054-F079,F081 | 前端 | 补齐 `TenderDetail.vue` 的工作流信息、人工确认、重算反馈和错误态 | Frontend Agent | done | BE-003,BE-004,BE-005 | 文档区块能明确显示规则来源、当前状态、修改结果和待人工事项 | `memory-bank/agent-worklogs/frontend-agent.md` |
|| BE-003 | F050-F053 | 后端 | 完善招标处理字段：保证金、项目类型、拒绝原因、项目绑定和流程状态 | Backend Agent | done | AUDIT-001 | 决策和上传接口能完整承载 Excel 行 50-53 的业务字段 | `memory-bank/agent-worklogs/backend-agent.md` |
|| BE-004 | F052,F054-F075 | 后端 | 完成真实解析链路：上传标书 -> 章节 -> 星标项 -> 文档清单/详情 | Backend Agent | done | AUDIT-001 | 真实样本上传后能生成解析章节并驱动商务/技术文档区 | `memory-bank/agent-worklogs/backend-agent.md` |
|| BE-005 | F058,F069-F081 | 后端 | 把素材库/技术案例/评分规则真正接入商务文档、技术文档、方案建议书和案例检索 | Backend Agent | done | BE-002,BE-004 | 关键模板能根据素材和评分规则自动填充并回显规则说明 | `memory-bank/agent-worklogs/backend-agent.md` |
|| BE-010 | F050-F053,项目工作台 | 后端 | 项目工作台真实数据驱动：Project 模型扩展 + workspace_service 动态构建 + upload 触发解析 | Backend Agent | done | BE-003,BE-004 | `get_projects_list`、`get_project_detail`、`get_project_progress`、`get_statistics` 全部基于真实 DB 数据 | `memory-bank/agent-worklogs/backend-agent.md` |
|| BE-011 | F058,F069-F081 | 后端 | 商务文档真实参数填充：`generate_business_document` 从 Project/Tender/ParsingSection 实时抽取 | Backend Agent | done | BE-004,BE-010 | 无 `str` 占位符，所有生成参数均来源于实际数据 | `memory-bank/agent-worklogs/backend-agent.md` |
|| FE-007 | 项目列表页面 | 前端 | 前端契约对齐：扩展 Project 类型 + BidList 增加解析/节点状态展示 | Frontend Agent | done | BE-010 | `解析状态`、`节点工作台`列正确展示，快捷跳转可用 | `memory-bank/agent-worklogs/frontend-agent.md` |
|| QA-004 | 全局 | 测试 | 后端烟雾测试：导入检查 + health 端点验证 | QA Agent | done | BE-010,BE-011 | `python -c "from app.main import app"` 通过，`/api/v1/health` 返回 200 | `memory-bank/agent-worklogs/qa-agent.md` |
| QA-001 | 全局 | 测试 | 重建 Python 3.11 基线下的 API smoke 套件，覆盖当前真实契约 | QA Agent | done | BE-001,BE-002 | 新 smoke 用例可复现本次报告中的关键结论并持续回归 | `memory-bank/agent-worklogs/qa-agent.md` |
| QA-002 | F049-F082 + 支撑能力 | 测试 | 建立页面人工走查清单，补页面级验证记录 | QA Agent | done | FE-001,FE-002,FE-003,FE-004,FE-005 | 所有关键页面至少有 1 条页面走查记录和结果 | `memory-bank/agent-worklogs/qa-agent.md` |
|| QA-003 | 全局 | 测试 | 评估并选型是否引入浏览器自动化验证 v2 页面 | QA Agent | done | QA-002 | 给出是否引入浏览器自动化的决策和最小落地方案 | `memory-bank/agent-worklogs/qa-agent.md` |

## 阶段二：LLM 链路打通与工程化改造 (Phase 2)

| task_id | 模块 | 问题类型 | 目标结果 | owner | status | depends_on | 验收标准 | 记录文件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FE-006 | 前端 | Bug修复 | 全局排查并修复 Axios/Fetch 语法混用问题 | Frontend Agent | todo | QA-002 | 前端代码中不存在 `res.ok` 或 `res.json()` 等针对 Axios 响应的错误调用 | `memory-bank/agent-worklogs/frontend-agent.md` |
| BE-006 | 后端 | 工程化 | 引入 Alembic 进行数据库版本迁移管理 | Backend Agent | todo | QA-001 | 可通过 `alembic upgrade head` 生成与代码一致的库表结构，消除 schema 漂移 | `memory-bank/agent-worklogs/backend-agent.md` |
| BE-007 | 后端 | 异步调度 | 引入 BackgroundTasks/Celery 改造长耗时解析与生成接口 | Backend Agent | todo | 无 | 耗时任务转为异步，前端不会遇到 504 Timeout，并能获取状态 | `memory-bank/agent-worklogs/backend-agent.md` |
| BE-008 | 后端 | LLM接入 | 重构 proposal_service.py，接入真实 LLM 替代硬编码模板 | Backend Agent | todo | BE-007 | 能根据上下文真实生成不同内容的文档，并根据标书给出语义化预打分 | `memory-bank/agent-worklogs/backend-agent.md` |
| BE-009 | 后端 | 文本处理 | 优化标书解析处理，引入分块与摘要策略代替硬截断 | Backend Agent | todo | BE-007 | 支持超长 PDF 解析，末尾的技术要求或合同条款不会被丢弃 | `memory-bank/agent-worklogs/backend-agent.md` |
| BE-012 | F11 | 后端 | 为 `/bidding-game/simulate` 补齐 iterative 模式、轮次结果、策略演化和持久化字段 | Backend Agent | done | BE-006 | `SimulationConfig.method=iterative` 已返回 `iterative_result`；迁移脚本已补齐 `bidding_game_simulations.iterative_result`；内存 SQLite 持久化烟测通过 | `memory-bank/agent-worklogs/backend-agent.md` |
| FE-008 | F11 | 前端 | 在博弈沙盘中接入 iterative 模式配置、结果摘要、轮次明细和策略演化图表 | Frontend Agent | done | BE-012 | `BiddingGameSimulator.vue` 可切换迭代模式并展示收敛轮次、演化表和图表；`npm run build` 通过 | `memory-bank/agent-worklogs/frontend-agent.md` |
| QA-005 | F11 | 测试 | 补多轮迭代博弈真实 HTTP 联调和真实数据库验证 | QA Agent | done | BE-012,FE-008 | 已完成 `POST /api/v1/auth/login` + `POST /api/v1/bidding-game/simulate` 真请求验证，确认 `iterative_result` 返回和 SQLite 落库；正式环境仅需补 Alembic 迁移回归 | `memory-bank/agent-worklogs/qa-agent.md` |
| BE-014 | F14 | 后端 | 实现协同博弈引擎：联盟解析、3种协同策略（高报价陪标/价格垫/区间包裹）、迭代联动、持久化 | Backend Agent | done | BE-012 | `_resolve_alliance_map` + `_apply_coalition_to_discount` 已接入 MC 模拟和迭代模式；`coalition_result` 返回正常 | `memory-bank/agent-worklogs/backend-agent.md` |
| FE-010 | F14 | 前端 | 在博弈沙盘添加协同博弈配置面板、联盟管理、结果展示 | Frontend Agent | done | BE-014 | `BiddingGameSimulator.vue` 可折叠联盟面板、多联盟增删、主攻方/陪标方选择、策略类型和折扣间距配置；结果区联盟面板展示正常 | `memory-bank/agent-worklogs/frontend-agent.md` |
| BE-013 | F13 | 后端 | 新增 `/bidding-game/history-learning` 与历史样本聚合逻辑，按项目回传竞对先验画像 | Backend Agent | done | BE-012 | `build_competitor_history_profiles()` 已聚合情报预测、手工历史折扣、Agent 先验和迭代轮次样本；路由已返回 `profiles/sample_count/source_breakdown` | `memory-bank/agent-worklogs/backend-agent.md` |
| FE-009 | F13 | 前端 | 在竞商情报和博弈沙盘之间打通“从历史数据学习”入口与参数回填 | Frontend Agent | done | BE-013 | `CompetitorIntelligence.vue` 可触发历史学习；`PricingStrategy.vue` 可传递 `project_id`；`BiddingGameSimulator.vue` 可应用历史画像；`npm run build` 通过 | `memory-bank/agent-worklogs/frontend-agent.md` |
| QA-006 | F13 | 测试 | 补历史学习最小运行态验证并记录测试环境阻塞项 | QA Agent | done | BE-013,FE-009 | 已完成内存 SQLite 最小路由处理层烟测和前端构建验证；完整 `pytest` 回归当前受仓库缺少 `python-docx` 阻塞，已记录在测试报告 | `memory-bank/agent-worklogs/qa-agent.md` |
