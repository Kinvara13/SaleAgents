from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.parsing import ParsingSectionSummary, ParsingSectionDetail, ParsingSectionUpdateRequest
from app.services import parsing_service

router = APIRouter()


ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


@router.post("/{project_id}/upload", response_model=list[ParsingSectionSummary])
async def upload_and_parse(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> list[ParsingSectionSummary]:
    """上传招标文件并解析（真实文件存储 + 模拟解析）"""
    import os
    from pathlib import Path
    from app.core.config import settings

    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # 保存文件到 projects/{project_id}/bid_documents/
    upload_dir = Path(settings.storage_path or "/Users/sen/SaleAgents/backend-v2/storage/projects") / project_id / "bid_documents"
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / filename
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小超过100MB限制")

    with open(file_path, "wb") as f:
        f.write(content)

    return parsing_service.simulate_parse(db, project_id, filename)


@router.get("/{project_id}/sections", response_model=list[ParsingSectionSummary])
def get_sections(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[ParsingSectionSummary]:
    return parsing_service.list_sections(db, project_id)


@router.get("/{project_id}/sections/{section_id}", response_model=ParsingSectionDetail)
def get_section_detail(
    project_id: str,
    section_id: str,
    db: Session = Depends(get_db),
) -> ParsingSectionDetail:
    return parsing_service.get_section_detail(db, project_id, section_id)


@router.patch("/{project_id}/sections/{section_id}", response_model=ParsingSectionDetail)
def patch_section(
    project_id: str,
    section_id: str,
    payload: ParsingSectionUpdateRequest,
    db: Session = Depends(get_db),
) -> ParsingSectionDetail:
    return parsing_service.update_section(db, project_id, section_id, payload)
