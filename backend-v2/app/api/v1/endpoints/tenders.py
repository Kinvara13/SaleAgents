from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.tender import TenderCreateRequest, TenderDecisionRequest, TenderSummary
from app.services import tender_service
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.auth import UserInfoResponse

router = APIRouter()


@router.get("", response_model=list[TenderSummary])
def get_tenders(
    current_user: UserInfoResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TenderSummary]:
    """获取招标信息列表"""
    return tender_service.list_tenders(db, user_id=current_user.id)


@router.post("", response_model=TenderSummary, status_code=status.HTTP_201_CREATED)
def post_tender(
    payload: TenderCreateRequest,
    current_user: UserInfoResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TenderSummary:
    """新增招标信息"""
    tender = tender_service.create_tender(db, payload, user_id=current_user.id)
    return tender


@router.get("/{tender_id}", response_model=TenderSummary)
def get_tender_detail(
    tender_id: str,
    db: Session = Depends(get_db),
) -> TenderSummary:
    """获取招标信息详情"""
    tender = tender_service.get_tender(db, tender_id)
    return TenderSummary.model_validate(tender)


class TenderDecisionRequestBody(BaseModel):
    decision: str  # "bid" | "reject"
    reason: str = ""
    margin: str = ""
    project_type: str = ""


@router.post("/{tender_id}/decision", response_model=TenderSummary)
def post_tender_decision(
    tender_id: str,
    body: TenderDecisionRequestBody,
    db: Session = Depends(get_db),
) -> TenderSummary:
    """投标/不投决策"""
    tender_payload = TenderDecisionRequest(
        decision=body.decision,
        reason=body.reason,
        margin=body.margin,
        project_type=body.project_type,
    )
    return tender_service.update_tender_decision(db, tender_id, tender_payload)


@router.post("/{tender_id}/upload", response_model=TenderSummary)
def upload_bid_document(
    tender_id: str,
    file: UploadFile = File(...),
    margin: str = Form(""),
    project_type: str = Form(""),
    background_tasks: BackgroundTasks = None,
    current_user: UserInfoResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TenderSummary:
    """上传标书文件，投标"""
    import os
    import uuid
    from datetime import datetime
    from pathlib import Path

    from app.core.config import settings

    upload_dir = getattr(settings, "upload_dir", "/tmp/saleagents/uploads")
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or ".pdf")[1] or ".pdf"
    saved_name = f"tender_{tender_id}_{uuid.uuid4().hex[:8]}{ext}"
    saved_path = os.path.join(upload_dir, saved_name)

    with open(saved_path, "wb") as f:
        content = file.file.read()
        f.write(content)

    from app.schemas.project import ProjectCreateRequest
    from app.services import project_service

    project = project_service.create_project(
        db,
        ProjectCreateRequest(
            name=f"投标项目_{tender_id}",
            owner=current_user.username,
            deadline="",
            amount="",
            user_id=current_user.id,
        ),
    )
    tender_service.bind_project(db, tender_id, project.id)
    
    # Update project tender_id and file list
    project.tender_id = tender_id
    project.parse_status = "解析中"
    project.file_list = [{"name": file.filename, "path": saved_path, "uploaded_at": str(datetime.utcnow())}]
    project.node_status = {
        "decision": "done",
        "parsing": "in_progress",
        "generation": "pending",
        "review": "pending",
    }
    db.commit()
    
    # Update tender margin and project_type
    tender = tender_service.get_tender(db, tender_id)
    if margin:
        tender.margin = margin
    if project_type:
        tender.project_type = project_type
    db.commit()
    
    # Trigger async parsing in background
    if background_tasks is not None:
        from app.api.v1.endpoints.parsing import _parse_single_file_async
        background_tasks.add_task(_parse_single_file_async, project.id, Path(saved_path), file.filename or "unknown")
    
    return TenderSummary.model_validate(tender_service.get_tender(db, tender_id))
