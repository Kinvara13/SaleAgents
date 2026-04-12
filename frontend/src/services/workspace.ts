import { apiDelete, apiGet, apiGetText, apiPatch, apiPost, apiPostForm } from "../lib/api";
import { getWorkspaceData as getMockWorkspaceData } from "../data/mockApi";
import type {
  ExtractedField,
  GenerationJob,
  GenerationAssetChunk,
  GenerationAssetIndexJob,
  GenerationJobAnalysis,
  GenerationProjectContext,
  GenerationSectionRecord,
  IndexedGenerationAsset,
  ParseSection,
  ProjectCreateInput,
  ProjectGenerationAssetPreferences,
  ProjectParsingContext,
  ProjectDocument,
  ProjectRow,
  ReviewClause,
  ReviewFeedback,
  ReviewIssue,
  ReviewJob,
  RuleConfig,
  RuleHit,
  RuleStatistics,
  ScoreCard,
  WorkspaceData,
} from "../types";

function mapWorkspaceResponse(payload: any): WorkspaceData {
  return {
    navItems: payload.nav_items,
    overviewMetrics: payload.overview_metrics,
    modules: payload.modules,
    projectStats: payload.project_stats,
    projectFilters: payload.project_filters,
    projectRows: payload.project_rows,
    parseSections: payload.parse_sections,
    extractedFields: payload.extracted_fields,
    scoreCards: payload.score_cards,
    ruleHits: payload.rule_hits,
    aiReasons: payload.ai_reasons,
    pendingChecks: payload.pending_checks,
    generationSections: payload.generation_sections,
    generationAssets: payload.generation_assets,
    generationTodos: payload.generation_todos,
    reviewSummary: payload.review_summary,
    reviewIssues: payload.review_issues,
    reviewActions: payload.review_actions,
  };
}

function applyFocusedWorkspace(data: WorkspaceData): WorkspaceData {
  const highRiskIssues = data.reviewIssues.filter((item) => ["P0", "P1"].includes(item.level)).length;
  const highRiskProjects = data.projectRows.filter((item) => ["P0", "P1"].includes(item.risk)).length;
  const draftingProjects = data.projectRows.filter((item) =>
    ["待决策", "生成中", "审核中"].includes(item.status),
  ).length;
  const weeklyDeadlines = data.projectRows.filter((item) => item.deadline.trim().length > 0).length;
  const pendingReviewActions = data.reviewActions.length;
  const pendingDraftActions = data.generationTodos.length + data.pendingChecks.length;

  return {
    ...data,
    navItems: [
      { key: "overview", index: "00", label: "产品总览", summary: "全局统计与各模块业务进展" },
      { key: "projects", index: "01", label: "商机台账", summary: "管理项目、截止时间与优先级" },
      { key: "parsing", index: "02", label: "要求提取", summary: "抽取资格、评分和格式要求" },
      { key: "decision", index: "03", label: "应答策略", summary: "汇总评分点、规则和推进建议" },
      { key: "generation", index: "04", label: "回标编写", summary: "自动生成符合要求的应答文件" },
      { key: "review", index: "05", label: "合同审查", summary: "识别红线条款并给出建议" },
      { key: "rules", index: "06", label: "规则中心", summary: "管理审查规则库与命中统计" },
    ],
    overviewMetrics: [
      { label: "项目总数", value: `${data.projectRows.length}`, hint: "当前库内跟进的招投标项目" },
      { label: "待回标", value: `${draftingProjects}`, hint: "仍在推进应答文件的项目" },
      { label: "高风险项", value: `${highRiskIssues}`, hint: "所有审查任务中发现的高风险条款" },
      { label: "企业资产", value: `${data.generationAssets.length}`, hint: "当前可引用的知识库素材片段" },
    ],
    modules: [
      {
        title: "合同审查机器人",
        description: "自动识别付款、违约、交付边界与责任分配中的风险条款，并输出解释与修订建议。",
        status: "运行中",
        metric: `累计发现 ${data.reviewIssues.length} 个审查问题`,
      },
      {
        title: "回标文件自动编写",
        description: "依据招标要求、模板和知识库素材生成符合格式要求的回标文件初稿。",
        status: "运行中",
        metric: `提供 ${data.generationSections.length} 个应答章节模板`,
      },
      {
        title: "招投标全链路支撑",
        description: "把资格门槛、评分办法结构化，辅助应答决策，提供企业知识库与规则引擎底座。",
        status: "运行中",
        metric: `支持多模态文档解析与资产检索`,
      },
    ],
    projectStats: [
      { label: "待回标项目", value: `${draftingProjects}`, tone: "blue", hint: "仍在推进应答文件" },
      { label: "待合同审查", value: `${pendingReviewActions}`, tone: "cyan", hint: "风险动作需要处理" },
      { label: "高风险商机", value: `${highRiskProjects}`, tone: "amber", hint: "需优先判断是否继续推进" },
      { label: "本周截止", value: `${weeklyDeadlines}`, tone: "violet", hint: "排期最紧的项目窗口" },
    ],
    projectFilters: ["全部商机", "待回标", "待合同审查", "本周截止", "高风险"],
  };
}

export async function getWorkspaceData(): Promise<WorkspaceData> {
  try {
    const payload = await apiGet<any>("/workspace");
    const data = applyFocusedWorkspace(mapWorkspaceResponse(payload));
    const [projects, parseSections, extractedFields, scoreCards, ruleHits, aiReasons, reviewSummary, reviewIssues, reviewActions] =
      await Promise.allSettled([
        apiGet<ProjectRow[]>("/projects"),
        apiGet<ParseSection[]>("/parsing/sections"),
        apiGet<ExtractedField[]>("/parsing/fields"),
        apiGet<ScoreCard[]>("/decision/scores"),
        apiGet<RuleHit[]>("/decision/rules"),
        apiGet<string[]>("/decision/reasons"),
        apiGet<WorkspaceData["reviewSummary"]>("/review/summary"),
        apiGet<ReviewIssue[]>("/review/issues"),
        apiGet<string[]>("/review/actions"),
      ]);

    if (projects.status === "fulfilled") {
      data.projectRows = projects.value;
    }
    if (parseSections.status === "fulfilled") {
      data.parseSections = parseSections.value;
    }
    if (extractedFields.status === "fulfilled") {
      data.extractedFields = extractedFields.value;
    }
    if (scoreCards.status === "fulfilled") {
      data.scoreCards = scoreCards.value;
    }
    if (ruleHits.status === "fulfilled") {
      data.ruleHits = ruleHits.value;
    }
    if (aiReasons.status === "fulfilled") {
      data.aiReasons = aiReasons.value;
    }
    if (reviewSummary.status === "fulfilled") {
      data.reviewSummary = reviewSummary.value;
    }
    if (reviewIssues.status === "fulfilled") {
      data.reviewIssues = reviewIssues.value;
    }
    if (reviewActions.status === "fulfilled") {
      data.reviewActions = reviewActions.value;
    }

    return data;
  } catch {
    return applyFocusedWorkspace(await getMockWorkspaceData());
  }
}

export async function createProject(input: ProjectCreateInput): Promise<ProjectRow> {
  return apiPost<ProjectRow, ProjectCreateInput>("/projects", {
    ...input,
    status: input.status ?? "待决策",
  });
}

export async function getProjectDetail(projectId: string): Promise<ProjectRow> {
  return apiGet<ProjectRow>(`/projects/${projectId}`);
}

export async function updateProject(projectId: string, input: { status?: string }): Promise<ProjectRow> {
  return apiPatch<ProjectRow, typeof input>(`/projects/${projectId}`, input);
}

export async function uploadReviewContract(input: {
  file: File;
  contractName: string;
  contractType: string;
}): Promise<ReviewJob> {
  const payload = new FormData();
  payload.append("file", input.file);
  payload.append("contract_name", input.contractName);
  payload.append("contract_type", input.contractType);
  return apiPostForm<ReviewJob>("/review/jobs/upload", payload);
}

export async function getReviewJobClauses(jobId: string): Promise<ReviewClause[]> {
  return apiGet<ReviewClause[]>(`/review/jobs/${jobId}/clauses`);
}

export async function getLatestReviewJob(): Promise<ReviewJob | null> {
  try {
    return await apiGet<ReviewJob>("/review/jobs/latest");
  } catch {
    return null;
  }
}

export async function getReviewJobIssues(jobId: string): Promise<ReviewIssue[]> {
  return apiGet<ReviewIssue[]>(`/review/jobs/${jobId}/issues`);
}

export async function rerunReviewJob(jobId: string): Promise<ReviewJob> {
  return apiPost<ReviewJob, Record<string, never>>(`/review/jobs/${jobId}/rerun`, {});
}

export async function resolveReviewIssue(issueId: string, resolutionNote: string): Promise<ReviewIssue> {
  return apiPost<ReviewIssue, { status: string; resolution_note: string }>(`/review/issues/${issueId}/resolve`, {
    status: "已处理",
    resolution_note: resolutionNote,
  });
}

export async function exportReviewJobReport(jobId: string): Promise<string> {
  return apiGetText(`/review/jobs/${jobId}/report`);
}

export async function exportReviewJobReportDocx(jobId: string): Promise<Blob> {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/review/jobs/${jobId}/report/docx`);
  if (!response.ok) {
    throw new Error("Failed to export DOCX report");
  }
  return response.blob();
}

export async function submitReviewFeedback(
  issueId: string,
  feedbackType: string,
  feedbackNote: string,
  reviewer: string,
): Promise<ReviewFeedback> {
  return apiPost<ReviewFeedback, { feedback_type: string; feedback_note: string; reviewer: string }>(
    `/review/issues/${issueId}/feedback`,
    {
      feedback_type: feedbackType,
      feedback_note: feedbackNote,
      reviewer: reviewer,
    },
  );
}

export async function getRuleConfigs(isEnabled?: boolean, category?: string): Promise<RuleConfig[]> {
  const params = new URLSearchParams();
  if (isEnabled !== undefined) {
    params.append("is_enabled", String(isEnabled));
  }
  if (category) {
    params.append("category", category);
  }
  const query = params.toString() ? `?${params.toString()}` : "";
  return apiGet<RuleConfig[]>(`/review/rules${query}`);
}

export async function getRuleConfig(ruleId: string): Promise<RuleConfig> {
  return apiGet<RuleConfig>(`/review/rules/${ruleId}`);
}

export async function initializeDefaultRules(): Promise<{ initialized: number; message: string }> {
  return apiPost<{ initialized: number; message: string }, Record<string, never>>("/review/rules/initialize", {});
}

export async function createRuleConfig(input: {
  name: string;
  title: string;
  issue_type: string;
  level: string;
  detail: string;
  suggestion: string;
  patterns?: string;
  document?: string;
  match_mode?: string;
  is_enabled?: boolean;
  priority?: number;
  category?: string;
  description?: string;
}): Promise<RuleConfig> {
  return apiPost<RuleConfig, typeof input>("/review/rules", input);
}

export async function updateRuleConfig(
  ruleId: string,
  input: {
    title?: string;
    issue_type?: string;
    level?: string;
    detail?: string;
    suggestion?: string;
    patterns?: string;
    document?: string;
    match_mode?: string;
    is_enabled?: boolean;
    priority?: number;
    category?: string;
    description?: string;
  },
): Promise<RuleConfig> {
  return apiPatch<RuleConfig, typeof input>(`/review/rules/${ruleId}`, input);
}

export async function deleteRuleConfig(ruleId: string): Promise<void> {
  await fetch(`${import.meta.env.VITE_API_BASE_URL}/review/rules/${ruleId}`, {
    method: "DELETE",
  });
}

export async function getRuleStatistics(ruleName?: string): Promise<RuleStatistics[]> {
  const params = ruleName ? `?rule_name=${encodeURIComponent(ruleName)}` : "";
  return apiGet<RuleStatistics[]>(`/review/rules/statistics${params}`);
}

export async function getProjectParsingContext(projectId: string): Promise<ProjectParsingContext> {
  return apiGet<ProjectParsingContext>(`/parsing/projects/${projectId}`);
}

export async function uploadProjectTenderDocument(input: {
  projectId: string;
  file: File;
  documentType?: string;
}): Promise<ProjectParsingContext> {
  const payload = new FormData();
  payload.append("file", input.file);
  payload.append("document_type", input.documentType ?? "招标文件");
  const response = await apiPostForm<{
    document: ProjectDocument;
    parse_sections: ParseSection[];
    extracted_fields: ExtractedField[];
    source_excerpt: string;
  }>(`/parsing/projects/${input.projectId}/upload`, payload);
  return {
    project_id: input.projectId,
    documents: [response.document],
    parse_sections: response.parse_sections,
    extracted_fields: response.extracted_fields,
    source_excerpt: response.source_excerpt,
  };
}

export async function rerunProjectParsing(projectId: string): Promise<ProjectParsingContext> {
  const response = await apiPost<{
    project_id: string;
    parse_sections: ParseSection[];
    extracted_fields: ExtractedField[];
    source_excerpt: string;
  }, Record<string, never>>(`/parsing/projects/${projectId}/run`, {});
  const context = await getProjectParsingContext(projectId);
  return {
    ...context,
    parse_sections: response.parse_sections,
    extracted_fields: response.extracted_fields,
    source_excerpt: response.source_excerpt,
  };
}

export async function updateProjectParsingField(
  projectId: string,
  fieldLabel: string,
  value: string,
): Promise<ExtractedField> {
  const response = await fetch(
    `${import.meta.env.VITE_API_BASE_URL}/parsing/projects/${projectId}/fields/${encodeURIComponent(fieldLabel)}`,
    {
      method: "PATCH",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ value }),
    },
  );
  if (!response.ok) {
    throw new Error("Failed to update project parsing field");
  }
  return response.json();
}

// ---- Generation Job service functions ----

export async function createGenerationJob(input: {
  project_name: string;
  template_name?: string;
  project_id?: string;
  client_name?: string;
  project_summary?: string;
  tender_requirements?: string;
  delivery_deadline?: string;
  service_commitment?: string;
  selected_asset_titles?: string[];
  section_titles?: string[];
}): Promise<GenerationJob> {
  return apiPost<GenerationJob, typeof input>("/generation/jobs", {
    project_name: input.project_name,
    template_name: input.template_name ?? "标准回标模板",
    project_id: input.project_id,
    client_name: input.client_name ?? "",
    project_summary: input.project_summary ?? "",
    tender_requirements: input.tender_requirements ?? "",
    delivery_deadline: input.delivery_deadline ?? "",
    service_commitment: input.service_commitment ?? "",
    selected_asset_titles: input.selected_asset_titles ?? [],
    section_titles: input.section_titles ?? [],
  });
}

export async function getIndexedGenerationAssets(): Promise<IndexedGenerationAsset[]> {
  return apiGet<IndexedGenerationAsset[]>("/generation/assets/indexed");
}

export async function createGenerationAsset(input: {
  title: string;
  asset_type: string;
  status: string;
  content: string;
  owner?: string;
  visibility?: string;
}): Promise<IndexedGenerationAsset> {
  return apiPost<IndexedGenerationAsset, typeof input>("/generation/assets", {
    owner: "frontend",
    visibility: "internal",
    ...input,
  });
}

export async function uploadGenerationAsset(input: {
  file: File;
  assetType: string;
  title?: string;
}): Promise<IndexedGenerationAsset> {
  const payload = new FormData();
  payload.append("file", input.file);
  payload.append("asset_type", input.assetType);
  payload.append("owner", "frontend");
  payload.append("visibility", "internal");
  if (input.title?.trim()) {
    payload.append("title", input.title.trim());
  }
  return apiPostForm<IndexedGenerationAsset>("/generation/assets/upload", payload);
}

export type ScoreDimension = {
  label: string;
  score: number;
  note: string;
};

export type DecisionScore = {
  total: number;
  dimensions: ScoreDimension[];
};

export type DecisionRuleHit = {
  name: string;
  level: string;
  result: string;
  detail: string;
};

export type ProjectDecisionJob = {
  id: string;
  project_id: string;
  status: string;
  score: DecisionScore | null;
  rule_hits: DecisionRuleHit[] | null;
  ai_reasons: string[] | null;
  pending_checks: string[] | null;
  created_at: string;
  completed_at: string | null;
};

export async function runProjectDecision(projectId: string): Promise<ProjectDecisionJob> {
  return apiPost<ProjectDecisionJob, null>(`/decision/projects/${projectId}/run`, null);
}

export async function getLatestDecisionJob(projectId: string): Promise<ProjectDecisionJob> {
  return apiGet<ProjectDecisionJob>(`/decision/projects/${projectId}/latest`);
}

export async function refreshGenerationAssetIndex(assetId?: string): Promise<GenerationAssetIndexJob> {
  return apiPost<GenerationAssetIndexJob, { asset_id?: string | null; triggered_by: string }>(
    "/generation/assets/refresh-index",
    {
      asset_id: assetId ?? null,
      triggered_by: "frontend",
    },
  );
}

export async function getGenerationAssetIndexJob(jobId: string): Promise<GenerationAssetIndexJob> {
  return apiGet<GenerationAssetIndexJob>(`/generation/assets/refresh-index/${jobId}`);
}

export async function updateGenerationAsset(
  assetId: string,
  input: {
    title: string;
    asset_type: string;
    status: string;
    content: string;
    owner: string;
    visibility: string;
  },
): Promise<IndexedGenerationAsset> {
  return apiPatch<IndexedGenerationAsset, typeof input>(`/generation/assets/${assetId}`, input);
}

export async function deleteGenerationAsset(assetId: string): Promise<void> {
  return apiDelete(`/generation/assets/${assetId}`);
}

export async function reviewGenerationAsset(
  assetId: string,
  input: { action: "approve" | "reject"; reviewer: string; review_note: string },
): Promise<IndexedGenerationAsset> {
  return apiPost<IndexedGenerationAsset, typeof input>(`/generation/assets/${assetId}/review`, input);
}

export async function getGenerationAssetChunks(assetId: string): Promise<GenerationAssetChunk[]> {
  return apiGet<GenerationAssetChunk[]>(`/generation/assets/${assetId}/chunks`);
}

export async function createGenerationAssetChunk(
  assetId: string,
  input: { title: string; content: string; keywords: string[]; section_tags: string[]; weight: number },
): Promise<GenerationAssetChunk> {
  return apiPost<GenerationAssetChunk, typeof input>(`/generation/assets/${assetId}/chunks`, input);
}

export async function updateGenerationAssetChunk(
  assetId: string,
  chunkId: string,
  input: { title: string; content: string; keywords: string[]; section_tags: string[]; weight: number },
): Promise<GenerationAssetChunk> {
  return apiPatch<GenerationAssetChunk, typeof input>(`/generation/assets/${assetId}/chunks/${chunkId}`, input);
}

export async function deleteGenerationAssetChunk(assetId: string, chunkId: string): Promise<void> {
  return apiDelete(`/generation/assets/${assetId}/chunks/${chunkId}`);
}

export async function getProjectGenerationContext(projectId: string): Promise<GenerationProjectContext> {
  return apiGet<GenerationProjectContext>(`/projects/${projectId}/generation/context`);
}

export async function getProjectGenerationPreferences(
  projectId: string,
): Promise<ProjectGenerationAssetPreferences> {
  return apiGet<ProjectGenerationAssetPreferences>(`/projects/${projectId}/generation/preferences`);
}

export async function updateProjectGenerationPreferences(
  projectId: string,
  input: { fixed_asset_titles: string[]; excluded_asset_titles: string[] },
): Promise<ProjectGenerationAssetPreferences> {
  return apiPatch<ProjectGenerationAssetPreferences, typeof input>(
    `/projects/${projectId}/generation/preferences`,
    input,
  );
}

export async function runProjectGeneration(
  projectId: string,
  input: {
    template_name?: string;
    project_summary?: string;
    tender_requirements?: string;
    delivery_deadline?: string;
    service_commitment?: string;
    selected_asset_titles?: string[];
    section_titles?: string[];
  },
): Promise<GenerationJob> {
  return apiPost<GenerationJob, typeof input>(`/projects/${projectId}/generation/run`, input);
}

export async function getLatestGenerationJob(): Promise<GenerationJob | null> {
  try {
    return await apiGet<GenerationJob>("/generation/jobs/latest");
  } catch {
    return null;
  }
}

export async function getGenerationJobSections(jobId: string): Promise<GenerationSectionRecord[]> {
  return apiGet<GenerationSectionRecord[]>(`/generation/jobs/${jobId}/sections`);
}

export async function getGenerationJobAnalysis(jobId: string): Promise<GenerationJobAnalysis> {
  return apiGet<GenerationJobAnalysis>(`/generation/jobs/${jobId}/analysis`);
}

export async function regenerateSection(
  jobId: string,
  sectionId: string,
): Promise<GenerationSectionRecord> {
  return apiPost<GenerationSectionRecord, Record<string, never>>(
    `/generation/jobs/${jobId}/sections/${sectionId}/regenerate`,
    {},
  );
}

export async function repairGenerationJobUncovered(jobId: string): Promise<GenerationSectionRecord[]> {
  return apiPost<GenerationSectionRecord[], Record<string, never>>(`/generation/jobs/${jobId}/repair-uncovered`, {});
}

export async function selfReviseGenerationJob(jobId: string): Promise<GenerationSectionRecord[]> {
  return apiPost<GenerationSectionRecord[], Record<string, never>>(`/generation/jobs/${jobId}/self-revise`, {});
}

export async function exportGenerationJob(jobId: string): Promise<string> {
  return apiGetText(`/generation/jobs/${jobId}/export`);
}

export async function exportGenerationJobDocx(jobId: string): Promise<Blob> {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/generation/jobs/${jobId}/export/docx`);
  if (!response.ok) {
    throw new Error("Failed to export generation DOCX");
  }
  return response.blob();
}

export async function updateGenerationSection(
  jobId: string,
  sectionId: string,
  input: { content: string; status?: string },
): Promise<GenerationSectionRecord> {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/generation/jobs/${jobId}/sections/${sectionId}`, {
    method: "PATCH",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      content: input.content,
      status: input.status ?? "已编辑",
    }),
  });
  if (!response.ok) {
    throw new Error("Failed to update generation section");
  }
  return response.json();
}

// ---- LLM Config service functions ----

export type LLMProvider = {
  id: string;
  name: string;
  base_url: string;
  api_key_masked: string;
  model: string;
};

export type LLMConfigResponse = {
  providers: LLMProvider[];
  active_provider_id: string | null;
};

export async function getLLMConfig(): Promise<LLMConfigResponse> {
  return apiGet<LLMConfigResponse>("/llm-config");
}

export async function addLLMProvider(input: {
  name: string;
  base_url: string;
  api_key: string;
  model: string;
}): Promise<LLMProvider> {
  return apiPost<LLMProvider, typeof input>("/llm-config", input);
}

export async function updateLLMProvider(
  providerId: string,
  input: { name: string; base_url: string; api_key: string; model: string },
): Promise<LLMProvider> {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/llm-config/${providerId}`, {
    method: "PUT",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!response.ok) throw new Error("Failed to update LLM provider");
  return response.json();
}

export async function deleteLLMProvider(providerId: string): Promise<void> {
  return apiDelete(`/llm-config/${providerId}`);
}

export async function activateLLMProvider(providerId: string): Promise<void> {
  await apiPost<Record<string, never>, Record<string, never>>(`/llm-config/activate/${providerId}`, {});
}
