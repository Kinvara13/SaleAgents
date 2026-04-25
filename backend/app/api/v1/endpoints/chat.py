import json
import logging
from typing import Generator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.llm_provider import LLMProviderModel

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatMessageRequest(BaseModel):
    content: str
    model: str | None = None


def _get_active_provider():
    try:
        with SessionLocal() as db:
            return db.query(LLMProviderModel).filter(LLMProviderModel.is_active == True).first()
    except Exception as e:
        logger.error("Error querying active LLM provider: %s", e)
        return None


def _chat_stream(message: str, model: str | None = None) -> Generator[str, None, None]:
    """Sync generator for SSE streaming."""
    provider = _get_active_provider()

    if provider:
        base_url = (provider.base_url or "").strip() or None
        api_key = (provider.api_key or "").strip()
        use_model = model or provider.model
        protocol = getattr(provider, "protocol", "openai")
    else:
        base_url = (settings.llm_base_url or "").strip() or None
        api_key = (settings.llm_api_key or "").strip()
        use_model = model or settings.llm_model
        protocol = "openai"

    if not api_key:
        yield f"data: {json.dumps({'error': 'LLM provider not configured'}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
        return

    if protocol == "anthropic":
        import httpx
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        url = base_url or "https://api.anthropic.com/v1"
        if not url.endswith("/messages"):
            url = url.rstrip("/") + "/messages"

        payload = {
            "model": use_model,
            "max_tokens": 2048,
            "temperature": 0.7,
            "system": "你是标书助手AI，帮助用户处理招投标相关工作。",
            "messages": [{"role": "user", "content": message}],
            "stream": True,
        }

        with httpx.Client(timeout=float(settings.llm_timeout_seconds)) as client:
            with client.stream("POST", url, headers=headers, json=payload) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk.get("type") == "content_block_delta":
                                text = chunk.get("delta", {}).get("text", "")
                                if text:
                                    yield f"data: {json.dumps({'content': text}, ensure_ascii=False)}\n\n"
                        except json.JSONDecodeError:
                            pass
    else:
        try:
            from openai import OpenAI
        except ImportError as exc:
            yield f"data: {json.dumps({'error': 'openai package not installed'}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=float(settings.llm_timeout_seconds),
        )

        stream = client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": "你是标书助手AI，帮助用户处理招投标相关工作。"},
                {"role": "user", "content": message},
            ],
            temperature=0.7,
            max_tokens=2048,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {json.dumps({'content': delta}, ensure_ascii=False)}\n\n"

    yield "data: [DONE]\n\n"


@router.post("/message")
def chat_message(request: ChatMessageRequest):
    return StreamingResponse(
        _chat_stream(request.content, request.model),
        media_type="text/event-stream",
    )


@router.post("/{project_id}/message")
def chat_project_message(project_id: str, request: ChatMessageRequest):
    # TODO: 加载项目上下文
    return StreamingResponse(
        _chat_stream(request.content, request.model),
        media_type="text/event-stream",
    )
