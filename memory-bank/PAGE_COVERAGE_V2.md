# SaleAgents v2 页面覆盖矩阵

更新日期：2026-04-21  
说明：本文件按“页面/路由 -> service -> API -> 功能点”反查覆盖情况。  
状态说明：`覆盖` / `部分覆盖` / `非功能入口` / `排除范围`

| 路由 | View | 调用 service / API | 覆盖功能点 | 缺失交互 | 缺失测试 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| `/login` | `Login.vue` | `auth.ts`; `/auth/login` | 支撑能力-登录鉴权 | 未见 refresh 失败回收、异常提示细化 | 未做页面走查，仅 API 烟测 | 部分覆盖 |
| `/home` | `Home.vue` | `listProjects`; 本地文件上传态 | 首页工作台雏形；不直接对应 34 功能点 | 上传仍是本地状态，未接真实解析流程 | 未做页面走查 | 非功能入口 |
| `/tender-info-list` | `TenderInfoList.vue` | `listTenders`; `/tenders` | F049-F051 | 无定时刷新、无来源筛选、无推送状态 | 页面未走查；只做列表 API 烟测 | 部分覆盖 |
| `/tender-info/:id` | `TenderInfoDetail.vue` | `getTender`; `submitDecision`; `uploadBidDocument` | F050-F051 | 缺保证金/项目类型输入；投/不投异常态和上传回调未回归 | 未做页面走查；未对决策/上传做运行态验证 | 部分覆盖 |
| `/bid-list` | `BidList.vue` | `listProjects`; `createProject`; `updateProject`; `deleteProject` | F052-F053 | 未展示重点字段、文件清单、节点工作台；仅基础台账 | 页面未走查；CRUD 只做 API 烟测 | 部分覆盖 |
| `/project-create` | `ProjectCreate.vue` | `listProjects`; 其余多为本地状态 | F052-F053 的上传/创建入口候选 | 文件解析、模板上传、引用区多数未接真实 API | 未做页面走查 | 部分覆盖 |
| `/tender-list` | `TenderList.vue` | `listProjects` | 与 `BidList` 能力重叠，承担项目入口 | 与 v2 主流程重叠；需决定保留还是合并 | 页面未走查 | 部分覆盖 |
| `/bid-list/:projectId/tender-detail` | `TenderDetail.vue` | `project.ts`; `tender.ts`; `businessDocument.ts`; `technicalDocument.ts`; `proposalPlan.ts`; `technicalCase.ts` | F054-F079；F081 | 上传解析未做实测；节点工作台、人工确认、重算逻辑不完整 | 仅做列表类 API 烟测，未做页面交互 | 部分覆盖 |
| `/bid-list/:projectId/proposal` | `ProposalEditor.vue` | 直接调用 `api` + `project.ts` | F082；并承载技术建议书生成/打分 | 把 axios 当 fetch 使用；多处动态路径写错；确认流和评分展示大概率失效 | 后端 generate/score 已测，页面未测 | 部分覆盖 |
| `/pricing-strategy` | `PricingStrategy.vue` | `project.ts`; `pricing.ts` | F080 | 仅待页面级回归 | 后端 calculate 已测，页面未走查 | 覆盖 |
| `/pre-evaluation` | `PreEvaluation.vue` | `preEvaluation.ts` | 标前评估支撑能力，不计入 34 功能点 | 与主流程的数据回传关系未说明 | 页面未走查 | 部分覆盖 |
| `/user-management` | `UserManagement.vue` | 直接调用 `api` | 支撑能力-用户管理 | axios/fetch 混用； PATCH/DELETE 动态路径写错 | 后端 `/users` 已测，页面未走查 | 部分覆盖 |
| `/role-management` | `RoleManagement.vue` | 直接调用 `api` | 支撑能力-角色管理 | axios/fetch 混用；列表读取逻辑错误 | `/users/roles/list` 已测，页面未走查 | 部分覆盖 |
| `/system-settings` | `SystemSettings.vue` | 直接调用 `api` | 支撑能力-系统设置 | AI 配置接口受数据库 schema 阻塞；页面未做兼容降级 | `/settings/rules` 已测； AI 配置 500 | 部分覆盖 |
| `/demo-workflow` | `DemoWorkflow.vue` | 无 | demo 制作流程 | 本轮排除 | 不在本轮测试范围 | 排除范围 |

## 页面层关键发现

### 1. 页面已经存在，但不等于功能闭环

- `TenderDetail.vue` 已经承载商务文档、技术文档、方案建议书和技术案例多个区块，但当前证据更多是“模板与列表存在”，不是“真实项目数据闭环”。
- `BidList.vue` 能做项目 CRUD，但距离 Excel 第 53 行要求的“项目工作台”差距仍大。

### 2. 直接使用 `api.ts` 的页面存在统一风险

- `ProposalEditor.vue`
- `UserManagement.vue`
- `RoleManagement.vue`
- `SystemSettings.vue`

这些页面中至少一部分代码把 axios 响应当作 fetch `Response` 使用，表现为：

- 读取 `res.ok`
- 调用 `res.json()`
- 动态路径写成普通字符串，如 `'/users/${id}'`

这类问题不会阻止 `vite build`，但会在运行态直接影响功能。

### 3. 页面测试现状

- 已完成：`frontend-v2` 构建通过。
- 未完成：暂无浏览器自动化；暂无系统性人工走查记录。
- 结论：当前“页面覆盖”只能判定到静态接线级别，不能替代真实交互验收。
