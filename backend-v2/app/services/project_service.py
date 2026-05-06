from typing import Dict, List, Optional, Union
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreateRequest, ProjectSummary, ProjectUpdateRequest


def extracted_fields_to_map(extracted_fields: Union[List, dict, None]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    if not isinstance(extracted_fields, list):
        return result
    for item in extracted_fields:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "").strip()
        value = str(item.get("value") or "").strip()
        if label and value:
            result[label] = value
    return result


def _pick_first_non_empty(*values: object) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def sync_project_core_fields(
    project: Project,
    *,
    tender: Optional[object] = None,
    bidder_name: Optional[str] = None,
) -> Project:
    field_map = extracted_fields_to_map(project.extracted_fields)

    parsed_name = _pick_first_non_empty(field_map.get("项目名称"))
    if parsed_name and (not project.name or project.name.startswith("投标项目_")):
        project.name = parsed_name

    project.client = _pick_first_non_empty(
        project.client,
        field_map.get("招标人"),
        field_map.get("采购人"),
    )
    project.deadline = _pick_first_non_empty(
        project.deadline,
        field_map.get("投标截止时间"),
        getattr(tender, "deadline", ""),
    )
    project.amount = _pick_first_non_empty(
        project.amount,
        field_map.get("预算金额"),
        getattr(tender, "amount", ""),
    )
    project.bidding_company = _pick_first_non_empty(
        project.bidding_company,
        field_map.get("投标人"),
        field_map.get("投标单位"),
        bidder_name,
        project.owner,
    )
    return project


def list_projects(db: Session, status: str | None = None, user_id: str | None = None) -> List[ProjectSummary]:
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    if user_id:
        query = query.filter(Project.user_id == user_id)
    query = query.order_by(Project.created_at.desc())
    return [ProjectSummary.model_validate(p) for p in query.all()]


def get_project(db: Session, project_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return project


def create_project(db: Session, payload: ProjectCreateRequest) -> ProjectSummary:
    project = Project(
        id=f"proj_{uuid4().hex[:12]}",
        name=payload.name,
        owner=payload.owner or "admin",
        client=payload.client or "",
        deadline=payload.deadline or "",
        amount=payload.amount or "",
        risk=payload.risk or "P2",
        status="待决策",
        bidding_company=payload.bidding_company or "",
        agent_name=payload.agent_name or "",
        agent_phone=payload.agent_phone or "",
        agent_email=payload.agent_email or "",
        company_address=payload.company_address or "",
        bank_name=payload.bank_name or "",
        bank_account=payload.bank_account or "",
        description=payload.description or "",
        confirm_status=payload.confirm_status or "待确认",
        user_id=payload.user_id or "user-001",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectSummary.model_validate(project)


def update_project(db: Session, project_id: str, payload: ProjectUpdateRequest) -> ProjectSummary:
    project = get_project(db, project_id)
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return ProjectSummary.model_validate(project)


def delete_project(db: Session, project_id: str) -> None:
    project = get_project(db, project_id)
    db.delete(project)
    db.commit()


def _map_status(status: str) -> str:
    """将后端文档状态映射为前端展示状态"""
    return {"pending": "待开始", "filled": "进行中", "confirmed": "已完成"}.get(status, "待开始")


def _doc_icon(doc_type: str) -> str:
    """根据文档类型返回图标"""
    icons = {
        "deviation": "📊", "commitment": "📝", "authorization": "🪪",
        "business_license": "📄", "qualification": "🔍", "special_invoice": "🧾",
        "non_control": "📋", "non_consortium": "📋", "holding_relation": "📊",
        "operation_commitment": "📋", "integrity_notice": "📋", "bid_bond": "💰",
        "additional_commitment": "📝", "tech_overview": "📄", "tech_deviation": "📊",
        "cmmi_cert": "🏆", "software_copyright": "©️", "project_strength": "📈",
        "compliance_check": "✅", "service_commitment": "🛠️", "additional_content": "📝",
        "tech_cover": "📑", "maintenance_period": "🔧", "project_manager": "👨‍💼",
        "staff_capability": "👥", "hardware_resource": "💻",
    }
    return icons.get(doc_type, "📄")


def get_project_bid_progress(db: Session, project_id: str) -> dict:
    """聚合项目回标文件完成情况"""
    from app.services.bid_template_service import normalize_template_files, template_section_label

    project = get_project(db, project_id)
    template_files = [item for item in normalize_template_files(project.bid_template_files) if item.get("selected", True)]
    if template_files:
        section_order = ["business", "technical", "proposal", "other"]
        section_icons = {
            "business": "📁",
            "technical": "📄",
            "proposal": "💰",
            "other": "📋",
        }
        sections = []
        for idx, section_type in enumerate(section_order, start=1):
            files = [item for item in template_files if item.get("section_type") == section_type]
            if not files:
                continue
            progress_files = []
            for item in files:
                status = str(item.get("status") or "待分配")
                display_status = _map_status(status) if status in {"pending", "filled", "confirmed"} else status
                progress_files.append({
                    "id": str(item.get("id") or item.get("path") or item.get("name")),
                    "name": str(item.get("name") or item.get("path") or "回标模板文件"),
                    "status": display_status,
                    "icon": str(item.get("icon") or _doc_icon(str(item.get("doc_type") or ""))),
                    "responsible": str(item.get("responsible") or ""),
                })
            completed = sum(1 for item in progress_files if item["status"] in ("已完成", "confirmed"))
            sections.append({
                "id": idx,
                "name": template_section_label(section_type),
                "icon": section_icons.get(section_type, "📋"),
                "completed": completed,
                "total": len(progress_files),
                "files": progress_files,
            })
        return {"sections": sections}

    from app.services.business_document_service import ensure_business_documents
    from app.services.technical_document_service import ensure_technical_documents
    from app.services.proposal_plan_service import ensure_proposal_plans

    business_docs = ensure_business_documents(db, project_id)
    technical_docs = ensure_technical_documents(db, project_id)
    proposal_docs = ensure_proposal_plans(db, project_id)

    sections = []

    # 商务部分
    if business_docs:
        business_files = []
        for i, doc in enumerate(business_docs):
            business_files.append({
                "id": doc.id,
                "name": doc.doc_name,
                "status": _map_status(doc.status),
                "icon": _doc_icon(doc.doc_type),
                "responsible": "",
            })
        completed = sum(1 for d in business_docs if d.status == "confirmed")
        sections.append({
            "id": 1,
            "name": "商务部分",
            "icon": "📁",
            "completed": completed,
            "total": len(business_docs),
            "files": business_files,
        })

    # 技术部分
    if technical_docs:
        technical_files = []
        for i, doc in enumerate(technical_docs):
            technical_files.append({
                "id": doc.id,
                "name": doc.doc_name,
                "status": _map_status(doc.status),
                "icon": _doc_icon(doc.doc_type),
                "responsible": "",
            })
        completed = sum(1 for d in technical_docs if d.status == "confirmed")
        sections.append({
            "id": 2,
            "name": "技术部分",
            "icon": "📄",
            "completed": completed,
            "total": len(technical_docs),
            "files": technical_files,
        })

    # 报价部分（使用方案建议书作为报价相关文档）
    if proposal_docs:
        proposal_files = []
        for i, doc in enumerate(proposal_docs):
            proposal_files.append({
                "id": doc.id,
                "name": doc.doc_name,
                "status": _map_status(doc.status),
                "icon": _doc_icon(doc.doc_type),
                "responsible": "",
            })
        completed = sum(1 for d in proposal_docs if d.status == "confirmed")
        sections.append({
            "id": 3,
            "name": "报价部分",
            "icon": "💰",
            "completed": completed,
            "total": len(proposal_docs),
            "files": proposal_files,
        })

    return {"sections": sections}


def get_project_scoring_criteria(db: Session, project_id: str) -> dict:
    """获取项目预估得分（从预评估作业的 tech_review_table 转换）"""
    from app.models.pre_evaluation import PreEvaluationJob

    job = (
        db.query(PreEvaluationJob)
        .filter(PreEvaluationJob.project_id == project_id)
        .order_by(PreEvaluationJob.created_at.desc())
        .first()
    )

    criteria = []
    if job and job.tech_review_table:
        table = job.tech_review_table
        if isinstance(table, list):
            group_map: dict[str, list[dict]] = {}
            for item in table:
                if not isinstance(item, dict):
                    continue
                primary = item.get("一级指标") or item.get("primary") or "评分项"
                group_map.setdefault(primary, []).append(item)

            for primary, items in group_map.items():
                for idx, item in enumerate(items):
                    criteria.append({
                        "primary": primary,
                        "secondary": item.get("二级指标") or item.get("secondary") or "",
                        "standard": item.get("评分标准") or item.get("standard") or item.get("description") or "",
                        "maxScore": int(item.get("分值") or item.get("maxScore") or item.get("score", 0)),
                        "type": "客观" if item.get("类型") in ("客观", "objective") or item.get("type") == "objective" else "主观",
                        "estimatedScore": int(item.get("预估得分") or item.get("estimatedScore") or 0),
                        "isFirstInGroup": idx == 0,
                        "groupSpan": len(items),
                    })

    # 如果预评估表没有数据，尝试从 document_score_histories 构建
    if not criteria:
        from app.models.document_score_history import DocumentScoreHistory
        scores = (
            db.query(DocumentScoreHistory)
            .filter(DocumentScoreHistory.project_id == project_id)
            .all()
        )
        if scores:
            for s in scores:
                criteria.append({
                    "primary": s.doc_kind,
                    "secondary": s.doc_id,
                    "standard": "",
                    "maxScore": int(s.max_score),
                    "type": "客观",
                    "estimatedScore": int(s.score),
                    "isFirstInGroup": True,
                    "groupSpan": 1,
                })

    return {"criteria": criteria}


def get_project_activities(db: Session, project_id: str) -> dict:
    """基于项目现有字段推断操作历史"""
    project = get_project(db, project_id)
    activities = []

    # 创建项目
    if project.created_at:
        time_str = project.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(project.created_at, "strftime") else str(project.created_at)[:16]
        activities.append({
            "icon": "📄",
            "iconBg": "bg-primary/10",
            "iconColor": "text-primary",
            "title": "创建项目",
            "time": time_str,
        })

    # 上传招标文件
    if project.file_list and isinstance(project.file_list, list) and len(project.file_list) > 0:
        file_name = project.file_list[0].get("name", "招标文件")
        uploaded_at = project.file_list[0].get("uploaded_at", "")
        time_str = uploaded_at[:16] if uploaded_at else ""
        activities.append({
            "icon": "✓",
            "iconBg": "bg-success/10",
            "iconColor": "text-success",
            "title": f"上传招标文件：{file_name}",
            "time": time_str,
        })

    # 节点状态变化
    if project.node_status and isinstance(project.node_status, dict):
        node_labels = {
            "decision": "投标决策",
            "parsing": "标书解析",
            "generation": "文档生成",
            "review": "文档评审",
        }
        for key, value in project.node_status.items():
            if value in ("done", "in_progress"):
                label = node_labels.get(key, key)
                status_text = "完成" if value == "done" else "开始"
                activities.append({
                    "icon": "⏰",
                    "iconBg": "bg-warning/10",
                    "iconColor": "text-warning",
                    "title": f"{label}{status_text}",
                    "time": "",
                })

    # 确认状态
    if project.confirm_status == "已确认" and project.confirmed_at:
        time_str = project.confirmed_at[:16] if project.confirmed_at else ""
        activities.append({
            "icon": "✓",
            "iconBg": "bg-success/10",
            "iconColor": "text-success",
            "title": f"项目确认：{project.confirm_feedback or '已确认'}",
            "time": time_str,
        })

    return {"activities": activities}
