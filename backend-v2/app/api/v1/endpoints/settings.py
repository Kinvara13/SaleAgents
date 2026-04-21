from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from pydantic import BaseModel
from app.schemas.settings import AIConfigResponse, AIConfigUpdateRequest, MaterialResponse, RuleResponse, RuleCreateRequest
from app.services import settings_service

router = APIRouter()


@router.get("/ai-config", response_model=AIConfigResponse)
def get_ai_config(db: Session = Depends(get_db)) -> AIConfigResponse:
    cfg = settings_service.get_ai_config(db)
    if cfg:
        return AIConfigResponse(
            id=cfg.id,
            provider=cfg.provider,
            api_key=cfg.api_key,
            base_url=cfg.base_url,
            model=cfg.model,
            temperature=float(cfg.temperature),
            max_tokens=cfg.max_tokens,
        )
    return AIConfigResponse()


@router.patch("/ai-config", response_model=AIConfigResponse)
def patch_ai_config(
    payload: AIConfigUpdateRequest,
    db: Session = Depends(get_db),
) -> AIConfigResponse:
    cfg = settings_service.update_ai_config(
        db,
        provider=payload.provider,
        api_key=payload.api_key,
        base_url=payload.base_url,
        model=payload.model,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )
    return AIConfigResponse(
        id=cfg.id,
        provider=cfg.provider,
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        model=cfg.model,
        temperature=float(cfg.temperature),
        max_tokens=cfg.max_tokens,
    )


@router.get("/materials", response_model=list[MaterialResponse])
def get_materials(db: Session = Depends(get_db)) -> list[MaterialResponse]:
    mats = settings_service.list_materials(db)
    return [
        MaterialResponse(
            id=m.id,
            name=m.name,
            material_type=m.material_type,
            description=m.description,
            created_at=m.created_at.isoformat(),
        )
        for m in mats
    ]


@router.post("/materials/upload", response_model=MaterialResponse)
async def upload_material(
    name: str,
    material_type: str = "general",
    description: str = "",
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> MaterialResponse:
    # Store file to storage directory
    import os, uuid
    storage_dir = "/Users/sen/SaleAgents/backendv2/storage/materials"
    os.makedirs(storage_dir, exist_ok=True)
    file_id = f"mat_{uuid.uuid4().hex[:12]}"
    ext = os.path.splitext(file.filename or "")[1] or ""
    file_path = f"{storage_dir}/{file_id}{ext}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    mat = settings_service.create_material(db, name, material_type, file_path, description)
    return MaterialResponse(
        id=mat.id,
        name=mat.name,
        material_type=mat.material_type,
        description=mat.description,
        created_at=mat.created_at.isoformat(),
    )


@router.get("/rules", response_model=list[RuleResponse])
def get_rules(db: Session = Depends(get_db)) -> list[RuleResponse]:
    rules = settings_service.list_rules(db)
    return [
        RuleResponse(
            id=r.id,
            name=r.name,
            rule_type=r.rule_type,
            content=r.content,
            is_active=r.is_active,
        )
        for r in rules
    ]


@router.post("/rules", response_model=RuleResponse, status_code=201)
def post_rule(
    payload: RuleCreateRequest,
    db: Session = Depends(get_db),
) -> RuleResponse:
    rule = settings_service.create_rule(db, payload.name, payload.rule_type, payload.content)
    return RuleResponse(
        id=rule.id,
        name=rule.name,
        rule_type=rule.rule_type,
        content=rule.content,
        is_active=rule.is_active,
    )
