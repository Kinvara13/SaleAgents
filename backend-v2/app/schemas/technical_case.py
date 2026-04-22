from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_serializer


def _serialize_datetime(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat() if isinstance(dt, datetime) else str(dt)


class TechnicalCaseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    primary_review_item: str
    secondary_review_item: str
    case_type: str
    scene_tags: str  # JSON string
    keywords: str    # JSON string
    summary: str
    contract_name: str
    contract_amount: str
    client_name: str
    score: str
    status: str
    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime) -> str:
        return _serialize_datetime(dt) or ""


class TechnicalCaseDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    primary_review_item: str
    secondary_review_item: str
    case_type: str
    scene_tags: str
    keywords: str
    summary: str
    contract_name: str
    contract_amount: str
    client_name: str
    contract_overview: str
    key_highlights: str
    content: str
    score: str
    status: str
    source: str
    video_url: str
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_dt(self, dt: datetime) -> str:
        return _serialize_datetime(dt) or ""


class TechnicalCaseCreateRequest(BaseModel):
    title: str
    primary_review_item: str = ""
    secondary_review_item: str = ""
    case_type: str = "项目案例"
    scene_tags: list[str] = []
    keywords: list[str] = []
    summary: str = ""
    contract_name: str = ""
    contract_amount: str = ""
    client_name: str = ""
    contract_overview: str = ""
    key_highlights: str = ""
    content: str = ""
    source: str = ""


class TechnicalCaseUpdateRequest(BaseModel):
    title: str | None = None
    primary_review_item: str | None = None
    secondary_review_item: str | None = None
    case_type: str | None = None
    scene_tags: list[str] | None = None
    keywords: list[str] | None = None
    summary: str | None = None
    contract_name: str | None = None
    contract_amount: str | None = None
    client_name: str | None = None
    contract_overview: str | None = None
    key_highlights: str | None = None
    content: str | None = None
    status: str | None = None
    source: str | None = None
    video_url: str | None = None