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

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx", ".zip", ".rar"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
UNZIP_DIR = Path(settings.storage_path or Path(__file__).resolve().parents[4] / "storage") / "unzip_temp"


def _decode_zip_filename(name: str) -> str:
    """Decode ZIP filename with Chinese encoding fallback.

    Python's zipfile uses cp437 by default for non-UTF-8 flag entries.
    Chinese tools (WinRAR, 360压缩) on Windows use GBK encoding.
    We must try cp437 first (not latin-1) to recover original bytes.
    """
    if not isinstance(name, str):
        name = str(name)
    
    # If filename already contains Chinese characters, it's correctly decoded
    if any('\u4e00' <= c <= '\u9fff' for c in name):
        return name
    
    # Check if filename is already valid UTF-8 (modern ZIP files with UTF-8 flag)
    try:
        name.encode('utf-8')
        # If no replacement characters and looks normal, return as-is
        if '\ufffd' not in name and not any(ord(c) > 127 and c.isprintable() for c in name[:20]):
            return name
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    
    def score(candidate: str) -> int:
        chinese = sum(1 for c in candidate if '\u4e00' <= c <= '\u9fff')
        ascii_count = sum(1 for c in candidate if c.isascii() and c.isprintable())
        mojibake = sum(1 for c in candidate if c in "ÃÂÄÅÆÇÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿµ")
        replacement = candidate.count('\ufffd')
        return chinese * 10 + ascii_count - mojibake * 3 - replacement * 20

    candidates = [name]

    # Python's zipfile uses cp437 by default for non-UTF-8 entries.
    # We must try cp437 first (not latin-1) to recover original bytes.
    for source_enc in ('cp437', 'latin-1'):
        try:
            original_bytes = name.encode(source_enc)
            for target_enc in ('utf-8', 'gbk', 'gb18030', 'gb2312'):
                try:
                    decoded = original_bytes.decode(target_enc)
                    if decoded and decoded not in candidates:
                        candidates.append(decoded)
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    best = max(candidates, key=score)
    if best != name:
        logger.info("Decoded archive filename: %s -> %s", name, best)
    return best


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

    if ext == ".zip" or ext == ".rar":
        # Handle ZIP/RAR archive
        archive_path = upload_dir / filename
        with open(archive_path, "wb") as f:
            f.write(content)
        background_tasks.add_task(_handle_archive_async, project_id, archive_path, ext, task.id)
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

def _handle_archive_async(project_id: str, archive_path: Path, ext: str, task_id: str):
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        logger.info(f"[ARCHIVE_PARSE] Start: project_id={project_id}, archive_path={archive_path}, ext={ext}, task_id={task_id}")
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

        def extract_zip_recursive(zip_path: Path, target_dir: Path, depth: int = 0) -> list[Path]:
            """Recursively extract ZIP files and return list of extracted file paths."""
            extracted_files: list[Path] = []
            if depth > 5:
                logger.warning(f"Max ZIP nesting depth reached at: {zip_path}")
                return extracted_files
            target_dir.mkdir(parents=True, exist_ok=True)
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    for info in zf.infolist():
                        decoded_name = _decode_zip_filename(info.filename)
                        # Skip macOS metadata and hidden files
                        if decoded_name.startswith("__MACOSX/") or decoded_name.startswith(".") or "/." in decoded_name:
                            continue
                        target_path = target_dir / decoded_name
                        if info.is_dir():
                            target_path.mkdir(parents=True, exist_ok=True)
                            continue
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(info) as src, open(target_path, "wb") as dst:
                            shutil.copyfileobj(src, dst)
                        extracted_files.append(target_path)
                        # Recursively extract nested ZIPs
                        if target_path.suffix.lower() == ".zip":
                            nested_dir = target_path.parent / target_path.stem
                            try:
                                nested_files = extract_zip_recursive(target_path, nested_dir, depth + 1)
                                extracted_files.extend(nested_files)
                                # Remove the nested ZIP file after extraction
                                target_path.unlink(missing_ok=True)
                                logger.info(f"Recursively extracted nested ZIP: {decoded_name} ({len(nested_files)} files)")
                            except Exception as e:
                                logger.warning(f"Failed to extract nested ZIP {decoded_name}: {e}")
            except zipfile.BadZipFile as e:
                logger.error(f"Bad ZIP file: {zip_path} - {e}")
                raise
            return extracted_files

        def extract_rar_recursive(rar_path: Path, target_dir: Path, depth: int = 0) -> list[Path]:
            """Recursively extract RAR files and return list of extracted file paths."""
            extracted_files: list[Path] = []
            if depth > 5:
                logger.warning(f"Max RAR nesting depth reached at: {rar_path}")
                return extracted_files
            target_dir.mkdir(parents=True, exist_ok=True)
            
            extracted = False
            
            # Try patool first
            if not extracted:
                try:
                    import patoolib
                    patoolib.extract_archive(str(rar_path), outdir=str(target_dir))
                    extracted = True
                    logger.info(f"Extracted RAR using patool: {rar_path}")
                except Exception as e:
                    logger.warning(f"patool extraction failed: {e}")
            
            # Try subprocess with 7z
            if not extracted:
                try:
                    import subprocess
                    result = subprocess.run(
                        ['7z', 'x', f'-o{target_dir}', '-y', str(rar_path)],
                        capture_output=True, text=True, timeout=60
                    )
                    if result.returncode == 0:
                        extracted = True
                        logger.info(f"Extracted RAR using 7z: {rar_path}")
                    else:
                        logger.warning(f"7z extraction failed: {result.stderr[:200]}")
                except Exception as e:
                    logger.warning(f"7z extraction failed: {e}")
            
            if not extracted:
                raise RuntimeError(
                    f"无法解压RAR文件: {rar_path.name}。"
                    f"系统未安装 unrar/unar 工具。"
                    f"请将RAR文件转换为ZIP格式后重新上传，或联系管理员安装 unrar 工具。"
                )
            
            for root, dirs, files in os.walk(target_dir):
                for fname in files:
                    decoded_name = _decode_zip_filename(fname)
                    if decoded_name.startswith("__MACOSX/") or decoded_name.startswith(".") or "/." in decoded_name:
                        continue
                    target_path = Path(root) / decoded_name
                    extracted_files.append(target_path)
                    if target_path.suffix.lower() == ".rar":
                        nested_dir = target_path.parent / target_path.stem
                        try:
                            nested_files = extract_rar_recursive(target_path, nested_dir, depth + 1)
                            extracted_files.extend(nested_files)
                            target_path.unlink(missing_ok=True)
                            logger.info(f"Recursively extracted nested RAR: {decoded_name}")
                        except Exception as e:
                            logger.warning(f"Failed to extract nested RAR {decoded_name}: {e}")
            return extracted_files

        if ext == ".zip":
            all_extracted_files = extract_zip_recursive(archive_path, extract_dir)
        elif ext == ".rar":
            all_extracted_files = extract_rar_recursive(archive_path, extract_dir)
        else:
            raise ValueError(f"Unsupported archive type: {ext}")
        
        logger.info(f"Extracted {len(all_extracted_files)} files from {ext.upper()} archive")

        # Process all extracted files
        files_to_parse: list[tuple[Path, str]] = []
        for root, dirs, files in os.walk(extract_dir):
            for fname in files:
                total_files_found += 1
                fpath = Path(root) / fname
                ext = fpath.suffix.lower()
                
                # Check if it's a supported document type
                supported_docs = {".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx"}
                if ext not in supported_docs:
                    if ext == ".zip":
                        skipped_files.append(f"{fname} (residual zip)")
                    else:
                        skipped_files.append(f"{fname} (unsupported extension: {ext})")
                    continue
                
                # Skip small files and obvious attachments
                file_size = fpath.stat().st_size if fpath.exists() else 0
                is_attachment = any(kw in fname.lower() for kw in ["附件", "证明", "证书", "资质", "执照", "授权", "承诺", "偏离", "格式", "模板", "样本", "澄清", "反馈"])
                if file_size < 10000 or is_attachment:
                    skipped_files.append(f"{fname} (attachment/small, skip LLM)")
                    continue
                
                files_to_parse.append((fpath, fname))
        
        # Parse files sequentially
        for fpath, fname in files_to_parse:
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
                logger.warning(f"Failed to parse {fname}: {e}")
                skipped_files.append(f"{fname} (parse error: {e})")

        logger.info(
            f"Archive extraction summary for project {project_id}: "
            f"found={total_files_found}, parsed={total_files_parsed}, skipped={len(skipped_files)}"
        )
        if skipped_files:
            for msg in skipped_files[:20]:  # Log first 20 skipped files
                logger.debug(f"Skipped file: {msg}")

        # Cleanup
        shutil.rmtree(UNZIP_DIR / project_id, ignore_errors=True)
        archive_path.unlink(missing_ok=True)

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
            project.file_list = [{"name": filename, "path": str(file_path), "uploaded_at": str(datetime.utcnow())}]
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
