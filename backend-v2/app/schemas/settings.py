from pydantic import BaseModel


class AIConfigResponse(BaseModel):
    id: str | None = None
    provider: str = "zhipu"
    api_key: str = ""
    base_url: str = ""
    model: str = "glm-4"
    temperature: float = 0.7
    max_tokens: int = 4096


class AIConfigUpdateRequest(BaseModel):
    provider: str = "zhipu"
    api_key: str = ""
    base_url: str = ""
    model: str = "glm-4"
    temperature: float = 0.7
    max_tokens: int = 4096


class MaterialResponse(BaseModel):
    id: str
    name: str
    material_type: str
    description: str
    created_at: str


class RuleResponse(BaseModel):
    id: str
    name: str
    rule_type: str
    content: str
    is_active: bool


class RuleCreateRequest(BaseModel):
    name: str
    rule_type: str = "general"
    content: str = ""
