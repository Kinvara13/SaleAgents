from pydantic import BaseModel, Field
from typing import Optional


class CompetitorPredictInput(BaseModel):
    name: str
    industry: str = ""
    region: str = ""
    size: str = ""
    historical_discount: Optional[float] = None


class CompetitorIntelPredictRequest(BaseModel):
    project_id: Optional[str] = None
    budget: float = Field(ge=0, default=0)
    project_type: str = ""
    competitors: list[CompetitorPredictInput] = []


class DiscountDistribution(BaseModel):
    p10: float
    p50: float
    p90: float
    distribution_type: str = "beta"
    alpha: float = 0.0
    beta_param: float = 0.0


class EvidenceItem(BaseModel):
    source: str
    reliability: str = "C"
    date: str = ""
    detail: str = ""


class AccompliceAlert(BaseModel):
    risk_level: str = Field(default="low", description="high / medium / low")
    reasons: list[str] = []
    related_companies: list[str] = []
    anomaly_score: float = Field(ge=0, le=1, default=0.0)


class CompetitorPrediction(BaseModel):
    name: str
    point_estimate: float
    distribution: DiscountDistribution
    confidence: float = Field(ge=0, le=1, default=0.5)
    evidence: list[EvidenceItem] = []
    accomplice_probability: float = Field(ge=0, le=1, default=0.0)
    accomplice_alert: Optional[AccompliceAlert] = None
    market_position: str = "balanced"


class CompetitorIntelPredictResponse(BaseModel):
    predictions: list[CompetitorPrediction] = []
    accomplice_groups: list[list[str]] = []
