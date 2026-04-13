# SaleAgents Memory Bank

## 1. 文档目的

本文件用于记录当前项目的开发进度、已完成事项、未完成事项、技术现状和后续计划。

下次继续开发前，优先阅读本文件，再结合以下文档一起看：

- `docs/bid-agent-prd.md`
- `docs/bid-agent-architecture.md`
- `docs/bid-agent-pages.md`

## 2. 当前项目目标

项目目标是构建一个"招投标智能体" MVP，核心包含 3 个模块：

1. 投标决策
2. 标书生成
3. 材料审核

当前实现策略：

- 先做轻量架构
- 先把工作台和接口骨架搭起来
- 先用本地静态/种子数据跑通页面和 API 链路
- 后续再逐步替换成真实数据库与真实业务流程

## 3. 当前技术栈

### 后端

- FastAPI
- SQLAlchemy
- PostgreSQL + `pgvector` 设计预留
- Redis 设计预留

### 前端

- React
- Vite
- TypeScript

### 当前运行方式

- 不使用 Docker
- 默认本地直跑
- 前端默认地址：`http://localhost:5173`
- 后端默认地址：`http://localhost:8000`
- API 前缀：`/api/v1`

## 4. 已完成事项

### 4.1 文档设计已完成

已完成 3 份核心产品/架构文档：

- `docs/bid-agent-prd.md`
- `docs/bid-agent-architecture.md`
- `docs/bid-agent-pages.md`

这些文档已经覆盖：

- 产品目标和范围
- 3 个模块的能力边界
- AI 与规则的融合方式
- 页面结构和字段设计
- 技术架构和轻量数据库方案

### 4.2 项目骨架已完成

已建立基础工程结构：

- `backend/`
- `frontend/`
- `database/`
- `docs/`

已补充：

- `README.md`
- `.env.example`
- `.gitignore`

### 4.3 后端基础骨架已完成

已完成：

- FastAPI 启动入口
- API 路由注册
- 配置读取
- 数据库 session 基础层
- ORM 基础模型
- 服务层基础结构
- 工作台种子数据初始化逻辑
- CORS 基础配置

关键文件：

- `backend/app/main.py`
- `backend/app/core/config.py`
- `backend/app/db/session.py`
- `backend/app/models/project.py`
- `backend/app/models/workspace_panel.py`
- `backend/app/services/workspace_service.py`

### 4.4 后端 API 骨架已完成

当前已提供以下 GET 接口：

- `/api/v1/health`
- `/api/v1/workspace`
- `/api/v1/projects`
- `/api/v1/parsing/sections`
- `/api/v1/parsing/fields`
- `/api/v1/decision/scores`
- `/api/v1/decision/rules`
- `/api/v1/decision/reasons`
- `/api/v1/generation/sections`
- `/api/v1/generation/assets`
- `/api/v1/generation/todos`
- `/api/v1/review/summary`
- `/api/v1/review/issues`
- `/api/v1/review/actions`

说明：

- 当前这些接口已经接入数据库 session
- 数据来源是应用启动时初始化到数据库中的种子数据
- 目前仍是"结构化种子数据驱动"，还不是真实业务数据流

### 4.5 数据库过渡方案已完成

当前数据库层采用过渡实现：

- `projects` 表存项目基础数据
- `workspace_panels` 表存工作台各面板 JSON 数据

这是一种"先跑通链路"的过渡方案，优点是：

- 开发快
- 便于前后端联调
- 便于后续逐步拆分成正式表结构

### 4.6 前端工作台已完成

当前前端已完成蓝冷色调科技公司风格工作台。

已完成页面：

- 控制总览
- 项目列表
- 文档解析
- 投标决策
- 标书生成
- 材料审核

当前为单应用多视图切换模式，尚未引入正式路由。

### 4.7 前端结构拆分已完成

已从单文件拆分为正式结构：

- `components/`
- `pages/`
- `data/`
- `services/`
- `lib/`
- `types.ts`

关键文件：

- `frontend/src/App.tsx`
- `frontend/src/components/Sidebar.tsx`
- `frontend/src/components/PageHeader.tsx`
- `frontend/src/pages/*.tsx`
- `frontend/src/services/workspace.ts`
- `frontend/src/lib/api.ts`

### 4.8 前后端联调方式已完成

当前前端数据策略：

- 优先请求真实后端 API
- 若请求失败，则回退到本地 mock 数据

已接入真实优先的页面数据：

- 项目列表
- 文档解析
- 投标决策

说明：

- 总览页、标书生成页、材料审核页当前也能通过 `/workspace` 获取数据
- 但尚未单独拆成页面专属真实接口调用逻辑

### 4.9 本地 SQLite 兜底联调已完成

为了解决当前机器未安装 PostgreSQL / `psql` 时无法继续联调的问题，已经补充了本地 SQLite 兜底方案。

已完成：

- 项目根目录新增 `.env`
- 使用 `DATABASE_URL_OVERRIDE=sqlite:///./bid_agent.db` 让后端本地直跑
- `backend/app/db/session.py` 已兼容 SQLite `check_same_thread=False`
- `frontend/vite.config.ts` 已设置 `envDir: ".."`，前端可直接读取项目根目录 `VITE_*` 环境变量
- `README.md` 与 `.env.example` 已补充 SQLite 启动说明

说明：

- 当前 SQLite 数据文件位于 `backend/bid_agent.db`
- 这是"先跑通联调"的本地兜底方案，不替代正式 PostgreSQL 环境

### 4.10 前端演示叙事已收敛为两个核心功能

根据最新反馈，前端不再强调"招投标全链路中台"，而是收敛为两个更容易讲清价值的核心功能：

- 合同审查机器人
- 招标应答自动编写 / 回标文件自动编写

已完成：

- 首页 hero 文案已改为双功能叙事
- 侧边栏导航已将"回标编写 / 合同审查"前置
- 首页模块卡已改为"两个主功能 + 一个支撑层"
- `标书生成` 页面已改写为"回标文件自动编写"
- `材料审核` 页面已改写为"合同审查机器人"
- `文档解析 / 投标决策 / 项目列表` 页面文案已改成支撑双功能的表达

说明：

- 当前主要是前端展示层与产品叙事调整
- 后端接口结构暂未收缩，仍保留现有骨架，便于后续继续联调与扩展

### 4.11 合同审查机器人后端 MVP 主链已落地

本轮已经开始把"合同审查机器人"从展示层概念落实为真实后端能力，当前已完成第一版规则审查工作流。

已完成：

- 新增 `review_jobs` 表，保存一次合同审查任务
- 新增 `review_issues_records` 表，保存命中的风险问题、证据、建议与处理状态
- 新增 `backend/app/schemas/review.py`
- 在 `backend/app/modules/review/service.py` 中实现第一版 `ReviewService`
- 已实现规则审查而非纯 mock，当前内置规则包括：
  - 付款尾款/终验比例红线
  - 自动续约风险
  - 单方责任承担风险
  - 单方验收解释风险
  - 无限责任风险
  - 知识产权归属风险

当前已提供的新接口：

- `POST /api/v1/review/jobs`
- `GET /api/v1/review/jobs/{job_id}`
- `GET /api/v1/review/jobs/{job_id}/issues`
- `GET /api/v1/review/jobs/{job_id}/summary`
- `POST /api/v1/review/jobs/{job_id}/rerun`
- `POST /api/v1/review/issues/{issue_id}/resolve`

兼容处理：

- 旧接口 `GET /api/v1/review/summary`
- 旧接口 `GET /api/v1/review/issues`
- 旧接口 `GET /api/v1/review/actions`

当前会优先读取最新一条真实审查任务结果；若还没有任务，则回退到原先的种子数据。

说明：

- 该阶段最初输入方式是"直接提交合同文本"
- 文件上传与 DOCX/PDF/TXT 解析能力已在下一阶段补上
- 还没有接 LLM 语义审查，只是规则审查 MVP

### 4.12 合同文件上传与条款切分已落地

本轮已完成合同审查第一阶段中的"文件上传 + 条款切分"。

已完成：

- 新增 `review_clauses_records` 表，保存切分后的合同条款
- `POST /api/v1/review/jobs/upload` 已支持上传后直接发起审查任务
- `GET /api/v1/review/jobs/{job_id}/clauses` 可查询切分后的条款列表
- 当前支持格式：
  - `txt`
  - `docx`
  - `pdf`
- 上传后会执行：
  - 文件文本抽取
  - 条款切分
  - 审查任务创建
  - 风险问题生成

说明：

- 当前 `txt` 与 `docx` 上传已验证通过
- `pdf` 解析代码已接入 `pypdf`，但本轮尚未单独做真实 PDF 样例验证
- 当前未落原始文件持久化，只保存抽取后的文本与切分结果

### 4.13 合同审查页已接入真实上传审查交互

前端 `合同审查机器人` 页面已不再只是静态展示，当前已经接上真实上传与审查触发。

已完成：

- `ReviewPage` 已接入合同文件上传表单
- 上传后会调用真实后端接口 `POST /api/v1/review/jobs/upload`
- 上传成功后会自动刷新工作台中的审查摘要、问题列表和建议动作
- 页面已支持展示：
  - 审查来源
  - 命中证据
  - 修订建议
  - 最新上传任务切分出的条款列表

说明：

- 当前联动的是后端真实接口，不再只是 mock 文案
- 页面级"处理问题 / 重新运行审核 / 导出报告"按钮还未全部接成真实动作

### 4.14 当前工作区已出现语义启发式审查逻辑

并行 agent 已在 `backend/app/modules/review/service.py` 中加入一版语义启发式审查逻辑。

当前已观察到的能力：

- 范围扩张风险
- 单方变更风险
- 结果性承诺风险
- 责任边界模糊风险

本轮已验证：

- 使用"包括但不限于 / 甲方有权调整 / 确保满足所有要求"等文本发起审查任务
- 可返回 `P1` 级语义风险与对应修订建议

注意：

- 当前是本地启发式语义规则，不是正式外部 LLM API 接入
- 后续仍需要统一收敛为真正的 LLM 语义审查方案

### 4.15 LLM 审查调用链已接入代码，但当前环境未启用

当前工作区中，合同审查后端已经接入 `LLMReviewClient`，并在 `ReviewService` 中优先尝试调用外部 LLM，再在失败或未配置时回退到启发式语义审查。

当前状态：

- `backend/app/services/llm_client.py` 已存在
- `backend/app/core/config.py` 已补充 `LLM_*` 配置项
- `.env.example` 已补充 `LLM_ENABLED / LLM_API_KEY / LLM_BASE_URL / LLM_MODEL` 示例项
- 当前本地环境检查结果：`llm_ready = False`

说明：

- 这意味着代码链路已经具备外部 LLM 接入点
- 但当前机器尚未提供有效 API Key，所以运行时仍会回退到启发式语义审查

### 4.16 合同审查闭环按钮已补成真实动作

前端 `合同审查机器人` 页面已补齐上一轮仍是占位的后续动作。

已完成：

- 新增 `GET /api/v1/review/jobs/latest`
- 新增 `GET /api/v1/review/jobs/{job_id}/report`
- 前端页面已接入：
  - 重新运行审查
  - 标记当前问题已处理
  - 导出法审摘要
- 页面会优先拉取最新审查任务及其问题、条款和报告能力

说明：

- `导出法审摘要` 当前导出的是 Markdown 报告
- 旧的工作台 summary/issues/actions 仍继续兼容

### 4.17 规则 + LLM 去重策略已增强

本轮已完成规则与 LLM 审查结果的智能去重策略。

已完成：

- 新增 `_dedupe_by_semantic_similarity` 方法
- 新增 `_is_duplicate_of_existing` 方法
- 新增 `_titles_are_similar` 方法，基于关键词重叠度判断相似性
- 新增 `_extract_keywords` 方法，提取中文关键词
- 新增 `_evidence_overlap` 方法，判断证据文本重叠

去重策略：

1. 先按 `(title, evidence)` 完全匹配去重
2. 再按语义相似度去重：
   - 标题关键词重叠度 >= 60% 且类型相同
   - 标题相似且证据文本有重叠
   - 证据文本有重叠且类型相同

说明：

- 该策略能有效减少规则审查与 LLM 语义审查的重复问题
- 关键词提取已过滤常见停用词（的、存在、条款、风险等）

### 4.18 审查报告导出已增强为双格式

本轮已完成 Markdown 与 Word 双格式导出能力。

已完成：

- 新增 `export_job_report_docx` 方法
- 新增 `GET /api/v1/review/jobs/{job_id}/report/docx` 接口
- 前端新增 `exportReviewJobReportDocx` 服务函数
- 前端页面新增"导出 Word"按钮
- 页面头部按钮已调整为"导出 Markdown"和"导出 Word"两个独立按钮

Word 报告特性：

- 使用 `python-docx` 生成标准 DOCX 格式
- 包含标题、摘要、审查问题表格、条款切分、建议动作
- 审查问题以表格形式呈现，便于阅读和打印
- 文件名格式：`{合同名称}-review-report.docx`

### 4.19 法务反馈闭环学习已实现

本轮已完成法务反馈闭环学习功能，用于记录法务对审查结果的处理决策并优化规则权重。

已完成：

- 新增 `review_feedback_records` 表，保存法务反馈记录
- 新增 `rule_statistics` 表，保存规则命中与准确率统计
- 新增 `POST /api/v1/review/issues/{issue_id}/feedback` 接口
- 新增 `GET /api/v1/review/rules/statistics` 接口
- 前端新增反馈表单，支持选择反馈类型（确认有效/标记误报/建议修改）
- 反馈提交后自动更新规则统计（命中数、确认数、误报数、准确率）

反馈类型：

- `confirmed`：确认有效，增加规则准确率
- `dismissed`：标记误报，降低规则准确率
- `modified`：建议修改，记录为待优化

### 4.20 规则库配置化已完成

本轮已完成规则库配置化，支持通过 API 动态管理审查规则。

已完成：

- 新增 `rule_configs` 表，保存可配置的审查规则
- 新增 `RuleConfigService` 服务类
- 新增规则管理接口：
  - `GET /api/v1/review/rules` - 列出规则
  - `GET /api/v1/review/rules/{rule_id}` - 获取规则详情
  - `POST /api/v1/review/rules` - 创建规则
  - `PATCH /api/v1/review/rules/{rule_id}` - 更新规则
  - `DELETE /api/v1/review/rules/{rule_id}` - 删除规则
  - `POST /api/v1/review/rules/initialize` - 初始化默认规则
- 默认规则已迁移到数据库，支持动态启用/禁用
- 规则支持优先级、分类、匹配模式等属性

规则属性：

- `name`：规则标识
- `title`：规则标题
- `issue_type`：问题类型
- `level`：风险等级（P0/P1/P2）
- `patterns`：匹配模式（JSON 数组）
- `match_mode`：匹配模式（any/all）
- `is_enabled`：是否启用
- `priority`：优先级

### 4.21 前端交互增强已完成

本轮已完成前端交互增强，包括法务反馈表单和问题筛选功能。

已完成：

- 前端新增法务反馈表单
- 支持选择反馈类型（确认有效/标记误报/建议修改）
- 支持填写反馈备注
- 提交反馈后显示成功提示
- 新增 `submitReviewFeedback` 服务函数
- 新增 `getRuleConfigs`、`createRuleConfig`、`updateRuleConfig` 等规则管理函数

### 4.22 合同审查页真实任务驱动已收口

本轮继续收口前端 `合同审查机器人` 页面，把此前“已经能请求真实后端，但页面主体仍混用工作台 seed 数据”的问题补齐。

已完成：

- `ReviewPage` 改为优先展示最新真实审查任务的摘要、问题列表与建议动作
- 页面新增“最新审查任务”卡片，展示合同名称、风险等级、问题数、高风险数和完成时间
- 风险问题列表新增筛选能力：
  - 按处理状态筛选（全部 / 待处理 / 已处理）
  - 按风险等级筛选（全部 / 高风险 / P0 / P1 / P2 / P3）
- 法务反馈表单已真正接入页面，可提交：
  - `confirmed`
  - `dismissed`
  - `modified`
- 前端 `ReviewJob` 类型已补齐 `summary / review_actions / created_at / updated_at / completed_at`
- `styles.css` 已补充任务卡、筛选区、空状态和反馈表单样式

说明：

- 这次主要是前端真实联动收口，没有新增后端接口
- 当前 `ReviewPage` 已能正确展示最新任务结果，而不再只展示 `/workspace` 返回的旧审查种子数据
- 规则统计页与反馈回流链路可继续基于这版页面做更深交互

### 4.23 生成模块启动级语法阻塞已修复

本轮联调时发现后端无法启动，阻塞点不在合同审查链路，而是在 `generation` 模块的内置模板文案中存在未转义字符串。

已完成：

- 修复 `backend/app/modules/generation/service.py` 中 `"云-边-端"` 未转义导致的 `SyntaxError`
- 清理 `backend/app` 下重新出现的 macOS `._*` 垃圾文件
- 重新验证 `python -m compileall app` 通过
- 重新启动后端并验证 `GET /api/v1/health` 正常返回

说明：

- 这是启动级 blocker 修复，不涉及生成模块业务逻辑调整
- 当前前端 `5173` 与后端 `8000` 都已可本地访问

### 4.24 回标生成链路已升级为“输入驱动 + 可编辑 + 双格式导出”

本轮开始把“回标文件自动编写”从固定模板演示推进到可实际操作的生成闭环。

已完成：

- 后端 `GenerationJobCreateRequest` 已支持更多业务输入：
  - `client_name`
  - `project_summary`
  - `tender_requirements`
  - `delivery_deadline`
  - `service_commitment`
  - `selected_asset_titles`
  - `section_titles`
- `backend/app/modules/generation/service.py` 已改为基于输入动态生成章节内容，而不是直接回填固定长文模板
- 新增章节编辑接口：
  - `PATCH /api/v1/generation/jobs/{job_id}/sections/{section_id}`
- 新增 Word 导出接口：
  - `GET /api/v1/generation/jobs/{job_id}/export/docx`
- 前端 `GenerationPage` 已改为支持：
  - 输入项目摘要、招标要求、交付时限、服务承诺
  - 选择素材
  - 自定义章节大纲
  - 在线编辑章节内容
  - 保存章节
  - 重新生成单章节
  - 导出 Markdown / Word
- 前端 `workspace.ts` 已新增生成链路的 `updateGenerationSection` 与 `exportGenerationJobDocx`

说明：

- 当前回标生成仍是规则化/模板化拼装，不是正式 LLM 长文生成
- 但这一版已经能把招标要求、素材选择和交付约束纳入生成过程，足以支撑下一步再接真实 LLM 或 RAG
- 由于当前数据库还未正式化，本轮没有新增 generation 表字段，输入参数只用于本次生成任务编排

### 4.25 回标生成已接入“LLM 优先、模板回退”执行策略

本轮继续沿着回标主链路往下做，把外部大模型正式接入到章节生成路径中，同时保留当前本地可跑的稳定回退逻辑。

已完成：

- `backend/app/services/llm_client.py` 已扩展为统一 LLM 层：
  - 保留 `LLMReviewClient`
  - 新增 `LLMGenerationClient`
- `GenerationService` 已改为：
  - 创建章节时优先调用 `llm_generation_client.generate_bid_section`
  - 若未配置 `LLM_API_KEY` 或调用失败，则自动回退到当前模板化章节生成
  - 单章节重生成同样沿用“LLM 优先，fallback 回退”的策略
- 当前 LLM 生成输入已覆盖：
  - 项目名称
  - 客户名称
  - 章节标题
  - 项目摘要
  - 招标要求
  - 交付时限
  - 服务承诺
  - 可引用素材
  - 抽取字段
  - 待确认事项
- 当前 LLM 输出被约束为 JSON：
  - `content`
  - `citations`
  - `todos`

说明：

- 当前本地环境 `llm_ready = False`
- 因此运行时仍走 fallback 生成，但代码链路已经具备真实 LLM 切换能力
- 这次没有新增新的前端页面动作，主要是把后端生成引擎升级为可切换的双模式

### 4.26 项目、要求提取与回标生成入口已贯通

本轮继续把“项目 / 招标文件要求 / 回标生成”三段接成一条可以直接操作的业务链路。

已完成：

- 后端新增项目级回标生成上下文接口：
  - `GET /api/v1/projects/{project_id}/generation/context`
- 后端新增项目级回标生成运行接口：
  - `POST /api/v1/projects/{project_id}/generation/run`
- `GenerationService` 已支持根据：
  - 项目基础信息
  - 要求提取字段
  - 解析出的招标结构
  - 待确认事项
  - 默认素材清单
  自动拼出一份生成默认上下文
- 前端 `GenerationPage` 已支持读取 `projectId` 查询参数，并自动加载项目生成上下文
- 前端 `ProjectsPage` 已为每个项目增加“去生成回标”入口，直接跳到：
  - `/generation?projectId=<project_id>`
- 当生成页绑定 `projectId` 时：
  - 项目名称、客户名称会自动带入
  - 项目摘要、招标要求、交付时限、服务承诺会自动带入
  - 生成动作会走项目级运行接口，而不是通用手工创建接口

说明：

- 当前“要求提取”仍然是基于工作台种子数据的全局上下文，不是项目级正式解析结果
- 但这条链路已经把项目、提取字段和回标生成入口串起来了，后续只需要把解析结果正式项目化即可继续演进
- 当前已经具备“从项目台账一键进入回标生成”的前端使用路径

### 4.27 要求提取已正式项目化

本轮把“要求提取”从全局 `workspace_panels` seed 数据中独立出来，落成了项目级正式记录。

已完成：

- 新增项目级正式表：
  - `project_documents`
  - `project_parse_sections`
  - `project_extracted_fields`
- 新增项目级解析 schema：
  - `backend/app/schemas/parsing.py`
- 新增解析服务：
  - `backend/app/services/parsing_service.py`
- 新增项目级解析接口：
  - `GET /api/v1/parsing/projects/{project_id}`
  - `POST /api/v1/parsing/projects/{project_id}/run`
  - `PATCH /api/v1/parsing/projects/{project_id}/fields/{field_label}`
- `GenerationService.get_project_context` 已优先读取项目级提取字段，不再优先依赖全局 seed 数据

说明：

- 当前项目级要求提取仍采用轻量规则抽取，不是 OCR + 版面分析
- 但现在每个项目已经拥有独立的解析结构、独立的字段和独立的来源文档，不会再共用一套全局字段
- 这一步完成后，后续 OCR 或更复杂抽取只需要替换 `ParsingService` 内部实现，不需要再改业务链路

### 4.28 项目招标文件上传已接入闭环

在项目级解析正式化之后，本轮继续把“项目 -> 上传招标文件 -> 提取要求 -> 生成回标”闭环接通。

已完成：

- 新增项目招标文件上传接口：
  - `POST /api/v1/parsing/projects/{project_id}/upload`
- 支持上传：
  - `txt`
  - `docx`
  - `pdf`
- 上传后会自动：
  - 抽取文本
  - 生成项目级解析章节
  - 生成项目级提取字段
  - 覆盖该项目上一轮解析结果
- 前端 `ParsingPage` 已支持：
  - 读取 `projectId`
  - 上传招标文件
  - 重跑提取
  - 校正字段并保存
  - 直接跳转到回标生成页
- 前端 `ProjectsPage` 的“查看要求提取”入口已改成带 `projectId` 跳转
- 项目级回标生成接口现在会读取上传后的项目级提取字段，生成上下文已被实测更新为：
  - 上传文件中的项目名称
  - 上传文件中的预算金额
  - 上传文件中的投标截止时间
  - 上传文件中的付款与交付要求

说明：

- 当前解析结果覆盖策略是“同项目保留文档历史，但只保留最新一套有效解析字段”
- 这条链路已经满足 MVP 闭环要求：从项目发起，上传招标文件，提取要求，再直接生成回标

### 4.29 项目文档已持久化到对象存储并支持版本记录

本轮把项目招标文件从“仅在请求阶段读取”升级为“持久化存储 + 版本留痕”。

已完成：

- 新增 `project_document_versions` 表，记录每次上传的版本快照
- 新增 `backend/app/services/object_storage.py`
- 上传文件现在会先写入对象存储抽象层，再落项目文档版本记录
- 当前存储策略：
  - 优先使用 MinIO / S3 兼容对象存储
  - 若未配置，则自动回退到本地 `backend/storage/`
- `ProjectParsingContextResponse.documents` 已补充：
  - `latest_version_no`
  - `versions`
  - 每个版本的 `storage_backend / object_key / file_size / parse_status`
- 前端 `ParsingPage` 已显示项目文档列表和版本记录

说明：

- 当前对象存储层已经具备可替换能力，后续接真实 MinIO 只需要补环境配置
- 当前版本策略按“同项目 + 同文件名 + 同文档类型”聚合，重复上传会递增版本号
- 当前仍未提供文件回放下载接口，但存储位置和版本元数据已经完整保留

### 4.30 OCR 与更细粒度字段抽取已接入项目解析主链路

本轮继续把扫描版 PDF 纳入项目解析链路，并把字段抽取粒度从基础字段扩展到更适合回标生成的项目级要求。

已完成：

- `ParsingService` 现在支持：
  - `txt`
  - `docx`
  - 文本型 `pdf`
  - 扫描型 `pdf`
- PDF 解析策略已升级为：
  - 先尝试 `pypdf` 抽取文本层
  - 文本过短时判定为扫描件
  - 使用 `PyMuPDF` 渲染页面图片
  - 使用 `RapidOCR` 作为主 OCR 引擎
  - 使用 macOS `ocrmac` 作为回退
  - 如仍失败，再尝试 `pytesseract`
- 已扩展项目级字段抽取：
  - 项目名称
  - 招标编号
  - 投标截止时间
  - 预算金额
  - 必备资质
  - 付款条款
  - 交付周期
  - 评分重点
  - 技术要求
  - 服务承诺
- 已补充 OCR 值清洗，修正常见时间拼接噪音
- 项目级回标生成上下文已验证会读取 OCR 后的字段结果

说明：

- 已实测上传中文扫描版 PDF，接口返回 `OCR已解析`
- 已实测同一扫描文件二次上传后生成 `v2` 版本记录
- 当前 `source_excerpt` 仍保留原始 OCR 文本，字段值会走清洗后的结构化结果
- 更强的版面分析、表格抽取和多文档合并仍未完成

### 4.31 回标生成已接入无向量库的轻量素材路由

本轮把“回标自动生成”从简单素材标题拼装，升级为“素材索引 -> 章节路由 -> 章节注入”的轻量检索链路，不依赖向量库。

已完成：

- 新增素材正式表：
  - `knowledge_assets_records`
  - `knowledge_asset_chunks_records`
- 新增章节命中素材记录表：
  - `generation_section_asset_refs`
- 新增素材索引服务：
  - `backend/app/services/asset_index_service.py`
- 新增素材路由服务：
  - `backend/app/services/asset_routing_service.py`
- 现有种子素材已在应用启动时自动索引入库
- 章节生成前会按以下信号做加权路由：
  - 章节标题匹配
  - 用户已选素材
  - 招标要求关键词
  - 项目摘要与结构化字段
  - 服务/资质/实施等场景匹配
- 路由命中的素材片段会注入章节生成：
  - LLM 模式下作为可引用素材上下文
  - fallback 模式下直接写入章节“可引用素材”区域
- `GET /api/v1/generation/jobs/{job_id}/sections` 已补充：
  - `routed_assets`
  - `routing_reasons`
- 新增素材索引查看接口：
  - `GET /api/v1/generation/assets/indexed`
- 前端 `GenerationPage` 已显示当前章节的命中素材与命中原因

说明：

- 当前这是一版“结构化标签 + 关键词 + 场景权重”的轻量路由，不是 embedding RAG
- 当前素材索引先基于现有种子素材和规则化标签构造，后续可升级为 LLM 离线索引
- 当前章节可命中同一素材下的多个片段，以便技术方案和实施章节引用不同证据块

### 4.32 素材库管理、离线索引刷新与项目级引用控制已落地

本轮继续把轻量素材路由补成“可维护、可配置”的版本，允许前端直接新增素材、上传素材文件、刷新索引，并按项目控制固定引用和禁用引用。

已完成：

- 新增素材来源表：
  - `knowledge_asset_sources_records`
- 新增项目级素材偏好表：
  - `project_asset_preferences`
- `asset_index_service` 已支持：
  - 手工新增文本素材
  - 上传 `txt / docx / pdf` 素材并抽取文本
  - 按素材源文本重建离线索引
  - 为旧种子素材自动补齐 `source_kind=seed`
- 新增素材管理接口：
  - `POST /api/v1/generation/assets`
  - `POST /api/v1/generation/assets/upload`
  - `POST /api/v1/generation/assets/refresh-index`
- 新增项目级素材偏好接口：
  - `GET /api/v1/projects/{project_id}/generation/preferences`
  - `PATCH /api/v1/projects/{project_id}/generation/preferences`
- 项目生成上下文 `GenerationProjectContextResponse` 已补充：
  - `fixed_asset_titles`
  - `excluded_asset_titles`
- `GenerationService` 已把项目级偏好真正接入生成链路：
  - 固定引用素材会强制进入候选集并提高权重
  - 禁用引用素材会在路由阶段直接排除
- 前端 `GenerationPage` 已支持：
  - 查看索引素材列表
  - 新增文本素材
  - 上传文件素材
  - 手动刷新索引
  - 对项目设置“固定引用 / 禁用引用”偏好

说明：

- 当前上传素材的文本抽取已支持 `txt / docx / pdf`，但素材上传还未接对象存储，主要保留结构化索引与源文本
- 当前项目级素材偏好以“标题”维度控制，不是更细的片段级白名单/黑名单
- 当前离线索引刷新是同步执行，适合 MVP；后续可改为后台任务

### 4.33 素材编辑删除、片段级管理、后台索引任务与审核流已落地

本轮继续把素材库补成“可运营”的状态，重点完成素材编辑、删除、片段级管理、后台索引任务和审核流闭环。

已完成：

- 新增素材工作流表：
  - `knowledge_asset_workflows`
- 新增素材索引任务表：
  - `knowledge_asset_index_jobs`
- `asset_index_service` 已支持：
  - 编辑素材基础信息与源文本
  - 删除素材及其来源、工作流和片段记录
  - 查看素材片段列表
  - 新增 / 编辑 / 删除素材片段
  - 审核通过 / 驳回素材
  - 索引刷新后回写任务状态与刷新数量
- 新增素材管理接口：
  - `PATCH /api/v1/generation/assets/{asset_id}`
  - `DELETE /api/v1/generation/assets/{asset_id}`
  - `POST /api/v1/generation/assets/{asset_id}/review`
  - `GET /api/v1/generation/assets/{asset_id}/chunks`
  - `POST /api/v1/generation/assets/{asset_id}/chunks`
  - `PATCH /api/v1/generation/assets/{asset_id}/chunks/{chunk_id}`
  - `DELETE /api/v1/generation/assets/{asset_id}/chunks/{chunk_id}`
  - `GET /api/v1/generation/assets/refresh-index/{job_id}`
- `POST /api/v1/generation/assets/refresh-index` 已改成后台任务模式：
  - 先返回 `queued` 任务
  - 后台执行重建索引
  - 轮询任务状态读取 `queued/running/completed/failed`
- `GenerationService` 已补齐 `owner/visibility` 传递，避免素材新增接口因参数漏接报错
- 前端 `GenerationPage` 已支持：
  - 选择素材并进入管理面板
  - 编辑素材标题、类型、归属和可见性
  - 删除素材
  - 提交审核通过 / 驳回
  - 查看、创建、编辑、删除素材片段
  - 查看后台索引任务状态并轮询结果
- 前端 `workspace.ts` 已清理重复导出，并补齐素材管理相关 API

说明：

- 当前素材“编辑内容”仍以素材源文本/摘要为主，不是独立富文本编辑器
- 索引重建会重写该素材下的自动切片，因此刷新后旧片段 ID 可能失效
- 当前审核流是单步审核，不含多人会签和权限角色隔离

### 4.34 回标生成已接入评分点映射、自检与章节覆盖率检查

本轮继续把“回标自动编写”从章节生成器推进成带检查能力的智能体工作流，重点补了评分点映射生成、生成后自检和章节覆盖率分析。

已完成：

- `GenerationSectionResponse` 已补充：
  - `matched_score_items`
  - `missing_requirements`
  - `coverage_score`
- 新增回标分析响应结构：
  - `GenerationScoreItemResponse`
  - `GenerationCheckResponse`
  - `GenerationSectionCoverageResponse`
  - `GenerationJobAnalysisResponse`
- 新增分析接口：
  - `GET /api/v1/generation/jobs/{job_id}/analysis`
- `generation_service` 已支持：
  - 从 `评分重点 / 技术要求 / 必备资质 / 服务承诺 / 交付周期 / 付款条款 / 招标要求` 提取评分项
  - 将评分项按语义路由到目标章节
  - 对每个章节计算覆盖率、已覆盖评分点、待补要求和自检提示
  - 汇总作业级覆盖率、已覆盖/未覆盖评分项数量和风险检查项
- fallback 章节生成已加入“本章需覆盖的评分点”，让评分点不只用于事后检查，也参与章节编写
- 前端 `GenerationPage` 已支持：
  - 展示作业级总体覆盖率
  - 展示评分点映射清单
  - 展示生成后自检问题
  - 在章节树和章节详情中展示覆盖率、已覆盖评分点和待补评分点

说明：

- 当前评分点提取仍是规则化文本切分，不是版面级评分表解析
- 当前覆盖率判断基于关键词和章节语义映射，适合 MVP，不等于最终投标评分真实得分
- 当前 LLM 生成模式会继承评分点注入能力，但是否走真实模型仍取决于 `LLM_API_KEY`

### 4.35 评分办法表格级解析、缺口补写与二轮自修订已接入

本轮继续把回标自动编写推进成更接近“工作型智能体”的状态，补了评分办法表格级解析、未覆盖评分点一键补写，以及生成后二轮自修订。

已完成：

- `parsing_service` 已增强评分办法提取：
  - 支持从表格/条目化评分文本中识别 `XX分` 样式评分项
  - 会优先把带分值的技术、商务、实施、服务、资质类评分行聚合写入 `评分重点`
  - 对常见“评分办法/评分标准/评审标准”区块做定向抽取
- `LLMGenerationClient` 已新增章节修订入口：
  - `revise_bid_section(...)`
  - 当存在 `LLM_API_KEY` 时，会按未覆盖评分点和自检问题优先走模型修订
  - 未配置模型时自动回退到规则化补写
- `generation_service` 已新增：
  - `repair_uncovered_sections(...)`
  - `self_revise_job(...)`
- 新增接口：
  - `POST /api/v1/generation/jobs/{job_id}/repair-uncovered`
  - `POST /api/v1/generation/jobs/{job_id}/self-revise`
- fallback 修订模式下：
  - 会把未覆盖评分点、自检问题和可引用素材直接附加进章节修订块
  - 已更新作业进度为“已补写评分缺口”或“已完成二轮自修订”
- 前端 `GenerationPage` 已支持：
  - `一键补写未覆盖评分点`
  - `生成后二轮自修订`

说明：

- 当前“表格级解析”仍基于 OCR/抽取后的行文本重建，不是真正的表格单元格结构建模
- 二轮自修订在未启用 LLM 时仍然可运行，但属于规则化补写，不是模型级重写
- 自修订后仍可能保留低覆盖章节，适合作为“先补齐，再人工精修”的第二轮流程

### 4.36 投标决策模块（应答策略）正式项目化

本轮把“投标决策智能体”从前端演示静态数据，落地成了可供项目执行的真实后端能力。

已完成：

- 新增 `project_decision_jobs` 表，用于存储项目级决策评估结果
- 新增 `backend/app/schemas/decision.py`，规范化 `ProjectDecisionJobResponse` 和评分维度结构
- 实现 `DecisionService`：
  - 基于项目级已提取字段 `ProjectExtractedField` 进行规则分析
  - 自动识别一票否决项、高风险项与待确认事项（如预算金额缺失、资质要求模糊等）
  - 生成多维度的 AI 评分结果和推进摘要
- 新增项目级决策接口：
  - `POST /api/v1/decision/projects/{project_id}/run`
  - `GET /api/v1/decision/projects/{project_id}/latest`
- 前端 `DecisionPage` 接入正式流程：
  - 支持读取 URL 参数 `?projectId=xxx`，并拉取该项目的最新策略结果
  - 在未生成时显示占位态，并提供“立即生成策略”按钮
  - 成功生成后，通过图表、规则命中卡和待确认列表展示动态决策数据
  - 保留并完善“去生成回标”等下一步导流按钮
- 前端 `ProjectsPage` 在项目列表快捷操作区补充了“去应答策略”按钮，打通了 `项目列表 -> 要求提取 -> 应答策略 -> 标书生成` 的完整体验路径。

说明：

- 当前决策服务的核心引擎仍采用规则+启发式策略实现（便于本地无 LLM 也能闭环体验），后续可像生成模块一样平滑切换为 LLM 决策核心。
- 这个模块的落地填补了“自动投标智能体”链条中此前一直缺失的项目级评估分析环。

### 4.37 投标决策模块接入 LLM 语义评分

本轮继续对刚落地的“投标决策智能体”进行强化，将其从纯规则推演升级为“LLM 优先，规则兜底”的双模式。

已完成：

- 在 `backend/app/services/llm_client.py` 中新增 `LLMDecisionClient`：
  - 封装了决策专用的 Prompt 结构
  - 要求大模型基于项目基本信息、提取的关键要求和已命中的硬性规则结果，输出 JSON 格式的综合评估。
  - 强制返回多维度评分（如资质与合规、技术能力匹配等）、决策摘要原因以及待确认事项列表。
- 改造 `backend/app/modules/decision/service.py`：
  - 在完成本地规则引擎分析后，调用 `llm_decision_client.evaluate_project`。
  - 如果环境配置了 `LLM_API_KEY` 并且调用成功，则使用大模型返回的多维评分和补充说明。
  - 如果调用失败或未配置大模型，系统会无缝回退到预设的启发式评分逻辑。

说明：

- 此改造遵循了本项目其他智能体（如合同审查、回标生成）统一的“双轨制”策略，既保证了有模型环境下的语义优势，也保证了本地离线演示环境下的稳定闭环。
- 此时你可以通过在项目根目录 `.env` 中配置 `LLM_API_KEY` 和 `LLM_BASE_URL` 开启真实大模型决策评估。

### 4.38 智能小组件 (Page Agent) 前端集成与优化已完成

本轮完成了全局智能小组件（PageAgentFab）的前端集成，并根据用户反馈优化了其页面布局位置。

已完成：

- 在前端集成全局 AI 助手悬浮球组件 `PageAgentFab`，支持自然语言操控 UI（如“帮我新建一个商机”）。
- `frontend/src/page-agent.css` 样式调整：将 `.page-agent-fab` 的悬浮位置从页面左下角（`left: 24px;`）移动到了右下角（`right: 24px;`），以更好地适应用户习惯与工作台整体布局。
- `README.md` 中关于 PageAgent 悬浮球的提示文档已同步更新为“右下角”。

说明：

- 这是一个贯穿所有视图的全局交互入口，能够大幅提升用户在招投标全链路操作中的智能化体验。

## 5. 已做过的检查

已完成：

- Python `compileall` 语法检查通过
- 前后端目录结构检查通过
- Python 3.11 虚拟环境创建完成
- 后端依赖安装完成
- 后端 `uvicorn` 启动验证通过
- `/api/v1/health` 验证通过
- `/api/v1/workspace` 验证通过
- `/api/v1/projects` 验证通过
- 前端 `npm run build` 验证通过
- 前端 Vite 开发服务器启动验证通过
- 已清理源码目录中的 macOS `._*` 资源分叉文件，避免检查误报
- 前端双功能聚焦版文案与布局调整完成
- 合同审查新表自动建表验证通过
- `POST /api/v1/review/jobs` 验证通过
- `GET /api/v1/review/jobs/{job_id}/issues` 验证通过
- `POST /api/v1/review/issues/{issue_id}/resolve` 验证通过
- 旧 `/api/v1/review/summary|issues|actions` 已验证可读取最新审查任务结果
- `POST /api/v1/review/jobs/upload` 的 `txt` 上传验证通过
- `POST /api/v1/review/jobs/upload` 的 `docx` 上传验证通过
- `GET /api/v1/review/jobs/{job_id}/clauses` 验证通过
- `ReviewPage` 前端上传联动构建通过
- 语义启发式审查案例验证通过
- `GET /api/v1/review/jobs/latest` 验证通过
- `GET /api/v1/review/jobs/{job_id}/report` 验证通过
- `POST /api/v1/review/jobs/{job_id}/rerun` 验证通过
- 合同审查前端闭环动作构建通过
- 规则 + LLM 去重策略构建通过
- `GET /api/v1/review/jobs/{job_id}/report/docx` 验证通过
- 前端双格式导出按钮构建通过
- `POST /api/v1/review/issues/{issue_id}/feedback` 验证通过
- `GET /api/v1/review/rules/statistics` 验证通过
- `PATCH /api/v1/generation/assets/{asset_id}` 验证通过
- `DELETE /api/v1/generation/assets/{asset_id}` 验证通过
- `POST /api/v1/generation/assets/{asset_id}/review` 验证通过
- `GET /api/v1/generation/assets/{asset_id}/chunks` 验证通过
- `POST /api/v1/generation/assets/{asset_id}/chunks` 验证通过
- `PATCH /api/v1/generation/assets/{asset_id}/chunks/{chunk_id}` 验证通过
- `DELETE /api/v1/generation/assets/{asset_id}/chunks/{chunk_id}` 验证通过
- `POST /api/v1/generation/assets/refresh-index` 后台任务化验证通过
- `GET /api/v1/generation/assets/refresh-index/{job_id}` 轮询验证通过
- `GenerationPage` 素材管理页前端构建通过
- `GET /api/v1/generation/jobs/{job_id}/analysis` 验证通过
- `GET /api/v1/generation/jobs/{job_id}/sections` 已返回章节覆盖率字段并验证通过
- 项目级 `POST /api/v1/projects/{project_id}/generation/run` 与评分点分析联动验证通过
- `GenerationPage` 评分点映射、自检与覆盖率前端构建通过
- `POST /api/v1/generation/jobs/{job_id}/repair-uncovered` 验证通过
- `POST /api/v1/generation/jobs/{job_id}/self-revise` 验证通过
- 项目 `project-002` 的 `评分重点` 已验证可抽取出带分值内容，例如“技术方案40分，实施经验30分，报价30分”
- `GET /api/v1/review/rules` 验证通过
- `POST /api/v1/review/rules/initialize` 验证通过
- 法务反馈闭环学习功能验证通过
- 规则库配置化功能验证通过
- 合同审查页真实任务驱动改造构建通过
- 生成模块语法阻塞修复后，后端 `compileall` 再次通过
- `GET /api/v1/health` 二次验证通过
- `POST /api/v1/generation/jobs` 输入驱动生成验证通过
- `GET /api/v1/generation/jobs/{job_id}/sections` 验证通过
- `PATCH /api/v1/generation/jobs/{job_id}/sections/{section_id}` 验证通过
- `GET /api/v1/generation/jobs/{job_id}/export/docx` 实际文件下载验证通过
- 回标生成页前端 `npm run build` 验证通过
- 当前环境 `llm_ready = False` 状态确认完成
- 引入 LLM 生成后的后端 `compileall` 通过
- `POST /api/v1/generation/jobs` 在新服务进程下再次验证通过
- `POST /api/v1/decision/projects/{project_id}/run` 验证通过
- `GET /api/v1/decision/projects/{project_id}/latest` 验证通过
- `DecisionPage` 前端页面联动及占位态渲染验证通过
- `LLMDecisionClient` 接入验证（配置大模型密钥后可执行真实语义决策打分）
- `POST /api/v1/generation/jobs/{job_id}/sections/{section_id}/regenerate` 再次验证通过
- `GET /api/v1/projects/{project_id}/generation/context` 验证通过
- `POST /api/v1/projects/{project_id}/generation/run` 验证通过
- 项目级回标生成后的 `GET /api/v1/generation/jobs/{job_id}/sections` 验证通过
- 前端项目直达生成页地址 `/generation?projectId=project-001` 返回正常
- 项目级解析后端 `compileall` 再次通过
- `POST /api/v1/parsing/projects/{project_id}/upload` 验证通过
- `GET /api/v1/parsing/projects/{project_id}` 验证通过
- 上传后的项目级生成上下文已验证会读取新解析字段
- 闭环验证通过：`项目 -> 上传招标文件 -> 项目级提取 -> 项目级生成`
- 前端项目直达解析页地址 `/parsing?projectId=project-001` 返回正常
- 对象存储抽象层写入验证通过
- 本地对象存储回退路径 `backend/storage/projects/...` 验证通过
- 项目文档版本递增验证通过
- 项目解析上下文已验证返回文档版本列表
- OCR 依赖安装完成：`minio / pymupdf / ocrmac / rapidocr_onnxruntime`
- 中文扫描版 PDF 上传验证通过，接口返回 `OCR已解析`
- OCR 后的项目级字段提取验证通过
- OCR 项目上下文已验证可直接流向 `/api/v1/projects/{project_id}/generation/context`
- `GET /api/v1/generation/assets/indexed` 验证通过
- 轻量素材路由生成验证通过：`POST /api/v1/projects/{project_id}/generation/run`
- 路由后的章节返回已验证包含 `routed_assets / routing_reasons`
- 回标导出内容已验证包含命中的素材片段与命中原因
- `POST /api/v1/generation/assets` 验证通过
- `POST /api/v1/generation/assets/upload` 验证通过
- `POST /api/v1/generation/assets/refresh-index` 验证通过
- `GET /api/v1/projects/{project_id}/generation/preferences` 验证通过
- `PATCH /api/v1/projects/{project_id}/generation/preferences` 验证通过
- 项目级固定引用 / 禁用引用已验证会影响后续章节素材命中结果

未完成：

- 未完成 PostgreSQL 实际连通性验证
- 未完成浏览器端真实联调截图验证

## 6. 当前未完成事项

### 6.1 数据库层未正式化

当前只是过渡存储，不是正式业务建模。

未完成：

- Alembic 迁移
- 正式表结构拆分
- 项目详情表
- 文档表
- 文档块表
- 决策报告表
- 规则命中表
- 审核问题表
- 知识库资产表

### 6.2 后端业务能力未完成

当前未完成：

- 项目详情接口
- 文档解析任务接口
- LLM 语义审查接口（代码已接入，但环境未配置 API Key）
- 审批接口

已完成：

- 决策执行接口
- 合同文件上传接口
- 审查报告导出接口（Markdown + DOCX）
- 规则管理接口
- 法务反馈闭环接口
- 项目级招标文件上传接口
- 项目级 OCR / PDF 解析主链路
- 项目文档对象存储持久化与版本记录
- 回标生成轻量素材索引与章节路由
- 素材上传 / 新增接口
- 项目级素材固定引用 / 禁用引用控制

### 6.3 真实业务流程未完成

当前尚未接入：

- LLM 调用（代码已接入，环境未配置）
- RAG 检索
- 审批流

说明：

- 合同审查 MVP 已接入基础规则引擎
- 合同审查 MVP 已接入本地文件上传与条款切分
- 合同审查页已接入真实上传审查前端交互
- 规则库配置化已完成，支持通过 API 动态管理规则
- 法务反馈闭环学习已完成，支持记录反馈并更新规则统计
- 项目招标文件现已持久化到对象存储抽象层，并保留版本历史
- 项目解析现已支持文本 PDF 与扫描 PDF 的 OCR 抽取
- 当前 OCR 仍以纯文本字段抽取为主，未接版面还原、表格结构化和多文档合并
- 回标生成现已支持无向量库的轻量素材路由，并已补齐素材新增、上传、索引刷新和项目级偏好控制
- 当前知识库仍未接素材删除、片段级管理、异步索引任务和后台权限控制
- 当前外部 LLM 调用链已接入，但本地环境尚未提供 API Key，运行时仍回退到启发式语义审查

### 6.4 前端仍有过渡实现

当前未完成：

- React Router
- 页面级真实 loading/error/empty 状态
- 表单交互
- 文件上传组件
- 文档预览器
- 项目详情页
- 知识库页
- 规则中心页
- 审批记录页

### 6.5 联调未闭环

当前已经完成"SQLite 兜底模式"的本地联调验证，但还没做到 PostgreSQL 环境下的真正闭环。

未完成：

- 本地 PostgreSQL 跑起并完成初始化
- PostgreSQL 模式下的后端启动验证
- 浏览器里实际确认前端请求命中真实接口
- 前端实际调通 `projects/parsing/decision`
- 浏览器里确认页面数据来自真实接口而非 fallback mock

## 7. 当前技术债与注意事项

### 7.1 `workspace_panels` 是过渡方案

这是为了先跑通工作台和接口。

后续应拆分为正式业务表，而不是长期保留为主存储方式。

### 7.2 前端当前仍是单应用切换视图

现在没有正式路由，这有利于快速搭原型，但不适合长期扩展。

后续建议接入 React Router，并逐步做页面级 URL。

### 7.3 工作台数据有"双来源"

当前存在：

- 后端数据库种子数据
- 前端本地 mock 数据

这有利于开发兜底，但后续必须收敛，否则容易出现数据不一致。

### 7.4 已接入第一版真实 LLM 能力，但范围仍有限

当前状态：

- 已接入合同审查场景的真实 LLM 调用入口
- 当前通过 `backend/app/services/llm_client.py` 统一封装
- 默认使用 OpenAI Python SDK 的 `Responses API`
- 支持通过 `.env` 中的 `LLM_BASE_URL` 切到 OpenAI 兼容网关
- 当前仅用于"合同审查语义风险补充"，还没有扩展到 OCR、RAG、标书生成等链路

注意：

- `review_service` 会先执行规则审查，再尝试调用 LLM 产出语义风险
- 如果未配置 `LLM_API_KEY` 或外部调用失败，会自动回退到本地启发式语义审查
- 当前 LLM 返回被约束为 JSON，字段会映射成现有 `review_issues_records` 落库结构

仍未接入：

- Embedding
- 检索
- 标书生成场景的大模型推理
- 审核结果学习闭环

### 7.5 当前根目录 `.env` 已同时服务前后端

当前前端通过 `frontend/vite.config.ts` 中的 `envDir: ".."` 读取项目根目录环境变量。

注意：

- 根目录里的 `VITE_API_BASE_URL` 现在会对前端生效
- 后续如果改动 API 地址，应优先更新项目根目录 `.env`

### 7.6 SQLite 只是本地联调兜底

当前 `.env` 中使用了 SQLite 覆盖配置，仅用于当前机器继续开发。

后续切回正式环境时应：

- 清空 `DATABASE_URL_OVERRIDE`
- 启动 PostgreSQL
- 执行 `database/init/001-init.sql`
- 重新验证后端启动与接口数据

### 7.7 合同审查当前是"规则 + LLM 语义补充"的工作流，仍不是完整 Agent

当前"合同审查机器人"后端本质上是：

- 审查任务创建
- 文件上传驱动的文本抽取
- 条款切分与落库
- 规则命中
- LLM 语义审查补充
- LLM 失败时回退启发式语义审查
- 风险项落库
- 摘要与动作建议生成
- 人工处理状态回写

尚未实现：

- 多步工具调用编排
- 更细粒度的审查报告导出与人工批注闭环
- 规则自动调优（基于统计数据自动调整规则权重）

本轮已完成的关键文件：

- `backend/app/services/llm_client.py`
- `backend/app/modules/review/service.py`
- `backend/app/services/rule_config_service.py`
- `backend/app/models/review_feedback.py`
- `backend/app/models/rule_config.py`
- `backend/app/models/rule_statistics.py`
- `backend/app/core/config.py`
- `backend/pyproject.toml`
- 根目录 `.env`
- `frontend/src/pages/ReviewPage.tsx`
- `frontend/src/services/workspace.ts`
- `frontend/src/types.ts`

给后续 agent 的接手说明：

- 不要重复再造 LLM 调用层，优先复用 `LLMReviewClient`
- 先检查 `.env` 是否已填写 `LLM_API_KEY`
- 若要切换供应商，优先通过 `LLM_BASE_URL` + OpenAI 兼容协议适配
- 规则 + LLM 去重策略已完成，位于 `_merge_issues` 方法中
- 审查报告导出已支持 Markdown 和 DOCX 双格式
- 法务反馈闭环学习已完成，位于 `submit_feedback` 方法中
- 规则库配置化已完成，位于 `RuleConfigService` 中
- 若继续做前端联动，可考虑增加规则配置页面、问题筛选、批量处理等功能
- 若继续做后端增强，优先做"规则自动调优"和"多步工具调用编排"

## 8. 推荐的下一阶段工作计划

### 阶段一：先把开发链路跑通

当前状态：已完成 SQLite 兜底模式下的本地跑通。

优先级最高。

任务：

1. 本地启动 PostgreSQL
2. 清空 `.env` 中的 `DATABASE_URL_OVERRIDE`
3. 使用 PostgreSQL 完成后端启动验证
4. 启动前端并在浏览器确认页面拉到真实后端数据
5. 去掉不必要的前端 fallback 依赖

### 阶段二：把数据库建模正式化

任务：

1. 引入 Alembic
2. 拆分正式业务表
3. 让 `projects / parsing / decision` 不再依赖 `workspace_panels`
4. 为 `generation / review` 建立正式表结构

### 阶段三：做真实业务主链路

优先顺序建议：

1. 项目管理
2. 合同文件上传
3. OCR / DOCX / PDF 条款切分
4. 合同审查规则库配置化
5. 接入 LLM 语义审查
6. 回标文件草稿生成

### 阶段四：接入 AI 能力

建议顺序：

1. OCR / 结构化抽取
2. 知识库切片与检索
3. 决策解释生成
4. 标书章节生成
5. 材料审核语义风险识别

## 9. 下次续开发建议顺序

下次进入项目后，建议按这个顺序继续：

1. 阅读本文件
2. 查看 `docs/bid-agent-architecture.md`
3. 查看 `backend/app/services/workspace_service.py`
4. 查看 `frontend/src/services/workspace.ts`
5. 优先完成"PostgreSQL 模式联调 + 浏览器确认真实接口数据"

如果要继续编码，建议下一步直接做：

### 方案 A：完成正式数据库联调

- 安装并启动 PostgreSQL
- 执行 `database/init/001-init.sql`
- 清空 `DATABASE_URL_OVERRIDE`
- 重新验证 `/api/v1/workspace`
- 浏览器确认页面来自真实接口而非 mock fallback

### 方案 B：先做数据库正式化

- 加 Alembic
- 拆业务表
- 改 service 层

### 方案 C：先做业务功能

- 做合同文件上传接口
- 做条款切分与审查任务入口
- 做规则 + LLM 去重增强
- 做前端上传与重跑联动

## 10. 启动提示

### 后端

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

如果当前机器没有 PostgreSQL，可先使用项目根目录 `.env` 中的 SQLite 覆盖配置直接启动。

### 前端

```bash
cd frontend
npm install
npm run dev
```

### 数据库初始化

```bash
psql -h localhost -U bid_agent -d bid_agent -f database/init/001-init.sql
```

## 11. 备注

本文件应在每次完成一轮较大开发后更新，至少维护以下内容：

- 已完成事项
- 未完成事项
- 当前运行状态
- 下一步建议
- 是否存在临时方案或技术债
