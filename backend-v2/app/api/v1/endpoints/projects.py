from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.project import (
    ProjectCreateRequest, ProjectSummary, ProjectUpdateRequest,
    BidProgress, ScoringCriteriaItem, ProjectActivities,
)
from app.services import project_service
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.auth import UserInfoResponse  # noqa: F401

router = APIRouter()


@router.get("", response_model=list[ProjectSummary])
def get_projects(
    status: str | None = Query(None, description="状态筛选"),
    user_id: str | None = Query(None, description="用户ID筛选"),
    mine: bool = Query(False, description="只看我的项目"),
    current_user: UserInfoResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProjectSummary]:
    # 如果 mine=true 或显式传了 user_id，按用户过滤
    filter_user_id = None
    if mine:
        filter_user_id = current_user.id
    elif user_id:
        filter_user_id = user_id
    return project_service.list_projects(db, status=status, user_id=filter_user_id)


@router.post("", response_model=ProjectSummary, status_code=status.HTTP_201_CREATED)
def post_project(
    payload: ProjectCreateRequest,
    current_user: UserInfoResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProjectSummary:
    # 创建时自动关联当前用户
    if not payload.user_id:
        payload.user_id = current_user.id
    return project_service.create_project(db, payload)


@router.get("/{project_id}", response_model=ProjectSummary)
def get_project_detail(
    project_id: str,
    db: Session = Depends(get_db),
) -> ProjectSummary:
    project = project_service.get_project(db, project_id)
    return ProjectSummary.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectSummary)
def patch_project(
    project_id: str,
    payload: ProjectUpdateRequest,
    db: Session = Depends(get_db),
) -> ProjectSummary:
    return project_service.update_project(db, project_id, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
) -> None:
    project_service.delete_project(db, project_id)


class ConfirmRequest(BaseModel):
    feedback: str = ""
    confirmed_by: str = "admin"


@router.post("/{project_id}/confirm", response_model=ProjectSummary)
def confirm_project(
    project_id: str,
    payload: ConfirmRequest,
    db: Session = Depends(get_db),
) -> ProjectSummary:
    """相关人员确认投标项目"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return project_service.update_project(
        db,
        project_id,
        ProjectUpdateRequest(
            confirm_status="已确认",
            confirm_feedback=payload.feedback,
            confirmed_by=payload.confirmed_by,
            confirmed_at=now,
        ),
    )


@router.get("/{project_id}/bid-progress", response_model=BidProgress)
def get_project_bid_progress(
    project_id: str,
    db: Session = Depends(get_db),
) -> BidProgress:
    """获取项目回标文件完成情况"""
    result = project_service.get_project_bid_progress(db, project_id)
    return BidProgress(**result)


@router.get("/{project_id}/scoring-criteria", response_model=list[ScoringCriteriaItem])
def get_project_scoring_criteria(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[ScoringCriteriaItem]:
    """获取项目预估得分"""
    result = project_service.get_project_scoring_criteria(db, project_id)
    return [ScoringCriteriaItem.model_validate(item) for item in result["criteria"]]


@router.get("/{project_id}/activities", response_model=ProjectActivities)
def get_project_activities(
    project_id: str,
    db: Session = Depends(get_db),
) -> ProjectActivities:
    """获取项目操作历史"""
    result = project_service.get_project_activities(db, project_id)
    return ProjectActivities(**result)
