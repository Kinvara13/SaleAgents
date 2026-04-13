import { useState, useEffect, useRef } from "react";

type LogTab = "backend" | "frontend" | "all";

interface LogsResponse {
  backend: string;
  frontend: string;
  backend_exists: boolean;
  frontend_exists: boolean;
}

export function LogsPage() {
  const [activeTab, setActiveTab] = useState<LogTab>("all");
  const [logs, setLogs] = useState<LogsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const backendRef = useRef<HTMLDivElement>(null);
  const frontendRef = useRef<HTMLDivElement>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const resp = await fetch(`/api/v1/system/logs?log_type=${activeTab}&lines=500`);
      if (resp.ok) {
        const data: LogsResponse = await resp.json();
        setLogs(data);
        setLastUpdated(new Date());
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [activeTab]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchLogs, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh, activeTab]);

  useEffect(() => {
    if (autoRefresh && backendRef.current) {
      backendRef.current.scrollTop = backendRef.current.scrollHeight;
    }
    if (autoRefresh && frontendRef.current) {
      frontendRef.current.scrollTop = frontendRef.current.scrollHeight;
    }
  }, [logs, autoRefresh]);

  const formatLine = (line: string) => {
    if (line.startsWith("ERROR") || line.includes("[ERROR]")) {
      return <span style={{ color: "#ef4444" }}>{line}</span>;
    }
    if (line.startsWith("WARNING") || line.includes("[ZIP解析]")) {
      return <span style={{ color: "#f59e0b" }}>{line}</span>;
    }
    if (line.includes("LLM") || line.includes("llm")) {
      return <span style={{ color: "#a78bfa" }}>{line}</span>;
    }
    if (line.startsWith("INFO")) {
      return <span style={{ color: "#60a5fa" }}>{line}</span>;
    }
    return <span style={{ color: "#d1d5db" }}>{line}</span>;
  };

  return (
    <div className="workspace-page">
      <div className="section-card-head" style={{ marginBottom: "16px" }}>
        <h3 style={{ margin: 0 }}>实时日志监控</h3>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {lastUpdated && (
            <span className="muted-caption" style={{ fontSize: "12px" }}>
              最后更新: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer", fontSize: "13px", color: "#94a3b8" }}>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              style={{ cursor: "pointer" }}
            />
            自动刷新 (3s)
          </label>
          <button className="ghost-button" style={{ padding: "4px 12px" }} onClick={fetchLogs} disabled={loading}>
            {loading ? "加载中..." : "刷新"}
          </button>
        </div>
      </div>

      <div style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
        {(["all", "backend", "frontend"] as LogTab[]).map((tab) => (
          <button
            key={tab}
            className={activeTab === tab ? "primary-button" : "ghost-button"}
            style={{ padding: "6px 16px" }}
            onClick={() => setActiveTab(tab)}
          >
            {tab === "all" ? "全部" : tab === "backend" ? "后端日志" : "前端日志"}
          </button>
        ))}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        {(activeTab === "all" || activeTab === "backend") && (
          <div className="workspace-card" style={{ padding: "0", overflow: "hidden" }}>
            <div style={{
              padding: "10px 16px",
              background: "rgba(255,255,255,0.03)",
              borderBottom: "1px solid rgba(129,186,255,0.1)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}>
              <span style={{ fontSize: "13px", fontWeight: 600, color: "#60a5fa" }}>🔌 后端日志 (backend.log)</span>
              {!logs?.backend_exists && <span className="muted-caption" style={{ fontSize: "12px" }}>文件不存在</span>}
            </div>
            <div
              ref={backendRef}
              style={{
                height: "calc(100vh - 340px)",
                overflowY: "auto",
                background: "#0a0f1a",
                padding: "12px 16px",
                fontFamily: "ui-monospace, 'Cascadia Code', 'Fira Code', monospace",
                fontSize: "12px",
                lineHeight: "1.6",
                whiteSpace: "pre-wrap",
                wordBreak: "break-all",
              }}
            >
              {logs?.backend_exists ? (
                logs.backend.split("\n").map((line, i) => (
                  <div key={i}>{formatLine(line)}</div>
                ))
              ) : (
                <span style={{ color: "#475569" }}>暂无后端日志，请确认后端服务已启动。</span>
              )}
            </div>
          </div>
        )}

        {(activeTab === "all" || activeTab === "frontend") && (
          <div className="workspace-card" style={{ padding: "0", overflow: "hidden" }}>
            <div style={{
              padding: "10px 16px",
              background: "rgba(255,255,255,0.03)",
              borderBottom: "1px solid rgba(129,186,255,0.1)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}>
              <span style={{ fontSize: "13px", fontWeight: 600, color: "#34d399" }}>⚡ 前端日志 (frontend.log)</span>
              {!logs?.frontend_exists && <span className="muted-caption" style={{ fontSize: "12px" }}>文件不存在</span>}
            </div>
            <div
              ref={frontendRef}
              style={{
                height: "calc(100vh - 340px)",
                overflowY: "auto",
                background: "#0a0f1a",
                padding: "12px 16px",
                fontFamily: "ui-monospace, 'Cascadia Code', 'Fira Code', monospace",
                fontSize: "12px",
                lineHeight: "1.6",
                whiteSpace: "pre-wrap",
                wordBreak: "break-all",
              }}
            >
              {logs?.frontend_exists ? (
                logs.frontend.split("\n").map((line, i) => (
                  <div key={i}>{formatLine(line)}</div>
                ))
              ) : (
                <span style={{ color: "#475569" }}>暂无前端日志，请确认前端服务已启动。</span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
