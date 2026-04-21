from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import jwt
import bcrypt

from app.core.config import settings

router = APIRouter()

security = HTTPBearer(auto_error=False)

# 预计算的 bcrypt hash（admin / admin123），避免启动时重新 hash 导致 bcrypt 版本兼容问题
_ADMIN_HASH = "$2b$12$v36nO8OF1VKUJuPWItLr5eCPneBE8X8uN64L9PPeRn8D.lDKcLWvG"


# 简单硬编码用户（开发/演示用）
_USERS = {
    "admin": {
        "id": "user-001",
        "username": "admin",
        "password_hash": _ADMIN_HASH,
        "role": "admin",
        "name": "管理员",
    },
}


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


def _create_token(data: dict, expires_delta: timedelta, token_type: str = "access") -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


def _decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    id: str
    username: str
    name: str
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> UserInfoResponse:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = _decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        username: str = payload.get("sub", "")
        user = _USERS.get(username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return UserInfoResponse(
            id=user["id"],
            username=user["username"],
            name=user["name"],
            role=user["role"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    user = _USERS.get(payload.username)
    if not user or not _verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = _create_token(
        {"sub": user["username"]},
        timedelta(minutes=settings.access_token_expire_minutes),
        token_type="access",
    )
    refresh_token = _create_token(
        {"sub": user["username"]},
        timedelta(days=settings.refresh_token_expire_days),
        token_type="refresh",
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest) -> TokenResponse:
    try:
        decoded = _decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        username: str = decoded.get("sub", "")
        user = _USERS.get(username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        access_token = _create_token(
            {"sub": user["username"]},
            timedelta(minutes=settings.access_token_expire_minutes),
            token_type="access",
        )
        refresh_token = _create_token(
            {"sub": user["username"]},
            timedelta(days=settings.refresh_token_expire_days),
            token_type="refresh",
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


@router.get("/me", response_model=UserInfoResponse)
def me(current_user: UserInfoResponse = Depends(get_current_user)) -> UserInfoResponse:
    return current_user