from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.review.service import review_service
from app.schemas.review import (
    ReviewFeedbackRequest,
    ReviewFeedbackResponse,
    ReviewJobClause,
    ReviewIssueResolveRequest,
    ReviewJobCreateRequest,
    ReviewJobIssue,
    ReviewJobResponse,
    ReviewJobRerunRequest,
    RuleConfigCreate,
    RuleConfigResponse,
    RuleConfigUpdate,
    RuleStatisticsResponse,
)
from app.schemas.workspace import MetricItem, ReviewIssue
from app.services.rule_config_service import rule_config_service
from app.services.workspace_service import get_review_actions, get_review_issues, get_review_summary

router = APIRouter()


@router.get("/summary", response_model=list[MetricItem])
def list_review_summary(db: Session = Depends(get_db)) -> list[MetricItem]:
    latest = review_service.get_latest_summary(db)
    return latest if latest is not None else get_review_summary(db)


@router.get("/issues", response_model=list[ReviewIssue])
def list_review_issues(db: Session = Depends(get_db)) -> list[ReviewIssue]:
    latest = review_service.get_latest_issues(db)
    return latest if latest is not None else get_review_issues(db)


@router.get("/actions", response_model=list[str])
def list_review_actions(db: Session = Depends(get_db)) -> list[str]:
    latest = review_service.get_latest_actions(db)
    return latest if latest is not None else get_review_actions(db)


@router.post("/jobs", response_model=ReviewJobResponse, status_code=status.HTTP_201_CREATED)
def create_review_job(
    payload: ReviewJobCreateRequest,
    db: Session = Depends(get_db),
) -> ReviewJobResponse:
    return review_service.create_job(db, payload)


@router.get("/jobs/latest", response_model=ReviewJobResponse | None)
def get_latest_review_job(db: Session = Depends(get_db)) -> ReviewJobResponse | None:
    return review_service.get_latest_job(db)


@router.get("/jobs/{job_id}", response_model=ReviewJobResponse)
def get_review_job(job_id: str, db: Session = Depends(get_db)) -> ReviewJobResponse:
    return review_service.get_job(db, job_id)


@router.get("/jobs/{job_id}/issues", response_model=list[ReviewJobIssue])
def get_review_job_issues(job_id: str, db: Session = Depends(get_db)) -> list[ReviewJobIssue]:
    return review_service.list_job_issues(db, job_id)


@router.get("/jobs/{job_id}/summary", response_model=list[MetricItem])
def get_review_job_summary(job_id: str, db: Session = Depends(get_db)) -> list[MetricItem]:
    return review_service.get_job_summary(db, job_id)


@router.get("/jobs/{job_id}/clauses", response_model=list[ReviewJobClause])
def get_review_job_clauses(job_id: str, db: Session = Depends(get_db)) -> list[ReviewJobClause]:
    return review_service.list_job_clauses(db, job_id)


@router.get("/jobs/{job_id}/report", response_class=PlainTextResponse)
def export_review_job_report(job_id: str, db: Session = Depends(get_db)) -> str:
    return review_service.export_job_report(db, job_id)


@router.get("/jobs/{job_id}/report/docx")
def export_review_job_report_docx(job_id: str, db: Session = Depends(get_db)) -> Response:
    docx_bytes = review_service.export_job_report_docx(db, job_id)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename=review-report-{job_id}.docx"
        },
    )


@router.post("/jobs/{job_id}/rerun", response_model=ReviewJobResponse)
def rerun_review_job(
    job_id: str,
    payload: ReviewJobRerunRequest,
    db: Session = Depends(get_db),
) -> ReviewJobResponse:
    return review_service.rerun_job(db, job_id, payload)


@router.post("/jobs/upload", response_model=ReviewJobResponse, status_code=status.HTTP_201_CREATED)
async def upload_review_job(
    file: UploadFile = File(...),
    contract_name: str | None = Form(default=None),
    contract_type: str = Form(default="采购合同"),
    project_id: str | None = Form(default=None),
    trigger: str = Form(default="upload"),
    db: Session = Depends(get_db),
) -> ReviewJobResponse:
    return review_service.create_job_from_upload(
        db,
        filename=file.filename or "uploaded-contract.txt",
        file_bytes=await file.read(),
        contract_name=contract_name,
        contract_type=contract_type,
        project_id=project_id,
        trigger=trigger,
    )


@router.post("/issues/{issue_id}/resolve", response_model=ReviewJobIssue)
def resolve_review_issue(
    issue_id: str,
    payload: ReviewIssueResolveRequest,
    db: Session = Depends(get_db),
) -> ReviewJobIssue:
    return review_service.resolve_issue(db, issue_id, payload)


@router.post("/issues/{issue_id}/feedback", response_model=ReviewFeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_issue_feedback(
    issue_id: str,
    payload: ReviewFeedbackRequest,
    db: Session = Depends(get_db),
) -> ReviewFeedbackResponse:
    return review_service.submit_feedback(db, issue_id, payload)


@router.get("/rules", response_model=list[RuleConfigResponse])
def list_rules(
    db: Session = Depends(get_db),
    is_enabled: bool | None = None,
    category: str | None = None,
) -> list[RuleConfigResponse]:
    return rule_config_service.list_rules(db, is_enabled=is_enabled, category=category)


@router.get("/rules/statistics", response_model=list[RuleStatisticsResponse])
def get_rule_statistics(
    db: Session = Depends(get_db),
    rule_name: str | None = None,
) -> list[RuleStatisticsResponse]:
    return rule_config_service.get_statistics(db, rule_name)


@router.post("/rules/initialize", status_code=status.HTTP_201_CREATED)
def initialize_default_rules(db: Session = Depends(get_db)) -> dict:
    count = rule_config_service.initialize_default_rules(db)
    return {"initialized": count, "message": f"Initialized {count} default rules."}


@router.get("/rules/{rule_id}", response_model=RuleConfigResponse)
def get_rule(rule_id: str, db: Session = Depends(get_db)) -> RuleConfigResponse:
    return rule_config_service.get_rule(db, rule_id)


@router.post("/rules", response_model=RuleConfigResponse, status_code=status.HTTP_201_CREATED)
def create_rule(payload: RuleConfigCreate, db: Session = Depends(get_db)) -> RuleConfigResponse:
    return rule_config_service.create_rule(db, payload)


@router.patch("/rules/{rule_id}", response_model=RuleConfigResponse)
def update_rule(rule_id: str, payload: RuleConfigUpdate, db: Session = Depends(get_db)) -> RuleConfigResponse:
    return rule_config_service.update_rule(db, rule_id, payload)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: str, db: Session = Depends(get_db)) -> None:
    rule_config_service.delete_rule(db, rule_id)
