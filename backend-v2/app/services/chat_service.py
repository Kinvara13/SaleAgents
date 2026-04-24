from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.chat import ChatMessage, ChatContext
from app.models.project import Project
from app.services.llm_client import llm_generation_client


PROMPT_TEMPLATES = {
    "default": (
        "你是一位专业的招投标顾问，擅长帮助企业编写投标文件、技术建议书，"
        "分析招标文件，评估中标概率。请根据以下上下文信息，回答用户问题。\n\n"
        "【招标文件内容】\n{context}\n\n"
        "请始终以专业、严谨的态度回复，内容准确、可操作。"
    ),
    "tender": (
        "你是一位资深招投标专家。请基于以下【招标文件】内容回答用户问题。\n\n"
        "{context}\n\n"
        "回答要具体、可操作，引用文件中的具体条款。"
    ),
    "proposal": (
        "你是一位投标技术方案专家。请基于【招标文件】和【技术建议书背景】回答问题。\n\n"
        "招标文件：\n{context}\n\n"
        "请优化技术建议书内容，使其更具竞争力。"
    ),
}


def _system_prompt(context: str = "") -> str:
    return PROMPT_TEMPLATES["default"].format(context=context or "（暂无上下文）")


def _stream_tokens(response_text: str):
    """将回复文本按字符拆分为 SSE 流式 token。"""
    for char in response_text:
        yield f"data: {char}"
    yield "data: [DONE]"


def send_message(
    db: Session,
    project_id: str,
    message: str,
) -> tuple[str, list[str]]:
    """Send a user message and return (message_id, streamed_tokens)."""
    _ensure_project(db, project_id)

    user_msg = ChatMessage(
        id=f"msg_{uuid4().hex[:12]}",
        project_id=project_id,
        role="user",
        content=message,
    )
    db.add(user_msg)

    history = _get_history(db, project_id)
    context = _get_context_text(db, project_id)

    # Build system prompt
    system_content = _system_prompt(context)

    # Build user prompt with recent history
    history_text = _build_history_text(history[-6:])  # 最近 6 轮
    user_prompt = f"{history_text}\n\n用户当前问题：{message}"

    # Call LLM for real response
    response_text = _generate_llm_response(system_content, user_prompt)
    if not response_text:
        response_text = "抱歉，当前 AI 服务未配置或暂时不可用。请检查系统设置中的 AI 配置，或稍后重试。"

    assistant_msg = ChatMessage(
        id=f"msg_{uuid4().hex[:12]}",
        project_id=project_id,
        role="assistant",
        content=response_text,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg.id, list(_stream_tokens(response_text))


def _generate_llm_response(system_prompt: str, user_prompt: str) -> str:
    """调用 LLM 生成真实回复。"""
    try:
        result = llm_generation_client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=2048,
        )
        return result or ""
    except Exception:
        return ""


def _build_history_text(history: list[ChatMessage]) -> str:
    """将历史消息拼接成文本。"""
    if not history:
        return ""
    lines = []
    for msg in history:
        role = "用户" if msg.role == "user" else "助手"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


def get_history(db: Session, project_id: str) -> list[dict]:
    _ensure_project(db, project_id)
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.project_id == project_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


def _get_history(db: Session, project_id: str) -> list[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.project_id == project_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def inject_context(
    db: Session,
    project_id: str,
    context_type: str,
    content: str,
) -> ChatContext:
    """Inject context into the project for future chat sessions."""
    _ensure_project(db, project_id)
    ctx = ChatContext(
        id=f"ctx_{uuid4().hex[:12]}",
        project_id=project_id,
        context_type=context_type,
        content=content,
    )
    db.add(ctx)
    db.commit()
    db.refresh(ctx)
    return ctx


def _ensure_project(db: Session, project_id: str) -> None:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")


def _get_context_text(db: Session, project_id: str) -> str:
    contexts = (
        db.query(ChatContext)
        .filter(ChatContext.project_id == project_id)
        .order_by(ChatContext.created_at.desc())
        .all()
    )
    if not contexts:
        return ""
    return "\n\n".join(c.content for c in contexts)


def clear_history(db: Session, project_id: str) -> None:
    """Clear all chat messages for a project."""
    db.query(ChatMessage).filter(ChatMessage.project_id == project_id).delete()
    db.commit()
