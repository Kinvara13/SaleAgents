from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.workspace_panel import WorkspacePanel
from app.schemas.project import ProjectCreateRequest, ProjectSummary, ProjectUpdateRequest
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
from app.services.mock_workspace import build_default_projects, build_default_workspace
from app.services.asset_index_service import asset_index_service

WORKSPACE_PANEL_KEYS = [
    "nav_items",
    "overview_metrics",
    "modules",
    "project_stats",
    "project_filters",
    "parse_sections",
    "extracted_fields",
    "score_cards",
    "rule_hits",
    "ai_reasons",
    "pending_checks",
    "generation_sections",
    "generation_assets",
    "generation_todos",
    "review_summary",
    "review_issues",
    "review_actions",
]


def initialize_database(db: Session) -> None:
    if db.scalar(select(Project.id).limit(1)) is None:
        for item in build_default_projects():
            db.add(
                Project(
                    id=item.id,
                    name=item.name,
                    status=item.status,
                    owner=item.owner,
                    client=item.client,
                    deadline=item.deadline,
                    amount=item.amount,
                    risk=item.risk,
                    module_progress=item.module_progress,
                )
            )

    existing_keys = set(db.scalars(select(WorkspacePanel.key)).all())
    snapshot = build_default_workspace().model_dump()
    for key in WORKSPACE_PANEL_KEYS:
        if key not in existing_keys:
            db.add(WorkspacePanel(key=key, payload=snapshot[key]))

    # Migrate LLM providers if json config exists
    from pathlib import Path
    import json
    from app.models.settings import AIConfig
    
    config_file = Path(__file__).resolve().parents[3] / "llm_providers.json"
    if config_file.exists() and db.query(AIConfig).count() == 0:
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                active_id = data.get("active_provider_id")
                for p in data.get("providers", []):
                    db.add(AIConfig(
                        id=p.get("id"),
                        name=p.get("name"),
                        base_url=p.get("base_url"),
                        api_key=p.get("api_key"),
                        model=p.get("model"),
                        provider=p.get("protocol", "openai"),
                        is_active=(p.get("id") == active_id)
                    ))
            import os
            os.remove(config_file)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to migrate llm_providers.json: {e}")

    db.commit()
    asset_index_service.initialize_seed_assets(db)


def list_projects(db: Session) -> list[ProjectSummary]:
    rows = db.scalars(select(Project).order_by(Project.created_at.asc())).all()
    return [_to_project_summary(row) for row in rows]


def get_project(db: Session, project_id: str) -> ProjectSummary:
    row = db.get(Project, project_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )
    return _to_project_summary(row)


def update_project(db: Session, project_id: str, payload: "ProjectUpdateRequest") -> ProjectSummary:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if payload.status is not None:
        project.status = payload.status
        
    db.commit()
    db.refresh(project)
    return _to_project_summary(project)


def create_project(db: Session, payload: ProjectCreateRequest) -> ProjectSummary:
    project = Project(
        id=f"project-{uuid4().hex[:8]}",
        name=payload.name.strip(),
        status=payload.status.strip() or "待决策",
        owner=payload.owner.strip(),
        client=payload.client.strip(),
        deadline=payload.deadline.strip(),
        amount=payload.amount.strip(),
        risk=payload.risk.strip().upper() or "P2",
        module_progress={
            "decision": "pending",
            "generation": "pending",
            "review": "pending",
        },
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _to_project_summary(project)


def _panel_payload(db: Session, key: str):
    panel = db.get(WorkspacePanel, key)
    return panel.payload if panel else []


def _to_project_summary(row: Project) -> ProjectSummary:
    return ProjectSummary(
        id=row.id,
        name=row.name,
        status=row.status,
        owner=row.owner,
        client=row.client,
        deadline=row.deadline,
        amount=row.amount,
        risk=row.risk,
        module_progress=row.module_progress,
    )


def get_parse_sections(db: Session) -> list[ParseSection]:
    return [ParseSection(**item) for item in _panel_payload(db, "parse_sections")]


def get_extracted_fields(db: Session) -> list[ExtractedField]:
    return [ExtractedField(**item) for item in _panel_payload(db, "extracted_fields")]


def get_score_cards(db: Session) -> list[ScoreCard]:
    return [ScoreCard(**item) for item in _panel_payload(db, "score_cards")]


def get_rule_hits(db: Session) -> list[RuleHit]:
    return [RuleHit(**item) for item in _panel_payload(db, "rule_hits")]


def get_ai_reasons(db: Session) -> list[str]:
    return list(_panel_payload(db, "ai_reasons"))


def get_generation_sections(db: Session) -> list[GenerationSection]:
    return [GenerationSection(**item) for item in _panel_payload(db, "generation_sections")]


def get_generation_assets(db: Session) -> list[KnowledgeAsset]:
    return [KnowledgeAsset(**item) for item in _panel_payload(db, "generation_assets")]


def get_generation_todos(db: Session) -> list[str]:
    return list(_panel_payload(db, "generation_todos"))


def get_review_summary(db: Session) -> list[MetricItem]:
    return [MetricItem(**item) for item in _panel_payload(db, "review_summary")]


def get_review_issues(db: Session) -> list[ReviewIssue]:
    return [ReviewIssue(**item) for item in _panel_payload(db, "review_issues")]


def get_review_actions(db: Session) -> list[str]:
    return list(_panel_payload(db, "review_actions"))


def get_workspace_data(db: Session) -> WorkspaceData:
    return WorkspaceData(
        nav_items=[NavItem(**item) for item in _panel_payload(db, "nav_items")],
        overview_metrics=[MetricItem(**item) for item in _panel_payload(db, "overview_metrics")],
        modules=[ModuleCard(**item) for item in _panel_payload(db, "modules")],
        project_stats=[MetricItem(**item) for item in _panel_payload(db, "project_stats")],
        project_filters=list(_panel_payload(db, "project_filters")),
        project_rows=list_projects(db),
        parse_sections=get_parse_sections(db),
        extracted_fields=get_extracted_fields(db),
        score_cards=get_score_cards(db),
        rule_hits=get_rule_hits(db),
        ai_reasons=get_ai_reasons(db),
        pending_checks=list(_panel_payload(db, "pending_checks")),
        generation_sections=get_generation_sections(db),
        generation_assets=get_generation_assets(db),
        generation_todos=get_generation_todos(db),
        review_summary=get_review_summary(db),
        review_issues=get_review_issues(db),
        review_actions=get_review_actions(db),
    )
