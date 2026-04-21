import api from './api'

export interface MetricItem {
  label: string
  value: string
  hint?: string
  tone?: string
}

export interface ReviewIssue {
  title: string
  type: string
  level: string
  status: string
  document: string
  detail: string
  evidence?: string
  suggestion?: string
  origin?: string
  rule_name?: string
}

export interface ReviewJob {
  id: string
  status: string
  contract_name: string
  created_at: string
}

export async function getReviewSummary(): Promise<MetricItem[]> {
  const res = await api.get<MetricItem[]>('/review/summary')
  return res.data
}

export async function getReviewIssues(): Promise<ReviewIssue[]> {
  const res = await api.get<ReviewIssue[]>('/review/issues')
  return res.data
}

export async function getReviewActions(): Promise<string[]> {
  const res = await api.get<string[]>('/review/actions')
  return res.data
}

export async function getLatestReviewJob(): Promise<ReviewJob> {
  const res = await api.get<ReviewJob>('/review/jobs/latest')
  return res.data
}

export async function getReviewJob(jobId: string): Promise<ReviewJob> {
  const res = await api.get<ReviewJob>(`/review/jobs/${jobId}`)
  return res.data
}

export async function getReviewJobIssues(jobId: string): Promise<ReviewIssue[]> {
  const res = await api.get<ReviewIssue[]>(`/review/jobs/${jobId}/issues`)
  return res.data
}

export async function createReviewJob(payload: Record<string, unknown>): Promise<ReviewJob> {
  const res = await api.post<ReviewJob>('/review/jobs', payload)
  return res.data
}
