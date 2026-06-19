import { useState } from "react";
import { Bell, Box, Code2, Database, Home, LineChart, RefreshCcw, Settings, Users, WalletCards } from "lucide-react";
import { Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { OperationsPage } from "./pages/OperationsPage";
import { CostPage } from "./pages/CostPage";
import { CodeMergePage } from "./pages/CodeMergePage";
import { OverviewPage } from "./pages/OverviewPage";

const navItems: { label: string; icon: React.ComponentType<{ size?: number }>; path: string }[] = [
  { label: "概览", icon: Home, path: "/" },
  { label: "运营分析", icon: LineChart, path: "/operations" },
  { label: "团队分析", icon: Users, path: "/teams" },
  { label: "用户分析", icon: Box, path: "/users" },
  { label: "成本分析", icon: WalletCards, path: "/cost" },
  { label: "代码入库分析", icon: Database, path: "/code-merge" },
  { label: "告警中心", icon: Bell, path: "/alerts" },
  { label: "设置", icon: Settings, path: "/settings" },
];

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="loading-state" style={{ flexDirection: "column", gap: 12, minHeight: 320 }}>
      <span style={{ fontSize: 32, color: "#d0d8e8" }}>🚧</span>
      <span style={{ color: "#8595ae" }}>{title} — 页面建设中</span>
    </div>
  );
}

export function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [updatedAt, setUpdatedAt] = useState("--");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">
          <Code2 size={30} />
        </div>
        <nav className="nav-list">
          {navItems.map((item) => (
            <button
              key={item.label}
              className={`nav-item${location.pathname === item.path ? " is-active" : ""}`}
              onClick={() => navigate(item.path)}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="sync-time">
          <RefreshCcw size={14} />
          <span>数据更新时间</span>
          <strong>{updatedAt}</strong>
        </div>
      </aside>
      <main className="dashboard">
        <Routes>
          <Route path="/" element={<OverviewPage onUpdatedAt={setUpdatedAt} />} />
          <Route path="/code-merge" element={<CodeMergePage onUpdatedAt={setUpdatedAt} />} />
          <Route path="/operations" element={<OperationsPage onUpdatedAt={setUpdatedAt} />} />
          <Route path="/teams" element={<PlaceholderPage title="团队分析" />} />
          <Route path="/users" element={<PlaceholderPage title="用户分析" />} />
          <Route path="/cost" element={<CostPage onUpdatedAt={setUpdatedAt} />} />
          <Route path="/alerts" element={<PlaceholderPage title="告警中心" />} />
          <Route path="/settings" element={<PlaceholderPage title="设置" />} />
        </Routes>
      </main>
    </div>
  );
}
