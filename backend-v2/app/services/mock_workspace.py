from app.schemas.project import ProjectSummary
from app.schemas.workspace import (
    ExtractedField,
    GenerationSection,
    KnowledgeAsset,
    MetricItem,
    ModuleCard,
    NavItem,
    ParseSection,
    ReviewIssue,
    RuleHit,
    ScoreCard,
    WorkspaceData,
)


def build_default_projects() -> list[ProjectSummary]:
    # mock 假数据已清除，仅保留真实项目
    return []

def build_default_workspace() -> WorkspaceData:
    return WorkspaceData(
        nav_items=[],
        overview_metrics=[],
        modules=[],
        project_stats=[],
        project_filters=[],
        project_rows=build_default_projects(),
        parse_sections=[],
        extracted_fields=[],
        score_cards=[],
        rule_hits=[],
        ai_reasons=[],
        pending_checks=[],
        generation_sections=[],
        generation_assets=[],
        generation_todos=[],
        review_summary=[],
        review_issues=[],
        review_actions=[],
    )
