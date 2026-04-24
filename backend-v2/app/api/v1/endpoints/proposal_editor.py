from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.schemas.proposal import (
    ProposalSectionSummary,
    ProposalSectionDetail,
    ProposalSectionUpdateRequest,
    ProposalScoreResponse,
    ProposalGenerationRequest,
    SCORING_RULES,
)
from app.schemas.task import TaskSubmitResponse
from app.services import proposal_service
from app.services.task_service import create_task, update_task_status

router = APIRouter()


@router.post("/{project_id}/generate", response_model=TaskSubmitResponse)
def generate_proposal(
    project_id: str,
    background_tasks: BackgroundTasks,
    payload: ProposalGenerationRequest | None = None,
    db: Session = Depends(get_db),
) -> TaskSubmitResponse:
    """触发异步生成任务，返回任务ID"""
    if payload is None:
        payload = ProposalGenerationRequest()
    
    # 更新项目生成状态
    project = db.query(Project).filter(Project.id == project_id).first()
    if project:
        if isinstance(project.node_status, dict):
            project.node_status["generation"] = "processing"
        else:
            project.node_status = {"generation": "processing"}
        db.commit()
    
    # 创建异步任务记录
    task = create_task(db, task_type="proposal_generation", project_id=project_id)
    
    background_tasks.add_task(_generate_proposal_with_task, project_id, payload, task.id)
    return TaskSubmitResponse(
        task_id=task.id,
        status="processing",
        message="生成任务已在后台启动",
    )


def _generate_proposal_with_task(project_id: str, payload: ProposalGenerationRequest, task_id: str) -> None:
    """带任务状态更新的异步生成包装器"""
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        update_task_status(db, task_id, "processing")
        
        result = proposal_service.generate_proposal(db, project_id, payload)
        
        # 更新项目状态
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            if isinstance(project.node_status, dict):
                project.node_status["generation"] = "completed"
            else:
                project.node_status = {"generation": "completed"}
            db.commit()
        
        update_task_status(
            db, task_id, "completed",
            result={"section_count": len(result)}
        )
    except Exception as e:
        import logging
        logging.error(f"Proposal generation failed for project {project_id}: {e}")
        db.rollback()
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            if isinstance(project.node_status, dict):
                project.node_status["generation"] = "failed"
            else:
                project.node_status = {"generation": "failed"}
            db.commit()
        
        update_task_status(db, task_id, "failed", error_message=str(e))
    finally:
        db.close()


@router.get("/{project_id}/sections", response_model=list[ProposalSectionSummary])
def get_sections(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[ProposalSectionSummary]:
    return proposal_service.list_sections(db, project_id)


@router.get("/{project_id}/sections/{section_id}", response_model=ProposalSectionDetail)
def get_section_detail(
    project_id: str,
    section_id: str,
    db: Session = Depends(get_db),
) -> ProposalSectionDetail:
    return proposal_service.get_section_detail(db, project_id, section_id)


@router.patch("/{project_id}/sections/{section_id}", response_model=ProposalSectionDetail)
def patch_section(
    project_id: str,
    section_id: str,
    payload: ProposalSectionUpdateRequest,
    db: Session = Depends(get_db),
) -> ProposalSectionDetail:
    return proposal_service.update_section(db, project_id, section_id, payload)


@router.post("/{project_id}/score", response_model=ProposalScoreResponse)
def score_proposal(
    project_id: str,
    db: Session = Depends(get_db),
) -> ProposalScoreResponse:
    sections, total = proposal_service.compute_score(db, project_id)
    return ProposalScoreResponse(sections=sections, total_score=total)


@router.post("/{project_id}/rescore", response_model=ProposalScoreResponse)
def rescore_proposal(
    project_id: str,
    db: Session = Depends(get_db),
) -> ProposalScoreResponse:
    """人工修改后的再次打分"""
    sections, total = proposal_service.compute_score(db, project_id, force=True)
    return ProposalScoreResponse(sections=sections, total_score=total)


@router.post("/{project_id}/confirm", response_model=list[ProposalSectionSummary])
def confirm_proposal(
    project_id: str,
    db: Session = Depends(get_db),
) -> list[ProposalSectionSummary]:
    return proposal_service.confirm_all(db, project_id)


@router.get("/{project_id}/scoring-rules")
def get_scoring_rules(project_id: str, db: Session = Depends(get_db)):
    """获取技术建议书评分规则（对应技术打分表）"""
    # 从项目关联的 technical_documents 获取评分相关配置
    rules = []
    for section_name, rule_info in SCORING_RULES.items():
        rules.append({
            "section_name": section_name,
            "max_score": rule_info["max"],
            "weight": rule_info["weight"],
            "criteria": rule_info["criteria"],
        })
    return {"total_max": 100, "sections": rules}