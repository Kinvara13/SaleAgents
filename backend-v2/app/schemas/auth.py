# Re-export UserInfoResponse from auth endpoint for use in Depends type annotations
from app.api.v1.endpoints.auth import UserInfoResponse

__all__ = ["UserInfoResponse"]
