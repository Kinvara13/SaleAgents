import api from './api'

export interface AIConfig {
  id: string
  name: string
  provider: string
  model: string
  base_url: string
  api_key: string
  temperature: number
  max_tokens: number
  is_active: boolean
}

export interface AIConfigTestResult {
  success: boolean
  message: string
  model_used: string
  latency_ms: number
}

export async function listAIConfigs(): Promise<AIConfig[]> {
  const res = await api.get<AIConfig[]>('/settings/ai-configs')
  return res.data || []
}

export async function testAIConfig(configId: string): Promise<AIConfigTestResult> {
  const res = await api.post<AIConfigTestResult>(`/settings/ai-configs/${configId}/test`)
  return res.data
}
