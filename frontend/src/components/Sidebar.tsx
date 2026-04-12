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
            {navItems.map((item) => (
              <NavLink
                key={item.key}
                to={VIEW_TO_PATH[item.key] ?? "/"}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "nav-item-active" : ""}`
                }
                title={isCollapsed ? item.label : undefined}
              >
                <span className="nav-index">{item.index}</span>
                <span className="nav-copy">
                  <strong>{item.label}</strong>
                  <em>{item.summary}</em>
                </span>
              </NavLink>
            ))}
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
              <span className="nav-index">⚙</span>
              <span className="nav-copy">
                <strong>大模型配置</strong>
                <em>模型管理与切换</em>
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
          {navItems.map((item) => (
            <NavLink
              key={item.key}
              to={VIEW_TO_PATH[item.key] ?? "/"}
              className={({ isActive }) =>
                `nav-item ${isActive ? "nav-item-active" : ""}`
              }
              style={{ justifyContent: 'center', padding: '12px 0' }}
              title={item.label}
            >
              <span className="nav-index" style={{ margin: 0 }}>{item.index}</span>
            </NavLink>
          ))}
        </nav>
      )}
    </aside>
  );
}
