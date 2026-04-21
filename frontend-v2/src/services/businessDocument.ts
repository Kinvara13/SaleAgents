import api from './api'

// ============ Business Document (商务文档) ============

export interface BusinessDocumentSummary {
  id: string
  doc_type: string
  doc_name: string
  has_fillable_fields: boolean
  is_star_item: boolean
  score_point: string
  status: string
  source_file: string
}

export interface BusinessDocumentDetail extends BusinessDocumentSummary {
  project_id: string
  original_content: string
  editable_content: string
  rule_description: string
  return_file_list: string // JSON string
  source_file: string
}

export async function listBusinessDocuments(projectId: string): Promise<BusinessDocumentSummary[]> {
  const res = await api.get<BusinessDocumentSummary[]>(
    `/api/v1/projects/${projectId}/business-documents`
  )
  return res.data
}

export async function getBusinessDocumentDetail(
  projectId: string,
  docId: string
): Promise<BusinessDocumentDetail> {
  const res = await api.get<BusinessDocumentDetail>(
    `/api/v1/projects/${projectId}/business-documents/${docId}`
  )
  return res.data
}

export async function updateBusinessDocument(
  projectId: string,
  docId: string,
  payload: { editable_content?: string; status?: string }
): Promise<BusinessDocumentDetail> {
  const res = await api.patch<BusinessDocumentDetail>(
    `/api/v1/projects/${projectId}/business-documents/${docId}`,
    payload
  )
  return res.data
}
