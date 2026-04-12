from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.generation.service import generation_service
from app.schemas.generation import (
    GenerationJobResponse,
    ProjectGenerationAssetPreferencesResponse,
    ProjectGenerationAssetPreferencesUpdateRequest,
    GenerationProjectContextResponse,
    GenerationProjectRunRequest,
)
from app.schemas.project import ProjectCreateRequest, ProjectSummary, ProjectUpdateRequest
from app.services.workspace_service import create_project, get_project, list_projects, update_project

router = APIRouter()


@router.get("", response_model=list[ProjectSummary])
def get_projects(db: Session = Depends(get_db)) -> list[ProjectSummary]:
    return list_projects(db)


@router.post("", response_model=ProjectSummary, status_code=status.HTTP_201_CREATED)
def post_project(
    payload: ProjectCreateRequest,
    db: Session = Depends(get_db),
) -> ProjectSummary:
    return create_project(db, payload)


@router.get("/{project_id}", response_model=ProjectSummary)
def get_project_detail(project_id: str, db: Session = Depends(get_db)) -> ProjectSummary:
    return get_project(db, project_id)


@router.patch("/{project_id}", response_model=ProjectSummary)
def patch_project(
    project_id: str,
    payload: ProjectUpdateRequest,
    db: Session = Depends(get_db),
) -> ProjectSummary:
    return update_project(db, project_id, payload)


@router.get("/{project_id}/generation/context", response_model=GenerationProjectContextResponse)
def get_project_generation_context(
    project_id: str,
    db: Session = Depends(get_db),
) -> GenerationProjectContextResponse:
    return generation_service.get_project_context(db, project_id)


@router.get(
    "/{project_id}/generation/preferences",
    response_model=ProjectGenerationAssetPreferencesResponse,
)
def get_project_generation_preferences(
    project_id: str,
    db: Session = Depends(get_db),
) -> ProjectGenerationAssetPreferencesResponse:
    return generation_service.get_project_asset_preferences(db, project_id)


@router.patch(
    "/{project_id}/generation/preferences",
    response_model=ProjectGenerationAssetPreferencesResponse,
)
def patch_project_generation_preferences(
    project_id: str,
    payload: ProjectGenerationAssetPreferencesUpdateRequest,
    db: Session = Depends(get_db),
) -> ProjectGenerationAssetPreferencesResponse:
    return generation_service.update_project_asset_preferences(db, project_id, payload)


@router.post(
    "/{project_id}/generation/run",
    response_model=GenerationJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_project_generation(
    project_id: str,
    payload: GenerationProjectRunRequest,
    db: Session = Depends(get_db),
) -> GenerationJobResponse:
    return generation_service.create_job_from_project(db, project_id, payload)
