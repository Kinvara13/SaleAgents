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
) -> list[TechnicalCase]:
    """根据评审项和关键词检索技术案例"""
    query = db.query(TechnicalCase).filter(
        TechnicalCase.project_id == project_id,
        TechnicalCase.status == "可用",
    )
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
    return query.order_by(TechnicalCase.score.desc()).all()