from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.proposal_plan import (
    ProposalPlanSummary,
    ProposalPlanDetail,
    ProposalPlanUpdateRequest,
    DocumentScoreResponse,
)
from app.services import proposal_plan_service
from app.services.scoring_service import calculate_score

router = APIRouter()


@router.get("/{project_id}/proposal-plans", response_model=list[ProposalPlanSummary])
def list_proposal_plans(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[ProposalPlanSummary]:
    """获取项目的方案建议书清单（6.1-6.4）"""
    return proposal_plan_service.list_proposal_plans(db, project_id)


@router.get("/{project_id}/proposal-plans/{doc_id}", response_model=ProposalPlanDetail)
def get_proposal_plan_detail(
    project_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
) -> ProposalPlanDetail:
    """获取方案建议书详情（含可编辑内容）"""
    return proposal_plan_service.get_proposal_plan_detail(db, project_id, doc_id)


@router.patch("/{project_id}/proposal-plans/{doc_id}", response_model=ProposalPlanDetail)
def update_proposal_plan(
    project_id: str,
    doc_id: str,
    payload: ProposalPlanUpdateRequest,
    db: Session = Depends(get_db),
) -> ProposalPlanDetail:
    """更新方案建议书文档（支持人工修改）"""
    return proposal_plan_service.update_proposal_plan(db, project_id, doc_id, payload)


@router.post("/{project_id}/proposal-plans/{doc_id}/generate", response_model=ProposalPlanDetail)
def generate_proposal_plan(
    project_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
) -> ProposalPlanDetail:
    """AI自动生成并填充方案建议书内容"""
    return proposal_plan_service.generate_proposal_plan(db, project_id, doc_id)


@router.get("/{project_id}/proposal-plans/{doc_id}/score", response_model=DocumentScoreResponse)
def score_proposal_plan(
    project_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
) -> DocumentScoreResponse:
    """计算方案建议书评分"""
    return DocumentScoreResponse(**calculate_score(db, project_id, doc_id, doc_kind="proposal"))
