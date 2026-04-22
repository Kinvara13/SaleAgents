from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.settings import AIConfig, Material, Rule
from app.schemas.settings import AIConfigResponse, MaterialResponse, RuleResponse


def get_ai_config(db: Session) -> AIConfig | None:
    cfg = db.query(AIConfig).filter(AIConfig.is_active == True).first()
    return cfg


def update_ai_config(db: Session, provider: str, api_key: str, base_url: str, model: str, temperature: float, max_tokens: int) -> AIConfig:
    cfg = db.query(AIConfig).filter(AIConfig.is_active == True).first()
    if cfg:
        cfg.provider = provider
        cfg.api_key = api_key
        cfg.base_url = base_url
        cfg.model = model
        cfg.temperature = temperature
        cfg.max_tokens = max_tokens
    else:
        cfg = AIConfig(
            id=f"aicfg_{uuid4().hex[:12]}",
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=str(temperature),
            max_tokens=max_tokens,
            is_active=True,
        )
        db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


# ---- AI Config Management (List) ----

def list_ai_configs(db: Session) -> list[AIConfig]:
    return db.query(AIConfig).order_by(AIConfig.updated_at.desc()).all()


def create_ai_config(
    db: Session,
    name: str,
    provider: str,
    api_key: str,
    base_url: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> AIConfig:
    cfg = AIConfig(
        id=f"aicfg_{uuid4().hex[:12]}",
        name=name,
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=str(temperature),
        max_tokens=max_tokens,
        is_active=False,
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


def update_ai_config_by_id(
    db: Session,
    config_id: str,
    name: str | None = None,
    provider: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> AIConfig | None:
    cfg = db.query(AIConfig).filter(AIConfig.id == config_id).first()
    if not cfg:
        return None
    if name is not None:
        cfg.name = name
    if provider is not None:
        cfg.provider = provider
    if api_key is not None:
        cfg.api_key = api_key
    if base_url is not None:
        cfg.base_url = base_url
    if model is not None:
        cfg.model = model
    if temperature is not None:
        cfg.temperature = str(temperature)
    if max_tokens is not None:
        cfg.max_tokens = max_tokens
    db.commit()
    db.refresh(cfg)
    return cfg


def delete_ai_config(db: Session, config_id: str) -> bool:
    cfg = db.query(AIConfig).filter(AIConfig.id == config_id).first()
    if not cfg:
        return False
    db.delete(cfg)
    db.commit()
    return True


def activate_ai_config(db: Session, config_id: str) -> AIConfig | None:
    cfg = db.query(AIConfig).filter(AIConfig.id == config_id).first()
    if not cfg:
        return None
    # Deactivate all others
    db.query(AIConfig).update({AIConfig.is_active: False})
    cfg.is_active = True
    db.commit()
    db.refresh(cfg)
    return cfg


# ---- Materials ----

def list_materials(db: Session) -> list[Material]:
    return db.query(Material).order_by(Material.created_at.desc()).all()


def create_material(db: Session, name: str, material_type: str, file_path: str, description: str) -> Material:
    mat = Material(
        id=f"mat_{uuid4().hex[:12]}",
        name=name,
        material_type=material_type,
        file_path=file_path,
        description=description,
    )
    db.add(mat)
    db.commit()
    db.refresh(mat)
    return mat


def delete_material(db: Session, material_id: str) -> bool:
    mat = db.query(Material).filter(Material.id == material_id).first()
    if mat:
        db.delete(mat)
        db.commit()
        return True
    return False


# ---- Rules ----

def list_rules(db: Session) -> list[Rule]:
    return db.query(Rule).order_by(Rule.created_at.desc()).all()


def create_rule(db: Session, name: str, rule_type: str, content: str) -> Rule:
    rule = Rule(
        id=f"rule_{uuid4().hex[:12]}",
        name=name,
        rule_type=rule_type,
        content=content,
        is_active=True,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def delete_rule(db: Session, rule_id: str) -> bool:
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if rule:
        db.delete(rule)
        db.commit()
        return True
    return False
