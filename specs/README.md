# SaleAgents 规范目录

本目录是 SaleAgents v2 的规范驱动开发入口。  
所有新的任务、实现、回归都优先遵循这里的文件，而不是历史散落文档。

## 目录文件

### 产品规范

1. `saleagents-v2-architecture.md` — SaleAgents V2 系统架构设计

### 工程规范

2. `api-contract-spec.md` — API 契约规范
3. `engineering-spec.md` — 工程总览规范
4. `frontend-style-spec.md` — 前端开发规范
5. `backend-dev-spec.md` — 后端开发规范
6. `testing-spec.md` — 测试规范
7. `task-governance-spec.md` — 任务治理规范

## 维护规则

- 公开 API 变化：先改 `api-contract-spec.md`
- 工程边界变化：先改 `engineering-spec.md`
- 前端交互与样式约束变化：先改 `frontend-style-spec.md`
- 后端分层、模型、数据库约束变化：先改 `backend-dev-spec.md`
- 测试门槛变化：先改 `testing-spec.md`
- 任务流转规则变化：先改 `task-governance-spec.md`
