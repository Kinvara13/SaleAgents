from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from pathlib import Path
from uuid import uuid4
import zipfile, os, shutil, logging

from app.db.session import get_db
from app.models.project import Project
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_TEMPLATE_EXTENSIONS = {".zip", ".rar", ".7z", ".docx", ".doc", ".pdf"}
MAX_TEMPLATE_SIZE = 50 * 1024 * 1024


def _decode_zip_filename(name: str) -> str:
    try:
        name.encode('utf-8')
        return name
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    try:
        if isinstance(name, bytes):
            return name.decode('gbk')
        return name.encode('cp437').decode('gbk')
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass
    return name.encode('utf-8', errors='replace').decode('utf-8', errors='replace')


@router.post("/{project_id}/upload-template")
async def upload_bid_template(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict:
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_TEMPLATE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(ALLOWED_TEMPLATE_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > MAX_TEMPLATE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小超过50MB限制")

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

    upload_dir = Path(settings.storage_path or Path(__file__).resolve().parents[4] / "storage") / "projects" / project_id / "bid_templates"
    upload_dir.mkdir(parents=True, exist_ok=True)

    template_path = upload_dir / filename
    with open(template_path, "wb") as f:
        f.write(content)

    bid_files: list[dict] = []

    if ext == ".zip":
        extract_dir = upload_dir / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)

        def extract_and_list(zip_path: Path, target_dir: Path, depth: int = 0) -> None:
            if depth > 3:
                return
            target_dir.mkdir(parents=True, exist_ok=True)
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    for info in zf.infolist():
                        decoded_name = _decode_zip_filename(info.filename)
                        if decoded_name.startswith("__MACOSX/") or decoded_name.startswith("."):
                            continue
                        target_path = target_dir / decoded_name
                        if info.is_dir():
                            target_path.mkdir(parents=True, exist_ok=True)
                            continue
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(info) as src, open(target_path, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        if target_path.suffix.lower() == ".zip":
                            nested_dir = target_path.parent / target_path.stem
                            try:
                                extract_and_list(target_path, nested_dir, depth + 1)
                                target_path.unlink(missing_ok=True)
                            except Exception:
                                pass
            except zipfile.BadZipFile:
                logger.error(f"Bad ZIP file: {zip_path}")
                raise

        extract_and_list(template_path, extract_dir)

        for root, dirs, files in os.walk(extract_dir):
            for fname in files:
                decoded_name = _decode_zip_filename(fname)
                ext = Path(decoded_name).suffix.lower()
                if ext in {".docx", ".doc", ".pdf", ".txt"}:
                    rel_path = os.path.relpath(os.path.join(root, decoded_name), extract_dir)
                    bid_files.append({
                        "id": f"tpl_{uuid4().hex[:8]}",
                        "name": decoded_name,
                        "path": rel_path,
                        "status": "待分配",
                        "selected": True,
                        "icon": "📄",
                    })

        shutil.rmtree(extract_dir, ignore_errors=True)

    elif ext in {".docx", ".doc"}:
        bid_files.append({
            "id": f"tpl_{uuid4().hex[:8]}",
            "name": filename,
            "path": filename,
            "status": "待分配",
            "selected": True,
            "icon": "📄",
        })

    project.bid_template_files = bid_files
    db.commit()

    return {
        "status": "success",
        "message": "模板上传成功",
        "filename": filename,
        "files": bid_files,
    }
