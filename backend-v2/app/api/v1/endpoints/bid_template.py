from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from pathlib import Path
from uuid import uuid4
import zipfile, os, shutil, logging

from app.db.session import get_db
from app.models.project import Project
from app.core.config import settings
from app.services.bid_template_service import (
    classify_template_file,
    normalize_template_files,
    should_include_template_file,
)

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_TEMPLATE_EXTENSIONS = {".zip", ".rar", ".7z", ".docx", ".doc", ".pdf"}
MAX_TEMPLATE_SIZE = 50 * 1024 * 1024


def _decode_zip_filename(name: str) -> str:
    """Decode ZIP filename with Chinese encoding fallback.

    Python's zipfile uses cp437 by default for non-UTF-8 entries.
    We must encode with cp437 (not latin-1) to recover original bytes.
    """
    if not isinstance(name, str):
        name = str(name)

    if any('\u4e00' <= c <= '\u9fff' for c in name):
        return name

    for source_enc in ('cp437', 'latin-1'):
        try:
            original_bytes = name.encode(source_enc)
            for target_enc in ('utf-8', 'gbk', 'gb18030'):
                try:
                    decoded = original_bytes.decode(target_enc)
                    if any('\u4e00' <= c <= '\u9fff' for c in decoded):
                        return decoded
                except (UnicodeDecodeError, UnicodeEncodeError):
                    pass
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    return name


def _extract_text_from_file(file_path: Path) -> str:
    """Extract text content from a document file for preview."""
    ext = file_path.suffix.lower()
    try:
        if ext == ".txt":
            return file_path.read_text(encoding="utf-8", errors="replace")
        elif ext == ".docx":
            from docx import Document
            doc = Document(str(file_path))
            return "\n".join([p.text for p in doc.paragraphs])
        elif ext == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(file_path))
                texts = []
                for page in reader.pages:
                    pt = page.extract_text() or ""
                    if pt.strip():
                        texts.append(pt)
                return "\n\n".join(texts)
            except Exception:
                return "[PDF内容预览暂不可用]"
        else:
            return file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        logger.warning(f"Failed to extract text from {file_path}: {e}")
        return f"[文件内容读取失败: {e}]"


def _extract_zip_recursive(zip_path: Path, target_dir: Path, depth: int = 0) -> list[Path]:
    """Recursively extract ZIP files and return list of extracted file paths."""
    extracted_files: list[Path] = []
    if depth > 3:
        logger.warning(f"Max ZIP nesting depth reached at: {zip_path}")
        return extracted_files
    target_dir.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for info in zf.infolist():
                decoded_name = _decode_zip_filename(info.filename)
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
                if target_path.suffix.lower() == ".zip":
                    nested_dir = target_path.parent / target_path.stem
                    try:
                        nested_files = _extract_zip_recursive(target_path, nested_dir, depth + 1)
                        extracted_files.extend(nested_files)
                        target_path.unlink(missing_ok=True)
                        logger.info(f"Recursively extracted nested ZIP: {decoded_name}")
                    except Exception as e:
                        logger.warning(f"Failed to extract nested ZIP {decoded_name}: {e}")
    except zipfile.BadZipFile as e:
        logger.error(f"Bad ZIP file: {zip_path} - {e}")
        raise
    return extracted_files


def _extract_rar_recursive(rar_path: Path, target_dir: Path, depth: int = 0) -> list[Path]:
    """Recursively extract RAR files and return list of extracted file paths."""
    extracted_files: list[Path] = []
    if depth > 3:
        logger.warning(f"Max RAR nesting depth reached at: {rar_path}")
        return extracted_files
    target_dir.mkdir(parents=True, exist_ok=True)
    
    extracted = False
    
    if not extracted:
        try:
            import patoolib
            patoolib.extract_archive(str(rar_path), outdir=str(target_dir))
            extracted = True
        except Exception as e:
            logger.warning(f"patool extraction failed: {e}")
    
    if not extracted:
        try:
            import subprocess
            result = subprocess.run(
                ['7z', 'x', f'-o{target_dir}', '-y', str(rar_path)],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                extracted = True
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
            if decoded_name.startswith(".") or "/." in decoded_name:
                continue
            target_path = Path(root) / decoded_name
            extracted_files.append(target_path)
            if target_path.suffix.lower() == ".rar":
                nested_dir = target_path.parent / target_path.stem
                try:
                    nested_files = _extract_rar_recursive(target_path, nested_dir, depth + 1)
                    extracted_files.extend(nested_files)
                    target_path.unlink(missing_ok=True)
                except Exception as e:
                    logger.warning(f"Failed to extract nested RAR {decoded_name}: {e}")
    return extracted_files


def _extract_7z_recursive(sevenz_path: Path, target_dir: Path, depth: int = 0) -> list[Path]:
    """Recursively extract 7z files and return list of extracted file paths."""
    try:
        import py7zr
    except ImportError:
        logger.error("py7zr library not installed. Please run: pip install py7zr")
        raise RuntimeError("7z support requires py7zr library. Run: pip install py7zr")
    
    extracted_files: list[Path] = []
    if depth > 3:
        logger.warning(f"Max 7z nesting depth reached at: {sevenz_path}")
        return extracted_files
    target_dir.mkdir(parents=True, exist_ok=True)
    try:
        with py7zr.SevenZipFile(str(sevenz_path), mode='r') as archive:
            archive.extractall(path=target_dir)
            for info in archive.list():
                decoded_name = _decode_zip_filename(info.filename)
                if decoded_name.startswith(".") or "/." in decoded_name:
                    continue
                target_path = target_dir / decoded_name
                if target_path.exists():
                    extracted_files.append(target_path)
                    if target_path.suffix.lower() == ".7z":
                        nested_dir = target_path.parent / target_path.stem
                        try:
                            nested_files = _extract_7z_recursive(target_path, nested_dir, depth + 1)
                            extracted_files.extend(nested_files)
                            target_path.unlink(missing_ok=True)
                            logger.info(f"Recursively extracted nested 7z: {decoded_name}")
                        except Exception as e:
                            logger.warning(f"Failed to extract nested 7z {decoded_name}: {e}")
    except Exception as e:
        logger.error(f"Bad 7z file: {sevenz_path} - {e}")
        raise
    return extracted_files


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
        extracted_files = _extract_zip_recursive(template_path, extract_dir)
        for file_path in extracted_files:
            file_ext = file_path.suffix.lower()
            rel_path = str(file_path.relative_to(extract_dir))
            if file_ext in {".docx", ".doc", ".pdf", ".txt", ".xlsx", ".xls"} and should_include_template_file(file_path.name, rel_path):
                bid_files.append({
                    "id": f"tpl_{uuid4().hex[:8]}",
                    "name": file_path.name,
                    "path": rel_path,
                    "status": "待分配",
                    "selected": True,
                    "icon": "📄",
                    "section_type": classify_template_file(file_path.name, rel_path),
                })
        # Keep extracted files for preview; only remove the original archive
        template_path.unlink(missing_ok=True)

    elif ext == ".rar":
        extract_dir = upload_dir / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)
        _extract_rar_recursive(template_path, extract_dir)
        for root, dirs, files in os.walk(extract_dir):
            for fname in files:
                decoded_name = _decode_zip_filename(fname)
                file_ext = Path(decoded_name).suffix.lower()
                if file_ext in {".docx", ".doc", ".pdf", ".txt", ".xlsx", ".xls"}:
                    rel_path = os.path.relpath(os.path.join(root, decoded_name), extract_dir)
                    if not should_include_template_file(decoded_name, rel_path):
                        continue
                    bid_files.append({
                        "id": f"tpl_{uuid4().hex[:8]}",
                        "name": decoded_name,
                        "path": rel_path,
                        "status": "待分配",
                        "selected": True,
                        "icon": "📄",
                        "section_type": classify_template_file(decoded_name, rel_path),
                    })
        # Keep extracted files for preview; only remove the original archive
        template_path.unlink(missing_ok=True)

    elif ext == ".7z":
        extract_dir = upload_dir / "extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)
        _extract_7z_recursive(template_path, extract_dir)
        for root, dirs, files in os.walk(extract_dir):
            for fname in files:
                decoded_name = _decode_zip_filename(fname)
                file_ext = Path(decoded_name).suffix.lower()
                if file_ext in {".docx", ".doc", ".pdf", ".txt", ".xlsx", ".xls"}:
                    rel_path = os.path.relpath(os.path.join(root, decoded_name), extract_dir)
                    if not should_include_template_file(decoded_name, rel_path):
                        continue
                    bid_files.append({
                        "id": f"tpl_{uuid4().hex[:8]}",
                        "name": decoded_name,
                        "path": rel_path,
                        "status": "待分配",
                        "selected": True,
                        "icon": "📄",
                        "section_type": classify_template_file(decoded_name, rel_path),
                    })
        # Keep extracted files for preview; only remove the original archive
        template_path.unlink(missing_ok=True)

    elif ext in {".docx", ".doc", ".pdf"}:
        bid_files.append({
            "id": f"tpl_{uuid4().hex[:8]}",
            "name": filename,
            "path": filename,
            "status": "待分配",
            "selected": True,
            "icon": "📄",
            "section_type": classify_template_file(filename, filename),
        })

    bid_files = normalize_template_files(bid_files)
    project.bid_template_files = bid_files
    db.commit()

    return {
        "status": "success",
        "message": "模板上传成功",
        "filename": filename,
        "files": bid_files,
    }


@router.get("/{project_id}/template-files")
def get_template_files(project_id: str, db: Session = Depends(get_db)) -> dict:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    
    return {
        "status": "success",
        "files": normalize_template_files(project.bid_template_files),
    }


@router.get("/{project_id}/template-files/{file_path:path}/preview")
def preview_template_file(project_id: str, file_path: str, db: Session = Depends(get_db)) -> dict:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    
    upload_dir = Path(settings.storage_path or Path(__file__).resolve().parents[4] / "storage") / "projects" / project_id / "bid_templates"
    # Files from archives are kept in "extracted/"; single uploads stay at root
    target_file = upload_dir / file_path
    if not target_file.exists():
        target_file = upload_dir / "extracted" / file_path
    if not target_file.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    
    content = _extract_text_from_file(target_file)
    
    return {
        "status": "success",
        "filename": target_file.name,
        "content": content,
    }


@router.put("/{project_id}/template-files")
def update_template_files(
    project_id: str,
    payload: list[dict],
    db: Session = Depends(get_db),
) -> dict:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

    project.bid_template_files = normalize_template_files(payload)
    db.commit()

    return {
        "status": "success",
        "message": "文件列表已更新",
        "files": project.bid_template_files,
    }
