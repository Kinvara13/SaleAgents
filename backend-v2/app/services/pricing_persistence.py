import logging
import math
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.pricing import (
    PricingCalculation,
    TechScoreEvaluation,
    CompetitorPrediction,
    BiddingGameSimulation,
)
from app.schemas.tech_score import TechScoreEvaluateResponse
from app.schemas.competitor_intel import CompetitorIntelPredictResponse
from app.schemas.bidding_game import BiddingGameSimulateResponse
from app.schemas.pricing import PricingCalculateResponse

logger = logging.getLogger(__name__)


def _normalize_competitor_name(name: str) -> str:
    return "".join(str(name or "").strip().lower().split())


def _safe_discount_value(value: object) -> float | None:
    try:
        discount = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(discount) or math.isinf(discount):
        return None
    if 0 <= discount <= 1:
        return discount
    if 1 < discount <= 100:
        return discount / 100
    return None


def build_competitor_history_profiles(
    db: Session,
    project_id: str | None = None,
    competitor_names: list[str] | None = None,
    limit: int = 50,
) -> tuple[list[dict], int]:
    normalized_targets = {
        _normalize_competitor_name(name): str(name).strip()
        for name in (competitor_names or [])
        if str(name).strip()
    }
    history_buckets: dict[str, dict] = {}

    def ensure_bucket(name: str) -> dict | None:
        clean_name = str(name or "").strip()
        if not clean_name:
            return None
        normalized = _normalize_competitor_name(clean_name)
        if normalized_targets and normalized not in normalized_targets:
            return None
        bucket = history_buckets.get(normalized)
        if bucket is None:
            bucket = {
                "name": normalized_targets.get(normalized, clean_name),
                "samples": [],
                "source_breakdown": {},
            }
            history_buckets[normalized] = bucket
        return bucket

    def add_sample(name: str, discount_value: object, source_key: str) -> None:
        bucket = ensure_bucket(name)
        if bucket is None:
            return
        normalized_discount = _safe_discount_value(discount_value)
        if normalized_discount is None:
            return
        bucket["samples"].append(normalized_discount)
        bucket["source_breakdown"][source_key] = bucket["source_breakdown"].get(source_key, 0) + 1

    prediction_records = list_competitor_predictions(db, project_id=project_id, limit=limit)
    simulation_records = list_bidding_game_simulations(db, project_id=project_id, limit=limit)
    logger.info(
        "Building competitor history profiles project_id=%s requested_competitors=%s prediction_records=%s simulation_records=%s",
        project_id or "ALL",
        len(normalized_targets),
        len(prediction_records),
        len(simulation_records),
    )

    for record in prediction_records:
        for competitor in record.input_competitors or []:
            add_sample(
                competitor.get("name", ""),
                competitor.get("historical_discount"),
                "manual_historical_input",
            )
        for prediction in record.predictions or []:
            add_sample(
                prediction.get("name", ""),
                prediction.get("point_estimate"),
                "intel_prediction",
            )

    for record in simulation_records:
        agent_configs = list(record.agent_configs or [])
        competitor_agent_configs = [agent for agent in agent_configs[1:] if _normalize_competitor_name(agent.get("name", ""))]
        for agent in competitor_agent_configs:
            add_sample(
                agent.get("name", ""),
                agent.get("discount_belief_mean"),
                "agent_prior_mean",
            )

        iterative_result = record.iterative_result or {}
        rounds = iterative_result.get("rounds") or []
        if rounds and competitor_agent_configs:
            for round_item in rounds:
                competitor_discounts = round_item.get("competitor_discounts") or []
                for idx, agent in enumerate(competitor_agent_configs):
                    if idx < len(competitor_discounts):
                        add_sample(
                            agent.get("name", ""),
                            competitor_discounts[idx],
                            "iterative_round",
                        )

    profiles: list[dict] = []
    for bucket in history_buckets.values():
        samples = bucket["samples"]
        if not samples:
            continue
        mean_value = sum(samples) / len(samples)
        if len(samples) > 1:
            variance = sum((value - mean_value) ** 2 for value in samples) / len(samples)
            std_value = math.sqrt(variance)
        else:
            std_value = 0.03
        profiles.append(
            {
                "name": bucket["name"],
                "discount_belief_mean": round(min(max(mean_value, 0.0), 1.0), 4),
                "discount_belief_std": round(min(max(std_value, 0.02), 0.5), 4),
                "sample_count": len(samples),
                "source_breakdown": bucket["source_breakdown"],
            }
        )

    profiles.sort(key=lambda item: (-item["sample_count"], item["name"]))
    logger.info(
        "Built competitor history profiles project_id=%s matched_profiles=%s",
        project_id or "ALL",
        len(profiles),
    )
    return profiles, len(prediction_records) + len(simulation_records)


def save_pricing_calculation(
    db: Session,
    project_id: str,
    response: PricingCalculateResponse,
    competitors: list[dict],
    user_id: str = "user-001",
) -> PricingCalculation:
    record = PricingCalculation(
        id=str(uuid.uuid4())[:16],
        project_id=project_id or "",
        budget=response.breakdown.budget,
        tech_score=response.breakdown.tech_score,
        discount_rate=response.breakdown.discount_rate,
        profit_margin=response.breakdown.profit_margin,
        tax_rate=response.breakdown.tax_rate,
        scoring_method=response.breakdown.scoring_method,
        k_value=response.breakdown.k_value,
        sensitivity=response.breakdown.sensitivity,
        price_score=response.our_price_score,
        total_score=response.total_score,
        rank=response.our_rank,
        ai_advice=response.ai_advice,
        competitors=competitors,
        user_id=user_id,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("Saved pricing calculation id=%s project=%s", record.id, project_id)
    return record


def save_tech_score_evaluation(
    db: Session,
    project_id: str,
    request_data: dict,
    response: TechScoreEvaluateResponse,
    user_id: str = "user-001",
) -> TechScoreEvaluation:
    record = TechScoreEvaluation(
        id=str(uuid.uuid4())[:16],
        project_id=project_id or "",
        objective_total=response.objective_score.total,
        subjective_total=response.subjective_score.total,
        total_tech_score=response.total_tech_score,
        confidence_range=response.confidence_range,
        needs_manual_review=response.needs_manual_review,
        objective_items=[item.model_dump() for item in response.objective_score.items],
        subjective_items=[item.model_dump() for item in response.subjective_score.items],
        scoring_criteria=request_data.get("scoring_criteria", {}),
        company_materials=request_data.get("company_materials", {}),
        user_id=user_id,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("Saved tech score evaluation id=%s project=%s", record.id, project_id)
    return record


def save_competitor_prediction(
    db: Session,
    project_id: str,
    input_competitors: list[dict],
    response: CompetitorIntelPredictResponse,
    user_id: str = "user-001",
) -> CompetitorPrediction:
    record = CompetitorPrediction(
        id=str(uuid.uuid4())[:16],
        project_id=project_id or "",
        predictions=[p.model_dump() for p in response.predictions],
        accomplice_groups=response.accomplice_groups,
        input_competitors=input_competitors,
        user_id=user_id,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("Saved competitor prediction id=%s project=%s", record.id, project_id)
    return record


def save_bidding_game_simulation(
    db: Session,
    project_id: str,
    scenario_config: dict,
    agent_configs: list[dict],
    response: BiddingGameSimulateResponse,
    user_id: str = "user-001",
) -> BiddingGameSimulation:
    record = BiddingGameSimulation(
        id=str(uuid.uuid4())[:16],
        project_id=project_id or "",
        recommended_price=response.optimal_bid.recommended_price,
        recommended_discount=response.optimal_bid.recommended_discount,
        win_probability=response.optimal_bid.win_probability,
        expected_profit=response.optimal_bid.expected_profit,
        confidence_interval=list(response.optimal_bid.confidence_interval),
        n_simulations=response.simulation_stats.n_simulations,
        simulation_stats=response.simulation_stats.model_dump(),
        sensitivity_result=response.sensitivity.model_dump(),
        nash_equilibrium=response.nash_equilibrium.model_dump(),
        bayesian_updates=[u.model_dump() for u in (response.bayesian_updates or [])],
        iterative_result=response.iterative_result.model_dump() if response.iterative_result else None,
        game_insights=response.game_insights,
        scenario_config=scenario_config,
    agent_configs=agent_configs,
    coalition_config=response.coalition_result.model_dump() if response.coalition_result else None,
    user_id=user_id,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("Saved bidding game simulation id=%s project=%s", record.id, project_id)
    return record


def list_pricing_calculations(
    db: Session, project_id: str | None = None, limit: int = 20
) -> list[PricingCalculation]:
    query = db.query(PricingCalculation)
    if project_id:
        query = query.filter(PricingCalculation.project_id == project_id)
    return query.order_by(PricingCalculation.created_at.desc()).limit(limit).all()


def list_tech_score_evaluations(
    db: Session, project_id: str | None = None, limit: int = 20
) -> list[TechScoreEvaluation]:
    query = db.query(TechScoreEvaluation)
    if project_id:
        query = query.filter(TechScoreEvaluation.project_id == project_id)
    return query.order_by(TechScoreEvaluation.created_at.desc()).limit(limit).all()


def list_competitor_predictions(
    db: Session, project_id: str | None = None, limit: int = 20
) -> list[CompetitorPrediction]:
    query = db.query(CompetitorPrediction)
    if project_id:
        query = query.filter(CompetitorPrediction.project_id == project_id)
    return query.order_by(CompetitorPrediction.created_at.desc()).limit(limit).all()


def list_bidding_game_simulations(
    db: Session, project_id: str | None = None, limit: int = 20
) -> list[BiddingGameSimulation]:
    query = db.query(BiddingGameSimulation)
    if project_id:
        query = query.filter(BiddingGameSimulation.project_id == project_id)
    return query.order_by(BiddingGameSimulation.created_at.desc()).limit(limit).all()
