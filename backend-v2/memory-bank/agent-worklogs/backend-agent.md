# Backend Agent Worklog

## BE-016: 清理遗留 mock/死代码

**执行时间**: 2026-04-24  
**执行者**: backend-agent

### 修改清单

#### 1. chat_service.py
- **删除** `_generate_response()` 函数（原第111-168行）
  - 该函数为大型硬编码 mock 回复函数，已确认无任何其他文件引用
  - 删除后代码从 241 行缩减至约 181 行
- **重命名** `_mock_stream()` → `_stream_tokens()`
  - 更新 docstring：从 "SSE streaming simulation" 改为 "将回复文本按字符拆分为 SSE 流式 token"
  - 该函数实际用途是将字符串按字符拆分用于 SSE 流式输出，并非 mock
- **更新调用点** `send_message()` 第83行：`list(_mock_stream(...))` → `list(_stream_tokens(...))`

#### 2. parsing_service.py
- **删除** `_mock_content()` 函数（原第575-576行）
  - 已确认无任何其他文件引用，是死代码
  - 删除后文件从 576 行缩减至 572 行

#### 3. tender_fetch_service.py
- **重命名** `_generate_mock_tenders()` → `_fallback_seed_tenders()`
  - 更新 docstring：从 "生成模拟招标数据（用于演示）" 改为 "在未接入真实招标抓取源时，生成后备示例数据以保持系统可用性"
- **更新调用点** `fetch_tenders_from_source()` 第68行
- **判断理由**：该函数仍被 `fetch_tenders_from_source()` 主动调用，属于"活的 mock 逻辑"而非死代码。BE-016 的任务范围是清理死代码，不应擅自删除活的调用链。重命名并修正注释以反映其真实角色（后备 seed 数据），待 BE-012 真实抓取逻辑接入后再移除。

### 未改动项
- **mock_workspace.py**：`build_default_workspace()` 被 `workspace_service.py` 的 `initialize_database()` 使用，用于初始化 WorkspacePanel 表的静态配置数据（导航项、模块卡片等）。这不是 mock，而是数据库 seed 配置，保留不动。

### 自测结果
- `python3 -m py_compile` 检查所有修改文件：**通过**
- 全局搜索旧函数名（`_mock_stream`, `_generate_response`, `_mock_content`, `_generate_mock_tenders`）：**零引用**
- `from app.main import app` 因环境 Python 版本（<3.10）限制无法运行，与本次修改无关

### Git
- Commit: `BE-016: 清理遗留 mock/死代码 — 删除 _generate_response，重命名 _mock_stream → _stream_tokens，删除 _mock_content`
