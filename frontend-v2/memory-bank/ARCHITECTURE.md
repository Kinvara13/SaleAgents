# ARCHITECTURE.md - 系统架构

> 历史参考：本文件内容包含已过期目录和技术结论。
> 当前有效入口：
> - `../../specs/engineering-spec.md`
> - `../../specs/backend-dev-spec.md`
> - `../../specs/frontend-style-spec.md`
> - `../../specs/api-contract-spec.md`
> - `../../memory-bank/PAGE_COVERAGE_V2.md`
> 除非做历史回顾，否则不要把本文件当主事实源。

---

## 1. 项目结构

```
~/SaleAgents/
├── backend/                         # FastAPI 后端（当前状态保留）
│   └── app/
│       └── api/v1/
│           ├── projects.py          # 招标项目管理 API
│           ├── generation.py        # 投标文件生成 API
│           ├── review.py            # 预审 API
│           └── auth.py              # [待新建] JWT 认证
│       ├── core/
│       │   ├── config.py
│       │   └── security.py
│       ├── models/
│       ├── schemas/
│       └── main.py
├── frontend/                        # 旧前端（React）
└── frontend-v2/                     # 新前端（Vue 3）← 当前开发
    ├── src/
    │   ├── views/                   # 页面组件
    │   │   ├── TenderList.vue       # 招标台账
    │   │   ├── TenderDetail.vue     # 招标详情
    │   │   ├── BidList.vue          # 应答列表
    │   │   ├── ProposalEditor.vue   # 应答编辑器
    │   │   ├── PricingStrategy.vue  # 报价策略
    │   │   ├── PreEvaluation.vue    # 预审
    │   │   ├── ProjectCreate.vue    # 项目创建
    │   │   ├── DemoWorkflow.vue    # 工作流演示
    │   │   └── Home.vue
    │   ├── layouts/
    │   │   └── MainLayout.vue       # 主布局（侧边栏 + 内容区）
    │   ├── services/                # [待新建] API 层
    │   │   ├── api.ts              # axios 封装 + 拦截器
    │   │   └── auth.ts             # 登录相关 API
    │   ├── router/
    │   │   └── index.ts             # [待补充] 路由守卫
    │   ├── stores/                  # 暂不使用 Pinia
    │   ├── types/                  # [待新建] TS 类型定义
    │   ├── App.vue
    │   ├── main.ts
    │   └── style.css
    ├── memory-bank/                 # 多 Agent 协作知识库
    │   ├── PROGRESS.md             # 任务进度追踪
    │   └── ARCHITECTURE.md         # 本文件
    ├── SPEC.md                      # 开发规范（决策记录）
    └── vite.config.ts
```

---

## 2. 前端技术栈

| 技术 | 用途 |
|------|------|
| Vue 3 + Composition API | 框架 |
| `<script setup lang="ts">` | 所有 .vue 文件必须 TS |
| Vite | 构建工具 |
| Tailwind CSS | 样式系统（主题色见 SPEC.md）|
| vue-router 4 | 路由（含路由守卫）|
| axios | HTTP 客户端 |

---

## 3. 后端技术栈

| 技术 | 用途 |
|------|------|
| FastAPI | Web 框架 |
| MongoDB | 数据库 |
| JWT | 认证（待新建 auth.py）|
| Python 3.11 | 运行环境 |

---

## 4. API 约定

### 前端 → 后端通信

- Base URL：`.env` 中 `VITE_API_BASE=http://localhost:8000`
- Token 放在请求头：`Authorization: Bearer <token>`
- 请求/响应使用 JSON

### 后端路由前缀
所有 API 统一前缀：`/api/v1/`

---

## 5. 登录流程

```
用户输入账号密码
    ↓
POST /api/v1/auth/login
    ↓
后端返回 { token, user }
    ↓
前端存 localStorage['sa_token']
    ↓
后续请求 Authorization: Bearer <token>
```

---

## 6. 数据流

```
前端 (Vue 3 axios)
    ↓ HTTP 请求
后端 (FastAPI)
    ↓ 调用
MongoDB / 文件存储
```

---

*最后更新：2026-04-20 19:13*
