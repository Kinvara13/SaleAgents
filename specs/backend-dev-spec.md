# SaleAgents 后端开发规范

## 1. 技术基线

- Python：`3.11+`
- Web：FastAPI
- ORM：SQLAlchemy
- 默认数据库：SQLite

## 2. 分层职责

- `endpoints/`
  - 参数校验、认证、响应模型、HTTP 语义
- `services/`
  - 业务逻辑、规则拼装、文件处理、数据聚合
- `schemas/`
  - 请求体与响应体契约
- `models/`
  - 数据库存储模型

禁止：

- 在 endpoint 中堆叠核心业务逻辑
- 直接在前端约定尚未更新时擅自修改响应结构

## 3. 路由管理

当前公开 API 的真实注册入口是：

- `backend-v2/app/api/router.py`

要求：

- 新增 endpoint 后，必须在该文件中显式注册
- 提交前必须自查是否已注册
- 健康检查类接口必须可直接 smoke

## 4. 响应与兼容

- 保持 response model 与实际返回一致
- 旧接口如果仍被前端使用，先保兼容，再计划收敛
- 兼容接口要在 `specs/api-contract-spec.md` 标记为 `legacy`

## 5. 数据库与迁移

### 5.1 初始化脚本规范

所有数据库操作脚本必须统一汇总到 `database/init/` 目录下的 SQL 脚本中：

- 脚本命名格式：`{序号}-{描述}.sql`（如 `001-init.sql`、`002-add-feature.sql`）
- 脚本必须是幂等的（可重复执行，使用 `IF NOT EXISTS`）
- 每个脚本必须包含注释说明用途和关联的 model 文件
- 脚本内容必须与 `backend-v2/app/models/*.py` 中的定义保持一致

### 5.2 模型变更流程

当修改 `backend-v2/app/models/*.py` 中的模型时：

1. 同步更新 `database/init/001-init.sql` 中对应的 CREATE TABLE 语句
2. 新增字段必须提供默认值或允许 NULL
3. 不能依赖 `Base.metadata.create_all()` 自动补齐已有表字段
4. 若模型字段已增加但老库未迁移，必须提供迁移脚本或兼容读取策略

### 5.3 禁止事项

- 不要把 `Base.metadata.create_all()` 当作列级迁移方案
- 涉及新增列、重命名列、兼容旧数据时，必须有显式迁移方案
- 所有 schema 漂移必须写入任务板和测试报告

当前已知案例：

- `ai_configs` 表缺少 `name` 列，导致 `/settings/ai-config*` 500

## 6. 文件与存储

- 上传目录应通过配置注入，不要硬编码不可迁移路径
- 文件上传必须保留原始文件名、保存路径、所属项目或任务信息
- 需要重生成时，要保留可追溯元数据

## 7. 认证

- 统一使用 Bearer Token
- 需要鉴权的 endpoint 必须显式声明依赖
- 支撑能力接口不可绕过权限设计直接暴露

## 8. 运行与验证

本地最小验证命令：

```bash
cd backend-v2
export DATABASE_URL_OVERRIDE='sqlite:///./sale_agents_v2.db'
python3.11 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

任何“接口可用”结论，都必须至少有一次运行态验证或明确标记“仅静态确认”。
