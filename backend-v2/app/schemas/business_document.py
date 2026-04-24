from pydantic import BaseModel, ConfigDict, Field


class BusinessDocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    doc_type: str
    doc_name: str
    has_fillable_fields: bool
    is_star_item: bool
    score_point: str
    status: str
    source_file: str


class BusinessDocumentDetail(BaseModel):
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


class BusinessDocumentUpdateRequest(BaseModel):
    editable_content: str | None = Field(default=None)
    status: str | None = Field(default=None)


class DocumentExportResponse(BaseModel):
    download_url: str
    filename: str
    format: str


class ScoreBreakdown(BaseModel):
    completeness: float = Field(description="内容完整度 0-1")
    rule_match: float = Field(description="规则匹配度 0-1")
    semantic_quality: float = Field(description="语义质量 0-1 (LLM评估)")
    asset_coverage: float = Field(description="素材覆盖度 0-1")
    placeholder_count: int = Field(description="占位符数量")
    missing_keywords: list[str] = Field(default_factory=list, description="缺失关键词")
    llm_reasoning: str = Field(default="", description="LLM评分理由")


class DocumentScoreResponse(BaseModel):
    score: float = Field(description="当前得分")
    max_score: float = Field(description="满分")
    is_scored: bool = Field(description="是否已计分")
    breakdown: ScoreBreakdown = Field(description="评分明细")
    previous_score: float | None = Field(default=None, description="上次得分（用于对比）")
    score_delta: float | None = Field(default=None, description="得分变化")
    message: str | None = Field(default=None, description="提示信息")
