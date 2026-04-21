# SaleAgents

招投标智能体 MVP 项目骨架。

当前工程默认采用轻量方案：

- `backend`：FastAPI
- `frontend`：React + Vite + TypeScript
- `database`：PostgreSQL + pgvector 初始化脚本。前期使用SQLite作为本地兜底。
- `storage/cache`：本地或现有环境中的 PostgreSQL、Redis、对象存储

## 目录结构

```text
SaleAgents/
├── backend/        # 后端 API 与业务模块
├── frontend/       # 前端工作台
├── database/       # 数据库初始化脚本
└── docs/           # PRD、架构、页面设计
```

## 快速开始

### 1. 准备本地依赖

请确保本地已经准备好以下服务，或接入现有开发环境：

- PostgreSQL + `pgvector`
- Redis
- 对象存储

默认本地连接约定：

- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Object Storage Endpoint: `localhost:9000`

如果当前只是想先把前后端链路跑通，也可以使用 SQLite 作为本地兜底，不必先安装 PostgreSQL。

先在项目根目录创建 `.env`：

```bash
cp .env.example .env
```

然后把下面这一行填进 `.env`：

```bash
DATABASE_URL_OVERRIDE=sqlite:///./bid_agent.db
```

说明：

- 这个 SQLite 文件会在 `backend/` 目录下自动创建
- 启动后端时仍然建议先 `cd backend`
- 当你准备切回 PostgreSQL 时，清空 `DATABASE_URL_OVERRIDE` 即可

### 2. 初始化数据库

```bash
psql -h localhost -U bid_agent -d bid_agent -f database/init/001-init.sql
```

### 3. 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

后端健康检查：

```bash
curl http://localhost:8000/api/v1/health
```

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：

```text
http://localhost:5173
```
