from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class KnowledgeAssetWorkflowRecord(Base):
    __tablename__ = "knowledge_asset_workflows"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    asset_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, unique=True)
    owner: Mapped[str] = mapped_column(String(128), nullable=False, default="system")
    visibility: Mapped[str] = mapped_column(String(32), nullable=False, default="internal")
    review_status: Mapped[str] = mapped_column(String(32), nullable=False, default="approved")
    reviewer: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    review_note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
