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

export function listProposalPlans(projectId: string) {
  return api.get<ProposalPlanSummary[]>(`/projects/${projectId}/proposal-plans`)
}

export function getProposalPlanDetail(projectId: string, docId: string) {
  return api.get<ProposalPlanDetail>(`/projects/${projectId}/proposal-plans/${docId}`)
}

export function updateProposalPlan(projectId: string, docId: string, data: { editable_content?: string; status?: string }) {
  return api.patch<ProposalPlanDetail>(`/projects/${projectId}/proposal-plans/${docId}`, data)
}
