import api from './api'

// ============ 请求类型 ============
export interface PricingPayload {
  project_id?: string
  budget?: number
  ex_tax_price?: number
  inc_tax_price?: number
  tax_rate?: number
  profit_margin?: number
  risk_factor?: number
  pricing_method?: string
  k_value?: number
  sensitivity?: number
  tech_score?: number
  competitors?: Array<{
    name: string
    discount_rate: number
  }>
}

// ============ 响应类型 ============
export interface PricingBreakdown {
  ex_tax_price: number
  inc_tax_price: number
  ex_tax_cost: number
  inc_tax_cost: number
  discount_rate: number
  profit_margin: number
  tax_rate: number
}

export interface CompetitorResult {
  id: string
  name: string
  is_our: boolean
  quote_price: number
  discount_rate: number
  price_score: number
  rank: number
}

export interface PricingScores {
  price_competitiveness: number
  profit_reasonability: number
  risk_controllability: number
}

export interface PricingResponse {
  success: boolean
  message: string
  breakdown: PricingBreakdown | null
  competitors: CompetitorResult[]
  our_rank: number
  our_price_score: number
  benchmark_price: number
  min_review_price: number
  total_score: number
  scores: PricingScores
  ai_advice: string
}

// ============ API 函数 ============

/**
 * 计算报价策略
 * @param payload 报价计算参数
 * @returns 计算结果包含报价明细、竞品模拟得分和总评分
 */
export async function calculatePricing(payload: PricingPayload): Promise<PricingResponse> {
  const res = await api.post<PricingResponse>('/pricing/calculate', payload)
  return res.data
}
