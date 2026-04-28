# 🧠 头脑风暴：定价策略模块 AI 增强规划

## 一、现状诊断

经过对代码和参考资料的深入分析，当前定价策略模块存在以下核心问题：

### 1.1 功能现状

| 能力 | 当前状态 | 问题 |
|------|---------|------|
| 报价计算 | ✅ 已实现 | 纯计算器，含税/不含税互算、成本推算 |
| 价格评分 | ✅ 已实现 | 三种评分法（顶点K随机/固定、线性法），但参数全靠手动输入 |
| 竞商模拟 | ⚠️ 表面实现 | 本质是"手动填折扣率 → 排名表"，不是真正的模拟器 |
| 技术分 | ❌ 仅一个输入框 | `tech_score` 是一个0-100的手动输入值，无拆解、无AI评估 |
| AI建议 | ❌ 伪AI | `_generate_ai_advice` 是纯规则if-else，非LLM驱动 |
| 总评分 | ⚠️ 简单加权 | `tech_score * 0.5 + price_score * 0.5`，权重硬编码 |

### 1.2 参考资料揭示的业务真相

从参考资料中我提取出以下关键洞察：

**评分规则文档**揭示：
- 技术分由 **客观分**（如资质、业绩、参数响应）和 **主观分**（如运营方案、命题方案）组成
- 主观分通常分档：一档（15-20分）、二档（10-15分）、三档（5-10分）、四档（不得分）
- 售前人员根据经验自行评估落在哪一档，**这是AI可以介入的关键点**

**外协项目评分表**揭示：
- 真实投标中存在20+家竞商同时参与
- 折扣率分布从0.41到0.95不等，差异极大
- 陪标策略是真实存在的：找陪标厂家保证自己得分优势

**咪咕报价测算**揭示：
- 折扣报价场景下，评审价 = 1 - 折扣率
- 技术分主观分拆分：运营方案（20分）+ 命题方案（10分）+ 客观分（70分）
- 竞争厂商按档位得分不同，差距可达7.5分

---

## 二、三大增强方向

### 方向一：AI 技术分评估器（AI Tech Score Evaluator）

**核心思路**：将技术分从"一个手动输入的数字"升级为"AI驱动的多维度评估体系"。

#### 2.1.1 功能设计

```
技术分评估体系
├── 客观分（AI辅助校验）
│   ├── 资质匹配度 → AI从招标文件抽取资质要求，与企业知识库比对
│   ├── 业绩案例匹配度 → AI语义匹配历史案例与项目需求
│   ├── 参数响应度 → AI比对技术参数表与招标要求
│   └── 交付能力评估 → 基于历史项目交付数据
│
├── 主观分（AI核心驱动）
│   ├── 运营方案评分 → AI基于方案内容+评分标准+历史高分方案评估
│   ├── 命题方案评分 → AI基于方案创新性、可行性、匹配度评估
│   └── 其他主观项 → 可配置的主观评分项
│
└── 综合技术分
    ├── 加权汇总
    ├── 置信度标注
    ├── 分档建议（一档/二档/三档/四档）
    └── 人工确认入口
```

#### 2.1.2 AI 驱动方式

| 评估项 | AI输入 | AI输出 | 置信度策略 |
|--------|--------|--------|-----------|
| 资质匹配 | 招标资质要求 + 企业资质库 | 匹配率 + 缺失清单 | 高（结构化比对为主） |
| 业绩匹配 | 项目需求描述 + 历史案例库 | 相似度分 + 推荐案例 | 中（语义匹配有不确定性） |
| 运营方案 | 方案文本 + 评分标准 + 历史高分 | 分档建议 + 评分理由 | 中低（主观性强，需人工确认） |
| 命题方案 | 方案文本 + 创新性/可行性标准 | 分档建议 + 评分理由 | 中低（主观性强，需人工确认） |

#### 2.1.3 交互设计

- 左侧：技术分拆解面板（客观分/主观分各子项，可展开/折叠）
- 中间：AI评估结果（分档建议、评分理由、引用依据）
- 右侧：人工确认区（接受AI建议/手动调整，标注调整原因）
- 底部：技术分汇总条（加权总分 + 置信度区间）

---

### 方向二：AI 竞商情报引擎（AI Competitor Intelligence）

**核心思路**：将竞商折扣率从"手动填数字"升级为"AI预测 + 概率分布 + 情报溯源"。

#### 2.2.1 功能设计

```
AI竞商情报引擎
├── 竞商画像
│   ├── 公司基本信息（行业、规模、区域）
│   ├── 历史投标记录（参与项目数、中标率、折扣率趋势）
│   ├── 公开财务数据（营收、利润率、现金流）
│   └── 市场定位标签（价格杀手/技术导向/均衡型）
│
├── 折扣率预测
│   ├── 点估计（最可能折扣率）
│   ├── 概率分布（P10/P50/P90）
│   ├── 置信区间
│   └── 预测依据（历史数据/市场信号/专家经验）
│
├── 情报溯源
│   ├── 数据来源标记（公开招标/内部记录/行业报告）
│   ├── 时效性标注（最新/半年内/一年以上）
│   └── 可靠性评级（A/B/C/D）
│
└── 陪标识别
    ├── 异常折扣率检测
    ├── 关联公司识别
    └── 陪标概率评估
```

#### 2.2.2 AI 预测模型

```python
# 竞商折扣率预测特征工程
features = {
    "company_features": [
        "company_size",           # 公司规模
        "industry_position",      # 行业地位
        "historical_avg_discount", # 历史平均折扣率
        "win_rate",               # 历史中标率
        "profit_margin_trend",    # 利润率趋势
    ],
    "project_features": [
        "project_budget",         # 项目预算
        "project_type",           # 项目类型
        "industry",               # 所属行业
        "region",                 # 区域
        "bidder_count",           # 预计参与家数
    ],
    "market_features": [
        "market_competition",     # 市场竞争程度
        "season_factor",          # 季节因素
        "policy_impact",          # 政策影响
    ]
}
```

#### 2.2.3 交互设计

- 竞商列表：每家公司显示"AI预测折扣率"和"手动输入折扣率"双轨
- 概率分布图：每家竞商的折扣率概率分布曲线（类似风险分析中的P10/P50/P90）
- 情报卡片：点击竞商展开情报详情（数据来源、历史趋势、预测依据）
- 陪标预警：异常模式高亮提示

---

### 方向三：多智能体博弈模拟器（Multi-Agent Bidding Game Simulator）

**核心思路**：这是最激进也最有亮点的方向。将"竞商报价模拟器"升级为真正的"招投标博弈沙盘"，让AI Agent代表各家公司进行策略博弈。

#### 2.3.1 设计哲学

当前的模拟器是**静态的**：你输入折扣率 → 它算出排名。但真实的招投标是**动态博弈**：

- 每家公司都在猜测其他公司的报价
- 每家公司都有自己的策略偏好（激进/保守/均衡）
- 存在信息不对称（有的公司知道内幕，有的不知道）
- 存在联盟和陪标行为
- 评标规则本身会影响所有人的策略选择

**多智能体博弈模拟器**就是要模拟这个动态过程。

#### 2.3.2 架构设计

```
招投标博弈沙盘
├── 场景配置
│   ├── 招标项目参数（预算、评分规则、技术分权重）
│   ├── 参与方配置（公司数量、类型、策略偏好）
│   ├── 信息结构（公开信息/私有信息/不对称信息）
│   └── 博弈轮次（单轮密封/多轮迭代）
│
├── AI Agent 模型
│   ├── 策略型Agent（Strategic Agent）
│   │   ├── 激进型：低价冲标，利润率底线低
│   │   ├── 保守型：保利润为主，不参与价格战
│   │   ├── 均衡型：综合考量，追求期望收益最大化
│   │   └── 陪标型：配合某公司，报价策略服从目标
│   │
│   ├── 决策模型
│   │   ├── 效用函数 = 中标概率 × 项目利润 - 投标成本
│   │   ├── 贝叶斯信念更新（根据公开信息更新对对手的估计）
│   │   └── 纳什均衡求解（在给定信息结构下）
│   │
│   └── 行为特征
│       ├── 风险偏好（风险厌恶/中性/偏好）
│       ├── 学习能力（从历史博弈中调整策略）
│       └── 有限理性（不完美计算，存在策略噪声）
│
├── 模拟引擎
│   ├── 蒙特卡洛模拟（N次独立模拟，统计结果分布）
│   ├── 敏感性分析（关键参数变化对结果的影响）
│   ├── 纳什均衡分析（理论最优策略）
│   └── 博弈回放（可视化每轮博弈过程）
│
└── 结果输出
    ├── 中标概率分布（我方在不同报价下的中标概率）
    ├── 最优报价区间（期望收益最大化的报价范围）
    ├── 策略鲁棒性（对手策略变化时我方结果的稳定性）
    ├── 蒙特卡洛统计（均值/中位数/分位数）
    └── 博弈洞察（关键决策点、策略互动效应）
```

#### 2.3.3 博弈模型详解

**第一阶段：密封拍卖模型（MVP）**

采用一级密封拍卖（First-Price Sealed-Bid）模型，这是最接近真实招投标的博弈论模型：

```
每个Agent i 的决策：
max_{b_i} P(win|b_i) × (V_i - b_i) - C_bid

其中：
- b_i: Agent i 的报价
- V_i: Agent i 对项目的估值（基于成本+目标利润）
- P(win|b_i): 在报价b_i下的中标概率
- C_bid: 投标成本

中标概率取决于：
- 评分规则（价格分+技术分加权）
- 对手报价的分布估计
- 自身技术分水平
```

**第二阶段：贝叶斯博弈（P1）**

引入信息不对称和信念更新：

```
Agent i 对Agent j 折扣率的信念：
Belief_j ~ N(μ_j, σ_j²)

其中：
- μ_j: 基于历史数据和公开信息的先验估计
- σ_j²: 不确定性（信息越少，方差越大）

每轮博弈后：
- 公开中标结果
- Agent更新信念：μ_j ← posterior(μ_j | observed_outcome)
```

**第三阶段：多轮迭代博弈（P2）**

支持多轮模拟，Agent具有学习能力：

```
Agent策略更新：
- Q-Learning: Q(s,a) ← Q(s,a) + α[r + γmax Q(s',a') - Q(s,a)]
- 策略梯度: θ ← θ + α∇_θ J(θ)
- 模仿学习: 从历史真实投标数据中学习策略
```

#### 2.3.4 交互设计

```
博弈沙盘界面
├── 顶部：场景配置栏
│   ├── 项目选择/参数输入
│   ├── 评分规则选择
│   ├── 参与方配置（拖拽添加/删除Agent）
│   └── 模拟参数（轮次、采样数）
│
├── 左侧：Agent面板
│   ├── 每个Agent卡片（名称、策略类型、技术分、估值范围）
│   ├── Agent策略可调（滑块：激进←→保守）
│   └── 我方Agent高亮标记
│
├── 中间：博弈可视化
│   ├── 实时博弈动画（每轮Agent出价过程可视化）
│   ├── 蒙特卡洛结果分布图（中标概率 vs 报价曲线）
│   ├── 纳什均衡点标注
│   └── 敏感性热力图
│
├── 右侧：结果面板
│   ├── 最优报价建议（点估计+区间）
│   ├── 中标概率
│   ├── 期望利润
│   ├── 策略鲁棒性评分
│   └── 风险提示
│
└── 底部：博弈回放控制
    ├── 播放/暂停/步进
    ├── 轮次选择
    └── Agent决策日志
```

#### 2.3.5 可行性评估

| 维度 | 评估 | 说明 |
|------|------|------|
| 技术可行性 | ⭐⭐⭐⭐ | 博弈论模型成熟，蒙特卡洛模拟工程化难度适中 |
| 数据需求 | ⭐⭐⭐ | 需要历史投标数据训练Agent，初期可用规则+少量数据 |
| 用户价值 | ⭐⭐⭐⭐⭐ | 填补市场空白，目前没有同类产品提供博弈模拟 |
| 开发成本 | ⭐⭐⭐ | MVP（密封拍卖+蒙特卡洛）可控，多轮博弈需更多投入 |
| AI亮点 | ⭐⭐⭐⭐⭐ | 多Agent博弈是AI前沿方向，极具技术展示价值 |

---

## 三、功能分层与优先级

### 3.1 MVP（第一优先级）

| 功能 | 描述 | 依赖 |
|------|------|------|
| F1: 技术分拆解评估 | 客观分+主观分拆解，AI评估主观分档位 | LLM + 评分标准知识库 |
| F2: AI竞商折扣率预测 | 基于历史数据+规则预测竞商折扣率 | 历史投标数据 + 规则引擎 |
| F3: 密封拍卖博弈模拟 | 一级密封拍卖模型 + 蒙特卡洛模拟 | 博弈论引擎 |
| F4: 最优报价推荐 | 基于博弈模拟结果推荐最优报价区间 | F3 |
| F5: 真AI建议 | 用LLM替代现有if-else建议 | LLM |

### 3.2 P1（第二优先级）

| 功能 | 描述 | 依赖 |
|------|------|------|
| F6: 贝叶斯信念更新 | Agent根据博弈结果更新对对手的估计 | F3 |
| F7: 陪标识别预警 | 检测异常折扣率模式和关联公司 | F2 + 异常检测模型 |
| F8: 技术分AI校验 | 客观分AI辅助校验（资质匹配、参数响应） | 知识库 + NER |
| F9: 敏感性分析 | 关键参数变化对结果的影响分析 | F3 |
| F10: 博弈回放可视化 | 可视化每轮博弈过程 | F3 |

### 3.3 P2（第三优先级）

| 功能 | 描述 | 依赖 |
|------|------|------|
| F11: 多轮迭代博弈 | Agent具有学习能力，策略动态调整 | F6 + RL |
| F12: 纳什均衡求解 | 理论最优策略计算 | 博弈论求解器 |
| F13: 历史数据学习 | 从真实投标数据中学习Agent策略 | 大量历史数据 |
| F14: 协同博弈 | 支持联盟/陪标场景模拟 | F11 |
| F15: 报价策略A/B测试 | 不同报价策略的对比模拟 | F3 |

---

## 四、技术架构

### 4.1 新增服务

```
backend-v2/app/
├── services/
│   ├── pricing_service.py          # 现有，需重构
│   ├── tech_score_evaluator.py     # 新增：技术分AI评估
│   ├── competitor_intelligence.py  # 新增：竞商情报引擎
│   └── bidding_game_engine.py      # 新增：博弈模拟引擎
├── schemas/
│   ├── pricing.py                  # 现有，需扩展
│   ├── tech_score.py               # 新增
│   ├── competitor_intel.py         # 新增
│   └── bidding_game.py             # 新增
├── api/v1/endpoints/
│   ├── pricing.py                  # 现有，需扩展
│   ├── tech_score.py               # 新增
│   ├── competitor_intel.py         # 新增
│   └── bidding_game.py             # 新增
└── models/
    ├── bidding_scenario.py         # 新增：博弈场景持久化
    └── competitor_profile.py       # 新增：竞商画像持久化
```

### 4.2 博弈引擎核心

```python
# bidding_game_engine.py 核心抽象

class BiddingAgent:
    """博弈参与方Agent"""
    strategy_type: str          # aggressive / conservative / balanced / accomplice
    tech_score: float           # 技术分
    cost_base: float            # 成本基数
    profit_target: float        # 目标利润率
    risk_preference: float      # 风险偏好 [-1, 1]
    belief_about_others: dict   # 对其他Agent的信念

class BiddingScenario:
    """博弈场景"""
    budget: float
    scoring_method: str
    tech_weight: float
    price_weight: float
    agents: list[BiddingAgent]

class GameEngine:
    """博弈引擎"""
    def run_monte_carlo(scenario, n_simulations=1000) -> SimulationResult
    def find_nash_equilibrium(scenario) -> NashEquilibriumResult
    def sensitivity_analysis(scenario, params) -> SensitivityResult
    def recommend_optimal_bid(scenario, our_agent) -> OptimalBidResult
```

### 4.3 前端页面重构

```
frontend-v2/src/
├── views/
│   └── PricingStrategy.vue        # 重构为多Tab布局
├── components/pricing/
│   ├── TechScoreEvaluator.vue     # 新增：技术分评估面板
│   ├── CompetitorIntelligence.vue # 新增：竞商情报面板
│   ├── BiddingGameSimulator.vue   # 新增：博弈模拟器面板
│   ├── MonteCarloChart.vue        # 新增：蒙特卡洛结果图
│   ├── AgentConfigCard.vue        # 新增：Agent配置卡片
│   └── GameReplayPlayer.vue       # 新增：博弈回放播放器
├── services/
│   ├── pricing.ts                 # 现有，需扩展
│   ├── techScore.ts               # 新增
│   ├── competitorIntel.ts         # 新增
│   └── biddingGame.ts             # 新增
```

### 4.4 页面布局重构

```
报价策略页面（重构后）
├── Tab 1: 报价计算器（现有功能保留优化）
│   ├── 报价参数
│   ├── 报价金额
│   └── 得分预览
│
├── Tab 2: AI技术分评估（新增）
│   ├── 客观分评估
│   ├── 主观分AI评估
│   ├── 综合技术分汇总
│   └── 人工确认
│
├── Tab 3: 竞商情报（新增）
│   ├── 竞商画像列表
│   ├── AI折扣率预测
│   ├── 情报溯源
│   └── 陪标预警
│
└── Tab 4: 博弈沙盘（新增，核心亮点）
    ├── 场景配置
    ├── Agent配置
    ├── 博弈模拟运行
    ├── 结果可视化
    └── 最优报价推荐
```

---

## 五、数据模型扩展

### 5.1 新增数据库表

```sql
-- 竞商画像
CREATE TABLE competitor_profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT,
    region TEXT,
    size TEXT,
    market_position TEXT,        -- price_killer / tech_oriented / balanced
    historical_avg_discount REAL,
    win_rate REAL,
    data_reliability TEXT,       -- A/B/C/D
    last_updated DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 竞商历史投标记录
CREATE TABLE competitor_bid_history (
    id TEXT PRIMARY KEY,
    competitor_id TEXT REFERENCES competitor_profiles(id),
    project_name TEXT,
    project_budget REAL,
    discount_rate REAL,
    tech_score REAL,
    total_score REAL,
    won BOOLEAN,
    bid_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 博弈场景
CREATE TABLE bidding_scenarios (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    name TEXT NOT NULL,
    budget REAL,
    scoring_method TEXT,
    tech_weight REAL DEFAULT 0.5,
    price_weight REAL DEFAULT 0.5,
    config JSON,                 -- 场景配置JSON
    created_by TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 博弈模拟结果
CREATE TABLE simulation_results (
    id TEXT PRIMARY KEY,
    scenario_id TEXT REFERENCES bidding_scenarios(id),
    simulation_type TEXT,        -- monte_carlo / nash / sensitivity
    n_simulations INTEGER,
    result JSON,                 -- 完整结果JSON
    optimal_bid REAL,
    win_probability REAL,
    expected_profit REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 六、API 契约扩展

### 6.1 技术分评估 API

```
POST /api/v1/tech-score/evaluate
Request:
{
    "project_id": "string",
    "scoring_criteria": {
        "objective_items": [
            {"name": "资质匹配", "max_score": 70, "weight": 0.7}
        ],
        "subjective_items": [
            {"name": "运营方案", "max_score": 20, "tiers": [
                {"tier": 1, "range": [15, 20], "description": "..."},
                {"tier": 2, "range": [10, 15], "description": "..."},
                {"tier": 3, "range": [5, 10], "description": "..."},
                {"tier": 4, "range": [0, 5], "description": "..."}
            ]},
            {"name": "命题方案", "max_score": 10, "tiers": [...]}
        ]
    },
    "company_materials": {
        "qualifications": ["..."],
        "cases": ["..."],
        "proposal_text": "..."
    }
}
Response:
{
    "objective_score": {"total": 65, "items": [...], "confidence": 0.92},
    "subjective_score": {
        "items": [
            {"name": "运营方案", "ai_tier": 2, "ai_score": 12, 
             "confidence": 0.68, "reasoning": "...", "references": [...]}
        ],
        "total": 19
    },
    "total_tech_score": 84,
    "confidence_range": [78, 90],
    "needs_manual_review": true
}
```

### 6.2 竞商情报 API

```
POST /api/v1/competitor-intel/predict
Request:
{
    "project_id": "string",
    "competitors": [
        {"name": "亚信", "industry": "IT服务", "region": "全国"}
    ]
}
Response:
{
    "predictions": [
        {
            "name": "亚信",
            "point_estimate": 0.79,
            "distribution": {
                "p10": 0.72, "p50": 0.79, "p90": 0.88,
                "distribution_type": "beta",
                "params": {"alpha": 8.2, "beta": 2.1}
            },
            "confidence": 0.72,
            "evidence": [
                {"source": "历史投标记录", "reliability": "A", "date": "2025-12"},
                {"source": "公开财报利润率", "reliability": "A", "date": "2025-Q3"}
            ],
            "accomplice_probability": 0.05
        }
    ]
}
```

### 6.3 博弈模拟 API

```
POST /api/v1/bidding-game/simulate
Request:
{
    "scenario": {
        "budget": 2500000,
        "scoring_method": "vertexRandomK",
        "tech_weight": 0.5,
        "price_weight": 0.5,
        "k_value": 95
    },
    "our_agent": {
        "tech_score": 85,
        "cost_base": 1800000,
        "profit_target": 18,
        "risk_preference": 0.0
    },
    "competitor_agents": [
        {"name": "亚信", "strategy": "balanced", "tech_score": 80, 
         "discount_belief": {"mean": 0.79, "std": 0.05}},
        {"name": "中软", "strategy": "aggressive", "tech_score": 75,
         "discount_belief": {"mean": 0.74, "std": 0.08}}
    ],
    "simulation_config": {
        "n_simulations": 1000,
        "method": "monte_carlo"
    }
}
Response:
{
    "optimal_bid": {
        "recommended_price": 2280000,
        "recommended_discount": 0.088,
        "win_probability": 0.72,
        "expected_profit": 410000,
        "confidence_interval": [2150000, 2420000]
    },
    "simulation_stats": {
        "n_simulations": 1000,
        "win_rate_at_optimal": 0.72,
        "avg_profit_at_optimal": 410000,
        "median_rank": 1,
        "p10_rank": 1,
        "p90_rank": 3
    },
    "sensitivity": {
        "most_sensitive_param": "competitor_1_discount",
        "price_elasticity": -0.15
    },
    "nash_equilibrium": {
        "found": true,
        "our_optimal_discount": 0.092,
        "equilibrium_type": "pure_strategy"
    },
    "game_insights": [
        "在当前技术分优势下，报价可适当上浮3-5%仍保持竞争力",
        "竞争对手A若采取激进策略，我方需将折扣率提高至12%以上"
    ]
}
```

---

## 七、风险与缓解

| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|---------|
| 历史投标数据不足，AI预测不准 | 高 | 中 | 初期用规则+专家经验，逐步积累数据后切换ML |
| 博弈模型过于简化，不反映真实 | 中 | 高 | 分阶段迭代，MVP用简单模型，逐步增加复杂度 |
| 主观分AI评估可信度低 | 中 | 中 | 强制人工确认，AI只给建议不给决定 |
| 多Agent模拟计算量大 | 低 | 中 | 异步计算+缓存，前端轮询结果 |
| 用户不理解博弈论概念 | 中 | 中 | 提供引导式UI，用通俗语言解释专业术语 |

---

## 八、实施路线图

```
Phase 1 (MVP) ──────────────────────────────────────────
├── Week 1-2: 技术分拆解 + AI主观分评估
│   ├── 后端：tech_score_evaluator.py + API
│   ├── 前端：TechScoreEvaluator.vue
│   └── 集成：替换现有tech_score输入框
│
├── Week 3-4: AI竞商折扣率预测
│   ├── 后端：competitor_intelligence.py + API
│   ├── 前端：CompetitorIntelligence.vue
│   └── 集成：竞商列表双轨显示
│
├── Week 5-7: 博弈沙盘MVP
│   ├── 后端：bidding_game_engine.py（密封拍卖+蒙特卡洛）
│   ├── 前端：BiddingGameSimulator.vue + MonteCarloChart.vue
│   └── 集成：新Tab页
│
└── Week 8: 真AI建议 + 集成测试
    ├── 替换现有if-else为LLM调用
    └── 端到端测试

Phase 2 (P1) ──────────────────────────────────────────
├── 贝叶斯信念更新
├── 陪标识别预警
├── 敏感性分析
└── 博弈回放可视化

Phase 3 (P2) ──────────────────────────────────────────
├── 多轮迭代博弈 + 强化学习
├── 纳什均衡求解器
├── 历史数据学习
└── 协同博弈/陪标场景
```

---

## 九、总结

这份规划的核心逻辑是**三层递进**：

1. **第一层（AI技术分评估器）**：解决"输入质量"问题 —— 技术分不再是一个拍脑袋的数字，而是AI辅助的多维度评估
2. **第二层（AI竞商情报引擎）**：解决"对手信息"问题 —— 竞商折扣率不再全靠经验，而是AI预测+概率分布
3. **第三层（多智能体博弈模拟器）**：解决"决策质量"问题 —— 从静态计算到动态博弈，从"模拟器"到"沙盘"

三层的关系是**数据递进**的：技术分评估器的输出 → 作为博弈沙盘中Agent的技术分输入；竞商情报引擎的输出 → 作为博弈沙盘中Agent的信念先验。最终，博弈沙盘综合所有信息，输出最优报价建议。

这个设计的最大亮点在于**第三层**：将博弈论、多Agent系统和蒙特卡洛模拟引入招投标报价决策，这在当前市场上几乎没有同类产品。它不仅仅是一个"计算器"，而是一个真正的"决策智能体"。

---

## 七、实施进度跟踪

### 7.1 功能点计划表

| 编号 | 功能 | 阶段 | 状态 | 完成日期 | 备注 |
|------|------|------|------|---------|------|
| F1 | 技术分拆解评估 | MVP | ✅ 已完成 | 2026-04-26 | 客观分+主观分拆解，LLM驱动主观分档位评估 |
| F2 | AI竞商折扣率预测 | MVP | ✅ 已完成 | 2026-04-26 | 行业基准+统计建模+Beta分布+陪标概率 |
| F3 | 密封拍卖博弈模拟 | MVP | ✅ 已完成 | 2026-04-26 | 蒙特卡洛模拟+4种Agent策略类型 |
| F4 | 最优报价推荐 | MVP | ✅ 已完成 | 2026-04-26 | 基于MC模拟推荐报价+置信区间 |
| F5 | 真AI建议 | MVP→P1 | ✅ 已完成 | 2026-04-26 | LLM优先+规则降级双轨策略，`_PricingLLMClient`已接入`_generate_ai_advice` |
| F6 | 贝叶斯信念更新 | P1 | ✅ 已完成 | 2026-04-26 | 后端`_bayesian_belief_update`+schema `BayesianBeliefUpdate`已实现 |
| F7 | 陪标识别预警 | P1 | ✅ 已完成 | 2026-04-26 | 多维度异常检测+关联公司识别+2-gram名称相似度+预警等级分类 |
| F8 | 技术分AI校验 | P1 | ✅ 已完成 | 2026-04-26 | LLM辅助客观分匹配校验+缺失项识别+AI校验标签 |
| F9 | 敏感性分析 | P1 | ✅ 已完成 | 2026-04-26 | 预算/利润率敏感性+价格弹性计算 |
| F10 | 博弈回放可视化 | P1 | ✅ 已完成 | 2026-04-26 | ECharts中标概率/利润曲线+贝叶斯信念更新图+信念偏移详情表 |
| F11 | 多轮迭代博弈 | P2 | ✅ 已完成 | 2026-04-26 | 后端迭代博弈链路、前端模式切换、结果可视化、持久化与真实 HTTP 联调已完成 |
| F12 | 纳什均衡求解 | P2 | ✅ 已完成 | 2026-04-26 | 近似纯策略纳什均衡已实现 |
| F13 | 历史数据学习 | P2 | ✅ 已完成 | 2026-04-26 | 已打通历史聚合接口、前端学习入口和 Agent 参数回填 |
| F14 | 协同博弈 | P2 | ✅ 已完成 | 2026-04-26 | 联盟配置+3种协同策略(高报价陪标/价格垫/区间包裹)+迭代联动+持久化+前端入口 |
| F15 | 报价策略A/B测试 | P2 | ✅ 已完成 | 2026-04-28 | 多策略组对比模拟+比例Z检验+策略优选推荐+前端A/B测试模式 |

### 7.2 Phase 1 MVP 实施报告

#### 7.2.1 完成概述

Phase 1 MVP 已于 2026-04-26 完成，基于 `dev/PricingStrategy` 分支实施。核心交付物包括：

- **3个后端Schema模块**：tech_score / competitor_intel / bidding_game
- **3个后端Service模块**：tech_score_evaluator / competitor_intelligence / bidding_game_engine
- **3个API端点**：`/tech-score/evaluate` / `/competitor-intel/predict` / `/bidding-game/simulate`
- **3个前端Service模块**：techScore.ts / competitorIntel.ts / biddingGame.ts
- **3个前端组件**：TechScoreEvaluator / CompetitorIntelligence / BiddingGameSimulator
- **1个主页面重构**：PricingStrategy.vue 改为4-Tab布局

#### 7.2.2 各功能点实施详情

**F1: 技术分拆解评估**

| 维度 | 实施情况 |
|------|---------|
| 客观分评估 | ✅ 支持手动输入客观分，也支持按资质/案例/参数自动匹配评分 |
| 主观分评估 | ✅ LLM驱动主观分档位评估（4档制），含置信度和评分理由 |
| LLM降级策略 | ✅ LLM不可用时自动降级为启发式评估（基于方案文本长度） |
| 置信区间 | ✅ 基于客观分和主观分置信度加权计算综合置信区间 |
| 人工确认入口 | ✅ `needs_manual_review` 标记，前端展示确认按钮 |
| 前端交互 | ✅ 左右双栏布局：左侧配置+右侧结果，含分档标签、置信度进度条 |
| 数据流通 | ✅ "应用技术分"按钮将结果回传至报价计算器 |

**F2: AI竞商折扣率预测**

| 维度 | 实施情况 |
|------|---------|
| 行业基准数据 | ✅ 内置5个行业基准（IT服务/软件开发/系统集成/运维服务/通信） |
| 公司规模因子 | ✅ 大型/中型/小型三档规模调整系数 |
| 市场定位推断 | ✅ 基于公司名称关键词+规模自动推断市场定位（price_killer/tech_oriented/balanced） |
| Beta分布建模 | ✅ P10/P50/P90概率分布，支持scipy精确计算和正态近似降级 |
| 情报溯源 | ✅ 3类证据来源（历史投标/行业基准/市场经验），含可靠性评级 |
| 陪标概率 | ✅ 基于Z-score异常检测的陪标概率评估 |
| 前端交互 | ✅ 竞商信息录入+预测结果卡片，含概率分布可视化条、陪标风险标签 |
| 数据流通 | ✅ "应用预测结果"按钮将折扣率回传至报价计算器竞商列表 |

**F3: 密封拍卖博弈模拟**

| 维度 | 实施情况 |
|------|---------|
| Agent策略类型 | ✅ 4种策略：激进型/保守型/均衡型/陪标型，各有独立的折扣采样参数 |
| 蒙特卡洛模拟 | ✅ 遍历折扣率网格×N次模拟，统计各折扣率下的胜率和利润 |
| 最优折扣选择 | ✅ 优先选择胜率≥50%中利润最高的折扣率，否则选胜率最高的 |
| 评分方法兼容 | ✅ 支持线性评分法/顶点K随机/顶点K固定三种评分方法 |
| 前端交互 | ✅ 三栏布局：场景参数+我方Agent+竞商Agent → 结果面板（4指标+统计+洞察） |
| 数据流通 | ✅ "应用最优报价"按钮将推荐报价回传至报价计算器 |

**F4: 最优报价推荐**

| 维度 | 实施情况 |
|------|---------|
| 推荐报价 | ✅ 基于MC模拟的推荐含税报价 |
| 推荐折扣率 | ✅ 最优折扣率点估计 |
| 中标概率 | ✅ 在最优折扣率下的胜率 |
| 期望利润 | ✅ 基于成本基数或利润率推算 |
| 置信区间 | ✅ 折扣率的±5个网格点区间 |

**F5: 真AI建议**

| 维度 | 实施情况 |
|------|---------|
| 博弈洞察 | ✅ `_generate_game_insights` 基于模拟结果生成策略建议（中标概率/技术分/竞商策略/陪标） |
| 报价计算器AI建议 | ✅ `_PricingLLMClient` 已接入 `_generate_ai_advice`，支持 LLM优先 + 规则降级 |

**F9: 敏感性分析**

| 维度 | 实施情况 |
|------|---------|
| 预算敏感性 | ✅ 预算±2%/5%/10%变化对胜率的影响 |
| 利润率敏感性 | ✅ 利润率±2%变化对胜率的影响 |
| 价格弹性 | ✅ 基于胜率变化的弹性系数计算 |
| 最敏感参数识别 | ✅ 自动识别影响最大的参数 |

**F12: 纳什均衡求解**

| 维度 | 实施情况 |
|------|---------|
| 近似纯策略均衡 | ✅ 遍历折扣率网格，找到我方最佳响应 |
| 均衡类型标注 | ✅ 标注为"approximate_pure_strategy" |

#### 7.2.3 验证结果

| 验证项 | 结果 | 说明 |
|--------|------|------|
| 后端路由注册 | ✅ 通过 | 3个新端点 `/tech-score/evaluate` `/competitor-intel/predict` `/bidding-game/simulate` 已注册 |
| 后端模块导入 | ✅ 通过 | 3个service模块均可正常导入，无循环依赖 |
| 前端编译构建 | ✅ 通过 | `vite build` 编译成功，137个模块转换，产出372KB JS + 38KB CSS |
| API契约一致性 | ✅ 通过 | 前端TypeScript接口与后端Pydantic Schema字段一一对应 |
| 模块间数据流通 | ✅ 通过 | 技术分→计算器、竞商情报→计算器、博弈沙盘→计算器三条链路均实现 |
| LLM降级容错 | ✅ 通过 | LLM不可用时自动降级为启发式评估，不影响功能可用性 |

#### 7.2.4 已知不足与P1改进方向

| 问题 | 影响 | P1改进计划 |
|------|------|-----------|
| 客观分评估较粗糙 | 仅基于关键词匹配（资质/案例/参数），未做语义匹配 | F8: 引入NER+知识库做精确匹配 |
| 竞商预测依赖静态基准 | 行业基准数据硬编码，无法动态更新 | 接入历史投标数据库 |
| 陪标识别仅基于统计异常 | 未做关联公司识别 | F7: 增加关联公司图谱 |
| 博弈模拟性能 | 200个折扣点×N次模拟，N=1000时较慢 | 引入并行模拟或采样优化 |
| 报价计算器AI建议仍为规则 | if-else逻辑，非LLM驱动 | F5: 接入LLM生成建议 |
| 无数据持久化 | 博弈场景和结果未持久化 | 新增数据库表（spec第五章已设计） |
| 缺少可视化图表 | MC结果分布、敏感性热力图未实现 | F10: 引入ECharts/Plotly图表 |
| Agent信念无更新机制 | 竞商折扣率信念为固定先验 | F6: 贝叶斯信念更新 |

### 7.3 Phase 2 (P1) 实施报告

#### 7.3.1 P1-A: 贝叶斯信念更新 ✅ 已完成

**实施日期**: 2026-04-26

**后端实现**:
- 新增 `_bayesian_belief_update()` 函数（[bidding_game_engine.py](backend-v2/app/services/bidding_game_engine.py)）
- 新增 `BayesianBeliefUpdate` schema（[bidding_game.py](backend-v2/app/schemas/bidding_game.py)）
- `SimulationConfig.method` 新增 `"bayesian"` 选项
- `BiddingGameSimulateResponse` 新增 `bayesian_updates` 字段
- 当 `method="bayesian"` 时，Agent在多轮模拟中根据观察到的对手折扣率采样更新信念
- 核心算法：共轭正态-正态后验更新，先验N(μ,σ²) + 观察样本 → 后验N(μ',σ'²)
- 信念偏移量 `belief_shift` 超过2%时自动生成博弈洞察提示

**前端展示**:
- BiddingGameSimulator.vue 中模拟方法下拉框已支持 "bayesian" 选项
- 贝叶斯更新结果随 `simResult` 返回，前端已可展示（待F10可视化增强）

#### 7.3.2 P1-C: 真AI建议（报价计算器） ✅ 已完成

**实施日期**: 2026-04-26

**实现内容**:
- `_PricingLLMClient` 类已创建（[pricing_service.py](backend-v2/app/services/pricing_service.py)）
- 继承自 `_BaseLLMClient`，实现 `generate_pricing_advice()` 方法
- 支持技术分/排名/价格得分/利润率/折扣率/预算/竞争态势等多维度输入
- `_generate_ai_advice()` 已升级为 LLM优先 + 规则降级双轨策略
- 从 `calculate_pricing()` 传入竞商摘要上下文（各竞商折扣率和价格得分）
- LLM不可用时自动降级到规则if-else建议，保证功能可用性

#### 7.3.3 P1-B: 陪标识别预警增强 ✅ 已完成

**实施日期**: 2026-04-26

**实现内容**:
- 新增 `AccompliceAlert` schema（[competitor_intel.py](backend-v2/app/schemas/competitor_intel.py)），含风险等级/原因/关联公司/异常评分
- 新增 `accomplice_groups` 响应字段，返回检测到的关联公司分组
- 新增 `_find_affiliated_group()` 函数：基于8大企业系关键词库（华为系/中兴系/亚信系/东软系/浪潮系/中软系/软通系/博彦系）识别关联公司
- 新增 `_compute_name_similarity()` 函数：基于2-gram Jaccard相似度检测名称相似公司
- 新增 `_detect_accomplice_alerts()` 函数：多维度异常检测
  - Z-score折扣率异常检测（偏高/偏低）
  - 关联公司同组参与投标检测
  - 名称相似度关联检测
  - 低价型公司异常低价检测
  - 异常偏高折扣率陪标检测
- 风险等级分类：high（≥0.5）/ medium（≥0.25）/ low（>0）
- 前端展示：关联公司预警面板 + 陪标分析详情卡片 + 风险等级标签

#### 7.3.4 P1-D: 博弈回放可视化 ✅ 已完成

**实施日期**: 2026-04-26

**实现内容**:
- 安装 echarts + vue-echarts 依赖
- 新增 `GameReplayCharts.vue` 组件（[GameReplayCharts.vue](frontend-v2/src/components/pricing/GameReplayCharts.vue)）
- 中标概率 vs 折扣率曲线图（含最优折扣率标记线）
- 期望利润 vs 折扣率曲线图（含最优折扣率标记线）
- 贝叶斯信念更新散点图（先验→后验偏移可视化）
- 信念偏移详情表格（先验均值/后验均值/偏移量/σ变化/观察数）
- 后端 `raw_simulation_data` 字段填充MC模拟详细数据
- 集成到 BiddingGameSimulator.vue 中，模拟结果下方自动展示图表

#### 7.3.5 P1-E: 技术分AI校验 ✅ 已完成

**实施日期**: 2026-04-26

**实现内容**:
- 新增 `_TechScoreLLMClient.verify_objective_items()` 方法（[tech_score_evaluator.py](backend-v2/app/services/tech_score_evaluator.py)）
- LLM根据评分项要求和企业材料，校验每个客观评分项的匹配情况
- 识别已满足和缺失的要求，给出匹配率和缺失清单
- Schema扩展：`ObjectiveScoreItem` 新增 `ai_verified`/`ai_verification_detail`/`missing_items` 字段
- `_evaluate_objective_items()` 升级为 LLM校验优先 + 规则降级双轨策略
- AI校验可用时使用LLM返回的匹配率和缺失项，不可用时降级到关键词匹配
- 前端展示：AI校验标签 + 校验详情 + 缺失项标签列表
- 置信度提升：AI校验可用时confidence从0.85提升到0.9

#### 7.3.6 P1-F: 数据持久化 ✅ 已完成

**实施日期**: 2026-04-26

**实现内容**:
- 新增 `pricing.py` 数据模型（[pricing.py](backend-v2/app/models/pricing.py)），定义4张数据库表：
  - `pricing_calculations`: 报价计算记录
  - `tech_score_evaluations`: 技术分评估记录
  - `competitor_predictions`: 竞商预测记录
  - `bidding_game_simulations`: 博弈模拟记录
- 新增 `pricing_persistence.py` 持久化服务（[pricing_persistence.py](backend-v2/app/services/pricing_persistence.py)）
  - `save_pricing_calculation()`: 保存报价计算结果
  - `save_tech_score_evaluation()`: 保存技术分评估结果
  - `save_competitor_prediction()`: 保存竞商预测结果
  - `save_bidding_game_simulation()`: 保存博弈模拟结果
  - 各模块的 `list_*()` 查询函数
- 4个API端点集成持久化：
  - `/pricing/calculate` → 自动保存计算结果
  - `/tech-score/evaluate` → 自动保存评估结果
  - `/competitor-intel/predict` → 自动保存预测结果
  - `/bidding-game/simulate` → 自动保存模拟结果
- 持久化采用非阻塞模式：写入失败不影响API返回结果
- 数据库迁移脚本已生成并stamp到最新版本

### 7.4 Phase 3 (P2) 推进进展

#### 7.4.1 P2-A: F11 多轮迭代博弈 ✅ 已完成

**实施日期**: 2026-04-26

**功能概述**:
- 在原有单轮密封报价模拟基础上，引入多轮博弈迭代能力，使 Agent 能依据轮次输赢、利润空间和策略偏好动态调整折扣率锚点。
- 输出轮次级结果、策略演化轨迹、收敛轮次、最终建议折扣和近轮次期望收益，为后续 F13 历史数据学习和 F14 协同博弈提供可复用数据结构。

**后端实现**:
- `SimulationConfig` 扩展 `iterative_rounds` / `learning_rate` / `exploration_rate` / `convergence_threshold` 四个参数，`method` 新增 `"iterative"` 选项。
- `bidding_game.py` 新增 `IterationRoundResult`、`AgentStrategyEvolution`、`IterativeGameResult`，并在 `BiddingGameSimulateResponse` 中正式启用 `iterative_result`。
- `bidding_game_engine.py` 新增 `_run_iterative_game()` 和 `_update_discount_anchor()`：
  - 每轮基于当前信念锚点采样我方与竞商折扣率
  - 按输赢、排名、利润率和策略偏好更新各 Agent 的下一轮折扣均值
  - 连续多轮变化小于阈值时判定收敛
- 同步修正博弈引擎总分计算逻辑：我方总分改为使用 `our_agent.tech_score`，不再硬编码为 100 分。
- `raw_simulation_data` 新增 `iterative_rounds` 与 `strategy_evolutions`，供前端图表和明细表复用。

**持久化与契约**:
- `pricing.py` 的 `BiddingGameSimulation` 新增 `iterative_result` JSON 字段。
- `pricing_persistence.py` 已支持保存 `response.iterative_result`。
- 已新增 Alembic 迁移 `f11c2a8e9b7d_add_iterative_result_to_bidding_game.py`，对存在的 `bidding_game_simulations` 表执行增量加列。

**前端实现**:
- `biddingGame.ts` 扩展迭代模式请求参数、响应类型和原始回放数据类型。
- `BiddingGameSimulator.vue` 新增模拟模式切换、迭代参数配置区、收敛摘要卡片、策略演化表、轮次明细表。
- `GameReplayCharts.vue` 新增“多轮迭代趋势”和“策略演化轨迹”两组 ECharts 视图。

**验证结果**:

| 验证项 | 结果 | 说明 |
|--------|------|------|
| 后端语法校验 | ✅ 通过 | `python3 -m compileall app` 通过，新增 schema / service / model 均可编译 |
| 前端构建 | ✅ 通过 | `npm run build` 成功，新增迭代模式类型和页面渲染未破坏现有构建 |
| IDE 诊断 | ✅ 通过 | 已编辑的 Vue / TypeScript / Python 文件无新增诊断错误 |
| 服务层运行态烟测 | ✅ 通过 | 使用 `python3.11` 直接调用 `simulate_bidding_game()`，成功返回 `iterative_result`，示例结果包含 `rounds=8`、`convergence_round=3` |
| 持久化烟测 | ✅ 通过 | 使用内存 SQLite + `save_bidding_game_simulation()` 完成保存，确认 `iterative_result` 成功落库且 `rounds=8` |
| API 处理层烟测 | ✅ 通过 | 直接调用 endpoint `simulate_bidding_game()`，确认可返回 `iterative_result` 且已写入 `bidding_game_simulations` |
| HTTP/真实库联调 | ✅ 通过 | 启动最小 FastAPI 服务后，已完成 `POST /api/v1/auth/login` + `POST /api/v1/bidding-game/simulate` 真请求验证，确认 `iterative_result.rounds=8`、`convergence_round=3`，并写入 `/tmp/saleagents_f11_http.db` |

**当前结论**:
- F11 已完成代码接入、类型接入、前端结果展示和真实 HTTP 联调验证，当前状态调整为“已完成”。
- 下一步优先项为：在正式环境执行 Alembic 迁移，并补一次发布后回归验证。

#### 7.4.2 P2-B: F13 历史数据学习 ✅ 已完成

**实施日期**: 2026-04-26

**功能概述**:
- 基于已保存的 `competitor_predictions` 和 `bidding_game_simulations` 记录，为指定项目和竞对列表聚合折扣样本，自动生成可回填到博弈 Agent 的历史先验参数。
- 历史样本覆盖手工录入历史折扣、AI 竞商点估计、竞对先验均值和多轮迭代轮次折扣，为后续 F14 协同博弈和更细粒度策略学习提供统一输入。

**后端实现**:
- `bidding_game.py` 新增 `BiddingGameHistoryLearningRequest`、`CompetitorHistoryProfile`、`BiddingGameHistoryLearningResponse`。
- `pricing_persistence.py` 新增 `build_competitor_history_profiles()`：
  - 复用 `list_competitor_predictions()` 与 `list_bidding_game_simulations()`
  - 统一归一化竞对名称和折扣率取值
  - 汇总 `manual_historical_input` / `intel_prediction` / `agent_prior_mean` / `iterative_round` 四类样本来源
  - 输出 `discount_belief_mean`、`discount_belief_std`、`sample_count`、`source_breakdown`
- `bidding_game.py` 新增 `POST /api/v1/bidding-game/history-learning` 路由，支持按 `project_id` 和 `competitor_names` 做项目级历史学习。
- 历史聚合对 `agent_configs` 按首项视为我方 Agent 进行排除，避免因我方名称变更导致己方先验误计入竞对样本。

**前端实现**:
- `biddingGame.ts` 新增历史学习请求/响应类型与 `fetchHistoricalAgentConfigs()`。
- `CompetitorIntelligence.vue` 新增“从历史数据学习”入口，可携带当前项目和竞对名单发起学习。
- `PricingStrategy.vue` 新增历史学习联动：
  - 从当前选中项目提取 `project_id`
  - 将返回的历史画像转发给博弈沙盘
  - 修复组件暴露类型与输入框 blur 定时器的类型问题
- `BiddingGameSimulator.vue` 新增 `applyHistoryProfiles()`，支持按竞对名称回填 `discount_belief_mean` / `discount_belief_std`，并补充关键 debug 日志。

**验证结果**:

| 验证项 | 结果 | 说明 |
|--------|------|------|
| 前端构建 | ✅ 通过 | `npm run build` 成功，历史学习入口和联动逻辑未破坏现有构建 |
| IDE 诊断 | ✅ 通过 | 已编辑的 Vue / TypeScript / Python 文件无新增诊断错误 |
| 路由处理层最小烟测 | ✅ 通过 | 基于内存 SQLite 直接调用 `learn_bidding_game_history()`，确认返回 `total_records_scanned=2`、`matched_competitor_count=2` |
| 聚合规则校验 | ✅ 通过 | 样本来源统计、均值/标准差收敛规则与 `source_breakdown` 输出符合预期 |
| 回归用例 | ⚠️ 受环境阻塞 | 新增 `tests/test_bidding_game_history_learning.py`，但仓库当前缺少 `python-docx`，`pytest` 在加载 `app.main` 时被现有 review 模块依赖阻塞 |

**当前结论**:
- F13 已完成接口、前端入口、参数回填和最小运行态验证。
- 当前剩余事项主要为测试环境补齐 `python-docx` 后执行完整 `pytest` 回归，不阻塞功能完成状态。

#### 7.4.3 P2 后续计划

| 优先级 | 功能 | 当前状态 | 下一步实施思路 |
|--------|------|---------|---------------|
| P2-A | F11: 多轮迭代博弈 | ✅ 已完成 | 在正式环境执行 Alembic 迁移并补一次发布后回归 |
| P2-B | F13: 历史数据学习 | ✅ 已完成 | 已打通历史聚合接口、前端学习入口和 Agent 参数回填，F13 文档全量同步 |
| P2-C | F14: 协同博弈 | ✅ 已完成 | 联盟配置+3种协同策略(高报价陪标/价格垫/区间包裹)+迭代联动+持久化+前端入口 |
| P2-D | F15: 报价策略A/B测试 | ✅ 已完成 | 多策略组对比模拟+比例Z检验+策略优选推荐+前端A/B测试模式 |

#### 7.4.4 P2-C: F14 协同博弈 ✅ 已完成

**实施日期**: 2026-04-26

**功能概述**:
- 在博弈模拟中引入联盟/陪标协同机制，支持用户配置多组联盟（每组含一个主攻方和若干陪标方），引擎在 MC 模拟和迭代模式中按联盟关系协调折扣率采样。

**后端 Schema 扩展**:
- `AllianceConfig`: leader / supporters / coordination_type / discount_spread / leader_bonus
- `CoalitionConfig`: alliances 列表 + enabled 开关 + profit_redistribution
- `CoalitionAgentEffect` / `CoalitionResult`: 联盟角色标注 + 策略类型分布
- `BiddingGameSimulateRequest.coalition_config` 可选注入
- `BiddingGameSimulateResponse.coalition_result` 返回联盟分析数据

**3种协同策略**:
1. `high_bid_escort`（高报价陪标）：陪标方折扣锚点 = clip(leader_discount - spread)，以更高价衬托主攻方报价
2. `price_padding`（价格垫）：陪标方在 leader_discount ± spread/2 范围内随机分布，削弱主攻方异常报价的突兀感
3. `bracket`（区间包裹）：陪标方轮流在 leader_discount 上下两侧形成价格区间，制造主攻方报价"居中正常"的假象

**引擎改造**:
- `_resolve_alliance_map()`: 解析联盟配置为 Agent ↔ 联盟信息映射表，同步标记 BiddingAgent 的 alliance_id/alliance_role
- `_apply_coalition_to_discount()`: 根据策略类型将陪标方采样折扣拉向目标位置（70%/50%/60% 向心调整比例）
- `_run_single_simulation()`: 新增 alliance_map 参数，采样后执行联盟协调
- `_monte_carlo_simulation()` / `_analyze_sensitivity()` / `_find_nash_equilibrium()`: 全线穿透 alliance_map
- `_run_iterative_game()`: 每轮采样后协调联盟折扣 + 每轮锚点更新后重同步陪标方锚点 = clip(leader_anchor - spread)
- `simulate_bidding_game()`: 统一构建联盟映射、穿透给所有子函数、产出 `CoalitionResult`（含联盟数/策略分布/Agent 角色表）

**持久化**:
- `BiddingGameSimulation.coalition_config` 新增 JSON 字段
- `save_bidding_game_simulation()` 自动保存 `response.coalition_result`
- Alembic 迁移: `a4e2d8f1b3c7_add_coalition_config_to_bidding_game.py`

**前端实现**:
- `biddingGame.ts`: 新增 AllianceConfig / CoalitionConfig / CoalitionAgentEffect / CoalitionResult 类型，`BiddingGameSimulatePayload.coalition_config` 和 `BiddingGameSimulateResponse.coalition_result`
- `BiddingGameSimulator.vue`:
  - 新增"协同博弈配置"可折叠面板：启用开关、多联盟管理、主攻方/陪标方选择、策略类型和折扣间距
  - 结果区新增 amber 色调联盟结果面板（联盟数量、策略分布、Agent 角色表）
  - 模拟请求自动携带 `coalitionConfig`

**验证结果**:
- 后端 `compileall` 通过
- 前端 `npm run build` 通过
- IDE 诊断仅剩 2 个可忽略的类型提示
- 最小运行态验证: 带联盟配置的 MC 模拟正确返回 coalition_result（alliance_count=1, agent_effects 含 leader/supporter 角色标注）
- 不带联盟配置的调用返回 coalition_result=None，向后兼容

#### 7.4.5 P2-D: F15 报价策略A/B测试 ✅ 已完成

**实施日期**: 2026-04-28

**功能概述**:
- 在博弈模拟中引入策略A/B测试模式，支持用户同时配置2-5组不同参数的我方Agent（利润率/风险偏好/策略类型等），在相同场景和竞商条件下并行执行蒙特卡洛模拟，对比各组胜率、利润和统计显著性，自动推荐最优策略。

**后端 Schema 扩展**:
- `ABTestStrategyGroup`: label + our_agent 配置
- `ABTestRequest`: scenario + strategy_groups(2-5) + competitor_agents + n_simulations + coalition_config
- `ABTestStrategyResult`: label / optimal_discount / recommended_price / win_probability / expected_profit / median_rank / avg_profit / confidence_interval / win_rate_curve / profit_curve
- `ABTestComparison`: best_strategy / best_win_probability / best_profit / win_rate_ranking / profit_ranking / significance_tests / recommendation
- `ABTestResponse`: strategy_results + comparison + insights

**引擎实现**:
- `run_ab_test()`: 遍历每个策略组，复用 `_monte_carlo_simulation()` 计算各组最优折扣和统计指标
- 比例Z检验: 对每对策略组做双比例Z检验（H₀: p_A = p_B），计算 z_score / p_value / significant_at_005
- 自动推荐: 基于胜率排名和利润排名综合推荐最优策略，生成文字推荐语
- 洞察生成: 对比最优与最差策略的差异，提示利润率/风险偏好调整方向

**API 端点**:
- `POST /api/v1/bidding-game/ab-test` → `ABTestResponse`

**前端实现**:
- `biddingGame.ts`: 新增 ABTestPayload / ABTestStrategyGroup / ABTestStrategyResult / ABTestComparison / ABTestResponse 类型和 `runABTest()` 函数
- `BiddingGameSimulator.vue`:
  - 模拟模式下拉框新增"A/B测试"选项
  - A/B测试模式下显示策略组配置面板（2-5组，每组可配利润率/风险偏好/策略类型）
  - 我方Agent面板在A/B测试模式下隐藏（由策略组替代）
  - 结果区新增A/B测试对比面板：胜率排名、利润排名、策略详情表、统计显著性检验表、洞察列表
  - "应用最优报价"按钮在A/B测试模式下应用最优策略组结果

**验证结果**:

| 验证项 | 结果 | 说明 |
|--------|------|------|
| 后端编译 | ✅ 通过 | `python3 -m compileall` 通过 |
| 后端导入 | ✅ 通过 | ABTestRequest/ABTestResponse/run_ab_test 均可正常导入 |
| 运行态烟测 | ✅ 通过 | 2组策略(A:balanced/18% vs B:aggressive/12%)，返回 best=A, significance_tests=1, insights=2 |
| 前端构建 | ✅ 通过 | `vite build` 成功，722个模块转换 |
| API端点注册 | ✅ 通过 | `/bidding-game/ab-test` 已注册到路由 |

---

### 7.5 全量功能完成总结

截至 2026-04-28，定价策略模块全部 15 个功能点均已完成实施：

| 阶段 | 功能点 | 状态 |
|------|--------|------|
| MVP | F1-F5: 技术分评估+竞商预测+博弈模拟+最优报价+真AI建议 | ✅ 全部完成 |
| P1 | F6-F10: 贝叶斯更新+陪标识别+技术分校验+敏感性分析+回放可视化 | ✅ 全部完成 |
| P2 | F11-F15: 迭代博弈+纳什均衡+历史学习+协同博弈+A/B测试 | ✅ 全部完成 |
