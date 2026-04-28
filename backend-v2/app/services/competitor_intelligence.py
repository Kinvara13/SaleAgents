import logging
import math
import random
from typing import Any

from app.schemas.competitor_intel import (
    CompetitorIntelPredictRequest,
    CompetitorIntelPredictResponse,
    CompetitorPrediction,
    DiscountDistribution,
    EvidenceItem,
    AccompliceAlert,
)

logger = logging.getLogger(__name__)

_MARKET_POSITION_PROFILES = {
    "price_killer": {"discount_bias": 0.15, "std_modifier": 0.8},
    "tech_oriented": {"discount_bias": -0.05, "std_modifier": 1.2},
    "balanced": {"discount_bias": 0.0, "std_modifier": 1.0},
}

_INDUSTRY_BENCHMARKS: dict[str, dict] = {
    "IT服务": {"avg_discount": 0.21, "std": 0.12},
    "软件开发": {"avg_discount": 0.18, "std": 0.10},
    "系统集成": {"avg_discount": 0.15, "std": 0.09},
    "运维服务": {"avg_discount": 0.12, "std": 0.08},
    "通信": {"avg_discount": 0.20, "std": 0.11},
    "default": {"avg_discount": 0.18, "std": 0.10},
}

_COMPANY_SIZE_FACTORS = {
    "大型": {"discount_adj": -0.03, "win_rate": 0.35},
    "中型": {"discount_adj": 0.02, "win_rate": 0.25},
    "小型": {"discount_adj": 0.08, "win_rate": 0.15},
    "": {"discount_adj": 0.0, "win_rate": 0.25},
}

_AFFILIATED_COMPANY_PATTERNS: list[dict[str, list[str]]] = [
    {"group": "华为系", "keywords": ["华为", "华为技术", "华为软件", "华为终端"]},
    {"group": "中兴系", "keywords": ["中兴", "中兴通讯", "中兴软件"]},
    {"group": "亚信系", "keywords": ["亚信", "亚信科技", "亚信安全"]},
    {"group": "东软系", "keywords": ["东软", "东软集团", "东软载波"]},
    {"group": "浪潮系", "keywords": ["浪潮", "浪潮信息", "浪潮软件"]},
    {"group": "中软系", "keywords": ["中软", "中软国际", "中国软件"]},
    {"group": "软通系", "keywords": ["软通", "软通动力", "软通智慧"]},
    {"group": "博彦系", "keywords": ["博彦", "博彦科技", "博彦嘉成"]},
]


def _infer_market_position(name: str, industry: str, size: str) -> str:
    large_company_keywords = ["华为", "中兴", "亚信", "东软", "浪潮", "中软", "软通", "博彦"]
    for kw in large_company_keywords:
        if kw in name:
            return "tech_oriented"
    if size == "小型":
        return "price_killer"
    return "balanced"


def _beta_params_from_mean_std(mean: float, std: float) -> tuple[float, float]:
    mean = max(0.01, min(0.99, mean))
    std = max(0.01, min(0.4, std))
    variance = std * std
    temp = mean * (1 - mean) / variance - 1
    if temp <= 0:
        return 2.0, 2.0
    alpha = max(0.5, mean * temp)
    beta_param = max(0.5, (1 - mean) * temp)
    return round(alpha, 2), round(beta_param, 2)


def _beta_ppf(mean: float, std: float, percentile: float) -> float:
    alpha, beta_param = _beta_params_from_mean_std(mean, std)
    try:
        from scipy.stats import beta as beta_dist
        return round(float(beta_dist.ppf(percentile, alpha, beta_param)), 4)
    except ImportError:
        z_scores = {0.1: -1.28, 0.5: 0.0, 0.9: 1.28}
        z = z_scores.get(percentile, 0.0)
        val = mean + z * std
        return round(max(0.01, min(0.99, val)), 4)


def _generate_evidence(
    name: str, industry: str, historical_discount: float | None
) -> list[EvidenceItem]:
    items = []
    if historical_discount is not None:
        items.append(EvidenceItem(
            source="历史投标记录",
            reliability="A",
            date="近期",
            detail=f"{name}历史折扣率约{historical_discount:.0%}",
        ))
    if industry:
        items.append(EvidenceItem(
            source="行业基准数据",
            reliability="B",
            date="2025",
            detail=f"{industry}行业平均折扣率参考",
        ))
    items.append(EvidenceItem(
        source="市场经验评估",
        reliability="C",
        date="当前",
        detail="基于销售经验的主观估计",
    ))
    return items


def _detect_accomplice_probability(
    name: str, discount: float, avg_discount: float, std: float
) -> float:
    if std < 0.01:
        return 0.0
    z_score = abs(discount - avg_discount) / std
    if z_score > 2.5:
        return min(0.8, 0.3 + z_score * 0.1)
    if z_score > 1.5:
        return min(0.4, 0.1 + z_score * 0.05)
    return 0.0


def _find_affiliated_group(name: str) -> str | None:
    """Check if a company name belongs to a known affiliated group"""
    for pattern in _AFFILIATED_COMPANY_PATTERNS:
        for kw in pattern["keywords"]:
            if kw in name:
                return pattern["group"]
    return None


def _compute_name_similarity(name_a: str, name_b: str) -> float:
    """Compute name similarity based on shared substrings (2-gram Jaccard)"""
    def _bigrams(s: str) -> set[str]:
        s = s.strip()
        return {s[i:i+2] for i in range(len(s) - 1)} if len(s) >= 2 else {s}

    bg_a = _bigrams(name_a)
    bg_b = _bigrams(name_b)
    if not bg_a or not bg_b:
        return 0.0
    intersection = bg_a & bg_b
    union = bg_a | bg_b
    return len(intersection) / len(union) if union else 0.0


def _detect_accomplice_alerts(
    predictions: list[CompetitorPrediction],
    all_estimates: list[float],
) -> tuple[list[AccompliceAlert | None], list[list[str]]]:
    """Multi-dimensional accomplice detection with affiliated company identification"""
    n = len(predictions)
    if n < 2:
        return [None] * n, []

    avg_discount = sum(all_estimates) / len(all_estimates) if all_estimates else 0.18
    std_discount = math.sqrt(
        sum((x - avg_discount) ** 2 for x in all_estimates) / len(all_estimates)
    ) if len(all_estimates) > 1 else 0.1

    name_to_group: dict[str, str | None] = {}
    for pred in predictions:
        name_to_group[pred.name] = _find_affiliated_group(pred.name)

    name_similarity_pairs: list[tuple[int, int, float]] = []
    for i in range(n):
        for j in range(i + 1, n):
            sim = _compute_name_similarity(predictions[i].name, predictions[j].name)
            if sim > 0.3:
                name_similarity_pairs.append((i, j, sim))

    alerts: list[AccompliceAlert | None] = []
    for i, pred in enumerate(predictions):
        reasons: list[str] = []
        related: list[str] = []
        anomaly_score = 0.0

        z_score = abs(all_estimates[i] - avg_discount) / std_discount if std_discount > 0.01 else 0.0
        if z_score > 2.5:
            anomaly_score += 0.35
            direction = "偏高" if all_estimates[i] > avg_discount else "偏低"
            reasons.append(f"折扣率{direction}，Z-score={z_score:.1f}，偏离行业均值{abs(all_estimates[i] - avg_discount):.1%}")
        elif z_score > 1.5:
            anomaly_score += 0.15
            reasons.append(f"折扣率偏离均值{abs(all_estimates[i] - avg_discount):.1%}，存在一定异常")

        group = name_to_group.get(pred.name)
        if group:
            group_members = [p.name for p in predictions if name_to_group.get(p.name) == group]
            if len(group_members) > 1:
                anomaly_score += 0.3
                others = [m for m in group_members if m != pred.name]
                related.extend(others)
                reasons.append(f"属于{group}，同组参与投标: {', '.join(others)}")

        for (ai, bi, sim) in name_similarity_pairs:
            if ai == i or bi == i:
                partner_idx = bi if ai == i else ai
                partner_name = predictions[partner_idx].name
                anomaly_score += 0.2 * sim
                related.append(partner_name)
                reasons.append(f"与{partner_name}名称相似度{sim:.0%}，可能存在关联")

        if pred.market_position == "price_killer" and all_estimates[i] < avg_discount * 0.7:
            anomaly_score += 0.15
            reasons.append("低价型公司报价异常偏低，可能为陪标拉低基准价")

        if all_estimates[i] > avg_discount * 1.5 and std_discount > 0.05:
            anomaly_score += 0.2
            reasons.append("折扣率异常偏高，可能为陪标拉高基准价")

        anomaly_score = min(1.0, anomaly_score)

        if anomaly_score >= 0.5:
            risk_level = "high"
        elif anomaly_score >= 0.25:
            risk_level = "medium"
        elif anomaly_score > 0.0:
            risk_level = "low"
        else:
            alerts.append(None)
            continue

        alerts.append(AccompliceAlert(
            risk_level=risk_level,
            reasons=reasons,
            related_companies=list(set(related)),
            anomaly_score=round(anomaly_score, 4),
        ))

    accomplice_groups: list[list[str]] = []
    processed_groups: set[str] = set()
    for pred in predictions:
        group = name_to_group.get(pred.name)
        if group and group not in processed_groups:
            members = [p.name for p in predictions if name_to_group.get(p.name) == group]
            if len(members) > 1:
                accomplice_groups.append(members)
                processed_groups.add(group)

    for (ai, bi, sim) in name_similarity_pairs:
        if sim > 0.5:
            pair = [predictions[ai].name, predictions[bi].name]
            already_covered = any(
                all(m in g for m in pair) for g in accomplice_groups
            )
            if not already_covered:
                accomplice_groups.append(pair)

    return alerts, accomplice_groups


def predict_competitor_intel(
    payload: CompetitorIntelPredictRequest,
) -> CompetitorIntelPredictResponse:
    logger.info("Predicting competitor intel for %d competitors", len(payload.competitors))

    predictions = []
    all_estimates = []

    for comp in payload.competitors:
        market_pos = _infer_market_position(comp.name, comp.industry, comp.size)
        profile = _MARKET_POSITION_PROFILES.get(market_pos, _MARKET_POSITION_PROFILES["balanced"])

        industry_key = comp.industry if comp.industry in _INDUSTRY_BENCHMARKS else "default"
        benchmark = _INDUSTRY_BENCHMARKS[industry_key]

        base_discount = comp.historical_discount if comp.historical_discount is not None else benchmark["avg_discount"]
        base_std = benchmark["std"]

        size_factor = _COMPANY_SIZE_FACTORS.get(comp.size, _COMPANY_SIZE_FACTORS[""])
        adjusted_discount = base_discount + profile["discount_bias"] + size_factor["discount_adj"]
        adjusted_std = base_std * profile["std_modifier"]

        adjusted_discount = max(0.01, min(0.95, adjusted_discount))
        adjusted_std = max(0.02, min(0.3, adjusted_std))

        all_estimates.append(adjusted_discount)

        p10 = _beta_ppf(adjusted_discount, adjusted_std, 0.1)
        p50 = _beta_ppf(adjusted_discount, adjusted_std, 0.5)
        p90 = _beta_ppf(adjusted_discount, adjusted_std, 0.9)
        alpha, beta_param = _beta_params_from_mean_std(adjusted_discount, adjusted_std)

        evidence = _generate_evidence(comp.name, comp.industry, comp.historical_discount)

        confidence = 0.7 if comp.historical_discount is not None else 0.45
        if comp.industry:
            confidence += 0.1
        confidence = min(0.9, confidence)

        predictions.append(CompetitorPrediction(
            name=comp.name,
            point_estimate=round(adjusted_discount, 4),
            distribution=DiscountDistribution(
                p10=p10, p50=p50, p90=p90,
                distribution_type="beta",
                alpha=alpha, beta_param=beta_param,
            ),
            confidence=confidence,
            evidence=evidence,
            accomplice_probability=0.0,
            market_position=market_pos,
        ))

    if len(all_estimates) > 1:
        avg = sum(all_estimates) / len(all_estimates)
        std_pop = math.sqrt(sum((x - avg) ** 2 for x in all_estimates) / len(all_estimates))
        for i, pred in enumerate(predictions):
            pred.accomplice_probability = round(
                _detect_accomplice_probability(pred.name, all_estimates[i], avg, std_pop), 4
            )

    alerts, accomplice_groups = _detect_accomplice_alerts(predictions, all_estimates)
    for i, alert in enumerate(alerts):
        if alert:
            predictions[i].accomplice_alert = alert
            if alert.risk_level in ("high", "medium"):
                predictions[i].accomplice_probability = max(
                    predictions[i].accomplice_probability,
                    alert.anomaly_score,
                )

    if accomplice_groups:
        logger.info("Detected %d potential accomplice groups: %s", len(accomplice_groups), accomplice_groups)

    return CompetitorIntelPredictResponse(
        predictions=predictions,
        accomplice_groups=accomplice_groups,
    )
