from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PricingCalculation(Base):
    __tablename__ = "pricing_calculations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, default="")
    budget: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tech_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    discount_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    profit_margin: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tax_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.06)
    scoring_method: Mapped[str] = mapped_column(String(32), nullable=False, default="ratio")
    k_value: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    sensitivity: Mapped[float] = mapped_column(Float, nullable=False, default=0.05)
    price_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rank: Mapped[int] = mapped_column(default=0)
    ai_advice: Mapped[str] = mapped_column(String(4096), nullable=False, default="")
    competitors: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, default="user-001")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )


class TechScoreEvaluation(Base):
    __tablename__ = "tech_score_evaluations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, default="")
    objective_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    subjective_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_tech_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence_range: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    needs_manual_review: Mapped[bool] = mapped_column(default=True)
    objective_items: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    subjective_items: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    scoring_criteria: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=dict)
    company_materials: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=dict)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, default="user-001")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )


class CompetitorPrediction(Base):
    __tablename__ = "competitor_predictions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, default="")
    predictions: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    accomplice_groups: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    input_competitors: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, default="user-001")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )


class BiddingGameSimulation(Base):
    __tablename__ = "bidding_game_simulations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True, default="")
    recommended_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recommended_discount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    win_probability: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    expected_profit: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence_interval: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    n_simulations: Mapped[int] = mapped_column(default=1000)
    simulation_stats: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=dict)
    sensitivity_result: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=dict)
    nash_equilibrium: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=dict)
    bayesian_updates: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    iterative_result: Mapped[list | dict | None] = mapped_column(JSON, nullable=True)
    game_insights: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    scenario_config: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=dict)
    agent_configs: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)
    coalition_config: Mapped[list | dict | None] = mapped_column(JSON, nullable=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, default="user-001")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
