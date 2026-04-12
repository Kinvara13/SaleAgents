from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, UploadFile, status
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.generation.service import generation_service
from app.schemas.generation import (
    GenerationAssetChunkCreateRequest,
    GenerationAssetChunkUpdateRequest,
    GenerationAssetCreateRequest,
    GenerationAssetRefreshRequest,
    GenerationAssetReviewRequest,
    GenerationAssetUpdateRequest,
    GenerationJobAnalysisResponse,
    GenerationJobCreateRequest,
    GenerationAssetIndexJobResponse,
    GenerationJobResponse,
    IndexedGenerationAssetResponse,
    KnowledgeAssetChunkResponse,
    GenerationSectionResponse,
    GenerationSectionUpdateRequest,
)
from app.schemas.workspace import GenerationSection, KnowledgeAsset
from app.services.asset_index_service import asset_index_service
from app.services.workspace_service import (
    get_generation_assets,
    get_generation_sections,
    get_generation_todos,
)

router = APIRouter()


# ----- legacy seed-data endpoints (keep for backward compatibility) ---------


@router.get("/sections", response_model=list[GenerationSection])
def list_generation_sections(db: Session = Depends(get_db)) -> list[GenerationSection]:
    return get_generation_sections(db)


@router.get("/assets", response_model=list[KnowledgeAsset])
def list_generation_assets(db: Session = Depends(get_db)) -> list[KnowledgeAsset]:
    return get_generation_assets(db)


@router.get("/assets/indexed", response_model=list[IndexedGenerationAssetResponse])
def list_indexed_generation_assets(db: Session = Depends(get_db)) -> list[IndexedGenerationAssetResponse]:
    return generation_service.list_indexed_assets(db)


@router.post("/assets", response_model=IndexedGenerationAssetResponse, status_code=status.HTTP_201_CREATED)
def create_generation_asset(
    payload: GenerationAssetCreateRequest,
    db: Session = Depends(get_db),
) -> IndexedGenerationAssetResponse:
    return generation_service.create_asset(
        db,
        title=payload.title,
        asset_type=payload.asset_type,
        status_text=payload.status,
        content=payload.content,
        owner=payload.owner,
        visibility=payload.visibility,
    )


@router.post("/assets/upload", response_model=IndexedGenerationAssetResponse, status_code=status.HTTP_201_CREATED)
async def upload_generation_asset(
    file: UploadFile = File(...),
    asset_type: str = Form("通用素材"),
    title: str | None = Form(default=None),
    owner: str = Form("system"),
    visibility: str = Form("internal"),
    db: Session = Depends(get_db),
) -> IndexedGenerationAssetResponse:
    return generation_service.upload_asset(
        db,
        filename=file.filename or "uploaded-asset.txt",
        file_bytes=await file.read(),
        asset_type=asset_type,
        title=title,
        owner=owner,
        visibility=visibility,
    )


@router.post("/assets/refresh-index")
def refresh_generation_asset_index(
    payload: GenerationAssetRefreshRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> GenerationAssetIndexJobResponse:
    job = generation_service.create_asset_refresh_job(
        db,
        asset_id=payload.asset_id,
        triggered_by=payload.triggered_by,
    )
    background_tasks.add_task(generation_service.run_asset_refresh_job, job.id)
    return job


@router.get("/assets/refresh-index/{job_id}", response_model=GenerationAssetIndexJobResponse)
def get_generation_asset_refresh_job(
    job_id: str,
    db: Session = Depends(get_db),
) -> GenerationAssetIndexJobResponse:
    return generation_service.get_asset_refresh_job(db, job_id)


@router.patch("/assets/{asset_id}", response_model=IndexedGenerationAssetResponse)
def patch_generation_asset(
    asset_id: str,
    payload: GenerationAssetUpdateRequest,
    db: Session = Depends(get_db),
) -> IndexedGenerationAssetResponse:
    return generation_service.update_asset(db, asset_id, payload)


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_generation_asset(
    asset_id: str,
    db: Session = Depends(get_db),
) -> Response:
    generation_service.delete_asset(db, asset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/assets/{asset_id}/review", response_model=IndexedGenerationAssetResponse)
def review_generation_asset(
    asset_id: str,
    payload: GenerationAssetReviewRequest,
    db: Session = Depends(get_db),
) -> IndexedGenerationAssetResponse:
    return generation_service.review_asset(db, asset_id, payload)


@router.get("/assets/{asset_id}/chunks", response_model=list[KnowledgeAssetChunkResponse])
def list_generation_asset_chunks(
    asset_id: str,
    db: Session = Depends(get_db),
) -> list[KnowledgeAssetChunkResponse]:
    return generation_service.list_asset_chunks(db, asset_id)


@router.post("/assets/{asset_id}/chunks", response_model=KnowledgeAssetChunkResponse, status_code=status.HTTP_201_CREATED)
def create_generation_asset_chunk(
    asset_id: str,
    payload: GenerationAssetChunkCreateRequest,
    db: Session = Depends(get_db),
) -> KnowledgeAssetChunkResponse:
    return generation_service.create_asset_chunk(db, asset_id, payload)


@router.patch("/assets/{asset_id}/chunks/{chunk_id}", response_model=KnowledgeAssetChunkResponse)
def patch_generation_asset_chunk(
    asset_id: str,
    chunk_id: str,
    payload: GenerationAssetChunkUpdateRequest,
    db: Session = Depends(get_db),
) -> KnowledgeAssetChunkResponse:
    return generation_service.update_asset_chunk(db, asset_id, chunk_id, payload)


@router.delete("/assets/{asset_id}/chunks/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_generation_asset_chunk(
    asset_id: str,
    chunk_id: str,
    db: Session = Depends(get_db),
) -> Response:
    generation_service.delete_asset_chunk(db, asset_id, chunk_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/todos", response_model=list[str])
def list_generation_todos(db: Session = Depends(get_db)) -> list[str]:
    return get_generation_todos(db)


# ----- real generation job endpoints ----------------------------------------


@router.post("/jobs", response_model=GenerationJobResponse, status_code=status.HTTP_201_CREATED)
def create_generation_job(
    payload: GenerationJobCreateRequest,
    db: Session = Depends(get_db),
) -> GenerationJobResponse:
    return generation_service.create_job(db, payload)


@router.get("/jobs/latest", response_model=GenerationJobResponse)
def get_latest_generation_job(db: Session = Depends(get_db)) -> GenerationJobResponse:
    return generation_service.get_latest_job(db)


@router.get("/jobs/{job_id}", response_model=GenerationJobResponse)
def get_generation_job(job_id: str, db: Session = Depends(get_db)) -> GenerationJobResponse:
    return generation_service.get_job(db, job_id)


@router.get("/jobs/{job_id}/analysis", response_model=GenerationJobAnalysisResponse)
def get_generation_job_analysis(job_id: str, db: Session = Depends(get_db)) -> GenerationJobAnalysisResponse:
    return generation_service.get_job_analysis(db, job_id)


@router.get("/jobs/{job_id}/sections", response_model=list[GenerationSectionResponse])
def get_generation_job_sections(
    job_id: str, db: Session = Depends(get_db)
) -> list[GenerationSectionResponse]:
    return generation_service.list_job_sections(db, job_id)


@router.post(
    "/jobs/{job_id}/sections/{section_id}/regenerate",
    response_model=GenerationSectionResponse,
)
def regenerate_generation_section(
    job_id: str,
    section_id: str,
    db: Session = Depends(get_db),
) -> GenerationSectionResponse:
    return generation_service.regenerate_section(db, job_id, section_id)


@router.post("/jobs/{job_id}/repair-uncovered", response_model=list[GenerationSectionResponse])
def repair_generation_job_uncovered(
    job_id: str,
    db: Session = Depends(get_db),
) -> list[GenerationSectionResponse]:
    return generation_service.repair_uncovered_sections(db, job_id)


@router.post("/jobs/{job_id}/self-revise", response_model=list[GenerationSectionResponse])
def self_revise_generation_job(
    job_id: str,
    db: Session = Depends(get_db),
) -> list[GenerationSectionResponse]:
    return generation_service.self_revise_job(db, job_id)


@router.patch(
    "/jobs/{job_id}/sections/{section_id}",
    response_model=GenerationSectionResponse,
)
def update_generation_section(
    job_id: str,
    section_id: str,
    payload: GenerationSectionUpdateRequest,
    db: Session = Depends(get_db),
) -> GenerationSectionResponse:
    return generation_service.update_section(db, job_id, section_id, payload)


@router.get("/jobs/{job_id}/export", response_class=PlainTextResponse)
def export_generation_job(job_id: str, db: Session = Depends(get_db)) -> str:
    return generation_service.export_job(db, job_id)


@router.get("/jobs/{job_id}/export/docx")
def export_generation_job_docx(job_id: str, db: Session = Depends(get_db)) -> Response:
    docx_bytes = generation_service.export_job_docx(db, job_id)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=generation-{job_id}.docx"},
    )
