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
  bidding_company: string
  description: string
  module_progress: Record<string, string>
  parse_status?: string
  node_status?: Record<string, string>
  bid_template_files?: Array<{
    id: string
    name: string
    path: string
    status?: string
    selected?: boolean
    icon?: string
    section_type?: string
    section_name?: string
    responsible?: string
  }>
  extracted_fields?: Array<{label: string; value: string; confidence?: string}>
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
  name?: string
  owner?: string
  client?: string
  deadline?: string
  amount?: string
  risk?: string
  bidding_company?: string
  agent_name?: string
  agent_phone?: string
  agent_email?: string
  company_address?: string
  bank_name?: string
  bank_account?: string
  description?: string
  confirm_status?: string
  confirm_feedback?: string
  confirmed_by?: string
  confirmed_at?: string
  tender_id?: string
  parse_status?: string
  file_list?: any[]
  node_status?: Record<string, string> | any
  extracted_fields?: any[]
  bid_template_files?: any[]
}

export async function listProjects(status?: string, mine?: boolean): Promise<Project[]> {
  const params: Record<string, string | boolean> = {}
  if (status) params.status = status
  if (mine) params.mine = mine
  const res = await api.get<Project[]>('/projects', { params })
  return res.data
}

export async function getProject(id: string): Promise<Project> {
  const res = await api.get<Project>(`/projects/${id}`)
  return res.data
}

export async function createProject(payload: ProjectCreateRequest): Promise<Project> {
  const res = await api.post<Project>('/projects', payload)
  return res.data
}

export async function updateProject(id: string, payload: ProjectUpdateRequest): Promise<Project> {
  const res = await api.patch<Project>(`/projects/${id}`, payload)
  return res.data
}

export async function deleteProject(id: string): Promise<void> {
  await api.delete(`/projects/${id}`)
}

export async function uploadAndParseTender(projectId: string, file: File): Promise<any> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post(`/parsing/${projectId}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return res.data
}

export async function getTenderSections(projectId: string): Promise<any> {
  const res = await api.get(`/parsing/${projectId}/sections`)
  return res.data
}

export interface TenderSection {
  id: string
  section_name: string
  section_type: string
  is_star_item: boolean
  source_file: string
}

export async function getTenderSectionDetail(projectId: string, sectionId: string): Promise<any> {
  const res = await api.get(`/parsing/${projectId}/sections/${sectionId}`)
  return res.data
}

export async function updateTenderSection(
  projectId: string,
  sectionId: string,
  payload: { content?: string }
): Promise<any> {
  const res = await api.patch(`/parsing/${projectId}/sections/${sectionId}`, payload)
  return res.data
}

// ============ Project Detail Extensions ============

export interface BidFile {
  id: string
  name: string
  status: string
  icon: string
  responsible: string
}

export interface BidSection {
  id: number
  name: string
  icon: string
  completed: number
  total: number
  files: BidFile[]
}

export interface ScoringCriteriaItem {
  primary: string
  secondary: string
  standard: string
  maxScore: number
  type: '客观' | '主观'
  estimatedScore: number
  isFirstInGroup: boolean
  groupSpan: number
}

export interface ProjectActivity {
  icon: string
  iconBg: string
  iconColor: string
  title: string
  time: string
}

export async function getProjectBidProgress(projectId: string): Promise<BidSection[]> {
  const res = await api.get<{ sections: BidSection[] }>(`/projects/${projectId}/bid-progress`)
  return res.data.sections
}

export async function getProjectScoringCriteria(projectId: string): Promise<ScoringCriteriaItem[]> {
  const res = await api.get<ScoringCriteriaItem[]>(`/projects/${projectId}/scoring-criteria`)
  return res.data
}

export async function getProjectActivities(projectId: string): Promise<ProjectActivity[]> {
  const res = await api.get<{ activities: ProjectActivity[] }>(`/projects/${projectId}/activities`)
  return res.data.activities
}

// ============ Knowledge Assets ============

export interface KnowledgeAsset {
  id: string
  title: string
  asset_type: string
  score: string
  status: string
  summary: string
}

export async function listKnowledgeAssets(assetType?: string, limit: number = 20): Promise<KnowledgeAsset[]> {
  const params: Record<string, string | number> = { limit }
  if (assetType) params.asset_type = assetType
  const res = await api.get<KnowledgeAsset[]>('/knowledge/knowledge-assets', { params })
  return res.data
}

export async function uploadBidTemplate(projectId: string, file: File): Promise<{status: string; message: string; filename: string; files: any[]}> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post(`/bid-template/${projectId}/upload-template`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return res.data
}

export async function updateBidTemplateFiles(projectId: string, files: any[]): Promise<any> {
  const res = await api.put(`/bid-template/${projectId}/template-files`, files)
  return res.data
}

export async function previewBidTemplateFile(projectId: string, filePath: string): Promise<{status: string; filename: string; content: string}> {
  const res = await api.get(`/bid-template/${projectId}/template-files/${encodeURIComponent(filePath)}/preview`)
  return res.data
}
