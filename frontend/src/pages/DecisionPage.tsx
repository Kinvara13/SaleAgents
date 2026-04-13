import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { PageHeader } from "../components/PageHeader";
import { Select } from "../components/Select";
import type { WorkspaceData } from "../types";
import { getLatestDecisionJob, runProjectDecision, updateProject, type ProjectDecisionJob } from "../services/workspace";

type DecisionPageProps = {
  data: WorkspaceData;
};

export function DecisionPage({ data }: DecisionPageProps) {
  const navigate = useNavigate();
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

  const [job, setJob] = useState<ProjectDecisionJob | null>(null);
  const [loading, setLoading] = useState(false);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) {
      setJob(null);
      return;
    }

    let mounted = true;
    setLoading(true);
    setError(null);
    getLatestDecisionJob(projectId)
      .then((res) => {
        if (mounted) setJob(res);
      })
      .catch((err) => {
        if (mounted) {
          setJob(null);
          if (err.message && !err.message.includes("404")) {
            setError(err.message);
          }
        }
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [projectId]);

  const handleRunDecision = async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);
    try {
      const newJob = await runProjectDecision(projectId);
      setJob(newJob);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  async function handleStatusChange(newStatus: string, actionName: string) {
    if (!projectId) return;
    setIsUpdatingStatus(true);
    setError(null);
    try {
      await updateProject(projectId, { status: newStatus });
      
      if (newStatus === "bid_prep") {
        navigate(`/generation?projectId=${projectId}`);
      } else {
        navigate(`/`);
      }
    } catch (err) {
      setError(`${actionName}操作失败，请重试`);
    } finally {
      setIsUpdatingStatus(false);
    }
  }

  const handleGoToGeneration = () => {
    handleStatusChange("bid_prep", "确认应答");
  };

  const aiReasons = job?.ai_reasons || [];
  const scoreCards = job?.score?.dimensions || [];
  const ruleHits = job?.rule_hits || [];
  const pendingChecks = job?.pending_checks || [];
  const totalScore = job?.score?.total || 0;

  const vetoCount = ruleHits.filter((r) => r.level === "P0").length;
  const highRiskCount = ruleHits.filter((r) => r.level === "P1").length;
  const pendingCount = pendingChecks.length;

  const selectedProjectName = data.projectRows.find(p => p.id === projectId)?.name || projectId || "";

  return (
    <div className="workspace-page">
      <PageHeader
        eyebrow="Response Strategy"
        title="应答策略"
        description="沉淀资格门槛、评分点与风险判断，为回标编写和合同审查提供统一推进建议。"
        actions={
          <>
            <button
              className="ghost-button"
              type="button"
              onClick={handleRunDecision}
              disabled={!projectId || loading}
            >
              {loading ? (
                <>
                  <svg className="animate-spin" style={{ marginRight: '8px', height: '16px', width: '16px' }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  大模型评估中...
                </>
              ) : "刷新策略评估"}
            </button>
            <button 
              className="ghost-button action-btn-danger" 
              onClick={() => handleStatusChange("lost", "放弃跟进")}
              disabled={!projectId || isUpdatingStatus}
            >
              {isUpdatingStatus ? "处理中..." : "放弃跟进"}
            </button>
            <button 
              className="primary-button" 
              onClick={handleGoToGeneration} 
              disabled={!projectId || isUpdatingStatus}
            >
              {isUpdatingStatus ? (
                <>
                  <svg className="animate-spin" style={{ marginRight: '8px', height: '16px', width: '16px' }} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  流转至回标编写
                </>
              ) : "确认应答并生成提纲"}
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

      {error && (
        <div style={{ padding: "12px", background: "rgba(220, 38, 38, 0.15)", color: "#fca5a5", marginBottom: "24px", borderRadius: "14px", border: "1px solid rgba(220, 38, 38, 0.3)" }}>
          获取策略失败：{error}
        </div>
      )}

      {!projectId ? (
        <div className="workspace-card" style={{ textAlign: "center", padding: "48px 24px" }}>
          <h3>请选择项目</h3>
          <p className="muted-caption" style={{ marginBottom: "24px" }}>在上方项目选择器中选择一个项目，查看其应答策略。</p>
        </div>
      ) : (!job && !loading) ? (
        <div className="workspace-card" style={{ textAlign: "center", padding: "48px 24px" }}>
          <h3>尚未生成应答策略</h3>
          <p className="muted-caption" style={{ marginBottom: "24px" }}>当前项目「{selectedProjectName}」还未进行提取字段评估和智能策略生成。</p>
          <button className="primary-button" onClick={handleRunDecision}>
            立即生成策略
          </button>
        </div>
      ) : (
        <>
          <section className="decision-top-grid">
            <article className="workspace-card recommendation-card">
              <span className="metric-label">Response Signal</span>
              <h3>建议继续应答</h3>
              <p>综合评分 {totalScore} / 100，建议先补齐兼容性证明并同步处理付款条款风险，再进入正式回标。</p>
              <div className="recommendation-meta">
                <span>命中一票否决：{vetoCount}</span>
                <span>高风险事项：{highRiskCount}</span>
                <span>待确认：{pendingCount}</span>
              </div>
            </article>

            <article className="workspace-card ai-summary-card">
              <span className="metric-label">AI Explainability</span>
              <h3>推进摘要</h3>
              <ul className="reason-list">
                {aiReasons.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </article>
          </section>

          <section className="decision-main-grid">
            <article className="workspace-card">
              <div className="section-card-head">
                <h3>分维度评分</h3>
                <span className="muted-caption">用于判断是否值得继续回标</span>
              </div>
              <div className="score-list">
                {scoreCards.map((card) => (
                  <div key={card.label} className="score-item">
                    <div className="score-head">
                      <strong>{card.label}</strong>
                      <span>{card.score}</span>
                    </div>
                    <div className="score-bar">
                      <div className="score-bar-fill" style={{ width: `${card.score}%` }} />
                    </div>
                    <p>{card.note}</p>
                  </div>
                ))}
              </div>
            </article>

            <article className="workspace-card">
              <div className="section-card-head">
                <h3>规则命中与待确认</h3>
                <span className="muted-caption">规则负责卡口，AI 负责解释</span>
              </div>
              <div className="rule-list">
                {ruleHits.map((rule, idx) => (
                  <div key={idx} className="rule-item">
                    <div className="rule-head">
                      <strong>{rule.name}</strong>
                      <span className={`risk-pill risk-${rule.level.toLowerCase()}`}>{rule.level}</span>
                    </div>
                    <span className="status-tag">{rule.result}</span>
                    <p>{rule.detail}</p>
                  </div>
                ))}
              </div>
              {pendingChecks.length > 0 && (
                <div className="pending-box">
                  <h4>待确认事项</h4>
                  <ul className="reason-list">
                    {pendingChecks.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </article>
          </section>
        </>
      )}
    </div>
  );
}
