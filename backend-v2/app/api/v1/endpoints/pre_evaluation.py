from fastapi import APIRouter, Depends, File, Form, UploadFile, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.pre_evaluation import PreEvaluationJobListItem, PreEvaluationJobResponse
from app.services.pre_evaluation_service import pre_evaluation_service

router = APIRouter()


@router.post("/upload", response_model=PreEvaluationJobResponse, status_code=status.HTTP_201_CREATED)
async def upload_pre_evaluation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    project_id: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> PreEvaluationJobResponse:
    # 同步只做：建表、落盘、设置状态为 parsing。这部分非常快。
    job = pre_evaluation_service.create_job_from_upload_sync(
        db,
        file_bytes=await file.read(),
        filename=file.filename or "uploaded-file",
        project_id=project_id,
    )
    
    # 将解析和 LLM 分析的长耗时任务放入 BackgroundTasks 异步执行
    background_tasks.add_task(
        pre_evaluation_service.process_job_async,
        job_id=job.id,
    )
    
    return job


@router.get("/jobs", response_model=list[PreEvaluationJobListItem])
def list_pre_evaluations(
    project_id: str | None = None,
    db: Session = Depends(get_db),
) -> list[PreEvaluationJobListItem]:
    return pre_evaluation_service.list_jobs(db, project_id=project_id)


@router.get("/jobs/{job_id}", response_model=PreEvaluationJobResponse)
def get_pre_evaluation(job_id: str, db: Session = Depends(get_db)) -> PreEvaluationJobResponse:
    return pre_evaluation_service.get_job(db, job_id)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pre_evaluation(job_id: str, db: Session = Depends(get_db)) -> None:
    pre_evaluation_service.delete_job(db, job_id)
