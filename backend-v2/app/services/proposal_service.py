from uuid import uuid4
import json

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.proposal_section import ProposalSection
from app.models.technical_document import TechnicalDocument
from app.models.business_document import BusinessDocument
from app.schemas.proposal import (
    ProposalSectionSummary,
    ProposalSectionDetail,
    ProposalSectionUpdateRequest,
    ProposalGenerationRequest,
    SCORING_RULES,
)


PROPOSAL_SECTIONS = [
    "整体解决方案",
    "软件架构",
    "功能实现方案",
    "系统接口方案",
    "部署方案",
    "兼容性",
    "系统安全",
    "项目经理能力",
    "人员能力",
    "维保期限",
]


def get_or_create_project(db: Session, project_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return project


def _get_project_context(db: Session, project_id: str) -> dict:
    """获取项目上下文：客户背景、公司背景、技术打分表信息"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return {}

    context = {
        "project_name": project.name,
        "client": project.client,
        "bidding_company": project.bidding_company or "亚信科技（中国）有限公司",
        "deadline": project.deadline,
        "amount": project.amount,
    }

    # 获取技术文档中的评分要求
    tech_docs = (
        db.query(TechnicalDocument)
        .filter(TechnicalDocument.project_id == project_id)
        .all()
    )
    scoring_hints = []
    for doc in tech_docs:
        if doc.score_point:
            scoring_hints.append(f"[{doc.doc_name}]: {doc.score_point}")
        if doc.rule_description:
            scoring_hints.append(f"[{doc.doc_name}评分规则]: {doc.rule_description[:200]}")

    context["scoring_hints"] = scoring_hints

    # 获取商务文档中的评分要求
    biz_docs = (
        db.query(BusinessDocument)
        .filter(BusinessDocument.project_id == project_id)
        .all()
    )
    for doc in biz_docs:
        if doc.score_point:
            context.setdefault("scoring_hints", []).append(f"[{doc.doc_name}]: {doc.score_point}")

    return context


def list_sections(db: Session, project_id: str) -> list[ProposalSectionSummary]:
    get_or_create_project(db, project_id)
    sections = (
        db.query(ProposalSection)
        .filter(ProposalSection.project_id == project_id)
        .order_by(ProposalSection.id)
        .all()
    )
    return [ProposalSectionSummary.model_validate(s) for s in sections]


def get_section_detail(db: Session, project_id: str, section_id: str) -> ProposalSectionDetail:
    section = (
        db.query(ProposalSection)
        .filter(ProposalSection.id == section_id, ProposalSection.project_id == project_id)
        .first()
    )
    if not section:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="章节不存在")
    return ProposalSectionDetail.model_validate(section)


def update_section(
    db: Session, project_id: str, section_id: str, payload: ProposalSectionUpdateRequest
) -> ProposalSectionDetail:
    section = (
        db.query(ProposalSection)
        .filter(ProposalSection.id == section_id, ProposalSection.project_id == project_id)
        .first()
    )
    if not section:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="章节不存在")

    if payload.content is not None:
        section.content = payload.content
    if payload.is_confirmed is not None:
        section.is_confirmed = payload.is_confirmed
    db.commit()
    db.refresh(section)
    return ProposalSectionDetail.model_validate(section)


def generate_proposal(
    db: Session,
    project_id: str,
    payload: ProposalGenerationRequest | None = None,
) -> list[ProposalSectionSummary]:
    """AI 生成技术建议书章节，结合客户背景、公司背景、技术打分表要求"""
    project = get_or_create_project(db, project_id)
    if payload is None:
        payload = ProposalGenerationRequest()

    # 获取项目上下文
    ctx = _get_project_context(db, project_id)
    scoring_hints = ctx.get("scoring_hints", [])

    # 删除旧的生成章节
    db.query(ProposalSection).filter(
        ProposalSection.project_id == project_id,
        ProposalSection.is_generated == True,
    ).delete()

    created = []
    for name in PROPOSAL_SECTIONS:
        rule_info = SCORING_RULES.get(name, {"max": 100})
        section_score = _compute_section_score(name, ctx, scoring_hints)

        section = ProposalSection(
            id=f"prop_{uuid4().hex[:12]}",
            project_id=project_id,
            section_name=name,
            content=_generate_section_content(name, ctx, scoring_hints, payload),
            score=section_score,
            is_confirmed=False,
            is_generated=True,
        )
        db.add(section)
        created.append(section)

    db.commit()
    return [ProposalSectionSummary.model_validate(s) for s in created]


def _compute_section_score(section_name: str, ctx: dict, scoring_hints: list[str]) -> int:
    """根据章节名称和评分提示计算章节得分"""
    base_score = 75  # 基础分

    # 结合评分规则调整
    rule_info = SCORING_RULES.get(section_name, {})
    criteria = rule_info.get("criteria", "")

    # 检查是否有相关的评分提示
    section_keywords = {
        "整体解决方案": ["整体", "方案", "解决"],
        "软件架构": ["架构", "软件"],
        "功能实现方案": ["功能", "实现"],
        "系统接口方案": ["接口", "系统"],
        "部署方案": ["部署"],
        "兼容性": ["兼容"],
        "系统安全": ["安全"],
        "项目经理能力": ["项目", "经理", "PMP"],
        "人员能力": ["人员", "资质", "认证"],
        "维保期限": ["维保", "维保期"],
    }

    keywords = section_keywords.get(section_name, [])
    bonus = 0
    for hint in scoring_hints:
        hint_lower = hint.lower()
        for kw in keywords:
            if kw in hint_lower:
                bonus += 3

    score = min(95, base_score + bonus)
    return int(score)


def _generate_section_content(
    section_name: str,
    ctx: dict,
    scoring_hints: list[str],
    payload: ProposalGenerationRequest,
) -> str:
    """生成章节内容，结合客户/公司背景和评分要求"""
    project_name = ctx.get("project_name", "待定项目")
    client = ctx.get("client", "目标客户")
    company = ctx.get("bidding_company", "亚信科技（中国）有限公司")

    scoring_hint_text = ""
    if payload.reference_scoring and scoring_hints:
        scoring_hint_text = "\n".join(f"- {h}" for h in scoring_hints[:5])

    templates = {
        "整体解决方案": f"""## 整体解决方案

### 一、项目概述
{payload.include_client_bg and f"本项目旨在为**{client}**提供全面的技术解决方案，满足其在信息化建设和数字化转型方面的迫切需求。" or "本项目旨在提供全面的技术解决方案。"}
项目名称：{project_name}
投标单位：{company}

### 二、需求分析
{f"结合客户背景分析，我公司认为本项目核心需求包括：" if payload.include_client_bg else "本项目核心需求包括："}
1. 系统需具备高可用性和可扩展性
2. 技术架构需满足未来3-5年业务发展需求
3. 安全合规性需满足国家及行业相关标准

### 三、解决方案概述
基于对招标文件的深入解读，结合{payload.include_company_bg and "我公司在行业内的丰富经验和技术积累" or "我们的技术积累"}，本方案从以下几个维度提供整体解决方案：

**1. 架构设计维度**
采用微服务架构，支持弹性扩展，满足高并发、高可用需求。

**2. 功能实现维度**
覆盖招标文件要求的核心功能点，并提供增值功能。

**3. 运维保障维度**
提供7×24小时技术支持，承诺{fpayload.include_company_bg and "公司具备完善的运维体系和专业的运维团队" or "专业的运维支持"}。

### 四、评分要点响应
{f"本章节响应技术打分表中的关键评分点：" if scoring_hint_text else "本章节完全响应招标文件中技术评分标准的要求。"}
{scoring_hint_text}
""",

        "软件架构": f"""## 软件架构

### 一、架构设计原则
1. **模块化设计**：采用高内聚、低耦合的模块化架构
2. **可扩展性**：支持水平扩展，满足业务增长需求
3. **可维护性**：代码结构清晰，便于后期维护和升级

### 二、技术架构选型
基于对{f"{client}的业务特点" if payload.include_client_bg else "项目需求"}的分析，本方案采用以下技术架构：
- **应用层**：Spring Boot / FastAPI 微服务框架
- **数据层**：PostgreSQL + Redis + MongoDB 混合存储
- **消息层**：Kafka / RabbitMQ 消息中间件
- **容器化**：Docker + Kubernetes 容器编排

### 三、系统拓扑结构
系统采用三层架构设计：
- **接入层**：负载均衡 + API 网关
- **业务层**：微服务集群，支持弹性扩缩容
- **数据层**：主从数据库 + 缓存集群

### 四、评分要点响应
{scoring_hint_text or "架构设计满足招标文件中关于系统架构的评分标准，具备先进性、可靠性和可扩展性。"}
""",

        "功能实现方案": f"""## 功能实现方案

### 一、核心功能模块
本方案提供以下核心功能模块，完整覆盖招标文件中技术规范书的要求：

| 功能模块 | 功能描述 | 技术实现 |
|---------|---------|---------|
| 用户管理 | 完整的用户 CRUD 操作 | RBAC 权限模型 |
| 业务处理 | 核心业务逻辑处理 | 事务管理 + 异步队列 |
| 数据分析 | 数据统计与报表 | ELK + 可视化 |
| 接口服务 | 标准化 API 接口 | RESTful + GraphQL |

### 二、关键技术实现
{f"结合{f'我公司在同类项目中的实施经验' if payload.include_company_bg else '项目需求'}，关键技术实现如下：" if payload.include_company_bg else "关键技术实现如下："}

1. **高并发处理**：采用分布式缓存 + 数据库读写分离，支持万级并发
2. **数据安全**：全链路 HTTPS + 数据加密存储 + 审计日志
3. **容灾备份**：异地多活部署 + 自动备份机制

### 三、评分要点响应
{scoring_hint_text or "功能实现方案完全响应招标文件中技术规范书的要求，覆盖所有关键功能点。"}
""",

        "系统接口方案": """## 系统接口方案

### 一、接口设计规范
本系统遵循以下接口设计规范：
- RESTful API 设计风格
- OpenAPI 3.0 接口文档
- JSON 数据交换格式
- 统一鉴权认证机制（OAuth 2.0 / JWT）

### 二、接口类型分类
| 接口类型 | 数量 | 说明 |
|---------|------|-----|
| 内部接口 | 50+ | 微服务间内部调用 |
| 外部 API | 20+ | 供第三方系统集成 |
| 消息接口 | 10+ | 与客户系统对接 |

### 三、接口安全措施
1. 传输层加密（HTTPS）
2. 接口鉴权（Token + 签名）
3. 流量控制（限流 + 熔断）
4. 日志审计（全链路追踪）

### 四、评分要点响应
接口方案满足招标文件中关于系统接口兼容性、安全性的评分要求。
""",

        "部署方案": """## 部署方案

### 一、部署架构
采用云原生部署架构，支持私有云、公有云、混合云部署：
- **容器化**：Docker 镜像统一封装
- **编排**：Kubernetes 自动调度
- **自动化**：CI/CD 流水线部署

### 二、部署策略
1. **蓝绿部署**：新版本与老版本并行，零中断切换
2. **滚动更新**：灰度发布，先更新部分节点
3. **回滚机制**：出现问题可快速回退到上一版本

### 三、运维保障
- 监控告警：Prometheus + Grafana
- 日志收集：ELK 统一日志平台
- 运维支持：7×24 小时专业运维团队
""",

        "兼容性": """## 兼容性

### 一、系统兼容性
本系统支持以下操作系统和平台：
- **服务器 OS**：CentOS 7+ / Ubuntu 20.04+ / Windows Server 2019+
- **数据库**：MySQL 8.0+ / PostgreSQL 12+ / Oracle 12c+
- **中间件**：Tomcat 9+ / WebLogic 12c+ / Nginx 1.18+

### 二、与客户系统兼容性
1. 支持对接客户现有的 Active Directory / LDAP 用户体系
2. 支持主流 ERP、CRM 系统数据对接
3. 支持移动端（iOS/Android）原生及 H5 混合开发

### 三、行业标准兼容性
- 符合国家信息安全等级保护要求
- 符合行业数据交换标准（HL7、FHIR 等）
""",

        "系统安全": """## 系统安全

### 一、安全体系架构
建立"预防-检测-响应"三位一体的安全体系：

| 安全层次 | 措施 | 说明 |
|---------|------|-----|
| 边界安全 | 防火墙 + WAF | 网络层防护 |
| 传输安全 | 全链路 HTTPS | 数据加密传输 |
| 存储安全 | AES-256 加密 | 数据静态加密 |
| 访问安全 | RBAC + MFA | 多因素认证 |

### 二、安全合规
1. 等保三级认证
2. ISO 27001 信息安全管理体系
3. 个人信息保护合规（GDPR/个保法）

### 三、应急响应
- 安全事件 4 小时响应
- 重要漏洞 24 小时修复
- 定期安全评估和渗透测试
""",

        "项目经理能力": f"""## 项目经理能力

### 一、项目经理简介
{f"本项目拟派项目经理为**张明**（PMP®认证，项目管理专业人士），具备15年以上大型信息化项目实施经验。" if payload.include_company_bg else "本项目拟派项目经理具备丰富的项目管理经验。"}

### 二、核心资质
- PMP®（项目管理专业人士）认证
- ITIL® v4 Foundation 认证
- 曾主导多个千万级信息化项目

### 三、类似项目经验
1. **某省政务云平台项目**：担任项目经理，项目金额3000万，已验收
2. **某市政府智慧城市项目**：担任技术总监，项目金额5000万
3. **某运营商 BSS 系统升级**：担任项目总监，项目金额2000万

### 四、评分要点响应
{scoring_hint_text or "项目经理配置完全满足招标文件中关于项目经理能力的评分要求。"}
""",

        "人员能力": """## 人员能力

### 一、团队配置
本项目核心团队配置如下：

| 角色 | 人数 | 资质要求 |
|------|------|---------|
| 项目经理 | 1 | PMP® 认证 |
| 技术架构师 | 2 | 高级工程师 |
| 开发工程师 | 8 | 5年以上经验 |
| 测试工程师 | 3 | ISTQB 认证 |
| 运维工程师 | 2 | RHCE 认证 |

### 二、团队资质
- CMMI 5 级认证团队
- 多个项目获得甲方嘉奖
- 核心技术骨干持有专利

### 三、培训机制
1. 入职培训（安全、合规）
2. 技能提升培训（季度）
3. 项目复盘总结（每月）
""",

        "维保期限": """## 维保期限

### 一、维保服务承诺
本项目提供以下维保服务：

| 服务类型 | 维保期 | 说明 |
|---------|--------|------|
| 缺陷修复 | 24个月 | 免费修复系统缺陷 |
| 安全更新 | 36个月 | 安全补丁更新 |
| 技术支持 | 24×7 | 7×24小时技术支持 |
| 版本升级 | 24个月 | 主流版本免费升级 |

### 二、维保期满服务
维保期满后，我公司提供以下延续服务：
- 年度维保服务（费用参照市场价）
- 定制化功能开发
- 驻场服务（按需）

### 三、服务响应机制
- 紧急问题（P0/P1）：2小时响应，4小时到场
- 一般问题（P2/P3）：8小时响应，24小时解决
- 常规咨询：48小时答复
""",
    }

    content = templates.get(section_name, f"## {section_name}\n\n内容待生成...")
    return content


def compute_score(
    db: Session,
    project_id: str,
    force: bool = False,
) -> tuple[list[ProposalSectionSummary], int]:
    """重新计算章节得分，支持强制重算（人工修改后再次打分）"""
    get_or_create_project(db, project_id)

    sections = (
        db.query(ProposalSection)
        .filter(ProposalSection.project_id == project_id, ProposalSection.is_generated == True)
        .order_by(ProposalSection.id)
        .all()
    )

    # 获取项目上下文用于评分
    ctx = _get_project_context(db, project_id)
    scoring_hints = ctx.get("scoring_hints", [])

    for section in sections:
        if force:
            # 强制重算：基于内容重新计算得分
            new_score = _recalculate_score(section.section_name, section.content, ctx, scoring_hints)
            section.score = new_score

    db.commit()

    summaries = [ProposalSectionSummary.model_validate(s) for s in sections]
    total = sum(s.score for s in summaries)
    return summaries, total


def _recalculate_score(section_name: str, content: str, ctx: dict, scoring_hints: list[str]) -> int:
    """根据内容质量重新计算得分"""
    base = 70
    bonus = 0

    # 检查内容丰富度
    lines = content.split("\n")
    if len(lines) > 20:
        bonus += 5
    if len(content) > 1500:
        bonus += 5

    # 检查是否包含评分关键词
    keywords_map = {
        "整体解决方案": ["需求分析", "架构设计", "解决方案"],
        "软件架构": ["微服务", "架构", "模块化"],
        "功能实现方案": ["功能", "模块", "实现"],
        "系统接口方案": ["API", "接口", "REST"],
        "部署方案": ["部署", "容器", "K8s"],
        "兼容性": ["兼容", "适配", "支持"],
        "系统安全": ["安全", "加密", "认证"],
        "项目经理能力": ["PMP", "项目经验", "认证"],
        "人员能力": ["资质", "认证", "团队"],
        "维保期限": ["维保", "响应", "服务"],
    }

    keywords = keywords_map.get(section_name, [])
    for kw in keywords:
        if kw in content:
            bonus += 3

    return min(95, base + bonus)


def confirm_all(db: Session, project_id: str) -> list[ProposalSectionSummary]:
    get_or_create_project(db, project_id)
    sections = (
        db.query(ProposalSection)
        .filter(ProposalSection.project_id == project_id, ProposalSection.is_generated == True)
        .all()
    )
    for s in sections:
        s.is_confirmed = True
    db.commit()
    return [ProposalSectionSummary.model_validate(s) for s in sections]