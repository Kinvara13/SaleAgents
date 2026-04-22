from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TechnicalCase(Base):
    """
    技术案例表
    存储可引用的技术案例素材，关联到评分体系的【一级评审项】+【二级评审项】
    """
    __tablename__ = "technical_cases"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    # 关联项目ID
    project_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    # 案例标题
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # 一级评审项（如"技术方案"、"实施方案"）
    primary_review_item: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    # 二级评审项（如"系统架构"、"功能完整性"）
    secondary_review_item: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    # 素材类型：项目案例/产品介绍/方案模板/行业报告等
    case_type: Mapped[str] = mapped_column(String(64), nullable=False, default="项目案例")
    # 适用场景标签（JSON数组）
    scene_tags: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # 关键词（JSON数组）
    keywords: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # 案例摘要/简介
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 合同名称
    contract_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    # 合同金额
    contract_amount: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    # 甲方名称
    client_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    # 合同内容概述
    contract_overview: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 关键技术亮点
    key_highlights: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 案例完整内容（富文本/JSON）
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 置信度评分（0-1）
    score: Mapped[str] = mapped_column(String(32), nullable=False, default="0.80")
    # 状态：可用/已引用/已过期
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="可用")
    # 来源
    source: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    # 视频URL（单独处理，不填入文档）
    video_url: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)