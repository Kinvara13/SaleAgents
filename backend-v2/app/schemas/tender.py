from datetime import datetime

from pydantic import BaseModel


class TenderCreateRequest(BaseModel):
    title: str = ""
    source_url: str = ""
    publish_date: str = ""
    deadline: str = ""
    amount: str = ""
    project_type: str = ""
    description: str = ""


class TenderDecisionRequest(BaseModel):
    decision: str  # "bid" | "reject"
    reason: str = ""


class TenderSummary(BaseModel):
    id: str
    title: str
    source_url: str
    publish_date: str
    deadline: str
    amount: str
    project_type: str
    description: str
    decision: str
    reject_reason: str
    project_id: str
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
