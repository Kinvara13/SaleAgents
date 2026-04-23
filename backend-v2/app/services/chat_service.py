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


def _mock_stream(response_text: str):
    """Yield tokens one by one for SSE streaming simulation."""
    # 将回复按字符拆分，模拟流式输出
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

    return assistant_msg.id, list(_mock_stream(response_text))


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


def _generate_response(message: str, history: list[ChatMessage], context: str) -> str:
    """Generate a mock AI response based on the message content."""
    msg = message.strip()

    if any(kw in msg for kw in ["你好", "您好", "hi", "hello"]):
        return "您好！我是您的投标 AI 助手。请问有什么可以帮您的？无论是招标文件解读、技术方案优化还是评分策略，我都可以为您提供专业建议。"

    if any(kw in msg for kw in ["技术建议书", "建议书", "技术方案"]):
        return ("根据招标文件中关于技术方案的要求，建议从以下几个方面优化：\n"
                "1. 突出公司核心技术优势和类似项目经验\n"
                "2. 量化技术指标，便于评审专家打分\n"
                "3. 增加项目风险管理方案，展示执行能力\n"
                "4. 确保技术方案与招标评分标准完全对应\n\n"
                "如需我帮您起草某一章节的具体内容，请告诉我章节名称和核心要求。")

    if any(kw in msg for kw in ["商务", "偏离表", "偏离"]):
        return ("商务偏离表需要仔细核对招标文件的每一项商务条款。\n"
                "建议：\n"
                "1. 逐条阅读招标文件商务部分\n"
                "2. 对于完全满足的条款，填写「无偏离」\n"
                "3. 对于有差异的条款，简要说明偏离内容及原因\n"
                "4. 保持表述专业，避免暴露过多劣势\n\n"
                "请问您目前商务部分遇到的具体问题是什么？")

    if any(kw in msg for kw in ["评分", "得分", "分数", "中标"]):
        return ("投标评分通常分为技术分和商务分两部分。\n"
                "建议策略：\n"
                "1. 先确保满足招标文件的实质性要求（必须项）\n"
                "2. 技术分：重点展示CMMI认证、项目案例、核心人员资质\n"
                "3. 商务分：报价策略、付款方式、维保承诺\n"
                "4. 避免极端报价，建议选择性价比最优方案\n\n"
                "如需我帮您分析具体的评分表，请上传评分标准文件。")

    if any(kw in msg for kw in ["上传", "文件", "解析"]):
        return ("好的，我已准备好接收您的招标文件。\n"
                "请上传招标文件（PDF/DOC格式），我将帮您：\n"
                "1. 解析招标文件的结构和大纲\n"
                "2. 识别关键商务条款和技术要求\n"
                "3. 标注需要重点关注的星标项\n"
                "4. 生成初步的投标大纲\n\n"
                "请问您要上传哪个文件？")

    if any(kw in msg for kw in ["CMMI", "证书", "资质", "认证"]):
        return ("CMMI证书和各类资质是技术评分的重要组成部分。\n"
                "建议：\n"
                "1. 在技术建议书中明确列出公司持有的CMMI等级证书\n"
                "2. 附上计算机软件著作权证书清单\n"
                "3. 提供项目经理及核心人员的资质证书\n"
                "4. 如有获奖案例，也请一并整理展示\n\n"
                "请问您目前有哪些资质材料需要整理？")

    # Default response
    return ("感谢您的提问！您的需求我已经理解。\n"
            "为了给出更准确的内容，建议您：\n"
            "1. 在「标书拆分」中上传招标文件\n"
            "2. 在「技术建议书」中让AI生成初稿\n"
            "3. 再针对具体章节与我对话优化\n\n"
            "请问还有什么可以帮您？")


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
