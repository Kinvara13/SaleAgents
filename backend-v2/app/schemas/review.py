from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.workspace import MetricItem


class ReviewJobCreateRequest(BaseModel):
    project_id: str | None = Field(default=None, max_length=64)
    contract_name: str = Field(min_length=1, max_length=255)
    contract_type: str = Field(default="采购合同", max_length=64)
    contract_text: str = Field(min_length=20)
    trigger: str = Field(default="manual", max_length=32)


class ReviewJobRerunRequest(BaseModel):
    contract_text: str | None = Field(default=None, min_length=20)
    contract_name: str | None = Field(default=None, max_length=255)
    contract_type: str | None = Field(default=None, max_length=64)


class ReviewIssueResolveRequest(BaseModel):
    status: str = Field(default="已处理", max_length=32)
    resolution_note: str = Field(default="", max_length=2000)


class ReviewFeedbackRequest(BaseModel):
    feedback_type: str = Field(max_length=32)
    feedback_note: str = Field(default="", max_length=2000)
    reviewer: str = Field(default="", max_length=64)


class ReviewFeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    issue_id: str
    job_id: str
    rule_name: str
    feedback_type: str
    feedback_note: str
    reviewer: str
    created_at: datetime


class RuleConfigCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=255)
    issue_type: str = Field(min_length=1, max_length=64)
    level: str = Field(min_length=1, max_length=16)
    detail: str = Field(min_length=1)
    suggestion: str = Field(min_length=1)
    patterns: str = Field(default="")
    document: str = Field(default="合同条款", max_length=255)
    match_mode: str = Field(default="any", max_length=16)
    is_enabled: bool = Field(default=True)
    priority: int = Field(default=100, ge=1, le=1000)
    category: str = Field(default="付款风险", max_length=64)
    description: str = Field(default="")


class RuleConfigUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    issue_type: str | None = Field(default=None, max_length=64)
    level: str | None = Field(default=None, max_length=16)
    detail: str | None = Field(default=None)
    suggestion: str | None = Field(default=None)
    patterns: str | None = Field(default=None)
    document: str | None = Field(default=None, max_length=255)
    match_mode: str | None = Field(default=None, max_length=16)
    is_enabled: bool | None = Field(default=None)
    priority: int | None = Field(default=None, ge=1, le=1000)
    category: str | None = Field(default=None, max_length=64)
    description: str | None = Field(default=None)


class RuleConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    title: str
    issue_type: str
    level: str
    detail: str
    suggestion: str
    patterns: str
    document: str
    match_mode: str
    is_enabled: bool
    priority: int
    category: str
    description: str
    created_at: datetime
    updated_at: datetime


class ReviewJobIssue(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    title: str
    type: str
    level: str
    status: str
    document: str
    detail: str
    evidence: str = ""
    suggestion: str = ""
    rule_name: str = ""
    resolution_note: str = ""


class ReviewJobClause(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    clause_no: int
    title: str = ""
    content: str
    source_ref: str = ""


class ReviewJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None = None
    contract_name: str
    contract_type: str
    trigger: str
    status: str
    overall_risk: str
    issue_count: int
    high_risk_issue_count: int
    summary: list[MetricItem]
    review_actions: list[str]
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class RuleStatisticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_name: str
    hit_count: int
    confirmed_count: int
    dismissed_count: int
    modified_count: int
    accuracy_rate: float
    last_feedback_at: datetime | None
