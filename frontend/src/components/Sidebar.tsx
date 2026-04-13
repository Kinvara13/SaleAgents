import { NavLink } from "react-router-dom";

import type { NavItem } from "../types";

const VIEW_TO_PATH: Record<string, string> = {
  overview: "/",
  generation: "/generation",
  review: "/review",
  rules: "/rules",
  parsing: "/parsing",
  decision: "/decision",
  projects: "/projects",
  logs: "/logs",
};

type SidebarProps = {
  navItems: NavItem[];
  isCollapsed?: boolean;
  onToggle?: () => void;
};

export function Sidebar({ navItems, isCollapsed = false, onToggle }: SidebarProps) {
  return (
    <aside className="sidebar">
      <button 
        className="sidebar-collapse-btn" 
        onClick={onToggle}
        title={isCollapsed ? "展开侧边栏" : "收起侧边栏"}
      >
        {isCollapsed ? '▶' : '◀'}
      </button>
      
      <div className="sidebar-glow" />
      <div className="sidebar-content">
        <div className="brand">
          <span className="brand-kicker">Agent Workspace</span>
          <h1>招投标智能体</h1>
          <p className="brand-copy"></p>
        </div>
        <section className="sidebar-panel">
          <p className="sidebar-label">核心模块</p>
          <nav className="nav-list">
            {navItems.map((item) => {
              // 为不同模块分配图标
              let icon = null;
              switch (item.key) {
                case "overview":
                  icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>;
                  break;
                case "projects":
                  icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>;
                  break;
                case "parsing":
                  icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>;
                  break;
                case "decision":
                  icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>;
                  break;
                case "generation":
                  icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>;
                  break;
                case "review":
                  icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><path d="M9 15l2 2 4-4"></path></svg>;
                  break;
                case "rules":
                  icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>;
                  break;
                default:
                  icon = <span style={{ fontSize: '12px' }}>{item.index}</span>;
              }

              return (
                <NavLink
                  key={item.key}
                  to={VIEW_TO_PATH[item.key] ?? "/"}
                  className={({ isActive }) =>
                    `nav-item ${isActive ? "nav-item-active" : ""}`
                  }
                  title={isCollapsed ? item.label : undefined}
                >
                  <span className="nav-index" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {icon}
                  </span>
                  <span className="nav-copy">
                    <strong>{item.label}</strong>
                    <em>{item.summary}</em>
                  </span>
                </NavLink>
              );
            })}
          </nav>
        </section>
        <section className="sidebar-panel">
          <p className="sidebar-label">系统管理</p>
          <nav className="nav-list">
            <NavLink
              to="/llm-config"
              className={({ isActive }) =>
                `nav-item ${isActive ? "nav-item-active" : ""}`
              }
              title={isCollapsed ? "大模型配置" : undefined}
            >
              <span className="nav-index" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="3"></circle>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                </svg>
              </span>
              <span className="nav-copy">
                <strong>大模型配置</strong>
                <em>模型管理与切换</em>
              </span>
            </NavLink>
            <NavLink
              to="/logs"
              className={({ isActive }) =>
                `nav-item ${isActive ? "nav-item-active" : ""}`
              }
              title={isCollapsed ? "系统日志" : undefined}
            >
              <span className="nav-index" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="4 17 10 11 4 5"></polyline>
                  <line x1="12" y1="19" x2="20" y2="19"></line>
                </svg>
              </span>
              <span className="nav-copy">
                <strong>系统日志</strong>
                <em>前后端实时监控</em>
              </span>
            </NavLink>
          </nav>
        </section>
        <section className="sidebar-foot">
          <p className="sidebar-label">系统状态</p>
          <div className="runtime-card">
            <strong>引擎与模型就绪</strong>
            <span>全链路 API 已打通，支持自动审查、决策辅助与应答生成。</span>
          </div>
        </section>
      </div>
      
      {/* 折叠状态下的图标导航 */}
      {isCollapsed && (
        <nav className="nav-list" style={{ marginTop: 0, width: '100%' }}>
          {navItems.map((item) => {
            let icon = null;
            switch (item.key) {
              case "overview":
                icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>;
                break;
              case "projects":
                icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>;
                break;
              case "parsing":
                icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>;
                break;
              case "decision":
                icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>;
                break;
              case "generation":
                icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>;
                break;
              case "review":
                icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><path d="M9 15l2 2 4-4"></path></svg>;
                break;
              case "rules":
                icon = <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>;
                break;
              default:
                icon = <span style={{ fontSize: '12px' }}>{item.index}</span>;
            }

            return (
              <NavLink
                key={item.key}
                to={VIEW_TO_PATH[item.key] ?? "/"}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "nav-item-active" : ""}`
                }
                style={{ justifyContent: 'center', padding: '12px 0' }}
                title={item.label}
              >
                <span className="nav-index" style={{ margin: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{icon}</span>
              </NavLink>
            );
          })}
          
          {/* 折叠状态下的系统管理图标 */}
          <div style={{ marginTop: '24px', borderTop: '1px solid rgba(132, 180, 255, 0.14)', paddingTop: '12px' }}>
            <NavLink
              to="/llm-config"
              className={({ isActive }) =>
                `nav-item ${isActive ? "nav-item-active" : ""}`
              }
              style={{ justifyContent: 'center', padding: '12px 0' }}
              title="大模型配置"
            >
              <span className="nav-index" style={{ margin: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="3"></circle>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                </svg>
              </span>
            </NavLink>
            <NavLink
              to="/logs"
              className={({ isActive }) =>
                `nav-item ${isActive ? "nav-item-active" : ""}`
              }
              style={{ justifyContent: 'center', padding: '12px 0' }}
              title="系统日志"
            >
              <span className="nav-index" style={{ margin: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="4 17 10 11 4 5"></polyline>
                  <line x1="12" y1="19" x2="20" y2="19"></line>
                </svg>
              </span>
            </NavLink>
          </div>
        </nav>
      )}
    </aside>
  );
}
