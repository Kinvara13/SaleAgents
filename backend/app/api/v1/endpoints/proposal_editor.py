# sale-agents-v2: proposal editor module (skeleton)
# TODO: implement business logic
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()


@router.get("/{proposal_id}", status_code=status.HTTP_200_OK)
def get_proposal(proposal_id: str, db: Session = Depends(get_db)) -> dict:
    """
    获取应答文件详情。

    Path params:
        proposal_id: 应答文件 ID

    Response (TBD):
        proposal content, sections, metadata
    """
    # TODO: implement get proposal logic
    raise NotImplementedError("get proposal not yet implemented")


@router.put("/{proposal_id}", status_code=status.HTTP_200_OK)
def update_proposal(proposal_id: str, db: Session = Depends(get_db)) -> dict:
    """
    更新应答文件。

    Path params:
        proposal_id: 应答文件 ID

    Request body (TBD):
        updated sections, content, metadata

    Response (TBD):
        updated proposal
    """
    # TODO: implement update proposal logic
    raise NotImplementedError("update proposal not yet implemented")
