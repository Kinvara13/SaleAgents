import api from './api'

// ============ Technical Document (技术文档) ============

export interface TechnicalDocumentSummary {
  id: string
  doc_type: string
  doc_name: string
  has_fillable_fields: boolean
  is_star_item: boolean
  score_point: string
  status: string
  source_file: string
}

export interface TechnicalDocumentDetail extends TechnicalDocumentSummary {
  project_id: string
  original_content: string
  editable_content: string
  rule_description: string
  return_file_list: string // JSON string
  source_file: string
}

export async function listTechnicalDocuments(projectId: string): Promise<TechnicalDocumentSummary[]> {
  const res = await api.get<TechnicalDocumentSummary[]>(
    `/api/v1/projects/${projectId}/technical-documents`
  )
  return res.data
}

export async function getTechnicalDocumentDetail(
  projectId: string,
  docId: string
): Promise<TechnicalDocumentDetail> {
  const res = await api.get<TechnicalDocumentDetail>(
    `/api/v1/projects/${projectId}/technical-documents/${docId}`
  )
  return res.data
}

export async function updateTechnicalDocument(
  projectId: string,
  docId: string,
  payload: { editable_content?: string; status?: string }
): Promise<TechnicalDocumentDetail> {
  const res = await api.patch<TechnicalDocumentDetail>(
    `/api/v1/projects/${projectId}/technical-documents/${docId}`,
    payload
  )
  return res.data
}