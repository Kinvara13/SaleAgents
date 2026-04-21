# PROGRESS.md - 项目进度

> SaleAgents frontend-v2 开发进度追踪，供多 AI Agent 协作使用。
> 每次状态变化后更新此文件。

---

## 📋 任务总览

| 模块 | 状态 | 负责人 | 备注 |
|------|------|--------|------|
| mock 数据清除 | ✅ DONE | — | 全部视图文件已清除 |
| axios API 层 | ✅ DONE | — | services/.ts + types/index.ts |
| 后端接口对接 | ✅ DONE | — | TenderList/TenderDetail/BidList/PreEvaluation |
| 登录 + JWT 鉴权 | ✅ DONE | — | Login.vue + 路由守卫 |
| proposal_editor.py | ✅ DONE | — | 后端路由已注册 |
| pricing.py | ✅ DONE | — | 后端路由已注册 |
| auth.py | ✅ DONE | — | 后端已存在且完善 |

---

## 🔄 当前开发任务

### 主任务：前后端拉通 + 登录权限

**状态**：✅ 已完成

**详细子任务**：

- [x] 清除所有 mock 数据（src/views/ 下全部 .vue 文件）
- [x] 创建 `src/services/api.ts`（axios 封装，Token 键名 `sa_token`）
- [x] 创建 `src/services/auth.ts`（登录 API）
- [x] 创建 `src/types/index.ts`（TS 类型定义）
- [x] 新建 `src/views/Login.vue`（登录页，已 TS 化）
- [x] 实现路由守卫（未登录跳转 /login）
- [x] 对接 TenderList → `GET/POST /api/v1/projects`
- [x] 对接 TenderDetail → `GET /api/v1/projects/:id`
- [x] 对接 BidList → `GET /api/v1/generation`
- [x] 对接 PreEvaluation → `GET /api/v1/review`
- [x] 后端 `router.py` 注册 `/pricing` 和 `/proposal-editor`
- [x] 前端构建通过（npm run build ✅）

---

## 📦 已完成

- [x] SPEC.md 初始化完成
- [x] 项目结构搭建（Vue 3 + Vite + Tailwind）
- [x] 技术栈决策（TypeScript + axios + 无 Pinia）
- [x] aibook 代码同步完成
- [x] 前后端拉通完成（2026-04-20）

---

## 🧠 知识库（待建设）

- [ ] ARCHITECTURE.md（系统架构图）
- [ ] API.md（接口文档）
- [ ] DESIGN.md（设计规范）

---

## 📝 开发规范

1. 每完成一个模块做 commit，commit 信息格式：`feat: [模块名] [简短描述]`
2. 遇到不确定的地方，先停下来问，不要盲目猜测
3. 所有 .vue 文件使用 TypeScript（`<script setup lang="ts">`）
4. API 调用统一走 `src/services/` 目录
5. Token 存储在 localStorage，键名：`sa_token`

---

*最后更新：2026-04-20*
