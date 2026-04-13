import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.llm_provider import LLMProviderModel

router = APIRouter()

class LLMProvider(BaseModel):
    id: str | None = None
    name: str
    base_url: str
    api_key: str
    model: str

class LLMProviderResponse(BaseModel):
    id: str
    name: str
    base_url: str
    api_key_masked: str
    model: str
    is_active: bool

class LLMConfigResponse(BaseModel):
    providers: list[LLMProviderResponse]
    active_provider_id: str | None

def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "****"
    return key[:4] + "****" + key[-4:]

def _to_response(provider: LLMProviderModel) -> LLMProviderResponse:
    return LLMProviderResponse(
        id=provider.id,
        name=provider.name,
        base_url=provider.base_url,
        api_key_masked=_mask_key(provider.api_key),
        model=provider.model,
        is_active=provider.is_active,
    )

@router.get("", response_model=LLMConfigResponse)
def list_providers(db: Session = Depends(get_db)):
    providers = db.query(LLMProviderModel).order_by(LLMProviderModel.created_at.asc()).all()
    active_provider = next((p for p in providers if p.is_active), None)
    return LLMConfigResponse(
        providers=[_to_response(p) for p in providers],
        active_provider_id=active_provider.id if active_provider else None,
    )

@router.post("", response_model=LLMProviderResponse)
def add_provider(provider: LLMProvider, db: Session = Depends(get_db)):
    new_id = provider.id or str(uuid.uuid4())[:8]
    
    # If this is the first provider, make it active
    is_first = db.query(LLMProviderModel).count() == 0
    
    db_provider = LLMProviderModel(
        id=new_id,
        name=provider.name,
        base_url=provider.base_url,
        api_key=provider.api_key,
        model=provider.model,
        is_active=is_first
    )
    
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    
    return _to_response(db_provider)

@router.put("/{provider_id}", response_model=LLMProviderResponse)
def update_provider(provider_id: str, provider: LLMProvider, db: Session = Depends(get_db)):
    db_provider = db.query(LLMProviderModel).filter(LLMProviderModel.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    db_provider.name = provider.name
    db_provider.base_url = provider.base_url
    db_provider.api_key = provider.api_key
    db_provider.model = provider.model
    
    db.commit()
    db.refresh(db_provider)
    
    return _to_response(db_provider)

@router.delete("/{provider_id}")
def delete_provider(provider_id: str, db: Session = Depends(get_db)):
    db_provider = db.query(LLMProviderModel).filter(LLMProviderModel.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    was_active = db_provider.is_active
    db.delete(db_provider)
    
    if was_active:
        first_provider = db.query(LLMProviderModel).first()
        if first_provider:
            first_provider.is_active = True
            
    db.commit()
    return {"ok": True}

@router.post("/activate/{provider_id}")
def activate_provider(provider_id: str, db: Session = Depends(get_db)):
    db_provider = db.query(LLMProviderModel).filter(LLMProviderModel.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="Provider not found")
        
    # Deactivate all others
    db.query(LLMProviderModel).update({"is_active": False})
    
    # Activate the selected one
    db_provider.is_active = True
    db.commit()
    
    return {"ok": True, "active_provider_id": provider_id}
