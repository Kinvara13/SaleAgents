from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session

from app.models.async_task import AsyncTask
from app.schemas.task import TaskListParams


def create_task(db: Session, task_type: str, project_id: str) -> AsyncTask:
    """创建新的异步任务记录"""
    task = AsyncTask(
        id=f"task_{uuid4().hex[:16]}",
        task_type=task_type,
        project_id=project_id,
        status="pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: str) -> AsyncTask | None:
    """获取任务详情"""
    return db.query(AsyncTask).filter(AsyncTask.id == task_id).first()


def update_task_status(
    db: Session,
    task_id: str,
    status: str,
    result: dict | None = None,
    error_message: str | None = None,
) -> AsyncTask | None:
    """更新任务状态"""
    task = db.query(AsyncTask).filter(AsyncTask.id == task_id).first()
    if not task:
        return None
    
    task.status = status
    task.updated_at = datetime.utcnow()
    
    if result is not None:
        task.result = result
    
    if error_message is not None:
        task.error_message = error_message
    
    if status in ("completed", "failed"):
        task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    return task


def list_tasks(db: Session, params: TaskListParams) -> tuple[list[AsyncTask], int]:
    """列出任务，支持过滤和分页"""
    query = db.query(AsyncTask)
    
    if params.project_id:
        query = query.filter(AsyncTask.project_id == params.project_id)
    
    if params.task_type:
        query = query.filter(AsyncTask.task_type == params.task_type)
    
    if params.status:
        query = query.filter(AsyncTask.status == params.status)
    
    total = query.count()
    tasks = query.order_by(AsyncTask.created_at.desc()).offset(params.offset).limit(params.limit).all()
    
    return tasks, total
