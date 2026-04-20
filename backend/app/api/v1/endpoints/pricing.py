# sale-agents-v2: pricing module (skeleton)
# TODO: implement business logic
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()


@router.post("/calculate", status_code=status.HTTP_200_OK)
def calculate_pricing(db: Session = Depends(get_db)) -> dict:
    """
    计算报价策略。

    Request body (TBD):
        project_id, cost_items, markup_rate, etc.

    Response (TBD):
        total_price, breakdown, recommendations
    """
    # TODO: implement pricing calculation logic
    raise NotImplementedError("pricing calculation not yet implemented")
