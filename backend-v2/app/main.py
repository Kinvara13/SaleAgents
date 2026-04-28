import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.scheduler_config import init_scheduler, get_scheduler
from app.db.base import Base
from app.db.session import engine
from app.models import *  # noqa: F401, F403
from app.db.seed_tenders import seed_tenders

setup_logging()
logger = logging.getLogger(__name__)


def _seed_tenders():
    from app.db.session import SessionLocal
    from app.models.tender import Tender
    db = SessionLocal()
    try:
        existing = db.query(Tender).first()
        if not existing:
            seed_tenders(db)
            db.commit()
    finally:
        db.close()


def _schedule_fetch_jobs():
    """注册定时抓取任务"""
    from apscheduler.triggers.interval import IntervalTrigger
    from app.services.tender_fetch_service import run_fetch_task
    from app.db.session import SessionLocal
    import logging

    logger = logging.getLogger(__name__)
    sched = get_scheduler()

    def _fetch_job():
        db = SessionLocal()
        try:
            run_fetch_task(db)
        except Exception:
            logger.exception("定时抓取任务异常")
        finally:
            db.close()

    # 每 30 分钟执行一次（可配置）
    sched.add_job(
        _fetch_job,
        trigger=IntervalTrigger(minutes=30),
        id="tender_fetch_job",
        name="招标信息定时抓取",
        replace_existing=True,
    )
    logger.info("已注册招标抓取定时任务，执行间隔: 30 分钟")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Seed tender data
    _seed_tenders()

    # 启动定时任务调度器
    sched = init_scheduler()
    _schedule_fetch_jobs()
    sched.start()

    yield

    # 应用关闭时停止调度器
    sched.shutdown(wait=False)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_prefix)

    # Serve exported documents as static files
    exports_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
    os.makedirs(exports_dir, exist_ok=True)
    app.mount("/exports", StaticFiles(directory=exports_dir), name="exports")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=True)
