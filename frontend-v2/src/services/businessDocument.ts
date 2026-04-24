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
    `/projects/${projectId}/business-documents`
  )
  return res.data
}

export async function getBusinessDocumentDetail(
  projectId: string,
  docId: string
): Promise<BusinessDocumentDetail> {
  const res = await api.get<BusinessDocumentDetail>(
    `/projects/${projectId}/business-documents/${docId}`
  )
  return res.data
}

export async function updateBusinessDocument(
  projectId: string,
  docId: string,
  payload: { editable_content?: string; status?: string }
): Promise<BusinessDocumentDetail> {
  const res = await api.patch<BusinessDocumentDetail>(
    `/projects/${projectId}/business-documents/${docId}`,
    payload
  )
  return res.data
}

export async function generateBusinessDocument(
  projectId: string,
  docId: string
): Promise<BusinessDocumentDetail> {
  const res = await api.post<BusinessDocumentDetail>(
    `/projects/${projectId}/business-documents/${docId}/generate`
  )
  return res.data
}

export interface DocumentExportResult {
  download_url: string
  filename: string
  format: string
}

export async function exportBusinessDocument(
  projectId: string,
  docId: string,
  fmt?: string
): Promise<DocumentExportResult> {
  const res = await api.post<DocumentExportResult>(
    `/projects/${projectId}/business-documents/${docId}/export`,
    null,
    { params: fmt ? { fmt } : undefined }
  )
  return res.data
}

export interface DocumentScoreResult {
  score: number
  max_score: number
  is_scored: boolean
  breakdown: Record<string, unknown>
  message?: string
}

export async function scoreBusinessDocument(
  projectId: string,
  docId: string
): Promise<DocumentScoreResult> {
  const res = await api.get<DocumentScoreResult>(
    `/projects/${projectId}/business-documents/${docId}/score`
  )
  return res.data
}
