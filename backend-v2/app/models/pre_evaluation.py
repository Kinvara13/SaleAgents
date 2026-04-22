from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PreEvaluationJob(Base):
    __tablename__ = "pre_evaluation_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: f"pe-job-{uuid4().hex[:10]}")
    project_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    review_method: Mapped[dict | list] = mapped_column(JSON, nullable=False, default=dict)
    tech_review_table: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    starred_items: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
