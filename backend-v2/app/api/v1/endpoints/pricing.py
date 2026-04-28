from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.pricing import PricingCalculateRequest, PricingCalculateResponse
from app.services import pricing_service
from app.services.pricing_persistence import save_pricing_calculation
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.auth import UserInfoResponse

router = APIRouter()


@router.post("/calculate", response_model=PricingCalculateResponse, status_code=status.HTTP_200_OK)
def calculate_pricing(
    payload: PricingCalculateRequest,
    current_user: UserInfoResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PricingCalculateResponse:
    result = pricing_service.calculate_pricing(payload)
    try:
        competitors_data = [c.model_dump() for c in payload.competitors] if payload.competitors else []
        save_pricing_calculation(
            db=db,
            project_id=payload.project_id or "",
            response=result,
            competitors=competitors_data,
            user_id=current_user.id if hasattr(current_user, "id") else "user-001",
        )
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Failed to persist pricing calculation: %s", exc)
    return result
