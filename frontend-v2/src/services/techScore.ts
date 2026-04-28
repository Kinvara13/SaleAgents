import api from './api'

export interface SubjectiveTier {
  tier: number
  min_score: number
  max_score: number
  description: string
}

export interface ObjectiveItem {
  name: string
  max_score: number
  weight: number
}

export interface SubjectiveItem {
  name: string
  max_score: number
  tiers: SubjectiveTier[]
}

export interface ScoringCriteria {
  objective_items: ObjectiveItem[]
  subjective_items: SubjectiveItem[]
}

export interface CompanyMaterials {
  qualifications: string[]
  cases: string[]
  proposal_text: string
  technical_params: string[]
}

export interface TechScoreEvaluatePayload {
  project_id?: string
  scoring_criteria: ScoringCriteria
  company_materials: CompanyMaterials
  tech_weight?: number
  manual_objective_score?: number
}

export interface ObjectiveScoreItem {
  name: string
  score: number
  max_score: number
  matched: boolean
  detail: string
  ai_verified: boolean
  ai_verification_detail: string
  missing_items: string[]
}

export interface ObjectiveScoreResult {
  total: number
  items: ObjectiveScoreItem[]
  confidence: number
}

export interface SubjectiveScoreItem {
  name: string
  ai_tier: number
  ai_score: number
  max_score: number
  confidence: number
  reasoning: string
  references: string[]
}

export interface SubjectiveScoreResult {
  items: SubjectiveScoreItem[]
  total: number
}

export interface TechScoreEvaluateResponse {
  objective_score: ObjectiveScoreResult
  subjective_score: SubjectiveScoreResult
  total_tech_score: number
  confidence_range: [number, number]
  needs_manual_review: boolean
}

export async function evaluateTechScore(payload: TechScoreEvaluatePayload): Promise<TechScoreEvaluateResponse> {
  const res = await api.post<TechScoreEvaluateResponse>('/tech-score/evaluate', payload)
  return res.data
}
