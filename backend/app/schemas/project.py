from pydantic import BaseModel, ConfigDict, Field


class ProjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: str
    owner: str
    client: str = ""
    deadline: str = ""
    amount: str = ""
    risk: str = ""
    module_progress: dict[str, str]


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    owner: str = Field(min_length=1, max_length=128)
    client: str = Field(default="", max_length=255)
    deadline: str = Field(default="", max_length=64)
    amount: str = Field(default="", max_length=64)
    risk: str = Field(default="P2", max_length=16)
    status: str = Field(default="待决策", max_length=64)


class ProjectUpdateRequest(BaseModel):
    status: str | None = Field(default=None, max_length=64)
