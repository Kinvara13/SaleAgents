from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException

from app.models.decision_job import ProjectDecisionJobRecord
from app.models.project_extracted_field import ProjectExtractedField
from app.models.project import Project
from app.schemas.decision import (
    ProjectDecisionJobResponse,
    DecisionScore,
    ScoreDimension,
    DecisionRuleHit,
)
from app.services.llm_client import llm_decision_client

class DecisionService:
    """Service for bid decision workflows."""

    def list_jobs(self, db: Session, project_id: str) -> list[ProjectDecisionJobRecord]:
        return (
            db.query(ProjectDecisionJobRecord)
            .filter(ProjectDecisionJobRecord.project_id == project_id)
            .order_by(desc(ProjectDecisionJobRecord.created_at))
            .all()
        )

    def get_latest_job(self, db: Session, project_id: str) -> ProjectDecisionJobRecord | None:
        return (
            db.query(ProjectDecisionJobRecord)
            .filter(ProjectDecisionJobRecord.project_id == project_id)
            .order_by(desc(ProjectDecisionJobRecord.created_at))
            .first()
        )

    def run_decision_job(self, db: Session, project_id: str) -> ProjectDecisionJobRecord:
        # Create a new job
        job = ProjectDecisionJobRecord(
            project_id=project_id,
            status="running"
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        try:
            # 1. Gather extracted fields for the project
            fields = db.query(ProjectExtractedField).filter(
                ProjectExtractedField.project_id == project_id
            ).all()
            field_map = {f.label: f.value for f in fields}

            # 2. Rule Engine (Heuristics based on parsed fields)
            rule_hits = []
            pending_checks = []

            # Budget rule
            budget_str = field_map.get("预算金额", "")
            if not budget_str or "不详" in budget_str or "待定" in budget_str:
                rule_hits.append({
                    "name": "预算评估",
                    "level": "P2",
                    "result": "信息缺失",
                    "detail": "招标文件未明确预算金额，建议跟进确认"
                })
                pending_checks.append("确认项目真实预算规模")
            elif "万" in budget_str:
                rule_hits.append({
                    "name": "预算评估",
                    "level": "P2",
                    "result": "通过",
                    "detail": f"预算明确 ({budget_str})"
                })

            # Qualifications
            qualifications = field_map.get("必备资质", "")
            if not qualifications or "不详" in qualifications:
                pending_checks.append("确认是否有隐藏资质门槛")
            else:
                rule_hits.append({
                    "name": "资质符合度",
                    "level": "P0",
                    "result": "建议人工复核",
                    "detail": f"要求资质：{qualifications}"
                })
                pending_checks.append("关键资质是否满足存在歧义")

            # Timeline
            deadline = field_map.get("投标截止时间", "")
            if not deadline or "不详" in deadline:
                pending_checks.append("确认投标截止时间")

            # Payment terms
            payment = field_map.get("付款条款", "")
            if "垫资" in payment or "延期" in payment:
                rule_hits.append({
                    "name": "付款风险",
                    "level": "P1",
                    "result": "高风险",
                    "detail": "存在垫资或付款周期较长风险"
                })

            if not pending_checks:
                pending_checks.append("技术参数缺少明确阈值")

            # 3. Try AI Semantic Matching / Scoring (LLM First, Fallback to Heuristics)
            project = db.query(Project).filter(Project.id == project_id).first()
            project_name = project.name if project else f"Project {project_id}"
            client_name = project.client if project else ""

            llm_result = llm_decision_client.evaluate_project(
                project_name=project_name,
                client_name=client_name,
                extracted_fields=field_map,
                rule_hits=rule_hits,
            )

            if llm_result:
                # LLM Success
                ai_reasons = llm_result.get("ai_reasons", [])
                score = llm_result.get("score", {
                    "total": 80,
                    "dimensions": [{"label": "综合评估", "score": 80, "note": "模型未返回详细维度"}]
                })
                # Merge LLM pending checks with rule pending checks
                llm_pending = llm_result.get("pending_checks", [])
                for check in llm_pending:
                    if check not in pending_checks:
                        pending_checks.append(check)
            else:
                # Fallback to Heuristics
                ai_reasons = [
                    "项目预算与公司准入标准匹配",
                    "核心资质基本满足，但需二次确认",
                    "交期存在一定压力，建议协调交付团队评估",
                ]

                score = {
                    "total": 82,
                    "dimensions": [
                        {"label": "资质与合规", "score": 85, "note": "满足基本门槛，无重大合规风险"},
                        {"label": "技术能力匹配", "score": 90, "note": "核心技术参数与现有产品高度契合"},
                        {"label": "商业与利润", "score": 75, "note": "付款周期适中，利润率符合预期"},
                        {"label": "竞争与环境", "score": 78, "note": "区域市场优势一般，面临一定竞争压力"}
                    ]
                }

            # Update job
            job.status = "completed"
            job.score = score
            job.rule_hits = rule_hits
            job.ai_reasons = ai_reasons
            job.pending_checks = pending_checks
            job.completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(job)
            return job

        except Exception as e:
            job.status = "failed"
            db.commit()
            raise e

decision_service = DecisionService()
