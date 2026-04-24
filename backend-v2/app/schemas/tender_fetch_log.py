from datetime import datetime

from pydantic import BaseModel


class TenderFetchLogItem(BaseModel):
    id: int
    task_name: str
    source: str
    status: str
    new_count: int
    updated_count: int
    error_message: str
    started_at: datetime
    ended_at: datetime | None

    model_config = {"from_attributes": True}


class TenderFetchLogList(BaseModel):
    total: int
    items: list[TenderFetchLogItem]
