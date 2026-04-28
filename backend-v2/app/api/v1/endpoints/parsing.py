from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import zipfile, tempfile, os, shutil, logging

from app.db.session import get_db

logger = logging.getLogger(__name__)
from app.schemas.parsing import ParsingSectionSummary, ParsingSectionDetail, ParsingSectionUpdateRequest
from app.schemas.task import TaskSubmitResponse
from app.services.parsing_service import parsing_service
from app.services.task_service import create_task, update_task_status
from app.models.parsing_section import ParsingSection
from app.models.project import Project
from app.core.config import settings

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx", ".zip"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
UNZIP_DIR = Path(settings.storage_path or Path(__file__).resolve().parents[4] / "storage") / "unzip_temp"


def _decode_zip_filename(name: str) -> str:
    """Decode ZIP filename with Chinese encoding fallback.
    
    Python's zipfile uses CP437 by default for non-UTF-8 flag entries.
    Chinese tools (WinRAR, 360压缩) on Windows may use GBK encoding instead.
    """
    try:
        # If it's already valid UTF-8, return as-is
        name.encode('utf-8')
        return name
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    # Try GBK encoding (Chinese Windows default)
    try:
        if isinstance(name, bytes):
            return name.decode('gbk')
        return name.encode('cp437').decode('gbk')
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass

    # Try GB2312
    try:
        if isinstance(name, bytes):
            return name.decode('gb2312')
        return name.encode('cp437').decode('gb2312')
    except (UnicodeDecodeError, UnicodeEncodeError):
        pass

    # Fallback: replace invalid chars
    return name.encode('utf-8', errors='replace').decode('utf-8', errors='replace')


@router.post("/{project_id}/upload", response_model=TaskSubmitResponse)
async def upload_and_parse(
    project_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> TaskSubmitResponse:
    filename = file.filename or "unknown"
    ext = Path(filename).suffix.lower()
    file_size = 0

    content = await file.read()
    file_size = len(content)
    logger.info(f"[UPLOAD] project_id={project_id}, filename={filename}, ext={ext}, size={file_size}")

    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"[UPLOAD] Rejected: unsupported extension {ext}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    if file_size > MAX_FILE_SIZE:
        logger.warning(f"[UPLOAD] Rejected: file too large {file_size}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小超过100MB限制")

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        logger.warning(f"[UPLOAD] Project not found: {project_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

    # 创建异步任务记录
    task = create_task(db, task_type="document_parsing", project_id=project_id)

    upload_dir = Path(settings.storage_path or Path(__file__).resolve().parents[4] / "storage") / "projects" / project_id / "bid_documents"
    upload_dir.mkdir(parents=True, exist_ok=True)

    if ext == ".zip":
        # Handle ZIP archive
        zip_path = upload_dir / filename
        with open(zip_path, "wb") as f:
            f.write(content)
        background_tasks.add_task(_handle_zip_async, project_id, zip_path, task.id)
    else:
        # Handle single file
        file_path = upload_dir / filename
        with open(file_path, "wb") as f:
            f.write(content)
        background_tasks.add_task(_parse_single_file_async, project_id, file_path, filename, task.id)

    return TaskSubmitResponse(
        task_id=task.id,
        status="processing",
        message="文件已接收，后台解析任务已启动",
    )

def _handle_zip_async(project_id: str, zip_path: Path, task_id: str):
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        logger.info(f"[ZIP_PARSE] Start: project_id={project_id}, zip_path={zip_path}, task_id={task_id}")
        update_task_status(db, task_id, "processing")

        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "解析中"
            project.parse_status = "解析中"
            if isinstance(project.node_status, dict):
                project.node_status["parsing"] = "processing"
            else:
                project.node_status = {"parsing": "processing"}
            db.commit()

        # Extract and parse each file, keeping the first one to clear existing sections
        first = True
        total_sections = 0
        total_files_found = 0
        total_files_parsed = 0
        skipped_files = []
        parsed_files = []

        extract_dir = UNZIP_DIR / project_id
        extract_dir.mkdir(parents=True, exist_ok=True)

        def extract_zip_recursive(zip_path: Path, target_dir: Path, depth: int = 0) -> None:
            if depth > 3:
                logger.warning(f"Max ZIP nesting depth reached at: {zip_path}")
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
                                extract_zip_recursive(target_path, nested_dir, depth + 1)
                                target_path.unlink(missing_ok=True)
                                logger.info(f"Recursively extracted nested ZIP: {decoded_name}")
                            except Exception as e:
                                logger.warning(f"Failed to extract nested ZIP {decoded_name}: {e}")
            except zipfile.BadZipFile as e:
                logger.error(f"Bad ZIP file: {zip_path} - {e}")
                raise

        extract_zip_recursive(zip_path, extract_dir)

        for root, dirs, files in os.walk(extract_dir):
            for fname in files:
                total_files_found += 1
                fpath = Path(root) / fname
                ext = fpath.suffix.lower()
                if ext not in ALLOWED_EXTENSIONS:
                    skipped_files.append(f"{fname} (unsupported extension: {ext})")
                    continue
                if ext == ".zip":
                    logger.info(f"Skipping residual ZIP file: {fname}")
                    skipped_files.append(f"{fname} (residual zip)")
                    continue
                # Skip small files and obvious attachments to speed up parsing
                file_size = fpath.stat().st_size if fpath.exists() else 0
                is_attachment = any(kw in fname.lower() for kw in ["附件", "证明", "证书", "资质", "执照", "授权", "承诺", "偏离", "格式", "模板", "样本"])
                if file_size < 10000 or is_attachment:
                    skipped_files.append(f"{fname} (attachment/small, skip LLM)")
                    continue
                try:
                    result = parsing_service.parse_document(
                        db, project_id, fpath, fname, clear_existing=first
                    )
                    total_sections += len(result)
                    total_files_parsed += 1
                    parsed_files.append({
                        "name": fname,
                        "path": str(fpath),
                        "uploaded_at": str(datetime.utcnow())
                    })
                    first = False
                except Exception as e:
                    logger.warning(f"Failed to parse {fname} in ZIP: {e}")

        logger.info(
            f"Zip extraction summary for project {project_id}: "
            f"found={total_files_found}, parsed={total_files_parsed}, skipped={len(skipped_files)}"
        )
        if skipped_files:
            for msg in skipped_files[:20]:  # Log first 20 skipped files
                logger.debug(f"Skipped file: {msg}")

        # Cleanup
        shutil.rmtree(UNZIP_DIR / project_id, ignore_errors=True)
        zip_path.unlink(missing_ok=True)

        if project:
            project.status = "解析完成"
            project.parse_status = "已解析"
            project.file_list = parsed_files
            if isinstance(project.node_status, dict):
                project.node_status["parsing"] = "completed"
            db.commit()

        update_task_status(db, task_id, "completed", result={"section_count": total_sections})
        logger.info(f"[ZIP_PARSE] Completed: project_id={project_id}, files_parsed={total_files_parsed}, sections={total_sections}")
    except Exception as e:
        logger.error(f"[ZIP_PARSE] Failed: project_id={project_id}, error={e}", exc_info=True)
        db.rollback()
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "解析失败"
            project.parse_status = "解析失败"
            if isinstance(project.node_status, dict):
                project.node_status["parsing"] = "failed"
            db.commit()
        update_task_status(db, task_id, "failed", error_message=str(e))
    finally:
        db.close()

def _parse_single_file_async(project_id: str, file_path: Path, filename: str, task_id: str | None = None):
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        if task_id:
            update_task_status(db, task_id, "processing")

        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "解析中"
            project.parse_status = "解析中"
            if isinstance(project.node_status, dict):
                project.node_status["parsing"] = "processing"
            else:
                project.node_status = {"parsing": "processing"}
            db.commit()

        sections = parsing_service.parse_document(db, project_id, file_path, filename)

        if project:
            project.status = "解析完成"
            project.parse_status = "已解析"
            if isinstance(project.node_status, dict):
                project.node_status["parsing"] = "completed"
            db.commit()

        if task_id:
            update_task_status(db, task_id, "completed", result={"section_count": len(sections)})
    except Exception as e:
        import logging
        logging.error(f"Single file parsing failed for project {project_id}: {e}")
        db.rollback()
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.status = "解析失败"
            project.parse_status = "解析失败"
            if isinstance(project.node_status, dict):
                project.node_status["parsing"] = "failed"
            db.commit()
        if task_id:
            update_task_status(db, task_id, "failed", error_message=str(e))
    finally:
        db.close()


@router.get("/{project_id}/sections", response_model=list[ParsingSectionSummary])
def get_sections(project_id: str, db: Session = Depends(get_db)) -> list[ParsingSectionSummary]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    sections = (
        db.query(ParsingSection)
        .filter(ParsingSection.project_id == project_id)
        .order_by(ParsingSection.section_type, ParsingSection.id)
        .all()
    )
    return [ParsingSectionSummary.model_validate(s) for s in sections]


@router.get("/{project_id}/sections/{section_id}", response_model=ParsingSectionDetail)
def get_section_detail(
    project_id: str,
    section_id: str,
    db: Session = Depends(get_db),
) -> ParsingSectionDetail:
    section = (
        db.query(ParsingSection)
        .filter(ParsingSection.id == section_id, ParsingSection.project_id == project_id)
        .first()
    )
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="章节不存在")
    return ParsingSectionDetail.model_validate(section)


@router.patch("/{project_id}/sections/{section_id}", response_model=ParsingSectionDetail)
def patch_section(
    project_id: str,
    section_id: str,
    payload: ParsingSectionUpdateRequest,
    db: Session = Depends(get_db),
) -> ParsingSectionDetail:
    section = (
        db.query(ParsingSection)
        .filter(ParsingSection.id == section_id, ParsingSection.project_id == project_id)
        .first()
    )
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="章节不存在")
    if payload.content is not None:
        section.content = payload.content
    db.commit()
    db.refresh(section)
    return ParsingSectionDetail.model_validate(section)
