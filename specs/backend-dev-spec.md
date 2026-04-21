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

- 新增列时必须考虑旧 SQLite 文件兼容
- 不能依赖 `create_all()` 自动补齐已有表字段
- 若模型字段已增加但老库未迁移，必须提供迁移脚本或兼容读取策略

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
