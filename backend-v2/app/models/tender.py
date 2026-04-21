from datetime import datetime

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Tender(Base):
    """招标信息表"""
    __tablename__ = "tenders"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    source_url: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    publish_date: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    deadline: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    amount: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    project_type: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 状态: pending(待处理) / bid(已投标) / reject(不投标)
    decision: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    reject_reason: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    # 关联的投标项目ID（当 decision=bid 时关联到 projects.id）
    project_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, default="user-001")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
