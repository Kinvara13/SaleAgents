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
    `/projects/${projectId}/technical-documents`
  )
  return res.data
}

export async function getTechnicalDocumentDetail(
  projectId: string,
  docId: string
): Promise<TechnicalDocumentDetail> {
  const res = await api.get<TechnicalDocumentDetail>(
    `/projects/${projectId}/technical-documents/${docId}`
  )
  return res.data
}

export async function updateTechnicalDocument(
  projectId: string,
  docId: string,
  payload: { editable_content?: string; status?: string }
): Promise<TechnicalDocumentDetail> {
  const res = await api.patch<TechnicalDocumentDetail>(
    `/projects/${projectId}/technical-documents/${docId}`,
    payload
  )
  return res.data
}

export async function generateTechnicalDocument(
  projectId: string,
  docId: string
): Promise<TechnicalDocumentDetail> {
  const res = await api.post<TechnicalDocumentDetail>(
    `/projects/${projectId}/technical-documents/${docId}/generate`
  )
  return res.data
}

export interface DocumentExportResult {
  download_url: string
  filename: string
  format: string
}

export async function exportTechnicalDocument(
  projectId: string,
  docId: string,
  fmt?: string
): Promise<DocumentExportResult> {
  const res = await api.post<DocumentExportResult>(
    `/projects/${projectId}/technical-documents/${docId}/export`,
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

export async function scoreTechnicalDocument(
  projectId: string,
  docId: string
): Promise<DocumentScoreResult> {
  const res = await api.get<DocumentScoreResult>(
    `/projects/${projectId}/technical-documents/${docId}/score`
  )
  return res.data
}