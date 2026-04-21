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

- 不要把 `Base.metadata.create_all()` 当作列级迁移方案
- 涉及新增列、重命名列、兼容旧数据时，必须有显式迁移方案
- 所有 schema 漂移必须写入任务板和测试报告

## 8. 文档更新要求

每次完成一个功能闭环，至少更新：

- `memory-bank/FEATURE_MATRIX_V2.md`
- `memory-bank/TASK_BOARD_V2.md`
- `memory-bank/CHANGE_LOG_V2.md`

涉及公开契约时还必须更新：

- `specs/api-contract-spec.md`
