from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.technical_document import (
    TechnicalDocumentSummary,
    TechnicalDocumentDetail,
    TechnicalDocumentUpdateRequest,
)
from app.services import technical_document_service

router = APIRouter()


@router.get("/{project_id}/technical-documents", response_model=list[TechnicalDocumentSummary])
def list_technical_documents(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[TechnicalDocumentSummary]:
    """获取项目的技术文档清单（4.14-4.22 技术部分）"""
    return technical_document_service.list_technical_documents(db, project_id)


@router.get("/{project_id}/technical-documents/{doc_id}", response_model=TechnicalDocumentDetail)
def get_technical_document_detail(
    project_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
) -> TechnicalDocumentDetail:
    """获取技术文档详情（含可编辑内容）"""
    return technical_document_service.get_technical_document_detail(db, project_id, doc_id)


@router.patch("/{project_id}/technical-documents/{doc_id}", response_model=TechnicalDocumentDetail)
def update_technical_document(
    project_id: str,
    doc_id: str,
    payload: TechnicalDocumentUpdateRequest,
    db: Session = Depends(get_db),
) -> TechnicalDocumentDetail:
    """更新技术文档（支持人工修改）"""
    return technical_document_service.update_technical_document(db, project_id, doc_id, payload)