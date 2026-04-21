import json
import os
import re
import zipfile
from datetime import datetime
from io import BytesIO
from uuid import uuid4

from docx import Document
from fastapi import HTTPException, status
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.pre_evaluation import PreEvaluationJob
from app.schemas.pre_evaluation import PreEvaluationJobListItem, PreEvaluationJobResponse
from app.services.llm_client import llm_pre_evaluation_client


class PreEvaluationService:
    def create_job_from_upload(
        self,
        db: Session,
        *,
        file_bytes: bytes,
        filename: str,
        project_id: str | None = None,
    ) -> PreEvaluationJobResponse:
        job = PreEvaluationJob(
            project_id=project_id,
            file_name=filename,
            file_path="",
            status="pending",
        )
        db.add(job)
        db.flush()

        # Save file
        storage_dir = settings.storage_path or "storage/pre_evaluations"
        os.makedirs(storage_dir, exist_ok=True)
        file_path = os.path.join(storage_dir, f"{job.id}-{filename}")
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        job.file_path = file_path
        db.flush()

        # Parse text
        job.status = "parsing"
        db.flush()
        try:
            source_text = self._extract_text_from_file(filename=filename, file_bytes=file_bytes)
        except Exception as exc:
            job.status = "failed"
            job.summary = f"文件解析失败: {exc}"
            db.commit()
            raise

        job.source_text = source_text[:50000]  # Limit text length
        db.flush()

        # Analyze with LLM
        job.status = "analyzing"
        db.flush()
        try:
            result = llm_pre_evaluation_client.analyze(source_text=job.source_text)
        except Exception as exc:
            job.status = "failed"
            job.summary = f"LLM 分析失败: {exc}"
            db.commit()
            raise

        job.review_method = result.get("review_method", {})
        job.tech_review_table = result.get("tech_review_table", [])
        job.starred_items = result.get("starred_items", [])
        job.summary = result.get("summary", "")
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        return self._to_response(job)

    def list_jobs(self, db: Session, project_id: str | None = None) -> list[PreEvaluationJobListItem]:
        query = select(PreEvaluationJob).order_by(PreEvaluationJob.created_at.desc())
        if project_id:
            query = query.where(PreEvaluationJob.project_id == project_id)
        rows = db.scalars(query).all()
        return [PreEvaluationJobListItem.model_validate(row) for row in rows]

    def get_job(self, db: Session, job_id: str) -> PreEvaluationJobResponse:
        job = db.get(PreEvaluationJob, job_id)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pre-evaluation job '{job_id}' not found.",
            )
        return self._to_response(job)

    def delete_job(self, db: Session, job_id: str) -> None:
        job = db.get(PreEvaluationJob, job_id)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pre-evaluation job '{job_id}' not found.",
            )
        # Delete file if exists
        if job.file_path and os.path.exists(job.file_path):
            os.remove(job.file_path)
        db.delete(job)
        db.commit()

    def _extract_text_from_file(self, *, filename: str, file_bytes: bytes) -> str:
        suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

        if suffix in {"txt", "md"}:
            return file_bytes.decode("utf-8", errors="ignore").strip()

        if suffix == "pdf":
            reader = PdfReader(BytesIO(file_bytes))
            pages = [(page.extract_text() or "").strip() for page in reader.pages]
            return "\n".join([item for item in pages if item]).strip()

        if suffix == "docx":
            document = Document(BytesIO(file_bytes))
            paragraphs = [item.text.strip() for item in document.paragraphs if item.text.strip()]
            return "\n".join(paragraphs).strip()

        if suffix == "zip":
            texts = []
            with zipfile.ZipFile(BytesIO(file_bytes)) as zf:
                for name in zf.namelist():
                    if name.startswith("__MACOSX/") or name.startswith("."):
                        continue
                    inner_suffix = name.lower().rsplit(".", 1)[-1] if "." in name else ""
                    if inner_suffix not in {"txt", "md", "pdf", "docx"}:
                        continue
                    try:
                        inner_bytes = zf.read(name)
                        inner_text = self._extract_text_from_file(filename=name, file_bytes=inner_bytes)
                        if inner_text:
                            texts.append(f"=== {name} ===\n{inner_text}")
                    except Exception:
                        continue
            return "\n\n".join(texts).strip()

        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Please upload txt, pdf, docx, or zip.",
        )

    def _to_response(self, job: PreEvaluationJob) -> PreEvaluationJobResponse:
        return PreEvaluationJobResponse.model_validate(job)


pre_evaluation_service = PreEvaluationService()
