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
  getGenerationAssetChunks,
  getGenerationAssetIndexJob,
  getGenerationJobAnalysis,
  getGenerationJobSections,
  getIndexedGenerationAssets,
  getLatestGenerationJob,
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
  const [searchParams] = useSearchParams();
  const projectId = searchParams.get("projectId");
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

  const [isCreating, setIsCreating] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
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
  }, []);

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
    const job = jobOverride ?? (await getLatestGenerationJob());
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
      const blob = await exportGenerationJobDocx(currentJob.id);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${currentJob.project_name}-回标初稿.docx`;
      anchor.click();
      URL.revokeObjectURL(url);
      setSuccessMsg("已导出 Word 回标初稿。");
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
      : isRealProject ? [] : data.generationSections.map((item) => ({ ...item, id: item.title, coverageScore: 0 }));

  return (
    <div className="workspace-page">
      <PageHeader
        eyebrow="Bid Response Drafting"
        title="回标文件自动编写"
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
            <button className="ghost-button" type="button" disabled>
              当前任务：{currentJob?.project_name ?? "暂无"}
            </button>
          </>
        }
      />

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

      {currentJob ? (
        <section className="workspace-card review-job-card">
          <div className="section-card-head">
            <div>
              <p className="eyebrow">Latest Draft Job</p>
              <h3>{currentJob.project_name}</h3>
            </div>
            <span className="status-tag">{currentJob.overall_progress}</span>
          </div>
          <div className="review-job-meta">
            <span className="status-tag">{currentJob.template_name}</span>
            <span className="status-tag">章节数：{currentJob.section_count}</span>
            <span className="status-tag">状态：{currentJob.status}</span>
            <span className="status-tag">更新时间：{new Date(currentJob.updated_at).toLocaleString("zh-CN")}</span>
          </div>
        </section>
      ) : null}

      {generationAnalysis ? (
        <section className="workspace-card review-upload-card">
          <div className="section-card-head">
            <div>
              <p className="eyebrow">Score Mapping & Self Check</p>
              <h3>评分点映射与生成后自检</h3>
            </div>
            <span className="status-tag">总体覆盖率 {generationAnalysis.overall_coverage_score}%</span>
          </div>
          <div className="review-job-meta">
            <span className="status-tag">评分项 {generationAnalysis.mapped_score_item_count}</span>
            <span className="status-tag">已覆盖 {generationAnalysis.covered_score_item_count}</span>
            <span className="status-tag">未覆盖 {generationAnalysis.uncovered_score_item_count}</span>
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
          <div className="asset-management-grid" style={{ marginTop: 20 }}>
            <div className="pending-box">
              <h4>评分点映射</h4>
              <div className="asset-chunk-list">
                {generationAnalysis.score_items.slice(0, 8).map((item) => (
                  <div key={item.id} className="section-item">
                    <div>
                      <strong>{item.title}</strong>
                      <span>
                        来源：{item.source} · 目标章节：{item.mapped_sections.join(" / ")}
                      </span>
                    </div>
                    <em>{item.coverage_status}</em>
                  </div>
                ))}
              </div>
            </div>
            <div className="pending-box">
              <h4>生成后自检</h4>
              <div className="asset-chunk-list">
                {generationAnalysis.checks.length ? (
                  generationAnalysis.checks.map((item) => (
                    <div key={item.id} className="field-item">
                      <div className="field-head">
                        <span>{item.category}</span>
                        <strong>{item.level}</strong>
                      </div>
                      <p>{item.title}</p>
                      <small>{item.detail}</small>
                    </div>
                  ))
                ) : (
                  <p className="muted-caption">当前未发现明显缺口，建议继续人工复核关键商务条款与评分明细。</p>
                )}
              </div>
            </div>
          </div>
        </section>
      ) : null}

      <section className="workspace-card review-upload-card">
        <div className="section-card-head">
          <div>
            <p className="eyebrow">Create Draft</p>
            <h3>创建回标初稿</h3>
          </div>
          <span className="muted-caption">把项目摘要、招标要求和素材选择一起喂给生成链路</span>
        </div>
        <form className="project-form-grid" onSubmit={handleCreate}>
          <label className="form-field">
            <span>项目名称</span>
            <input
              required
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              disabled={Boolean(projectId)}
              placeholder="例如：智慧园区安防平台建设项目"
            />
          </label>
          <label className="form-field">
            <span>客户名称</span>
            <input
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              disabled={Boolean(projectId)}
              placeholder="例如：海岚科技"
            />
          </label>
          <label className="form-field">
            <span>回标模板</span>
            <Select 
              value={templateName} 
              onChange={(val) => setTemplateName(val)}
              options={[
                { value: "标准回标模板", label: "标准回标模板" },
              ]}
            />
          </label>
          <label className="form-field">
            <span>交付时限</span>
            <input
              value={deliveryDeadline}
              onChange={(e) => setDeliveryDeadline(e.target.value)}
              placeholder="例如：合同签订后 90 日内"
            />
          </label>
          <label className="form-field form-field-full">
            <span>项目摘要</span>
            <textarea
              value={projectSummary}
              onChange={(e) => setProjectSummary(e.target.value)}
              rows={4}
              placeholder="概括项目背景、建设范围、场景目标和关键价值。"
            />
          </label>
          <label className="form-field form-field-full">
            <span>招标要求</span>
            <textarea
              value={tenderRequirements}
              onChange={(e) => setTenderRequirements(e.target.value)}
              rows={5}
              placeholder="逐条录入资格、评分点、技术参数、接口要求、交付约束等。支持换行。"
            />
          </label>
          <label className="form-field form-field-full">
            <span>服务承诺</span>
            <textarea
              value={serviceCommitment}
              onChange={(e) => setServiceCommitment(e.target.value)}
              rows={4}
              placeholder="录入 SLA、质保、巡检、驻场、培训等承诺范围。"
            />
          </label>
          <label className="form-field form-field-full">
            <span>自定义章节大纲</span>
            <textarea
              value={customOutline}
              onChange={(e) => setCustomOutline(e.target.value)}
              rows={3}
              placeholder="留空则使用标准模板；如需自定义可逐行填写章节名。"
            />
          </label>
          <div className="form-field form-field-full">
            <span>选择引用素材</span>
            <div className="filter-chips">
              {(indexedAssets.length
                ? indexedAssets.map((asset) => ({
                    title: asset.title,
                    score: asset.score,
                    status: asset.status,
                  }))
                : data.generationAssets
              ).map((asset) => (
                <button
                  key={asset.title}
                  className={`chip ${selectedAssets.includes(asset.title) ? "chip-active" : ""}`}
                  type="button"
                  onClick={() => toggleAsset(asset.title)}
                >
                  {asset.title}
                </button>
              ))}
            </div>
          </div>
          <div className="form-submit-row">
            <p className="muted-caption">
              {currentJob
                ? `最近任务：${currentJob.project_name} · ${currentJob.section_count} 个章节`
                : projectId
                  ? "当前已绑定项目上下文，提交后会按项目、要求提取和素材默认值直接生成。"
                  : "提交后系统会根据输入动态组织章节内容，并关联素材和待确认事项。"}
            </p>
            <button className="primary-button" type="submit" disabled={isCreating}>
              {isCreating ? "生成中..." : projectId ? "按项目生成回标初稿" : "生成回标初稿"}
            </button>
          </div>
          {errorMsg ? <p className="form-error">{errorMsg}</p> : null}
          {successMsg ? <p className="form-success">{successMsg}</p> : null}
        </form>
      </section>

      <section className="workspace-card review-upload-card">
        <div className="section-card-head">
          <div>
            <p className="eyebrow">Asset Routing Control</p>
            <h3>素材库与项目级引用控制</h3>
          </div>
          <div className="review-job-meta">
            <button className="ghost-button" type="button" onClick={handleRefreshAssets} disabled={isRefreshingAssets}>
              {isRefreshingAssets ? "刷新中..." : activeAsset ? "刷新当前素材索引" : "刷新素材索引"}
            </button>
            {projectId ? (
              <button className="primary-button" type="button" onClick={handleSavePreferences} disabled={isSavingPreferences}>
                {isSavingPreferences ? "保存中..." : "保存项目素材偏好"}
              </button>
            ) : null}
          </div>
        </div>
        {indexJob ? (
          <div className="review-job-meta">
            <span className="status-tag">索引任务：{indexJob.status}</span>
            <span className="status-tag">触发人：{indexJob.triggered_by}</span>
            <span className="status-tag">刷新数量：{indexJob.refreshed_count}</span>
            {indexJob.completed_at ? (
              <span className="status-tag">
                完成时间：{new Date(indexJob.completed_at).toLocaleString("zh-CN")}
              </span>
            ) : null}
          </div>
        ) : null}
        <div className="project-form-grid">
          <form className="form-field form-field-full" onSubmit={handleCreateAsset}>
            <span>新增文本素材</span>
            <input value={assetTitle} onChange={(event) => setAssetTitle(event.target.value)} placeholder="素材标题" />
            <Select 
              value={assetType} 
              onChange={(val) => setAssetType(val)}
              options={[
                { value: "通用素材", label: "通用素材" },
                { value: "解决方案", label: "解决方案" },
                { value: "案例库", label: "案例库" },
                { value: "资质", label: "资质" },
                { value: "服务模板", label: "服务模板" },
              ]}
            />
            <textarea
              value={assetContent}
              onChange={(event) => setAssetContent(event.target.value)}
              rows={4}
              placeholder="粘贴案例、资质说明、方案摘要或服务条款内容。"
            />
            <div className="review-action-row" style={{ display: "flex", gap: 12 }}>
              <button className="primary-button" type="submit" disabled={isCreatingAsset}>
                {isCreatingAsset ? "新增中..." : "新增素材"}
              </button>
              <input
                value={assetUploadTitle}
                onChange={(event) => setAssetUploadTitle(event.target.value)}
                placeholder="上传素材标题（可选）"
              />
              <label className="ghost-button" style={{ display: "inline-flex", alignItems: "center" }}>
                {isUploadingAsset ? "上传中..." : "上传文件素材"}
                <input type="file" accept=".txt,.docx,.pdf" onChange={handleUploadAsset} hidden />
              </label>
            </div>
          </form>
          <div className="asset-management-grid form-field-full">
            <div className="field-list">
            {indexedAssets.map((asset) => (
              <div
                key={asset.id}
                className={`field-item asset-record-card ${activeAsset?.id === asset.id ? "asset-record-card-active" : ""}`}
              >
                <div className="field-head">
                  <span>{asset.title}</span>
                  <strong>{asset.asset_type}</strong>
                </div>
                <p>{asset.summary}</p>
                <small>
                  标签：{asset.section_tags.join(" / ") || "未标注"} · 来源：{asset.source_kind}
                </small>
                <div className="review-job-meta" style={{ marginTop: 12 }}>
                  <span className="status-tag">审核：{asset.review_status}</span>
                  <span className="status-tag">权限：{asset.visibility}</span>
                  <span className="status-tag">归属：{asset.owner || "system"}</span>
                </div>
                <div className="review-action-row" style={{ display: "flex", gap: 12, marginTop: 12 }}>
                  <button className="ghost-button" type="button" onClick={() => setActiveAssetId(asset.id)}>
                    管理
                  </button>
                  <button
                    className={`chip ${selectedAssets.includes(asset.title) ? "chip-active" : ""}`}
                    type="button"
                    onClick={() => toggleAsset(asset.title)}
                  >
                    常规引用
                  </button>
                  <button
                    className={`chip ${fixedAssets.includes(asset.title) ? "chip-active" : ""}`}
                    type="button"
                    onClick={() => togglePreference(asset.title, "fixed")}
                    disabled={!projectId}
                  >
                    固定引用
                  </button>
                  <button
                    className={`chip ${excludedAssets.includes(asset.title) ? "chip-active" : ""}`}
                    type="button"
                    onClick={() => togglePreference(asset.title, "excluded")}
                    disabled={!projectId}
                  >
                    禁用引用
                  </button>
                </div>
              </div>
            ))}
            </div>

            <div className="workspace-card asset-detail-panel">
              <div className="section-card-head">
                <div>
                  <p className="eyebrow">Asset Detail</p>
                  <h3>{activeAsset?.title ?? "选择素材"}</h3>
                </div>
                {activeAsset ? <span className="status-tag">{activeAsset.review_status}</span> : null}
              </div>
              {activeAsset ? (
                <>
                  <div className="project-form-grid asset-detail-form">
                    <label className="form-field">
                      <span>素材标题</span>
                      <input value={assetTitle} onChange={(event) => setAssetTitle(event.target.value)} />
                    </label>
                    <label className="form-field">
                      <span>素材类型</span>
                      <Select 
                        value={assetType} 
                        onChange={(val) => setAssetType(val)}
                        options={[
                          { value: "通用素材", label: "通用素材" },
                          { value: "解决方案", label: "解决方案" },
                          { value: "案例库", label: "案例库" },
                          { value: "资质", label: "资质" },
                          { value: "服务模板", label: "服务模板" },
                        ]}
                      />
                    </label>
                    <label className="form-field">
                      <span>归属人</span>
                      <input value={assetOwner} onChange={(event) => setAssetOwner(event.target.value)} />
                    </label>
                    <label className="form-field">
                      <span>可见性</span>
                      <Select 
                        value={assetVisibility} 
                        onChange={(val) => setAssetVisibility(val)}
                        options={[
                          { value: "internal", label: "internal" },
                          { value: "project", label: "project" },
                          { value: "private", label: "private" },
                        ]}
                      />
                    </label>
                    <label className="form-field form-field-full">
                      <span>素材摘要 / 编辑内容</span>
                      <textarea
                        value={assetContent}
                        onChange={(event) => setAssetContent(event.target.value)}
                        rows={5}
                      />
                    </label>
                  </div>
                  <div className="review-action-row" style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                    <button className="primary-button" type="button" onClick={handleSaveAsset} disabled={isSavingAsset}>
                      {isSavingAsset ? "保存中..." : "保存素材"}
                    </button>
                    <button className="ghost-button" type="button" onClick={handleDeleteAsset} disabled={isDeletingAsset}>
                      {isDeletingAsset ? "删除中..." : "删除素材"}
                    </button>
                  </div>

                  <div className="pending-box">
                    <h4>审核流</h4>
                    <div className="project-form-grid asset-detail-form">
                      <label className="form-field">
                        <span>审核人</span>
                        <input value={reviewerName} onChange={(event) => setReviewerName(event.target.value)} />
                      </label>
                      <label className="form-field form-field-full">
                        <span>审核意见</span>
                        <textarea
                          value={reviewNote}
                          onChange={(event) => setReviewNote(event.target.value)}
                          rows={3}
                        />
                      </label>
                    </div>
                    <div className="review-action-row" style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                      <button
                        className="primary-button"
                        type="button"
                        onClick={() => handleReviewAsset("approve")}
                        disabled={isReviewingAsset}
                      >
                        {isReviewingAsset ? "提交中..." : "审核通过"}
                      </button>
                      <button
                        className="ghost-button"
                        type="button"
                        onClick={() => handleReviewAsset("reject")}
                        disabled={isReviewingAsset}
                      >
                        驳回素材
                      </button>
                    </div>
                  </div>

                  <div className="pending-box">
                    <div className="section-card-head">
                      <h4>片段级管理</h4>
                      <button className="ghost-button" type="button" onClick={resetChunkEditor}>
                        新建片段
                      </button>
                    </div>
                    <div className="asset-chunk-list">
                      {assetChunks.map((chunk) => (
                        <div
                          key={chunk.id}
                          className={`section-item ${activeChunkId === chunk.id ? "section-item-active" : ""}`}
                          onClick={() => selectChunk(chunk)}
                        >
                          <div>
                            <strong>{chunk.title}</strong>
                            <span>标签：{chunk.section_tags.join(" / ") || "未标注"}</span>
                          </div>
                          <em>权重 {chunk.weight}</em>
                        </div>
                      ))}
                      {!assetChunks.length ? <p className="muted-caption">当前素材还没有可管理片段。</p> : null}
                    </div>
                    <div className="project-form-grid asset-detail-form">
                      <label className="form-field">
                        <span>片段标题</span>
                        <input value={chunkTitle} onChange={(event) => setChunkTitle(event.target.value)} />
                      </label>
                      <label className="form-field">
                        <span>权重</span>
                        <input value={chunkWeight} onChange={(event) => setChunkWeight(event.target.value)} />
                      </label>
                      <label className="form-field form-field-full">
                        <span>片段内容</span>
                        <textarea
                          value={chunkContent}
                          onChange={(event) => setChunkContent(event.target.value)}
                          rows={4}
                        />
                      </label>
                      <label className="form-field">
                        <span>关键词</span>
                        <input
                          value={chunkKeywords}
                          onChange={(event) => setChunkKeywords(event.target.value)}
                          placeholder="逗号分隔"
                        />
                      </label>
                      <label className="form-field">
                        <span>适用章节</span>
                        <input
                          value={chunkSectionTags}
                          onChange={(event) => setChunkSectionTags(event.target.value)}
                          placeholder="逗号分隔"
                        />
                      </label>
                    </div>
                    <div className="review-action-row" style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                      <button className="primary-button" type="button" onClick={handleSaveChunk} disabled={isSavingChunk}>
                        {isSavingChunk ? "保存中..." : activeChunkId ? "更新片段" : "新增片段"}
                      </button>
                      {activeChunkId ? (
                        <button
                          className="ghost-button"
                          type="button"
                          onClick={() => void handleDeleteChunk(activeChunkId)}
                          disabled={isDeletingChunk}
                        >
                          {isDeletingChunk ? "删除中..." : "删除片段"}
                        </button>
                      ) : null}
                    </div>
                  </div>
                </>
              ) : (
                <p className="muted-caption">先从左侧选中一个素材，再做编辑、审核和片段管理。</p>
              )}
            </div>
          </div>
        </div>
      </section>

      <section className="generation-layout">
        <article className="workspace-card">
          <div className="section-card-head">
            <h3>回标结构树</h3>
            <span className="muted-caption">模板：{currentJob?.template_name ?? "标准回标模板"}</span>
          </div>
          <div className="section-list">
            {displaySections.map((section) => {
              const isActive = activeSection?.id === section.id;
              return (
                <div
                  key={section.id}
                  className={`section-item ${isActive ? "section-item-active" : ""}`}
                  style={{ cursor: sections.length > 0 ? "pointer" : "default" }}
                  onClick={() => sections.length > 0 && setActiveSectionId(section.id)}
                >
                  <div>
                    <strong>{section.title}</strong>
                    <span>
                      引用 {section.citations} 条 · 待确认 {section.todo} 项 · 覆盖率 {section.coverageScore ?? 0}%
                    </span>
                  </div>
                  <em>{section.status}</em>
                </div>
              );
            })}
          </div>
        </article>

        <article className="workspace-card generation-editor-card">
          <div className="section-card-head">
            <h3>章节编写区</h3>
            <span className="muted-caption">当前章节：{activeSection?.title ?? "请先创建任务"}</span>
          </div>
          <div className="editor-surface">
            {activeSection ? (
              <>
                <div className="editor-block">
                  <span className="editor-label">AI 生成内容</span>
                  <textarea
                    value={draftContent}
                    onChange={(event) => setDraftContent(event.target.value)}
                    rows={18}
                  />
                </div>
                <div className="editor-block">
                  <span className="editor-label">状态信息</span>
                  <p>
                    状态：{activeSection.status} · 引用 {activeSection.citations} 条 · 待确认{" "}
                    {activeSection.todos} 项 · 覆盖率 {activeSection.coverage_score ?? 0}%
                  </p>
                  {activeSection.matched_score_items?.length ? (
                    <p>已覆盖评分点：{activeSection.matched_score_items.join(" / ")}</p>
                  ) : null}
                  {activeSection.missing_requirements?.length ? (
                    <p>待补评分点：{activeSection.missing_requirements.join(" / ")}</p>
                  ) : null}
                  {activeSection.routed_assets?.length ? (
                    <>
                      <p>命中素材：{activeSection.routed_assets.join(" / ")}</p>
                      {activeSection.routing_reasons?.length ? (
                        <p>命中原因：{activeSection.routing_reasons.join("；")}</p>
                      ) : null}
                    </>
                  ) : null}
                </div>
                <div className="review-action-row" style={{ display: "flex", gap: 12 }}>
                  <button
                    className="primary-button"
                    type="button"
                    onClick={handleSaveSection}
                    disabled={isSaving}
                  >
                    {isSaving ? "保存中..." : "保存当前章节"}
                  </button>
                  <button
                    className="ghost-button"
                    type="button"
                    onClick={() => handleRegenerate(activeSection)}
                    disabled={isRegenerating}
                  >
                    {isRegenerating ? "重新生成中..." : "重新生成本章节"}
                  </button>
                </div>
              </>
            ) : (
              <>
                <div className="editor-block">
                  <span className="editor-label">生成逻辑</span>
                  <p>
                    先输入项目摘要、招标要求、交付约束和素材范围，再由系统按章节组织初稿内容。
                    生成后可逐章编辑、重生和导出，保证既能快速成稿，也保留人工精修空间。
                  </p>
                </div>
                <div className="editor-block">
                  <span className="editor-label">当前建议</span>
                  <p>优先录入评分点、参数要求、交付周期和服务边界，这些信息会直接影响章节质量。</p>
                </div>
              </>
            )}
          </div>
        </article>

        <article className="workspace-card">
          <div className="section-card-head">
            <h3>证据素材库</h3>
            <span className="muted-caption">可直接纳入回标内容的素材清单</span>
          </div>
          <div className="asset-list">
            {(indexedAssets.length > 0 ? indexedAssets : isRealProject ? [] : data.generationAssets).map((asset) => (
              <div key={asset.title} className="asset-item">
                <div className="rule-head">
                  <strong>{asset.title}</strong>
                  <span className="status-tag">{asset.status}</span>
                </div>
                <span>{(asset as any).asset_type || (asset as any).type || '通用'}</span>
                <p>相关度 {asset.score}</p>
              </div>
            ))}
          </div>
          <div className="pending-box">
            <h4>待业务确认</h4>
            <ul className="reason-list">
              {(isRealProject ? [] : data.generationTodos).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </article>
      </section>
    </div>
  );
}
