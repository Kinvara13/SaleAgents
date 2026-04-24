import json
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.settings import Material
from app.schemas.material import MaterialCreate, MaterialUpdate


def list_materials(
    db: Session,
    *,
    category: str | None = None,
    tag: str | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Material]:
    query = db.query(Material)
    if category:
        query = query.filter(Material.category == category)
    if is_active is not None:
        query = query.filter(Material.is_active == is_active)
    if search:
        like = f"%{search}%"
        query = query.filter(
            Material.name.ilike(like) | Material.description.ilike(like) | Material.content.ilike(like)
        )
    if tag:
        # Simple JSON string containment check
        query = query.filter(Material.tags.contains(tag))
    return query.offset(skip).limit(limit).all()


def get_material(db: Session, material_id: str) -> Material:
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="素材不存在")
    return material


def create_material(db: Session, payload: MaterialCreate) -> Material:
    material = Material(
        id=str(uuid.uuid4()),
        name=payload.name,
        category=payload.category,
        tags=json.dumps(payload.tags, ensure_ascii=False),
        content=payload.content,
        file_path=payload.file_path,
        description=payload.description,
        organization=payload.organization,
        acquired_date=payload.acquired_date,
        valid_until=payload.valid_until,
        is_active=payload.is_active,
        metadata_json=json.dumps(payload.metadata_json, ensure_ascii=False),
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def update_material(db: Session, material_id: str, payload: MaterialUpdate) -> Material:
    material = get_material(db, material_id)
    update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
    if "tags" in update_data and update_data["tags"] is not None:
        update_data["tags"] = json.dumps(update_data["tags"], ensure_ascii=False)
    if "metadata_json" in update_data and update_data["metadata_json"] is not None:
        update_data["metadata_json"] = json.dumps(update_data["metadata_json"], ensure_ascii=False)
    for key, value in update_data.items():
        setattr(material, key, value)
    db.commit()
    db.refresh(material)
    return material


def delete_material(db: Session, material_id: str) -> None:
    material = get_material(db, material_id)
    db.delete(material)
    db.commit()
