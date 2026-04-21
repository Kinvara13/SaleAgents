from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PreEvaluationJobListItem(BaseModel):
    id: str
    file_name: str
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class PreEvaluationJobResponse(BaseModel):
    id: str
    project_id: str | None = None
    file_name: str
    status: str
    source_text: str = ""
    review_method: dict | list = Field(default_factory=dict)
    tech_review_table: list[dict] = Field(default_factory=list)
    starred_items: list[dict] = Field(default_factory=list)
    summary: str = ""
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True
