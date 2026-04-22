from pydantic import BaseModel, ConfigDict


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    name: str
    role: str
    is_active: bool


class UserDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    name: str
    role: str
    is_active: bool
    created_at: str


class UserCreateRequest(BaseModel):
    username: str
    password: str
    name: str = ""
    role: str = "executor"


class UserUpdateRequest(BaseModel):
    name: str | None = None
    role: str | None = None
    is_active: bool | None = None
