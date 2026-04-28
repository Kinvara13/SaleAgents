from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings


@lru_cache
def _get_engine():
    database_url = settings.database_url
    engine_kwargs: dict = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        engine_kwargs["poolclass"] = NullPool
        engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 60}
    engine = create_engine(database_url, **engine_kwargs)
    if database_url.startswith("sqlite"):
        with engine.connect() as conn:
            conn.exec_driver_sql("PRAGMA journal_mode=WAL")
            conn.exec_driver_sql("PRAGMA busy_timeout=60000")
    return engine


engine = _get_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
