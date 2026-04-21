# sale-agents-v2: proposal editor module
# 应答文件（技术建议书）编辑器模块
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Any

from app.db.session import get_db

router = APIRouter()


# ============ Request/Response Schemas ============

class ProposalSection(BaseModel):
    """标书章节"""
    id: str
    title: str
    content: str = ""
    order: int = 0


class ProposalMetadata(BaseModel):
    """元数据"""
    project_id: str | None = None
    tender_id: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    status: str = "草稿"
    author: str = ""


class ProposalResponse(BaseModel):
    """应答文件响应"""
    id: str
    title: str = ""
    content: str = ""
    sections: list[ProposalSection] = []
    metadata: ProposalMetadata = Field(default_factory=ProposalMetadata)
    star_items: list[dict] = []  # 星标项列表
    star_responses: dict[str, dict] = {}  # 星标项应答内容


class ProposalUpdateRequest(BaseModel):
    """更新应答文件请求"""
    title: str | None = None
    content: str | None = None
    sections: list[ProposalSection] | None = None
    metadata: ProposalMetadata | None = None
    star_items: list[dict] | None = None
    star_responses: dict[str, dict] | None = None


class StarItemConfirmRequest(BaseModel):
    """星标项确认请求"""
    satisfied: bool


class StarItemConfirmResponse(BaseModel):
    """星标项确认响应"""
    name: str
    source: str
    satisfied: bool | None = None
    section: str = ""
    content: str = ""


# ============ 内存存储（实际项目中应使用数据库） ============

# 模拟提案数据存储
_proposals_store: dict[str, dict] = {
    "demo-proposal-1": {
        "id": "demo-proposal-1",
        "title": "某城市智能交通系统建设项目技术建议书",
        "content": "",
        "sections": [
            {"id": "s1", "title": "1. 项目理解", "content": "", "order": 1},
            {"id": "s2", "title": "2. 技术方案", "content": "", "order": 2},
            {"id": "s3", "title": "3. 项目实施计划", "content": "", "order": 3},
            {"id": "s4", "title": "4. 质量保障", "content": "", "order": 4},
            {"id": "s5", "title": "5. 售后服务", "content": "", "order": 5},
        ],
        "metadata": {
            "project_id": "proj-1",
            "tender_id": "tender-1",
            "status": "草稿",
            "author": ""
        },
        "star_items": [
            {"name": "项目理解完整性", "source": "招标文件 P12", "satisfied": None},
            {"name": "技术方案先进性", "source": "招标文件 P15", "satisfied": None},
            {"name": "实施计划可行性", "source": "招标文件 P18", "satisfied": None},
            {"name": "案例证明材料", "source": "招标文件 P20", "satisfied": None},
            {"name": "售后服务响应时间", "source": "招标文件 P25", "satisfied": None},
        ],
        "star_responses": {}
    }
}

# 当前活跃提案ID
_current_proposal_id: str | None = None


# ============ API Routes ============

@router.get("/{proposal_id}", response_model=ProposalResponse)
def get_proposal(
    proposal_id: str,
    db: Session = Depends(get_db)
) -> ProposalResponse:
    """
    获取应答文件详情
    
    Path params:
        proposal_id: 应答文件 ID
    """
    global _current_proposal_id
    _current_proposal_id = proposal_id
    
    # 查找存储的提案
    if proposal_id in _proposals_store:
        data = _proposals_store[proposal_id]
        return ProposalResponse(
            id=data["id"],
            title=data.get("title", ""),
            content=data.get("content", ""),
            sections=[ProposalSection(**s) for s in data.get("sections", [])],
            metadata=ProposalMetadata(**data.get("metadata", {})),
            star_items=data.get("star_items", []),
            star_responses=data.get("star_responses", {})
        )
    
    # 如果不存在，返回默认模板
    return ProposalResponse(
        id=proposal_id,
        title="技术建议书",
        content="",
        sections=[
            {"id": "s1", "title": "1. 项目理解", "content": "", "order": 1},
            {"id": "s2", "title": "2. 技术方案", "content": "", "order": 2},
            {"id": "s3", "title": "3. 项目实施计划", "content": "", "order": 3},
            {"id": "s4", "title": "4. 质量保障", "content": "", "order": 4},
            {"id": "s5", "title": "5. 售后服务", "content": "", "order": 5},
        ],
        metadata=ProposalMetadata(status="草稿"),
        star_items=[],
        star_responses={}
    )


@router.put("/{proposal_id}", response_model=ProposalResponse)
def update_proposal(
    proposal_id: str,
    payload: ProposalUpdateRequest,
    db: Session = Depends(get_db)
) -> ProposalResponse:
    """
    更新应答文件
    
    Path params:
        proposal_id: 应答文件 ID
    
    Request body:
        title: 文档标题
        content: 文档内容
        sections: 章节列表
        metadata: 元数据
        star_items: 星标项列表
        star_responses: 星标项应答内容
    """
    global _proposals_store
    
    # 获取现有数据或创建新数据
    if proposal_id in _proposals_store:
        data = _proposals_store[proposal_id]
    else:
        data = {
            "id": proposal_id,
            "title": "",
            "content": "",
            "sections": [],
            "metadata": {},
            "star_items": [],
            "star_responses": {}
        }
    
    # 更新字段
    if payload.title is not None:
        data["title"] = payload.title
    if payload.content is not None:
        data["content"] = payload.content
    if payload.sections is not None:
        data["sections"] = [s.model_dump() for s in payload.sections]
    if payload.metadata is not None:
        data["metadata"] = payload.metadata.model_dump()
    if payload.star_items is not None:
        data["star_items"] = payload.star_items
    if payload.star_responses is not None:
        data["star_responses"] = payload.star_responses
    
    # 保存
    _proposals_store[proposal_id] = data
    
    return ProposalResponse(
        id=data["id"],
        title=data.get("title", ""),
        content=data.get("content", ""),
        sections=[ProposalSection(**s) for s in data.get("sections", [])],
        metadata=ProposalMetadata(**data.get("metadata", {})),
        star_items=data.get("star_items", []),
        star_responses=data.get("star_responses", {})
    )


@router.post("/{proposal_id}/star-items/{item_name}/confirm", response_model=StarItemConfirmResponse)
def confirm_star_item(
    proposal_id: str,
    item_name: str,
    payload: StarItemConfirmRequest,
    db: Session = Depends(get_db)
) -> StarItemConfirmResponse:
    """
    确认星标项满足状态
    
    Path params:
        proposal_id: 应答文件 ID
        item_name: 星标项名称
    """
    if proposal_id not in _proposals_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"提案 {proposal_id} 不存在"
        )
    
    data = _proposals_store[proposal_id]
    star_items = data.get("star_items", [])
    
    # 查找并更新星标项
    found = False
    for item in star_items:
        if item.get("name") == item_name:
            item["satisfied"] = payload.satisfied
            found = True
            break
    
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"星标项 '{item_name}' 不存在"
        )
    
    # 获取应答内容
    star_responses = data.get("star_responses", {})
    response_data = star_responses.get(item_name, {})
    
    return StarItemConfirmResponse(
        name=item_name,
        source=next((item.get("source", "") for item in star_items if item.get("name") == item_name), ""),
        satisfied=payload.satisfied,
        section=response_data.get("section", ""),
        content=response_data.get("content", "")
    )


@router.get("/{proposal_id}/star-items", response_model=list[StarItemConfirmResponse])
def list_star_items(
    proposal_id: str,
    db: Session = Depends(get_db)
) -> list[StarItemConfirmResponse]:
    """
    获取星标项列表
    """
    if proposal_id not in _proposals_store:
        return []
    
    data = _proposals_store[proposal_id]
    star_items = data.get("star_items", [])
    star_responses = data.get("star_responses", {})
    
    result = []
    for item in star_items:
        response_data = star_responses.get(item.get("name", ""), {})
        result.append(StarItemConfirmResponse(
            name=item.get("name", ""),
            source=item.get("source", ""),
            satisfied=item.get("satisfied"),
            section=response_data.get("section", ""),
            content=response_data.get("content", "")
        ))
    
    return result


@router.post("/{proposal_id}/sections/{section_id}/content", response_model=ProposalSection)
def update_section_content(
    proposal_id: str,
    section_id: str,
    content: str,
    db: Session = Depends(get_db)
) -> ProposalSection:
    """
    更新章节内容
    """
    if proposal_id not in _proposals_store:
        _proposals_store[proposal_id] = {
            "id": proposal_id,
            "title": "",
            "content": "",
            "sections": [],
            "metadata": {},
            "star_items": [],
            "star_responses": {}
        }
    
    data = _proposals_store[proposal_id]
    sections = data.get("sections", [])
    
    # 查找章节
    found = False
    for section in sections:
        if section.get("id") == section_id:
            section["content"] = content
            found = True
            return ProposalSection(**section)
    
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"章节 {section_id} 不存在"
        )
    
    return ProposalSection(**sections[0])
