from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.parsing import (
    ProjectDocumentUploadResponse,
    ProjectParsingContextResponse,
    ProjectParsingFieldUpdateRequest,
    ProjectParsingRunResponse,
)
from app.schemas.workspace import ExtractedField, ParseSection
from app.services.parsing_service import parsing_service
from app.services.workspace_service import get_extracted_fields, get_parse_sections

router = APIRouter()


@router.get("/sections", response_model=list[ParseSection])
def list_parse_sections(db: Session = Depends(get_db)) -> list[ParseSection]:
    return get_parse_sections(db)


@router.get("/fields", response_model=list[ExtractedField])
def list_extracted_fields(db: Session = Depends(get_db)) -> list[ExtractedField]:
    return get_extracted_fields(db)


@router.get("/projects/{project_id}", response_model=ProjectParsingContextResponse)
def get_project_parsing_context(project_id: str, db: Session = Depends(get_db)) -> ProjectParsingContextResponse:
    return parsing_service.get_project_context(db, project_id)


@router.post(
    "/projects/{project_id}/upload",
    response_model=ProjectDocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_project_document(
    project_id: str,
    file: UploadFile = File(...),
    document_type: str = Form(default="招标文件"),
    db: Session = Depends(get_db),
) -> ProjectDocumentUploadResponse:
    return parsing_service.upload_project_document(
        db,
        project_id=project_id,
        filename=file.filename or "uploaded-tender.txt",
        file_bytes=await file.read(),
        document_type=document_type,
    )


@router.post("/projects/{project_id}/run", response_model=ProjectParsingRunResponse)
def rerun_project_parsing(project_id: str, db: Session = Depends(get_db)) -> ProjectParsingRunResponse:
    return parsing_service.rerun_project_parsing(db, project_id)


@router.patch("/projects/{project_id}/fields/{field_label}", response_model=ExtractedField)
def update_project_parsing_field(
    project_id: str,
    field_label: str,
    payload: ProjectParsingFieldUpdateRequest,
    db: Session = Depends(get_db),
) -> ExtractedField:
    return parsing_service.update_project_field(db, project_id, field_label, payload)
