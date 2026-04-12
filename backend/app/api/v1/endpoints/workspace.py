from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.workspace import WorkspaceData
from app.services.workspace_service import get_workspace_data

router = APIRouter()


@router.get("", response_model=WorkspaceData)
def get_workspace(db: Session = Depends(get_db)) -> WorkspaceData:
    return get_workspace_data(db)
