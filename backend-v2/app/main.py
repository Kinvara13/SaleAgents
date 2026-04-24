import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import *  # noqa: F401, F403
from app.db.seed_tenders import seed_tenders


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


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Seed tender data
    _seed_tenders()
    yield


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
