import api from './api'

export interface CompetitorPredictInput {
  name: string
  industry: string
  region: string
  size: string
  historical_discount?: number
}

export interface CompetitorIntelPredictPayload {
  project_id?: string
  budget?: number
  project_type?: string
  competitors: CompetitorPredictInput[]
}

export interface DiscountDistribution {
  p10: number
  p50: number
  p90: number
  distribution_type: string
  alpha: number
  beta_param: number
}

export interface EvidenceItem {
  source: string
  reliability: string
  date: string
  detail: string
}

export interface AccompliceAlert {
  risk_level: 'high' | 'medium' | 'low'
  reasons: string[]
  related_companies: string[]
  anomaly_score: number
}

export interface CompetitorPrediction {
  name: string
  point_estimate: number
  distribution: DiscountDistribution
  confidence: number
  evidence: EvidenceItem[]
  accomplice_probability: number
  accomplice_alert: AccompliceAlert | null
  market_position: string
}

export interface CompetitorIntelPredictResponse {
  predictions: CompetitorPrediction[]
  accomplice_groups: string[][]
}

export async function predictCompetitorIntel(payload: CompetitorIntelPredictPayload): Promise<CompetitorIntelPredictResponse> {
  const res = await api.post<CompetitorIntelPredictResponse>('/competitor-intel/predict', payload)
  return res.data
}
