from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.session import get_db
from app.schemas.task import TaskStatusResponse, TaskListParams, TaskSubmitResponse
from app.services import task_service

router = APIRouter()


@router.get("/{task_id}", response_model=TaskStatusResponse)
def get_task_status(
    task_id: str,
    db: Session = Depends(get_db),
) -> TaskStatusResponse:
    """查询异步任务状态"""
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 {task_id} 不存在",
        )
    return TaskStatusResponse.model_validate(task)


@router.get("", response_model=list[TaskStatusResponse])
def list_tasks(
    project_id: str | None = Query(None, description="按项目ID过滤"),
    task_type: str | None = Query(None, description="按任务类型过滤"),
    status: str | None = Query(None, description="按状态过滤"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[TaskStatusResponse]:
    """列出异步任务，支持过滤"""
    params = TaskListParams(
        project_id=project_id,
        task_type=task_type,
        status=status,
        limit=limit,
        offset=offset,
    )
    tasks, _ = task_service.list_tasks(db, params)
    return [TaskStatusResponse.model_validate(t) for t in tasks]
