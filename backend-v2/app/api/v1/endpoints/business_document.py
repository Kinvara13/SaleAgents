from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.business_document import (
    BusinessDocumentSummary,
    BusinessDocumentDetail,
    BusinessDocumentUpdateRequest,
    DocumentExportResponse,
    DocumentScoreResponse,
)
from app.services import business_document_service
from app.services.document_export_service import export_document
from app.services.scoring_service import calculate_score

router = APIRouter()


@router.get("/{project_id}/business-documents", response_model=list[BusinessDocumentSummary])
def list_business_documents(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[BusinessDocumentSummary]:
    """获取项目的商务文档清单（4.1 商务部分）"""
    return business_document_service.list_business_documents(db, project_id)


@router.get("/{project_id}/business-documents/{doc_id}", response_model=BusinessDocumentDetail)
def get_business_document_detail(
    project_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
) -> BusinessDocumentDetail:
    """获取商务文档详情（含可编辑内容）"""
    return business_document_service.get_business_document_detail(db, project_id, doc_id)


@router.patch("/{project_id}/business-documents/{doc_id}", response_model=BusinessDocumentDetail)
def update_business_document(
    project_id: str,
    doc_id: str,
    payload: BusinessDocumentUpdateRequest,
    db: Session = Depends(get_db),
) -> BusinessDocumentDetail:
    """更新商务文档（4.2+ 支持人工修改）"""
    return business_document_service.update_business_document(db, project_id, doc_id, payload)


@router.post("/{project_id}/business-documents/{doc_id}/generate", response_model=BusinessDocumentDetail)
def generate_business_document(
    project_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
) -> BusinessDocumentDetail:
    """AI自动生成并填充商务文档内容"""
    return business_document_service.generate_business_document(db, project_id, doc_id)


@router.post("/{project_id}/business-documents/{doc_id}/export", response_model=DocumentExportResponse)
def export_business_document(
    project_id: str,
    doc_id: str,
    fmt: str | None = None,
    db: Session = Depends(get_db),
) -> DocumentExportResponse:
    """导出商务文档为 Word/Excel"""
    result = export_document(db, project_id, doc_id, doc_kind="business", fmt=fmt)
    return DocumentExportResponse(
        download_url=result["download_url"],
        filename=result["filename"],
        format=result["format"],
    )


@router.get("/{project_id}/business-documents/{doc_id}/score", response_model=DocumentScoreResponse)
def score_business_document(
    project_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
) -> DocumentScoreResponse:
    """计算商务文档评分"""
    return DocumentScoreResponse(**calculate_score(db, project_id, doc_id, doc_kind="business"))