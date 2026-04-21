# SaleAgents v2 前端开发规范（SPEC）

> 本文档为 SaleAgents v2 前端项目的开发规范，供多 AI coding 智能体协作开发使用。
> 内容基于 `~/SaleAgents/frontend-v2/` 实际代码分析生成，不可凭空编造。

---

## 1. 技术栈声明

| 技术 | 版本/说明 | 备注 |
|------|-----------|------|
| Vue 3 | ^3.4.0 | Composition API + `<script setup>` 优先 |
| Vite | ^5.2.0 | 构建工具 |
| Tailwind CSS | ^3.4.3 | 设计系统基于此 |
| vue-router | ^4.3.0 | 路由 |
| 状态管理 | **暂不需要** | 跨组件数据靠 props/emit/query params；如需全局状态再引入 Pinia |
| HTTP 客户端 | **axios** | 请求封装，baseURL 配置 |
| TypeScript | **必须使用** | 实际架构需用 TS 重构所有 .vue/.js 文件 |

> ⚠️ **已确认决策**：
> - ✅ TypeScript **必须使用**（aibook 高保真仅作 UI 参考，实际架构需用 TS 重构所有 .vue/.js 文件）
> - ✅ HTTP 客户端：**axios**（参考旧前端 fetch 封装风格，但改用 axios 实例）
> - ❓ 状态管理：**暂不需要**（旧前端也无状态管理，跨组件数据靠 props/emit/query params；如需全局状态再引入 Pinia）
> - ✅ 登录权限**必须有**（JWT/Session 认证）
> - ❓ .env 配置（VITE_API_BASE）：待确认

---

## 2. 设计系统规范

### 2.1 主题色（Tailwind 配置）

```js
// tailwind.config.js
colors: {
  primary:    '#1A56DB',   // 主色（蓝）
  success:    '#10B981',   // 成功（绿）
  warning:    '#F59E0B',   // 警告（橙）
  danger:     '#EF4444',   // 危险（红）
  background: '#F8FAFC',   // 页面背景
  sidebar:    '#1E3A5F',   // 侧边栏背景（深蓝）
}
```

> ⚠️ `danger` 在 Tailwind 中已定义，但部分代码使用 `text-red-500` 硬编码，需统一。

### 2.2 字体规范

```css
/* style.css */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
```

- 使用系统字体栈，无自定义字体
- 中文字体由系统 fallback 解决

### 2.3 间距、圆角、阴影规范

| 用途 | Tailwind 类 |
|------|-------------|
| 页面容器内边距 | `px-4 py-8` / `p-6` |
| 卡片圆角 | `rounded-xl` / `rounded-lg` / `rounded-xl` |
| 卡片阴影 | `shadow-sm`（默认）/ `shadow-md`（hover） |
| 卡片边框 | `border border-gray-100` / `border-gray-200` |
| 按钮高度 | 固定 `height: 30px`（inline style）+ Tailwind `px-4 py-1.5` |
| 输入框圆角 | `rounded-lg` |
| 下拉框圆角 | `rounded-lg` |

### 2.4 常用组件模式

```html
<!-- 页面主卡片 -->
<div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">

<!-- 可点击卡片（带 hover 效果） -->
<div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all duration-300 cursor-pointer">

<!-- 输入框 -->
<input type="text" class="... border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary text-sm">

<!-- 主按钮 -->
<button class="px-4 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors">

<!-- 次要按钮 -->
<button class="px-4 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-100 transition-all">

<!-- 状态标签（颜色语义化） -->
<span class="px-3 py-1 rounded-full text-xs font-medium bg-success/10 text-success">进行中</span>
```

### 2.5 全局动画

```css
/* style.css 定义 */
.fade-in { animation: fade-in 0.5s ease-out; }
.typing-animation { /* 打字机效果 */ }
.progress-animation { /* 进度条效果 */ }
.pulse-ring { /* 脉冲环效果 */ }
```

---

## 3. 目录结构规范

```
~/SaleAgents/frontend-v2/
├── src/
│   ├── main.js              # 应用入口
│   ├── App.vue              # 根组件
│   ├── style.css           # 全局样式 + Tailwind 入口
│   ├── router/
│   │   └── index.js        # 路由定义
│   ├── layouts/
│   │   └── MainLayout.vue  # 主布局（含侧边栏）
│   ├── views/              # 页面（所有路由对应组件）
│   │   ├── Home.vue
│   │   ├── PreEvaluation.vue
│   │   ├── TenderList.vue
│   │   ├── TenderDetail.vue
│   │   ├── BidList.vue
│   │   ├── ProposalEditor.vue
│   │   ├── DemoWorkflow.vue
│   │   ├── PricingStrategy.vue
│   │   └── ProjectCreate.vue
│   └── assets/             # 静态资源
│       └── demo制作最终页面.html   # 仅有这一个文件
│
├── index.html              # HTML 入口
├── vite.config.js          # Vite 配置
├── tailwind.config.js      # Tailwind 主题配置
├── postcss.config.js       # PostCSS 配置
└── package.json            # 依赖定义
```

> ⚠️ 当前无 `components/`、`services/`、`types/`、`stores/`、`composables/` 等目录。如需扩展，请遵循本文档规范新建目录。

---

## 4. 组件规范

### 4.1 文件命名
- **页面组件**：大驼峰 `.vue`（如 `TenderList.vue`）
- **通用组件**：大驼峰 `.vue`（如 `BaseButton.vue`）
- **布局组件**：大驼峰 `.vue`（如 `MainLayout.vue`）

### 4.2 组件内部结构

```vue
<template>
  <!-- HTML 结构 -->
</template>

<script setup>
import { ref, computed } from 'vue'
// Composition API + <script setup> 语法
</script>

<style scoped>
/* 样式（scoped 优先） */
</style>
```

### 4.3 Props 定义（待 TypeScript 引入后）

```vue
<script setup>
// 当前为 JS，未来引入 TS 后应使用：
// interface Props { title: string; count?: number; }
// const props = defineProps<Props>()
// 或带默认值：
// const props = withDefaults(defineProps<Props>(), { count: 0 })
</script>
```

### 4.4 Emits 定义

```vue
<script setup>
const emit = defineEmits(['update', 'delete'])
// emit('update', payload)
</script>
```

---

## 5. API 层规范

> ⚠️ **已确认**：HTTP 客户端使用 **axios**，baseURL 环境变量 `VITE_API_BASE`，参考旧前端 `lib/api.ts` 的封装风格（请求/响应拦截器、错误处理）。

### 5.1 规范草案

- **API 服务文件位置**：`src/services/`（待创建）
- **请求封装**：使用 axios 实例，配置 `baseURL`
- **后端 base URL**：`http://localhost:8000/api/v1`
- **响应数据结构约定**：
  ```json
  {
    "data": { },
    "error": null,
    "message": "success"
  }
  ```
- **错误处理**：
  - `401` → 未认证，跳转登录页
  - `403` → 无权限，提示用户
  - `500` → 服务端错误，提示"系统繁忙"

### 5.2 环境变量（待创建 .env）

```env
VITE_API_BASE=http://localhost:8000/api/v1
```

---

## 6. 路由规范

### 6.1 路由定义位置
`src/router/index.js`

### 6.2 路由表

| 前端路径 | 路由名称 | 对应组件 | 后端端点（推测） |
|----------|----------|----------|------------------|
| `/` | Layout Root | MainLayout | - |
| `/home` | Home | Home.vue | -（首页/概览） |
| `/pre-evaluation` | PreEvaluation | PreEvaluation.vue | review.py |
| `/tender-list` | TenderList | TenderList.vue | projects.py |
| `/tender-detail/:id` | TenderDetail | TenderDetail.vue | projects.py |
| `/bid-list` | BidList | BidList.vue | generation.py |
| `/proposal-editor` | ProposalEditor | ProposalEditor.vue | proposal_editor.py |
| `/demo-workflow` | DemoWorkflow | DemoWorkflow.vue | （待定） |
| `/pricing-strategy` | PricingStrategy | PricingStrategy.vue | pricing.py |
| `/project-create` | ProjectCreate | ProjectCreate.vue | projects.py |

### 6.3 路由规范
- 所有子路由在 Layout 下嵌套（通过 `children` 数组）
- 动态路由参数使用 `:id` 格式（如 `/tender-detail/:id`）
- 前端路由使用 `createWebHistory`（HTML5 History 模式）
- **当前无路由守卫**（无登录验证逻辑）

### 6.4 导航守卫示例（待实现）
```js
router.beforeEach((to, from, next) => {
  // TODO: 检查登录状态
  next()
})
```

---

## 7. Tailwind CSS 使用规范

### 7.1 工具类 vs 自定义组件类
- **优先使用工具类**：颜色、间距、圆角、阴影等优先用 Tailwind 工具类
- **自定义类用于动画/复杂样式**：在 `style.css` 或 `<style>` 中定义（如 `.fade-in`、`.typing-animation`）
- **避免大量 inline style**：除高度/宽度精确值外，优先用 Tailwind 类

### 7.2 颜色类使用规范
| 场景 | 使用方式 |
|------|----------|
| 主题色（按钮背景） | `bg-primary` + `hover:bg-primary/90` |
| 文字主色 | `text-primary` |
| 成功状态 | `text-success` / `bg-success/10` |
| 警告状态 | `text-warning` / `bg-warning/10` |
| 危险/错误 | ⚠️ 部分代码用 `text-red-500`，建议统一为 `text-danger` |
| 边框颜色 | `border-gray-100`（浅）/ `border-gray-200`（中）/ `border-gray-300`（深） |
| 背景 | `bg-white` / `bg-gray-50` / `bg-background` |

### 7.3 响应式断点使用规范
| 断点 | 类前缀 | 典型用法 |
|------|--------|----------|
| 移动端 | 无前缀 | 默认 |
| 平板 | `md:` | `md:grid-cols-2` |
| 桌面 | `lg:` | `lg:grid-cols-3` |

### 7.4 常见工具类
```
flex/grid: flex, flex-col, grid, grid-cols-3
间距: space-x-4, gap-6, p-6, px-4, py-8, mb-6
圆角: rounded-lg, rounded-xl, rounded-full
阴影: shadow-sm, shadow-md, hover:shadow-md
动画: transition-all, transition-colors, duration-300
文字: text-sm, text-lg, font-semibold, text-gray-500
```

---

## 8. TypeScript 规范

> ⚠️ **待确认**：当前项目无 TypeScript。下方为规范草案。

- **类型定义位置**：`src/types/`（待创建）
- **接口命名**：PascalCase（如 `User`, `Project`, `TenderDetail`）
- **必填 vs 可选**：使用 `?` 标记可选字段
  ```ts
  interface Project {
    id: string;
    name: string;
    client?: string;  // 可选
    status: '进行中' | '已截止' | '草稿';
  }
  ```
- Props 定义使用 `defineProps<Props>()` 或 `withDefaults`

---

## 9. Git 协作规范（多 AI Agent 用）

### 9.1 分支命名
```
feature/<功能名>      # 新功能，如 feature/tender-detail-page
fix/<问题描述>        # 修复，如 fix/upload-file-bug
refactor/<范围>       # 重构，如 refactor/api-layer
docs/<范围>          # 文档更新
```

### 9.2 Commit 信息格式
```
<type>: <description>

type: feat | fix | docs | style | refactor | test | chore
```

示例：
```
feat: add tender detail page with project info display
fix: resolve sidebar collapse state not persisting
docs: update SPEC.md with new routing rules
style: adjust card hover shadow transition
refactor: extract API calls to services layer
```

### 9.3 PR / Merge 流程
- **直接合并 main**：当前阶段 AI agent 开发可直接合并到 `main`
- **后续（建议）**：引入 PR review 机制，每位 agent 的 PR 需另一位 agent review 后合并
- **冲突处理**：合并前确保 `main` 最新，用 `git merge main` 解决冲突

### 9.4 AI Agent 协作注意事项
- 每个 agent 负责一个独立功能模块（如 `feature/proposal-editor`）
- 修改共享文件（如 `router/index.js`、`MainLayout.vue`）前先同步其他 agent
- 使用清晰的 commit message 便于追溯

---

## 10. 已知页面清单

| 文件 | 前端路由 | 后端推测端点 | 说明 |
|------|----------|--------------|------|
| `Home.vue` | `/home` | -（首页/概览） | 平台首页，含 Tab 导航（投标前评估/标书制作/DEMO制作） |
| `PreEvaluation.vue` | `/pre-evaluation` | `review.py` | 投标前评估 |
| `TenderList.vue` | `/tender-list` | `projects.py` | 招标项目列表，含筛选/搜索 |
| `TenderDetail.vue` | `/tender-detail/:id` | `projects.py` | 项目详情，含基本信息/招标要求/投标文件 |
| `BidList.vue` | `/bid-list` | `generation.py` | 回标文件列表 |
| `ProposalEditor.vue` | `/proposal-editor` | `proposal_editor.py` | 技术建议书编辑器 |
| `DemoWorkflow.vue` | `/demo-workflow` | （待定） | DEMO 制作流程 |
| `PricingStrategy.vue` | `/pricing-strategy` | `pricing.py` | 报价策略 |
| `ProjectCreate.vue` | `/project-create` | `projects.py` | 新增项目 |

---

## 11. 开发注意事项

### 11.1 环境配置
- **无 .env 文件**：当前未创建 `.env` 文件；后端地址待确认后创建
- **Vite 配置**：`vite.config.js` 目前仅含 Vue 插件，无代理配置；后端联调时可能需要添加：
  ```js
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true }
    }
  }
  ```

### 11.2 本地开发依赖
- 前端：`npm run dev` → `http://localhost:5173`
- 后端：`http://localhost:8000/api/v1`（待确认）

### 11.3 常见坑点

| 坑点 | 说明 |
|------|------|
| `danger` vs `red` | Tailwind 配置了 `danger: '#EF4444'`，但部分代码用 `text-red-500` 硬编码，需统一 |
| 路由参数读取 | `TenderDetail.vue` 通过 `route.params.id` 获取项目 ID，需确保类型为 string |
| `uploadedFiles` 状态 | `Home.vue` 的 `uploadedFiles` 只绑定一份，三个 Tab 共用；可能导致切换 Tab 后文件丢失 |
| 布局层级 | `MainLayout.vue` 的 `<main>` 使用 `flex-1 overflow-auto`，子页面需自行控制内边距 |
| 状态管理缺失 | 当前无全局状态管理，跨组件数据共享靠 props/emit 或 query params |
| API 层缺失 | 当前无 HTTP 请求代码，所有数据均为 mock（硬编码数组） |

### 11.4 待完成任务

1. **API 层建设**：创建 `services/` 目录，引入 axios，封装请求
2. **TypeScript 引入**（可选）：迁移 `.js` → `.ts`，建立 `types/` 目录
3. **状态管理**（可选）：如需全局状态，引入 Pinia
4. **.env 配置**：创建 `.env` 文件，配置 `VITE_API_BASE`
5. **路由守卫**：登录态校验（待后端确认）
6. **错误处理**：统一错误提示组件
7. **组件拆分**：`views/` 中的重复 UI（如筛选栏、上传组件）应抽取到 `components/`

---

## 附录：MainLayout.vue 侧边栏菜单配置

```js
const menuItems = [
  { name: '首页',         path: '/home',              icon: '🏠' },
  { name: '标前评估',     path: '/pre-evaluation',     icon: '📊' },
  { name: '招标项目',     path: '/tender-list',        icon: '📋' },
  { name: '回标文件',     path: '/bid-list',           icon: '📁' },
  { name: '技术建议书',   path: '/proposal-editor',     icon: '✍️' },
  { name: 'DEMO制作',     path: '/demo-workflow',       icon: '🎬' },
  { name: '报价策略',     path: '/pricing-strategy',    icon: '💰' },
]
```

侧边栏可折叠（`isSidebarCollapsed`），折叠后宽度 80px，展开宽度 200px。

---

_本文档由 AI 架构师基于 `~/SaleAgents/frontend-v2/` 源码分析生成，如有疑问请在协作群里提问。_

---

## 设计系统（Design System）

### 配色系统

| Token | 色值 | 用途 |
|---|---|---|
| primary | `#1A56DB` | 主按钮、聚焦边框、链接 |
| primary-light | `#2563EB` | 渐变终点 |
| primary-hover | `#1E40AF` | 按钮悬停 |
| success | `#10B981` | 成功状态 |
| warning | `#F59E0B` | 警告状态 |
| danger | `#EF4444` | 错误提示 |
| bg-page | `#F9FAFB` | 页面背景 |
| bg-card | `#FFFFFF` | 卡片背景 |
| bg-input | `#F9FAFB` | 输入框背景 |
| border | `#E5E7EB` | 默认边框 |
| border-focus | `#1A56DB` | 聚焦边框 |
| text-primary | `#1E293B` | 主标题 |
| text-body | `#374151` | 正文 |
| text-sub | `#64748B` | 副文本 |
| text-placeholder | `#9CA3AF` | 占位符 |

### 登录页布局（参考实现）

```
┌─────────────────────┬──────────────────────────────────┐
│  品牌区（蓝渐变）     │  表单区（白色）                    │
│  520px              │  520px                           │
│                     │                                  │
│  [Logo]             │  欢迎回来                        │
│  SaleAgents         │  请登录您的账号以继续              │
│  AI标书智能体平台     │                                  │
│                     │  用户名 / 手机号  [___________]   │
│  ● 智能招标分析       │  密码          [___________] 👁   │
│  ● 自动生成应答文件   │                                  │
│  ● 定价策略优化       │  [         登 录         ]       │
│                     │                                  │
│    ○ ○ (装饰圆形)    │  ───── 或使用演示账号 ─────       │
│                     │  [管理员]  [普通用户]              │
└─────────────────────┴──────────────────────────────────┘
```

### 组件规范

#### 输入框
- 高度：44px（padding 0.875rem 1rem）
- 背景：`#F9FAFB`，聚焦时 `#FFFFFF`
- 边框：`1.5px solid #E5E7EB`，聚焦时 `#1A56DB` + `box-shadow: 0 0 0 3px rgba(26,86,219,0.1)`
- 左侧图标：`#9CA3AF`，垂直居中，input 内 `padding-left: 2.75rem`
- 圆角：10px
- 错误态：边框 `#EF4444`

#### 主按钮
- 高度：48px（padding 0.9375rem）
- 背景：`linear-gradient(to right, #1A56DB, #2563EB)`
- 投影：`box-shadow: 0 4px 14px rgba(26,86,219,0.25)`
- 悬停：`transform: translateY(-1px)` + `box-shadow: 0 6px 20px rgba(26,86,219,0.35)`
- 圆角：10px
- 字体：600，letter-spacing 0.05em

#### 演示账号按钮
- 背景：`#F9FAFB`
- 边框：`1.5px solid #E5E7EB`
- 圆角：10px
- 悬停：`#F3F4F6` 背景 + `#D1D5DB` 边框
- 角色名：0.75rem 600 weight，凭证：0.7rem

#### 错误提示
- 背景：`#FEF2F2`
- 边框：`1px solid #FECACA`
- 圆角：10px
- 颜色：`#DC2626`
- 带 SVG 图标 + fade 动画

### 动效规范

- 默认过渡：`all 0.2s`
- 按钮投影过渡：`all 0.25s`
- 错误提示淡入：`opacity 0.3s`
- spinner：`border-top-color white, 0.7s linear infinite`

### 字体

```
-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif
```

### 响应式断点

- `≥901px`：左右分栏布局（品牌区 + 表单区）
- `≤900px`：左侧品牌区隐藏，单列白色表单

### 应用范围

所有页面（ TenderList / BidList / PreEvaluation / PricingStrategy / ProposalEditor 等）统一采用此设计系统。
