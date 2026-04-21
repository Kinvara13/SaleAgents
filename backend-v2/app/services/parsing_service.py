from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.parsing_section import ParsingSection
from app.models.project import Project
from app.schemas.parsing import ParsingSectionSummary, ParsingSectionDetail, ParsingSectionUpdateRequest


BUSINESS_SECTIONS = [
    "商务偏离表",
    "应答承诺函",
    "授权委托书",
    "营业执照",
    "资格审查资料",
    "应答保证金",
    "封面",
]

TECH_SECTIONS = [
    "技术条款偏离表",
    "CMMI证书",
    "计算机软件著作权证书",
    "项目案例",
    "自查确认单",
    "服务承诺书",
    "封面",
]

# Star items (星标项)
BUSINESS_STAR = {"商务偏离表", "应答承诺函", "授权委托书"}
TECH_STAR = {"技术条款偏离表", "项目案例", "自查确认单"}


def get_or_create_project(db: Session, project_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return project


def list_sections(db: Session, project_id: str) -> list[ParsingSectionSummary]:
    get_or_create_project(db, project_id)
    sections = (
        db.query(ParsingSection)
        .filter(ParsingSection.project_id == project_id)
        .order_by(ParsingSection.section_type, ParsingSection.id)
        .all()
    )
    return [ParsingSectionSummary.model_validate(s) for s in sections]


def get_section_detail(db: Session, project_id: str, section_id: str) -> ParsingSectionDetail:
    section = (
        db.query(ParsingSection)
        .filter(ParsingSection.id == section_id, ParsingSection.project_id == project_id)
        .first()
    )
    if not section:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="章节不存在")
    return ParsingSectionDetail.model_validate(section)


def update_section(
    db: Session, project_id: str, section_id: str, payload: ParsingSectionUpdateRequest
) -> ParsingSectionDetail:
    section = (
        db.query(ParsingSection)
        .filter(ParsingSection.id == section_id, ParsingSection.project_id == project_id)
        .first()
    )
    if not section:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="章节不存在")

    if payload.content is not None:
        section.content = payload.content
    db.commit()
    db.refresh(section)
    return ParsingSectionDetail.model_validate(section)


def simulate_parse(db: Session, project_id: str, filename: str) -> list[ParsingSectionSummary]:
    """Simulate parsing: create sections for a project."""
    get_or_create_project(db, project_id)

    # Remove existing sections
    db.query(ParsingSection).filter(ParsingSection.project_id == project_id).delete()

    created = []
    for name in BUSINESS_SECTIONS:
        section = ParsingSection(
            id=f"sec_{uuid4().hex[:12]}",
            project_id=project_id,
            section_name=name,
            section_type="商务",
            content=_mock_content(name),
            is_star_item=(name in BUSINESS_STAR),
            source_file=filename,
        )
        db.add(section)
        created.append(section)

    for name in TECH_SECTIONS:
        section = ParsingSection(
            id=f"sec_{uuid4().hex[:12]}",
            project_id=project_id,
            section_name=name,
            section_type="技术",
            content=_mock_content(name),
            is_star_item=(name in TECH_STAR),
            source_file=filename,
        )
        db.add(section)
        created.append(section)

    db.commit()
    return [ParsingSectionSummary.model_validate(s) for s in created]


def _mock_content(name: str) -> str:
    return f"【{name}】\n\n此处为招标文件解析得到的 {name} 内容。\n\n在正式投标文件中，应根据招标文件要求及公司实际情况填写相应内容。\n\n（内容由 AI 解析生成，人工可在此处编辑修改）"
