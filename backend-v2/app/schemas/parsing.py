from pydantic import BaseModel, ConfigDict, Field


class ParsingSectionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    section_name: str
    section_type: str  # 商务 / 技术
    is_star_item: bool
    source_file: str


class ParsingSectionDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    section_name: str
    section_type: str
    content: str
    is_star_item: bool
    source_file: str


class ParsingSectionUpdateRequest(BaseModel):
    content: str | None = Field(default=None)
