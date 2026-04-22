from datetime import datetime

from sqlalchemy import DateTime, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ParsingSection(Base):
    __tablename__ = "parsing_sections"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id"), nullable=False)
    section_name: Mapped[str] = mapped_column(String(255), nullable=False)
    section_type: Mapped[str] = mapped_column(String(16), nullable=False)  # 商务 / 技术
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_star_item: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    source_file: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
