import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { PageHeader } from "../components/PageHeader";
import { Modal } from "../components/Modal";
import { Select } from "../components/Select";
import { createProject, updateProject } from "../services/workspace";
import type { ProjectCreateInput, WorkspaceData } from "../types";

type ProjectsPageProps = {
  data: WorkspaceData;
  onProjectCreated: () => Promise<void>;
};

const initialForm: ProjectCreateInput = {
  name: "",
  owner: "",
  client: "",
  deadline: "",
  amount: "",
  risk: "P2",
  status: "待决策",
};

export function ProjectsPage({ data, onProjectCreated }: ProjectsPageProps) {
  const navigate = useNavigate();
  const [isCreating, setIsCreating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [form, setForm] = useState<ProjectCreateInput>(initialForm);
  const [confirmModal, setConfirmModal] = useState<{ isOpen: boolean; projectId: string | null }>({
    isOpen: false,
    projectId: null,
  });
  const [alertModal, setAlertModal] = useState<{ isOpen: boolean; message: string }>({
    isOpen: false,
    message: "",
  });

  const projectCountLabel = `${data.projectRows.length} 个项目已纳入台账`;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setIsSubmitting(true);

    try {
      await createProject(form);
      await onProjectCreated();
      setForm(initialForm);
      setIsCreating(false);
    } catch {
      setErrorMessage("项目创建失败，请确认后端服务已启动并重试。");
    } finally {
      setIsSubmitting(false);
    }
  }

  function confirmCloseProject(projectId: string) {
    setConfirmModal({ isOpen: true, projectId });
  }

  async function handleCloseProject() {
    const { projectId } = confirmModal;
    if (!projectId) return;

    setConfirmModal({ isOpen: false, projectId: null });
    try {
      await updateProject(projectId, { status: "已关闭" });
      await onProjectCreated(); // Re-fetch the workspace data
    } catch {
      setAlertModal({ isOpen: true, message: "关闭商机失败，请重试。" });
    }
  }

  return (
    <div className="workspace-page">
      <PageHeader
        eyebrow="Opportunity Ledger"
        title="商机台账"
        description={`统一查看哪些项目值得进入“合同审查”和“回标编写”流程。当前 ${projectCountLabel}。`}
        actions={
          <>
            <button className="primary-button" type="button" onClick={() => setIsCreating(true)}>
              新建项目
            </button>
            <button className="ghost-button" type="button">
              导出排期
            </button>
          </>
        }
      />

      <section className="mini-metric-grid mini-metric-horizontal">
        {data.projectStats.map((item) => (
          <article key={item.label} className={`mini-metric mini-metric-${item.tone}`}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
            {item.hint ? <p>{item.hint}</p> : null}
          </article>
        ))}
      </section>

      <section className="workspace-card">
        <div className="toolbar-row">
          <div className="filter-chips">
            {data.projectFilters.map((item, index) => (
              <button key={item} className={`chip ${index === 0 ? "chip-active" : ""}`} type="button">
                {item}
              </button>
            ))}
          </div>
          <div className="search-box">搜索项目名称 / 招标人 / 项目编号</div>
        </div>

        <div className="data-table">
          <div className="table-row table-head-row">
            <span>项目名称</span>
            <span>负责人</span>
            <span>客户</span>
            <span>截止时间</span>
            <span>预算</span>
            <span>状态</span>
            <span>风险</span>
          </div>
          {data.projectRows.map((row) => (
            <div key={row.name} className="table-row">
              <div className="table-title-cell">
                <strong>{row.name}</strong>
                <span>已纳入双场景演示流程，可继续推进审查或回标编写</span>
                {row.id ? (
                  <div className="action-btn-group">
                    <button
                      className="action-btn"
                      type="button"
                      onClick={() => navigate(`/parsing?projectId=${row.id}`)}
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                      </svg>
                      提取
                    </button>
                    <button
                      className="action-btn"
                      type="button"
                      onClick={() => navigate(`/decision?projectId=${row.id}`)}
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12" y2="12"></line>
                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                      </svg>
                      策略
                    </button>
                    <button
                      className="action-btn"
                      type="button"
                      onClick={() => navigate(`/generation?projectId=${row.id}`)}
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                        <polyline points="2 17 12 22 22 17"></polyline>
                        <polyline points="2 12 12 17 22 12"></polyline>
                      </svg>
                      回标
                    </button>
                    {row.status !== "已关闭" && (
                      <button
                        className="action-btn action-btn-danger"
                        type="button"
                        onClick={() => row.id && confirmCloseProject(row.id)}
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <circle cx="12" cy="12" r="10"></circle>
                          <line x1="15" y1="9" x2="9" y2="15"></line>
                          <line x1="9" y1="9" x2="15" y2="15"></line>
                        </svg>
                        关闭
                      </button>
                    )}
                  </div>
                ) : null}
              </div>
              <span>{row.owner}</span>
              <span>{row.client}</span>
              <span>{row.deadline}</span>
              <span>{row.amount}</span>
              <span className="status-tag">{row.status}</span>
              <span className={`risk-pill risk-${row.risk.toLowerCase()}`}>{row.risk}</span>
            </div>
          ))}
        </div>
      </section>

      <Modal
        isOpen={isCreating}
        title="新建项目"
        maxWidth="560px"
        onClose={() => {
          setIsCreating(false);
          setForm(initialForm);
          setErrorMessage("");
        }}
        footer={
          <>
            <button
              className="ghost-button"
              type="button"
              onClick={() => {
                setIsCreating(false);
                setForm(initialForm);
                setErrorMessage("");
              }}
            >
              取消
            </button>
            <button className="primary-button" type="submit" form="project-form" disabled={isSubmitting}>
              {isSubmitting ? "创建中..." : "创建项目"}
            </button>
          </>
        }
      >
        <form id="project-form" className="project-form-grid" onSubmit={handleSubmit}>
          <label className="form-field">
            <span>项目名称</span>
            <input
              required
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              placeholder="例如：智慧园区安防平台建设项目"
            />
          </label>
          <label className="form-field">
            <span>项目负责人</span>
            <input
              required
              value={form.owner}
              onChange={(event) => setForm({ ...form, owner: event.target.value })}
              placeholder="例如：张敏"
            />
          </label>
          <label className="form-field">
            <span>客户 / 招标人</span>
            <input
              value={form.client}
              onChange={(event) => setForm({ ...form, client: event.target.value })}
              placeholder="例如：海岚科技"
            />
          </label>
          <label className="form-field">
            <span>投标截止时间</span>
            <input
              value={form.deadline}
              onChange={(event) => setForm({ ...form, deadline: event.target.value })}
              placeholder="例如：03-24 18:00"
            />
          </label>
          <label className="form-field">
            <span>预算金额</span>
            <input
              value={form.amount}
              onChange={(event) => setForm({ ...form, amount: event.target.value })}
              placeholder="例如：¥ 420 万"
            />
          </label>
          <label className="form-field">
            <span>风险等级</span>
            <Select 
              value={form.risk} 
              onChange={(val) => setForm({ ...form, risk: val })}
              options={[
                { value: "P0", label: "P0 - 战略级必须拿下" },
                { value: "P1", label: "P1 - 核心利润项目" },
                { value: "P2", label: "P2 - 常规跟进" },
                { value: "P3", label: "P3 - 凑数/顺带跟进" },
              ]}
            />
          </label>
          {errorMessage ? <p className="form-error" style={{ gridColumn: '1 / -1' }}>{errorMessage}</p> : null}
          <p className="muted-caption" style={{ gridColumn: '1 / -1', fontSize: '12px' }}>
            当前先保存基础字段，后续继续接招标文件上传、合同审查和回标编写入口。
          </p>
        </form>
      </Modal>

      <Modal
        isOpen={confirmModal.isOpen}
        title="确认关闭"
        onClose={() => setConfirmModal({ isOpen: false, projectId: null })}
        footer={
          <>
            <button className="ghost-button" onClick={() => setConfirmModal({ isOpen: false, projectId: null })}>
              取消
            </button>
            <button className="primary-button" onClick={handleCloseProject}>
              确定
            </button>
          </>
        }
      >
        <p>确定要关闭该商机吗？</p>
      </Modal>

      <Modal
        isOpen={alertModal.isOpen}
        title="提示"
        onClose={() => setAlertModal({ isOpen: false, message: "" })}
        footer={
          <button className="primary-button" onClick={() => setAlertModal({ isOpen: false, message: "" })}>
            确定
          </button>
        }
      >
        <p>{alertModal.message}</p>
      </Modal>
    </div>
  );
}
