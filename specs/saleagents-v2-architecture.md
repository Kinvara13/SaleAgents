# SaleAgents V2 系统架构设计

## 1. 文档信息

| 属性 | 内容 |
|------|------|
| 版本 | V2.0 |
| 日期 | 2026-04-28 |
| 关联文档 | `specs/api-contract-spec.md`, `specs/engineering-spec.md`, `specs/backend-dev-spec.md`, `memory-bank/FEATURE_MATRIX_V2.md` |

---

## 2. 系统概述

SaleAgents V2 是招投标智能体 MVP，采用前后端分离架构。后端基于 FastAPI + SQLAlchemy，前端基于 Vue 3 + Vite + Tailwind CSS + TypeScript。

### 2.1 核心功能模块

招标信息管理、项目管理、文档解析、商务/技术文档生成、方案建议书、技术案例匹配、标前评估、报价策略计算、方案编辑器、聊天、系统设置、用户管理。

### 2.2 技术栈

| 层级 | 技术选型 |
|------|----------|
| 后端 | FastAPI + SQLAlchemy + Pydantic + APScheduler |
| 数据库 | SQLite (默认) / PostgreSQL (生产) |
| 前端 | Vue 3 + Composition API + TypeScript + Vite + Tailwind CSS |
| HTTP | Axios + Vue Router 4 |

---

## 3. 目录结构

```
SaleAgents/
|-- backend-v2/
|   |-- app/
|   |   |-- api/
|   |   |   |-- router.py              # 统一路由注册入口
|   |   |   |-- v1/endpoints/         # 24 个 endpoint 模块
|   |   |-- core/
|   |   |   |-- config.py, scheduler_config.py
|   |   |-- db/
|   |   |   |-- base.py, session.py, seed_tenders.py
|   |   |-- models/                    # 17 个模型
|   |   |-- schemas/                   # 23 个 schema
|   |   |-- services/                  # 27 个 service
|   |   |-- main.py
|-- frontend-v2/
|   |-- src/
|   |   |-- layouts/MainLayout.vue
|   |   |-- router/index.ts            # 16 个页面路由
|   |   |-- services/                  # 15 个 service
|   |   |-- views/                     # 15 个页面组件
|   |-- package.json, vite.config.ts, tailwind.config.js
|-- database/init/001-init.sql
|-- docs/, specs/, memory-bank/
```

---

## 4. 后端架构

### 4.1 分层设计

```
HTTP Request → [Endpoint] → [Service] → [Schema] → [Model] → Database
```

- **Endpoint**: 参数校验、认证、响应模型
- **Service**: 业务逻辑、规则拼装、文件处理
- **Schema**: 请求/响应契约
- **Model**: ORM 映射

### 4.2 路由注册

入口：`backend-v2/app/api/router.py`

```python
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(business_document.router, prefix="/projects", tags=["business-documents"])
api_router.include_router(technical_document.router, prefix="/projects", tags=["technical-documents"])
api_router.include_router(technical_case.router, prefix="/projects", tags=["technical-cases"])
api_router.include_router(parsing.router, prefix="/parsing", tags=["parsing"])
api_router.include_router(proposal_editor.router, prefix="/proposal-editor", tags=["proposal-editor"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(tenders.router, prefix="/tenders", tags=["tenders"])
api_router.include_router(proposal_plan.router, prefix="/projects", tags=["proposal-plans"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["pricing"])
api_router.include_router(review.router, prefix="/review", tags=["review"])
api_router.include_router(pre_evaluation.router, prefix="/pre-evaluation", tags=["pre-evaluation"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
```

### 4.3 路由分组 (16 个标签)

| 标签 | 前缀 | 标签 | 前缀 |
|------|------|------|------|
| health | / | proposal-plans | /projects/{id}/proposal-plans |
| auth | /auth | pricing | /pricing |
| projects | /projects | review | /review |
| business-documents | /projects/{id}/business-documents | pre-evaluation | /pre-evaluation |
| technical-documents | /projects/{id}/technical-documents | tasks | /tasks |
| technical-cases | /projects/{id}/technical-cases | parsing | /parsing |
| proposal-editor | /proposal-editor | chat | /chat |
| users | /users | settings | /settings |

### 4.4 模型清单 (17 个)

Project, ParsingSection, ProposalSection, ChatMessage, ChatContext, User, AIConfig, Material, Rule, Tender, TechnicalCase, PreEvaluationJob, BusinessDocument, TechnicalDocument, WorkspacePanel, ProposalPlan, AsyncTask, DocumentScoreHistory, TenderFetchLog

### 4.5 关键 Services

| Service | 职责 |
|---------|------|
| project_service | 项目 CRUD、状态管理 |
| tender_service | 招标信息管理 |
| parsing_service | 文档解析、字段提取 |
| business_document_service | 商务文档生成、编辑、评分 |
| technical_document_service | 技术文档生成、编辑、评分 |
| proposal_plan_service | 方案建议书管理 |
| proposal_service | 提案章节生成、评分 |
| technical_case_service | 技术案例检索、匹配 |
| pricing_service | 报价计算 |
| pre_evaluation_service | 标前评估任务 |
| chat_service | 聊天消息管理 |
| scoring_service | 文档评分计算 |
| document_export_service | 文档导出 |
| tender_fetch_service | 招标信息定时抓取 |
| llm_client | LLM API 调用封装 |

---

## 5. 前端架构

### 5.1 路由配置

入口：`frontend-v2/src/router/index.ts`，16 个页面。

| 页面 | 路由 | 页面 | 路由 |
|------|------|------|------|
| Login | /login | ProposalEditor | /proposal-editor, /bid-list/:id/proposal |
| Home | /home | DemoWorkflow | /demo-workflow |
| PreEvaluation | /pre-evaluation | PricingStrategy | /pricing-strategy |
| TenderList | /tender-list | ProjectCreate | /project-create |
| TenderDetail | /tender-detail/:id | UserManagement | /user-management |
| TenderInfoList | /tender-info-list | RoleManagement | /role-management |
| TenderInfoDetail | /tender-info/:id | SystemSettings | /system-settings |
| BidList | /bid-list | | |

路由守卫：未登录用户重定向到 `/login`（public 页面除外）。

### 5.2 Service 层 (15 个)

| Service | 对应后端 | Service | 对应后端 |
|---------|----------|---------|----------|
| api.ts | Axios 封装 | proposalPlan.ts | /projects/{id}/proposal-plans |
| auth.ts | /auth | proposal.ts | /proposal-editor |
| project.ts | /projects | pricing.ts | /pricing |
| tender.ts | /tenders | preEvaluation.ts | /pre-evaluation |
| businessDocument.ts | /projects/{id}/business-documents | chat.ts | /chat |
| technicalDocument.ts | /projects/{id}/technical-documents | settings.ts | /settings |
| technicalCase.ts | /projects/{id}/technical-cases | review.ts | /review |
| | | generation.ts | /generation |

---

## 6. 数据库设计

### 6.1 表清单 (40 表 + 1 视图)

#### 用户与认证
- `users`

#### 项目管理
- `projects`, `project_documents`, `project_document_versions`, `project_parse_sections`, `project_extracted_fields`, `project_asset_preferences`

#### 招标信息
- `tenders`, `tender_fetch_logs`

#### 文档解析
- `parsing_sections`

#### 文档类型
- `business_documents`, `technical_documents`, `proposal_plans`, `proposal_sections`

#### 技术案例
- `technical_cases`

#### 标前评估
- `pre_evaluation_jobs`

#### 聊天记录
- `chat_messages`, `chat_contexts`

#### AI 配置与素材
- `ai_configs`, `materials`, `rules`

#### 工作台与任务
- `workspace_panels`, `async_tasks`, `document_score_histories`

#### 知识库
- `knowledge_assets_records`, `knowledge_asset_chunks_records`, `knowledge_asset_sources_records`, `knowledge_asset_index_jobs`, `knowledge_asset_workflows`

#### 生成任务
- `generation_jobs`, `generation_sections_records`, `generation_section_asset_refs`

#### 决策与审查
- `project_decision_jobs`, `review_jobs`, `review_issues_records`, `review_clauses_records`, `review_feedback_records`

#### 规则配置
- `rule_configs`, `rule_statistics`

#### 统计视图
- `v_project_stats` (聚合 section_count, business_doc_count, tech_doc_count 等)

### 6.2 关键索引

`idx_technical_cases_project_id`, `idx_pre_evaluation_jobs_project_id`, `idx_document_score_histories_project_id`, `idx_review_jobs_project_id`, `idx_generation_sections_job_id`, `idx_rule_configs_name`

---

## 7. API 接口

### 7.1 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /auth/login | 登录 |
| POST | /auth/refresh | 刷新 Token |

### 7.2 项目管理
| 方法 | 路径 |
|------|------|
| GET | /projects |
| POST | /projects |
| GET | /projects/{project_id} |
| PATCH | /projects/{project_id} |
| DELETE | /projects/{project_id} |
| POST | /projects/{project_id}/confirm |

### 7.3 招标信息
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /tenders | 列表 |
| POST | /tenders | 创建 |
| GET | /tenders/{tender_id} | 详情 |
| POST | /tenders/{tender_id}/decision | 决策 |
| POST | /tenders/{tender_id}/upload | 上传标书 |

### 7.4 文档解析
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /parsing/{project_id}/upload | 上传解析 |
| GET | /parsing/{project_id}/sections | 章节列表 |
| PATCH | /parsing/{project_id}/sections/{section_id} | 更新章节 |

### 7.5 商务/技术文档
| 方法 | 路径 |
|------|------|
| GET | /projects/{project_id}/{business,technical}-documents |
| GET | /projects/{project_id}/{business,technical}-documents/{doc_id} |
| PATCH | /projects/{project_id}/{business,technical}-documents/{doc_id} |
| POST | /projects/{project_id}/{business,technical}-documents/{doc_id}/generate |

### 7.6 方案建议书
| 方法 | 路径 |
|------|------|
| GET | /projects/{project_id}/proposal-plans |
| GET | /projects/{project_id}/proposal-plans/{doc_id} |
| PATCH | /projects/{project_id}/proposal-plans/{doc_id} |
| POST | /projects/{project_id}/proposal-plans/{doc_id}/generate |

### 7.7 技术案例
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /projects/{project_id}/technical-cases | 列表 |
| POST | /projects/{project_id}/technical-cases | 创建 |
| PATCH | /projects/{project_id}/technical-cases/{case_id} | 更新 |
| DELETE | /projects/{project_id}/technical-cases/{case_id} | 删除 |
| GET | /projects/{project_id}/technical-cases/search | 搜索 |

### 7.8 其他接口

| 模块 | 路径 | 方法 |
|------|------|------|
| 标前评估 | /pre-evaluation | GET, POST, GET {job_id} |
| 报价策略 | /pricing/calculate | POST |
| 方案编辑器 | /proposal-editor/{project_id} | /generate, /score, /rescore, /confirm |
| 聊天 | /chat/{project_id} | /messages GET/POST, /history DELETE |
| 系统设置 | /settings | /ai-config, /materials, /rules |
| 用户管理 | /users | GET, POST, PATCH {user_id}, DELETE {user_id}, /roles/list |
| 审查 | /review | GET, POST, GET {job_id} |

---

## 8. 核心工作流

### 8.1 招标信息处理流程

```mermaid
flowchart TD
    A[招标抓取 30min] --> B[tenders 表]
    B --> C[招标列表查看]
    C --> D{决策}
    D -->|投标| E[创建项目]
    D -->|不投| F[记录原因]
    E --> G[上传标书]
    G --> H[触发解析]
    H --> I[parse_status=已解析]
```

### 8.2 文档生成流程

```mermaid
flowchart TD
    A[点击生成] --> B[Service 查询模板/素材]
    B --> C[LLM 生成内容]
    C --> D[存储 editable_content]
    D --> E[计算打分点]
    E --> F[用户人工修改]
    F --> G[重评分]
    G --> H[更新评分历史]
```

### 8.3 技术案例匹配

```mermaid
flowchart TD
    A[请求匹配] --> B[/technical-cases/search]
    B --> C[按 keywords/tags 匹配]
    C --> D[返回相似案例]
    D --> E[用户选择关联]
    E --> F[关联到项目]
```

---

## 9. 部署指南

### 9.1 环境要求

| 组件 | 版本 |
|------|------|
| Python | 3.11+ |
| Node.js | LTS |
| 数据库 | SQLite (开发) / PostgreSQL (生产) |

### 9.2 后端启动

```bash
cd backend-v2
source .venv/bin/activate

# 开发
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 健康检查
curl http://localhost:8000/api/v1/health
```

### 9.3 前端启动

```bash
cd frontend-v2
npm install
npm run dev        # 端口 8081，代理 /api -> localhost:8000
npm run build      # 生产构建
npm run preview    # 预览
```

### 9.4 数据库初始化

```bash
# SQLite (默认，启动时自动创建)
uvicorn app.main:app --reload

# PostgreSQL
export DATABASE_URL_OVERRIDE=postgresql://user:pass@localhost:5432/saleagents
psql -h localhost -U bid_agent -d bid_agent -f database/init/001-init.sql
```

### 9.5 环境变量 (.env)

```bash
DATABASE_URL_OVERRIDE=sqlite:///./sale_agents_v2.db
FRONTEND_ORIGINS=http://localhost:8081
LLM_PROVIDER=zhipu
LLM_API_KEY=your_api_key
```

### 9.6 快速启动

```bash
./start.sh   # 启动后端 + 前端
./stop.sh    # 停止服务
```

---

## 10. 技术规格

| 项目 | 值 |
|------|------|
| API 前缀 | /api/v1 |
| 后端端口 | 8000 |
| 前端端口 | 8081 |
| 认证方式 | Bearer Token (JWT) |
| 定时任务 | 招标抓取每 30 分钟 |
| 导出路径 | /exports (backend-v2/exports/) |
