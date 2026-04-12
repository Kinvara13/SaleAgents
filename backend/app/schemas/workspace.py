from pydantic import BaseModel

from app.schemas.project import ProjectSummary


class NavItem(BaseModel):
    key: str
    index: str
    label: str
    summary: str


class MetricItem(BaseModel):
    label: str
    value: str
    hint: str | None = None
    tone: str | None = None


class ModuleCard(BaseModel):
    title: str
    description: str
    status: str
    metric: str


class ParseSection(BaseModel):
    title: str
    page: str
    state: str
    source_text: str = ""
    source_file: str = ""


class ExtractedField(BaseModel):
    label: str
    value: str
    confidence: str


class ScoreCard(BaseModel):
    label: str
    score: int
    note: str


class RuleHit(BaseModel):
    name: str
    result: str
    detail: str
    level: str


class GenerationSection(BaseModel):
    title: str
    status: str
    citations: int
    todo: int


class KnowledgeAsset(BaseModel):
    title: str
    type: str
    score: str
    status: str


class ReviewIssue(BaseModel):
    title: str
    type: str
    level: str
    status: str
    document: str
    detail: str
    evidence: str = ""
    suggestion: str = ""
    origin: str = ""
    rule_name: str = ""


class WorkspaceData(BaseModel):
    nav_items: list[NavItem]
    overview_metrics: list[MetricItem]
    modules: list[ModuleCard]
    project_stats: list[MetricItem]
    project_filters: list[str]
    project_rows: list[ProjectSummary]
    parse_sections: list[ParseSection]
    extracted_fields: list[ExtractedField]
    score_cards: list[ScoreCard]
    rule_hits: list[RuleHit]
    ai_reasons: list[str]
    pending_checks: list[str]
    generation_sections: list[GenerationSection]
    generation_assets: list[KnowledgeAsset]
    generation_todos: list[str]
    review_summary: list[MetricItem]
    review_issues: list[ReviewIssue]
    review_actions: list[str]
