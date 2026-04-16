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
    api_key: str = ""
    model: str
    protocol: str = "openai"

class LLMProviderResponse(BaseModel):
    id: str
    name: str
    base_url: str
    api_key_masked: str
    model: str
    protocol: str
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
        protocol=getattr(provider, "protocol", "openai"),
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
        protocol=provider.protocol,
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
    if provider.api_key and not provider.api_key.endswith("****"):
        db_provider.api_key = provider.api_key
    db_provider.model = provider.model
    db_provider.protocol = provider.protocol
    
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

    db.query(LLMProviderModel).update({"is_active": False})

    db_provider.is_active = True
    db.commit()

    return {"ok": True, "active_provider_id": provider_id}


class LLMTestRequest(BaseModel):
    id: str | None = None
    base_url: str
    api_key: str
    model: str
    protocol: str = "openai"

class LLMTestResponse(BaseModel):
    success: bool
    message: str
    response_time_ms: int | None = None
    model_used: str | None = None

@router.post("/test", response_model=LLMTestResponse)
def test_provider(provider: LLMTestRequest, db: Session = Depends(get_db)):
    import time
    from fastapi import HTTPException
    
    actual_api_key = provider.api_key
    if provider.id and (not actual_api_key or actual_api_key.endswith("****")):
        db_provider = db.query(LLMProviderModel).filter(LLMProviderModel.id == provider.id).first()
        if db_provider:
            actual_api_key = db_provider.api_key
        else:
            raise HTTPException(status_code=404, detail="Provider not found, cannot get api key")

    start = time.time()
    
    if provider.protocol == "anthropic":
        try:
            import httpx
            headers = {
                "x-api-key": actual_api_key.strip(),
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            url = provider.base_url.strip() or "https://api.anthropic.com/v1"
            if not url.endswith("/messages"):
                url = url.rstrip("/") + "/messages"
                
            payload = {
                "model": provider.model.strip(),
                "max_tokens": 100,
                "messages": [
                    {"role": "user", "content": "你好，请用一句话自我介绍。"}
                ]
            }
            response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
            elapsed = int((time.time() - start) * 1000)
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [{}])[0].get("text", "")
                return LLMTestResponse(
                    success=True,
                    message=f"连接成功！模型返回：{content[:200]}",
                    response_time_ms=elapsed,
                    model_used=data.get("model", provider.model)
                )
            else:
                return LLMTestResponse(
                    success=False,
                    message=f"连接失败 (HTTP {response.status_code}): {response.text[:300]}",
                    response_time_ms=elapsed,
                )
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            return LLMTestResponse(
                success=False,
                message=f"连接失败：{str(e)[:300]}",
                response_time_ms=elapsed,
            )
            
    else: # openai default
        try:
            from openai import OpenAI
        except ImportError:
            raise HTTPException(status_code=500, detail="openai package not installed")

        client = OpenAI(
            api_key=actual_api_key.strip(),
            base_url=(provider.base_url.strip() or None),
            timeout=30.0,
        )

        try:
            response = client.chat.completions.create(
                model=provider.model.strip(),
                messages=[
                    {"role": "system", "content": "你是一个人工智能助手，请用一句话自我介绍。"},
                    {"role": "user", "content": "你好"},
                ],
                max_tokens=100,
                temperature=0.7,
            )
            elapsed = int((time.time() - start) * 1000)
            content = response.choices[0].message.content or ""
            return LLMTestResponse(
                success=True,
                message=f"连接成功！模型返回：{content[:200]}",
                response_time_ms=elapsed,
                model_used=response.model,
            )
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            return LLMTestResponse(
                success=False,
                message=f"连接失败：{str(e)[:300]}",
                response_time_ms=elapsed,
            )
