from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.workspace import RuleHit, ScoreCard
from app.services.workspace_service import get_ai_reasons, get_rule_hits, get_score_cards
from app.schemas.decision import ProjectDecisionJobResponse
from app.modules.decision.service import decision_service

router = APIRouter()


@router.post("/projects/{project_id}/run", response_model=ProjectDecisionJobResponse)
def run_decision_for_project(project_id: str, db: Session = Depends(get_db)) -> ProjectDecisionJobResponse:
    """Run the decision analysis for a given project."""
    try:
        job = decision_service.run_decision_job(db, project_id=project_id)
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/latest", response_model=ProjectDecisionJobResponse)
def get_latest_decision_job(project_id: str, db: Session = Depends(get_db)) -> ProjectDecisionJobResponse:
    """Get the latest decision job for a given project."""
    job = decision_service.get_latest_job(db, project_id=project_id)
    if not job:
        raise HTTPException(status_code=404, detail="No decision job found for this project")
    return job


@router.get("/scores", response_model=list[ScoreCard])
def list_decision_scores(db: Session = Depends(get_db)) -> list[ScoreCard]:
    return get_score_cards(db)


@router.get("/rules", response_model=list[RuleHit])
def list_rule_hits(db: Session = Depends(get_db)) -> list[RuleHit]:
    return get_rule_hits(db)


@router.get("/reasons", response_model=list[str])
def list_ai_reasons(db: Session = Depends(get_db)) -> list[str]:
    return get_ai_reasons(db)
