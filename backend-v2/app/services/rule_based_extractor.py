"""
Rule-based pre-extraction engine for Chinese tender/bidding documents.

Provides fast, deterministic field extraction using regex and keyword matching.
Serves as the first extraction layer before LLM-based extraction, with rule-based
results taking priority for structured fields (project name, bid number, deadline).

Usage:
    from app.services.rule_based_extractor import rule_extractor
    result = rule_extractor.extract_fields(raw_text)
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

HEADING_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^第[一二三四五六七八九十百\d]+章[、\.．\s]+"),
    re.compile(r"^第[一二三四五六七八九十\d]+节[、\.．\s]+"),
    re.compile(r"^[一二三四五六七八九十]+[、\.．]\s*"),
    re.compile(r"^\([一二三四五六七八九十\d]+\)"),
    re.compile(r"^\(\d+\)"),
    re.compile(r"^\d+[\.．]\d+\s+"),
    re.compile(r"^\d+[、\.．]\s+\S"),
    re.compile(r"^(附件|附录)\d*\s*"),
]

MAX_SECTION_CHARS = 5000
HEAD_PRESERVE = 3000
TAIL_PRESERVE = MAX_SECTION_CHARS - HEAD_PRESERVE

_STAR_SECTION_KEYWORDS: dict[str, str] = {
    "关键条款": "关键条款",
    "实质性要求": "实质性要求",
    "否决条款": "否决条款",
    "废标": "废标条款",
    "无效投标": "无效投标条款",
    "投标无效": "投标无效情形",
    "否决投标": "否决投标条款",
}


class RuleBasedExtractor:
    """Extract structured fields from raw Chinese tender/bidding text using regex and keyword matching."""

    def extract_fields(self, text: str) -> dict[str, Any]:
        """Extract all supported fields from *text*.

        Returns dict with keys: project_name, bid_number, deadline, scoring_criteria,
        disqualification_clauses, qualification_requirements, technical_requirements,
        contract_terms, commercial_terms, bidder_instructions, star_items, confidence.
        """
        if not text or not text.strip():
            logger.warning("extract_fields called with empty/whitespace text")
            return self._empty_result()

        text = text.strip()
        confidence: dict[str, float] = {}

        project_name, c = self.extract_project_name(text)
        confidence["project_name"] = c

        bid_number, c = self.extract_bid_number(text)
        confidence["bid_number"] = c

        deadline, c = self.extract_deadline(text)
        confidence["deadline"] = c

        scoring_criteria, c = self.extract_scoring_criteria(text)
        confidence["scoring_criteria"] = c

        disqualification_clauses, c = self.extract_disqualification_clauses(text)
        confidence["disqualification_clauses"] = c

        qualification_requirements, c = self.extract_qualification_requirements(text)
        confidence["qualification_requirements"] = c

        technical_requirements, c = self.extract_technical_requirements(text)
        confidence["technical_requirements"] = c

        contract_terms, c = self.extract_contract_terms(text)
        confidence["contract_terms"] = c

        commercial_terms, c = self.extract_commercial_terms(text)
        confidence["commercial_terms"] = c

        bidder_instructions, c = self.extract_bidder_instructions(text)
        confidence["bidder_instructions"] = c

        star_items, c = self.extract_star_items(text)
        confidence["star_items"] = c

        result = {
            "project_name": project_name,
            "bid_number": bid_number,
            "deadline": deadline,
            "scoring_criteria": scoring_criteria,
            "disqualification_clauses": disqualification_clauses,
            "qualification_requirements": qualification_requirements,
            "technical_requirements": technical_requirements,
            "contract_terms": contract_terms,
            "commercial_terms": commercial_terms,
            "bidder_instructions": bidder_instructions,
            "star_items": star_items,
            "confidence": confidence,
        }

        extracted_count = sum(
            1 for k, v in result.items()
            if k not in ("star_items", "confidence") and v
        )
        logger.info(
            "Rule-based extraction complete: %d/%d fields extracted",
            extracted_count,
            len(result) - 2,
        )
        return result

    def extract_project_name(self, text: str) -> tuple[str, float]:
        """Extract project name via keyword patterns.

        Tries explicit labels (项目名称/招标项目/采购项目/工程名称) first,
        then first meaningful line inside a "招标公告" section.
        """
        label_patterns = [
            r"(?:项目名称|招标项目|采购项目|工程名称|项目标题)\s*[：:]\s*(.+)",
        ]
        for pat in label_patterns:
            m = re.search(pat, text)
            if m:
                name = self._clean_value(m.group(1))
                if name:
                    logger.debug("Project name extracted via label: %s", name[:60])
                    return name, 0.9

        m = re.search(r"招标公告[^\n]*\n\s*(.+)", text)
        if m:
            candidate = self._clean_value(m.group(1))
            if candidate and not re.match(r"^[\d年月日\-/\.]", candidate):
                logger.debug("Project name extracted from 招标公告 header: %s", candidate[:60])
                return candidate, 0.6

        return "", 0.0

    def extract_bid_number(self, text: str) -> tuple[str, float]:
        """Extract bid/project number.

        Tries explicit labels first, then falls back to alphanumeric code
        patterns (5-30 chars) near the top of the document.
        """
        label_patterns = [
            r"(?:招标编号|项目编号|采购编号|标书编号|招标号|项目号|编号)\s*[：:]\s*([A-Za-z0-9\-_（）\(\)]{5,30})",
        ]
        for pat in label_patterns:
            m = re.search(pat, text)
            if m:
                num = m.group(1).strip()
                logger.debug("Bid number extracted via label: %s", num)
                return num, 0.9

        top = text[:2000]
        fallback = re.findall(r"(?<![A-Za-z0-9])([A-Za-z0-9][\-_A-Za-z0-9]{4,29})(?![A-Za-z0-9])", top)
        for candidate in fallback:
            if re.match(r"^\d{4}[\-年]", candidate):
                continue
            if len(candidate) >= 5:
                logger.debug("Bid number extracted via fallback pattern: %s", candidate)
                return candidate, 0.4

        return "", 0.0

    def extract_deadline(self, text: str) -> tuple[str, float]:
        """Extract bid submission deadline (date + time).

        Matches formats like 2024年12月31日 09:30, 2024-12-31 09:30, 2024/12/31 09:30:00
        with optional label prefix (投标截止时间/递交截止时间/开标时间).
        """
        date_pat = r"(\d{4})\s*[年\-/\.]\s*(\d{1,2})\s*[月\-/\.]\s*(\d{1,2})\s*日?"
        time_pat = r"(\d{1,2})\s*[：:时]\s*(\d{1,2})(?:\s*[：:分]\s*(\d{1,2}))?"

        label_keywords = [
            "投标截止时间", "递交截止时间", "投标截止日期",
            "开标时间", "截止时间", "截止日期", "报名截止",
            "提交截止", "响应截止",
        ]
        for kw in label_keywords:
            pattern = re.escape(kw) + r"[^\n]{0,10}?" + date_pat + r"\s*" + time_pat + r"?"
            m = re.search(pattern, text)
            if m:
                dt_str = self._format_datetime(m)
                if dt_str:
                    logger.debug("Deadline extracted via label '%s': %s", kw, dt_str)
                    return dt_str, 0.95

        for kw in label_keywords:
            pattern = re.escape(kw) + r"[^\n]{0,10}?" + date_pat
            m = re.search(pattern, text)
            if m:
                dt_str = self._format_date_only(m)
                if dt_str:
                    logger.debug("Deadline date-only via label '%s': %s", kw, dt_str)
                    return dt_str, 0.8

        top = text[:3000]
        for m in re.finditer(date_pat + r"\s*" + time_pat + r"?", top):
            dt_str = self._format_datetime(m)
            if dt_str:
                start = max(0, m.start() - 50)
                ctx = top[start : m.end()]
                if any(kw in ctx for kw in ["截止", "开标", "递交", "提交", "到期"]):
                    logger.debug("Deadline extracted via context fallback: %s", dt_str)
                    return dt_str, 0.6

        return "", 0.0

    def extract_star_items(self, text: str) -> tuple[list[dict[str, str]], float]:
        """Extract items marked with ★ or * (critical/key items).

        Returns list of dicts: [{name, content, source_section}].
        """
        items: list[dict[str, str]] = []

        star_pattern = re.compile(r"[★\*]\s*(.+?)(?:\n|$)", re.MULTILINE)
        for m in star_pattern.finditer(text):
            content = m.group(1).strip()
            if not content:
                continue
            source = self._find_nearest_section(text, m.start())
            items.append({
                "name": self._extract_item_name(content),
                "content": content,
                "source_section": source,
            })

        critical_sections = ["关键条款", "实质性要求", "否决条款"]
        for section_kw in critical_sections:
            section_content, _ = self._extract_section_by_keywords(
                text, [section_kw], max_chars=3000
            )
            if section_content:
                for line in section_content.split("\n"):
                    line = line.strip()
                    if line and len(line) > 5:
                        items.append({
                            "name": section_kw,
                            "content": line,
                            "source_section": section_kw,
                        })

        seen: set[str] = set()
        unique_items: list[dict[str, str]] = []
        for item in items:
            key = item["content"][:100]
            if key not in seen:
                seen.add(key)
                unique_items.append(item)

        confidence = 0.8 if unique_items else 0.0
        if unique_items:
            logger.debug("Extracted %d star/critical items", len(unique_items))
        return unique_items, confidence

    def extract_scoring_criteria(self, text: str) -> tuple[str, float]:
        """Extract scoring/evaluation criteria section."""
        return self._extract_section_by_keywords(
            text,
            ["评分标准", "评标办法", "评审标准", "评分细则", "评分规则", "评标标准"],
        )

    def extract_disqualification_clauses(self, text: str) -> tuple[str, float]:
        """Extract disqualification / invalid-bid clauses."""
        return self._extract_section_by_keywords(
            text,
            ["废标", "无效投标", "否决投标", "投标无效情形", "废标条款", "不合格投标"],
        )

    def extract_qualification_requirements(self, text: str) -> tuple[str, float]:
        """Extract qualification requirements section."""
        return self._extract_section_by_keywords(
            text,
            ["资格审查", "资质要求", "投标人资格", "资格条件", "投标资格", "供应商资格"],
        )

    def extract_technical_requirements(self, text: str) -> tuple[str, float]:
        """Extract technical requirements section."""
        return self._extract_section_by_keywords(
            text,
            ["技术要求", "技术规格", "技术规范", "技术标准", "技术参数", "技术方案要求"],
        )

    def extract_contract_terms(self, text: str) -> tuple[str, float]:
        """Extract contract terms section."""
        return self._extract_section_by_keywords(
            text,
            ["合同条款", "合同条件", "合同主要条款", "合同文本"],
        )

    def extract_commercial_terms(self, text: str) -> tuple[str, float]:
        """Extract commercial terms section."""
        return self._extract_section_by_keywords(
            text,
            ["商务条款", "商务要求", "付款方式", "保证金", "商务条件", "履约保证金", "付款条件"],
        )

    def extract_bidder_instructions(self, text: str) -> tuple[str, float]:
        """Extract bidder instructions section."""
        return self._extract_section_by_keywords(
            text,
            ["投标人须知", "投标须知", "投标人须知前附表", "投标须知前附表"],
        )

    def _extract_section_by_keywords(
        self,
        text: str,
        keywords: list[str],
        max_chars: int = MAX_SECTION_CHARS,
    ) -> tuple[str, float]:
        """Find a section by keyword headings and extract its content.

        Searches for a line containing one of *keywords* that looks like a heading,
        extracts content from that line to the next detected heading, and truncates
        if > *max_chars* (head + tail preservation).

        Returns (content, confidence).
        """
        lines = text.split("\n")

        start_idx: int | None = None
        matched_kw = ""
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            for kw in keywords:
                if kw in stripped:
                    if self._looks_like_heading(stripped, kw):
                        start_idx = i
                        matched_kw = kw
                        break
            if start_idx is not None:
                break

        if start_idx is None:
            return "", 0.0

        end_idx = len(lines)
        for j in range(start_idx + 1, len(lines)):
            stripped = lines[j].strip()
            if stripped and self._is_heading_line(stripped):
                end_idx = j
                break

        section_text = "\n".join(lines[start_idx:end_idx]).strip()

        if not section_text:
            return "", 0.0

        if len(section_text) > max_chars:
            section_text = self._truncate_section(section_text, max_chars)
            logger.debug(
                "Section '%s' truncated from %d to %d chars",
                matched_kw,
                len("\n".join(lines[start_idx:end_idx])),
                max_chars,
            )

        confidence = 0.85 if len(section_text) > 50 else 0.5
        logger.debug(
            "Section '%s' extracted: %d chars, confidence=%.2f",
            matched_kw,
            len(section_text),
            confidence,
        )
        return section_text, confidence

    def _looks_like_heading(self, line: str, keyword: str) -> bool:
        """Check if *line* containing *keyword* looks like a section heading.

        A heading-like line is short (< 80 chars) and the keyword appears
        near the start, or the line matches a known heading pattern.
        """
        for pat in HEADING_PATTERNS:
            if pat.match(line):
                return True

        kw_pos = line.find(keyword)
        if kw_pos >= 0 and len(line) < 80:
            if kw_pos < 30 or len(line) < 40:
                return True

        return False

    def _is_heading_line(self, line: str) -> bool:
        """Check if *line* is a section heading (used to detect section boundaries)."""
        for pat in HEADING_PATTERNS:
            if pat.match(line):
                return True
        return False

    def _find_nearest_section(self, text: str, position: int) -> str:
        """Find the nearest section heading before *position* in *text*."""
        before = text[:position]
        lines = before.split("\n")
        for line in reversed(lines):
            stripped = line.strip()
            if stripped:
                for pat in HEADING_PATTERNS:
                    if pat.match(stripped):
                        return stripped[:60]
                for kw, label in _STAR_SECTION_KEYWORDS.items():
                    if kw in stripped:
                        return label
                if len(stripped) < 50:
                    return stripped[:60]
        return "未知来源"

    def _extract_item_name(self, content: str) -> str:
        """Derive a short name from star-item content."""
        m = re.match(r"(.{2,20})\s*[：:]", content)
        if m:
            return m.group(1).strip()
        return content[:30].strip()

    def _truncate_section(self, text: str, max_chars: int) -> str:
        """Truncate *text* preserving head and tail."""
        if len(text) <= max_chars:
            return text
        head = text[:HEAD_PRESERVE]
        tail = text[-TAIL_PRESERVE:]
        return f"{head}\n\n... [中间部分已省略，共{len(text)}字符] ...\n\n{tail}"

    def _format_datetime(self, m: re.Match[str]) -> str:
        """Format a regex match into a standard datetime string."""
        try:
            year, month, day = m.group(1), m.group(2), m.group(3)
            parts = [f"{year}-{int(month):02d}-{int(day):02d}"]
            if m.group(4) is not None:
                hour = int(m.group(4))
                minute = int(m.group(5))
                second = int(m.group(6)) if m.group(6) else 0
                parts.append(f"{hour:02d}:{minute:02d}:{second:02d}")
            return " ".join(parts)
        except (IndexError, ValueError):
            return ""

    def _format_date_only(self, m: re.Match[str]) -> str:
        """Format a regex match containing only a date."""
        try:
            year, month, day = m.group(1), m.group(2), m.group(3)
            return f"{year}-{int(month):02d}-{int(day):02d}"
        except (IndexError, ValueError):
            return ""

    @staticmethod
    def _clean_value(raw: str) -> str:
        """Clean an extracted value: strip whitespace, trailing punctuation."""
        val = raw.strip()
        val = re.sub(r"[，。；,;.\s]+$", "", val)
        for suffix in ["招标公告", "采购公告", "竞争性谈判", "公开招标"]:
            if val.endswith(suffix):
                val = val[: -len(suffix)].strip()
        return val

    @staticmethod
    def _empty_result() -> dict[str, Any]:
        """Return an empty result dict with correct structure."""
        return {
            "project_name": "",
            "bid_number": "",
            "deadline": "",
            "scoring_criteria": "",
            "disqualification_clauses": "",
            "qualification_requirements": "",
            "technical_requirements": "",
            "contract_terms": "",
            "commercial_terms": "",
            "bidder_instructions": "",
            "star_items": [],
            "confidence": {},
        }


rule_extractor = RuleBasedExtractor()
