// SaleAgents 前端全局类型定义

export interface Project {
  id: string
  name: string
  status: string
  owner: string
  client: string
  deadline: string
  amount: string
  risk: string
  module_progress?: Record<string, string>
}

export interface ParsingSection {
  id: string
  project_id?: string
  section_name: string
  section_type: '商务' | '技术'
  content?: string
  is_star_item: boolean
  source_file: string
}

export interface ProposalSection {
  id: string
  project_id?: string
  section_name: string
  content?: string
  score: number
  is_confirmed: boolean
  is_generated: boolean
}

export interface UserInfo {
  id: string
  username: string
  name: string
  role: string
}

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

export interface ReviewIssue {
  title: string
  type: string
  level: string
  status: string
  document: string
  detail: string
  evidence?: string
  suggestion?: string
  origin?: string
  rule_name?: string
}

export interface MetricItem {
  label: string
  value: string
  hint?: string
  tone?: string
}

export interface NavItem {
  key: string
  index: string
  label: string
  summary: string
}

export interface ModuleCard {
  title: string
  description: string
  status: string
  metric: string
}
