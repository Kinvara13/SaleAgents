import api from './api'

// ============ Technical Case (技术案例) ============

export interface TechnicalCaseSummary {
  id: string
  project_id: string
  title: string
  primary_review_item: string
  secondary_review_item: string
  case_type: string
  scene_tags: string  // JSON string
  keywords: string    // JSON string
  summary: string
  contract_name: string
  contract_amount: string
  client_name: string
  score: string
  status: string
  created_at: string
}

export interface TechnicalCaseDetail extends TechnicalCaseSummary {
  contract_overview: string
  key_highlights: string
  content: string
  source: string
  video_url: string
  updated_at: string
}

export interface CreateTechnicalCasePayload {
  title: string
  primary_review_item?: string
  secondary_review_item?: string
  case_type?: string
  scene_tags?: string[]
  keywords?: string[]
  summary?: string
  contract_name?: string
  contract_amount?: string
  client_name?: string
  contract_overview?: string
  key_highlights?: string
  content?: string
  source?: string
}

export async function listTechnicalCases(projectId: string): Promise<TechnicalCaseSummary[]> {
  const res = await api.get<TechnicalCaseSummary[]>(
    `/projects/${projectId}/technical-cases`
  )
  return res.data
}

export async function getTechnicalCaseDetail(
  projectId: string,
  caseId: string
): Promise<TechnicalCaseDetail> {
  const res = await api.get<TechnicalCaseDetail>(
    `/projects/${projectId}/technical-cases/${caseId}`
  )
  return res.data
}

export async function createTechnicalCase(
  projectId: string,
  payload: CreateTechnicalCasePayload
): Promise<TechnicalCaseDetail> {
  const res = await api.post<TechnicalCaseDetail>(
    `/projects/${projectId}/technical-cases`,
    payload
  )
  return res.data
}

export async function updateTechnicalCase(
  projectId: string,
  caseId: string,
  payload: Partial<CreateTechnicalCasePayload & { status?: string; video_url?: string }>
): Promise<TechnicalCaseDetail> {
  const res = await api.patch<TechnicalCaseDetail>(
    `/projects/${projectId}/technical-cases/${caseId}`,
    payload
  )
  return res.data
}

export async function deleteTechnicalCase(
  projectId: string,
  caseId: string
): Promise<void> {
  await api.delete(`/projects/${projectId}/technical-cases/${caseId}`)
}

export async function searchTechnicalCases(
  projectId: string,
  params: { primary_item?: string; secondary_item?: string; keyword?: string }
): Promise<TechnicalCaseSummary[]> {
  const res = await api.get<TechnicalCaseSummary[]>(
    `/projects/${projectId}/technical-cases-search/search`,
    { params }
  )
  return res.data
}