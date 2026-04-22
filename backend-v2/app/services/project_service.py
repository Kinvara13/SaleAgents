from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreateRequest, ProjectSummary, ProjectUpdateRequest


def list_projects(db: Session, status: str | None = None, user_id: str | None = None) -> list[ProjectSummary]:
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    if user_id:
        query = query.filter(Project.user_id == user_id)
    query = query.order_by(Project.created_at.desc())
    return [ProjectSummary.model_validate(p) for p in query.all()]


def get_project(db: Session, project_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return project


def create_project(db: Session, payload: ProjectCreateRequest) -> ProjectSummary:
    project = Project(
        id=f"proj_{uuid4().hex[:12]}",
        name=payload.name,
        client=payload.client or "",
        deadline=payload.deadline or "",
        amount=payload.amount or "",
        risk=payload.risk or "P2",
        status="待决策",
        owner="admin",
        bidding_company=payload.bidding_company or "",
        agent_name=payload.agent_name or "",
        agent_phone=payload.agent_phone or "",
        agent_email=payload.agent_email or "",
        company_address=payload.company_address or "",
        bank_name=payload.bank_name or "",
        bank_account=payload.bank_account or "",
        confirm_status=payload.confirm_status or "待确认",
        user_id=payload.user_id or "user-001",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectSummary.model_validate(project)


def update_project(db: Session, project_id: str, payload: ProjectUpdateRequest) -> ProjectSummary:
    project = get_project(db, project_id)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return ProjectSummary.model_validate(project)


def delete_project(db: Session, project_id: str) -> None:
    project = get_project(db, project_id)
    db.delete(project)
    db.commit()
