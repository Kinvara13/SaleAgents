import api from './api'

// ============ 类型定义 ============

/** 标书章节 */
export interface ProposalSection {
  id: string
  title: string
  content: string
  order: number
}

/** 元数据 */
export interface ProposalMetadata {
  project_id?: string
  tender_id?: string
  created_at?: string
  updated_at?: string
  status: string
  author: string
}

/** 星标项 */
export interface StarItem {
  name: string
  source: string
  satisfied: boolean | null
}

/** 应答内容 */
export interface StarResponse {
  section: string
  content: string
}

/** 应答文件完整响应 */
export interface Proposal {
  id: string
  title: string
  content: string
  sections: ProposalSection[]
  metadata: ProposalMetadata
  star_items: StarItem[]
  star_responses: Record<string, StarResponse>
}

/** 更新请求 */
export interface ProposalUpdatePayload {
  title?: string
  content?: string
  sections?: ProposalSection[]
  metadata?: ProposalMetadata
  star_items?: StarItem[]
  star_responses?: Record<string, StarResponse>
}

/** 星标项确认请求 */
export interface StarItemConfirmPayload {
  satisfied: boolean
}

// ============ API 函数 ============

/**
 * 获取应答文件详情
 * @param proposalId 应答文件ID
 * @returns 应答文件完整信息
 */
export async function getProposal(proposalId: string): Promise<Proposal> {
  const res = await api.get<Proposal>(`/api/v1/proposal-editor/${proposalId}`)
  return res.data
}

/**
 * 更新应答文件
 * @param proposalId 应答文件ID
 * @param payload 更新内容
 * @returns 更新后的应答文件
 */
export async function updateProposal(proposalId: string, payload: ProposalUpdatePayload): Promise<Proposal> {
  const res = await api.put<Proposal>(`/api/v1/proposal-editor/${proposalId}`, payload)
  return res.data
}

/**
 * 确认星标项满足状态
 * @param proposalId 应答文件ID
 * @param itemName 星标项名称
 * @param satisfied 是否满足
 * @returns 确认结果
 */
export async function confirmStarItem(
  proposalId: string,
  itemName: string,
  satisfied: boolean
): Promise<StarItem> {
  const res = await api.post<StarItem>(
    `/api/v1/proposal-editor/${proposalId}/star-items/${encodeURIComponent(itemName)}/confirm`,
    { satisfied }
  )
  return res.data
}

/**
 * 获取星标项列表
 * @param proposalId 应答文件ID
 * @returns 星标项列表
 */
export async function listStarItems(proposalId: string): Promise<StarItem[]> {
  const res = await api.get<StarItem[]>(`/api/v1/proposal-editor/${proposalId}/star-items`)
  return res.data
}

/**
 * 更新章节内容
 * @param proposalId 应答文件ID
 * @param sectionId 章节ID
 * @param content 章节内容
 * @returns 更新后的章节
 */
export async function updateSectionContent(
  proposalId: string,
  sectionId: string,
  content: string
): Promise<ProposalSection> {
  const res = await api.post<ProposalSection>(
    `/api/v1/proposal-editor/${proposalId}/sections/${sectionId}/content`,
    { content },
    { headers: { 'Content-Type': 'application/json' } }
  )
  return res.data
}
