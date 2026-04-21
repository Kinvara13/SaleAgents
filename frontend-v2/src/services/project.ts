import api from './api'

export interface Project {
  id: string
  name: string
  status: string
  owner: string
  client: string
  deadline: string
  amount: string
  risk: string
  module_progress: Record<string, string>
}

export interface ProjectCreateRequest {
  name: string
  owner: string
  client?: string
  deadline?: string
  amount?: string
  risk?: string
  status?: string
}

export interface ProjectUpdateRequest {
  status?: string
}

export async function listProjects(status?: string, mine?: boolean): Promise<Project[]> {
  const params: Record<string, string | boolean> = {}
  if (status) params.status = status
  if (mine) params.mine = mine
  const res = await api.get<Project[]>('/api/v1/projects', { params })
  return res.data
}

export async function getProject(id: string): Promise<Project> {
  const res = await api.get<Project>(`/api/v1/projects/${id}`)
  return res.data
}

export async function createProject(payload: ProjectCreateRequest): Promise<Project> {
  const res = await api.post<Project>('/api/v1/projects', payload)
  return res.data
}

export async function updateProject(id: string, payload: ProjectUpdateRequest): Promise<Project> {
  const res = await api.patch<Project>(`/api/v1/projects/${id}`, payload)
  return res.data
}

export async function deleteProject(id: string): Promise<void> {
  await api.delete(`/api/v1/projects/${id}`)
}
