from datetime import datetime
from pydantic import BaseModel, Field

class ScoreDimension(BaseModel):
    label: str
    score: int
    note: str

class DecisionScore(BaseModel):
    total: int
    dimensions: list[ScoreDimension]

class DecisionRuleHit(BaseModel):
    name: str
    level: str
    result: str
    detail: str

class ProjectDecisionJobResponse(BaseModel):
    id: str
    project_id: str
    status: str
    score: DecisionScore | None = None
    rule_hits: list[DecisionRuleHit] | None = None
    ai_reasons: list[str] | None = None
    pending_checks: list[str] | None = None
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True

