from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project_document_version import ProjectDocumentVersion
from app.services.object_storage import object_storage_service

router = APIRouter()

@router.get('/{project_id}/document')
def get_project_document_file(project_id: str, db: Session = Depends(get_db)):
    version = (
        db.query(ProjectDocumentVersion)
        .filter(ProjectDocumentVersion.project_id == project_id)
        .order_by(ProjectDocumentVersion.created_at.desc())
        .first()
    )
    
    if not version or not version.object_key:
        raise HTTPException(status_code=404, detail='Document not found')
        
    try:
        file_bytes = object_storage_service.read_bytes(version.object_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    content_type = 'application/pdf' if version.file_type == 'pdf' else 'application/octet-stream'
    
    return Response(
        content=file_bytes, 
        media_type=content_type,
        headers={'Content-Disposition': f'inline; filename="{version.file_name}"'}
    )
