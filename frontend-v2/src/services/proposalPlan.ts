import api from './api'

export interface ProposalPlanSummary {
  id: string
  doc_type: string
  doc_name: string
  has_fillable_fields: boolean
  is_star_item: boolean
  score_point: string
  status: string
  source_file: string
}

export interface ProposalPlanDetail extends ProposalPlanSummary {
  project_id: string
  original_content: string
  editable_content: string
  rule_description: string
  return_file_list: string
  source_file: string
}

export async function listProposalPlans(projectId: string): Promise<ProposalPlanSummary[]> {
  const res = await api.get<ProposalPlanSummary[]>(`/projects/${projectId}/proposal-plans`)
  return res.data
}

export async function getProposalPlanDetail(projectId: string, docId: string): Promise<ProposalPlanDetail> {
  const res = await api.get<ProposalPlanDetail>(`/projects/${projectId}/proposal-plans/${docId}`)
  return res.data
}

export async function updateProposalPlan(projectId: string, docId: string, data: { editable_content?: string; status?: string }): Promise<ProposalPlanDetail> {
  const res = await api.patch<ProposalPlanDetail>(`/projects/${projectId}/proposal-plans/${docId}`, data)
  return res.data
}

export async function generateProposalPlan(projectId: string, docId: string): Promise<ProposalPlanDetail> {
  const res = await api.post<ProposalPlanDetail>(`/projects/${projectId}/proposal-plans/${docId}/generate`)
  return res.data
}
