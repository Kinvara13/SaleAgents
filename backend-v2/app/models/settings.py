from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AIConfig(Base):
    __tablename__ = "ai_configs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, default="未命名配置")
    provider: Mapped[str] = mapped_column(String(32), nullable=False, default="zhipu")
    api_key: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    base_url: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    model: Mapped[str] = mapped_column(String(64), nullable=False, default="glm-4")
    temperature: Mapped[str] = mapped_column(String(16), nullable=False, default="0.7")
    max_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=4096)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    # 素材分类: cmmi / soft_copy / project_experience / personnel_capability / certificate / other
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="other")
    # 细分类标签，JSON 数组
    tags: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # 素材文本内容（用于匹配和填充）
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 原始文件路径
    file_path: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    # 素材描述
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    # 关联公司/组织
    organization: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    # 获取日期
    acquired_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    # 有效期至
    valid_until: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    # 是否激活
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # 元数据（额外字段）
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    # 保留旧字段以兼容
    material_type: Mapped[str] = mapped_column(String(64), nullable=False, default="general")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Rule(Base):
    __tablename__ = "rules"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(32), nullable=False, default="general")
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
