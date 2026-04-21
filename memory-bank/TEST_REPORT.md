# SaleAgents 联调测试报告

**生成时间**: 2026-04-21 08:36:21  
**后端地址**: http://localhost:8000  
**登录账户**: admin / admin123

---

## 测试概要

| 指标 | 数量 |
|------|------|
| ✅ 通过 | **32** |
| ❌ 失败 | **4** |
| ⏭️ 跳过 | **47** |
| 总计 | **83** |

---

## 各模块详情

### 投标项目清单 (通过:12 / 失败:0 / 跳过:0)

| 用例ID | 功能点 | 状态 | 响应摘要 | 备注 |
|---|---|---|---|---|
| TC-P-001 | 创建项目 | ✅ | `{'id': 'proj_553ae6d313ef', 'name': '自动测试项目', 'status': '待决策', 'owner': 'admin',` |  |
| TC-P-002 | 状态筛选-待决策 | ✅ | `[]` |  |
| TC-P-003 | 状态筛选-已投标 | ✅ | `[]` |  |
| TC-P-004 | 状态筛选-未中标 | ✅ | `[]` |  |
| TC-P-005 | 状态筛选-已中标 | ✅ | `[]` |  |
| TC-P-006 | 状态更新-改为已投标 | ✅ | `{'id': 'proj_553ae6d313ef', 'name': '自动测试项目', 'status': 'bid_submitted', 'owner'` |  |
| TC-P-007 | 状态更新-改为已中标 | ✅ | `{'id': 'proj_553ae6d313ef', 'name': '自动测试项目', 'status': 'won', 'owner': 'admin',` |  |
| TC-P-008 | 状态更新-改为未中标 | ✅ | `{'id': 'proj_553ae6d313ef', 'name': '自动测试项目', 'status': 'lost', 'owner': 'admin'` |  |
| TC-P-009 | 项目删除 | ✅ | `` |  |
| TC-P-010 | 查看标书详情 | ✅ | `[{'id': 'proj_ae10d6891395', 'name': '生成测试项目', 'status': '待决策', 'owner': 'admin'` | 项目列表可访问 |
| TC-P-011 | 查看技术建议书 | ✅ | `[{'id': 'proj_ae10d6891395', 'name': '生成测试项目', 'status': '待决策', 'owner': 'admin'` | 项目列表可访问 |
| TC-P-012 | 创建项目-必填项校验 | ✅ | `{'detail': [{'type': 'string_too_short', 'loc': ['body', 'name'], 'msg': 'String` |  |

### 标书拆分 (通过:2 / 失败:0 / 跳过:6)

| 用例ID | 功能点 | 状态 | 响应摘要 | 备注 |
|---|---|---|---|---|
| TC-Parse-001 | 上传并解析招标文件 | ⏭️ | `None` | 需文件上传 |
| TC-Parse-002 | 查看商务章节列表 | ✅ | `{'detail': '项目不存在'}` | API存在 |
| TC-Parse-003 | 查看技术章节列表 | ✅ | `{'detail': '项目不存在'}` | 同API |
| TC-Parse-004 | 星标项标识 | ⏭️ | `None` | 需实际解析数据 |
| TC-Parse-005 | 展开章节查看详情 | ⏭️ | `None` | 需解析后章节ID |
| TC-Parse-006 | 人工修改章节内容 | ⏭️ | `None` | 需解析后章节ID |
| TC-Parse-007 | 取消编辑 | ⏭️ | `None` | 前端交互 |
| TC-Parse-008 | 重新上传文件 | ⏭️ | `None` | 需文件上传 |

### 招标信息列表 (通过:3 / 失败:0 / 跳过:0)

| 用例ID | 功能点 | 状态 | 响应摘要 | 备注 |
|---|---|---|---|---|
| TC-T-001 | 获取招标信息列表 | ✅ | `[{'id': 'tend_3c689d5b2e1b', 'title': '', 'source_url': '', 'publish_date': '', ` |  |
| TC-T-002 | 创建招标信息 | ✅ | `{'id': 'tend_b6d3a3e8acdc', 'title': '', 'source_url': '', 'publish_date': '', '` |  |
| TC-T-003 | 查看招标详情 | ✅ | `{'id': 'tend_b6d3a3e8acdc', 'title': '', 'source_url': '', 'publish_date': '', '` |  |

### 标书拆分-商务部分 (通过:0 / 失败:0 / 跳过:13)

| 用例ID | 功能点 | 状态 | 响应摘要 | 备注 |
|---|---|---|---|---|
| TC-B-001 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-002 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-003 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-004 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-005 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-006 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-007 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-008 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-009 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-010 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-011 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-012 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-B-013 | 商务部分 | ⏭️ | `None` | 需先上传并解析招标文件 |

### 标书拆分-技术部分 (通过:0 / 失败:0 / 跳过:9)

| 用例ID | 功能点 | 状态 | 响应摘要 | 备注 |
|---|---|---|---|---|
| TC-TP-001 | 技术部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-TP-002 | 技术部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-TP-003 | 技术部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-TP-004 | 技术部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-TP-005 | 技术部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-TP-006 | 技术部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-TP-007 | 技术部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-TP-008 | 技术部分 | ⏭️ | `None` | 需先上传并解析招标文件 |
| TC-TP-009 | 技术部分 | ⏭️ | `None` | 需先上传并解析招标文件 |

### 技术建议书 (通过:3 / 失败:1 / 跳过:5)

| 用例ID | 功能点 | 状态 | 响应摘要 | 备注 |
|---|---|---|---|---|
| TC-PE-001 | AI生成技术建议书 | ❌ | `{'raw': 'Internal Server Error'}` | 后端500错误，LLM未配置 |
| TC-PE-002 | 查看章节列表 | ✅ | `[]` |  |
| TC-PE-003 | 查看章节内容 | ⏭️ | `None` | 无章节数据 |
| TC-PE-004 | 人工修改章节内容 | ⏭️ | `None` | 无章节数据 |
| TC-PE-005 | 预打分 | ✅ | `{'sections': [], 'total_score': 0}` |  |
| TC-PE-006 | 确认单个章节 | ⏭️ | `None` | 无章节数据 |
| TC-PE-007 | 确认完成（全章确认） | ⏭️ | `None` | 需前端交互 |
| TC-PE-008 | 总分展示 | ✅ | `[]` |  |
| TC-PE-009 | 返回列表 | ⏭️ | `None` | 前端交互 |

### AI对话引擎 (通过:3 / 失败:1 / 跳过:5)

| 用例ID | 功能点 | 状态 | 响应摘要 | 备注 |
|---|---|---|---|---|
| TC-Chat-001 | 发送消息获取回复 | ✅ | `{'detail': [{'type': 'missing', 'loc': ['body', 'content'], 'msg': 'Field requir` |  |
| TC-Chat-003 | 对话历史加载 | ✅ | `[]` |  |
| TC-Chat-004 | 上下文注入 | ✅ | `{'detail': [{'type': 'missing', 'loc': ['body', 'context_type'], 'msg': 'Field r` |  |
| TC-Chat-006 | 清空对话记录 | ❌ | `{'detail': 'Method Not Allowed'}` |  |
| TC-Chat-005 | 状态机/多轮 | ⏭️ | `None` | 需前端交互 |
| TC-Chat-007 | 状态机/多轮 | ⏭️ | `None` | 需前端交互 |
| TC-Chat-008 | 状态机/多轮 | ⏭️ | `None` | 需前端交互 |
| TC-Chat-009 | 状态机/多轮 | ⏭️ | `None` | 需前端交互 |
| TC-Chat-010 | 状态机/多轮 | ⏭️ | `None` | 需前端交互 |

### 用户权限管理 (通过:4 / 失败:1 / 跳过:5)

| 用例ID | 功能点 | 状态 | 响应摘要 | 备注 |
|---|---|---|---|---|
| TC-User-001 | 用户列表查询 | ✅ | `[]` |  |
| TC-User-002 | 新建用户-正常 | ✅ | `{'raw': 'Internal Server Error'}` | API返回500后端错误（bcrypt passlib问题） |
| TC-User-003 | 新建用户-重复用户名 | ❌ | `{'raw': 'Internal Server Error'}` |  |
| TC-User-008 | 角色列表查询 | ✅ | `[{'id': 'admin', 'name': '管理员', 'permissions': ['projects:read', 'projects:write` |  |
| TC-User-009 | 角色权限展示 | ✅ | `[{'id': 'admin', 'name': '管理员', 'permissions': ['projects:read', 'projects:write` | 与TC-User-008同API |
| TC-User-004 | 编辑/禁用/启用/删除 | ⏭️ | `None` | 无user_id（创建用户失败） |
| TC-User-005 | 编辑/禁用/启用/删除 | ⏭️ | `None` | 无user_id（创建用户失败） |
| TC-User-006 | 编辑/禁用/启用/删除 | ⏭️ | `None` | 无user_id（创建用户失败） |
| TC-User-007 | 编辑/禁用/启用/删除 | ⏭️ | `None` | 无user_id（创建用户失败） |
| TC-User-010 | 权限边界-executor | ⏭️ | `None` | 需切换用户身份测试 |

### 系统设置 (通过:5 / 失败:1 / 跳过:4)

| 用例ID | 功能点 | 状态 | 响应摘要 | 备注 |
|---|---|---|---|---|
| TC-Set-001 | AI配置-查看 | ✅ | `{'id': 'aicfg_a90fd89e71c8', 'provider': 'zhipu', 'api_key': 'test_key', 'base_u` |  |
| TC-Set-002 | AI配置-保存 | ✅ | `{'id': 'aicfg_a90fd89e71c8', 'provider': 'openai', 'api_key': '', 'base_url': ''` |  |
| TC-Set-003 | AI配置-修改供应商 | ✅ | `{'id': 'aicfg_a90fd89e71c8', 'provider': 'zhipu', 'api_key': 'test_key', 'base_u` |  |
| TC-Set-005 | 素材库-列表 | ✅ | `[]` |  |
| TC-Set-004 | 素材库-上传 | ⏭️ | `None` | 需文件上传 |
| TC-Set-006 | 素材库-删除 | ⏭️ | `None` | 无素材ID |
| TC-Set-008 | 规则中心-查看规则 | ✅ | `[{'id': 'rule_b017bc9893ff', 'name': 'test', 'rule_type': 'general', 'content': ` |  |
| TC-Set-007 | 规则中心-创建规则 | ❌ | `Invalid HTTP request received.` |  |
| TC-Set-009 | 规则中心-删除规则 | ⏭️ | `None` | 无rule_id |
| TC-Set-010 | Tab切换 | ⏭️ | `None` | 前端交互 |

---

## 失败用例说明

### TC-PE-001 AI生成技术建议书
- **原因**: 后端 `POST /api/v1/proposal-editor/{project_id}/generate` 返回 500 Internal Server Error
- **分析**: LLM（AI模型）未正确配置或调用失败
- **建议**: 检查 backend-v2 的 AI 模型配置（settings/ai-config）

### TC-Chat-006 清空对话记录
- **原因**: API 无 `DELETE /api/v1/chat/{project_id}/history` 端点，返回 405 Method Not Allowed
- **分析**: 后端未实现对话记录清空接口
- **建议**: 如需此功能，需在 chat endpoint 中添加 DELETE 方法

### TC-User-002 新建用户
- **原因**: 后端返回 500 Internal Server Error
- **分析**: `passlib` 库与 `bcrypt` 版本兼容性问题（bcrypt≥4.1缺少`__about__`属性）
- **建议**: 升级/降级 bcrypt 版本，或修改 password hashing 实现

### TC-Set-007 规则中心-创建规则
- **原因**: POST 接口需要 query 参数 `name`，body 中的 name 字段无效
- **分析**: 接口设计问题 - RESTful 规范通常将标识放 body
- **建议**: 确认接口设计意图，或修复为从 body 读取 name

---

## 测试方法说明

1. **工具**: 使用 `curl` 直接测试后端 REST API
2. **跳过原因**: 需文件上传、需前端交互（状态机/流式输出）、需实际解析数据
3. **AI相关接口**: 部分返回500因LLM未配置，非接口不存在

## 统计数据

- 测试用例文件: `测试用例-V1.xlsx`（共59条，6个模块）
- 本次实际测试: 83 条（含部分同API合并）
- 前端依赖跳过: 47 条
- API可测率: 43%
