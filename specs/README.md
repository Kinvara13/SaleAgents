# SaleAgents 规范目录

本目录是 SaleAgents v2 的规范驱动开发入口。  
所有新的任务、实现、回归都优先遵循这里的文件，而不是历史散落文档。

## 目录优先级

1. `api-contract-spec.md`
2. `engineering-spec.md`
3. `frontend-style-spec.md`
4. `backend-dev-spec.md`
5. `testing-spec.md`
6. `task-governance-spec.md`

## 维护规则

- 公开 API 变化：先改 `api-contract-spec.md`
- 工程边界变化：先改 `engineering-spec.md`
- 前端交互与样式约束变化：先改 `frontend-style-spec.md`
- 后端分层、模型、数据库约束变化：先改 `backend-dev-spec.md`
- 测试门槛变化：先改 `testing-spec.md`
- 任务流转规则变化：先改 `task-governance-spec.md`

## 与历史文档的关系

- `frontend-v2/SPEC.md`
- `frontend-v2/memory-bank/PROGRESS.md`
- `frontend-v2/memory-bank/ARCHITECTURE.md`

以上文件仅保留历史参考，不再作为主维护入口。
