from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewFeedbackCreate(BaseModel):
    issue_id: str = Field(min_length=1, max_length=64)
    job_id: str = Field(min_length=1, max_length=64)
    rule_name: str = Field(default="", max_length=128)
    feedback_type: str = Field(min_length=1, max_length=32)
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


class RuleStatisticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rule_name: str
    hit_count: int
    confirmed_count: int
    dismissed_count: int
    modified_count: int
    accuracy_rate: float
    last_feedback_at: datetime | None
