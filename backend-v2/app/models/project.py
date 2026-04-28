from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="待决策")
    owner: Mapped[str] = mapped_column(String(128), nullable=False, default="admin")
    client: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    deadline: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    amount: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    risk: Mapped[str] = mapped_column(String(16), nullable=False, default="P2")
    bidding_company: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    agent_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    agent_phone: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    agent_email: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    company_address: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    bank_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    bank_account: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    description: Mapped[str] = mapped_column(String(2000), nullable=False, default="")
    confirm_status: Mapped[str] = mapped_column(String(32), nullable=False, default="待确认")
    confirm_feedback: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    confirmed_by: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    confirmed_at: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, default="user-001")
    tender_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    parse_status: Mapped[str] = mapped_column(String(32), nullable=False, default="未上传")
    file_list: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    node_status: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=dict)
    extracted_fields: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    bid_template_files: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
