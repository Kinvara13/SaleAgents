# TASK_BOARD_V2.md - SaleAgents v2

## 后端任务

| 任务 | 状态 | 说明 |
|------|------|------|
| BE-001 | done | 项目脚手架与基础配置 |
| BE-002 | done | 数据库模型设计 |
| BE-003 | done | API 基础结构 |
| BE-004 | done | 认证与权限 |
| BE-005 | done | 核心业务流程实现 |
| BE-006 | done | Alembic 数据库迁移管理 |
| BE-007 | done | 异步任务改造 (BackgroundTasks) |
| BE-008 | todo | 性能优化与缓存 |
| BE-009 | todo | 测试覆盖与 CI/CD |
| BE-010 | todo | 部署与运维 |

## BE-006 详情
- Alembic 初始化完成，配置位于 `alembic.ini` 和 `alembic/` 目录
- 首个 migration `20250615_init_schema.py` 已创建，基于当前全部 38 张表
- `alembic upgrade head` 可生成与代码一致的库表结构
- `ai_configs` 表已确认包含 `name` 列（schema 漂移已修复）

## BE-007 详情
- 选型：FastAPI BackgroundTasks（SQLite 环境，无独立消息队列）
- 异步化接口：
  - `POST /parsing/{project_id}/upload` → 返回 `202 Accepted` + `{task_id, status: pending}`
  - `POST /proposal-editor/{project_id}/generate` → 返回 `202 Accepted` + `{task_id, status: pending}`
- 任务状态查询：`GET /tasks/{task_id}` 返回任务状态/进度/结果
- 新增 model: `AsyncTask` (`app/models/async_task.py`)
- 新增 endpoint: `app/api/v1/endpoints/async_tasks.py`
- 新增 service: `app/services/async_task_service.py`
