# SaleAgents 任务治理规范

## 1. 任务类型

- `AUDIT`
  - 审计、盘点、证据归集
- `FE`
  - 前端页面、交互、service、样式
- `BE`
  - 后端接口、服务、数据库、兼容
- `QA`
  - 测试计划、回归、样本、报告
- `SPEC`
  - 规范、流程、模板、文档治理

## 2. 优先级

- `P0`
  - 阻断主流程或公开 API
- `P1`
  - 功能不闭环、关键体验缺失
- `P2`
  - 次级体验或维护性问题

## 3. 状态流转

- `todo`
- `in_progress`
- `blocked`
- `review`
- `done`

要求：

- 只有认领后才能进入 `in_progress`
- 被依赖问题未解决时，用 `blocked`
- 有验证证据后才能从 `review` 到 `done`

## 4. 每个任务必须具备的信息

- `task_id`
- 来源功能点
- 问题类型
- 目标结果
- owner
- status
- depends_on
- 验收标准
- 记录文件

禁止随意增减任务板字段。

## 5. 完成要求

标记 `done` 前必须同时满足：

- 代码或文档已提交到工作区
- 验收标准已经被验证
- `TASK_BOARD_V2.md` 已更新
- `CHANGE_LOG_V2.md` 已更新
- 对应 `agent-worklogs/*.md` 已更新

## 6. 跨 Agent 协调

- 一个任务只能有一个主 owner
- 协作方在自己的 worklog 追加协助记录，不抢主 owner
- 公开 API 变更统一由 Backend Agent 发起，Frontend Agent 跟进
- 规范变更统一由 Spec Agent 归档
