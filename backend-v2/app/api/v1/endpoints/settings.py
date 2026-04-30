from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from pydantic import BaseModel
from app.schemas.settings import (
    AIConfigResponse, AIConfigUpdateRequest, AIConfigCreateRequest,
    AIConfigTestResponse,
    MaterialResponse, RuleResponse, RuleCreateRequest,
)
from app.services import settings_service

router = APIRouter()


# ---- Legacy single-config endpoints (keep for backward compat) ----

@router.get("/ai-config", response_model=AIConfigResponse)
def get_ai_config(db: Session = Depends(get_db)) -> AIConfigResponse:
    cfg = settings_service.get_ai_config(db)
    if cfg:
        return AIConfigResponse(
            id=cfg.id,
            name=cfg.name,
            provider=cfg.provider,
            api_key=cfg.api_key,
            base_url=cfg.base_url,
            model=cfg.model,
            temperature=float(cfg.temperature),
            max_tokens=cfg.max_tokens,
            is_active=cfg.is_active,
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
        name=cfg.name,
        provider=cfg.provider,
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        model=cfg.model,
        temperature=float(cfg.temperature),
        max_tokens=cfg.max_tokens,
        is_active=cfg.is_active,
    )


# ---- AI Config Management (List) ----

@router.get("/ai-configs", response_model=list[AIConfigResponse])
def get_ai_configs(db: Session = Depends(get_db)) -> list[AIConfigResponse]:
    configs = settings_service.list_ai_configs(db)
    return [
        AIConfigResponse(
            id=c.id,
            name=c.name,
            provider=c.provider,
            api_key=c.api_key,
            base_url=c.base_url,
            model=c.model,
            temperature=float(c.temperature),
            max_tokens=c.max_tokens,
            is_active=c.is_active,
        )
        for c in configs
    ]


@router.post("/ai-configs", response_model=AIConfigResponse, status_code=201)
def create_ai_config(
    payload: AIConfigCreateRequest,
    db: Session = Depends(get_db),
) -> AIConfigResponse:
    cfg = settings_service.create_ai_config(
        db,
        name=payload.name,
        provider=payload.provider,
        api_key=payload.api_key,
        base_url=payload.base_url,
        model=payload.model,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )
    return AIConfigResponse(
        id=cfg.id,
        name=cfg.name,
        provider=cfg.provider,
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        model=cfg.model,
        temperature=float(cfg.temperature),
        max_tokens=cfg.max_tokens,
        is_active=cfg.is_active,
    )


@router.patch("/ai-configs/{config_id}", response_model=AIConfigResponse)
def patch_ai_config_by_id(
    config_id: str,
    payload: AIConfigUpdateRequest,
    db: Session = Depends(get_db),
) -> AIConfigResponse:
    cfg = settings_service.update_ai_config_by_id(
        db, config_id,
        name=payload.name,
        provider=payload.provider,
        api_key=payload.api_key,
        base_url=payload.base_url,
        model=payload.model,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )
    if not cfg:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    return AIConfigResponse(
        id=cfg.id,
        name=cfg.name,
        provider=cfg.provider,
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        model=cfg.model,
        temperature=float(cfg.temperature),
        max_tokens=cfg.max_tokens,
        is_active=cfg.is_active,
    )


@router.delete("/ai-configs/{config_id}", status_code=204)
def delete_ai_config(config_id: str, db: Session = Depends(get_db)) -> None:
    ok = settings_service.delete_ai_config(db, config_id)
    if not ok:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")


@router.post("/ai-configs/{config_id}/activate", response_model=AIConfigResponse)
def activate_ai_config(config_id: str, db: Session = Depends(get_db)) -> AIConfigResponse:
    cfg = settings_service.activate_ai_config(db, config_id)
    if not cfg:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    return AIConfigResponse(
        id=cfg.id,
        name=cfg.name,
        provider=cfg.provider,
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        model=cfg.model,
        temperature=float(cfg.temperature),
        max_tokens=cfg.max_tokens,
        is_active=cfg.is_active,
    )


@router.post("/ai-configs/{config_id}/test", response_model=AIConfigTestResponse)
def test_ai_config(config_id: str, db: Session = Depends(get_db)) -> AIConfigTestResponse:
    cfg = settings_service.get_ai_config_by_id(db, config_id)
    if not cfg:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")
    if not cfg.api_key:
        return AIConfigTestResponse(success=False, message="API Key 未配置")

    import time

    start = time.time()
    try:
        if cfg.provider == "anthropic":
            import httpx
            base_url = (cfg.base_url or "https://api.anthropic.com/v1").rstrip("/") + "/messages"
            resp = httpx.post(
                base_url,
                headers={
                    "x-api-key": cfg.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": cfg.model,
                    "max_tokens": 20,
                    "messages": [{"role": "user", "content": "请回复：测试成功"}],
                },
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()
            latency = int((time.time() - start) * 1000)
            content = data.get("content", [{}])[0].get("text", "")
            return AIConfigTestResponse(
                success=True,
                message=f"连接正常，响应：{content[:50]}",
                model_used=data.get("model", cfg.model),
                latency_ms=latency,
            )
        else:
            from openai import OpenAI
            client = OpenAI(
                api_key=cfg.api_key,
                base_url=cfg.base_url or None,
                timeout=30.0,
            )
            resp = client.chat.completions.create(
                model=cfg.model,
                messages=[{"role": "user", "content": "请回复：测试成功"}],
                max_tokens=20,
            )
            latency = int((time.time() - start) * 1000)
            content = resp.choices[0].message.content or ""
            return AIConfigTestResponse(
                success=True,
                message=f"连接正常，响应：{content[:50]}",
                model_used=resp.model or cfg.model,
                latency_ms=latency,
            )
    except Exception as e:
        latency = int((time.time() - start) * 1000)
        err_msg = str(e)
        if "403" in err_msg or "access_terminated" in err_msg:
            err_msg = "API Key 无权访问该模型（403）"
        elif "401" in err_msg:
            err_msg = "API Key 无效（401）"
        elif "404" in err_msg:
            err_msg = "模型不存在（404）"
        elif "Connection" in err_msg:
            err_msg = "无法连接到 API 服务器"
        return AIConfigTestResponse(
            success=False,
            message=err_msg,
            latency_ms=latency,
        )


# ---- Materials ----

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
    from pathlib import Path
    from app.core.config import settings
    storage_dir = Path(settings.storage_path or Path(__file__).resolve().parents[4] / "storage") / "materials"
    storage_dir.mkdir(parents=True, exist_ok=True)
    file_id = f"mat_{uuid.uuid4().hex[:12]}"
    ext = os.path.splitext(file.filename or "")[1] or ""
    file_path = str(storage_dir / f"{file_id}{ext}")
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


@router.delete("/materials/{material_id}", status_code=204)
def delete_material(material_id: str, db: Session = Depends(get_db)) -> None:
    ok = settings_service.delete_material(db, material_id)
    if not ok:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material not found")


# ---- Rules ----

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


@router.delete("/rules/{rule_id}", status_code=204)
def delete_rule(rule_id: str, db: Session = Depends(get_db)) -> None:
    ok = settings_service.delete_rule(db, rule_id)
    if not ok:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
