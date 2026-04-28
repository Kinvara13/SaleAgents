# SaleAgents 工程规范

## 1. 适用范围

- 根目录 `backend-v2/`
- 根目录 `frontend-v2/`
- 根目录 `memory-bank/`
- 根目录 `specs/`

## 2. 基本原则

- 先审计，再实现
- 先更新规范，再改公开契约
- 先写任务记录，再开始编码
- 所有结论必须可追溯到代码、运行态或测试记录

## 3. 目录职责

- `backend-v2/`
  - FastAPI 服务、数据库模型、业务服务、接口契约
- `frontend-v2/`
  - Vue3 页面、路由、service、前端交互
- `memory-bank/`
  - 事实矩阵、任务板、测试计划、测试报告、变更留痕
- `specs/`
  - 工程规约、接口规约、测试规约、任务治理规约

## 4. 运行环境要求

- Python：`3.11+`
- Node：与 `frontend-v2/package.json` 兼容的当前 LTS
- 数据库：默认 SQLite，本地文件为 `backend-v2/sale_agents_v2.db`

禁止：

- 默认使用 Python 3.9 启动 `backend-v2`
- 在未声明兼容策略时直接改动公开接口

## 5. 命名与分层

- 页面：`frontend-v2/src/views/*.vue`
- 前端 service：`frontend-v2/src/services/*.ts`
- 后端 endpoint：`backend-v2/app/api/v1/endpoints/*.py`
- 后端 service：`backend-v2/app/services/*.py`
- schema：`backend-v2/app/schemas/*.py`
- model：`backend-v2/app/models/*.py`

要求：

- 页面不要直接实现复杂协议拼接；优先通过 service 封装
- endpoint 负责参数、认证、响应模型
- service 负责业务逻辑
- schema 负责输入输出契约
- model 负责数据库映射

## 6. 变更管理

以下变更必须同时更新 `memory-bank/CHANGE_LOG_V2.md`：

- 公开 API 路径、请求体、响应体变化
- 页面主流程变化
- 数据库 schema 变化
- 测试门槛变化
- 规范文件变化

## 7. 数据库与迁移

### 7.1 初始化脚本规范

所有数据库操作脚本必须统一汇总到 `database/init/` 目录下的 SQL 脚本中：

- 脚本命名格式：`{序号}-{描述}.sql`（如 `001-init.sql`、`002-add-feature.sql`）
- 脚本必须是幂等的（可重复执行，使用 `IF NOT EXISTS`）
- 每个脚本必须包含注释说明用途和关联的 model 文件
- 脚本内容必须与 `backend-v2/app/models/*.py` 中的定义保持一致

初始化脚本执行顺序：

```bash
# 按文件名排序依次执行
psql -d database -f database/init/001-init.sql
psql -d database -f database/init/002-xxx.sql
```

### 7.2 模型变更流程

当修改 `backend-v2/app/models/*.py` 中的模型时：

1. 同步更新 `database/init/001-init.sql` 中对应的 CREATE TABLE 语句
2. 新增字段必须提供默认值或允许 NULL
3. 不能依赖 `Base.metadata.create_all()` 自动补齐已有表字段
4. 若模型字段已增加但老库未迁移，必须提供迁移脚本或兼容读取策略

### 7.3 禁止事项

- 不要把 `Base.metadata.create_all()` 当作列级迁移方案
- 涉及新增列、重命名列、兼容旧数据时，必须有显式迁移方案
- 所有 schema 漂移必须写入任务板和测试报告

当前已知案例：

- `ai_configs` 表缺少 `name` 列，导致 `/settings/ai-config*` 500

## 8. 文档更新要求

每次完成一个功能闭环，至少更新：

- `memory-bank/FEATURE_MATRIX_V2.md`
- `memory-bank/TASK_BOARD_V2.md`
- `memory-bank/CHANGE_LOG_V2.md`

涉及公开契约时还必须更新：

- `specs/api-contract-spec.md`
