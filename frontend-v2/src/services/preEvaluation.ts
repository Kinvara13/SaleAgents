import api from './api'

export interface PreEvaluationJob {
  id: string
  file_name: string
  status: string
  created_at: string
  completed_at?: string
}

export interface PreEvaluationJobDetail {
  id: string
  project_id?: string
  file_name: string
  status: string
  review_method: {
    method?: string
    description?: string
    key_points?: string[]
  }
  tech_review_table: Array<{
    item: string
    score: string
    criteria: string
  }>
  starred_items: Array<{
    item: string
    importance: string
    suggestion: string
  }>
  summary: string
  created_at: string
  completed_at?: string
}

export async function uploadPreEvaluation(file: File, projectId?: string): Promise<PreEvaluationJobDetail> {
  const formData = new FormData()
  formData.append('file', file)
  if (projectId) {
    formData.append('project_id', projectId)
  }
  const res = await api.post<PreEvaluationJobDetail>('/pre-evaluation/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return res.data
}

export async function listPreEvaluations(projectId?: string): Promise<PreEvaluationJob[]> {
  const params = projectId ? { project_id: projectId } : undefined
  const res = await api.get<PreEvaluationJob[]>('/pre-evaluation/jobs', { params })
  return res.data
}

export async function getPreEvaluation(jobId: string): Promise<PreEvaluationJobDetail> {
  const res = await api.get<PreEvaluationJobDetail>(`/pre-evaluation/jobs/${jobId}`)
  return res.data
}

export async function deletePreEvaluation(jobId: string): Promise<void> {
  await api.delete(`/pre-evaluation/jobs/${jobId}`)
}
