from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.knowledge_asset import KnowledgeAssetRecord

router = APIRouter()


@router.get("/knowledge-assets")
def list_knowledge_assets(
    asset_type: str | None = None,
    limit: int = 20,
    db: Session = Depends(get_db),
) -> list[dict]:
    query = db.query(KnowledgeAssetRecord)
    if asset_type:
        query = query.filter(KnowledgeAssetRecord.asset_type == asset_type)
    assets = query.order_by(KnowledgeAssetRecord.created_at.desc()).limit(limit).all()
    return [
        {
            "id": a.id,
            "title": a.title,
            "asset_type": a.asset_type,
            "score": a.score,
            "status": a.status,
            "summary": a.summary,
        }
        for a in assets
    ]
