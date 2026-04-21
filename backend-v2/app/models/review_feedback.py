from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReviewFeedbackRecord(Base):
    __tablename__ = "review_feedback_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    issue_id: Mapped[str] = mapped_column(ForeignKey("review_issues_records.id"), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("review_jobs.id"), nullable=False, index=True)
    rule_name: Mapped[str] = mapped_column(String(128), nullable=False, default="", index=True)
    feedback_type: Mapped[str] = mapped_column(String(32), nullable=False)
    feedback_note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    reviewer: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
