from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TenderFetchLog(Base):
    """招标信息抓取日志表"""
    __tablename__ = "tender_fetch_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 抓取任务名称
    task_name: Mapped[str] = mapped_column(String(128), nullable=False, default="default_fetch")
    # 抓取来源（如 gov.cn, zbytb.com 等）
    source: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    # 抓取状态: success / partial / failed / running
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="success")
    # 新增记录数
    new_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 更新记录数
    updated_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 错误信息
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 开始时间
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    # 结束时间
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    def duration_seconds(self) -> float | None:
        if self.ended_at and self.started_at:
            return (self.ended_at - self.started_at).total_seconds()
        return None
