from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.proposal import (
    ProposalSectionSummary,
    ProposalSectionDetail,
    ProposalSectionUpdateRequest,
    ProposalScoreResponse,
    ProposalGenerationRequest,
    SCORING_RULES,
)
from app.services import proposal_service

router = APIRouter()


@router.post("/{project_id}/generate")
def generate_proposal(
    project_id: str,
    background_tasks: BackgroundTasks,
    payload: ProposalGenerationRequest | None = None,
    db: Session = Depends(get_db),
) -> dict:
    """触发异步生成任务"""
    if payload is None:
        payload = ProposalGenerationRequest()
    background_tasks.add_task(proposal_service.generate_proposal_async, db, project_id, payload)
    return {"status": "processing", "message": "生成任务已在后台启动"}


@router.get("/{project_id}/sections", response_model=list[ProposalSectionSummary])
def get_sections(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[ProposalSectionSummary]:
    return proposal_service.list_sections(db, project_id)


@router.get("/{project_id}/sections/{section_id}", response_model=ProposalSectionDetail)
def get_section_detail(
    project_id: str,
    section_id: str,
    db: Session = Depends(get_db),
) -> ProposalSectionDetail:
    return proposal_service.get_section_detail(db, project_id, section_id)


@router.patch("/{project_id}/sections/{section_id}", response_model=ProposalSectionDetail)
def patch_section(
    project_id: str,
    section_id: str,
    payload: ProposalSectionUpdateRequest,
    db: Session = Depends(get_db),
) -> ProposalSectionDetail:
    return proposal_service.update_section(db, project_id, section_id, payload)


@router.post("/{project_id}/score", response_model=ProposalScoreResponse)
def score_proposal(
    project_id: str,
    db: Session = Depends(get_db),
) -> ProposalScoreResponse:
    sections, total = proposal_service.compute_score(db, project_id)
    return ProposalScoreResponse(sections=sections, total_score=total)


@router.post("/{project_id}/rescore", response_model=ProposalScoreResponse)
def rescore_proposal(
    project_id: str,
    db: Session = Depends(get_db),
) -> ProposalScoreResponse:
    """人工修改后的再次打分"""
    sections, total = proposal_service.compute_score(db, project_id, force=True)
    return ProposalScoreResponse(sections=sections, total_score=total)


@router.post("/{project_id}/confirm", response_model=list[ProposalSectionSummary])
def confirm_proposal(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[ProposalSectionSummary]:
    return proposal_service.confirm_all(db, project_id)


@router.get("/{project_id}/scoring-rules")
def get_scoring_rules(project_id: str, db: Session = Depends(get_db)):
    """获取技术建议书评分规则（对应技术打分表）"""
    # 从项目关联的 technical_documents 获取评分相关配置
    rules = []
    for section_name, rule_info in SCORING_RULES.items():
        rules.append({
            "section_name": section_name,
            "max_score": rule_info["max"],
            "weight": rule_info["weight"],
            "criteria": rule_info["criteria"],
        })
    return {"total_max": 100, "sections": rules}