from datetime import datetime

from sqlalchemy import DateTime, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BusinessDocument(Base):
    __tablename__ = "business_documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id"), nullable=False)
    # 文档类型标识，对应功能点编号如 deviation（商务偏离表）、commitment（应答承诺函）等
    doc_type: Mapped[str] = mapped_column(String(64), nullable=False)
    # 文档中文名称
    doc_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # 原始文件内容/模板内容
    original_content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 可编辑内容（用户填写后的内容）
    editable_content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 是否有可填写字段
    has_fillable_fields: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # 是否为星标项
    is_star_item: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # 打分点说明
    score_point: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    # 规则说明
    rule_description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 状态：pending / filled / confirmed
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    # 关联的回标文件清单（JSON字符串数组）
    return_file_list: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # 来源文件
    source_file: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
