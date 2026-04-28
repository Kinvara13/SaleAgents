import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.bidding_game import (
    BiddingGameHistoryLearningRequest,
    BiddingGameHistoryLearningResponse,
    BiddingGameSimulateRequest,
    BiddingGameSimulateResponse,
    ABTestRequest,
    ABTestResponse,
)
from app.services import bidding_game_engine
from app.services.pricing_persistence import (
    build_competitor_history_profiles,
    save_bidding_game_simulation,
)
from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.auth import UserInfoResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/simulate", response_model=BiddingGameSimulateResponse, status_code=status.HTTP_200_OK)
def simulate_bidding_game(
    payload: BiddingGameSimulateRequest,
    current_user: UserInfoResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BiddingGameSimulateResponse:
    logger.info(
        "Received bidding game simulation request project_id=%s user_id=%s competitors=%s method=%s",
        payload.project_id or "",
        getattr(current_user, "id", "unknown"),
        len(payload.competitor_agents),
        payload.simulation_config.method,
    )
    result = bidding_game_engine.simulate_bidding_game(payload)
    try:
        save_bidding_game_simulation(
            db=db,
            project_id=payload.project_id or "",
            scenario_config=payload.scenario.model_dump(),
            agent_configs=[
                payload.our_agent.model_dump(),
                *[a.model_dump() for a in payload.competitor_agents],
            ],
            response=result,
            user_id=current_user.id if hasattr(current_user, "id") else "user-001",
        )
    except Exception as exc:
        logger.warning("Failed to persist bidding game simulation: %s", exc)
    return result


@router.post(
    "/history-learning",
    response_model=BiddingGameHistoryLearningResponse,
    status_code=status.HTTP_200_OK,
)
def learn_bidding_game_history(
    payload: BiddingGameHistoryLearningRequest,
    current_user: UserInfoResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BiddingGameHistoryLearningResponse:
    logger.info(
        "Received bidding game history learning request project_id=%s user_id=%s requested_competitors=%s limit=%s",
        payload.project_id or "",
        getattr(current_user, "id", "unknown"),
        len(payload.competitor_names),
        payload.limit,
    )
    profiles, total_records_scanned = build_competitor_history_profiles(
        db=db,
        project_id=payload.project_id,
        competitor_names=payload.competitor_names,
        limit=payload.limit,
    )
    response = BiddingGameHistoryLearningResponse(
        project_id=payload.project_id,
        profiles=profiles,
        total_records_scanned=total_records_scanned,
        matched_competitor_count=len(profiles),
        message="History learning completed" if profiles else "No historical samples matched the requested competitors",
    )
    logger.info(
        "Completed bidding game history learning project_id=%s matched_competitors=%s scanned_records=%s",
        payload.project_id or "",
        response.matched_competitor_count,
        response.total_records_scanned,
    )
    return response


@router.post("/ab-test", response_model=ABTestResponse, status_code=status.HTTP_200_OK)
def run_ab_test(
    payload: ABTestRequest,
    current_user: UserInfoResponse = Depends(get_current_user),
) -> ABTestResponse:
    logger.info(
        "Received A/B test request project_id=%s user_id=%s strategy_groups=%d competitors=%d n_sim=%d",
        payload.project_id or "",
        getattr(current_user, "id", "unknown"),
        len(payload.strategy_groups),
        len(payload.competitor_agents),
        payload.n_simulations,
    )
    result = bidding_game_engine.run_ab_test(payload)
    logger.info(
        "A/B test completed best_strategy=%s best_win=%.2f",
        result.comparison.best_strategy,
        result.comparison.best_win_probability,
    )
    return result
