import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatMessageRequest, ChatContextRequest
from app.services import chat_service

router = APIRouter()


@router.post("/{project_id}/message")
def post_message(
    project_id: str,
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Send a message and stream AI response (SSE)."""
    _, tokens = chat_service.send_message(db, project_id, payload.content)

    def stream():
        for token in tokens:
            if token.startswith("data: [DONE]"):
                yield "data: [DONE]\n\n"
                break
            yield f"{token}\n\n"
            import time
            time.sleep(0.02)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{project_id}/history")
def get_history(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[dict]:
    return chat_service.get_history(db, project_id)


@router.post("/{project_id}/context")
def inject_context(
    project_id: str,
    payload: ChatContextRequest,
    db: Session = Depends(get_db),
):
    """Inject context (tender document, scoring rules, material) into chat."""
    ctx = chat_service.inject_context(db, project_id, payload.context_type, payload.content)
    return {"id": ctx.id, "context_type": ctx.context_type, "created_at": ctx.created_at.isoformat()}


@router.delete("/{project_id}/history")
def clear_history(
    project_id: str,
    db: Session = Depends(get_db),
):
    """Clear chat history for a project."""
    chat_service.clear_history(db, project_id)
    return {"message": "Chat history cleared"}
