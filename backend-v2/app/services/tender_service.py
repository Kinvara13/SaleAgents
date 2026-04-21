from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.tender import Tender
from app.schemas.tender import TenderCreateRequest, TenderSummary, TenderDecisionRequest


def list_tenders(db: Session, user_id: str | None = None) -> list[TenderSummary]:
    query = db.query(Tender)
    if user_id:
        query = query.filter(Tender.user_id == user_id)
    query = query.order_by(Tender.created_at.desc())
    return [TenderSummary.model_validate(t) for t in query.all()]


def get_tender(db: Session, tender_id: str) -> Tender:
    tender = db.query(Tender).filter(Tender.id == tender_id).first()
    if not tender:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="招标信息不存在")
    return tender


def create_tender(db: Session, payload: TenderCreateRequest) -> TenderSummary:
    tender = Tender(
        id=f"tend_{uuid4().hex[:12]}",
        title=payload.title,
        source_url=payload.source_url,
        publish_date=payload.publish_date,
        deadline=payload.deadline,
        amount=payload.amount,
        project_type=payload.project_type,
        description=payload.description,
        decision="pending",
    )
    db.add(tender)
    db.commit()
    db.refresh(tender)
    return TenderSummary.model_validate(tender)


def update_tender_decision(
    db: Session, tender_id: str, payload: TenderDecisionRequest
) -> TenderSummary:
    tender = get_tender(db, tender_id)
    tender.decision = payload.decision
    if payload.decision == "reject":
        tender.reject_reason = payload.reason or ""
    db.commit()
    db.refresh(tender)
    return TenderSummary.model_validate(tender)


def bind_project(db: Session, tender_id: str, project_id: str) -> TenderSummary:
    tender = get_tender(db, tender_id)
    tender.project_id = project_id
    tender.decision = "bid"
    db.commit()
    db.refresh(tender)
    return TenderSummary.model_validate(tender)
