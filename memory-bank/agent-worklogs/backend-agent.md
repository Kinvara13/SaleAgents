# Backend Agent Worklog

## 角色边界

- 只负责 `backend-v2/`
- 任何公开 API 改动前先更新 `specs/api-contract-spec.md`

## 待跟进任务

- `BE-008` ✓ done
- `BE-009` ✓ done

## 日志

### 2026-04-24 (BE-008 + BE-009)

**BE-008: LLM接入 - 重构 proposal_service**
- 修改 `generate_proposal()` 使用 LLM 语义打分替代关键词匹配打分
- 修改 `compute_score(force=False)` 在分数为 0 时自动使用 LLM 补打语义分数
- `检收标准`: `generate_proposal` 能根据上下文真实生成不同内容的文档，`score_proposal` 能给出语义化预打分

**BE-009: PDF 分块解析优化**
- 重构 `parsing_service.py` 为类型服务 `ParsingService`，支持:
  - `parse_document()` / `parse_pdf()`: 真实 PDF 文本提取
  - 按标题分块（heading-based chunking）避免硬截断
  - 超长章节自动摘要（LLM）
  - `项目字段映射` (`project_fields_map`)
  - `解析上下文` (`get_project_context`) 供生成模块使用
- 更新 `llm_parsing_client.py` 添加 `summarize_text()` 方法用于超长文本摘要
- 更新 `parsing.py` 使用新的 `parsing_service.parse_document()`
- `检收标准`: 支持超长 PDF 解析（末尾技术要求/合同条款不会丢弃）

**关键文件变更**:
- `app/services/proposal_service.py`: 11 行修改
- `app/services/parsing_service.py`: 584 行重构
- `app/services/llm_parsing_client.py`: 66 行新增
- `app/api/v1/endpoints/parsing.py`: 简化 218 行

### 2026-04-24 (BE-017)

**BE-017: 招标信息真实 HTTP 抓取**
- 重写 `tender_fetch_service.py`，替换原有 `_fallback_seed_tenders` 模拟实现为真实 HTTP 抓取链路
- 新增 `_fetch_with_retry`：基于 `httpx`，支持指数退避重试（3 次）、合理 User-Agent、超时设置、编码指定
- 新增 `_parse_ccgp_tenders`：使用 `BeautifulSoup` 解析中国政府采购网 search.ccgp.gov.cn 搜索结果页，提取标题、source_url、publish_date 等
- 新增 `_parse_zbytb_tenders`：解析中国招标信息网 zbytb.com 列表页
- 修改 `fetch_tenders_from_source`：优先尝试 `_fetch_real_tenders`，失败时自动降级到 `_fallback_seed_tenders`，保留降级策略
- 不修改 `run_fetch_task` 外层调度逻辑
- 更新 `requirements.txt` 和 `pyproject.toml`：新增 `httpx`、`beautifulsoup4`
- `python -m py_compile` 通过
- `检收标准`: 至少接入 1 个真实招标源；保留 fallback 降级策略；含重试与错误处理

### 2026-04-21

- 认领并开始处理任务 `BE-001`: 在 `backend-v2/app/api/router.py` 注册健康检查路由并补 smoke 用例。
- 认领并开始处理任务 `BE-002`: 修复 `ai_configs` 数据库 schema 漂移。
- 初始化 worklog
- 已知阻塞：`ai_configs` 表 schema 漂移导致 AI 配置接口 500
- 已知阻塞：健康检查路由未注册
- 已知环境约束：运行验证必须使用 Python 3.11
