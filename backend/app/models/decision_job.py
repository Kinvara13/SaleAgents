from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, String
from app.db.base import Base

class ProjectDecisionJobRecord(Base):
    __tablename__ = "project_decision_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    project_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")  # pending, completed, failed
    score = Column(JSON, nullable=True)  # { "total": 84, "dimensions": [...] }
    rule_hits = Column(JSON, nullable=True)  # [ { "name": "...", "level": "...", "result": "...", "detail": "..." } ]
    ai_reasons = Column(JSON, nullable=True)  # [ "..." ]
    pending_checks = Column(JSON, nullable=True)  # [ "..." ]
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

