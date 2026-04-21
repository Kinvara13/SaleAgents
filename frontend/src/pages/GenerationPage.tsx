import { useEffect, useMemo, useState, type ChangeEvent, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";
import { Modal } from "../components/Modal";
import { Select } from "../components/Select";
import {
  createGenerationAsset,
  createGenerationAssetChunk,
  createGenerationJob,
  deleteGenerationAsset,
  deleteGenerationAssetChunk,
  exportGenerationJob,
  exportGenerationJobDocx,
  exportGenerationJobDocxWithTemplate,
  getGenerationAssetChunks,
  getGenerationAssetIndexJob,
  getGenerationJobAnalysis,
  getGenerationJobSections,
  getIndexedGenerationAssets,
  getLatestGenerationJob,
  getLatestGenerationJobByProject,
  getProjectGenerationContext,
  getProjectGenerationPreferences,
  refreshGenerationAssetIndex,
  repairGenerationJobUncovered,
  reviewGenerationAsset,
  regenerateSection,
  runProjectGeneration,
  selfReviseGenerationJob,
  updateGenerationAsset,
  updateGenerationAssetChunk,
  updateProjectGenerationPreferences,
  updateGenerationSection,
  uploadGenerationAsset,
} from "../services/workspace";
import type {
  GenerationAssetChunk,
  GenerationAssetIndexJob,
  GenerationJobAnalysis,
  GenerationJob,
  GenerationSectionRecord,
  IndexedGenerationAsset,
  WorkspaceData,
} from "../types";

type GenerationPageProps = {
  data: WorkspaceData;
  onGenerationUpdated: () => Promise<void>;
};

function normalizeOutline(raw: string): string[] {
  return raw
    .split(/\n|,|，|;/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function normalizeTags(raw: string): string[] {
  return raw
    .split(/\n|,|，|;|；|\//)
    .map((item) => item.trim())
    .filter(Boolean);
}

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

export function GenerationPage({ data, onGenerationUpdated }: GenerationPageProps) {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlProjectId = searchParams.get("projectId");

  const [selectedProjectId, setSelectedProjectId] = useState<string | undefined>(
    urlProjectId || (data.projectRows.length > 0 ? data.projectRows[0].id : undefined)
  );

  useEffect(() => {
    if (selectedProjectId) {
      setSearchParams({ projectId: selectedProjectId });
    }
  }, [selectedProjectId, setSearchParams]);

  const projectId = selectedProjectId;
  const [currentJob, setCurrentJob] = useState<GenerationJob | null>(null);
  const [generationAnalysis, setGenerationAnalysis] = useState<GenerationJobAnalysis | null>(null);
  const [sections, setSections] = useState<GenerationSectionRecord[]>([]);
  const [activeSectionId, setActiveSectionId] = useState<string>("");
  const [draftContent, setDraftContent] = useState("");

  const [projectName, setProjectName] = useState("");
  const [clientName, setClientName] = useState("");
  const [templateName, setTemplateName] = useState("标准回标模板");
  const [projectSummary, setProjectSummary] = useState("");
  const [tenderRequirements, setTenderRequirements] = useState("");
  const [deliveryDeadline, setDeliveryDeadline] = useState("");
  const [serviceCommitment, setServiceCommitment] = useState("");
  const [customOutline, setCustomOutline] = useState("");
  const [selectedAssets, setSelectedAssets] = useState<string[]>([]);
  const [prefillProjectId, setPrefillProjectId] = useState<string>("");
  const [indexedAssets, setIndexedAssets] = useState<IndexedGenerationAsset[]>([]);
  const [fixedAssets, setFixedAssets] = useState<string[]>([]);
  const [excludedAssets, setExcludedAssets] = useState<string[]>([]);
  const [assetTitle, setAssetTitle] = useState("");
  const [assetType, setAssetType] = useState("通用素材");
  const [assetContent, setAssetContent] = useState("");
  const [assetUploadTitle, setAssetUploadTitle] = useState("");
  const [activeAssetId, setActiveAssetId] = useState("");
  const [assetOwner, setAssetOwner] = useState("frontend");
  const [assetVisibility, setAssetVisibility] = useState("internal");
  const [reviewerName, setReviewerName] = useState("frontend");
  const [reviewNote, setReviewNote] = useState("");
  const [assetChunks, setAssetChunks] = useState<GenerationAssetChunk[]>([]);
  const [activeChunkId, setActiveChunkId] = useState("");
  const [chunkTitle, setChunkTitle] = useState("");
  const [chunkContent, setChunkContent] = useState("");
  const [chunkKeywords, setChunkKeywords] = useState("");
  const [chunkSectionTags, setChunkSectionTags] = useState("");
  const [chunkWeight, setChunkWeight] = useState("1");
  const [indexJob, setIndexJob] = useState<GenerationAssetIndexJob | null>(null);
  const [isSavingPreferences, setIsSavingPreferences] = useState(false);
  const [isCreatingAsset, setIsCreatingAsset] = useState(false);
  const [isUploadingAsset, setIsUploadingAsset] = useState(false);
  const [isRefreshingAssets, setIsRefreshingAssets] = useState(false);
  const [isSavingAsset, setIsSavingAsset] = useState(false);
  const [isDeletingAsset, setIsDeletingAsset] = useState(false);
  const [isReviewingAsset, setIsReviewingAsset] = useState(false);
  const [isSavingChunk, setIsSavingChunk] = useState(false);
  const [isDeletingChunk, setIsDeletingChunk] = useState(false);
  const [isAssetManagerOpen, setIsAssetManagerOpen] = useState(false);

  const [activeTab, setActiveTab] = useState<"section" | "score" | "evidence">("section");
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isRepairing, setIsRepairing] = useState(false);
  const [isSelfRevising, setIsSelfRevising] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    title: string;
    message: string;
    onConfirm: () => void;
  }>({
    isOpen: false,
    title: "",
    message: "",
    onConfirm: () => {},
  });

  useEffect(() => {
    void syncLatestJob();
    void loadIndexedAssets();
  }, [projectId]);

  useEffect(() => {
    if (!projectId || projectId === prefillProjectId) {
      return;
    }

    void hydrateFromProject(projectId);
  }, [projectId, prefillProjectId]);

  const activeSection = useMemo(
    () => sections.find((item) => item.id === activeSectionId) ?? sections[0] ?? null,
    [activeSectionId, sections],
  );

  const activeAsset = useMemo(
    () => indexedAssets.find((item) => item.id === activeAssetId) ?? indexedAssets[0] ?? null,
    [activeAssetId, indexedAssets],
  );

  useEffect(() => {
    if (!activeSection) {
      setDraftContent("");
      return;
    }
    setActiveSectionId(activeSection.id);
    setDraftContent(activeSection.content);
  }, [activeSection?.id, activeSection?.content]);

  useEffect(() => {
    if (!indexedAssets.length) {
      setActiveAssetId("");
      setAssetChunks([]);
      return;
    }
    if (!activeAssetId || !indexedAssets.some((item) => item.id === activeAssetId)) {
      setActiveAssetId(indexedAssets[0].id);
    }
  }, [activeAssetId, indexedAssets]);

  useEffect(() => {
    if (!activeAsset) {
      return;
    }
    setAssetTitle(activeAsset.title);
    setAssetType(activeAsset.asset_type);
    setAssetContent(activeAsset.summary);
    setAssetOwner(activeAsset.owner || "frontend");
    setAssetVisibility(activeAsset.visibility || "internal");
    setReviewNote(activeAsset.review_note || "");
    void loadAssetChunks(activeAsset.id);
  }, [activeAsset?.id]);

  async function syncLatestJob(jobOverride?: GenerationJob | null) {
    const job = jobOverride ?? (projectId
      ? await getLatestGenerationJobByProject(projectId)
      : await getLatestGenerationJob());
    if (!job) {
      setCurrentJob(null);
      setGenerationAnalysis(null);
      setSections([]);
      setActiveSectionId("");
      return;
    }
    const [secs, analysis] = await Promise.all([
      getGenerationJobSections(job.id),
      getGenerationJobAnalysis(job.id),
    ]);
    setCurrentJob(job);
    setGenerationAnalysis(analysis);
    setSections(secs);
    setActiveSectionId(secs[0]?.id ?? "");
  }

  async function hydrateFromProject(nextProjectId: string) {
    try {
      const [context, preferences] = await Promise.all([
        getProjectGenerationContext(nextProjectId),
        getProjectGenerationPreferences(nextProjectId),
      ]);
      setPrefillProjectId(nextProjectId);
      setProjectName(context.project_name);
      setClientName(context.client_name);
      setTemplateName(context.template_name);
      setProjectSummary(context.project_summary);
      setTenderRequirements(context.tender_requirements);
      setDeliveryDeadline(context.delivery_deadline);
      setServiceCommitment(context.service_commitment);
      setCustomOutline(context.section_titles.join("\n"));
      setSelectedAssets(context.selected_asset_titles);
      setFixedAssets(preferences.fixed_asset_titles);
      setExcludedAssets(preferences.excluded_asset_titles);
      setErrorMsg("");
      setSuccessMsg(`已载入项目上下文：${context.project_name}`);
    } catch {
      setErrorMsg("加载项目生成上下文失败，请稍后重试。");
    }
  }

  async function loadIndexedAssets() {
    try {
      const assets = await getIndexedGenerationAssets();
      setIndexedAssets(assets);
    } catch {
      setIndexedAssets([]);
    }
  }

  async function loadAssetChunks(assetId: string) {
    try {
      const chunks = await getGenerationAssetChunks(assetId);
      setAssetChunks(chunks);
    } catch {
      setAssetChunks([]);
    }
  }

  function resetChunkEditor() {
    setActiveChunkId("");
    setChunkTitle("");
    setChunkContent("");
    setChunkKeywords("");
    setChunkSectionTags("");
    setChunkWeight("1");
  }

  function selectChunk(chunk: GenerationAssetChunk) {
    setActiveChunkId(chunk.id);
    setChunkTitle(chunk.title);
    setChunkContent(chunk.content);
    setChunkKeywords(chunk.keywords.join(", "));
    setChunkSectionTags(chunk.section_tags.join(", "));
    setChunkWeight(String(chunk.weight));
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!projectName.trim()) {
      setErrorMsg("请输入项目名称。");
      return;
    }
    setIsCreating(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const payload = {
        template_name: templateName,
        project_summary: projectSummary.trim(),
        tender_requirements: tenderRequirements.trim(),
        delivery_deadline: deliveryDeadline.trim(),
        service_commitment: serviceCommitment.trim(),
        selected_asset_titles: selectedAssets,
        section_titles: normalizeOutline(customOutline),
      };
      const job = projectId
        ? await runProjectGeneration(projectId, payload)
        : await createGenerationJob({
            project_name: projectName.trim(),
            client_name: clientName.trim(),
            project_id: prefillProjectId || undefined,
            ...payload,
          });
      await onGenerationUpdated();
      await syncLatestJob(job);
      setSuccessMsg(`已生成回标初稿：${job.project_name}（${job.section_count} 个章节）`);
      setProjectName("");
      setClientName("");
      setProjectSummary("");
      setTenderRequirements("");
      setDeliveryDeadline("");
      setServiceCommitment("");
      setCustomOutline("");
      setSelectedAssets([]);
      if (!projectId) {
        setPrefillProjectId("");
      }
    } catch {
      setErrorMsg("创建生成任务失败，请确认后端服务已启动并重试。");
    } finally {
      setIsCreating(false);
    }
  }

  async function handleRegenerate(sec: GenerationSectionRecord) {
    if (!currentJob) return;
    setIsRegenerating(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const updated = await regenerateSection(currentJob.id, sec.id);
      const nextSections = sections.map((item) => (item.id === updated.id ? updated : item));
      setSections(nextSections);
      setActiveSectionId(updated.id);
      setDraftContent(updated.content);
      setSuccessMsg(`已重新生成章节：${updated.title}`);
    } catch {
      setErrorMsg("重新生成章节失败。");
    } finally {
      setIsRegenerating(false);
    }
  }

  async function handleSaveSection() {
    if (!currentJob || !activeSection) return;
    setIsSaving(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const updated = await updateGenerationSection(currentJob.id, activeSection.id, {
        content: draftContent,
        status: "已编辑",
      });
      const nextSections = sections.map((item) => (item.id === updated.id ? updated : item));
      setSections(nextSections);
      setActiveSectionId(updated.id);
      setSuccessMsg(`已保存章节：${updated.title}`);
      await syncLatestJob();
    } catch {
      setErrorMsg("保存章节失败。");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleRepairUncovered() {
    if (!currentJob) return;
    setIsRepairing(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      await repairGenerationJobUncovered(currentJob.id);
      await syncLatestJob();
      setSuccessMsg("已按未覆盖评分点自动补写章节。");
    } catch {
      setErrorMsg("补写未覆盖评分点失败。");
    } finally {
      setIsRepairing(false);
    }
  }

  async function handleSelfRevise() {
    if (!currentJob) return;
    setIsSelfRevising(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      await selfReviseGenerationJob(currentJob.id);
      await syncLatestJob();
      setSuccessMsg("已完成生成后二轮自修订。");
    } catch {
      setErrorMsg("二轮自修订失败。");
    } finally {
      setIsSelfRevising(false);
    }
  }

  async function handleExport() {
    if (!currentJob) return;
    setIsExporting(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const report = await exportGenerationJob(currentJob.id);
      const blob = new Blob([report], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${currentJob.project_name}-回标初稿.md`;
      anchor.click();
      URL.revokeObjectURL(url);
      setSuccessMsg("已导出 Markdown 回标初稿。");
    } catch {
      setErrorMsg("导出失败。");
    } finally {
      setIsExporting(false);
    }
  }

  async function handleExportDocx() {
    if (!currentJob) return;
    setIsExporting(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const blob = templateFile
        ? await exportGenerationJobDocxWithTemplate(currentJob.id, templateFile)
        : await exportGenerationJobDocx(currentJob.id);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${currentJob.project_name}-回标初稿.docx`;
      anchor.click();
      URL.revokeObjectURL(url);
      setSuccessMsg(templateFile ? "已导出 Word 回标初稿（已应用模板）。" : "已导出 Word 回标初稿。");
    } catch {
      setErrorMsg("导出 Word 失败。");
    } finally {
      setIsExporting(false);
    }
  }

  function toggleAsset(title: string) {
    setSelectedAssets((current) =>
      current.includes(title) ? current.filter((item) => item !== title) : [...current, title],
    );
  }

  function togglePreference(title: string, mode: "fixed" | "excluded") {
    if (mode === "fixed") {
      setFixedAssets((current) =>
        current.includes(title) ? current.filter((item) => item !== title) : [...current, title],
      );
      setExcludedAssets((current) => current.filter((item) => item !== title));
      return;
    }
    setExcludedAssets((current) =>
      current.includes(title) ? current.filter((item) => item !== title) : [...current, title],
    );
    setFixedAssets((current) => current.filter((item) => item !== title));
  }

  async function handleSavePreferences() {
    if (!projectId) return;
    setIsSavingPreferences(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const saved = await updateProjectGenerationPreferences(projectId, {
        fixed_asset_titles: fixedAssets,
        excluded_asset_titles: excludedAssets,
      });
      setFixedAssets(saved.fixed_asset_titles);
      setExcludedAssets(saved.excluded_asset_titles);
      const context = await getProjectGenerationContext(projectId);
      setSelectedAssets(context.selected_asset_titles);
      setSuccessMsg("已保存项目级素材引用偏好。");
    } catch {
      setErrorMsg("保存项目级素材偏好失败。");
    } finally {
      setIsSavingPreferences(false);
    }
  }

  async function handleCreateAsset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!assetTitle.trim() || !assetContent.trim()) return;
    setIsCreatingAsset(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const created = await createGenerationAsset({
        title: assetTitle.trim(),
        asset_type: assetType,
        status: "可引用",
        content: assetContent.trim(),
      });
      await loadIndexedAssets();
      setActiveAssetId(created.id);
      setSelectedAssets((current) => (current.includes(created.title) ? current : [...current, created.title]));
      setAssetTitle("");
      setAssetContent("");
      setSuccessMsg(`已新增素材：${created.title}`);
    } catch {
      setErrorMsg("新增素材失败。");
    } finally {
      setIsCreatingAsset(false);
    }
  }

  async function handleUploadAsset(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setIsUploadingAsset(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const created = await uploadGenerationAsset({
        file,
        assetType,
        title: assetUploadTitle.trim() || undefined,
      });
      await loadIndexedAssets();
      setActiveAssetId(created.id);
      setSelectedAssets((current) => (current.includes(created.title) ? current : [...current, created.title]));
      setAssetUploadTitle("");
      setSuccessMsg(`已上传素材：${created.title}`);
    } catch {
      setErrorMsg("上传素材失败。");
    } finally {
      setIsUploadingAsset(false);
      event.target.value = "";
    }
  }

  async function handleRefreshAssets() {
    setIsRefreshingAssets(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      let currentJob = await refreshGenerationAssetIndex(activeAsset?.id);
      setIndexJob(currentJob);
      for (let attempt = 0; attempt < 30; attempt += 1) {
        if (["completed", "failed"].includes(currentJob.status)) {
          break;
        }
        await sleep(1000);
        currentJob = await getGenerationAssetIndexJob(currentJob.id);
        setIndexJob(currentJob);
      }
      await loadIndexedAssets();
      if (currentJob.status === "completed") {
        setSuccessMsg(`索引任务完成，已刷新 ${currentJob.refreshed_count} 条素材。`);
      } else {
        setErrorMsg(currentJob.error_message || "素材索引刷新失败。");
      }
    } catch {
      setErrorMsg("刷新素材索引失败。");
    } finally {
      setIsRefreshingAssets(false);
    }
  }

  async function handleSaveAsset() {
    if (!activeAsset) return;
    if (!assetTitle.trim() || !assetContent.trim()) {
      setErrorMsg("素材标题和摘要不能为空。");
      return;
    }
    setIsSavingAsset(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const updated = await updateGenerationAsset(activeAsset.id, {
        title: assetTitle.trim(),
        asset_type: assetType,
        status: activeAsset.status,
        content: assetContent.trim(),
        owner: assetOwner.trim() || "frontend",
        visibility: assetVisibility,
      });
      await loadIndexedAssets();
      setActiveAssetId(updated.id);
      setSuccessMsg(`已更新素材：${updated.title}`);
    } catch {
      setErrorMsg("更新素材失败。");
    } finally {
      setIsSavingAsset(false);
    }
  }

  async function handleDeleteAsset() {
    if (!activeAsset) return;
    setConfirmModal({
      isOpen: true,
      title: "删除素材",
      message: `确认删除素材“${activeAsset.title}”？`,
      onConfirm: async () => {
        setIsDeletingAsset(true);
        setErrorMsg("");
        setSuccessMsg("");
        try {
          await deleteGenerationAsset(activeAsset.id);
          setSelectedAssets((current) => current.filter((item) => item !== activeAsset.title));
          setFixedAssets((current) => current.filter((item) => item !== activeAsset.title));
          setExcludedAssets((current) => current.filter((item) => item !== activeAsset.title));
          await loadIndexedAssets();
          resetChunkEditor();
          setSuccessMsg(`已删除素材：${activeAsset.title}`);
        } catch {
          setErrorMsg("删除素材失败。");
        } finally {
          setIsDeletingAsset(false);
        }
      },
    });
  }

  async function handleReviewAsset(action: "approve" | "reject") {
    if (!activeAsset) return;
    if (!reviewerName.trim()) {
      setErrorMsg("请输入审核人。");
      return;
    }
    setIsReviewingAsset(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const updated = await reviewGenerationAsset(activeAsset.id, {
        action,
        reviewer: reviewerName.trim(),
        review_note: reviewNote.trim(),
      });
      await loadIndexedAssets();
      setActiveAssetId(updated.id);
      setSuccessMsg(
        action === "approve" ? `已审核通过素材：${updated.title}` : `已驳回素材：${updated.title}`,
      );
    } catch {
      setErrorMsg("提交素材审核失败。");
    } finally {
      setIsReviewingAsset(false);
    }
  }

  async function handleSaveChunk() {
    if (!activeAsset) return;
    if (!chunkTitle.trim() || !chunkContent.trim()) {
      setErrorMsg("片段标题和内容不能为空。");
      return;
    }
    setIsSavingChunk(true);
    setErrorMsg("");
    setSuccessMsg("");
    try {
      const payload = {
        title: chunkTitle.trim(),
        content: chunkContent.trim(),
        keywords: normalizeTags(chunkKeywords),
        section_tags: normalizeTags(chunkSectionTags),
        weight: Number(chunkWeight) || 1,
      };
      const chunk = activeChunkId
        ? await updateGenerationAssetChunk(activeAsset.id, activeChunkId, payload)
        : await createGenerationAssetChunk(activeAsset.id, payload);
      await loadAssetChunks(activeAsset.id);
      selectChunk(chunk);
      await loadIndexedAssets();
      setSuccessMsg(activeChunkId ? `已更新片段：${chunk.title}` : `已新增片段：${chunk.title}`);
    } catch {
      setErrorMsg("保存素材片段失败。");
    } finally {
      setIsSavingChunk(false);
    }
  }

  async function handleDeleteChunk(chunkId: string) {
    if (!activeAsset) return;
    setConfirmModal({
      isOpen: true,
      title: "删除片段",
      message: "确认删除这个素材片段？",
      onConfirm: async () => {
        setIsDeletingChunk(true);
        setErrorMsg("");
        setSuccessMsg("");
        try {
          await deleteGenerationAssetChunk(activeAsset.id, chunkId);
          await loadAssetChunks(activeAsset.id);
          await loadIndexedAssets();
          if (activeChunkId === chunkId) {
            resetChunkEditor();
          }
          setSuccessMsg("已删除素材片段。");
        } catch {
          setErrorMsg("删除素材片段失败。");
        } finally {
          setIsDeletingChunk(false);
        }
      },
    });
  }

  const isRealProject = !!projectId;
  const displaySections: Array<{
    id: string;
    title: string;
    status: string;
    citations?: string[] | number;
    todo?: string[] | number;
    coverageScore: number;
  }> =
    sections.length > 0
      ? sections.map((s) => ({
          id: s.id,
          title: s.title,
          status: s.status,
          citations: s.citations,
          todo: s.todos,
          coverageScore: s.coverage_score ?? 0,
        }))
      : [];

  return (
    <div className="workspace-page">
      <PageHeader
        eyebrow="Bid Response Drafting"
        title="回标编写"
        description="基于项目摘要、招标要求、交付约束和可选素材动态生成回标章节，并支持章节编辑、再生成和双格式导出。"
        actions={
          <>
            <button
              className="primary-button"
              type="button"
              onClick={handleExport}
              disabled={!currentJob || isExporting}
            >
              {isExporting ? "导出中..." : "导出 Markdown"}
            </button>
            <button
              className="ghost-button"
              type="button"
              onClick={handleExportDocx}
              disabled={!currentJob || isExporting}
            >
              导出 Word
            </button>
          </>
        }
      />

      <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: -12 }}>
        <span style={{ fontSize: "13px", color: "rgba(139, 200, 255, 0.72)", letterSpacing: "0.06em" }}>当前项目</span>
        <Select
          className="workspace-select"
          value={selectedProjectId || ""}
          onChange={(val) => setSelectedProjectId(val)}
          options={
            data.projectRows.length === 0
              ? [{ label: "暂无项目", value: "" }]
              : data.projectRows.map((p) => ({ label: p.name, value: p.id || "" }))
          }
        />
      </div>

      <Modal
        isOpen={confirmModal.isOpen}
        title={confirmModal.title}
        onClose={() => setConfirmModal({ ...confirmModal, isOpen: false })}
        footer={
          <>
            <button className="ghost-button" onClick={() => setConfirmModal({ ...confirmModal, isOpen: false })}>取消</button>
            <button className="danger-button" onClick={() => {
              confirmModal.onConfirm();
              setConfirmModal({ ...confirmModal, isOpen: false });
            }}>确认</button>
          </>
        }
      >
        <p style={{ padding: "1rem 0" }}>{confirmModal.message}</p>
      </Modal>

      {/* ===== 编辑模式：有 currentJob 时显示三栏布局 ===== */}
      {currentJob ? (
        <div className="generation-layout" style={{ display: "grid", gridTemplateColumns: "20% 1fr 20%", gap: 20 }}>

          {/* ---- 左侧：工作上下文栏 ---- */}
          <aside className="workspace-card" style={{ padding: "1rem", overflowY: "auto", maxHeight: "calc(100vh - 220px)" }}>
            <div className="section-card-head" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '8px' }}>
              <h3 style={{ fontSize: "1.1rem", lineHeight: "1.4", wordBreak: "break-all" }}>{currentJob.project_name}</h3>
            </div>
            <div className="review-job-meta" style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              <span className="status-tag">{currentJob.template_name}</span>
              <span className="status-tag">章节数：{currentJob.section_count}</span>
              <span className="status-tag">{currentJob.overall_progress}</span>
            </div>

            {generationAnalysis ? (
              <>
                <div style={{ marginTop: 16 }}>
                  <h4 style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 8 }}>覆盖进度</h4>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{
                      width: 56, height: 56, borderRadius: "50%",
                      background: `conic-gradient(
                        ${generationAnalysis.overall_coverage_score >= 80 ? "#22c55e" : generationAnalysis.overall_coverage_score >= 50 ? "#eab308" : "#ef4444"} ${generationAnalysis.overall_coverage_score}%,
                        #e5e7eb ${generationAnalysis.overall_coverage_score}%
                      )`,
                      display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.75rem", fontWeight: 700, color: "#374151"
                    }}>
                      {generationAnalysis.overall_coverage_score}%
                    </div>
                    <div>
                      <p style={{ fontSize: "0.75rem" }}>已覆盖 {generationAnalysis.covered_score_item_count} / {generationAnalysis.mapped_score_item_count}</p>
                      <p style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>未覆盖 {generationAnalysis.uncovered_score_item_count} 项</p>
                    </div>
                  </div>
                </div>
              </>
            ) : null}

            {/* 引用素材列表 */}
            {sections.some(s => s.routed_assets?.length) ? (
              <div style={{ marginTop: 16 }}>
                <h4 style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 8 }}>已引用素材</h4>
                <div className="asset-chunk-list">
                  {sections.flatMap(s => (s.routed_assets ?? []).map((asset, i) => (
                    <div key={`${s.id}-${i}`} className="section-item" style={{ fontSize: "0.75rem" }}>
                      <span>{asset}</span>
                      <em style={{ fontSize: "0.65rem" }}>→ {s.title}</em>
                    </div>
                  )))}
                </div>
              </div>
            ) : null}

            {/* 待业务确认 */}
            {false ? (
              <div style={{ marginTop: 16 }}>
                <h4 style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 8 }}>待业务确认</h4>
                <ul className="reason-list" style={{ fontSize: "0.75rem" }}>
                  {[].map((item, i) => (
                    <li key={i}>{item}</li>
                  ))}
                </ul>
              </div>
            ) : null}
          </aside>

          {/* ---- 中间：Tab 编辑区 ---- */}
          <main>
            {/* Tab 切换 */}
            <div className="workspace-card" style={{ padding: "0.75rem 1rem", marginBottom: 16, display: "flex", gap: 8 }}>
              <button
                className="ghost-button"
                style={activeTab === "section" ? { background: "var(--primary, #3b82f6)", color: "#fff" } : {}}
                onClick={() => setActiveTab("section")}
              >
                章节编辑
              </button>
              <button
                className="ghost-button"
                style={activeTab === "score" ? { background: "var(--primary, #3b82f6)", color: "#fff" } : {}}
                onClick={() => setActiveTab("score")}
              >
                评分点详情
              </button>
              <button
                className="ghost-button"
                style={activeTab === "evidence" ? { background: "var(--primary, #3b82f6)", color: "#fff" } : {}}
                onClick={() => setActiveTab("evidence")}
              >
                证据素材
              </button>
            </div>

            {/* Tab1: 章节编辑 */}
            {activeTab === "section" && (
              <div style={{ display: "grid", gridTemplateColumns: "160px 1fr", gap: 16 }}>
                <article className="workspace-card" style={{ padding: "1rem" }}>
                  <h3 style={{ fontSize: "0.9rem", marginBottom: 12 }}>回标结构</h3>
                  <div className="field-list">
                    {displaySections.map((s) => (
                      <div
                        key={s.id}
                        className={`field-item ${activeSectionId === s.id ? "asset-record-card-active" : ""}`}
                        style={{ cursor: "pointer", padding: "0.5rem", borderRadius: 8 }}
                        onClick={() => setActiveSectionId(s.id)}
                      >
                        <strong style={{ fontSize: "0.8rem" }}>{s.title}</strong>
                        <div style={{ display: "flex", gap: 4, marginTop: 4 }}>
                          <span className="status-tag" style={{ fontSize: "0.65rem" }}>{s.status}</span>
                          <span className="status-tag" style={{ fontSize: "0.65rem", background: s.coverageScore >= 80 ? "#22c55e" : s.coverageScore >= 50 ? "#eab308" : "#ef4444", color: "#fff" }}>
                            {s.coverageScore}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </article>

                <article className="workspace-card" style={{ padding: "1rem" }}>
                  <div className="section-card-head">
                    <div>
                      <p className="eyebrow">编辑章节</p>
                      <h3>{activeSection?.title ?? "请选择章节"}</h3>
                    </div>
                  </div>
                  <div className="editor-surface">
                    {activeSection ? (
                      <>
                        <div className="editor-block">
                          <span className="editor-label">AI 生成内容</span>
                          <textarea
                            value={draftContent}
                            onChange={(e) => setDraftContent(e.target.value)}
                            rows={20}
                            style={{ width: "100%", fontSize: "0.9rem", lineHeight: "1.6", padding: "10px", resize: "vertical" }}
                          />
                        </div>
                        <div className="editor-block">
                          <span className="editor-label">状态信息</span>
                          <p style={{ fontSize: "0.8rem" }}>
                            状态：{activeSection.status} · 引用 {activeSection.citations} 条 · 待确认 {activeSection.todos} 项 · 覆盖率 {activeSection.coverage_score ?? 0}%
                          </p>
                          {activeSection.matched_score_items?.length ? (
                            <p style={{ fontSize: "0.75rem" }}>已覆盖评分点：{activeSection.matched_score_items.join(" / ")}</p>
                          ) : null}
                          {activeSection.missing_requirements?.length ? (
                            <p style={{ fontSize: "0.75rem", color: "#ef4444" }}>待补评分点：{activeSection.missing_requirements.join(" / ")}</p>
                          ) : null}
                          {activeSection.routed_assets?.length ? (
                            <p style={{ fontSize: "0.75rem" }}>命中素材：{activeSection.routed_assets.join(" / ")}</p>
                          ) : null}
                        </div>
                        <div className="review-action-row" style={{ display: "flex", gap: 12, marginTop: 12 }}>
                          <button className="primary-button" type="button" onClick={handleSaveSection} disabled={isSaving}>
                            {isSaving ? "保存中..." : "保存当前章节"}
                          </button>
                          <button className="ghost-button" type="button" onClick={() => handleRegenerate(activeSection)} disabled={isRegenerating}>
                            {isRegenerating ? "重新生成中..." : "重新生成本章节"}
                          </button>
                        </div>
                      </>
                    ) : (
                      <div className="editor-block">
                        <span className="editor-label">生成逻辑</span>
                        <p style={{ fontSize: "0.85rem" }}>
                          先输入项目摘要、招标要求、交付约束和素材范围，再由系统按章节组织初稿内容。生成后可逐章编辑、重生和导出。
                        </p>
                      </div>
                    )}
                  </div>
                </article>
              </div>
            )}

            {/* Tab2: 评分点详情 */}
            {activeTab === "score" && generationAnalysis && (
              <div className="workspace-card" style={{ padding: "1rem" }}>
                <div className="section-card-head">
                  <div>
                    <p className="eyebrow">Score Mapping</p>
                    <h3>评分点映射详情</h3>
                  </div>
                  <span className="status-tag">总体覆盖率 {generationAnalysis.overall_coverage_score}%</span>
                </div>
                <div className="asset-management-grid" style={{ marginTop: 16 }}>
                  <div className="pending-box">
                    <h4>已覆盖评分点</h4>
                    <div className="asset-chunk-list">
                      {generationAnalysis.score_items.filter(i => i.coverage_status === "已覆盖").map((item) => (
                        <div key={item.id} className="section-item">
                          <div>
                            <strong>{item.title}</strong>
                            <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                              来源：{item.source} · 章节：{item.mapped_sections.join(" / ")}
                            </span>
                          </div>
                          <em style={{ color: "#22c55e" }}>{item.coverage_status}</em>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="pending-box">
                    <h4>未覆盖评分点</h4>
                    <div className="asset-chunk-list">
                      {generationAnalysis.score_items.filter(i => i.coverage_status === "未覆盖").length > 0 ? (
                        generationAnalysis.score_items.filter(i => i.coverage_status === "未覆盖").map((item) => (
                          <div key={item.id} className="section-item">
                            <div>
                              <strong>{item.title}</strong>
                              <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                                来源：{item.source} · 目标章节：{item.mapped_sections.join(" / ")}
                              </span>
                            </div>
                            <em style={{ color: "#ef4444" }}>{item.coverage_status}</em>
                          </div>
                        ))
                      ) : (
                        <p className="muted-caption">所有评分点均已覆盖 🎉</p>
                      )}
                    </div>
                  </div>
                </div>
                <div style={{ marginTop: 16 }}>
                  <h4>生成后自检</h4>
                  <div className="asset-chunk-list">
                    {generationAnalysis.checks.length > 0 ? (
                      generationAnalysis.checks.map((item) => (
                        <div key={item.id} className="field-item">
                          <div className="field-head">
                            <span>{item.category}</span>
                            <strong>{item.level}</strong>
                          </div>
                          <p style={{ fontSize: "0.85rem" }}>{item.title}</p>
                          <small>{item.detail}</small>
                        </div>
                      ))
                    ) : (
                      <p className="muted-caption">当前未发现明显缺口，建议继续人工复核关键商务条款与评分明细。</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Tab3: 证据素材 */}
            {activeTab === "evidence" && (
              <div className="workspace-card" style={{ padding: "1rem" }}>
                <div className="section-card-head">
                  <div>
                    <p className="eyebrow">Evidence Assets</p>
                    <h3>证据素材库</h3>
                  </div>
                  <span className="muted-caption">可直接纳入回标内容的素材清单</span>
                </div>
                <div className="asset-list" style={{ marginTop: 16 }}>
                  {(indexedAssets.length > 0 ? indexedAssets : []).map((asset) => (
                    <div key={asset.title} className="asset-item">
                      <div className="rule-head">
                        <strong>{asset.title}</strong>
                        <span className="status-tag">{asset.status}</span>
                      </div>
                      <span>{(asset as any).asset_type || (asset as any).type || "通用"}</span>
                      <p style={{ fontSize: "0.8rem" }}>相关度 {asset.score}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </main>

          {/* ---- 右侧：评分点工具栏 ---- */}
          <aside className="workspace-card" style={{ padding: "1rem", overflowY: "auto", maxHeight: "calc(100vh - 220px)" }}>
            <div className="section-card-head">
              <p className="eyebrow">Tools</p>
              <h3>评分点工具</h3>
            </div>

            {generationAnalysis ? (
              <div style={{ marginTop: 16 }}>
                <h4 style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 8 }}>覆盖统计</h4>
                <div style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: "0.8rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>已覆盖</span>
                    <span style={{ color: "#22c55e" }}>{generationAnalysis.covered_score_item_count} 项</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>未覆盖</span>
                    <span style={{ color: "#ef4444" }}>{generationAnalysis.uncovered_score_item_count} 项</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span>总分项</span>
                    <span>{generationAnalysis.mapped_score_item_count} 项</span>
                  </div>
                  <div style={{ height: 8, borderRadius: 4, background: "#e5e7eb", overflow: "hidden", marginTop: 4 }}>
                    <div style={{
                      height: "100%", width: `${generationAnalysis.overall_coverage_score}%`,
                      background: generationAnalysis.overall_coverage_score >= 80 ? "#22c55e" : generationAnalysis.overall_coverage_score >= 50 ? "#eab308" : "#ef4444",
                      transition: "width 0.3s"
                    }} />
                  </div>
                </div>
              </div>
            ) : null}

            <div style={{ marginTop: 20, display: "flex", flexDirection: "column", gap: 10 }}>
              <button
                className="primary-button"
                type="button"
                onClick={handleRepairUncovered}
                disabled={!currentJob || isRepairing}
              >
                {isRepairing ? "补写中..." : "一键补写未覆盖评分点"}
              </button>
              <button
                className="ghost-button"
                type="button"
                onClick={handleSelfRevise}
                disabled={!currentJob || isSelfRevising}
              >
                {isSelfRevising ? "自修订中..." : "生成后二轮自修订"}
              </button>
            </div>

            <div style={{ marginTop: 20, borderTop: "1px solid #e5e7eb", paddingTop: 16 }}>
              <h4 style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 8 }}>导出</h4>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <button className="primary-button" type="button" onClick={handleExport} disabled={!currentJob || isExporting}>
                  {isExporting ? "导出中..." : "导出 Markdown"}
                </button>
                <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                  <button className="ghost-button" type="button" onClick={handleExportDocx} disabled={!currentJob || isExporting} style={{ flex: 1 }}>
                    {isExporting ? "导出中..." : "导出 Word"}
                  </button>
                  <label className="ghost-button" style={{ cursor: "pointer", fontSize: "0.75rem", padding: "6px 10px", whiteSpace: "nowrap" }}>
                    {templateFile ? templateFile.name : "上传模板"}
                    <input
                      type="file"
                      accept=".docx"
                      style={{ display: "none" }}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => {
                        setTemplateFile(e.target.files?.[0] ?? null);
                      }}
                    />
                  </label>
                </div>
                {templateFile && (
                  <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 6 }}>
                    <span>📄 {templateFile.name}</span>
                    <button
                      type="button"
                      onClick={() => setTemplateFile(null)}
                      style={{ background: "none", border: "none", color: "#f87171", cursor: "pointer", fontSize: "0.75rem", padding: 0 }}
                    >
                      移除
                    </button>
                  </div>
                )}
                <div style={{ marginTop: 6, padding: "8px 10px", background: "rgba(139, 92, 246, 0.08)", borderRadius: 6, border: "1px solid rgba(139,92,246,0.2)" }}>
                  <p style={{ margin: "0 0 4px", fontSize: "0.7rem", color: "#c4b5fd", fontWeight: 600 }}>📋 模板占位符说明</p>
                  <p style={{ margin: 0, fontSize: "0.65rem", color: "#a78bfa", lineHeight: 1.6 }}>
                    在 Word 模板中使用 <code style={{ background: "rgba(139,92,246,0.15)", padding: "1px 4px", borderRadius: 3 }}>{`{{章节标题}}`}</code> 作为占位符<br/>
                    系统会自动替换为对应的 AI 生成内容<br/>
                    示例：<code style={{ background: "rgba(139,92,246,0.15)", padding: "1px 4px", borderRadius: 3 }}>{`{{项目理解与建设目标}}`}</code> → 替换为该章节内容<br/>
                    支持：<code style={{ background: "rgba(139,92,246,0.15)", padding: "1px 4px", borderRadius: 3 }}>{`{{项目名称}}`}</code>{" "}
                    <code style={{ background: "rgba(139,92,246,0.15)", padding: "1px 4px", borderRadius: 3 }}>{`{{模板}}`}</code>{" "}
                    <code style={{ background: "rgba(139,92,246,0.15)", padding: "1px 4px", borderRadius: 3 }}>{`{{生成时间}}`}</code>{" "}
                    等元数据占位符
                  </p>
                </div>
              </div>
            </div>

            {/* 素材库快捷入口 */}
            <div style={{ marginTop: 20, borderTop: "1px solid #e5e7eb", paddingTop: 16 }}>
              <h4 style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 8 }}>素材管理</h4>
              <button 
                className="ghost-button" 
                type="button" 
                onClick={() => setIsAssetManagerOpen(true)} 
                style={{ width: "100%", marginBottom: 8, background: "rgba(119, 180, 255, 0.1)", color: "#dce9ff", border: "1px solid rgba(119, 180, 255, 0.2)" }}
              >
                打开素材库管理
              </button>
              {projectId ? (
                <button className="ghost-button" type="button" onClick={handleSavePreferences} disabled={isSavingPreferences} style={{ width: "100%" }}>
                  {isSavingPreferences ? "保存中..." : "保存素材偏好"}
                </button>
              ) : null}
            </div>
          </aside>
        </div>
      ) : (
        /* ===== 向导模式：无 currentJob 时 ===== */
        <div>
          {!isWizardOpen ? (
            <div className="workspace-card" style={{ padding: "2rem", textAlign: "center" }}>
              <h3 style={{ marginBottom: 12 }}>暂无回标任务</h3>
              <p className="muted-caption" style={{ marginBottom: 20 }}>点击下方按钮，填写项目信息创建新的回标初稿</p>
              <button className="primary-button" type="button" onClick={() => setIsWizardOpen(true)}>
                + 创建新回标
              </button>
            </div>
          ) : (
            <div className="workspace-card" style={{ padding: "1.5rem" }}>
              <div className="section-card-head" style={{ marginBottom: 20 }}>
                <div>
                  <p className="eyebrow">Create Draft</p>
                  <h3>创建回标初稿</h3>
                </div>
                <button className="ghost-button" type="button" onClick={() => setIsWizardOpen(false)}>
                  收起
                </button>
              </div>
              <form className="project-form-grid" onSubmit={handleCreate}>
                <label className="form-field">
                  <span>项目名称</span>
                  <input required value={projectName} onChange={(e) => setProjectName(e.target.value)} disabled={Boolean(projectId)} placeholder="例如：智慧园区安防平台建设项目" />
                </label>
                <label className="form-field">
                  <span>客户名称</span>
                  <input value={clientName} onChange={(e) => setClientName(e.target.value)} disabled={Boolean(projectId)} placeholder="例如：海岚科技" />
                </label>
                <label className="form-field">
                  <span>回标模板</span>
                  <Select value={templateName} onChange={(val) => setTemplateName(val)} options={[{ value: "标准回标模板", label: "标准回标模板" }]} />
                </label>
                <label className="form-field">
                  <span>交付时限</span>
                  <input value={deliveryDeadline} onChange={(e) => setDeliveryDeadline(e.target.value)} placeholder="例如：合同签订后 90 日内" />
                </label>
                <label className="form-field form-field-full">
                  <span>项目摘要</span>
                  <textarea value={projectSummary} onChange={(e) => setProjectSummary(e.target.value)} rows={3} placeholder="概括项目背景、建设范围、场景目标和关键价值。" />
                </label>
                <label className="form-field form-field-full">
                  <span>招标要求</span>
                  <textarea value={tenderRequirements} onChange={(e) => setTenderRequirements(e.target.value)} rows={4} placeholder="逐条录入资格、评分点、技术参数、接口要求、交付约束等。支持换行。" />
                </label>
                <label className="form-field form-field-full">
                  <span>服务承诺</span>
                  <textarea value={serviceCommitment} onChange={(e) => setServiceCommitment(e.target.value)} rows={3} placeholder="录入 SLA、质保、巡检、驻场、培训等承诺范围。" />
                </label>
                <label className="form-field form-field-full">
                  <span>自定义章节大纲</span>
                  <textarea value={customOutline} onChange={(e) => setCustomOutline(e.target.value)} rows={2} placeholder="留空则使用标准模板；如需自定义可逐行填写章节名。" />
                </label>
                <div className="form-field form-field-full">
                  <span>选择引用素材</span>
                  <div className="filter-chips">
                    {(indexedAssets.length ? indexedAssets.map((asset) => ({ title: asset.title, score: asset.score, status: asset.status })) : []).map((asset) => (
                      <button key={asset.title} className={`chip ${selectedAssets.includes(asset.title) ? "chip-active" : ""}`} type="button" onClick={() => toggleAsset(asset.title)}>
                        {asset.title}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="form-submit-row">
                  <p className="muted-caption">
                    {projectId ? "当前已绑定项目上下文，提交后会按项目、要求提取和素材默认值直接生成。" : "提交后系统会根据输入动态组织章节内容，并关联素材和待确认事项。"}
                  </p>
                  <button className="primary-button" type="submit" disabled={isCreating}>
                    {isCreating ? "生成中..." : projectId ? "按项目生成回标初稿" : "生成回标初稿"}
                  </button>
                </div>
                {errorMsg ? <p className="form-error">{errorMsg}</p> : null}
                {successMsg ? <p className="form-success">{successMsg}</p> : null}
              </form>
            </div>
          )}
        </div>
      )}

      {/* 素材管理弹窗 */}
      <Modal
        isOpen={isAssetManagerOpen}
        title="素材库管理"
        maxWidth="1000px"
        onClose={() => setIsAssetManagerOpen(false)}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="section-card-head" style={{ marginBottom: 0, paddingBottom: 0, borderBottom: 'none' }}>
            <div className="review-job-meta">
              <button className="ghost-button" type="button" onClick={handleRefreshAssets} disabled={isRefreshingAssets}>
                {isRefreshingAssets ? "刷新中..." : "刷新素材索引"}
              </button>
              {indexJob ? (
                <>
                  <span className="status-tag">索引任务：{indexJob.status}</span>
                  <span className="status-tag">刷新数量：{indexJob.refreshed_count}</span>
                </>
              ) : null}
            </div>
          </div>
          
          <div className="project-form-grid" style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <form className="form-field form-field-full" onSubmit={handleCreateAsset} style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <input value={assetTitle} onChange={(e) => setAssetTitle(e.target.value)} placeholder="素材标题" />
                  <Select value={assetType} onChange={(val) => setAssetType(val)} options={[{ value: "通用素材", label: "通用素材" }, { value: "解决方案", label: "解决方案" }, { value: "案例库", label: "案例库" }, { value: "资质", label: "资质" }, { value: "服务模板", label: "服务模板" }]} />
                </div>
                <div style={{ flex: 2 }}>
                  <textarea value={assetContent} onChange={(e) => setAssetContent(e.target.value)} rows={3} placeholder="粘贴案例、资质说明、方案摘要或服务条款内容。" style={{ height: '100%' }} />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', minWidth: '120px' }}>
                  <button className="primary-button" type="submit" disabled={isCreatingAsset}>{isCreatingAsset ? "新增中..." : "新增文本素材"}</button>
                  <label className="ghost-button" style={{ display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", margin: 0 }}>
                    {isUploadingAsset ? "上传中..." : "上传文件素材"}
                    <input type="file" accept=".txt,.docx,.pdf" onChange={handleUploadAsset} hidden />
                  </label>
                </div>
              </div>
            </form>
            
            <div className="asset-management-grid form-field-full" style={{ display: 'grid', gridTemplateColumns: '1fr 2.5fr', gap: '16px' }}>
              <div className="field-list" style={{ overflowY: 'auto', maxHeight: '500px' }}>
                {indexedAssets.map((asset) => (
                  <div key={asset.id} className={`field-item asset-record-card ${activeAsset?.id === asset.id ? "asset-record-card-active" : ""}`} style={{ cursor: "pointer" }} onClick={() => setActiveAssetId(asset.id)}>
                    <div className="rule-head">
                      <strong>{asset.title}</strong>
                      <span className="status-tag">{asset.status}</span>
                    </div>
                    <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{(asset as any).asset_type || "通用"}</span>
                  </div>
                ))}
              </div>
              
              {activeAsset ? (
                <div className="asset-detail-panel" style={{ overflowY: 'auto', paddingRight: '8px', maxHeight: '500px' }}>
                  <h4 style={{ fontSize: "0.9rem", marginBottom: 12 }}>素材详情</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                    <label className="form-field"><span>标题</span><input value={assetTitle} onChange={(e) => setAssetTitle(e.target.value)} /></label>
                    <label className="form-field"><span>类型</span><Select value={assetType} onChange={(val) => setAssetType(val)} options={[{ value: "通用素材", label: "通用素材" }, { value: "解决方案", label: "解决方案" }, { value: "案例库", label: "案例库" }, { value: "资质", label: "资质" }, { value: "服务模板", label: "服务模板" }]} /></label>
                  </div>
                  <label className="form-field" style={{ marginTop: '12px' }}><span>摘要</span><textarea value={assetContent} onChange={(e) => setAssetContent(e.target.value)} rows={4} /></label>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '12px', marginTop: '12px' }}>
                    <label className="form-field"><span>审核人</span><input value={reviewerName} onChange={(e) => setReviewerName(e.target.value)} /></label>
                    <label className="form-field"><span>审核意见</span><input value={reviewNote} onChange={(e) => setReviewNote(e.target.value)} /></label>
                  </div>
                  
                  <div className="review-action-row" style={{ display: "flex", gap: 8, marginTop: 12, paddingBottom: 16, borderBottom: "1px solid rgba(129, 186, 255, 0.12)" }}>
                    <button className="primary-button" type="button" onClick={handleSaveAsset} disabled={isSavingAsset}>{isSavingAsset ? "保存中..." : "保存修改"}</button>
                    <button className="ghost-button" type="button" onClick={() => handleReviewAsset("approve")} disabled={isReviewingAsset}>审核通过</button>
                    <button className="ghost-button" type="button" onClick={() => handleReviewAsset("reject")} disabled={isReviewingAsset}>驳回</button>
                    <button className="ghost-button" type="button" onClick={handleDeleteAsset} disabled={isDeletingAsset} style={{ color: "#ef4444", marginLeft: 'auto' }}>删除素材</button>
                  </div>
                  
                  <div style={{ marginTop: 16 }}>
                    <h4 style={{ fontSize: "0.85rem", marginBottom: 12 }}>关联片段管理</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '300px', overflowY: 'auto' }}>
                        {assetChunks.map((chunk) => (
                          <div key={chunk.id} className={`section-item ${activeChunkId === chunk.id ? "asset-record-card-active" : ""}`} style={{ cursor: "pointer", padding: "8px 12px", background: 'rgba(255,255,255,0.03)', borderRadius: '6px' }} onClick={() => selectChunk(chunk)}>
                            <strong style={{ fontSize: "0.8rem", display: 'block', marginBottom: '4px' }}>{chunk.title}</strong>
                            <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                              <span>🔑 {chunk.keywords.join(", ")}</span>
                              <span>📑 {chunk.section_tags.join(", ")}</span>
                            </div>
                          </div>
                        ))}
                        {assetChunks.length === 0 && <p className="muted-caption">暂无片段</p>}
                        <button className="ghost-button" style={{ marginTop: '8px' }} onClick={() => { setActiveChunkId(""); setChunkTitle(""); setChunkContent(""); setChunkKeywords(""); setChunkSectionTags(""); }}>+ 新增片段</button>
                      </div>
                      
                      <div style={{ background: 'rgba(10,24,43,0.4)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(129, 186, 255, 0.1)' }}>
                        <label className="form-field"><span>片段标题</span><input value={chunkTitle} onChange={(e) => setChunkTitle(e.target.value)} /></label>
                        <label className="form-field" style={{ marginTop: '12px' }}><span>内容</span><textarea value={chunkContent} onChange={(e) => setChunkContent(e.target.value)} rows={4} /></label>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '12px' }}>
                          <label className="form-field"><span>关键词 (逗号分隔)</span><input value={chunkKeywords} onChange={(e) => setChunkKeywords(e.target.value)} /></label>
                          <label className="form-field"><span>归属章节 (逗号分隔)</span><input value={chunkSectionTags} onChange={(e) => setChunkSectionTags(e.target.value)} /></label>
                        </div>
                        <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
                          <button className="primary-button" type="button" onClick={handleSaveChunk} disabled={isSavingChunk} style={{ flex: 1 }}>{isSavingChunk ? "保存中..." : activeChunkId ? "更新片段" : "新增片段"}</button>
                          {activeChunkId ? <button className="ghost-button" type="button" onClick={() => handleDeleteChunk(activeChunkId)} disabled={isDeletingChunk} style={{ color: "#ef4444" }}>删除</button> : null}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="asset-detail-panel" style={{ display: "flex", alignItems: "center", justifyContent: "center", background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
                  <p className="muted-caption">👈 请在左侧选择一个素材以查看或编辑详情</p>
                </div>
              )}
            </div>
          </div>
          {successMsg ? <p className="form-success" style={{ margin: 0 }}>{successMsg}</p> : null}
          {errorMsg ? <p className="form-error" style={{ margin: 0 }}>{errorMsg}</p> : null}
        </div>
      </Modal>
    </div>
  );

}
