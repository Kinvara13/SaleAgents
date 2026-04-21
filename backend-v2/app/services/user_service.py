from uuid import uuid4
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserSummary, UserDetail, UserCreateRequest, UserUpdateRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def list_users(db: Session) -> list[UserSummary]:
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserSummary.model_validate(u) for u in users]


def get_user(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, payload: UserCreateRequest) -> UserSummary:
    if get_user_by_username(db, payload.username):
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    user = User(
        id=f"user_{uuid4().hex[:12]}",
        username=payload.username,
        password_hash=pwd_context.hash(payload.password),
        name=payload.name or payload.username,
        role=payload.role or "executor",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserSummary.model_validate(user)


def update_user(db: Session, user_id: str, payload: UserUpdateRequest) -> UserSummary:
    user = get_user(db, user_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "is_active" in update_data:
        user.is_active = update_data["is_active"]
    if "role" in update_data:
        user.role = update_data["role"]
    if "name" in update_data:
        user.name = update_data["name"]
    db.commit()
    db.refresh(user)
    return UserSummary.model_validate(user)


def delete_user(db: Session, user_id: str) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()


ROLES = [
    {
        "id": "admin",
        "name": "管理员",
        "permissions": [
            "projects:read", "projects:write", "projects:delete",
            "parsing:read", "parsing:write",
            "proposal:read", "proposal:write",
            "chat:read", "chat:write",
            "users:read", "users:write", "users:delete",
            "settings:read", "settings:write",
            "rules:read", "rules:write",
        ],
    },
    {
        "id": "project_owner",
        "name": "项目负责人",
        "permissions": [
            "projects:read", "projects:write",
            "parsing:read", "parsing:write",
            "proposal:read", "proposal:write",
            "chat:read", "chat:write",
            "users:read",
        ],
    },
    {
        "id": "executor",
        "name": "执行人员",
        "permissions": [
            "projects:read",
            "parsing:read",
            "chat:read", "chat:write",
        ],
    },
    {
        "id": "reviewer",
        "name": "审核人员",
        "permissions": [
            "projects:read",
            "proposal:read",
            "chat:read",
        ],
    },
]


def list_roles() -> list[dict]:
    return ROLES
