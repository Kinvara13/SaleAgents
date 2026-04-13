import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import { PageAgentFab } from "./components/PageAgentFab";
import { Sidebar } from "./components/Sidebar";
import { DecisionPage } from "./pages/DecisionPage";
import { GenerationPage } from "./pages/GenerationPage";
import { LogsPage } from "./pages/LogsPage";
import { OverviewPage } from "./pages/OverviewPage";
import { ParsingPage } from "./pages/ParsingPage";
import { ProjectsPage } from "./pages/ProjectsPage";
import { ReviewPage } from "./pages/ReviewPage";
import { RulesPage } from "./pages/RulesPage";
import { LLMConfigPage } from "./pages/LLMConfigPage";
import { getWorkspaceData } from "./services/workspace";
import type { WorkspaceData } from "./types";
import { initPageAgent } from "./PageAgentInit";

export default function App() {
  const [data, setData] = useState<WorkspaceData | null>(null);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
    const saved = localStorage.getItem("sidebar_collapsed");
    return saved ? JSON.parse(saved) : false;
  });

  const toggleSidebar = () => {
    const newState = !isSidebarCollapsed;
    setIsSidebarCollapsed(newState);
    localStorage.setItem("sidebar_collapsed", JSON.stringify(newState));
  };

  useEffect(() => {
    let mounted = true;

    getWorkspaceData().then((snapshot) => {
      if (mounted) {
        setData(snapshot);
      }
    });

    // 初始化 PageAgent
    initPageAgent();

    return () => {
      mounted = false;
    };
  }, []);

  async function refreshWorkspace() {
    const snapshot = await getWorkspaceData();
    setData(snapshot);
  }

  useEffect(() => {
    let mounted = true;

    getWorkspaceData().then((snapshot) => {
      if (mounted) {
        setData(snapshot);
      }
    });

    return () => {
      mounted = false;
    };
  }, []);

  if (!data) {
    return (
      <div className="loading-screen">
        <div className="loading-card">
          <span className="eyebrow">Initializing Workspace</span>
          <h2>正在加载招投标智能体工作台</h2>
          <p>正在同步规则引擎、知识库与大模型状态，准备为您提供全链路支撑服务。</p>
        </div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className={`app-shell ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <Sidebar 
          navItems={data.navItems} 
          isCollapsed={isSidebarCollapsed} 
          onToggle={toggleSidebar} 
        />
        <main className="content">
          <Routes>
            <Route path="/" element={<OverviewPage data={data} />} />
            <Route
              path="/generation"
              element={
                <GenerationPage data={data} onGenerationUpdated={refreshWorkspace} />
              }
            />
            <Route
              path="/review"
              element={
                <ReviewPage data={data} onReviewUpdated={refreshWorkspace} />
              }
            />
            <Route path="/rules" element={<RulesPage />} />
            <Route path="/parsing" element={<ParsingPage data={data} />} />
            <Route path="/decision" element={<DecisionPage data={data} />} />
            <Route
              path="/projects"
              element={
                <ProjectsPage data={data} onProjectCreated={refreshWorkspace} />
              }
            />
            <Route path="/llm-config" element={<LLMConfigPage />} />
            <Route path="/logs" element={<LogsPage />} />
          </Routes>
        </main>
        <PageAgentFab />
      </div>
    </BrowserRouter>
  );
}
