from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.workspace_panel import WorkspacePanel
from app.schemas.project import ProjectCreateRequest, ProjectSummary, ProjectUpdateRequest
from app.schemas.workspace import (
    ExtractedField,
    GenerationSection,
    KnowledgeAsset,
    MetricItem,
    ModuleCard,
    NavItem,
    ParseSection,
    ReviewIssue,
    RuleHit,
    ScoreCard,
    WorkspaceData,
)
from app.services.mock_workspace import build_default_projects, build_default_workspace
from app.services.asset_index_service import asset_index_service

WORKSPACE_PANEL_KEYS = [
    "nav_items",
    "overview_metrics",
    "modules",
    "project_stats",
    "project_filters",
    "parse_sections",
    "extracted_fields",
    "score_cards",
    "rule_hits",
    "ai_reasons",
    "pending_checks",
    "generation_sections",
    "generation_assets",
    "generation_todos",
    "review_summary",
    "review_issues",
    "review_actions",
]


def initialize_database(db: Session) -> None:
    if db.scalar(select(Project.id).limit(1)) is None:
        for item in build_default_projects():
            db.add(
                Project(
                    id=item.id,
                    name=item.name,
                    status=item.status,
                    owner=item.owner,
                    client=item.client,
                    deadline=item.deadline,
                    amount=item.amount,
                    risk=item.risk,
                    node_status={
                        "decision": "pending",
                        "parsing": "pending",
                        "generation": "pending",
                        "review": "pending",
                    },
                )
            )

    existing_keys = set(db.scalars(select(WorkspacePanel.key)).all())
    # Seed empty workspace panels if they don't exist
    for key in WORKSPACE_PANEL_KEYS:
        if key not in existing_keys:
            db.add(WorkspacePanel(key=key, payload=[]))

    # Migrate LLM providers if json config exists
    from pathlib import Path
    import json
    from app.models.settings import AIConfig
    
    config_file = Path(__file__).resolve().parents[3] / "llm_providers.json"
    if config_file.exists() and db.query(AIConfig).count() == 0:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                active_id = data.get("active_provider_id")
                for p in data.get("providers", []):
                    db.add(AIConfig(
                        id=p.get("id"),
                        name=p.get("name"),
                        base_url=p.get("base_url"),
                        api_key=p.get("api_key"),
                        model=p.get("model"),
                        provider=p.get("protocol", "openai"),
                        is_active=(p.get("id") == active_id)
                    ))
            import os
            os.remove(config_file)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to migrate llm_providers.json: {e}")

    db.commit()
    asset_index_service.initialize_seed_assets(db)


def list_projects(db: Session) -> list[ProjectSummary]:
    rows = db.scalars(select(Project).order_by(Project.created_at.asc())).all()
    return [_to_project_summary(row) for row in rows]


def get_project(db: Session, project_id: str) -> ProjectSummary:
    row = db.get(Project, project_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return _to_project_summary(row)


def update_project(db: Session, project_id: str, payload: "ProjectUpdateRequest") -> ProjectSummary:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if payload.status is not None:
        project.status = payload.status
        
    db.commit()
    db.refresh(project)
    return _to_project_summary(project)


def create_project(db: Session, payload: ProjectCreateRequest) -> ProjectSummary:
    project = Project(
        id=f"project-{uuid4().hex[:8]}",
        name=payload.name.strip(),
        status=payload.status.strip() or "待决策",
        owner=payload.owner.strip(),
        client=payload.client.strip(),
        deadline=payload.deadline.strip(),
        amount=payload.amount.strip(),
        risk=payload.risk.strip().upper() or "P2",
        module_progress={
            "decision": "pending",
            "generation": "pending",
            "review": "pending",
        },
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _to_project_summary(project)


def _panel_payload(db: Session, key: str):
    panel = db.get(WorkspacePanel, key)
    return panel.payload if panel else []


def _to_project_summary(row: Project) -> ProjectSummary:
    return ProjectSummary(
        id=row.id,
        name=row.name,
        status=row.status,
        owner=row.owner,
        client=row.client,
        deadline=row.deadline,
        amount=row.amount,
        risk=row.risk,
        bidding_company=row.bidding_company,
        agent_name=row.agent_name,
        agent_phone=row.agent_phone,
        agent_email=row.agent_email,
        company_address=row.company_address,
        bank_name=row.bank_name,
        bank_account=row.bank_account,
        confirm_status=row.confirm_status,
        confirm_feedback=row.confirm_feedback,
        confirmed_by=row.confirmed_by,
        confirmed_at=row.confirmed_at,
        user_id=row.user_id,
        tender_id=row.tender_id,
        parse_status=row.parse_status,
        file_list=row.file_list if row.file_list else [],
        node_status=row.node_status if row.node_status else {},
        extracted_fields=row.extracted_fields if row.extracted_fields else [],
    )


def get_parse_sections(db: Session) -> list[ParseSection]:
    """基于最近解析的项目动态构建章节列表"""
    from app.models.parsing_section import ParsingSection
    sections = db.query(ParsingSection).order_by(ParsingSection.created_at.desc()).limit(20).all()
    return [
        ParseSection(
            title=s.section_name,
            page="-",
            state="已解析" if s.content and len(s.content) > 20 else "待填充",
            source_text=s.content[:200] if s.content else "",
            source_file=s.source_file or "",
        )
        for s in sections
    ]


def get_extracted_fields(db: Session) -> list[ExtractedField]:
    """基于最近解析项目的 extracted_fields 动态构建"""
    from app.models.project import Project
    projects = db.query(Project).filter(Project.extracted_fields != []).order_by(Project.updated_at.desc()).limit(5).all()
    fields = []
    for p in projects:
        for f in (p.extracted_fields or []):
            if isinstance(f, dict):
                fields.append(ExtractedField(
                    label=f.get("label", "未知字段"),
                    value=str(f.get("value", "")),
                    confidence=f.get("confidence", "80%"),
                ))
    return fields[:10]


def get_score_cards(db: Session) -> list[ScoreCard]:
    """基于规则库动态构建评分卡片"""
    from app.models.settings import Rule
    rules = db.query(Rule).filter(Rule.is_active == True).limit(10).all()
    return [
        ScoreCard(label=r.name, score=r.score or 0, note=r.description or "")
        for r in rules
    ]


def get_rule_hits(db: Session) -> list[RuleHit]:
    """基于规则库动态构建规则命中"""
    from app.models.settings import Rule
    rules = db.query(Rule).filter(Rule.is_active == True).limit(10).all()
    return [
        RuleHit(name=r.name, result="已配置", detail=r.description or "", level="info")
        for r in rules
    ]


def get_ai_reasons(db: Session) -> list[str]:
    """基于项目状态动态构建 AI 分析理由"""
    from app.models.project import Project
    reasons = []
    recent = db.query(Project).order_by(Project.updated_at.desc()).limit(3).all()
    for p in recent:
        if p.parse_status == "已解析":
            reasons.append(f"项目 {p.name} 已完成标书解析，共提取 {(p.extracted_fields or []).__len__()} 个关键字段")
        elif p.parse_status == "解析中":
            reasons.append(f"项目 {p.name} 正在解析中...")
    return reasons or ["暂无最近的 AI 分析记录"]


def get_generation_sections(db: Session) -> list[GenerationSection]:
    """基于商务/技术文档生成状态动态构建"""
    from app.models.business_document import BusinessDocument
    from app.models.technical_document import TechnicalDocument
    biz = db.query(BusinessDocument).limit(10).all()
    tech = db.query(TechnicalDocument).limit(10).all()
    sections = []
    for d in biz:
        sections.append(GenerationSection(
            title=d.doc_name,
            status=d.status,
            citations=0,
            todo=1 if d.status in ["待填充", "待生成"] else 0,
        ))
    for d in tech:
        sections.append(GenerationSection(
            title=d.doc_name,
            status=d.status,
            citations=0,
            todo=1 if d.status in ["待填充", "待生成"] else 0,
        ))
    return sections[:20]


def get_generation_assets(db: Session) -> list[KnowledgeAsset]:
    """基于素材库动态构建"""
    from app.models.settings import Material
    mats = db.query(Material).filter(Material.is_active == True).limit(10).all()
    return [
        KnowledgeAsset(title=m.name, type=m.category or "通用", score="90", status="可用")
        for m in mats
    ]


def get_generation_todos(db: Session) -> list[str]:
    """基于文档状态动态构建待办事项"""
    from app.models.business_document import BusinessDocument
    from app.models.technical_document import TechnicalDocument
    todos = []
    biz_pending = db.query(BusinessDocument).filter(BusinessDocument.status.in_(["待填充", "待生成"])).count()
    tech_pending = db.query(TechnicalDocument).filter(TechnicalDocument.status.in_(["待填充", "待生成"])).count()
    if biz_pending > 0:
        todos.append(f"商务文档待生成: {biz_pending} 份")
    if tech_pending > 0:
        todos.append(f"技术文档待生成: {tech_pending} 份")
    return todos or ["暂无待办事项"]


def get_review_summary(db: Session) -> list[MetricItem]:
    """基于审查问题数量动态构建"""
    from app.models.business_document import BusinessDocument
    from app.models.technical_document import TechnicalDocument
    biz_total = db.query(BusinessDocument).count()
    tech_total = db.query(TechnicalDocument).count()
    biz_done = db.query(BusinessDocument).filter(BusinessDocument.status == "已完成").count()
    tech_done = db.query(TechnicalDocument).filter(TechnicalDocument.status == "已完成").count()
    return [
        MetricItem(label="商务文档", value=f"{biz_done}/{biz_total}", hint="完成度", tone="good" if biz_done == biz_total else "warning"),
        MetricItem(label="技术文档", value=f"{tech_done}/{tech_total}", hint="完成度", tone="good" if tech_done == tech_total else "warning"),
    ]


def get_review_issues(db: Session) -> list[ReviewIssue]:
    """基于规则库动态构建审查问题"""
    from app.models.settings import Rule
    rules = db.query(Rule).filter(Rule.is_active == True, Rule.is_mandatory == True).limit(10).all()
    return [
        ReviewIssue(
            title=r.name,
            type="rule",
            level="high" if r.is_mandatory else "medium",
            status="待检查",
            document="全局",
            detail=r.description or "",
        )
        for r in rules
    ]


def get_review_actions(db: Session) -> list[str]:
    return ["执行完整审查流程", "导出审查报告"]


def get_workspace_data(db: Session) -> WorkspaceData:
    return WorkspaceData(
        nav_items=[NavItem(**item) for item in _panel_payload(db, "nav_items")],
        overview_metrics=[MetricItem(**item) for item in _panel_payload(db, "overview_metrics")],
        modules=[ModuleCard(**item) for item in _panel_payload(db, "modules")],
        project_stats=[MetricItem(**item) for item in _panel_payload(db, "project_stats")],
        project_filters=list(_panel_payload(db, "project_filters")),
        project_rows=list_projects(db),
        parse_sections=get_parse_sections(db),
        extracted_fields=get_extracted_fields(db),
        score_cards=get_score_cards(db),
        rule_hits=get_rule_hits(db),
        ai_reasons=get_ai_reasons(db),
        pending_checks=list(_panel_payload(db, "pending_checks")),
        generation_sections=get_generation_sections(db),
        generation_assets=get_generation_assets(db),
        generation_todos=get_generation_todos(db),
        review_summary=get_review_summary(db),
        review_issues=get_review_issues(db),
        review_actions=get_review_actions(db),
    )
