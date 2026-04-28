from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.competitor_intel import (
    CompetitorIntelPredictRequest,
    CompetitorIntelPredictResponse,
)
from app.services import competitor_intelligence
from app.services.pricing_persistence import save_competitor_prediction
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.auth import UserInfoResponse

router = APIRouter()


@router.post("/predict", response_model=CompetitorIntelPredictResponse, status_code=status.HTTP_200_OK)
def predict_competitor_intel(
    payload: CompetitorIntelPredictRequest,
    current_user: UserInfoResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CompetitorIntelPredictResponse:
    result = competitor_intelligence.predict_competitor_intel(payload)
    try:
        save_competitor_prediction(
            db=db,
            project_id="",
            input_competitors=[c.model_dump() for c in payload.competitors],
            response=result,
            user_id=current_user.id if hasattr(current_user, "id") else "user-001",
        )
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Failed to persist competitor prediction: %s", exc)
    return result
