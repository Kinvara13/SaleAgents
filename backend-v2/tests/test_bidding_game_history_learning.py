from datetime import datetime

from app.models.pricing import BiddingGameSimulation, CompetitorPrediction
from tests.conftest import TestingSessionLocal


def test_bidding_game_history_learning(client):
    project_id = "history-learning-test"
    db = TestingSessionLocal()
    try:
        db.add(
            CompetitorPrediction(
                id="cp-history-001",
                project_id=project_id,
                predictions=[
                    {"name": "亚信", "point_estimate": 0.21},
                    {"name": "中软", "point_estimate": 0.24},
                ],
                accomplice_groups=[],
                input_competitors=[
                    {"name": "亚信", "historical_discount": 0.19},
                    {"name": "中软", "historical_discount": None},
                ],
                user_id="test_user_123",
                created_at=datetime.utcnow(),
            )
        )
        db.add(
            BiddingGameSimulation(
                id="bg-history-001",
                project_id=project_id,
                recommended_price=2000000,
                recommended_discount=0.2,
                win_probability=0.65,
                expected_profit=180000,
                confidence_interval=[0.18, 0.22],
                n_simulations=500,
                simulation_stats={},
                sensitivity_result={},
                nash_equilibrium={},
                bayesian_updates=[],
                iterative_result={
                    "rounds": [
                        {"round_no": 1, "competitor_discounts": [0.18, 0.25]},
                        {"round_no": 2, "competitor_discounts": [0.22, 0.27]},
                    ]
                },
                game_insights=[],
                scenario_config={},
                agent_configs=[
                    {"name": "我方", "discount_belief_mean": 0.2},
                    {"name": "亚信", "discount_belief_mean": 0.2},
                    {"name": "中软", "discount_belief_mean": 0.26},
                ],
                user_id="test_user_123",
                created_at=datetime.utcnow(),
            )
        )
        db.commit()
    finally:
        db.close()

    response = client.post(
        "/api/v1/bidding-game/history-learning",
        json={
            "project_id": project_id,
            "competitor_names": ["亚信", "中软"],
            "limit": 20,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == project_id
    assert payload["total_records_scanned"] == 2
    assert payload["matched_competitor_count"] == 2

    profiles = {item["name"]: item for item in payload["profiles"]}
    assert set(profiles.keys()) == {"亚信", "中软"}

    assert profiles["亚信"]["sample_count"] == 5
    assert profiles["亚信"]["discount_belief_mean"] == 0.2
    assert profiles["亚信"]["discount_belief_std"] == 0.02
    assert profiles["亚信"]["source_breakdown"] == {
        "manual_historical_input": 1,
        "intel_prediction": 1,
        "agent_prior_mean": 1,
        "iterative_round": 2,
    }

    assert profiles["中软"]["sample_count"] == 4
    assert profiles["中软"]["discount_belief_mean"] == 0.255
    assert profiles["中软"]["discount_belief_std"] == 0.02
    assert profiles["中软"]["source_breakdown"] == {
        "intel_prediction": 1,
        "agent_prior_mean": 1,
        "iterative_round": 2,
    }
