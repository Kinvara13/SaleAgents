import json
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.technical_case import TechnicalCase


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _safe_json(value: str) -> str:
    """确保值是合法的 JSON 字符串"""
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, str):
        try:
            json.loads(value)
            return value
        except Exception:
            return json.dumps(value, ensure_ascii=False)
    return json.dumps(str(value), ensure_ascii=False)


# 技术文档类型 → 案例匹配策略映射
DOC_TYPE_CASE_MAPPING: dict[str, dict] = {
    "tech_overview": {
        "case_types": ["项目案例", "技术方案"],
        "scene_tags": ["技术方案", "系统架构", "整体解决方案"],
        "keywords": ["技术", "方案", "架构", "系统"],
    },
    "cmmi_cert": {
        "case_types": ["资质认证"],
        "scene_tags": ["CMMI", "软件能力成熟度", "资质"],
        "keywords": ["CMMI", "认证", "软件能力", "成熟度"],
    },
    "software_copyright": {
        "case_types": ["知识产权"],
        "scene_tags": ["软件著作权", "知识产权", "自主研发"],
        "keywords": ["软件著作权", "知识产权", "软著", "著作权"],
    },
    "project_strength": {
        "case_types": ["项目案例"],
        "scene_tags": ["项目业绩", "同类项目", "合同", "案例"],
        "keywords": ["项目", "案例", "合同", "业绩", "客户"],
    },
    "service_commitment": {
        "case_types": ["服务承诺", "项目案例"],
        "scene_tags": ["SLA", "服务", "维保", "响应时间"],
        "keywords": ["服务", "承诺", "SLA", "维保", "响应"],
    },
    "additional_content": {
        "case_types": ["项目案例", "技术方案"],
        "scene_tags": ["技术亮点", "创新", "团队", "核心能力"],
        "keywords": ["技术", "亮点", "创新", "团队", "能力"],
    },
}

# 不需要案例的文档类型
NO_CASE_DOC_TYPES = {"tech_deviation", "compliance_check", "tech_cover"}


def list_technical_cases(db: Session, project_id: str) -> list[TechnicalCase]:
    """获取项目的技术案例列表"""
    return (
        db.query(TechnicalCase)
        .filter(TechnicalCase.project_id == project_id)
        .order_by(TechnicalCase.created_at.desc())
        .all()
    )


def get_technical_case_detail(db: Session, project_id: str, case_id: str) -> TechnicalCase:
    """获取技术案例详情"""
    case = (
        db.query(TechnicalCase)
        .filter(TechnicalCase.id == case_id, TechnicalCase.project_id == project_id)
        .first()
    )
    if not case:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Technical case not found")
    return case


def create_technical_case(db: Session, payload: dict) -> TechnicalCase:
    """创建技术案例"""
    case = TechnicalCase(
        id=str(uuid.uuid4()),
        project_id=payload.get("project_id", ""),
        title=payload.get("title", ""),
        primary_review_item=payload.get("primary_review_item", ""),
        secondary_review_item=payload.get("secondary_review_item", ""),
        case_type=payload.get("case_type", "项目案例"),
        scene_tags=_safe_json(payload.get("scene_tags", [])),
        keywords=_safe_json(payload.get("keywords", [])),
        summary=payload.get("summary", ""),
        contract_name=payload.get("contract_name", ""),
        contract_amount=payload.get("contract_amount", ""),
        client_name=payload.get("client_name", ""),
        contract_overview=payload.get("contract_overview", ""),
        key_highlights=payload.get("key_highlights", ""),
        content=payload.get("content", ""),
        source=payload.get("source", ""),
        status="可用",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def update_technical_case(db: Session, project_id: str, case_id: str, payload: dict) -> TechnicalCase:
    """更新技术案例"""
    case = (
        db.query(TechnicalCase)
        .filter(TechnicalCase.id == case_id, TechnicalCase.project_id == project_id)
        .first()
    )
    if not case:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Technical case not found")

    update_fields = [
        "title", "primary_review_item", "secondary_review_item", "case_type",
        "summary", "contract_name", "contract_amount", "client_name",
        "contract_overview", "key_highlights", "content", "status", "source", "video_url",
    ]
    for field in update_fields:
        if field in payload and payload[field] is not None:
            setattr(case, field, payload[field])

    # JSON 字段特殊处理
    if "scene_tags" in payload and payload["scene_tags"] is not None:
        case.scene_tags = _safe_json(payload["scene_tags"])
    if "keywords" in payload and payload["keywords"] is not None:
        case.keywords = _safe_json(payload["keywords"])

    case.updated_at = _utcnow()
    db.commit()
    db.refresh(case)
    return case


def delete_technical_case(db: Session, project_id: str, case_id: str) -> bool:
    """删除技术案例"""
    case = (
        db.query(TechnicalCase)
        .filter(TechnicalCase.id == case_id, TechnicalCase.project_id == project_id)
        .first()
    )
    if not case:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Technical case not found")
    db.delete(case)
    db.commit()
    return True


def search_technical_cases(
    db: Session,
    project_id: str,
    primary_item: str = "",
    secondary_item: str = "",
    keyword: str = "",
    doc_type: str = "",
    limit: int = 5,
    scope: str = "project",
) -> list[TechnicalCase]:
    """
    根据文档类型和关键词智能检索技术案例

    匹配优先级：
    1. doc_type 映射 → case_type + scene_tags + keywords
    2. primary_review_item / secondary_review_item 精确匹配
    3. keyword 关键词模糊匹配（title / keywords / summary）
    """
    if doc_type in NO_CASE_DOC_TYPES:
        return []

    query = db.query(TechnicalCase).filter(
        TechnicalCase.status == "可用",
    )

    if scope == "project" and project_id:
        query = query.filter(TechnicalCase.project_id == project_id)

    mapping = DOC_TYPE_CASE_MAPPING.get(doc_type)
    if mapping:
        from sqlalchemy import or_
        conditions: list = []
        for ct in mapping["case_types"]:
            conditions.append(TechnicalCase.case_type == ct)
        for tag in mapping["scene_tags"]:
            conditions.append(TechnicalCase.scene_tags.contains(tag))
        for kw in mapping["keywords"]:
            conditions.append(TechnicalCase.keywords.contains(kw))
        if keyword:
            conditions.append(TechnicalCase.title.contains(keyword))
        if conditions:
            query = query.filter(or_(*conditions))
    else:
        if primary_item:
            query = query.filter(TechnicalCase.primary_review_item == primary_item)
        if secondary_item:
            query = query.filter(TechnicalCase.secondary_review_item == secondary_item)
        if keyword:
            query = query.filter(
                (TechnicalCase.title.contains(keyword))
                | (TechnicalCase.keywords.contains(keyword))
                | (TechnicalCase.summary.contains(keyword))
            )

    return query.order_by(TechnicalCase.score.desc()).limit(limit).all()