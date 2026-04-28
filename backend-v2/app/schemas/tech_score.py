from pydantic import BaseModel, Field
from typing import Optional


class SubjectiveTier(BaseModel):
    tier: int = Field(ge=1, le=4, description="1=best, 4=worst")
    min_score: float
    max_score: float
    description: str = ""


class SubjectiveItem(BaseModel):
    name: str
    max_score: float
    tiers: list[SubjectiveTier] = []


class ObjectiveItem(BaseModel):
    name: str
    max_score: float
    weight: float = 1.0


class ScoringCriteria(BaseModel):
    objective_items: list[ObjectiveItem] = []
    subjective_items: list[SubjectiveItem] = []


class CompanyMaterials(BaseModel):
    qualifications: list[str] = []
    cases: list[str] = []
    proposal_text: str = ""
    technical_params: list[str] = []


class TechScoreEvaluateRequest(BaseModel):
    project_id: Optional[str] = None
    scoring_criteria: ScoringCriteria
    company_materials: CompanyMaterials
    tech_weight: float = Field(ge=0, le=1, default=0.5)
    manual_objective_score: Optional[float] = None


class ObjectiveScoreItem(BaseModel):
    name: str
    score: float
    max_score: float
    matched: bool = False
    detail: str = ""
    ai_verified: bool = False
    ai_verification_detail: str = ""
    missing_items: list[str] = []


class ObjectiveScoreResult(BaseModel):
    total: float
    items: list[ObjectiveScoreItem] = []
    confidence: float = Field(ge=0, le=1, default=1.0)


class SubjectiveScoreItem(BaseModel):
    name: str
    ai_tier: int
    ai_score: float
    max_score: float
    confidence: float = Field(ge=0, le=1)
    reasoning: str = ""
    references: list[str] = []


class SubjectiveScoreResult(BaseModel):
    items: list[SubjectiveScoreItem] = []
    total: float


class TechScoreEvaluateResponse(BaseModel):
    objective_score: ObjectiveScoreResult
    subjective_score: SubjectiveScoreResult
    total_tech_score: float
    confidence_range: list[float] = Field(min_length=2, max_length=2)
    needs_manual_review: bool = True
