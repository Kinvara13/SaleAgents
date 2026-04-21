from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserSummary, UserDetail, UserCreateRequest, UserUpdateRequest
from app.services import user_service

router = APIRouter()


@router.get("", response_model=list[UserSummary])
def get_users(db: Session = Depends(get_db)) -> list[UserSummary]:
    return user_service.list_users(db)


@router.post("", response_model=UserSummary, status_code=status.HTTP_201_CREATED)
def post_user(payload: UserCreateRequest, db: Session = Depends(get_db)) -> UserSummary:
    return user_service.create_user(db, payload)


@router.get("/{user_id}", response_model=UserDetail)
def get_user(user_id: str, db: Session = Depends(get_db)) -> UserDetail:
    user = user_service.get_user(db, user_id)
    return UserDetail(
        id=user.id,
        username=user.username,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
    )


@router.patch("/{user_id}", response_model=UserSummary)
def patch_user(
    user_id: str,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db),
) -> UserSummary:
    return user_service.update_user(db, user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db)) -> None:
    user_service.delete_user(db, user_id)


@router.get("/roles/list")
def get_roles() -> list[dict]:
    return user_service.list_roles()
