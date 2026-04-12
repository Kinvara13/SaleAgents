export type ViewKey =
  | "overview"
  | "projects"
  | "parsing"
  | "decision"
  | "generation"
  | "review"
  | "rules";

export type NavItem = {
  key: ViewKey;
  index: string;
  label: string;
  summary: string;
};

export type MetricItem = {
  label: string;
  value: string;
  hint?: string;
  tone?: string;
};

export type ModuleCard = {
  title: string;
  description: string;
  status: string;
  metric: string;
};

export type ProjectRow = {
  id?: string;
  name: string;
  owner: string;
  client: string;
  deadline: string;
  amount: string;
  status: string;
  risk: string;
  module_progress?: Record<string, string>;
};

export type ProjectCreateInput = {
  name: string;
  owner: string;
  client: string;
  deadline: string;
  amount: string;
  risk: string;
  status?: string;
};

export type ParseSection = {
  title: string;
  page: string;
  state: string;
  source_text?: string;
  source_file?: string;
};

export type ExtractedField = {
  label: string;
  value: string;
  confidence: string;
};

export type ProjectDocument = {
  id: string;
  project_id: string;
  file_name: string;
  file_type: string;
  document_type: string;
  parse_status: string;
  created_at: string;
  updated_at: string;
  latest_version_no?: number;
  versions?: {
    id: string;
    document_id: string;
    project_id: string;
    version_no: number;
    file_name: string;
    file_type: string;
    document_type: string;
    storage_backend: string;
    object_key: string;
    file_size: number;
    parse_status: string;
    created_at: string;
  }[];
};

export type ScoreCard = {
  label: string;
  score: number;
  note: string;
};

export type RuleHit = {
  name: string;
  result: string;
  detail: string;
  level: string;
};

export type GenerationSection = {
  title: string;
  status: string;
  citations: number;
  todo: number;
};

export type KnowledgeAsset = {
  title: string;
  type: string;
  score: string;
  status: string;
};

export type ReviewIssue = {
  id?: string;
  title: string;
  type: string;
  level: string;
  status: string;
  document: string;
  detail: string;
  evidence?: string;
  suggestion?: string;
  origin?: string;
  rule_name?: string;
  resolution_note?: string;
};

export type ReviewClause = {
  id: string;
  job_id: string;
  clause_no: number;
  title: string;
  content: string;
  source_ref: string;
};

export type ReviewJob = {
  id: string;
  contract_name: string;
  contract_type: string;
  trigger: string;
  status: string;
  overall_risk: string;
  issue_count: number;
  high_risk_issue_count: number;
  summary: MetricItem[];
  review_actions: string[];
  created_at: string;
  updated_at: string;
  completed_at: string | null;
};

export type ReviewFeedback = {
  id: string;
  issue_id: string;
  job_id: string;
  rule_name: string;
  feedback_type: string;
  feedback_note: string;
  reviewer: string;
  created_at: string;
};

export type RuleConfig = {
  id: string;
  name: string;
  title: string;
  issue_type: string;
  level: string;
  detail: string;
  suggestion: string;
  patterns: string;
  document: string;
  match_mode: string;
  is_enabled: boolean;
  priority: number;
  category: string;
  description: string;
  created_at: string;
  updated_at: string;
};

export type RuleStatistics = {
  rule_name: string;
  hit_count: number;
  confirmed_count: number;
  dismissed_count: number;
  modified_count: number;
  accuracy_rate: number;
  last_feedback_at: string | null;
};

export type GenerationJob = {
  id: string;
  project_id: string | null;
  project_name: string;
  template_name: string;
  status: string;
  section_count: number;
  overall_progress: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
};

export type GenerationProjectContext = {
  project_id: string;
  project_name: string;
  client_name: string;
  template_name: string;
  project_summary: string;
  tender_requirements: string;
  delivery_deadline: string;
  service_commitment: string;
  selected_asset_titles: string[];
  section_titles: string[];
  fixed_asset_titles: string[];
  excluded_asset_titles: string[];
};

export type IndexedGenerationAsset = {
  id: string;
  title: string;
  asset_type: string;
  score: string;
  status: string;
  summary: string;
  keywords: string[];
  scene_tags: string[];
  section_tags: string[];
  source_kind: string;
  file_name: string;
  owner: string;
  visibility: string;
  review_status: string;
  reviewer: string;
  review_note: string;
};

export type GenerationAssetChunk = {
  id: string;
  asset_id: string;
  title: string;
  content: string;
  keywords: string[];
  section_tags: string[];
  sort_order: number;
  weight: number;
};

export type GenerationAssetIndexJob = {
  id: string;
  asset_id: string;
  status: string;
  triggered_by: string;
  refreshed_count: number;
  error_message: string;
  created_at: string;
  completed_at: string | null;
};

export type ProjectGenerationAssetPreferences = {
  project_id: string;
  fixed_asset_titles: string[];
  excluded_asset_titles: string[];
};

export type ParsedFileInfo = {
  file_name: string;
  file_type: string;
  parse_status: string;
  document_type: string;
  section_found: string;
  word_count: number;
  skip_reason?: string;
};

export type ProjectParsingContext = {
  project_id: string;
  documents: ProjectDocument[];
  parse_sections: ParseSection[];
  extracted_fields: ExtractedField[];
  source_excerpt: string;
  parsed_files?: ParsedFileInfo[];
  debug_info?: {
    total_files_in_zip: number;
    parsed_count: number;
    skipped_count: number;
    all_files_in_zip: string[];
  };
};

export type GenerationSectionRecord = {
  id: string;
  job_id: string;
  section_no: number;
  title: string;
  content: string;
  status: string;
  citations: number;
  todos: number;
  created_at: string;
  routed_assets?: string[];
  routing_reasons?: string[];
  matched_score_items?: string[];
  missing_requirements?: string[];
  coverage_score?: number;
};

export type GenerationScoreItem = {
  id: string;
  title: string;
  source: string;
  weight: number;
  mapped_sections: string[];
  matched_sections: string[];
  matched_keywords: string[];
  coverage_status: string;
};

export type GenerationCheck = {
  id: string;
  level: string;
  category: string;
  title: string;
  detail: string;
  related_sections: string[];
};

export type GenerationSectionCoverage = {
  section_id: string;
  section_title: string;
  coverage_score: number;
  matched_score_items: string[];
  missing_requirements: string[];
  self_check_notes: string[];
};

export type GenerationJobAnalysis = {
  job_id: string;
  overall_coverage_score: number;
  mapped_score_item_count: number;
  covered_score_item_count: number;
  uncovered_score_item_count: number;
  score_items: GenerationScoreItem[];
  checks: GenerationCheck[];
  section_coverages: GenerationSectionCoverage[];
};

export type WorkspaceData = {
  navItems: NavItem[];
  overviewMetrics: MetricItem[];
  modules: ModuleCard[];
  projectStats: MetricItem[];
  projectFilters: string[];
  projectRows: ProjectRow[];
  parseSections: ParseSection[];
  extractedFields: ExtractedField[];
  scoreCards: ScoreCard[];
  ruleHits: RuleHit[];
  aiReasons: string[];
  pendingChecks: string[];
  generationSections: GenerationSection[];
  generationAssets: KnowledgeAsset[];
  generationTodos: string[];
  reviewSummary: MetricItem[];
  reviewIssues: ReviewIssue[];
  reviewActions: string[];
};
