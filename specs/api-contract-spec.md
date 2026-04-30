# SaleAgents v2 API 契约规范

更新日期：2026-04-21  
真实注册入口：`backend-v2/app/api/router.py`

## 1. 契约原则

- 以当前已注册路由为准
- 任何公开 API 变更先更新本文件
- 兼容接口必须明确标注 `legacy`

## 2. 主要接口分组

### 认证

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

当前结论：

- `login` 已运行态通过

### 项目

- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{project_id}`
- `PATCH /api/v1/projects/{project_id}`
- `DELETE /api/v1/projects/{project_id}`
- `POST /api/v1/projects/{project_id}/confirm`

当前结论：

- 列表、创建已运行态通过

### 招标信息

- `GET /api/v1/tenders`
- `POST /api/v1/tenders`
- `GET /api/v1/tenders/{tender_id}`
- `POST /api/v1/tenders/{tender_id}/decision`
- `POST /api/v1/tenders/{tender_id}/upload`

当前结论：

- 列表已运行态通过
- 决策与上传待补运行态验证

### 解析

- `POST /api/v1/parsing/{project_id}/upload`
- `GET /api/v1/parsing/{project_id}/sections`
- `GET /api/v1/parsing/{project_id}/sections/{section_id}`
- `PATCH /api/v1/parsing/{project_id}/sections/{section_id}`

当前结论：

- `sections` 列表已返回空数组
- 真实样本上传与章节详情待回归
- 2026-04-30：解析链路保持原接口不变，后端改为本地 PDF/OCR、Word、Excel 文本提取优先；LLM 仅基于本地抽取文本补充字段匹配，失败时降级为规则/关键词抽取。`extracted_fields` 继续返回 `{label,value,confidence}` 列表；压缩包内多文件解析会按字段增量合并，后续附件不得清空前序文件已抽取的基本信息。星标项来源限定为真实关键/星标条款，模板占位章节不再标记为星标。

### 商务文档

- `GET /api/v1/projects/{project_id}/business-documents`
- `GET /api/v1/projects/{project_id}/business-documents/{doc_id}`
- `PATCH /api/v1/projects/{project_id}/business-documents/{doc_id}`

### 技术文档

- `GET /api/v1/projects/{project_id}/technical-documents`
- `GET /api/v1/projects/{project_id}/technical-documents/{doc_id}`
- `PATCH /api/v1/projects/{project_id}/technical-documents/{doc_id}`

### 方案建议书

- `GET /api/v1/projects/{project_id}/proposal-plans`
- `GET /api/v1/projects/{project_id}/proposal-plans/{doc_id}`
- `PATCH /api/v1/projects/{project_id}/proposal-plans/{doc_id}`

### 技术案例

- `GET /api/v1/projects/{project_id}/technical-cases`
- `GET /api/v1/projects/{project_id}/technical-cases/{case_id}`
- `POST /api/v1/projects/{project_id}/technical-cases`
- `PATCH /api/v1/projects/{project_id}/technical-cases/{case_id}`
- `DELETE /api/v1/projects/{project_id}/technical-cases/{case_id}`
- `GET /api/v1/projects/{project_id}/technical-cases-search/search`

### 技术建议书

- `POST /api/v1/proposal-editor/{project_id}/generate`
- `GET /api/v1/proposal-editor/{project_id}/sections`
- `GET /api/v1/proposal-editor/{project_id}/sections/{section_id}`
- `PATCH /api/v1/proposal-editor/{project_id}/sections/{section_id}`
- `POST /api/v1/proposal-editor/{project_id}/score`
- `POST /api/v1/proposal-editor/{project_id}/rescore`
- `POST /api/v1/proposal-editor/{project_id}/confirm`
- `GET /api/v1/proposal-editor/{project_id}/scoring-rules`
- `GET /api/v1/proposal-editor/{project_id}/export/docx`

当前结论：

- `generate`、`score` 已运行态通过
- 2026-04-30：`generate`、章节编辑、`rescore`、`confirm`、`export/docx` 使用临时 SQLite smoke 通过

### 回标模板

- `POST /api/v1/bid-template/{project_id}/upload-template`
- `GET /api/v1/bid-template/{project_id}/template-files`
- `GET /api/v1/bid-template/{project_id}/template-files/{file_path}/preview`
- `PUT /api/v1/bid-template/{project_id}/template-files`

当前结论：

- 2026-04-30：模板文件清洗会过滤招标文件、按文件名/路径分类到商务/技术/方案/其他，并对重复路径去重；`GET /projects/{project_id}/bid-progress` 优先展示清洗后的回标模板文件。

### 报价

- `POST /api/v1/pricing/calculate`

当前结论：

- 运行态通过
- `tax_rate` 当前要求 `<= 1`
- `risk_factor` 当前按整数校验

### 用户与角色

- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `DELETE /api/v1/users/{user_id}`
- `GET /api/v1/users/roles/list`

当前结论：

- 用户创建、角色列表已运行态通过

### 聊天

- `POST /api/v1/chat/{project_id}/message`
- `GET /api/v1/chat/{project_id}/history`
- `POST /api/v1/chat/{project_id}/context`
- `DELETE /api/v1/chat/{project_id}/history`

当前结论：

- `DELETE history` 已运行态通过

### 系统设置

#### legacy 单配置

- `GET /api/v1/settings/ai-config`
- `PATCH /api/v1/settings/ai-config`

#### 当前多配置

- `GET /api/v1/settings/ai-configs`
- `POST /api/v1/settings/ai-configs`
- `PATCH /api/v1/settings/ai-configs/{config_id}`
- `DELETE /api/v1/settings/ai-configs/{config_id}`
- `POST /api/v1/settings/ai-configs/{config_id}/activate`

#### 素材与规则

- `GET /api/v1/settings/materials`
- `POST /api/v1/settings/materials/upload`
- `GET /api/v1/settings/rules`
- `POST /api/v1/settings/rules`

当前结论：

- `rules` 创建已通过
- `ai-config` 与 `ai-configs` 数据库 schema 已补齐（`name` 列已添加），端点逻辑已接入 `settings_service`，运行态待回归验证

## 3. 已解决的契约漂移

- ~~`health.py` 定义了 `/health`，但未在 `app/api/router.py` 注册~~ → 已在 `router.py` 注册，`GET /api/v1/health` 运行态通过
- ~~前端 `ProposalEditor.vue`、`UserManagement.vue`、`RoleManagement.vue` 对 axios 的使用不符合当前接口调用方式~~ → FE-001/FE-002 已修复

## 4. 待补运行态验证

- `/api/v1/settings/ai-config*` 全组接口
- `/api/v1/tenders/{tender_id}/decision` 与 `/api/v1/tenders/{tender_id}/upload`
- `/api/v1/parsing/{project_id}/upload` 真实样本上传与章节详情

## 5. 契约变更流程

1. 先修改本文件
2. 再修改后端代码
3. 再修改前端调用
4. 最后更新 `TEST_PLAN_V2.md` 与 `TEST_REPORT_V2.md`
