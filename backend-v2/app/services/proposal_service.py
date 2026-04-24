from uuid import uuid4
import json

from sqlalchemy.orm import Session
from app.services.llm_client import llm_proposal_client

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


def generate_proposal_async(
    project_id: str,
    payload: ProposalGenerationRequest,
) -> None:
    """异步后台生成技术建议书章节（独立 Session）"""
    from app.db.session import SessionLocal
    from app.models.project import Project
    db = SessionLocal()
    try:
        result = generate_proposal(db, project_id, payload)
        # 更新项目状态
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            if isinstance(project.node_status, dict):
                project.node_status["generation"] = "completed"
            else:
                project.node_status = {"generation": "completed"}
            db.commit()
    except Exception as e:
        import logging
        logging.error(f"Async proposal generation failed for project {project_id}: {e}")
        db.rollback()
        # 更新失败状态
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            if isinstance(project.node_status, dict):
                project.node_status["generation"] = "failed"
            else:
                project.node_status = {"generation": "failed"}
            db.commit()
    finally:
        db.close()

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
        content = _generate_section_content(db, project_id, name, ctx, scoring_hints, payload)
        section_score = _recalculate_score(name, content, ctx, scoring_hints)

        section = ProposalSection(
            id=f"prop_{uuid4().hex[:12]}",
            project_id=project_id,
            section_name=name,
            content=content,
            score=section_score,
            is_confirmed=False,
            is_generated=True,
        )
        db.add(section)
        created.append(section)

    db.commit()
    return [ProposalSectionSummary.model_validate(s) for s in created]


def _compute_section_score(section_name: str, ctx: dict, scoring_hints: list[str]) -> int:
    """Legacy keyword-based scorer; kept for reference but no longer used in generation."""
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
    db: Session,
    project_id: str,
    section_name: str,
    ctx: dict,
    scoring_hints: list[str],
    payload: ProposalGenerationRequest,
) -> str:
    """生成章节内容，结合客户/公司背景、素材库、技术案例和评分要求，真实调用 LLM"""

    # 准备传给 LLM 的上下文
    llm_context = {
        "project_name": ctx.get("project_name", "待定项目"),
        "client": ctx.get("client", "目标客户"),
        "bidding_company": ctx.get("bidding_company", "亚信科技（中国）有限公司"),
        "deadline": ctx.get("deadline", ""),
        "amount": ctx.get("amount", "")
    }

    # Gather real project & tender info for asset routing
    from app.models.tender import Tender
    tender = db.query(Tender).filter(Tender.project_id == project_id).first()

    from app.models.parsing_section import ParsingSection
    parsing_sections = db.query(ParsingSection).filter(ParsingSection.project_id == project_id).all()
    tender_requirements = "\n\n".join([
        f"[{s.section_name}]\n{s.content[:500]}"
        for s in parsing_sections if s.content
    ]) if parsing_sections else ""

    project_summary = f"项目名称: {ctx.get('project_name', '')}\n"
    if ctx.get("client"):
        project_summary += f"招标人: {ctx['client']}\n"
    if ctx.get("amount"):
        project_summary += f"投标金额: {ctx['amount']}\n"
    if ctx.get("deadline"):
        project_summary += f"截止日期: {ctx['deadline']}\n"
    if ctx.get("bidding_company"):
        project_summary += f"投标公司: {ctx['bidding_company']}\n"

    delivery_deadline = ctx.get("deadline", "")
    service_commitment = tender.service_commitment if tender else ""

    from app.services.workspace_service import get_extracted_fields
    extracted_fields = {item.label: item.value for item in get_extracted_fields(db)}

    # 调用素材路由服务获取相关素材
    from app.services.asset_routing_service import asset_routing_service
    routed_assets = asset_routing_service.route_assets_for_section(
        db,
        section_title=section_name,
        project_summary=project_summary,
        tender_requirements=tender_requirements,
        delivery_deadline=delivery_deadline,
        service_commitment=service_commitment,
        selected_asset_titles=[],
        fixed_asset_titles=[],
        excluded_asset_titles=[],
        extracted_fields=extracted_fields,
        limit=3,
    )
    routed_asset_payloads = [
        f"{item.asset_title}�{item.chunk_title}�{item.snippet}"
        for item in routed_assets
    ]

    # 调用技术案例服务获取相关案例
    from app.services.technical_case_service import search_technical_cases
    cases = search_technical_cases(db, project_id, keyword=section_name)
    case_payloads = [
        f"案例名称：{case.title}�合同：{case.contract_name}�摘要：{case.summary}"
        for case in cases[:3]
    ]

    # 筛选相关提示词
    filtered_hints = scoring_hints
    if not payload.reference_scoring:
        filtered_hints = []

    # 调用大模型生成章节
    content = llm_proposal_client.generate_section(
        section_name=section_name,
        context=llm_context,
        scoring_hints=filtered_hints,
        routed_assets=routed_asset_payloads,
        technical_cases=case_payloads,
    )

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
        elif section.score == 0:
            # 首次评分：对尚未打分的章节进行语义化预打分
            new_score = _recalculate_score(section.section_name, section.content, ctx, scoring_hints)
            section.score = new_score

    db.commit()

    summaries = [ProposalSectionSummary.model_validate(s) for s in sections]
    total = sum(s.score for s in summaries)
    return summaries, total


def _recalculate_score(section_name: str, content: str, ctx: dict, scoring_hints: list[str]) -> int:
    """根据内容质量重新计算得分，调用 LLM 进行语义打分"""
    rule_info = SCORING_RULES.get(section_name, {})
    max_score = rule_info.get("max", 100)
    
    score = llm_proposal_client.score_section(
        section_name=section_name,
        content=content,
        scoring_hints=scoring_hints,
        max_score=max_score
    )
    return score


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