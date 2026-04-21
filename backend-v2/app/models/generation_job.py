from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    project_name: Mapped[str] = mapped_column(String(255), default="")
    template_name: Mapped[str] = mapped_column(String(128), default="标准回标模板")
    status: Mapped[str] = mapped_column(String(32), default="completed")
    section_count: Mapped[int] = mapped_column(Integer, default=0)
    overall_progress: Mapped[str] = mapped_column(String(32), default="已生成")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
