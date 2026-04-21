from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class IndexedGenerationAssetResponse(BaseModel):
    id: str
    title: str
    asset_type: str
    score: str
    status: str
    summary: str = ""
    keywords: list[str] = Field(default_factory=list)
    scene_tags: list[str] = Field(default_factory=list)
    section_tags: list[str] = Field(default_factory=list)
    source_kind: str = "manual"
    file_name: str = ""
    owner: str = "system"
    visibility: str = "internal"
    review_status: str = "approved"
    reviewer: str = ""
    review_note: str = ""


class KnowledgeAssetChunkResponse(BaseModel):
    id: str
    asset_id: str
    title: str
    content: str
    keywords: list[str] = Field(default_factory=list)
    section_tags: list[str] = Field(default_factory=list)
    sort_order: int
    weight: float


class GenerationAssetUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    asset_type: str = Field(default="通用素材", max_length=64)
    status: str = Field(default="可引用", max_length=32)
    content: str = Field(min_length=1, max_length=20000)
    owner: str = Field(default="system", max_length=128)
    visibility: str = Field(default="internal", max_length=32)


class GenerationAssetCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    asset_type: str = Field(default="通用素材", max_length=64)
    status: str = Field(default="可引用", max_length=32)
    content: str = Field(min_length=1, max_length=20000)
    owner: str = Field(default="system", max_length=128)
    visibility: str = Field(default="internal", max_length=32)


class GenerationAssetRefreshRequest(BaseModel):
    asset_id: str | None = Field(default=None, max_length=64)
    triggered_by: str = Field(default="system", max_length=128)


class GenerationAssetReviewRequest(BaseModel):
    action: str = Field(pattern="^(approve|reject)$")
    reviewer: str = Field(min_length=1, max_length=128)
    review_note: str = Field(default="", max_length=2000)


class GenerationAssetChunkCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=4000)
    keywords: list[str] = Field(default_factory=list)
    section_tags: list[str] = Field(default_factory=list)
    weight: float = Field(default=1.0, ge=0.1, le=10.0)


class GenerationAssetChunkUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=4000)
    keywords: list[str] = Field(default_factory=list)
    section_tags: list[str] = Field(default_factory=list)
    weight: float = Field(default=1.0, ge=0.1, le=10.0)


class GenerationAssetIndexJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    asset_id: str
    status: str
    triggered_by: str
    refreshed_count: int
    error_message: str
    created_at: datetime
    completed_at: datetime | None = None


class ProjectGenerationAssetPreferencesResponse(BaseModel):
    project_id: str
    fixed_asset_titles: list[str] = Field(default_factory=list)
    excluded_asset_titles: list[str] = Field(default_factory=list)


class ProjectGenerationAssetPreferencesUpdateRequest(BaseModel):
    fixed_asset_titles: list[str] = Field(default_factory=list)
    excluded_asset_titles: list[str] = Field(default_factory=list)


class GenerationJobCreateRequest(BaseModel):
    project_id: str | None = Field(default=None, max_length=64)
    project_name: str = Field(min_length=1, max_length=255)
    template_name: str = Field(default="标准回标模板", max_length=128)
    client_name: str = Field(default="", max_length=255)
    project_summary: str = Field(default="", max_length=4000)
    tender_requirements: str = Field(default="", max_length=8000)
    delivery_deadline: str = Field(default="", max_length=128)
    service_commitment: str = Field(default="", max_length=4000)
    selected_asset_titles: list[str] = Field(default_factory=list)
    section_titles: list[str] = Field(default_factory=list)
    technical_spec_text: str = Field(default="", max_length=50000)


class GenerationProjectContextResponse(BaseModel):
    project_id: str
    project_name: str
    client_name: str = ""
    template_name: str = "标准回标模板"
    project_summary: str = ""
    tender_requirements: str = ""
    delivery_deadline: str = ""
    service_commitment: str = ""
    selected_asset_titles: list[str] = Field(default_factory=list)
    section_titles: list[str] = Field(default_factory=list)
    fixed_asset_titles: list[str] = Field(default_factory=list)
    excluded_asset_titles: list[str] = Field(default_factory=list)
    source_excerpt: str = ""


class GenerationProjectRunRequest(BaseModel):
    template_name: str | None = Field(default=None, max_length=128)
    project_summary: str | None = Field(default=None, max_length=4000)
    tender_requirements: str | None = Field(default=None, max_length=8000)
    delivery_deadline: str | None = Field(default=None, max_length=128)
    service_commitment: str | None = Field(default=None, max_length=4000)
    selected_asset_titles: list[str] | None = Field(default=None)
    section_titles: list[str] | None = Field(default=None)


class GenerationSectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str
    section_no: int
    title: str
    content: str
    status: str
    citations: int
    todos: int
    created_at: datetime
    routed_assets: list[str] = Field(default_factory=list)
    routing_reasons: list[str] = Field(default_factory=list)
    matched_score_items: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    coverage_score: int = 0


class GenerationScoreItemResponse(BaseModel):
    id: str
    title: str
    source: str
    weight: int = 1
    mapped_sections: list[str] = Field(default_factory=list)
    matched_sections: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    coverage_status: str = "待覆盖"


class GenerationCheckResponse(BaseModel):
    id: str
    level: str
    category: str
    title: str
    detail: str
    related_sections: list[str] = Field(default_factory=list)


class GenerationSectionCoverageResponse(BaseModel):
    section_id: str
    section_title: str
    coverage_score: int = 0
    matched_score_items: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    self_check_notes: list[str] = Field(default_factory=list)


class GenerationJobAnalysisResponse(BaseModel):
    job_id: str
    overall_coverage_score: int = 0
    mapped_score_item_count: int = 0
    covered_score_item_count: int = 0
    uncovered_score_item_count: int = 0
    score_items: list[GenerationScoreItemResponse] = Field(default_factory=list)
    checks: list[GenerationCheckResponse] = Field(default_factory=list)
    section_coverages: list[GenerationSectionCoverageResponse] = Field(default_factory=list)


class GenerationSectionUpdateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=20000)
    status: str = Field(default="已编辑", max_length=32)


class GenerationJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None = None
    project_name: str
    template_name: str
    status: str
    section_count: int
    overall_progress: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
