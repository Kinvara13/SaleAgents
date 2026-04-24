from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class MaterialBase(BaseModel):
    name: str
    category: str = Field(default="other")
    tags: list[str] = Field(default_factory=list)
    content: str = Field(default="")
    file_path: str = Field(default="")
    description: str = Field(default="")
    organization: str = Field(default="")
    acquired_date: str = Field(default="")
    valid_until: str = Field(default="")
    is_active: bool = Field(default=True)
    metadata_json: dict = Field(default_factory=dict)


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    content: str | None = None
    file_path: str | None = None
    description: str | None = None
    organization: str | None = None
    acquired_date: str | None = None
    valid_until: str | None = None
    is_active: bool | None = None
    metadata_json: dict | None = None


class MaterialSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    tags: str  # JSON string from DB
    description: str
    is_active: bool
    created_at: datetime


class MaterialDetail(MaterialBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    material_type: str = Field(default="general")  # backward compat
    created_at: datetime
    updated_at: datetime
