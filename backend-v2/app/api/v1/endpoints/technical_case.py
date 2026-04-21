from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.technical_case import (
    TechnicalCaseSummary,
    TechnicalCaseDetail,
    TechnicalCaseCreateRequest,
    TechnicalCaseUpdateRequest,
)
from app.services import technical_case_service

router = APIRouter()


@router.get("/{project_id}/technical-cases", response_model=list[TechnicalCaseSummary])
def list_technical_cases(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[TechnicalCaseSummary]:
    """获取项目的技术案例列表"""
    return technical_case_service.list_technical_cases(db, project_id)


@router.get("/{project_id}/technical-cases/{case_id}", response_model=TechnicalCaseDetail)
def get_technical_case_detail(
    project_id: str,
    case_id: str,
    db: Session = Depends(get_db),
) -> TechnicalCaseDetail:
    """获取技术案例详情"""
    return technical_case_service.get_technical_case_detail(db, project_id, case_id)


@router.post("/{project_id}/technical-cases", response_model=TechnicalCaseDetail)
def create_technical_case(
    project_id: str,
    payload: TechnicalCaseCreateRequest,
    db: Session = Depends(get_db),
) -> TechnicalCaseDetail:
    """创建技术案例"""
    return technical_case_service.create_technical_case(
        db, {**payload.model_dump(), "project_id": project_id}
    )


@router.patch("/{project_id}/technical-cases/{case_id}", response_model=TechnicalCaseDetail)
def update_technical_case(
    project_id: str,
    case_id: str,
    payload: TechnicalCaseUpdateRequest,
    db: Session = Depends(get_db),
) -> TechnicalCaseDetail:
    """更新技术案例"""
    return technical_case_service.update_technical_case(
        db, project_id, case_id, payload.model_dump(exclude_none=True)
    )


@router.delete("/{project_id}/technical-cases/{case_id}")
def delete_technical_case(
    project_id: str,
    case_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """删除技术案例"""
    technical_case_service.delete_technical_case(db, project_id, case_id)
    return {"message": "deleted"}


@router.get("/{project_id}/technical-cases-search/search", response_model=list[TechnicalCaseSummary])
def search_technical_cases(
    project_id: str,
    primary_item: str = "",
    secondary_item: str = "",
    keyword: str = "",
    db: Session = Depends(get_db),
) -> list[TechnicalCaseSummary]:
    """根据评审项和关键词检索技术案例（素材库检索）"""
    return technical_case_service.search_technical_cases(
        db, project_id, primary_item, secondary_item, keyword
    )