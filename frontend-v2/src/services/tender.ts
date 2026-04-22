import api from './api'

// ============ Parsing (标书拆分) ============

export interface ParsingSection {
  id: string
  section_name: string
  section_type: '商务' | '技术'
  is_star_item: boolean
  source_file: string
}

export interface ParsingSectionDetail extends ParsingSection {
  project_id: string
  content: string
}

export async function listParsingSections(projectId: string): Promise<ParsingSection[]> {
  const res = await api.get<ParsingSection[]>(`/parsing/${projectId}/sections`)
  return res.data
}

export async function getParsingSectionDetail(
  projectId: string,
  sectionId: string
): Promise<ParsingSectionDetail> {
  const res = await api.get<ParsingSectionDetail>(
    `/parsing/${projectId}/sections/${sectionId}`
  )
  return res.data
}

export async function updateParsingSection(
  projectId: string,
  sectionId: string,
  content: string
): Promise<ParsingSectionDetail> {
  const res = await api.patch<ParsingSectionDetail>(
    `/parsing/${projectId}/sections/${sectionId}`,
    { content }
  )
  return res.data
}

export async function uploadAndParse(projectId: string, file: File): Promise<ParsingSection[]> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post<ParsingSection[]>(
    `/parsing/${projectId}/upload`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return res.data
}

// ============ Tender (招标信息) ============

export interface Tender {
  id: string
  title: string
  source_url: string
  publish_date: string
  deadline: string
  amount: string
  margin: string
  project_type: string
  description: string
  decision: 'pending' | 'bid' | 'reject'
  reject_reason: string
  project_id: string
  user_id: string
  created_at: string
}

export async function listTenders(): Promise<Tender[]> {
  const res = await api.get<Tender[]>('/tenders')
  return res.data
}

export async function getTender(id: string): Promise<Tender> {
  const res = await api.get<Tender>(`/tenders/${id}`)
  return res.data
}

export async function submitDecision(
  id: string,
  payload: { decision: 'bid' | 'reject'; reason?: string; margin?: string; project_type?: string }
): Promise<Tender> {
  const res = await api.post<Tender>(`/tenders/${id}/decision`, payload)
  return res.data
}

export async function uploadBidDocument(id: string, file: File, margin?: string, projectType?: string): Promise<Tender> {
  const formData = new FormData()
  formData.append('file', file)
  if (margin) formData.append('margin', margin)
  if (projectType) formData.append('project_type', projectType)
  
  const res = await api.post<Tender>(
    `/tenders/${id}/upload`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return res.data
}
