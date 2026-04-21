from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Literal

router = APIRouter()

LogType = Literal["backend", "frontend", "all"]


class LogsResponse(BaseModel):
    backend: str = ""
    frontend: str = ""
    backend_exists: bool = False
    frontend_exists: bool = False


@router.get("/logs", response_model=LogsResponse)
def get_logs(
    log_type: LogType = Query(default="all", description="要读取的日志类型: backend | frontend | all"),
    lines: int = Query(default=200, ge=10, le=2000, description="返回的最大行数"),
):
    project_root = Path(__file__).resolve().parents[4].parent
    logs_dir = project_root / "logs"

    result = LogsResponse()

    if log_type in ("backend", "all"):
        backend_log = logs_dir / "backend.log"
        result.backend_exists = backend_log.exists()
        if result.backend_exists:
            result.backend = _read_last_lines(backend_log, lines)

    if log_type in ("frontend", "all"):
        frontend_log = logs_dir / "frontend.log"
        result.frontend_exists = frontend_log.exists()
        if result.frontend_exists:
            result.frontend = _read_last_lines(frontend_log, lines)

    return result


def _read_last_lines(path: Path, n: int) -> str:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        all_lines = content.splitlines()
        return "\n".join(all_lines[-n:])
    except Exception:
        return ""
