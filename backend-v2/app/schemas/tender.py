from datetime import datetime

from pydantic import BaseModel, field_validator


class TenderCreateRequest(BaseModel):
    title: str = ""
    source_url: str = ""
    publish_date: str = ""
    deadline: str = ""
    amount: str = ""
    margin: str = ""
    project_type: str = ""
    description: str = ""


class TenderDecisionRequest(BaseModel):
    decision: str  # "bid" | "reject"
    reason: str = ""
    margin: str = ""
    project_type: str = ""


class TenderSummary(BaseModel):
    id: str
    title: str
    source_url: str
    publish_date: str
    deadline: str
    amount: str
    margin: str | None = None
    project_type: str
    description: str
    decision: str
    reject_reason: str
    project_id: str
    service_commitment: str | None = None
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator('margin', mode='before')
    @classmethod
    def convert_margin_to_str(cls, v):
        if v is None:
            return ""
        return str(v)

    @field_validator('service_commitment', mode='before')
    @classmethod
    def convert_service_commitment_to_str(cls, v):
        if v is None:
            return ""
        return str(v)
