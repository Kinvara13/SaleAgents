import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.parsing_section import ParsingSection
from app.models.project import Project
from app.schemas.parsing import ParsingSectionSummary, ParsingSectionDetail, ParsingSectionUpdateRequest
from app.schemas.workspace import ParseSection
from app.services.llm_parsing_client import llm_parsing_client

logger = logging.getLogger(__name__)

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

BUSINESS_STAR = {"商务偏离表", "应答承诺函", "授权委托书"}
TECH_STAR = {"技术条款偏离表", "项目案例", "自查确认单"}

# Chunking constants
MAX_CHUNK_CHARS = 12000
SUMMARIZE_THRESHOLD = 15000
MIN_CHUNK_CHARS = 200

# Heading patterns for Chinese tender documents
HEADING_PATTERNS = [
    re.compile(r"^第[一二三四五六七八九十百\d]+章[、\.．\s]+"),
    re.compile(r"^第[一二三四五六七八九十\d]+节[、\.．\s]+"),
    re.compile(r"^[一二三四五六七八九十]+[、\.．]\s*"),
    re.compile(r"^\([一二三四五六七八九十\d]+\)"),
    re.compile(r"^\(\d+\)"),
    re.compile(r"^\d+[\.．]\d+\s+"),
    re.compile(r"^\d+[、\.．]\s+\S"),
    re.compile(r"^(附件|附录)\d*\s*"),
]

KEYWORD_SECTION_HEADINGS = {
    "招标公告", "投标人须知", "评标办法", "合同条款", "技术要求",
    "商务要求", "资格审查", "投标文件格式", "报价要求", "服务承诺",
    "质保要求", "交付要求", "项目背景", "项目概况", "建设目标",
    "总体要求", "功能需求", "非功能需求", "安全要求", "附件",
}


def _is_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or len(stripped) > 80:
        return False
    for pattern in HEADING_PATTERNS:
        if pattern.match(stripped):
            return True
    # Heuristic: short line ending with punctuation and containing section keywords
    if len(stripped) < 40:
        clean = stripped.rstrip("：:. \n")
        if clean in KEYWORD_SECTION_HEADINGS:
            return True
        if any(kw in clean for kw in ["说明", "要求", "条款", "标准", "规范", "评审", "评分", "合同", "资质", "附录"]):
            if stripped.endswith(("：", ":", "。")):
                return True
    return False


def _extract_text_from_file(file_path: Path, ext: str) -> tuple[str, list[tuple[int, str]]]:
    """Extract text from a file. Returns (full_text, list_of(page_num, page_text))."""
    pages: list[tuple[int, str]] = []
    full_text = ""

    try:
        if ext == ".txt":
            text = file_path.read_text(encoding="utf-8", errors="replace")
            pages.append((1, text))
            full_text = text
        elif ext == ".docx":
            try:
                from docx import Document
                doc = Document(str(file_path))
                text = "\n".join([p.text for p in doc.paragraphs])
                pages.append((1, text))
                full_text = text
            except Exception:
                pass
        elif ext == ".xlsx":
            try:
                import openpyxl
                wb = openpyxl.load_workbook(str(file_path), data_only=True)
                lines = []
                for sheet in wb.sheetnames:
                    ws = wb[sheet]
                    for row in ws.iter_rows(values_only=True):
                        line = " ".join([str(c) if c else "" for c in row])
                        if line.strip():
                            lines.append(line)
                text = "\n".join(lines)
                pages.append((1, text))
                full_text = text
            except Exception:
                pass
        elif ext == ".pdf":
            # Try pypdf first (faster), fallback to pdfplumber (better extraction)
            try:
                import pypdf
                reader = pypdf.PdfReader(str(file_path))
                for i, page in enumerate(reader.pages, start=1):
                    pt = page.extract_text() or ""
                    if pt.strip():
                        pages.append((i, pt))
            except Exception:
                logger.warning("pypdf extraction failed, trying pdfplumber for %s", file_path)
                try:
                    import pdfplumber
                    with pdfplumber.open(str(file_path)) as pdf:
                        for i, page in enumerate(pdf.pages, start=1):
                            pt = page.extract_text() or ""
                            if pt.strip():
                                pages.append((i, pt))
                except Exception:
                    pass
            full_text = "\n\n".join(f"--- Page {p[0]} ---\n{p[1]}" for p in pages)
        else:
            text = file_path.read_text(encoding="utf-8", errors="replace")
            pages.append((1, text))
            full_text = text
    except Exception as e:
        logger.error("Text extraction failed for %s: %s", file_path, e)
        full_text = f"[文件读取失败: {e}]"

    return full_text, pages


def _chunk_by_headings(pages: list[tuple[int, str]]) -> list[dict[str, Any]]:
    """Group page text into logical chunks by heading detection."""
    chunks: list[dict[str, Any]] = []
    current_title = "文档开头"
    current_lines: list[str] = []
    current_start_page = 1

    for page_num, page_text in pages:
        lines = page_text.splitlines()
        for line in lines:
            if _is_heading(line):
                # Save previous chunk
                if current_lines:
                    content = "\n".join(current_lines).strip()
                    if len(content) >= MIN_CHUNK_CHARS:
                        chunks.append({
                            "title": current_title,
                            "start_page": current_start_page,
                            "end_page": page_num,
                            "content": content,
                        })
                current_title = line.strip().rstrip("：:. \n")
                current_lines = []
                current_start_page = page_num
            else:
                current_lines.append(line)

    # Save last chunk
    if current_lines:
        content = "\n".join(current_lines).strip()
        if len(content) >= MIN_CHUNK_CHARS:
            chunks.append({
                "title": current_title,
                "start_page": current_start_page,
                "end_page": pages[-1][0] if pages else current_start_page,
                "content": content,
            })

    return chunks


def _split_oversized_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Split chunks that exceed MAX_CHUNK_CHARS into smaller pieces."""
    result: list[dict[str, Any]] = []
    for chunk in chunks:
        content = chunk["content"]
        if len(content) <= MAX_CHUNK_CHARS:
            result.append(chunk)
            continue
        # Try to split by paragraphs
        paragraphs = content.split("\n\n")
        parts: list[str] = []
        current_part = ""
        for para in paragraphs:
            if len(current_part) + len(para) + 2 > MAX_CHUNK_CHARS:
                if current_part:
                    parts.append(current_part.strip())
                current_part = para
            else:
                current_part = current_part + "\n\n" + para if current_part else para
        if current_part:
            parts.append(current_part.strip())

        for idx, part in enumerate(parts, start=1):
            if len(part) >= MIN_CHUNK_CHARS:
                result.append({
                    "title": f"{chunk['title']} (Part {idx})" if len(parts) > 1 else chunk["title"],
                    "start_page": chunk["start_page"],
                    "end_page": chunk["end_page"],
                    "content": part,
                })
    return result


def _summarize_chunk(content: str, section_name: str) -> str:
    """Use LLM to summarize a long chunk. Falls back to tail-aware truncation."""
    try:
        summary = llm_parsing_client.summarize_text(content, title=section_name, max_words=2000)
        if summary:
            return summary
    except Exception as e:
        logger.warning("LLM summarization failed for chunk '%s': %s", section_name, e)

    # Fallback: smart truncation preserving head and tail
    head_len = 6000
    tail_len = 4000
    if len(content) > head_len + tail_len + 200:
        return (
            content[:head_len]
            + "\n\n...[中间内容省略]...\n\n"
            + content[-tail_len:]
        )
    return content[:MAX_CHUNK_CHARS]


@dataclass
class ParsingContext:
    parse_sections: list = field(default_factory=list)
    source_excerpt: str = ""


class ParsingService:
    """Real PDF/document parsing with chunking and summarization."""

    # --- Backward-compatible module-level API wrappers ---

    def list_sections(self, db: Session, project_id: str) -> list[ParsingSectionSummary]:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
        sections = (
            db.query(ParsingSection)
            .filter(ParsingSection.project_id == project_id)
            .order_by(ParsingSection.section_type, ParsingSection.id)
            .all()
        )
        return [ParsingSectionSummary.model_validate(s) for s in sections]

    def get_section_detail(self, db: Session, project_id: str, section_id: str) -> ParsingSectionDetail:
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
        self, db: Session, project_id: str, section_id: str, payload: ParsingSectionUpdateRequest
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

    # --- Core parsing logic ---

    def parse_document(
        self,
        db: Session,
        project_id: str,
        file_path: Path,
        filename: str,
        clear_existing: bool = True,
    ) -> list[ParsingSectionSummary]:
        """Parse a single document (PDF/DOCX/TXT/etc.) into ParsingSections."""
        ext = Path(filename).suffix.lower()
        full_text, pages = _extract_text_from_file(file_path, ext)

        if not full_text or len(full_text.strip()) < 50:
            logger.warning("No text extracted from %s", filename)
            return self._create_placeholder_sections(db, project_id, filename)

        # 1. Chunk by headings
        chunks = _chunk_by_headings(pages)

        # 2. Split oversized chunks
        chunks = _split_oversized_chunks(chunks)

        # 4. Merge tiny chunks with neighbors
        chunks = self._merge_tiny_chunks(chunks)

        # 5. Extract tender fields via LLM (using curated text: head + tail + important paragraphs)
        curated_text = self._curate_text_for_llm(full_text)
        tender_info = llm_parsing_client.extract_tender_fields(curated_text)
        if not tender_info:
            logger.warning(f"No tender fields extracted for {filename} - LLM extraction returned empty")

        # 6. Persist
        if clear_existing:
            db.query(ParsingSection).filter(ParsingSection.project_id == project_id).delete()

        created: list[ParsingSection] = []

        # Document structure chunks
        for chunk in chunks:
            section = ParsingSection(
                id=f"sec_{uuid4().hex[:12]}",
                project_id=project_id,
                section_name=chunk["title"],
                section_type="评审" if any(k in chunk["title"] for k in ["评分", "评审", "招标"]) else "内容",
                content=chunk["content"],
                is_star_item=any(k in chunk["title"] for k in ["★", "星标", "废标", "否决", "红线", "关键条款", "实质性要求"]),
                source_file=filename,
            )
            db.add(section)
            created.append(section)

        # Key-field sections from LLM extraction
        if tender_info:
            scoring_text = self._extract_field_value(tender_info, "评分重点")
            if scoring_text and len(scoring_text) > 20:
                created.append(self._add_section(
                    db, project_id, "评分规则解析", "评审", scoring_text, True, filename
                ))

            tech_req = self._extract_field_value(tender_info, "技术要求")
            if tech_req and len(tech_req) > 20:
                created.append(self._add_section(
                    db, project_id, "技术要求", "评审", tech_req, True, filename
                ))

            qual_req = self._extract_field_value(tender_info, "必备资质")
            if qual_req and len(qual_req) > 20:
                created.append(self._add_section(
                    db, project_id, "资质要求", "评审", qual_req, True, filename
                ))

            # Extract star items from LLM response
            star_items_list = tender_info.get("星标项列表", [])
            if isinstance(star_items_list, list):
                for star_item in star_items_list:
                    if isinstance(star_item, dict):
                        star_name = star_item.get("name", "")
                        star_content = star_item.get("content", "")
                        if star_name and star_content:
                            created.append(self._add_section(
                                db, project_id, star_name, "评审", star_content, True, filename
                            ))

            # Update project extracted_fields
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                extracted = []
                for key in ["项目名称", "招标编号", "标书类型", "投标截止时间", "预算金额",
                            "标书起始时间", "标书结束时间", "是否有保证金", "保证金金额", "保证金形式",
                            "必备资质", "付款条款", "交付周期", "评分重点", "技术要求", "服务承诺",
                            "是否需要签字盖章", "是否有项目澄清会", "项目澄清会时间", "项目澄清会链接"]:
                    val = self._extract_field_value(tender_info, key)
                    if val:
                        extracted.append({"label": key, "value": val, "confidence": "85%"})
                if extracted:
                    project.extracted_fields = extracted

        # Placeholder business/tech sections expected by the frontend
        for name in BUSINESS_SECTIONS:
            created.append(self._add_section(
                db, project_id, name, "商务",
                f"【{name}】\n\n解析自招标文件 {filename}，请根据招标要求及公司实际情况填写。",
                name in BUSINESS_STAR, filename
            ))
        for name in TECH_SECTIONS:
            created.append(self._add_section(
                db, project_id, name, "技术",
                f"【{name}】\n\n解析自招标文件 {filename}，请根据技术规范书要求填写。",
                name in TECH_STAR, filename
            ))

        db.commit()
        return [ParsingSectionSummary.model_validate(s) for s in created]

    def _add_section(
        self, db: Session, project_id: str, name: str, sec_type: str,
        content: str, is_star: bool, filename: str
    ) -> ParsingSection:
        section = ParsingSection(
            id=f"sec_{uuid4().hex[:12]}",
            project_id=project_id,
            section_name=name,
            section_type=sec_type,
            content=content,
            is_star_item=is_star,
            source_file=filename,
        )
        db.add(section)
        return section

    def _extract_field_value(self, tender_info: dict, key: str) -> str:
        item = tender_info.get(key)
        if isinstance(item, dict):
            return str(item.get("value", ""))
        return str(item) if item else ""

    def _curate_text_for_llm(self, full_text: str, max_chars: int = 20000) -> str:
        """Curate text for LLM field extraction: include head, tail, and keyword-rich paragraphs."""
        if len(full_text) <= max_chars:
            return full_text

        # Strategy: head + keyword-rich middle + tail
        keywords = ["评分", "评标", "技术要求", "资质", "资格", "废标", "无效", "星标", "★",
                    "合同", "付款", "交付", "保证金", "保修", "质保"]
        paragraphs = full_text.split("\n")
        head_len = max_chars // 3
        tail_len = max_chars // 3
        middle_budget = max_chars - head_len - tail_len

        head = full_text[:head_len]
        tail = full_text[-tail_len:]

        important_middle: list[str] = []
        middle_text = full_text[head_len:-tail_len]
        for para in middle_text.split("\n"):
            if any(kw in para for kw in keywords):
                important_middle.append(para)
                if sum(len(p) for p in important_middle) >= middle_budget:
                    break

        curated = head + "\n\n...[中间内容筛选]...\n\n" + "\n".join(important_middle) + "\n\n...[末尾内容]...\n\n" + tail
        return curated[:max_chars]

    def _merge_tiny_chunks(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Merge chunks smaller than MIN_CHUNK_CHARS with adjacent chunks."""
        if not chunks:
            return chunks
        merged: list[dict[str, Any]] = [chunks[0].copy()]
        for chunk in chunks[1:]:
            last = merged[-1]
            if len(chunk["content"]) < MIN_CHUNK_CHARS:
                # Merge into previous
                last["content"] = last["content"] + "\n\n" + chunk["content"]
                last["end_page"] = chunk["end_page"]
                last["title"] = last["title"] if len(last["title"]) > len(chunk["title"]) else chunk["title"]
            elif len(last["content"]) < MIN_CHUNK_CHARS:
                # Previous was tiny, merge current into it
                last["content"] = last["content"] + "\n\n" + chunk["content"]
                last["end_page"] = chunk["end_page"]
            else:
                merged.append(chunk.copy())
        return merged

    def _create_placeholder_sections(self, db: Session, project_id: str, filename: str) -> list[ParsingSectionSummary]:
        """Fallback when no text could be extracted."""
        db.query(ParsingSection).filter(ParsingSection.project_id == project_id).delete()
        created: list[ParsingSection] = []
        for name in BUSINESS_SECTIONS:
            created.append(self._add_section(
                db, project_id, name, "商务",
                f"【{name}】\n\n上传文件：{filename}\n\n（请在下方编辑器中填写内容）",
                name in BUSINESS_STAR, filename
            ))
        for name in TECH_SECTIONS:
            created.append(self._add_section(
                db, project_id, name, "技术",
                f"【{name}】\n\n上传文件：{filename}\n\n（请在下方编辑器中填写内容）",
                name in TECH_STAR, filename
            ))
        db.commit()
        return [ParsingSectionSummary.model_validate(s) for s in created]

    def simulate_parse(self, db: Session, project_id: str, filename: str) -> list[ParsingSectionSummary]:
        """Legacy simulation entrypoint; now delegates to placeholder creation."""
        return self._create_placeholder_sections(db, project_id, filename)

    # --- APIs used by generation service ---

    def project_fields_map(self, db: Session, project_id: str) -> dict[str, str]:
        """Return extracted fields as a flat dict for generation service."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if project and project.extracted_fields:
            result: dict[str, str] = {}
            for item in project.extracted_fields:
                if isinstance(item, dict):
                    result[item.get("label", "")] = str(item.get("value", ""))
            return result
        # Fallback: try to build from parsing_sections content
        sections = db.query(ParsingSection).filter(ParsingSection.project_id == project_id).all()
        for s in sections:
            if s.section_name == "评分规则解析":
                return {"评分重点": s.content}
        return {}

    def get_project_context(self, db: Session, project_id: str) -> ParsingContext:
        """Return parsing context for generation service."""
        sections = (
            db.query(ParsingSection)
            .filter(ParsingSection.project_id == project_id)
            .order_by(ParsingSection.created_at.asc())
            .all()
        )
        parse_sections = [
            ParseSection(
                title=s.section_name,
                page="-",
                state="已解析" if s.content and len(s.content) > 20 else "待填充",
                source_text=s.content[:200] if s.content else "",
                source_file=s.source_file or "",
            )
            for s in sections
        ]
        # Build a source excerpt from the first few content sections
        excerpts: list[str] = []
        for s in sections:
            if s.section_type in ("评审", "内容") and s.content:
                excerpts.append(f"[{s.section_name}]\n{s.content[:500]}")
            if len("\n".join(excerpts)) > 3000:
                break
        return ParsingContext(
            parse_sections=parse_sections,
            source_excerpt="\n\n".join(excerpts),
        )


# Module-level singleton for imports
parsing_service = ParsingService()


# Keep module-level functions for backward compatibility with existing code
def get_or_create_project(db: Session, project_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return project


def list_sections(db: Session, project_id: str) -> list[ParsingSectionSummary]:
    return parsing_service.list_sections(db, project_id)


def get_section_detail(db: Session, project_id: str, section_id: str) -> ParsingSectionDetail:
    return parsing_service.get_section_detail(db, project_id, section_id)


def update_section(
    db: Session, project_id: str, section_id: str, payload: ParsingSectionUpdateRequest
) -> ParsingSectionDetail:
    return parsing_service.update_section(db, project_id, section_id, payload)


def simulate_parse(db: Session, project_id: str, filename: str) -> list[ParsingSectionSummary]:
    return parsing_service.simulate_parse(db, project_id, filename)
