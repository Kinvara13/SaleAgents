from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender_fetch_log import TenderFetchLog
from app.schemas.tender_fetch_log import TenderFetchLogList, TenderFetchLogItem

router = APIRouter()


@router.get("/", response_model=TenderFetchLogList)
def list_fetch_logs(
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TenderFetchLogList:
    """获取招标抓取任务执行日志

    - status: 过滤状态（success / partial / failed / running）
    - 默认按执行时间倒序
    """
    query = db.query(TenderFetchLog)
    if status:
        query = query.filter(TenderFetchLog.status == status)

    total = query.count()
    items = (
        query.order_by(TenderFetchLog.started_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return TenderFetchLogList(
        total=total,
        items=[TenderFetchLogItem.model_validate(i) for i in items],
    )


@router.get("/latest-failed", response_model=TenderFetchLogItem | None)
def get_latest_failed_log(
    db: Session = Depends(get_db),
) -> TenderFetchLogItem | None:
    """获取最近一次失败的抓取任务日志（用于告警展示）"""
    log = (
        db.query(TenderFetchLog)
        .filter(TenderFetchLog.status.in_(["failed", "partial"]))
        .order_by(TenderFetchLog.started_at.desc())
        .first()
    )
    if log:
        return TenderFetchLogItem.model_validate(log)
    return None
