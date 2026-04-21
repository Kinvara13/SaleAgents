# SaleAgents v2 多 Agent 协作工作流

本文件是根目录 `memory-bank/` 下的协作约束。  
后续所有 Agent 必须先读本文件，再认领任务。

## 1. 角色边界

- `Audit Agent`
  - 负责功能映射、证据归集、状态判定、差距描述。
  - 不直接改业务代码。
- `Frontend Agent`
  - 只负责 `frontend-v2/`。
  - 包括页面、路由、service、样式、前端测试补齐。
- `Backend Agent`
  - 只负责 `backend-v2/`。
  - 包括 endpoint、schema、service、数据库兼容、接口测试补齐。
- `QA Agent`
  - 负责测试计划、测试报告、样本管理、回归记录。
- `Spec Agent`
  - 负责 `specs/` 和根目录 `memory-bank/` 的规范、模板、术语与流程文件。

## 2. 唯一事实源

优先级从高到低：

1. 当前运行态验证结果
2. 当前仓库代码
3. `memory-bank/FEATURE_MATRIX_V2.md`
4. `memory-bank/PAGE_COVERAGE_V2.md`
5. `specs/*.md`
6. 历史文档，如 `TASK_STATUS.md`、`TEST_REPORT.md`、`frontend-v2/SPEC.md`

任何历史文档与当前代码冲突时，以前五项为准。

## 3. 领任务规则

1. 先查看 `memory-bank/TASK_BOARD_V2.md`
2. 把待处理任务状态改成 `in_progress`
3. 在对应 `agent-worklogs/*.md` 追加一条认领记录
4. 再进入实现或补充审计

禁止行为：

- 两个 Agent 同时修改同一份主文档
- 不更新任务板就直接改代码
- 在未更新 `specs/api-contract-spec.md` 前直接改公开 API

## 4. 记录回写规则

每个任务至少同步更新三处：

- `memory-bank/TASK_BOARD_V2.md`
- `memory-bank/CHANGE_LOG_V2.md`
- 对应 `memory-bank/agent-worklogs/<agent>.md`

回写原则：

- 只追加，不覆盖历史记录
- 如果旧结论失效，新增“修正记录”
- 记录必须注明日期、任务号、影响范围、结论

## 5. 实施前检查单

在开始改代码前，必须确认：

- 功能差距已写入 `FEATURE_MATRIX_V2.md`
- 页面/API 契约已写入或更新 `specs/api-contract-spec.md`
- 任务已在 `TASK_BOARD_V2.md` 认领
- 对应 worklog 已写入“开始处理”

## 6. 完成定义

任务可标记 `done` 的最小条件：

- 代码或文档改动已落地
- 有至少一条验证证据
- 任务板、变更日志、agent worklog 已同步
- 若涉及公开契约，`specs/` 已更新

## 7. 冲突处理

- 文档冲突：以根目录 `memory-bank/` 和 `specs/` 为准
- API 冲突：以 `backend-v2/app/api/router.py` 注册的当前路由为准
- 页面冲突：以 `frontend-v2/src/router/index.ts` 当前可访问路由为准
- 测试冲突：以最新 `TEST_REPORT_V2.md` 为准，并在 `CHANGE_LOG_V2.md` 中写明修正原因
