# SaleAgents v2 AI Agent 协作提示词

本文档用于给后续 AI agent 派发开发、测试、规范维护任务。  
目标是让所有 agent 都按根目录 `memory-bank/` 和 `specs/` 的规则持续开发、回写记录、更新规范。

## 1. 使用原则

- 不要让 agent 一上来直接改代码
- 先读规则、再认领任务、再实施
- 完成后必须回写任务板、变更日志和对应 worklog
- 涉及 API 契约变化时，必须先更新 `specs/api-contract-spec.md`

## 2. 标准步骤

### 第一步：先读规则和事实源

必读文件：

- `/Users/sen/SaleAgents/memory-bank/FEATURE_MATRIX_V2.md`
- `/Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md`
- `/Users/sen/SaleAgents/memory-bank/AGENT_WORKFLOW.md`
- `/Users/sen/SaleAgents/specs/api-contract-spec.md`

按角色补充阅读：

- 前端：`/Users/sen/SaleAgents/specs/frontend-style-spec.md`
- 后端：`/Users/sen/SaleAgents/specs/backend-dev-spec.md`
- 测试：`/Users/sen/SaleAgents/specs/testing-spec.md`
- 规范：`/Users/sen/SaleAgents/specs/engineering-spec.md`、`/Users/sen/SaleAgents/specs/task-governance-spec.md`

### 第二步：先认领任务

agent 开始前必须：

1. 在 `/Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md` 中把对应任务改成 `in_progress`
2. 在对应 `memory-bank/agent-worklogs/*.md` 中追加开始记录
3. 确认该任务依赖项是否已完成

### 第三步：实施时遵守规则

- 不覆盖历史记录，只追加
- 不擅自修改公开 API 契约
- 如果功能状态结论变化，要同步更新 `FEATURE_MATRIX_V2.md`
- 如果测试结论变化，要同步更新 `TEST_REPORT_V2.md`

### 第四步：完成后必须回写

至少同步更新：

- `/Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md`
- `/Users/sen/SaleAgents/memory-bank/CHANGE_LOG_V2.md`
- 对应 `/Users/sen/SaleAgents/memory-bank/agent-worklogs/*.md`

如涉及契约变化，还必须更新：

- `/Users/sen/SaleAgents/specs/api-contract-spec.md`

### 第五步：最终输出

要求 agent 最后输出：

- 本次认领的任务
- 代码或文档改动
- 验证结果
- 剩余风险
- 已更新文件列表

## 3. 通用提示词模板

```text
你现在是 SaleAgents v2 的协作开发 agent。先不要直接改代码，先按以下顺序执行：

1. 阅读并遵守这些文件：
- /Users/sen/SaleAgents/memory-bank/AGENT_WORKFLOW.md
- /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md
- /Users/sen/SaleAgents/memory-bank/FEATURE_MATRIX_V2.md
- /Users/sen/SaleAgents/specs/api-contract-spec.md

2. 根据你的角色，再阅读对应规范：
- 前端角色：/Users/sen/SaleAgents/specs/frontend-style-spec.md
- 后端角色：/Users/sen/SaleAgents/specs/backend-dev-spec.md
- 测试角色：/Users/sen/SaleAgents/specs/testing-spec.md
- 规范角色：/Users/sen/SaleAgents/specs/engineering-spec.md 和 /Users/sen/SaleAgents/specs/task-governance-spec.md

3. 先从 /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md 中认领指定任务，把状态改成 in_progress，并在对应 worklog 里追加开始记录，然后再实施。

4. 实施期间遵守：
- 不要覆盖历史记录，只追加
- 如果涉及 API 契约变化，先更新 /Users/sen/SaleAgents/specs/api-contract-spec.md
- 如果涉及功能完成度变化，更新 /Users/sen/SaleAgents/memory-bank/FEATURE_MATRIX_V2.md
- 完成后必须同步更新：
  - /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md
  - /Users/sen/SaleAgents/memory-bank/CHANGE_LOG_V2.md
  - 对应的 /Users/sen/SaleAgents/memory-bank/agent-worklogs/*.md

5. 完成后输出：
- 本次认领的任务
- 代码或文档改动
- 验证结果
- 剩余风险
- 已更新文件列表
```

## 4. 前端 Agent 提示词

```text
你是 Frontend Agent。处理 /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md 中的 FE 任务。

必读：
- /Users/sen/SaleAgents/memory-bank/AGENT_WORKFLOW.md
- /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md
- /Users/sen/SaleAgents/memory-bank/FEATURE_MATRIX_V2.md
- /Users/sen/SaleAgents/specs/frontend-style-spec.md
- /Users/sen/SaleAgents/specs/api-contract-spec.md

本轮优先任务：
- FE-001
- FE-002
- FE-003

重点要求：
- 修复 axios/fetch 混用
- 修复动态路径错误
- 不要擅自改 API 契约；如必须改，先更新 api-contract-spec
- 完成后同步更新任务板、变更日志、frontend-agent worklog
```

## 5. 后端 Agent 提示词

```text
你是 Backend Agent。处理 /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md 中的 BE 任务。

必读：
- /Users/sen/SaleAgents/memory-bank/AGENT_WORKFLOW.md
- /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md
- /Users/sen/SaleAgents/memory-bank/FEATURE_MATRIX_V2.md
- /Users/sen/SaleAgents/specs/backend-dev-spec.md
- /Users/sen/SaleAgents/specs/api-contract-spec.md

本轮优先任务：
- BE-001
- BE-002

重点要求：
- 先修复健康检查路由注册
- 先修复 ai_configs schema 漂移
- 运行验证统一使用 Python 3.11
- 如果改公开接口，先更新 api-contract-spec
- 完成后同步更新任务板、变更日志、backend-agent worklog
```

## 6. QA Agent 提示词

```text
你是 QA Agent。处理 /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md 中的 QA 任务。

必读：
- /Users/sen/SaleAgents/memory-bank/AGENT_WORKFLOW.md
- /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md
- /Users/sen/SaleAgents/memory-bank/TEST_PLAN_V2.md
- /Users/sen/SaleAgents/memory-bank/TEST_REPORT_V2.md
- /Users/sen/SaleAgents/specs/testing-spec.md
- /Users/sen/SaleAgents/specs/api-contract-spec.md

本轮优先任务：
- QA-001

重点要求：
- 以 Python 3.11 为基线重建 smoke 测试
- 修正旧测试报告中的过期结论
- 新发现必须回写 TEST_REPORT_V2、TASK_BOARD_V2、CHANGE_LOG_V2、qa-agent worklog
```

## 7. Spec Agent 提示词

```text
你是 Spec Agent。处理 /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md 中的 SPEC 任务和后续规范维护。

必读：
- /Users/sen/SaleAgents/memory-bank/AGENT_WORKFLOW.md
- /Users/sen/SaleAgents/specs/README.md
- /Users/sen/SaleAgents/specs/engineering-spec.md
- /Users/sen/SaleAgents/specs/task-governance-spec.md
- /Users/sen/SaleAgents/specs/api-contract-spec.md

重点要求：
- 只维护规范和流程，不直接改业务实现
- 发现实现与规范冲突时，先记录差异，再决定更新哪边
- 所有规范变更必须写入 CHANGE_LOG_V2 和 spec-agent worklog
```

## 8. 直接派单模板

### 通用派单模板

```text
请作为 {角色} 执行 {任务号}。

先阅读：
- /Users/sen/SaleAgents/memory-bank/AGENT_WORKFLOW.md
- /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md
- /Users/sen/SaleAgents/specs/api-contract-spec.md

再阅读与你角色对应的规范文件。

要求：
- 先把 {任务号} 在 TASK_BOARD_V2.md 标记为 in_progress
- 在对应 agent worklog 中追加开始记录
- 按规范实施，不要跳过文档回写
- 完成后更新 TASK_BOARD_V2.md、CHANGE_LOG_V2.md 和对应 worklog
- 最后输出改动、验证、风险、文件列表
```

### 后端派单示例

```text
请作为 Backend Agent 执行 BE-002。

先阅读：
- /Users/sen/SaleAgents/memory-bank/AGENT_WORKFLOW.md
- /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md
- /Users/sen/SaleAgents/specs/backend-dev-spec.md
- /Users/sen/SaleAgents/specs/api-contract-spec.md

要求：
- 先把 BE-002 在 TASK_BOARD_V2.md 标记为 in_progress
- 修复 ai_configs schema 漂移导致的 /settings/ai-config 和 /settings/ai-configs 500
- 使用 Python 3.11 做运行验证
- 完成后更新 TASK_BOARD_V2.md、CHANGE_LOG_V2.md、memory-bank/agent-worklogs/backend-agent.md
- 最后输出改动、验证、风险、文件列表
```

### 前端派单示例

```text
请作为 Frontend Agent 执行 FE-001。

先阅读：
- /Users/sen/SaleAgents/memory-bank/AGENT_WORKFLOW.md
- /Users/sen/SaleAgents/memory-bank/TASK_BOARD_V2.md
- /Users/sen/SaleAgents/specs/frontend-style-spec.md
- /Users/sen/SaleAgents/specs/api-contract-spec.md

要求：
- 先把 FE-001 在 TASK_BOARD_V2.md 标记为 in_progress
- 修复 ProposalEditor.vue 中 axios/fetch 混用和动态路径问题
- 不擅自修改公开 API；如有必要，先更新 api-contract-spec
- 完成后更新 TASK_BOARD_V2.md、CHANGE_LOG_V2.md、memory-bank/agent-worklogs/frontend-agent.md
- 最后输出改动、验证、风险、文件列表
```

## 9. 当前推荐执行顺序

建议派单顺序：

1. `Backend Agent` 处理 `BE-001`、`BE-002`
2. `Frontend Agent` 处理 `FE-001`、`FE-002`、`FE-003`
3. `QA Agent` 处理 `QA-001`
4. 再继续处理 `FE-004`、`FE-005`、`BE-003`、`BE-004`、`BE-005`

原因：

- 先修复健康检查和 AI 配置阻塞，避免测试基线不稳定
- 先修复前端 axios/fetch 混用，避免页面验证失真
- 再做更深的解析链路、工作台和素材库闭环
