from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.proposal_plan import (
    ProposalPlanSummary,
    ProposalPlanDetail,
    ProposalPlanUpdateRequest,
)
from app.services import proposal_plan_service

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
    """更新方案建议书（支持人工修改）"""
    return proposal_plan_service.update_proposal_plan(db, project_id, doc_id, payload)
