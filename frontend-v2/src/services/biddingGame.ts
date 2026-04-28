import api from './api'

export interface AgentConfig {
  name: string
  strategy: string
  tech_score: number
  cost_base: number
  profit_target: number
  risk_preference: number
  discount_belief_mean: number
  discount_belief_std: number
}

export interface BiddingScenarioConfig {
  budget: number
  scoring_method: string
  tech_weight: number
  price_weight: number
  k_value: number
  sensitivity: number
  tax_rate: number
}

export interface SimulationConfig {
  n_simulations: number
  method: string
  iterative_rounds?: number
  learning_rate?: number
  exploration_rate?: number
  convergence_threshold?: number
}

export interface AllianceConfig {
  leader: string
  supporters: string[]
  coordination_type: string
  leader_bonus: number
  discount_spread: number
}

export interface CoalitionConfig {
  alliances: AllianceConfig[]
  enabled: boolean
  profit_redistribution: boolean
}

export interface CoalitionAgentEffect {
  agent_name: string
  role: string
  alliance_id: number
  discount_shift: number
  effective_discount: number
}

export interface CoalitionResult {
  alliances: string[]
  agent_effects: CoalitionAgentEffect[]
  alliance_count: number
  coordination_type_breakdown: Record<string, number>
}

export interface BiddingGameSimulatePayload {
  project_id?: string
  scenario: BiddingScenarioConfig
  our_agent: AgentConfig
  competitor_agents: AgentConfig[]
  simulation_config?: SimulationConfig
  coalition_config?: CoalitionConfig
}

export interface BiddingGameHistoryLearningPayload {
  project_id?: string
  competitor_names: string[]
  limit?: number
}

export interface CompetitorHistoryProfile {
  name: string
  discount_belief_mean: number
  discount_belief_std: number
  sample_count: number
  source_breakdown: Record<string, number>
}

export interface BiddingGameHistoryLearningResponse {
  project_id?: string
  profiles: CompetitorHistoryProfile[]
  total_records_scanned: number
  matched_competitor_count: number
  message: string
}

export interface OptimalBidResult {
  recommended_price: number
  recommended_discount: number
  win_probability: number
  expected_profit: number
  confidence_interval: [number, number]
}

export interface SimulationStats {
  n_simulations: number
  win_rate_at_optimal: number
  avg_profit_at_optimal: number
  median_rank: number
  p10_rank: number
  p90_rank: number
}

export interface SensitivityResult {
  most_sensitive_param: string
  price_elasticity: number
}

export interface NashEquilibriumResult {
  found: boolean
  our_optimal_discount: number
  equilibrium_type: string
}

export interface BayesianBeliefUpdate {
  agent_name: string
  prior_mean: number
  prior_std: number
  posterior_mean: number
  posterior_std: number
  observed_samples: number[]
  n_observations: number
  belief_shift: number
}

export interface DiscountDataPoint {
  discount: number
  win_rate: number
}

export interface ProfitDataPoint {
  discount: number
  avg_profit: number
}

export interface BayesianDetail {
  agent_name: string
  prior_mean: number
  prior_std: number
  posterior_mean: number
  posterior_std: number
  belief_shift: number
  n_observations: number
}

export interface RawSimulationData {
  discount_winrate_curve?: DiscountDataPoint[]
  discount_profit_curve?: ProfitDataPoint[]
  bayesian_details?: BayesianDetail[]
  iterative_rounds?: IterativeRoundSnapshot[]
  strategy_evolutions?: StrategyEvolutionSnapshot[]
}

export interface IterativeRoundResult {
  round_no: number
  our_discount: number
  our_price_score: number
  our_total_score: number
  our_rank: number
  won: boolean
  competitor_discounts: number[]
  competitor_scores: number[]
  profit: number
}

export interface AgentStrategyEvolution {
  agent_name: string
  initial_discount_mean: number
  final_discount_mean: number
  strategy_shift: number
  rounds_played: number
  wins: number
  learning_curve: number[]
}

export interface IterativeGameResult {
  rounds: IterativeRoundResult[]
  strategy_evolutions: AgentStrategyEvolution[]
  convergence_round: number
  final_optimal_discount: number
  final_win_probability: number
  final_expected_profit: number
  insights: string[]
}

export interface IterativeRoundSnapshot {
  round_no: number
  our_discount: number
  our_rank: number
  profit: number
  won: boolean
}

export interface StrategyEvolutionSnapshot {
  agent_name: string
  initial_discount_mean: number
  final_discount_mean: number
  strategy_shift: number
  learning_curve: number[]
}

export interface BiddingGameSimulateResponse {
  optimal_bid: OptimalBidResult
  simulation_stats: SimulationStats
  sensitivity: SensitivityResult
  nash_equilibrium: NashEquilibriumResult
  bayesian_updates: BayesianBeliefUpdate[]
  coalition_result?: CoalitionResult | null
  game_insights: string[]
  raw_simulation_data?: RawSimulationData
  iterative_result?: IterativeGameResult | null
}

export async function simulateBiddingGame(payload: BiddingGameSimulatePayload): Promise<BiddingGameSimulateResponse> {
  const res = await api.post<BiddingGameSimulateResponse>('/bidding-game/simulate', payload)
  return res.data
}

export async function learnBiddingGameHistory(payload: BiddingGameHistoryLearningPayload): Promise<BiddingGameHistoryLearningResponse> {
  const res = await api.post<BiddingGameHistoryLearningResponse>('/bidding-game/history-learning', payload)
  return res.data
}

export interface ABTestStrategyGroup {
  label: string
  our_agent: AgentConfig
}

export interface ABTestPayload {
  project_id?: string
  scenario: BiddingScenarioConfig
  strategy_groups: ABTestStrategyGroup[]
  competitor_agents: AgentConfig[]
  n_simulations: number
  coalition_config?: CoalitionConfig
}

export interface ABTestStrategyResult {
  label: string
  optimal_discount: number
  recommended_price: number
  win_probability: number
  expected_profit: number
  median_rank: number
  avg_profit: number
  confidence_interval: [number, number]
  win_rate_curve: { discount: number; win_rate: number }[]
  profit_curve: { discount: number; avg_profit: number }[]
}

export interface ABTestComparison {
  best_strategy: string
  best_win_probability: number
  best_profit: number
  win_rate_ranking: { label: string; win_probability: number }[]
  profit_ranking: { label: string; expected_profit: number }[]
  significance_tests: {
    comparison: string
    z_score: number
    p_value: number
    significant_at_005: boolean
    win_rate_diff: number
  }[]
  recommendation: string
}

export interface ABTestResponse {
  strategy_results: ABTestStrategyResult[]
  comparison: ABTestComparison
  insights: string[]
}

export async function runABTest(payload: ABTestPayload): Promise<ABTestResponse> {
  const res = await api.post<ABTestResponse>('/bidding-game/ab-test', payload)
  return res.data
}
