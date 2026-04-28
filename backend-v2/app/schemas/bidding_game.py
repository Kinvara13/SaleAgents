from pydantic import BaseModel, Field
from typing import Optional


class AgentConfig(BaseModel):
    name: str
    strategy: str = Field(default="balanced", description="aggressive / conservative / balanced / accomplice")
    tech_score: float = Field(ge=0, le=100, default=75)
    cost_base: float = Field(ge=0, default=0)
    profit_target: float = Field(ge=0, default=15)
    risk_preference: float = Field(ge=-1, le=1, default=0.0)
    discount_belief_mean: float = Field(ge=0, le=1, default=0.5)
    discount_belief_std: float = Field(ge=0, le=0.5, default=0.1)


class BiddingScenarioConfig(BaseModel):
    budget: float = Field(ge=0, default=0)
    scoring_method: str = Field(default="linear", description="linear / vertexRandomK / vertexFixedK")
    tech_weight: float = Field(ge=0, le=1, default=0.5)
    price_weight: float = Field(ge=0, le=1, default=0.5)
    k_value: float = Field(ge=0, le=100, default=95)
    sensitivity: float = Field(ge=0, default=2)
    tax_rate: float = Field(ge=0, le=1, default=0.06)


class SimulationConfig(BaseModel):
    n_simulations: int = Field(ge=100, le=10000, default=1000)
    method: str = Field(
        default="monte_carlo",
        description="monte_carlo / nash / sensitivity / bayesian / iterative",
    )
    iterative_rounds: int = Field(ge=5, le=100, default=12)
    learning_rate: float = Field(ge=0.01, le=1, default=0.18)
    exploration_rate: float = Field(ge=0, le=0.5, default=0.12)
    convergence_threshold: float = Field(ge=0.001, le=0.1, default=0.01)


class BayesianBeliefUpdate(BaseModel):
    agent_name: str
    prior_mean: float
    prior_std: float
    posterior_mean: float
    posterior_std: float
    observed_samples: list[float] = []
    n_observations: int = 0
    belief_shift: float = 0.0


class AllianceConfig(BaseModel):
    leader: str
    supporters: list[str] = Field(min_length=1)
    coordination_type: str = Field(
        default="high_bid_escort",
        description="high_bid_escort / price_padding / bracket",
    )
    leader_bonus: float = Field(ge=0, le=1, default=0.0)
    discount_spread: float = Field(ge=0.01, le=0.5, default=0.06)


class CoalitionConfig(BaseModel):
    alliances: list[AllianceConfig] = Field(default_factory=list)
    enabled: bool = False
    profit_redistribution: bool = False


class CoalitionAgentEffect(BaseModel):
    agent_name: str
    role: str = ""
    alliance_id: int = 0
    discount_shift: float = 0.0
    effective_discount: float = 0.0


class CoalitionResult(BaseModel):
    alliances: list[str] = []
    agent_effects: list[CoalitionAgentEffect] = []
    alliance_count: int = 0
    coordination_type_breakdown: dict[str, int] = Field(default_factory=dict)


class BiddingGameSimulateRequest(BaseModel):
    project_id: Optional[str] = None
    scenario: BiddingScenarioConfig
    our_agent: AgentConfig
    competitor_agents: list[AgentConfig] = []
    simulation_config: SimulationConfig = SimulationConfig()
    coalition_config: Optional[CoalitionConfig] = None


class BiddingGameHistoryLearningRequest(BaseModel):
    project_id: Optional[str] = None
    competitor_names: list[str] = Field(default_factory=list)
    limit: int = Field(ge=1, le=200, default=50)


class CompetitorHistoryProfile(BaseModel):
    name: str
    discount_belief_mean: float = Field(ge=0, le=1)
    discount_belief_std: float = Field(ge=0, le=0.5)
    sample_count: int = 0
    source_breakdown: dict[str, int] = Field(default_factory=dict)


class BiddingGameHistoryLearningResponse(BaseModel):
    project_id: Optional[str] = None
    profiles: list[CompetitorHistoryProfile] = Field(default_factory=list)
    total_records_scanned: int = 0
    matched_competitor_count: int = 0
    message: str = ""


class OptimalBidResult(BaseModel):
    recommended_price: float
    recommended_discount: float
    win_probability: float
    expected_profit: float
    confidence_interval: list[float] = Field(min_length=2, max_length=2)


class SimulationStats(BaseModel):
    n_simulations: int
    win_rate_at_optimal: float
    avg_profit_at_optimal: float
    median_rank: float
    p10_rank: float
    p90_rank: float


class SensitivityResult(BaseModel):
    most_sensitive_param: str = ""
    price_elasticity: float = 0.0


class NashEquilibriumResult(BaseModel):
    found: bool = False
    our_optimal_discount: float = 0.0
    equilibrium_type: str = ""


class IterationRoundResult(BaseModel):
    round_no: int
    our_discount: float
    our_price_score: float
    our_total_score: float
    our_rank: int
    won: bool
    competitor_discounts: list[float] = []
    competitor_scores: list[float] = []
    profit: float = 0.0


class AgentStrategyEvolution(BaseModel):
    agent_name: str
    initial_discount_mean: float
    final_discount_mean: float
    strategy_shift: float = 0.0
    rounds_played: int = 0
    wins: int = 0
    learning_curve: list[float] = []


class IterativeGameResult(BaseModel):
    rounds: list[IterationRoundResult] = []
    strategy_evolutions: list[AgentStrategyEvolution] = []
    convergence_round: int = 0
    final_optimal_discount: float = 0.0
    final_win_probability: float = 0.0
    final_expected_profit: float = 0.0
    insights: list[str] = []


class BiddingGameSimulateResponse(BaseModel):
    optimal_bid: OptimalBidResult
    simulation_stats: SimulationStats
    sensitivity: SensitivityResult
    nash_equilibrium: NashEquilibriumResult
    bayesian_updates: list[BayesianBeliefUpdate] = []
    coalition_result: Optional[CoalitionResult] = None
    game_insights: list[str] = []
    raw_simulation_data: Optional[dict] = None
    iterative_result: Optional[IterativeGameResult] = None


class ABTestStrategyGroup(BaseModel):
    label: str = Field(default="A", description="Strategy group label, e.g. A / B / C")
    our_agent: AgentConfig


class ABTestRequest(BaseModel):
    project_id: Optional[str] = None
    scenario: BiddingScenarioConfig
    strategy_groups: list[ABTestStrategyGroup] = Field(min_length=2, max_length=5)
    competitor_agents: list[AgentConfig] = []
    n_simulations: int = Field(ge=100, le=10000, default=500)
    coalition_config: Optional[CoalitionConfig] = None


class ABTestStrategyResult(BaseModel):
    label: str
    optimal_discount: float
    recommended_price: float
    win_probability: float
    expected_profit: float
    median_rank: float
    avg_profit: float
    confidence_interval: list[float] = Field(min_length=2, max_length=2)
    win_rate_curve: list[dict] = Field(default_factory=list)
    profit_curve: list[dict] = Field(default_factory=list)


class ABTestComparison(BaseModel):
    best_strategy: str = ""
    best_win_probability: float = 0.0
    best_profit: float = 0.0
    win_rate_ranking: list[dict] = Field(default_factory=list)
    profit_ranking: list[dict] = Field(default_factory=list)
    significance_tests: list[dict] = Field(default_factory=list)
    recommendation: str = ""


class ABTestResponse(BaseModel):
    strategy_results: list[ABTestStrategyResult] = []
    comparison: ABTestComparison = ABTestComparison()
    insights: list[str] = []
