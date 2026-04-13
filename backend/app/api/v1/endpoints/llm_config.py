import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

CONFIG_FILE = Path(__file__).resolve().parents[3] / "llm_providers.json"


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


class LLMConfigResponse(BaseModel):
    providers: list[LLMProviderResponse]
    active_provider_id: str | None


def _load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"providers": [], "active_provider_id": None}


def _save_config(data: dict) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _mask_key(key: str) -> str:
    if len(key) <= 8:
        return "****"
    return key[:4] + "****" + key[-4:]


def _to_response(provider: dict) -> LLMProviderResponse:
    return LLMProviderResponse(
        id=provider["id"],
        name=provider["name"],
        base_url=provider["base_url"],
        api_key_masked=_mask_key(provider["api_key"]),
        model=provider["model"],
    )


@router.get("", response_model=LLMConfigResponse)
def list_providers():
    data = _load_config()
    return LLMConfigResponse(
        providers=[_to_response(p) for p in data.get("providers", [])],
        active_provider_id=data.get("active_provider_id"),
    )


@router.post("", response_model=LLMProviderResponse)
def add_provider(provider: LLMProvider):
    data = _load_config()
    providers = data.get("providers", [])

    import uuid
    new_id = provider.id or str(uuid.uuid4())[:8]
    new_provider = {
        "id": new_id,
        "name": provider.name,
        "base_url": provider.base_url,
        "api_key": provider.api_key,
        "model": provider.model,
    }

    providers.append(new_provider)
    data["providers"] = providers

    if not data.get("active_provider_id"):
        data["active_provider_id"] = new_id

    _save_config(data)
    return _to_response(new_provider)


@router.put("/{provider_id}", response_model=LLMProviderResponse)
def update_provider(provider_id: str, provider: LLMProvider):
    data = _load_config()
    providers = data.get("providers", [])

    for i, p in enumerate(providers):
        if p["id"] == provider_id:
            providers[i] = {
                "id": provider_id,
                "name": provider.name,
                "base_url": provider.base_url,
                "api_key": provider.api_key,
                "model": provider.model,
            }
            _save_config(data)
            return _to_response(providers[i])

    raise HTTPException(status_code=404, detail="Provider not found")


@router.delete("/{provider_id}")
def delete_provider(provider_id: str):
    data = _load_config()
    providers = data.get("providers", [])
    data["providers"] = [p for p in providers if p["id"] != provider_id]

    if data.get("active_provider_id") == provider_id:
        data["active_provider_id"] = data["providers"][0]["id"] if data["providers"] else None

    _save_config(data)
    return {"ok": True}


@router.post("/activate/{provider_id}")
def activate_provider(provider_id: str):
    data = _load_config()
    providers = data.get("providers", [])

    if not any(p["id"] == provider_id for p in providers):
        raise HTTPException(status_code=404, detail="Provider not found")

    data["active_provider_id"] = provider_id
    _save_config(data)
    return {"ok": True, "active_provider_id": provider_id}
