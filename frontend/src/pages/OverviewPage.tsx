import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { WorkspaceData } from "../types";
import { getProjectParsingContext, getLatestDecisionJob } from "../services/workspace";
import { Select } from "../components/Select";

type OverviewPageProps = {
  data: WorkspaceData;
};

export function OverviewPage({ data }: OverviewPageProps) {
  const navigate = useNavigate();
  const [selectedProjectId, setSelectedProjectId] = useState<string | undefined>(
    data.projectRows.length > 0 ? data.projectRows[0].id : undefined
  );

  const [workflowState, setWorkflowState] = useState<Record<string, "pending" | "completed" | "in_progress">>({
    projects: "completed",
    parsing: "pending",
    decision: "pending",
    generation: "pending",
    review: "pending",
  });

  useEffect(() => {
    if (!selectedProjectId) return;

    const proj = data.projectRows.find((p) => p.id === selectedProjectId);
    if (!proj) return;

    if (proj.status === "已关闭") {
      setWorkflowState({
        projects: "completed",
        parsing: "completed",
        decision: "completed",
        generation: "completed",
        review: "completed",
      });
      return;
    }

    // Check Parsing Status
    getProjectParsingContext(selectedProjectId)
      .then((ctx) => {
        const isParsed = ctx.parse_sections.length > 0 || ctx.extracted_fields.length > 0;
        setWorkflowState((prev) => ({ ...prev, parsing: isParsed ? "completed" : "pending" }));
      })
      .catch(() => setWorkflowState((prev) => ({ ...prev, parsing: "pending" })));

    // Check Decision Status
    getLatestDecisionJob(selectedProjectId)
      .then((job) => {
        setWorkflowState((prev) => ({
          ...prev,
          decision: job?.status === "completed" ? "completed" : job?.status === "running" ? "in_progress" : "pending",
        }));
      })
      .catch(() => setWorkflowState((prev) => ({ ...prev, decision: "pending" })));

    // Generation Status heuristic
    const genProj = data.projectRows.find((p) => p.id === selectedProjectId);
    if (genProj) {
      const isGenDone = genProj.status === "已完成" || genProj.status.includes("完成");
      const isGenRunning = genProj.status === "生成中";
      setWorkflowState((prev) => ({
        ...prev,
        generation: isGenDone ? "completed" : isGenRunning ? "in_progress" : "pending",
      }));
    }
  }, [selectedProjectId, data.projectRows]);

  const handleNodeClick = (route: string) => {
    if (!selectedProjectId && route !== "/projects" && route !== "/review") return;
    if (route === "/projects" || route === "/review") {
      navigate(route);
    } else {
      navigate(`${route}?projectId=${selectedProjectId}`);
    }
  };

  const getStatusText = (status: string) => {
    if (status === "completed") return "已完成";
    if (status === "in_progress") return "进行中";
    return "未完成";
  };

  const getStatusIcon = (status: string, num: string) => {
    if (status === "completed") {
      return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      );
    }
    if (status === "in_progress") {
      return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <polyline points="12 6 12 12 16 14"></polyline>
        </svg>
      );
    }
    return num;
  };

  const isLineActive = (fromStatus: string) => {
    return fromStatus === "completed";
  };

  return (
    <>
      <section className="hero-panel">
        <div className="hero-copy-block">
          <p className="eyebrow">Workspace Overview</p>
          <h2>招投标智能体工作台</h2>
          <p className="hero-copy">
            欢迎来到招投标智能体工作台。这里集成了合同审查机器人、招投标自动应答、要求提取与策略辅助等核心功能。
            当前系统已接入大模型语义理解与规则引擎，支持全链路的招投标效率提升与风险管控。
          </p>
          <div className="hero-chip-row">
            <span className="hero-chip">合同条款红线识别</span>
            <span className="hero-chip">招投标自动应答</span>
            <span className="hero-chip">多模态文档解析</span>
            <span className="hero-chip hero-chip-muted">LLM 智能决策</span>
          </div>
        </div>
        <div className="hero-aside">
          <div className="signal-card">
            <span className="signal-label">System Status</span>
            <strong>智能体运行中</strong>
            <p>规则引擎与大模型节点正常，商机台账与知识库服务已就绪。</p>
          </div>
          <div className="signal-grid">
            {data.overviewMetrics.map((metric) => (
              <article key={metric.label} className="signal-metric">
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
                <p>{metric.hint}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="workflow-section" style={{ marginTop: '32px' }}>
        <div className="workflow-header">
          <div className="workflow-title-block">
            <h3>项目工作流</h3>
            <p className="muted-caption">选择项目，查看并推进招投标全链路任务</p>
          </div>
          <Select 
            className="workspace-select" 
            value={selectedProjectId || ""} 
            onChange={(val) => setSelectedProjectId(val)}
            options={
              data.projectRows.length === 0 
                ? [{ label: "暂无项目", value: "" }]
                : data.projectRows.map(p => ({ label: p.name, value: p.id || "" }))
            }
          />
        </div>

        <div className="workflow-pipeline">
          <div className={`workflow-node node-${workflowState.projects.replace('_', '-')}`} onClick={() => handleNodeClick("/projects")}>
            <div className="node-icon">{getStatusIcon(workflowState.projects, "01")}</div>
            <div className="node-info">
              <strong>商机台账</strong>
              <span>{getStatusText(workflowState.projects)}</span>
            </div>
          </div>
          
          <div className={`workflow-line ${isLineActive(workflowState.projects) ? 'active' : ''}`} />

          <div className={`workflow-node node-${workflowState.parsing.replace('_', '-')}`} onClick={() => handleNodeClick("/parsing")}>
            <div className="node-icon">{getStatusIcon(workflowState.parsing, "02")}</div>
            <div className="node-info">
              <strong>要求提取</strong>
              <span>{getStatusText(workflowState.parsing)}</span>
            </div>
          </div>

          <div className={`workflow-line ${isLineActive(workflowState.parsing) ? 'active' : ''}`} />

          <div className={`workflow-node node-${workflowState.decision.replace('_', '-')}`} onClick={() => handleNodeClick("/decision")}>
            <div className="node-icon">{getStatusIcon(workflowState.decision, "03")}</div>
            <div className="node-info">
              <strong>应答策略</strong>
              <span>{getStatusText(workflowState.decision)}</span>
            </div>
          </div>

          <div className={`workflow-line ${isLineActive(workflowState.decision) ? 'active' : ''}`} />

          <div className={`workflow-node node-${workflowState.generation.replace('_', '-')}`} onClick={() => handleNodeClick("/generation")}>
            <div className="node-icon">{getStatusIcon(workflowState.generation, "04")}</div>
            <div className="node-info">
              <strong>回标编写</strong>
              <span>{getStatusText(workflowState.generation)}</span>
            </div>
          </div>
        </div>

        <div className="workflow-parallel">
          <div className="parallel-label">并行支撑</div>
          <div className={`workflow-node node-independent`} onClick={() => handleNodeClick("/review")}>
            <div className="node-icon">C</div>
            <div className="node-info">
              <strong>合同审查</strong>
              <span>独立工具</span>
            </div>
          </div>
        </div>
      </section>

      <section className="status-strip" style={{ marginTop: '32px' }}>
        <div className="status-card">
          <span className="metric-label">最近审查</span>
          <strong>已完成 {data.reviewIssues.length} 项风险识别</strong>
          <p>涵盖付款条件、违约责任与知识产权等红线审查，保障合同安全。</p>
        </div>
        <div className="status-card">
          <span className="metric-label">生成进度</span>
          <strong>{data.generationTodos.length + data.pendingChecks.length} 个待确认项</strong>
          <p>当前项目在要求提取与标书生成中存在信息缺口，需人工跟进补齐。</p>
        </div>
        <div className="status-card">
          <span className="metric-label">知识库就绪</span>
          <strong>{data.generationAssets.length} 个素材切片</strong>
          <p>企业知识资产已结构化，可随时被回标编写智能体检索和引用。</p>
        </div>
      </section>
    </>
  );
}
