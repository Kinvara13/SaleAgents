# Backend Agent Worklog

## 2025-06-15

### BE-006: Alembic 数据库迁移管理
- 初始化 Alembic：`alembic init alembic`
- 配置 `alembic.ini`：SQLite 连接、autogenerate 模板、mako 编码
- 配置 `alembic/env.py`：导入 Base 和 models，设置 `target_metadata = Base.metadata`
- 创建首个 migration：`alembic revision --autogenerate -m "init schema"`
- migration 文件：`alembic/versions/20250615_init_schema.py`，涵盖 38 张表
- 验证：`alembic upgrade head` 成功，数据库结构与 models 完全一致
- `ai_configs.name` 列漂移已确认修复

### BE-007: 异步任务改造
- 选型：FastAPI BackgroundTasks（SQLite 环境，轻量级，无需 Redis/Celery）
- 新增 `AsyncTask` model（38 张表中的第 38 张），存储任务状态/类型/进度/结果/错误信息
- 新增 `AsyncTaskResponse` / `AsyncTaskListResponse` schemas
- 新增 `AsyncTaskService`（含 `create_task`, `get_task`, `run_async` 等）
- 新增 `async_tasks.py` endpoint，提供 `GET /tasks/{task_id}` 状态查询
- 改造 `POST /parsing/{project_id}/upload`：立即返回 task_id，后台执行上传解析
- 改造 `POST /proposal-editor/{project_id}/generate`：立即返回 task_id，后台执行方案生成
- 在 `router.py` 中注册 `/tasks` 路由

### 提交
- 全部修改已提交至 GitHub
