# SaleAgents v2 测试报告

生成日期：2026-04-21  
测试范围：根目录统一审计产物对应的静态检查 + 最小运行态烟测  
测试基线：`backend-v2`、`frontend-v2`

## 1. 环境结论

- 默认 `python3`：`3.9`
- 可用运行版本：`python3.11`
- 前端构建：`npm run build` 通过
- 浏览器自动化：仓库中未发现现成框架

关键环境发现：

- 使用默认 `python3` 启动 `backend-v2` 会在导入阶段失败，因为代码使用了 Python 3.10+ 的联合类型语法 `str | None`
- 使用 `python3.11` 启动后，后端可正常提供大部分 API

## 2. 修正历史结论

相较于旧的 `memory-bank/TEST_REPORT.md`，本轮确认以下结论已经变化：

- `DELETE /api/v1/chat/{project_id}/history`：当前返回 `200`，旧报告中的 `405` 已失效
- `POST /api/v1/users`：当前返回 `201`，旧报告中的 bcrypt 500 结论已失效
- `POST /api/v1/proposal-editor/{project_id}/generate`：当前可返回章节列表，旧报告中的固定 500 结论已失效
- `POST /api/v1/settings/rules`：当前可返回 `201`，旧报告中“接口设计异常”的结论已过时

## 3. 后端运行态烟测

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| `POST /api/v1/auth/login` | 通过 | 返回 access_token / refresh_token |
| `DELETE /api/v1/chat/test_project/history` | 通过 | 返回 `{"message":"Chat history cleared"}` |
| `GET /api/v1/projects` | 通过 | 返回项目列表 |
| `POST /api/v1/projects` | 通过 | 返回新建项目 `proj_9e7d...` |
| `GET /api/v1/tenders` | 通过 | 返回招标信息列表 |
| `GET /api/v1/users/roles/list` | 通过 | 返回角色与权限列表 |
| `POST /api/v1/users` | 通过 | 返回新建用户对象 |
| `POST /api/v1/settings/rules` | 通过 | 返回新规则对象 |
| `GET /api/v1/projects/{id}/business-documents` | 通过 | 返回 13 个商务文档模板 |
| `GET /api/v1/projects/{id}/technical-documents` | 通过 | 返回技术文档模板列表 |
| `GET /api/v1/projects/{id}/proposal-plans` | 通过 | 返回 4 个方案建议书模板 |
| `GET /api/v1/projects/{id}/technical-cases` | 通过 | 返回空列表，接口可调用 |
| `POST /api/v1/proposal-editor/{id}/generate` | 通过 | 返回生成章节列表 |
| `POST /api/v1/proposal-editor/{id}/score` | 通过 | 返回 `sections` + `total_score` |
| `POST /api/v1/pricing/calculate` | 通过 | 使用符合 schema 的 payload 成功返回报价结果 |

## 4. 当前失败/阻塞项

| 检查项 | 结果 | 根因 |
| --- | --- | --- |
| `GET /api/v1/health` | 失败，404 | `health.py` 定义了路由，但 `backend-v2/app/api/router.py` 未注册 `health.router` |
| `GET /api/v1/settings/ai-config` | 失败，500 | SQLite 表 `ai_configs` 缺少 `name` 列，属于数据库 schema 漂移 |
| `GET /api/v1/settings/ai-configs` | 失败，500 | 同上 |
| `python3 -m uvicorn app.main:app` | 失败 | 默认 `python3` 为 3.9，不满足代码语法要求 |

## 5. 前端静态检查结果

### 通过项

- `frontend-v2` 构建通过
- 路由表存在并可覆盖主流程页面
- 大多数核心页面已经有对应 service 或 API 调用入口

### 关键问题

#### `ProposalEditor.vue`

- 把 axios 响应当作 fetch `Response` 使用：
  - 读取 `res.ok`
  - 调用 `res.json()`
- 多处动态路径写成普通字符串，如 `'/proposal-editor/${projectId}/score'`
- 影响：技术建议书生成、评分、重评分、确认、详情获取在页面侧大概率失效

#### `UserManagement.vue`

- `PATCH /users/${id}`、`DELETE /users/${id}` 等路径写成普通字符串
- 同样把 axios 响应当作 fetch 使用
- 影响：用户编辑、删除、启停用在页面侧不可靠

#### `RoleManagement.vue`

- 仍按 fetch 风格处理 axios 响应
- 影响：角色列表页面数据加载逻辑不可靠

#### `SystemSettings.vue`

- 页面契约对的是 `/settings/ai-configs`，但当前接口被数据库 schema 阻塞
- 规则区基本可用，AI 配置区当前不可用

## 6. 覆盖边界

本轮已经完成：

- 根目录审计文档落地
- 当前代码静态覆盖梳理
- Python 3.11 环境下的后端最小烟测
- 前端构建验证

本轮未完成：

- 页面级人工走查
- 浏览器自动化验证
- 文件上传类真实样本回归
- 解析章节、星标项、素材库自动填充和人工确认节点的端到端回归
