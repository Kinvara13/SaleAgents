from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.tech_score import TechScoreEvaluateRequest, TechScoreEvaluateResponse
from app.services import tech_score_evaluator
from app.services.pricing_persistence import save_tech_score_evaluation
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.auth import UserInfoResponse

router = APIRouter()


@router.post("/evaluate", response_model=TechScoreEvaluateResponse, status_code=status.HTTP_200_OK)
def evaluate_tech_score(
    payload: TechScoreEvaluateRequest,
    current_user: UserInfoResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TechScoreEvaluateResponse:
    result = tech_score_evaluator.evaluate_tech_score(payload)
    try:
        save_tech_score_evaluation(
            db=db,
            project_id=payload.project_id or "",
            request_data=payload.model_dump(),
            response=result,
            user_id=current_user.id if hasattr(current_user, "id") else "user-001",
        )
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Failed to persist tech score evaluation: %s", exc)
    return result
