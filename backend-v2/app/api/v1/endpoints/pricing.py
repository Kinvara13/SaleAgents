from fastapi import APIRouter, Depends, status

from app.schemas.pricing import PricingCalculateRequest, PricingCalculateResponse
from app.services import pricing_service
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.auth import UserInfoResponse  # noqa: F401

router = APIRouter()


@router.post("/calculate", response_model=PricingCalculateResponse, status_code=status.HTTP_200_OK)
def calculate_pricing(
    payload: PricingCalculateRequest,
    current_user: UserInfoResponse = Depends(get_current_user),
) -> PricingCalculateResponse:
    """
    报价策略计算
    根据报价策略填写报价表，系统自动计算得分

    - 计算报价明细（不含税/含税价格、成本、折扣率）
    - 竞商报价模拟与排名
    - 价格得分、总评分计算
    - AI报价建议
    """
    return pricing_service.calculate_pricing(payload)
