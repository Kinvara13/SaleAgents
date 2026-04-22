from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class CompetitorInput(BaseModel):
    name: str
    discount_rate: float = Field(ge=0, le=100)


class PricingCalculateRequest(BaseModel):
    project_id: Optional[str] = None
    budget: float = Field(ge=0, default=0)
    ex_tax_price: Optional[float] = None
    inc_tax_price: Optional[float] = None
    tax_rate: float = Field(ge=0, le=1, default=0.06)
    profit_margin: float = Field(ge=0, default=15)
    risk_factor: int = Field(ge=1, le=5, default=3)
    pricing_method: str = Field(default="linear")
    k_value: float = Field(ge=0, le=100, default=95)
    sensitivity: float = Field(ge=0, default=2)
    effective_bidder_count: int = Field(ge=1, default=5)
    tech_score: float = Field(ge=0, le=100, default=75)
    competitors: list[CompetitorInput] = Field(default_factory=list)


class PricingBreakdown(BaseModel):
    ex_tax_price: float
    inc_tax_price: float
    ex_tax_cost: float
    inc_tax_cost: float
    discount_rate: float
    profit_margin: float
    tax_rate: float


class CompetitorResult(BaseModel):
    id: str
    name: str
    is_our: bool
    quote_price: float
    discount_rate: float
    price_score: float
    rank: int


class PricingScores(BaseModel):
    price_competitiveness: float
    profit_reasonability: float
    risk_controllability: float


class PricingCalculateResponse(BaseModel):
    success: bool = True
    message: str = ""
    breakdown: PricingBreakdown
    competitors: list[CompetitorResult]
    our_rank: int
    our_price_score: float
    benchmark_price: float
    min_review_price: float
    total_score: float
    scores: PricingScores
    ai_advice: str
