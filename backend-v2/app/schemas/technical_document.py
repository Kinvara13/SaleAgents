from pydantic import BaseModel, ConfigDict, Field


class TechnicalDocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    doc_type: str
    doc_name: str
    has_fillable_fields: bool
    is_star_item: bool
    score_point: str
    status: str
    source_file: str


class TechnicalDocumentDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    doc_type: str
    doc_name: str
    original_content: str
    editable_content: str
    has_fillable_fields: bool
    is_star_item: bool
    score_point: str
    rule_description: str
    status: str
    return_file_list: str  # JSON string
    source_file: str


class TechnicalDocumentUpdateRequest(BaseModel):
    editable_content: str | None = Field(default=None)
    status: str | None = Field(default=None)


class DocumentExportResponse(BaseModel):
    download_url: str
    filename: str
    format: str


class DocumentScoreResponse(BaseModel):
    score: float
    max_score: float
    is_scored: bool
    breakdown: dict
    message: str | None = None