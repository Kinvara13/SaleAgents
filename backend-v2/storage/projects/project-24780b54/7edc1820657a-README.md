# SaleAgents

招投标智能体 MVP 项目骨架。

当前工程默认采用轻量方案：

- `backend`：FastAPI
- `frontend`：React + Vite + TypeScript
- `database`：PostgreSQL + pgvector 初始化脚本
- `storage/cache`：本地或现有环境中的 PostgreSQL、Redis、对象存储

## 目录结构

```text
SaleAgents/
├── backend/        # 后端 API 与业务模块
├── frontend/       # 前端工作台
├── database/       # 数据库初始化脚本
└── docs/           # PRD、架构、页面设计
```

## 快速开始

### 1. 准备本地依赖

请确保本地已经准备好以下服务，或接入现有开发环境：

- PostgreSQL + `pgvector`
- Redis
- 对象存储

默认本地连接约定：

- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Object Storage Endpoint: `localhost:9000`

如果当前只是想先把前后端链路跑通，也可以使用 SQLite 作为本地兜底，不必先安装 PostgreSQL。

先在项目根目录创建 `.env`：

```bash
cp .env.example .env
```

然后把下面这一行填进 `.env`：

```bash
DATABASE_URL_OVERRIDE=sqlite:///./bid_agent.db
```

说明：

- 这个 SQLite 文件会在 `backend/` 目录下自动创建
- 启动后端时仍然建议先 `cd backend`
- 当你准备切回 PostgreSQL 时，清空 `DATABASE_URL_OVERRIDE` 即可

### 2. 初始化数据库

```bash
psql -h localhost -U bid_agent -d bid_agent -f database/init/001-init.sql
```

### 3. 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

后端健康检查：

```bash
curl http://localhost:8000/api/v1/health
```

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：

```text
http://localhost:5173
```

## 当前已搭好的内容

- 基础目录结构
- FastAPI 启动入口
- 健康检查接口
- 招投标三模块的后端扩展位
- React 工作台首页骨架
- PostgreSQL `pgvector` 初始化脚本
- 本地运行说明

## 推荐下一步

1. 补充数据库表结构与迁移
2. 接入项目管理、文档上传、知识库和规则管理接口
3. 接入文档解析与 AI 工作流
4. 对接页面原型中的项目台账、决策页、生成页、审核页

## 端到端招投标操作指南

系统已打通从新建商机到导出标书的全链路，并且去除了假数据，真实对接了大模型 `mimo-v2-pro` 和本地 SQLite 数据库。请按照以下步骤体验：

### 1. 新建项目与标书上传
- 进入 **商机台账** 页面，点击“新建商机”。
- 填写项目名称（如“咪咕公司网络阵地运营管理系统一期工程项目”）、金额等信息。
- 项目创建后，目前系统支持将 PDF 标书存入数据库对应的 `project_documents` 中。

### 2. 要求提取（解析标书）
- 在商机台账列表中，找到对应的项目，点击操作列的 **提取** 按钮。
- 点击右上角的 **重新抽取招标要求**。
- **背后逻辑**：后端会解析 PDF 标书，通过大模型和正则匹配，自动抽取出资质要求、评分项、违约条款等核心字段，并展示在卡片中。

### 3. 应答策略（AI 辅助决策）
- 从要求提取页面右上角，或通过左侧菜单进入 **应答策略** 页面。
- 确保右上角项目下拉框选中目标项目，点击 **刷新策略评估**。
- **背后逻辑**：系统将提取到的招标要求发送给大模型，AI 结合内置规则，对项目风险进行评估，生成雷达图、命中红线规则和建议评级（如 P1 核心利润项目）。

### 4. 回标编写（自动生成标书）
- 从左侧菜单进入 **回标编写** 页面。
- 选择目标项目和 **标准回标模板**。
- 点击顶部抢眼的 **生成回标初稿** 按钮。
- **背后逻辑**：大模型根据提取的要求、策略和内置大纲，逐段生成标书章节（如公司简介、技术方案）。页面大纲会实时显示生成进度。
- 点击已完成的章节，可在右侧编辑器中进行二次人工润色。

### 5. 导出交付
- 等待所有章节生成完毕后，点击页面右上角的 **导出为 Word**。
- 系统会将大模型生成好的分块内容拼接成一份完整的 `.docx` 文件并下载到本地。

> **提示**：如果想要使用页面左下角的悬浮球唤起 **PageAgent**（自然语言操控 UI），可以直接点击该紫蓝色悬浮球，输入“帮我新建一个商机”即可体验 AI 自动操作网页。
