"""Scoring service: auto-calculate document scores with LLM semantic evaluation."""

import json
import re
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.business_document import BusinessDocument
from app.models.technical_document import TechnicalDocument
from app.models.proposal_plan import ProposalPlan
from app.models.document_score_history import DocumentScoreHistory
from app.services.llm_client import llm_scoring_client


_PLACEHOLDER_PATTERNS = [
    re.compile(r"_{3,}"),
    re.compile(r"\[【[^】]*】"),
    re.compile(r"请填写"),
    re.compile(r"请描述"),
    re.compile(r"请详细描述"),
    re.compile(r"请列出"),
    re.compile(r"\{\{[^}]*\}\}"),
    re.compile(r"<[^>]+>"),
]


def _parse_max_score(score_point: str | None) -> float:
    if not score_point:
        return 0.0
    m = re.search(r"(\d+(?:\.\d+)?)\s*分", score_point)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)", score_point)
    if m:
        return float(m.group(1))
    return 0.0


def _count_placeholders(content: str) -> int:
    total = 0
    for pat in _PLACEHOLDER_PATTERNS:
        total += len(pat.findall(content))
    return total


def _rule_match_score(rule_description: str | None, content: str) -> tuple[float, list[str]]:
    if not rule_description:
        return 1.0, []

    keywords: list[str] = []
    for line in rule_description.splitlines():
        line = line.strip()
        if not line:
            continue
        cleaned = re.sub(r"^[\u2460-\u247f\d]+[\.\)）\s]+", "", line)
        cleaned = re.split(r"[\uff0c,\u3002\uff1b;]", cleaned)[0]
        if 4 <= len(cleaned) <= 30:
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


def _get_document(db: Session, project_id: str, doc_id: str, doc_kind: str):
    if doc_kind == "business":
        return db.query(BusinessDocument).filter(
            BusinessDocument.id == doc_id,
            BusinessDocument.project_id == project_id,
        ).first()
    elif doc_kind == "technical":
        return db.query(TechnicalDocument).filter(
            TechnicalDocument.id == doc_id,
            TechnicalDocument.project_id == project_id,
        ).first()
    elif doc_kind == "proposal":
        return db.query(ProposalPlan).filter(
            ProposalPlan.id == doc_id,
            ProposalPlan.project_id == project_id,
        ).first()
    return None


def _get_previous_score(db: Session, project_id: str, doc_id: str, doc_kind: str) -> float | None:
    last = (
        db.query(DocumentScoreHistory)
        .filter(
            DocumentScoreHistory.project_id == project_id,
            DocumentScoreHistory.doc_id == doc_id,
            DocumentScoreHistory.doc_kind == doc_kind,
        )
        .order_by(DocumentScoreHistory.created_at.desc())
        .first()
    )
    return last.score if last else None


def _save_score_history(
    db: Session,
    project_id: str,
    doc_id: str,
    doc_kind: str,
    score: float,
    max_score: float,
    breakdown: dict[str, Any],
) -> None:
    history = DocumentScoreHistory(
        id=str(uuid.uuid4()),
        project_id=project_id,
        doc_id=doc_id,
        doc_kind=doc_kind,
        score=score,
        max_score=max_score,
        breakdown=json.dumps(breakdown, ensure_ascii=False),
    )
    db.add(history)
    db.commit()


def calculate_score(
    db: Session,
    project_id: str,
    doc_id: str,
    doc_kind: str,
    *,
    use_llm: bool = True,
    routed_assets: list[str] | None = None,
) -> dict[str, Any]:
    doc = _get_document(db, project_id, doc_id, doc_kind)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    content = doc.editable_content or doc.original_content or ""
    max_score = _parse_max_score(doc.score_point)

    if max_score <= 0:
        return {
            "score": 0,
            "max_score": 0,
            "is_scored": False,
            "breakdown": {
                "completeness": 0,
                "rule_match": 0,
                "semantic_quality": 0,
                "asset_coverage": 0,
                "placeholder_count": _count_placeholders(content),
                "missing_keywords": [],
                "llm_reasoning": "",
            },
            "previous_score": None,
            "score_delta": None,
            "message": "该文档未设置评分分值，无法计算得分",
        }

    # 1. Completeness heuristic
    placeholder_count = _count_placeholders(content)
    content_length = len(content.strip())
    base_length = max(len(doc.original_content or ""), 100)

    if placeholder_count == 0 and content_length > base_length * 0.5:
        completeness = 1.0
    else:
        completeness = max(0.0, 1.0 - (placeholder_count / 10.0))

    # 2. Rule match heuristic
    rule_match, missing_keywords = _rule_match_score(doc.rule_description, content)

    # 3. LLM semantic scoring
    semantic_quality = 0.0
    asset_coverage = 0.0
    llm_reasoning = "LLM 未配置"
    if use_llm and llm_scoring_client.is_llm_ready:
        llm_result = llm_scoring_client.score_document(
            doc_name=doc.doc_name,
            score_point=doc.score_point,
            rule_description=doc.rule_description,
            content=content,
            routed_assets=routed_assets or [],
        )
        semantic_quality = llm_result["semantic_quality"]
        asset_coverage = llm_result["asset_coverage"]
        llm_reasoning = llm_result["reasoning"]

    # 4. Weighted total: completeness 30% + rule_match 20% + semantic_quality 35% + asset_coverage 15%
    score = max_score * (
        completeness * 0.30 +
        rule_match * 0.20 +
        semantic_quality * 0.35 +
        asset_coverage * 0.15
    )
    score = round(score, 2)

    previous_score = _get_previous_score(db, project_id, doc_id, doc_kind)
    score_delta = round(score - previous_score, 2) if previous_score is not None else None

    breakdown = {
        "completeness": round(completeness, 2),
        "rule_match": round(rule_match, 2),
        "semantic_quality": round(semantic_quality, 2),
        "asset_coverage": round(asset_coverage, 2),
        "placeholder_count": placeholder_count,
        "missing_keywords": missing_keywords,
        "llm_reasoning": llm_reasoning,
    }

    # Save history
    _save_score_history(db, project_id, doc_id, doc_kind, score, max_score, breakdown)

    return {
        "score": score,
        "max_score": max_score,
        "is_scored": True,
        "breakdown": breakdown,
        "previous_score": previous_score,
        "score_delta": score_delta,
        "message": None,
    }
