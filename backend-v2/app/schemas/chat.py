from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    content: str


class ChatContextRequest(BaseModel):
    context_type: str  # tender_document / scoring / material
    content: str


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str
