import api from './api'

// ============ 类型定义 ============

/** 技术建议书章节摘要 */
export interface ProposalSectionSummary {
  id: string
  section_name: string
  score: number
  is_confirmed: boolean
  is_generated: boolean
}

/** 技术建议书章节详情 */
export interface ProposalSectionDetail {
  id: string
  project_id: string
  section_name: string
  content: string
  score: number
  is_confirmed: boolean
  is_generated: boolean
}

/** 更新章节请求 */
export interface ProposalSectionUpdateRequest {
  content?: string
  is_confirmed?: boolean
}

/** 评分响应 */
export interface ProposalScoreResponse {
  sections: ProposalSectionSummary[]
  total_score: number
}

/** 生成请求 */
export interface ProposalGenerationRequest {
  include_client_bg?: boolean
  include_company_bg?: boolean
  reference_scoring?: boolean
}

/** 任务提交响应 */
export interface TaskSubmitResponse {
  task_id: string
  status: string
  message: string
}

// ============ API 函数 ============

/**
 * 获取项目的技术建议书章节列表
 */
export async function listProposalSections(projectId: string): Promise<ProposalSectionSummary[]> {
  const res = await api.get<ProposalSectionSummary[]>(`/proposal-editor/${projectId}/sections`)
  return res.data
}

/**
 * 获取技术建议书章节详情
 */
export async function getProposalSectionDetail(
  projectId: string,
  sectionId: string
): Promise<ProposalSectionDetail> {
  const res = await api.get<ProposalSectionDetail>(`/proposal-editor/${projectId}/sections/${sectionId}`)
  return res.data
}

/**
 * 更新技术建议书章节
 */
export async function updateProposalSection(
  projectId: string,
  sectionId: string,
  payload: ProposalSectionUpdateRequest
): Promise<ProposalSectionDetail> {
  const res = await api.patch<ProposalSectionDetail>(
    `/proposal-editor/${projectId}/sections/${sectionId}`,
    payload
  )
  return res.data
}

/**
 * 触发技术建议书生成任务
 */
export async function generateProposal(
  projectId: string,
  payload?: ProposalGenerationRequest
): Promise<TaskSubmitResponse> {
  const res = await api.post<TaskSubmitResponse>(`/proposal-editor/${projectId}/generate`, payload || {})
  return res.data
}

/**
 * 计算技术建议书评分
 */
export async function scoreProposal(projectId: string): Promise<ProposalScoreResponse> {
  const res = await api.post<ProposalScoreResponse>(`/proposal-editor/${projectId}/score`)
  return res.data
}

/**
 * 人工修改后重新评分
 */
export async function rescoreProposal(projectId: string): Promise<ProposalScoreResponse> {
  const res = await api.post<ProposalScoreResponse>(`/proposal-editor/${projectId}/rescore`)
  return res.data
}

/**
 * 确认全部章节
 */
export async function confirmProposal(projectId: string): Promise<ProposalSectionSummary[]> {
  const res = await api.post<ProposalSectionSummary[]>(`/proposal-editor/${projectId}/confirm`)
  return res.data
}

export async function exportProposalDocx(projectId: string): Promise<Blob> {
  const res = await api.get(`/proposal-editor/${projectId}/export/docx`, {
    responseType: 'blob',
  })
  return res.data
}

export interface TaskStatusResponse {
  id: string
  task_type: string
  project_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  result?: Record<string, unknown> | null
  error_message?: string | null
}

export async function getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
  const res = await api.get<TaskStatusResponse>(`/tasks/${taskId}`)
  return res.data
}

// ============ Legacy API（保留兼容） ============

/** @deprecated 使用 listProposalSections */
export async function getProposal(proposalId: string): Promise<any> {
  const res = await api.get(`/proposal-editor/${proposalId}`)
  return res.data
}

/** @deprecated 使用 updateProposalSection */
export async function updateProposal(proposalId: string, payload: any): Promise<any> {
  const res = await api.put(`/proposal-editor/${proposalId}`, payload)
  return res.data
}

/** @deprecated */
export async function confirmStarItem(proposalId: string, itemName: string, satisfied: boolean): Promise<any> {
  const res = await api.post(`/proposal-editor/${proposalId}/star-items/${encodeURIComponent(itemName)}/confirm`, { satisfied })
  return res.data
}

/** 星标项（前端类型，兼容旧代码） */
export interface StarItem {
  name: string
  source: string
  satisfied: boolean | null
}

/** 应答内容（前端类型，兼容旧代码） */
export interface StarResponse {
  section: string
  content: string
}
