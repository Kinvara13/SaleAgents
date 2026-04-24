from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialSummary,
    MaterialDetail,
)
from app.services import material_service

router = APIRouter()


@router.get("/", response_model=list[MaterialSummary])
def list_materials(
    category: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[MaterialSummary]:
    return material_service.list_materials(
        db, category=category, tag=tag, search=search, is_active=is_active, skip=skip, limit=limit
    )


@router.post("/", response_model=MaterialDetail)
def create_material(
    payload: MaterialCreate,
    db: Session = Depends(get_db),
) -> MaterialDetail:
    return MaterialDetail.model_validate(material_service.create_material(db, payload))


@router.get("/{material_id}", response_model=MaterialDetail)
def get_material(
    material_id: str,
    db: Session = Depends(get_db),
) -> MaterialDetail:
    return MaterialDetail.model_validate(material_service.get_material(db, material_id))


@router.patch("/{material_id}", response_model=MaterialDetail)
def update_material(
    material_id: str,
    payload: MaterialUpdate,
    db: Session = Depends(get_db),
) -> MaterialDetail:
    return MaterialDetail.model_validate(material_service.update_material(db, material_id, payload))


@router.delete("/{material_id}")
def delete_material(
    material_id: str,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    material_service.delete_material(db, material_id)
    return {"message": "素材已删除"}
