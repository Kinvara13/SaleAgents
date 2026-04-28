import logging
import math
import random
from typing import Any

from app.schemas.bidding_game import (
    BiddingGameSimulateRequest,
    BiddingGameSimulateResponse,
    OptimalBidResult,
    SimulationStats,
    SensitivityResult,
    NashEquilibriumResult,
    BayesianBeliefUpdate,
    AgentConfig,
    BiddingScenarioConfig,
    IterationRoundResult,
    AgentStrategyEvolution,
    IterativeGameResult,
    CoalitionConfig,
    AllianceConfig,
    CoalitionResult,
    CoalitionAgentEffect,
    ABTestRequest,
    ABTestStrategyResult,
    ABTestComparison,
    ABTestResponse,
)
from app.services.pricing_service import (
    _calc_average,
    _calc_vertex_benchmark,
    _calc_vertex_score,
    _calc_linear_score,
)

logger = logging.getLogger(__name__)


class BiddingAgent:
    def __init__(self, config: AgentConfig, is_our: bool = False):
        self.name = config.name
        self.strategy = config.strategy
        self.tech_score = config.tech_score
        self.cost_base = config.cost_base
        self.profit_target = config.profit_target
        self.risk_preference = config.risk_preference
        self.discount_belief_mean = config.discount_belief_mean
        self.discount_belief_std = config.discount_belief_std
        self.is_our = is_our
        self.alliance_id: int | None = None
        self.alliance_role: str = ""
        self.alliance_leader: str = ""

    def sample_discount(self) -> float:
        if self.is_our:
            return 0.0
        return _sample_discount_from_belief(
            self.discount_belief_mean,
            self.discount_belief_std,
            self.strategy,
            self.risk_preference,
        )


def _beta_params(mean: float, std: float) -> tuple[float, float]:
    mean = max(0.01, min(0.99, mean))
    std = max(0.01, min(0.4, std))
    variance = std * std
    temp = mean * (1 - mean) / variance - 1
    if temp <= 0:
        return 2.0, 2.0
    alpha = max(0.5, mean * temp)
    beta_param = max(0.5, (1 - mean) * temp)
    return round(alpha, 2), round(beta_param, 2)


def _clamp_discount(value: float) -> float:
    return max(0.01, min(0.95, value))


def _sample_discount_from_belief(
    mean: float,
    std: float,
    strategy: str,
    risk_preference: float = 0.0,
    exploration_scale: float = 1.0,
) -> float:
    strategy_params = {
        "aggressive": {"mean_shift": 0.08, "std_mult": 0.8},
        "conservative": {"mean_shift": -0.04, "std_mult": 0.6},
        "balanced": {"mean_shift": 0.0, "std_mult": 1.0},
        "accomplice": {"mean_shift": -0.10, "std_mult": 0.3},
    }
    params = strategy_params.get(strategy, strategy_params["balanced"])

    adjusted_mean = _clamp_discount(mean + params["mean_shift"] + risk_preference * 0.02)
    adjusted_std = max(0.01, min(0.3, std * params["std_mult"] * max(exploration_scale, 0.2)))

    alpha, beta_param = _beta_params(adjusted_mean, adjusted_std)
    try:
        from scipy.stats import beta as beta_dist

        sample = float(beta_dist.rvs(alpha, beta_param))
    except ImportError:
        sample = random.gauss(adjusted_mean, adjusted_std)

    return _clamp_discount(sample)


def _compute_profit(
    discount_rate: float,
    agent: AgentConfig | BiddingAgent,
    scenario: BiddingScenarioConfig,
) -> float:
    budget = scenario.budget
    if budget <= 0:
        return 0.0

    revenue = budget * (1 - discount_rate)
    cost = agent.cost_base if agent.cost_base > 0 else revenue / (1 + agent.profit_target / 100)
    return revenue - cost


def _compute_margin_target(agent: AgentConfig | BiddingAgent, scenario: BiddingScenarioConfig) -> float:
    if scenario.budget <= 0:
        return 0.0

    if agent.cost_base > 0:
        target_revenue = agent.cost_base * (1 + agent.profit_target / 100)
        return _clamp_discount(1 - target_revenue / scenario.budget)

    return _clamp_discount(0.1 + (agent.profit_target / 1000))


def _rank_scores(scores: list[float]) -> list[int]:
    indexed_scores = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
    ranks = [0] * len(scores)
    current_rank = 1
    for idx, (original_idx, score) in enumerate(indexed_scores):
        if idx > 0 and score < indexed_scores[idx - 1][1]:
            current_rank = idx + 1
        ranks[original_idx] = current_rank
    return ranks


def _compute_price_score_for_agent(
    discount_rate: float,
    all_discounts: list[float],
    scenario: BiddingScenarioConfig,
) -> float:
    method = scenario.scoring_method
    if method in ("vertexRandomK", "vertexFixedK"):
        review_prices = [1 - d for d in all_discounts]
        k = scenario.k_value / 100 if method == "vertexRandomK" else 0.9
        benchmark = _calc_vertex_benchmark(review_prices, k)
        d1 = 1 - discount_rate
        return _calc_vertex_score(d1, benchmark, 1.0)
    else:
        review_prices = all_discounts
        benchmark = _calc_average(review_prices)
        min_review = min(review_prices)
        d1 = discount_rate
        lambda_val = scenario.sensitivity / 100
        return _calc_linear_score(d1, min_review, benchmark, lambda_val)


def _run_single_simulation(
    our_discount: float,
    our_agent: AgentConfig,
    competitor_agents: list[BiddingAgent],
    scenario: BiddingScenarioConfig,
    competitor_discounts: list[float] | None = None,
    alliance_map: dict[str, dict] | None = None,
) -> dict:
    if competitor_discounts is None:
        competitor_discounts = [agent.sample_discount() for agent in competitor_agents]

    if alliance_map:
        leader_discounts: dict[int, float] = {}
        for agent_idx, agent in enumerate(competitor_agents):
            info = alliance_map.get(agent.name)
            if info and info.get("role") == "leader":
                leader_discounts[info["alliance_id"]] = competitor_discounts[agent_idx]

        for agent_idx, agent in enumerate(competitor_agents):
            info = alliance_map.get(agent.name)
            if info and info.get("role") == "supporter":
                alliance_id = info["alliance_id"]
                leader_discount = leader_discounts.get(alliance_id, competitor_discounts[agent_idx])
                competitor_discounts[agent_idx] = _apply_coalition_to_discount(
                    agent.name,
                    competitor_discounts[agent_idx],
                    leader_discount,
                    info,
                    alliance_id,
                )

    all_discounts = [our_discount] + competitor_discounts

    our_price_score = _compute_price_score_for_agent(our_discount, all_discounts, scenario)

    competitor_scores = []
    competitor_price_scores = []
    for i, agent in enumerate(competitor_agents):
        comp_price_score = _compute_price_score_for_agent(
            competitor_discounts[i], all_discounts, scenario
        )
        competitor_price_scores.append(comp_price_score)
        comp_total = (scenario.tech_weight * agent.tech_score + scenario.price_weight * comp_price_score) / (
            scenario.tech_weight + scenario.price_weight
        )
        competitor_scores.append(comp_total)

    our_total = (scenario.tech_weight * our_agent.tech_score + scenario.price_weight * our_price_score) / (
        scenario.tech_weight + scenario.price_weight
    )

    all_scores = [our_total] + competitor_scores
    ranks = _rank_scores(all_scores)
    our_profit = _compute_profit(our_discount, our_agent, scenario)

    return {
        "our_discount": our_discount,
        "our_price_score": our_price_score,
        "our_total_score": our_total,
        "rank": ranks[0],
        "won": ranks[0] == 1,
        "competitor_discounts": competitor_discounts,
        "competitor_price_scores": competitor_price_scores,
        "competitor_scores": competitor_scores,
        "competitor_ranks": ranks[1:],
        "our_profit": our_profit,
    }


def _monte_carlo_simulation(
    our_agent: AgentConfig,
    competitor_agents: list[BiddingAgent],
    scenario: BiddingScenarioConfig,
    n_simulations: int,
    alliance_map: dict[str, dict] | None = None,
) -> dict:
    discount_range = [i * 0.005 for i in range(1, 200)]
    results_by_discount = {}

    for our_discount in discount_range:
        wins = 0
        total_profit = 0.0
        ranks = []

        for _ in range(n_simulations):
            sim = _run_single_simulation(our_discount, our_agent, competitor_agents, scenario, alliance_map=alliance_map)
            if sim["won"]:
                wins += 1
            ranks.append(sim["rank"])
            total_profit += sim["our_profit"]

        results_by_discount[our_discount] = {
            "win_rate": wins / n_simulations,
            "avg_profit": total_profit / n_simulations,
            "avg_rank": sum(ranks) / len(ranks),
            "median_rank": sorted(ranks)[len(ranks) // 2],
        }

    best_discount = max(results_by_discount.keys(), key=lambda d: results_by_discount[d]["win_rate"])

    high_win_discounts = [
        d for d in discount_range if results_by_discount[d]["win_rate"] >= 0.5
    ]
    if high_win_discounts:
        optimal_discount = max(
            high_win_discounts, key=lambda d: results_by_discount[d]["avg_profit"]
        )
    else:
        optimal_discount = best_discount

    optimal_result = results_by_discount[optimal_discount]

    sorted_discounts = sorted(results_by_discount.keys())
    ci_low_idx = max(0, sorted_discounts.index(optimal_discount) - 5)
    ci_high_idx = min(len(sorted_discounts) - 1, sorted_discounts.index(optimal_discount) + 5)
    ci_low = sorted_discounts[ci_low_idx]
    ci_high = sorted_discounts[ci_high_idx]

    recommended_price = scenario.budget * (1 - optimal_discount) if scenario.budget > 0 else 0

    expected_profit = optimal_result["avg_profit"]

    return {
        "optimal_discount": optimal_discount,
        "recommended_price": recommended_price,
        "win_probability": optimal_result["win_rate"],
        "expected_profit": expected_profit,
        "confidence_interval": [ci_low, ci_high],
        "median_rank": optimal_result["median_rank"],
        "avg_rank": optimal_result["avg_rank"],
        "all_results": results_by_discount,
    }


def _analyze_sensitivity(
    our_agent: AgentConfig,
    competitor_agents: list[BiddingAgent],
    scenario: BiddingScenarioConfig,
    alliance_map: dict[str, dict] | None = None,
) -> SensitivityResult:
    base_discount = 0.15
    n_sim = 200

    base_result = _monte_carlo_simulation(our_agent, competitor_agents, scenario, n_sim, alliance_map=alliance_map)
    base_win_rate = base_result["win_probability"]

    most_sensitive = ""
    max_impact = 0.0
    price_elasticity = 0.0

    for delta in [0.02, 0.05, 0.10]:
        modified_scenario = scenario.model_copy(update={"budget": scenario.budget * (1 + delta)})
        mod_result = _monte_carlo_simulation(our_agent, competitor_agents, modified_scenario, n_sim, alliance_map=alliance_map)
        impact = abs(mod_result["win_probability"] - base_win_rate)
        if impact > max_impact:
            max_impact = impact
            most_sensitive = "budget"

    discount_up = base_discount + 0.05
    discount_down = base_discount - 0.05
    if discount_up < 0.95 and discount_down > 0.01:
        up_result = _monte_carlo_simulation(
            our_agent.model_copy(update={"profit_target": our_agent.profit_target - 2}),
            competitor_agents, scenario, n_sim, alliance_map=alliance_map,
        )
        down_result = _monte_carlo_simulation(
            our_agent.model_copy(update={"profit_target": our_agent.profit_target + 2}),
            competitor_agents, scenario, n_sim, alliance_map=alliance_map,
        )
        if base_win_rate > 0:
            price_elasticity = (up_result["win_probability"] - down_result["win_probability"]) / (
                2 * 0.05 / base_discount
            )

    return SensitivityResult(
        most_sensitive_param=most_sensitive or "competitor_discount",
        price_elasticity=round(price_elasticity, 4),
    )


def _find_nash_equilibrium(
    our_agent: AgentConfig,
    competitor_agents: list[BiddingAgent],
    scenario: BiddingScenarioConfig,
    alliance_map: dict[str, dict] | None = None,
) -> NashEquilibriumResult:
    n_sim = 100
    discount_grid = [i * 0.02 for i in range(1, 50)]

    best_response = {}
    for our_d in discount_grid:
        best_our_score = -1
        for _ in range(n_sim):
            sim = _run_single_simulation(our_d, our_agent, competitor_agents, scenario, alliance_map=alliance_map)
            if sim["our_total_score"] > best_our_score:
                best_our_score = sim["our_total_score"]
        best_response[our_d] = best_our_score

    nash_discount = max(best_response, key=best_response.get)

    return NashEquilibriumResult(
        found=True,
        our_optimal_discount=round(nash_discount, 4),
        equilibrium_type="approximate_pure_strategy",
    )


def _resolve_alliance_map(
    coalition_config: CoalitionConfig | None,
    competitor_agents: list[BiddingAgent],
    our_agent: BiddingAgent,
) -> tuple[dict[str, dict], list[CoalitionAgentEffect]]:
    if not coalition_config or not coalition_config.enabled or not coalition_config.alliances:
        return {}, []

    agent_lookup: dict[str, BiddingAgent] = {our_agent.name: our_agent}
    for agent in competitor_agents:
        agent_lookup[agent.name] = agent

    alliance_map: dict[str, dict] = {}
    effects: list[CoalitionAgentEffect] = []

    for alliance_idx, alliance in enumerate(coalition_config.alliances):
        leader = agent_lookup.get(alliance.leader)
        if leader is None:
            continue
        leader.alliance_id = alliance_idx
        leader.alliance_role = "leader"
        leader.alliance_leader = alliance.leader
        alliance_map[alliance.leader] = {
            "alliance_id": alliance_idx,
            "role": "leader",
            "coordination_type": alliance.coordination_type,
            "discount_spread": alliance.discount_spread,
            "leader_name": alliance.leader,
        }
        effects.append(
            CoalitionAgentEffect(
                agent_name=alliance.leader,
                role="leader",
                alliance_id=alliance_idx,
                discount_shift=0.0,
                effective_discount=0.0,
            )
        )

        for supporter_name in alliance.supporters:
            supporter = agent_lookup.get(supporter_name)
            if supporter is None:
                continue
            supporter.alliance_id = alliance_idx
            supporter.alliance_role = "supporter"
            supporter.alliance_leader = alliance.leader
            alliance_map[supporter_name] = {
                "alliance_id": alliance_idx,
                "role": "supporter",
                "coordination_type": alliance.coordination_type,
                "discount_spread": alliance.discount_spread,
                "leader_name": alliance.leader,
            }
            effects.append(
                CoalitionAgentEffect(
                    agent_name=supporter_name,
                    role="supporter",
                    alliance_id=alliance_idx,
                    discount_shift=0.0,
                    effective_discount=0.0,
                )
            )

    logger.info(
        "Resolved alliance map alliances=%d mapped_agents=%d",
        len(coalition_config.alliances),
        len(alliance_map),
    )
    return alliance_map, effects


def _apply_coalition_to_discount(
    agent_name: str,
    sampled_discount: float,
    leader_discount: float,
    alliance_info: dict,
    alliance_idx: int,
) -> float:
    coordination_type = alliance_info.get("coordination_type", "high_bid_escort")
    spread = float(alliance_info.get("discount_spread", 0.06))

    if coordination_type == "high_bid_escort":
        target = max(0.01, leader_discount - spread)
        adjusted = sampled_discount + (target - sampled_discount) * 0.7
    elif coordination_type == "price_padding":
        noise = random.uniform(-spread * 0.5, spread * 0.5)
        target = _clamp_discount(leader_discount + noise)
        adjusted = sampled_discount + (target - sampled_discount) * 0.5
    elif coordination_type == "bracket":
        supporter_offset = hash(f"{agent_name}_{alliance_idx}") % 100 / 100.0
        bracket_sign = 1 if supporter_offset > 0.5 else -1
        target = _clamp_discount(leader_discount + bracket_sign * spread * 0.6)
        adjusted = sampled_discount + (target - sampled_discount) * 0.6
    else:
        adjusted = sampled_discount

    return round(_clamp_discount(adjusted), 4)


def _generate_game_insights(
    optimal_discount: float,
    win_probability: float,
    our_agent: AgentConfig,
    competitor_agents: list[BiddingAgent],
    scenario: BiddingScenarioConfig,
) -> list[str]:
    insights = []

    if win_probability >= 0.7:
        insights.append(f"当前参数下我方中标概率较高({win_probability:.0%})，报价策略空间充裕。")
    elif win_probability >= 0.4:
        insights.append(f"中标概率中等({win_probability:.0%})，建议精细调整折扣率以提升竞争力。")
    else:
        insights.append(f"中标概率偏低({win_probability:.0%})，需考虑更激进的报价或提升技术分。")

    if our_agent.tech_score >= 85:
        insights.append("技术分优势明显，报价可适当上浮3-5%仍保持竞争力。")
    elif our_agent.tech_score < 70:
        insights.append("技术分偏低，需通过更低的报价弥补技术分差距。")

    aggressive_count = sum(1 for a in competitor_agents if a.strategy == "aggressive")
    if aggressive_count > 0:
        insights.append(f"存在{aggressive_count}家激进型竞商，若其采取低价策略，我方需将折扣率提高至{optimal_discount + 0.05:.0%}以上。")

    accomplice_count = sum(1 for a in competitor_agents if a.strategy == "accomplice")
    if accomplice_count > 0:
        insights.append(f"检测到{accomplice_count}家疑似陪标方，其报价可能偏高以拉高基准价。")

    return insights


def _bayesian_belief_update(
    competitor_agents: list[BiddingAgent],
    scenario: BiddingScenarioConfig,
    n_rounds: int = 10,
) -> list[BayesianBeliefUpdate]:
    logger.info("Running Bayesian belief update for %d agents over %d rounds", len(competitor_agents), n_rounds)

    updates = []
    for agent in competitor_agents:
        prior_mean = agent.discount_belief_mean
        prior_std = agent.discount_belief_std
        prior_var = prior_std * prior_std

        observed_discounts = []
        for _ in range(n_rounds):
            sample = agent.sample_discount()
            observed_discounts.append(round(sample, 4))

        n_obs = len(observed_discounts)
        if n_obs == 0:
            updates.append(BayesianBeliefUpdate(
                agent_name=agent.name,
                prior_mean=round(prior_mean, 4),
                prior_std=round(prior_std, 4),
                posterior_mean=round(prior_mean, 4),
                posterior_std=round(prior_std, 4),
                observed_samples=[],
                n_observations=0,
                belief_shift=0.0,
            ))
            continue

        sample_mean = sum(observed_discounts) / n_obs
        sample_var = sum((x - sample_mean) ** 2 for x in observed_discounts) / n_obs if n_obs > 1 else prior_var

        known_var = prior_var if sample_var < 1e-6 else sample_var

        posterior_var = 1.0 / (1.0 / prior_var + n_obs / known_var) if known_var > 0 else prior_var
        posterior_mean = posterior_var * (prior_mean / prior_var + n_obs * sample_mean / known_var) if known_var > 0 else prior_mean

        posterior_mean = max(0.01, min(0.95, posterior_mean))
        posterior_std = max(0.02, min(0.3, math.sqrt(posterior_var)))

        belief_shift = round(posterior_mean - prior_mean, 4)

        updates.append(BayesianBeliefUpdate(
            agent_name=agent.name,
            prior_mean=round(prior_mean, 4),
            prior_std=round(prior_std, 4),
            posterior_mean=round(posterior_mean, 4),
            posterior_std=round(posterior_std, 4),
            observed_samples=observed_discounts[:20],
            n_observations=n_obs,
            belief_shift=belief_shift,
        ))

        agent.discount_belief_mean = posterior_mean
        agent.discount_belief_std = posterior_std

    return updates


def _update_discount_anchor(
    current_anchor: float,
    observed_discount: float,
    agent: AgentConfig | BiddingAgent,
    rank: int,
    won: bool,
    profit: float,
    scenario: BiddingScenarioConfig,
    learning_rate: float,
) -> float:
    revenue = scenario.budget * (1 - observed_discount) if scenario.budget > 0 else 0.0
    profit_margin = (profit / revenue) if revenue > 0 else 0.0
    target_margin = agent.profit_target / 100 if agent.profit_target > 0 else 0.12
    desired_discount = observed_discount

    if won:
        if profit_margin > target_margin + 0.02:
            desired_discount -= 0.008
        elif profit_margin < target_margin * 0.75:
            desired_discount += 0.004
    else:
        desired_discount += min(0.03, 0.008 * max(rank - 1, 1))

    strategy_bias = {
        "aggressive": 0.012,
        "conservative": -0.008,
        "balanced": 0.0,
        "accomplice": -0.015,
    }.get(agent.strategy, 0.0)
    desired_discount += strategy_bias + agent.risk_preference * 0.006
    desired_discount = _clamp_discount(desired_discount)

    next_anchor = current_anchor + learning_rate * (desired_discount - current_anchor)
    return _clamp_discount(next_anchor)


def _run_iterative_game(
    our_agent: AgentConfig,
    competitor_agents: list[BiddingAgent],
    scenario: BiddingScenarioConfig,
    iterative_rounds: int,
    learning_rate: float,
    exploration_rate: float,
    convergence_threshold: float,
    alliance_map: dict[str, dict] | None = None,
) -> IterativeGameResult:
    logger.info(
        "Running iterative bidding game: rounds=%d learning_rate=%.3f exploration=%.3f competitors=%d",
        iterative_rounds,
        learning_rate,
        exploration_rate,
        len(competitor_agents),
    )

    our_anchor = _compute_margin_target(our_agent, scenario)
    competitor_anchors = {agent.name: _clamp_discount(agent.discount_belief_mean) for agent in competitor_agents}
    learning_curves: dict[str, list[float]] = {"我方": [round(our_anchor, 4)]}
    for agent in competitor_agents:
        learning_curves[agent.name] = [round(competitor_anchors[agent.name], 4)]

    rounds: list[IterationRoundResult] = []
    competitor_wins = {agent.name: 0 for agent in competitor_agents}
    previous_anchor = our_anchor
    stable_rounds = 0
    convergence_round = 0

    for round_no in range(1, iterative_rounds + 1):
        current_exploration = exploration_rate * max(0.35, 1 - ((round_no - 1) / max(iterative_rounds, 1)))
        our_discount = _sample_discount_from_belief(
            our_anchor,
            max(0.015, current_exploration * 0.2),
            our_agent.strategy,
            our_agent.risk_preference,
            exploration_scale=max(current_exploration * 2, 0.3),
        )
        competitor_discounts = [
            _sample_discount_from_belief(
                competitor_anchors[agent.name],
                max(agent.discount_belief_std, current_exploration * 0.15),
                agent.strategy,
                agent.risk_preference,
                exploration_scale=max(current_exploration * 1.6, 0.3),
            )
            for agent in competitor_agents
        ]

        if alliance_map:
            leader_discounts: dict[int, float] = {}
            for agent_idx, agent in enumerate(competitor_agents):
                info = alliance_map.get(agent.name)
                if info and info.get("role") == "leader":
                    leader_discounts[info["alliance_id"]] = competitor_discounts[agent_idx]
            for agent_idx, agent in enumerate(competitor_agents):
                info = alliance_map.get(agent.name)
                if info and info.get("role") == "supporter":
                    alliance_id = info["alliance_id"]
                    leader_discount = leader_discounts.get(alliance_id, competitor_discounts[agent_idx])
                    competitor_discounts[agent_idx] = _apply_coalition_to_discount(
                        agent.name,
                        competitor_discounts[agent_idx],
                        leader_discount,
                        info,
                        alliance_id,
                    )

        sim = _run_single_simulation(
            our_discount,
            our_agent,
            competitor_agents,
            scenario,
            competitor_discounts=competitor_discounts,
            alliance_map=alliance_map,
        )

        rounds.append(
            IterationRoundResult(
                round_no=round_no,
                our_discount=round(sim["our_discount"], 4),
                our_price_score=round(sim["our_price_score"], 4),
                our_total_score=round(sim["our_total_score"], 4),
                our_rank=sim["rank"],
                won=sim["won"],
                competitor_discounts=[round(v, 4) for v in sim["competitor_discounts"]],
                competitor_scores=[round(v, 4) for v in sim["competitor_scores"]],
                profit=round(sim["our_profit"], 2),
            )
        )

        our_anchor = _update_discount_anchor(
            our_anchor,
            sim["our_discount"],
            our_agent,
            sim["rank"],
            sim["won"],
            sim["our_profit"],
            scenario,
            learning_rate,
        )
        learning_curves["我方"].append(round(our_anchor, 4))

        for idx, agent in enumerate(competitor_agents):
            if sim["competitor_ranks"][idx] == 1:
                competitor_wins[agent.name] += 1
            competitor_profit = _compute_profit(sim["competitor_discounts"][idx], agent, scenario)
            next_anchor = _update_discount_anchor(
                competitor_anchors[agent.name],
                sim["competitor_discounts"][idx],
                agent,
                sim["competitor_ranks"][idx],
                sim["competitor_ranks"][idx] == 1,
                competitor_profit,
                scenario,
                learning_rate * 0.85,
            )
            competitor_anchors[agent.name] = next_anchor
            agent.discount_belief_mean = next_anchor
            learning_curves[agent.name].append(round(next_anchor, 4))

        if alliance_map:
            for agent in competitor_agents:
                info = alliance_map.get(agent.name)
                if info and info.get("role") == "supporter":
                    leader_name = info["leader_name"]
                    leader_anchor = competitor_anchors.get(leader_name)
                    if leader_anchor is not None:
                        spread = float(info.get("discount_spread", 0.06))
                        synced_anchor = _clamp_discount(leader_anchor - spread)
                        competitor_anchors[agent.name] = synced_anchor
                        agent.discount_belief_mean = synced_anchor

        if abs(our_anchor - previous_anchor) <= convergence_threshold:
            stable_rounds += 1
            if stable_rounds >= 3 and convergence_round == 0:
                convergence_round = round_no
        else:
            stable_rounds = 0
        previous_anchor = our_anchor

    recent_rounds = rounds[-min(5, len(rounds)):] if rounds else []
    final_optimal_discount = round(sum(r.our_discount for r in recent_rounds) / len(recent_rounds), 4) if recent_rounds else round(our_anchor, 4)
    final_win_probability = round(sum(1 for r in recent_rounds if r.won) / len(recent_rounds), 4) if recent_rounds else 0.0
    final_expected_profit = round(sum(r.profit for r in recent_rounds) / len(recent_rounds), 2) if recent_rounds else 0.0

    strategy_evolutions = [
        AgentStrategyEvolution(
            agent_name="我方",
            initial_discount_mean=learning_curves["我方"][0],
            final_discount_mean=learning_curves["我方"][-1],
            strategy_shift=round(learning_curves["我方"][-1] - learning_curves["我方"][0], 4),
            rounds_played=len(rounds),
            wins=sum(1 for r in rounds if r.won),
            learning_curve=learning_curves["我方"],
        )
    ]
    for agent in competitor_agents:
        curve = learning_curves[agent.name]
        strategy_evolutions.append(
            AgentStrategyEvolution(
                agent_name=agent.name,
                initial_discount_mean=curve[0],
                final_discount_mean=curve[-1],
                strategy_shift=round(curve[-1] - curve[0], 4),
                rounds_played=len(rounds),
                wins=competitor_wins[agent.name],
                learning_curve=curve,
            )
        )

    insights = []
    if convergence_round:
        insights.append(f"我方策略在第{convergence_round}轮附近进入稳定区间，可将其视为收敛拐点。")
    else:
        insights.append("当前轮次内策略仍在探索，建议提高轮次后再观察是否收敛。")

    if final_win_probability >= 0.6:
        insights.append("最近轮次中我方保持较高胜率，当前迭代策略具备较强稳定性。")
    else:
        insights.append("最近轮次胜率仍有波动，建议结合技术分和陪标情景继续压测。")

    return IterativeGameResult(
        rounds=rounds,
        strategy_evolutions=strategy_evolutions,
        convergence_round=convergence_round,
        final_optimal_discount=final_optimal_discount,
        final_win_probability=final_win_probability,
        final_expected_profit=final_expected_profit,
        insights=insights,
    )


def simulate_bidding_game(payload: BiddingGameSimulateRequest) -> BiddingGameSimulateResponse:
    logger.info(
        "Simulating bidding game: %d competitors, %d simulations, method=%s coalition=%s",
        len(payload.competitor_agents),
        payload.simulation_config.n_simulations,
        payload.simulation_config.method,
        payload.coalition_config.enabled if payload.coalition_config else False,
    )

    scenario = payload.scenario
    our_agent_config = payload.our_agent
    competitor_agents = [BiddingAgent(c, is_our=False) for c in payload.competitor_agents]
    our_agent = BiddingAgent(our_agent_config, is_our=True)

    alliance_map, alliance_effects = _resolve_alliance_map(
        payload.coalition_config,
        competitor_agents,
        our_agent,
    )

    n_sim = payload.simulation_config.n_simulations
    method = payload.simulation_config.method

    bayesian_updates: list[BayesianBeliefUpdate] = []
    iterative_result: IterativeGameResult | None = None
    if method == "bayesian" and competitor_agents:
        bayesian_updates = _bayesian_belief_update(
            competitor_agents, scenario, n_rounds=max(10, n_sim // 50)
        )
    elif method == "iterative":
        iterative_result = _run_iterative_game(
            our_agent_config,
            competitor_agents,
            scenario,
            iterative_rounds=payload.simulation_config.iterative_rounds,
            learning_rate=payload.simulation_config.learning_rate,
            exploration_rate=payload.simulation_config.exploration_rate,
            convergence_threshold=payload.simulation_config.convergence_threshold,
            alliance_map=alliance_map if alliance_map else None,
        )

    mc_result = _monte_carlo_simulation(
        our_agent_config, competitor_agents, scenario, n_sim,
        alliance_map=alliance_map if alliance_map else None,
    )

    sensitivity = _analyze_sensitivity(
        our_agent_config, competitor_agents, scenario,
        alliance_map=alliance_map if alliance_map else None,
    )

    nash = _find_nash_equilibrium(
        our_agent_config, competitor_agents, scenario,
        alliance_map=alliance_map if alliance_map else None,
    )

    insights = _generate_game_insights(
        mc_result["optimal_discount"],
        mc_result["win_probability"],
        our_agent_config,
        competitor_agents,
        scenario,
    )

    if alliance_map:
        alliances = list(alliance_map.values())
        alliance_count = len(set(a["alliance_id"] for a in alliances))
        coalition_result = CoalitionResult(
            alliances=[f"alliance_{aid}" for aid in range(alliance_count)],
            agent_effects=alliance_effects,
            alliance_count=alliance_count,
            coordination_type_breakdown={
                ct: sum(1 for a in alliances if a.get("coordination_type") == ct)
                for ct in {"high_bid_escort", "price_padding", "bracket"}
            },
        )
        supporters_count = sum(1 for a in alliances if a.get("role") == "supporter")
        if supporters_count:
            insights.append(
                f"协同博弈：检测到{alliance_count}个联盟共{supporters_count}个陪标方，"
                f"联盟协调策略下主攻方胜率可能被高估，建议结合真实投标数据交叉验证。"
            )
    else:
        coalition_result = None

    if bayesian_updates:
        significant_shifts = [u for u in bayesian_updates if abs(u.belief_shift) > 0.02]
        if significant_shifts:
            for u in significant_shifts:
                direction = "上修" if u.belief_shift > 0 else "下修"
                insights.append(
                    f"贝叶斯更新：{u.agent_name}折扣率信念{direction}{abs(u.belief_shift):.1%}（{u.prior_mean:.1%}→{u.posterior_mean:.1%}），"
                    f"基于{u.n_observations}次观察。"
                )

    if iterative_result:
        insights.extend(iterative_result.insights)
        optimal_discount = iterative_result.final_optimal_discount
        optimal_price = scenario.budget * (1 - optimal_discount) if scenario.budget > 0 else 0.0
        mc_result["optimal_discount"] = optimal_discount
        mc_result["recommended_price"] = optimal_price
        mc_result["win_probability"] = iterative_result.final_win_probability or mc_result["win_probability"]
        mc_result["expected_profit"] = iterative_result.final_expected_profit or mc_result["expected_profit"]
        ci_low = _clamp_discount(optimal_discount - max(payload.simulation_config.convergence_threshold * 2, 0.01))
        ci_high = _clamp_discount(optimal_discount + max(payload.simulation_config.convergence_threshold * 2, 0.01))
        mc_result["confidence_interval"] = [ci_low, ci_high]

    p10_ranks = []
    p90_ranks = []
    for _ in range(n_sim // 10):
        sim = _run_single_simulation(
            mc_result["optimal_discount"], our_agent_config, competitor_agents, scenario,
            alliance_map=alliance_map if alliance_map else None,
        )
        p10_ranks.append(sim["rank"])
    p10_ranks.sort()
    p90_ranks = p10_ranks

    optimal_bid = OptimalBidResult(
        recommended_price=round(mc_result["recommended_price"], 2),
        recommended_discount=round(mc_result["optimal_discount"], 4),
        win_probability=round(mc_result["win_probability"], 4),
        expected_profit=round(mc_result["expected_profit"], 2),
        confidence_interval=[
            round(mc_result["confidence_interval"][0], 4),
            round(mc_result["confidence_interval"][1], 4),
        ],
    )

    sim_stats = SimulationStats(
        n_simulations=n_sim,
        win_rate_at_optimal=round(mc_result["win_probability"], 4),
        avg_profit_at_optimal=round(mc_result["expected_profit"], 2),
        median_rank=round(mc_result["median_rank"], 1),
        p10_rank=round(p10_ranks[max(0, len(p10_ranks) // 10)], 1) if p10_ranks else 1.0,
        p90_rank=round(p90_ranks[min(len(p90_ranks) - 1, len(p90_ranks) * 9 // 10)], 1) if p90_ranks else 3.0,
    )

    raw_data: dict[str, Any] = {}
    all_results = mc_result.get("all_results", {})
    if all_results:
        discount_winrate = []
        discount_profit = []
        for d in sorted(all_results.keys()):
            r = all_results[d]
            discount_winrate.append({"discount": round(d, 4), "win_rate": round(r["win_rate"], 4)})
            discount_profit.append({"discount": round(d, 4), "avg_profit": round(r["avg_profit"], 2)})
        raw_data["discount_winrate_curve"] = discount_winrate
        raw_data["discount_profit_curve"] = discount_profit

    if bayesian_updates:
        raw_data["bayesian_details"] = [
            {
                "agent_name": u.agent_name,
                "prior_mean": u.prior_mean,
                "prior_std": u.prior_std,
                "posterior_mean": u.posterior_mean,
                "posterior_std": u.posterior_std,
                "belief_shift": u.belief_shift,
                "n_observations": u.n_observations,
            }
            for u in bayesian_updates
        ]

    if iterative_result:
        raw_data["iterative_rounds"] = [
            {
                "round_no": r.round_no,
                "our_discount": r.our_discount,
                "our_rank": r.our_rank,
                "profit": r.profit,
                "won": r.won,
            }
            for r in iterative_result.rounds
        ]
        raw_data["strategy_evolutions"] = [
            {
                "agent_name": s.agent_name,
                "initial_discount_mean": s.initial_discount_mean,
                "final_discount_mean": s.final_discount_mean,
                "strategy_shift": s.strategy_shift,
                "learning_curve": s.learning_curve,
            }
            for s in iterative_result.strategy_evolutions
        ]

    return BiddingGameSimulateResponse(
        optimal_bid=optimal_bid,
        simulation_stats=sim_stats,
        sensitivity=sensitivity,
        nash_equilibrium=nash,
        bayesian_updates=bayesian_updates,
        coalition_result=coalition_result,
        game_insights=insights,
        raw_simulation_data=raw_data if raw_data else None,
        iterative_result=iterative_result,
    )


def _proportion_z_test(p1: float, p2: float, n1: int, n2: int) -> dict:
    p_combined = (p1 * n1 + p2 * n2) / (n1 + n2) if (n1 + n2) > 0 else 0.5
    se = math.sqrt(p_combined * (1 - p_combined) * (1 / n1 + 1 / n2)) if n1 > 0 and n2 > 0 else 1.0
    if se < 1e-9:
        return {"z_score": 0.0, "p_value": 1.0, "significant_at_005": False}
    z = (p1 - p2) / se
    try:
        import mpmath
        p_value = 2 * float(mpmath.erfc(abs(z) / math.sqrt(2)))
    except ImportError:
        x = abs(z) / math.sqrt(2)
        p_value = max(0.0, 1.0 - min(1.0, x * 0.3989 * math.exp(-x * x / 2) * (1 + 0.0417 * x * x)))
    return {
        "z_score": round(z, 4),
        "p_value": round(max(0.0, min(1.0, p_value)), 4),
        "significant_at_005": p_value < 0.05,
    }


def run_ab_test(payload: ABTestRequest) -> ABTestResponse:
    logger.info(
        "Running A/B test: %d strategy groups, %d competitors, %d simulations",
        len(payload.strategy_groups),
        len(payload.competitor_agents),
        payload.n_simulations,
    )

    scenario = payload.scenario
    competitor_agents = [BiddingAgent(c, is_our=False) for c in payload.competitor_agents]

    alliance_map, _ = _resolve_alliance_map(
        payload.coalition_config,
        competitor_agents,
        BiddingAgent(payload.strategy_groups[0].our_agent, is_our=True),
    )

    strategy_results: list[ABTestStrategyResult] = []

    for group in payload.strategy_groups:
        our_agent_config = group.our_agent
        logger.info(
            "A/B test group %s: discount_mean=%.3f profit_target=%.1f risk_pref=%.2f tech_score=%.1f",
            group.label,
            our_agent_config.discount_belief_mean,
            our_agent_config.profit_target,
            our_agent_config.risk_preference,
            our_agent_config.tech_score,
        )

        mc_result = _monte_carlo_simulation(
            our_agent_config,
            competitor_agents,
            scenario,
            payload.n_simulations,
            alliance_map=alliance_map if alliance_map else None,
        )

        win_rate_curve = []
        profit_curve = []
        all_results = mc_result.get("all_results", {})
        for d in sorted(all_results.keys()):
            r = all_results[d]
            win_rate_curve.append({"discount": round(d, 4), "win_rate": round(r["win_rate"], 4)})
            profit_curve.append({"discount": round(d, 4), "avg_profit": round(r["avg_profit"], 2)})

        strategy_results.append(
            ABTestStrategyResult(
                label=group.label,
                optimal_discount=round(mc_result["optimal_discount"], 4),
                recommended_price=round(mc_result["recommended_price"], 2),
                win_probability=round(mc_result["win_probability"], 4),
                expected_profit=round(mc_result["expected_profit"], 2),
                median_rank=round(mc_result["median_rank"], 1),
                avg_profit=round(mc_result["expected_profit"], 2),
                confidence_interval=[
                    round(mc_result["confidence_interval"][0], 4),
                    round(mc_result["confidence_interval"][1], 4),
                ],
                win_rate_curve=win_rate_curve,
                profit_curve=profit_curve,
            )
        )

    win_ranking = sorted(
        [{"label": r.label, "win_probability": r.win_probability} for r in strategy_results],
        key=lambda x: x["win_probability"],
        reverse=True,
    )
    profit_ranking = sorted(
        [{"label": r.label, "expected_profit": r.expected_profit} for r in strategy_results],
        key=lambda x: x["expected_profit"],
        reverse=True,
    )

    best_by_win = strategy_results[0]
    for r in strategy_results:
        if r.win_probability > best_by_win.win_probability:
            best_by_win = r
        elif r.win_probability == best_by_win.win_probability and r.expected_profit > best_by_win.expected_profit:
            best_by_win = r

    best_by_profit = max(strategy_results, key=lambda r: r.expected_profit)

    sig_tests = []
    n = payload.n_simulations
    for i in range(len(strategy_results)):
        for j in range(i + 1, len(strategy_results)):
            r_i = strategy_results[i]
            r_j = strategy_results[j]
            test = _proportion_z_test(r_i.win_probability, r_j.win_probability, n, n)
            test["comparison"] = f"{r_i.label} vs {r_j.label}"
            test["win_rate_diff"] = round(r_i.win_probability - r_j.win_probability, 4)
            sig_tests.append(test)

    recommendation = ""
    if len(strategy_results) >= 2:
        best_label = best_by_win.label
        second_best = None
        for r in strategy_results:
            if r.label != best_label:
                if second_best is None or r.win_probability > second_best.win_probability:
                    second_best = r
        if second_best:
            win_diff = best_by_win.win_probability - second_best.win_probability
            if win_diff > 0.1:
                recommendation = (
                    f"策略{best_label}在胜率上显著领先（+{win_diff:.1%}），"
                    f"推荐采用策略{best_label}。"
                )
            elif win_diff > 0.03:
                recommendation = (
                    f"策略{best_label}胜率略优（+{win_diff:.1%}），"
                    f"但策略{best_by_profit.label}期望利润更高（¥{best_by_profit.expected_profit:,.0f}），"
                    f"建议根据风险偏好选择。"
                )
            else:
                recommendation = (
                    f"策略{best_label}与策略{second_best.label}胜率接近（差异{win_diff:.1%}），"
                    f"建议优先考虑期望利润更高的策略{best_by_profit.label}。"
                )

    comparison = ABTestComparison(
        best_strategy=best_by_win.label,
        best_win_probability=best_by_win.win_probability,
        best_profit=best_by_profit.expected_profit,
        win_rate_ranking=win_ranking,
        profit_ranking=profit_ranking,
        significance_tests=sig_tests,
        recommendation=recommendation,
    )

    insights: list[str] = []
    insights.append(f"共测试{len(strategy_results)}组策略，胜率最高为策略{best_by_win.label}（{best_by_win.win_probability:.1%}）。")
    if best_by_win.label != best_by_profit.label:
        insights.append(
            f"策略{best_by_profit.label}期望利润最高（¥{best_by_profit.expected_profit:,.0f}），"
            f"但胜率低于策略{best_by_win.label}，存在利润-胜率权衡。"
        )
    for test in sig_tests:
        if test.get("significant_at_005"):
            insights.append(
                f"统计检验：{test['comparison']}胜率差异显著（p={test['p_value']:.4f}），"
                f"差异为{test['win_rate_diff']:.1%}。"
            )
    if not any(t.get("significant_at_005") for t in sig_tests):
        insights.append("所有策略间胜率差异均未达到统计显著性（p>0.05），建议增加模拟次数或调整策略参数。")

    logger.info(
        "A/B test completed: best_strategy=%s best_win=%.2f best_profit=%.0f",
        comparison.best_strategy,
        comparison.best_win_probability,
        comparison.best_profit,
    )

    return ABTestResponse(
        strategy_results=strategy_results,
        comparison=comparison,
        insights=insights,
    )
