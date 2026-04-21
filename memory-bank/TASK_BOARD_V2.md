# SaleAgents v2 任务看板

更新日期：2026-04-21  
说明：所有后续工作先在本表认领，再进入实现。状态建议使用：`todo` / `in_progress` / `blocked` / `review` / `done`

| task_id | 来源功能点 | 问题类型 | 目标结果 | owner | status | depends_on | 验收标准 | 记录文件 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUDIT-001 | F049-F082 | 审计 | 建立 34 行功能矩阵、页面覆盖矩阵、测试计划/报告 | Audit Agent | done | 无 | 根目录文档落地并可追溯到代码/运行态证据 | `memory-bank/agent-worklogs/audit-agent.md` |
| SPEC-001 | 全局 | 规范 | 创建 `specs/` 目录及 6 份规范文件 | Spec Agent | done | AUDIT-001 | `specs/` 首批规范齐全，可直接指导实现 | `memory-bank/agent-worklogs/spec-agent.md` |
| SPEC-002 | 全局 | 规范 | 将 `frontend-v2/SPEC.md` 与 `frontend-v2/memory-bank/*` 标记为历史参考 | Spec Agent | done | SPEC-001 | 旧文档文件头清楚标记迁移入口 | `memory-bank/agent-worklogs/spec-agent.md` |
| BE-001 | 支撑能力-健康检查 | 后端 | 在 `backend-v2/app/api/router.py` 注册健康检查路由并补 smoke 用例 | Backend Agent | todo | AUDIT-001 | `GET /api/v1/health` 返回 200 且纳入测试报告 | `memory-bank/agent-worklogs/backend-agent.md` |
| BE-002 | 支撑能力-系统设置 | 后端 | 修复 `ai_configs` 数据库 schema 漂移，恢复 `/settings/ai-config*` | Backend Agent | todo | AUDIT-001 | `/settings/ai-config` 与 `/settings/ai-configs` 均返回 200；旧数据可兼容 | `memory-bank/agent-worklogs/backend-agent.md` |
| FE-001 | F082 | 前端 | 修复 `ProposalEditor.vue` 中 axios/fetch 混用和动态路径问题 | Frontend Agent | todo | AUDIT-001 | 页面可拉取章节、生成、评分、重评分、确认并正确展示结果 | `memory-bank/agent-worklogs/frontend-agent.md` |
| FE-002 | 支撑能力-用户/角色 | 前端 | 修复 `UserManagement.vue`、`RoleManagement.vue` 的 axios 用法与动态路径错误 | Frontend Agent | todo | AUDIT-001 | 用户 CRUD 与角色列表在页面可正常工作 | `memory-bank/agent-worklogs/frontend-agent.md` |
| FE-003 | 支撑能力-系统设置 | 前端 | 对齐 `SystemSettings.vue` 与当前后端契约，补错误态和兼容提示 | Frontend Agent | todo | BE-002 | AI 配置、规则、素材区的成功/失败态可见且可回归 | `memory-bank/agent-worklogs/frontend-agent.md` |
| FE-004 | F052-F053 | 前端 | 把 `ProjectCreate.vue` 和 `BidList.vue` 提升为真实项目工作台，而非仅基础 CRUD | Frontend Agent | todo | AUDIT-001 | 页面展示项目重点字段、确认状态、文件清单和节点工作台 | `memory-bank/agent-worklogs/frontend-agent.md` |
| FE-005 | F054-F079,F081 | 前端 | 补齐 `TenderDetail.vue` 的工作流信息、人工确认、重算反馈和错误态 | Frontend Agent | todo | BE-003,BE-004,BE-005 | 文档区块能明确显示规则来源、当前状态、修改结果和待人工事项 | `memory-bank/agent-worklogs/frontend-agent.md` |
| BE-003 | F050-F053 | 后端 | 完善招标处理字段：保证金、项目类型、拒绝原因、项目绑定和流程状态 | Backend Agent | todo | AUDIT-001 | 决策和上传接口能完整承载 Excel 行 50-53 的业务字段 | `memory-bank/agent-worklogs/backend-agent.md` |
| BE-004 | F052,F054-F075 | 后端 | 完成真实解析链路：上传标书 -> 章节 -> 星标项 -> 文档清单/详情 | Backend Agent | todo | AUDIT-001 | 真实样本上传后能生成解析章节并驱动商务/技术文档区 | `memory-bank/agent-worklogs/backend-agent.md` |
| BE-005 | F058,F069-F081 | 后端 | 把素材库/技术案例/评分规则真正接入商务文档、技术文档、方案建议书和案例检索 | Backend Agent | todo | BE-002,BE-004 | 关键模板能根据素材和评分规则自动填充并回显规则说明 | `memory-bank/agent-worklogs/backend-agent.md` |
| QA-001 | 全局 | 测试 | 重建 Python 3.11 基线下的 API smoke 套件，覆盖当前真实契约 | QA Agent | todo | BE-001,BE-002 | 新 smoke 用例可复现本次报告中的关键结论并持续回归 | `memory-bank/agent-worklogs/qa-agent.md` |
| QA-002 | F049-F082 + 支撑能力 | 测试 | 建立页面人工走查清单，补页面级验证记录 | QA Agent | todo | FE-001,FE-002,FE-003,FE-004,FE-005 | 所有关键页面至少有 1 条页面走查记录和结果 | `memory-bank/agent-worklogs/qa-agent.md` |
| QA-003 | 全局 | 测试 | 评估并选型是否引入浏览器自动化验证 v2 页面 | QA Agent | todo | QA-002 | 给出是否引入浏览器自动化的决策和最小落地方案 | `memory-bank/agent-worklogs/qa-agent.md` |
