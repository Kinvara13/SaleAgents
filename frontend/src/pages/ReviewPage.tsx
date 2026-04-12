import { useEffect, useState, type ChangeEvent, type FormEvent } from "react";

import { PageHeader } from "../components/PageHeader";
import { Select } from "../components/Select";
import {
  exportReviewJobReport,
  exportReviewJobReportDocx,
  getLatestReviewJob,
  getReviewJobClauses,
  getReviewJobIssues,
  rerunReviewJob,
  resolveReviewIssue,
  submitReviewFeedback,
  uploadReviewContract,
} from "../services/workspace";
import type { ReviewClause, ReviewIssue, ReviewJob, WorkspaceData } from "../types";

type ReviewPageProps = {
  data: WorkspaceData;
  onReviewUpdated: () => Promise<void>;
};

const STATUS_FILTERS = [
  { key: "all", label: "全部问题" },
  { key: "pending", label: "待处理" },
  { key: "resolved", label: "已处理" },
] as const;

const LEVEL_FILTERS = [
  { key: "all", label: "全部等级" },
  { key: "high", label: "仅高风险" },
  { key: "P0", label: "P0" },
  { key: "P1", label: "P1" },
  { key: "P2", label: "P2" },
  { key: "P3", label: "P3" },
] as const;

type StatusFilterKey = (typeof STATUS_FILTERS)[number]["key"];
type LevelFilterKey = (typeof LEVEL_FILTERS)[number]["key"];

function issueKey(issue: ReviewIssue): string {
  return issue.id ?? issue.title;
}

export function ReviewPage({ data, onReviewUpdated }: ReviewPageProps) {
  const [selectedIssueKey, setSelectedIssueKey] = useState(data.reviewIssues[0] ? issueKey(data.reviewIssues[0]) : "");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [contractName, setContractName] = useState("");
  const [contractType, setContractType] = useState("采购合同");
  const [isUploading, setIsUploading] = useState(false);
  const [isRunningAction, setIsRunningAction] = useState(false);
  const [statusFilter, setStatusFilter] = useState<StatusFilterKey>("all");
  const [levelFilter, setLevelFilter] = useState<LevelFilterKey>("all");
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");
  const [currentJob, setCurrentJob] = useState<ReviewJob | null>(null);
  const [jobIssues, setJobIssues] = useState<ReviewIssue[]>([]);
  const [reviewClauses, setReviewClauses] = useState<ReviewClause[]>([]);
  const [feedbackType, setFeedbackType] = useState("confirmed");
  const [feedbackNote, setFeedbackNote] = useState("");
  const [isSubmittingFeedback, setIsSubmittingFeedback] = useState(false);

  const sourceIssues = jobIssues.length > 0 ? jobIssues : data.reviewIssues;
  const currentSummary = currentJob?.summary?.length ? currentJob.summary : data.reviewSummary;
  const currentActions = currentJob?.review_actions?.length ? currentJob.review_actions : data.reviewActions;
  const filteredIssues = sourceIssues.filter((issue) => {
    if (statusFilter === "pending" && issue.status === "已处理") {
      return false;
    }
    if (statusFilter === "resolved" && issue.status !== "已处理") {
      return false;
    }
    if (levelFilter === "high" && !["P0", "P1"].includes(issue.level)) {
      return false;
    }
    if (["P0", "P1", "P2", "P3"].includes(levelFilter) && issue.level !== levelFilter) {
      return false;
    }
    return true;
  });

  useEffect(() => {
    if (!filteredIssues.some((item) => issueKey(item) === selectedIssueKey)) {
      setSelectedIssueKey(filteredIssues[0] ? issueKey(filteredIssues[0]) : "");
    }
  }, [filteredIssues, selectedIssueKey]);

  useEffect(() => {
    void syncLatestReviewJob();
  }, []);

  const selectedIssue =
    filteredIssues.find((item) => issueKey(item) === selectedIssueKey) ?? filteredIssues[0] ?? null;

  async function syncLatestReviewJob(jobOverride?: ReviewJob | null) {
    const latestJob = jobOverride ?? (await getLatestReviewJob());
    if (!latestJob) {
      setCurrentJob(null);
      setJobIssues([]);
      setReviewClauses([]);
      return;
    }

    const [issues, clauses] = await Promise.all([
      getReviewJobIssues(latestJob.id),
      getReviewJobClauses(latestJob.id),
    ]);
    setCurrentJob(latestJob);
    setJobIssues(issues);
    setReviewClauses(clauses);
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) {
      setUploadError("请先选择合同文件。");
      setUploadSuccess("");
      return;
    }

    setIsUploading(true);
    setUploadError("");
    setUploadSuccess("");

    try {
      const job = await uploadReviewContract({
        file: selectedFile,
        contractName: contractName.trim() || selectedFile.name,
        contractType,
      });
      await onReviewUpdated();
      await syncLatestReviewJob(job);
      setUploadSuccess(`已完成审查：${job.contract_name}。`);
      setSelectedFile(null);
      setContractName("");
    } catch {
      setUploadError("合同上传或审查失败，请确认后端服务已启动并重试。");
    } finally {
      setIsUploading(false);
    }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const nextFile = event.target.files?.[0] ?? null;
    setSelectedFile(nextFile);
    setUploadError("");
    if (nextFile && !contractName) {
      setContractName(nextFile.name.replace(/\.[^.]+$/, ""));
    }
  }

  async function handleRerun() {
    if (!currentJob) {
      return;
    }
    setIsRunningAction(true);
    setUploadError("");
    setUploadSuccess("");

    try {
      const job = await rerunReviewJob(currentJob.id);
      await onReviewUpdated();
      await syncLatestReviewJob(job);
      setUploadSuccess(`已重新运行审查：${job.contract_name}。`);
    } catch {
      setUploadError("重新运行审查失败，请稍后重试。");
    } finally {
      setIsRunningAction(false);
    }
  }

  async function handleResolveSelectedIssue() {
    if (!selectedIssue?.id) {
      setUploadError("当前问题缺少 issue id，暂时无法回写处理状态。");
      return;
    }
    setIsRunningAction(true);
    setUploadError("");
    setUploadSuccess("");

    try {
      await resolveReviewIssue(selectedIssue.id, "已在工作台中标记为已处理。");
      await onReviewUpdated();
      await syncLatestReviewJob(currentJob);
      setUploadSuccess(`已标记问题为已处理：${selectedIssue.title}`);
    } catch {
      setUploadError("回写处理状态失败，请稍后重试。");
    } finally {
      setIsRunningAction(false);
    }
  }

  async function handleExportReport() {
    if (!currentJob) {
      setUploadError("当前没有可导出的审查任务。");
      return;
    }
    setIsRunningAction(true);
    setUploadError("");
    setUploadSuccess("");

    try {
      const report = await exportReviewJobReport(currentJob.id);
      const blob = new Blob([report], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${currentJob.contract_name}-review-report.md`;
      anchor.click();
      URL.revokeObjectURL(url);
      setUploadSuccess(`已导出审查报告：${currentJob.contract_name}`);
    } catch {
      setUploadError("导出审查报告失败，请稍后重试。");
    } finally {
      setIsRunningAction(false);
    }
  }

  async function handleExportDocx() {
    if (!currentJob) {
      setUploadError("当前没有可导出的审查任务。");
      return;
    }
    setIsRunningAction(true);
    setUploadError("");
    setUploadSuccess("");

    try {
      const blob = await exportReviewJobReportDocx(currentJob.id);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${currentJob.contract_name}-review-report.docx`;
      anchor.click();
      URL.revokeObjectURL(url);
      setUploadSuccess(`已导出 Word 报告：${currentJob.contract_name}`);
    } catch {
      setUploadError("导出 Word 报告失败，请稍后重试。");
    } finally {
      setIsRunningAction(false);
    }
  }

  async function handleSubmitFeedback(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedIssue?.id) {
      setUploadError("当前问题缺少 issue id，暂时无法提交反馈。");
      return;
    }

    setIsSubmittingFeedback(true);
    setUploadError("");
    setUploadSuccess("");

    try {
      await submitReviewFeedback(
        selectedIssue.id,
        feedbackType,
        feedbackNote.trim(),
        "法务工作台",
      );
      await onReviewUpdated();
      setFeedbackNote("");
      setUploadSuccess(`已记录反馈：${selectedIssue.title}`);
    } catch {
      setUploadError("提交法务反馈失败，请稍后重试。");
    } finally {
      setIsSubmittingFeedback(false);
    }
  }

  return (
    <div className="workspace-page">
      <PageHeader
        eyebrow="Contract Review Robot"
        title="合同审查机器人"
        description="自动识别付款、违约、交付边界与责任分配中的高风险条款，并给出解释、建议和可回流的法务反馈。"
        actions={
          <>
            <button
              className="primary-button"
              type="button"
              onClick={handleRerun}
              disabled={!currentJob || isRunningAction}
            >
              {isRunningAction ? "处理中..." : "重新运行审查"}
            </button>
            <button className="ghost-button" type="button">
              当前任务：{currentJob?.contract_name ?? "暂无"}
            </button>
            <button className="ghost-button" type="button" onClick={handleExportReport} disabled={!currentJob}>
              导出 Markdown
            </button>
            <button className="ghost-button" type="button" onClick={handleExportDocx} disabled={!currentJob}>
              导出 Word
            </button>
          </>
        }
      />

      {currentJob ? (
        <section className="workspace-card review-job-card">
          <div className="section-card-head">
            <div>
              <p className="eyebrow">Latest Review Job</p>
              <h3>{currentJob.contract_name}</h3>
            </div>
            <span className={`risk-pill risk-${currentJob.overall_risk.toLowerCase()}`}>
              {currentJob.overall_risk}
            </span>
          </div>
          <div className="review-job-meta">
            <span className="status-tag">{currentJob.contract_type}</span>
            <span className="status-tag">触发方式：{currentJob.trigger}</span>
            <span className="status-tag">问题数：{currentJob.issue_count}</span>
            <span className="status-tag">高风险：{currentJob.high_risk_issue_count}</span>
            <span className="status-tag">完成时间：{new Date(currentJob.updated_at).toLocaleString("zh-CN")}</span>
          </div>
        </section>
      ) : null}

      <section className="workspace-card review-upload-card">
        <div className="section-card-head">
          <div>
            <p className="eyebrow">Upload Contract</p>
            <h3>上传合同并触发真实审查</h3>
          </div>
          <span className="muted-caption">支持 txt / docx / pdf</span>
        </div>

        <form className="project-form-grid" onSubmit={handleUpload}>
          <label className="form-field">
            <span>合同名称</span>
            <input
              value={contractName}
              onChange={(event) => setContractName(event.target.value)}
              placeholder="例如：智慧园区采购合同"
            />
          </label>
          <label className="form-field">
            <span>合同类型</span>
            <Select 
              value={contractType} 
              onChange={(val) => setContractType(val)}
              options={[
                { value: "采购合同", label: "采购合同" },
                { value: "销售合同", label: "销售合同" },
                { value: "服务合同", label: "服务合同" },
                { value: "框架协议", label: "框架协议" },
              ]}
            />
          </label>
          <label className="form-field form-field-full">
            <span>合同文件</span>
            <input type="file" accept=".txt,.docx,.pdf" onChange={handleFileChange} />
          </label>
          <div className="form-submit-row">
            <p className="muted-caption">
              {selectedFile
                ? `当前已选择：${selectedFile.name}`
                : currentJob
                  ? `最近任务：${currentJob.contract_name} · 风险 ${currentJob.overall_risk}`
                  : "上传后会自动抽取文本、切分条款并运行合同审查。"}
            </p>
            <button className="primary-button" type="submit" disabled={isUploading}>
              {isUploading ? "审查中..." : "上传并审查"}
            </button>
          </div>
          {uploadError ? <p className="form-error">{uploadError}</p> : null}
          {uploadSuccess ? <p className="form-success">{uploadSuccess}</p> : null}
        </form>
      </section>

      <section className="mini-metric-grid">
        {currentSummary.map((item) => (
          <article key={item.label} className={`mini-metric mini-metric-${item.tone ?? "blue"}`}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            {item.hint ? <p>{item.hint}</p> : null}
          </article>
        ))}
      </section>

      <section className="review-layout">
        <article className="workspace-card">
          <div className="section-card-head">
            <h3>风险条款列表</h3>
            <span className="muted-caption">按严重等级排序，可筛选查看详情</span>
          </div>
          <div className="review-filter-row">
            <div className="filter-chips">
              {STATUS_FILTERS.map((item) => (
                <button
                  key={item.key}
                  className={`chip ${statusFilter === item.key ? "chip-active" : ""}`}
                  type="button"
                  onClick={() => setStatusFilter(item.key)}
                >
                  {item.label}
                </button>
              ))}
            </div>
            <div className="filter-chips">
              {LEVEL_FILTERS.map((item) => (
                <button
                  key={item.key}
                  className={`chip ${levelFilter === item.key ? "chip-active" : ""}`}
                  type="button"
                  onClick={() => setLevelFilter(item.key)}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          <div className="issue-list">
            {filteredIssues.length > 0 ? (
              filteredIssues.map((issue) => (
                <button
                  key={issueKey(issue)}
                  className={`issue-item issue-item-button ${issueKey(selectedIssue ?? issue) === issueKey(issue) ? "issue-item-active" : ""}`}
                  type="button"
                  onClick={() => setSelectedIssueKey(issueKey(issue))}
                >
                  <div className="rule-head">
                    <strong>{issue.title}</strong>
                    <span className={`risk-pill risk-${issue.level.toLowerCase()}`}>{issue.level}</span>
                  </div>
                  <span className="status-tag">{issue.status}</span>
                  <p>{issue.detail}</p>
                  <small>
                    {issue.origin ?? issue.type} · {issue.document}
                  </small>
                </button>
              ))
            ) : (
              <article className="issue-empty-state">
                <strong>当前筛选条件下没有问题</strong>
                <p>可以切回全部问题，或者重新上传合同后查看新的命中结果。</p>
              </article>
            )}
          </div>
        </article>

        <article className="workspace-card review-detail-card">
          <div className="section-card-head">
            <h3>条款解释与建议</h3>
            <span className="muted-caption">
              {selectedIssue ? `当前选中：${selectedIssue.title}` : "当前暂无待分析条款"}
            </span>
          </div>
          {selectedIssue ? (
            <div className="editor-surface">
              <div className="editor-block">
                <span className="editor-label">审查来源</span>
                <p>
                  {selectedIssue.origin ?? "规则命中"} · {selectedIssue.document}
                </p>
              </div>
              <div className="editor-block">
                <span className="editor-label">命中条款 / 证据</span>
                <p>{selectedIssue.evidence ?? "当前问题尚未补充原文证据。"}</p>
              </div>
              <div className="editor-block">
                <span className="editor-label">AI 风险解释</span>
                <p>{selectedIssue.detail}</p>
              </div>
              <div className="editor-block">
                <span className="editor-label">修订建议</span>
                <p>{selectedIssue.suggestion ?? "建议法务进一步确认责任边界并给出修订版本。"}</p>
              </div>
              {selectedIssue.rule_name ? (
                <div className="editor-block">
                  <span className="editor-label">命中规则</span>
                  <p>{selectedIssue.rule_name}</p>
                </div>
              ) : null}
              {selectedIssue.resolution_note ? (
                <div className="editor-block">
                  <span className="editor-label">处理备注</span>
                  <p>{selectedIssue.resolution_note}</p>
                </div>
              ) : null}
            </div>
          ) : (
            <div className="pending-box">
              <p className="muted-caption">请选择左侧问题，查看条款解释、建议和反馈入口。</p>
            </div>
          )}
          <div className="pending-box">
            <h4>建议动作</h4>
            <ul className="reason-list">
              {currentActions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <div className="review-action-row">
              <button
                className="primary-button"
                type="button"
                onClick={handleResolveSelectedIssue}
                disabled={!selectedIssue?.id || isRunningAction}
              >
                标记当前问题已处理
              </button>
            </div>
          </div>

          <form className="pending-box feedback-form" onSubmit={handleSubmitFeedback}>
            <h4>法务反馈回流</h4>
            <p className="muted-caption">把误报、确认命中或修改建议回写到规则学习闭环。</p>
            <label className="form-field">
              <span>反馈结论</span>
              <Select 
                value={feedbackType} 
                onChange={(val) => setFeedbackType(val)}
                options={[
                  { value: "confirmed", label: "确认命中" },
                  { value: "dismissed", label: "误报 / 不采纳" },
                  { value: "modified", label: "建议修改规则或文案" },
                ]}
              />
            </label>
            <label className="form-field">
              <span>反馈备注</span>
              <textarea
                value={feedbackNote}
                onChange={(event) => setFeedbackNote(event.target.value)}
                placeholder="例如：该条款属于我方标准接受范围，建议降低等级或缩小匹配范围。"
                rows={4}
              />
            </label>
            <div className="review-action-row">
              <button
                className="ghost-button"
                type="submit"
                disabled={!selectedIssue?.id || isSubmittingFeedback}
              >
                {isSubmittingFeedback ? "提交中..." : "提交法务反馈"}
              </button>
            </div>
          </form>
        </article>
      </section>

      {reviewClauses.length > 0 ? (
        <section className="workspace-card">
          <div className="section-card-head">
            <h3>最新上传条款切分</h3>
            <span className="muted-caption">上传后即时返回的结构化条款</span>
          </div>
          <div className="clause-list">
            {reviewClauses.map((clause) => (
              <article key={clause.id} className="clause-item">
                <div className="rule-head">
                  <strong>
                    {clause.title} · #{clause.clause_no}
                  </strong>
                  <span className="status-tag">{clause.source_ref}</span>
                </div>
                <p>{clause.content}</p>
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  );
}
