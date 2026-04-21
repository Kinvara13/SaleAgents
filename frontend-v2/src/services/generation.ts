import api from './api'

export interface GenerationSection {
  title: string
  status: string
  citations: number
  todo: number
}

export interface KnowledgeAsset {
  title: string
  type: string
  score: string
  status: string
}

export interface GenerationJob {
  id: string
  status: string
  project_id: string
  created_at: string
}

export async function listGenerationSections(): Promise<GenerationSection[]> {
  const res = await api.get<GenerationSection[]>('/generation/sections')
  return res.data
}

export async function listGenerationAssets(): Promise<KnowledgeAsset[]> {
  const res = await api.get<KnowledgeAsset[]>('/generation/assets')
  return res.data
}

export async function listGenerationTodos(): Promise<string[]> {
  const res = await api.get<string[]>('/generation/todos')
  return res.data
}

export async function getLatestGenerationJob(): Promise<GenerationJob> {
  const res = await api.get<GenerationJob>('/generation/jobs/latest')
  return res.data
}

export async function getGenerationJob(jobId: string): Promise<GenerationJob> {
  const res = await api.get<GenerationJob>(`/generation/jobs/${jobId}`)
  return res.data
}

export async function getGenerationJobSections(jobId: string): Promise<GenerationSection[]> {
  const res = await api.get<GenerationSection[]>(`/generation/jobs/${jobId}/sections`)
  return res.data
}
