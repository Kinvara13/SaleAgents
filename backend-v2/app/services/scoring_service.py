"""Scoring service: auto-calculate document scores based on completeness."""

import re
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.business_document import BusinessDocument
from app.models.technical_document import TechnicalDocument


_PLACEHOLDER_PATTERNS = [
    re.compile(r"_{3,}"),            # _______
    re.compile(r"\[【[^\u3011]*】"),   # 【请填写】 类占位符
    re.compile(r"请填写"),
    re.compile(r"请描述"),
    re.compile(r"请详细描述"),
    re.compile(r"请列出"),
    re.compile(r"\{\{[^}]*\}\}"),  # {{placeholder}}
    re.compile(r"<[^>]+>"),          # HTML-like placeholders
]


def _parse_max_score(score_point: str | None) -> float:
    """Extract numeric score from strings like '商务评分 - 15分'."""
    if not score_point:
        return 0.0
    m = re.search(r"(\d+(?:\.\d+)?)\s*分", score_point)
    if m:
        return float(m.group(1))
    # Try just a number
    m = re.search(r"(\d+(?:\.\d+)?)", score_point)
    if m:
        return float(m.group(1))
    return 0.0


def _count_placeholders(content: str) -> int:
    """Count how many placeholder patterns exist in content."""
    total = 0
    for pat in _PLACEHOLDER_PATTERNS:
        total += len(pat.findall(content))
    return total


def _rule_match_score(rule_description: str | None, content: str) -> tuple[float, list[str]]:
    """
    Check whether the content addresses items mentioned in rule_description.
    Returns a 0-1 score and a list of matched/missing keywords.
    """
    if not rule_description:
        return 1.0, []

    # Extract key requirements from rule_description
    # Heuristic: split by punctuation and look for noun phrases
    keywords: list[str] = []
    for line in rule_description.splitlines():
        line = line.strip()
        if not line:
            continue
        # Remove common stop prefixes
        cleaned = re.sub(r"^[①-⑳\d]+[\.\)）\s]+", "", line)
        # Take first clause (before first punctuation)
        cleaned = re.split(r"[，,。.；;]", cleaned)[0]
        if len(cleaned) >= 4 and len(cleaned) <= 30:
            keywords.append(cleaned)

    if not keywords:
        return 1.0, []

    matched = []
    missing = []
    for kw in keywords:
        if kw in content or any(part in content for part in kw.split() if len(part) >= 4):
            matched.append(kw)
        else:
            missing.append(kw)

    score = len(matched) / len(keywords) if keywords else 1.0
    return score, missing


def calculate_score(
    db: Session,
    project_id: str,
    doc_id: str,
    doc_kind: str,
) -> dict[str, Any]:
    """Calculate document score."""
    if doc_kind == "business":
        doc = db.query(BusinessDocument).filter(
            BusinessDocument.id == doc_id,
            BusinessDocument.project_id == project_id,
        ).first()
    else:
        doc = db.query(TechnicalDocument).filter(
            TechnicalDocument.id == doc_id,
            TechnicalDocument.project_id == project_id,
        ).first()

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    content = doc.editable_content or doc.original_content or ""
    max_score = _parse_max_score(doc.score_point)

    # If no score point defined, treat as pass/fail or informational
    if max_score <= 0:
        return {
            "score": 0,
            "max_score": 0,
            "is_scored": False,
            "breakdown": {
                "completeness": 0,
                "rule_match": 0,
                "placeholder_count": _count_placeholders(content),
            },
            "message": "该文档未设置评分分值，无法计算得分",
        }

    # Completeness: fewer placeholders = higher score
    placeholder_count = _count_placeholders(content)
    content_length = len(content.strip())
    base_length = max(len(doc.original_content or ""), 100)

    if placeholder_count == 0 and content_length > base_length * 0.5:
        completeness = 1.0
    else:
        # Deduct proportionally: up to 10 placeholders can fully deduct
        completeness = max(0.0, 1.0 - (placeholder_count / 10.0))

    # Rule match
    rule_match, missing_keywords = _rule_match_score(doc.rule_description, content)

    # Weighted total
    score = max_score * (completeness * 0.6 + rule_match * 0.4)
    score = round(score, 2)

    return {
        "score": score,
        "max_score": max_score,
        "is_scored": True,
        "breakdown": {
            "completeness": round(completeness, 2),
            "rule_match": round(rule_match, 2),
            "placeholder_count": placeholder_count,
            "missing_keywords": missing_keywords,
        },
    }
