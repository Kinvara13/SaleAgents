from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProjectAssetPreferenceRecord(Base):
    __tablename__ = "project_asset_preferences"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    asset_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    preference_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="fixed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
