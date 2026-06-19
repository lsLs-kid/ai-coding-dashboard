import { useState } from "react";
import { Bell, Box, Code2, Database, Home, LineChart, RefreshCcw, Settings, Users, WalletCards } from "lucide-react";
import { Route, Routes, useLocation, useNavigate } from "react-router-dom";
import { CodeMergePage } from "./pages/CodeMergePage";
import { OverviewPage } from "./pages/OverviewPage";

const navItems: { label: string; icon: React.ComponentType<{ size?: number }>; path: string | null }[] = [
  { label: "概览", icon: Home, path: "/" },
  { label: "运营分析", icon: LineChart, path: null },
  { label: "团队分析", icon: Users, path: null },
  { label: "用户分析", icon: Box, path: null },
  { label: "成本分析", icon: WalletCards, path: null },
  { label: "代码入库分析", icon: Database, path: "/code-merge" },
  { label: "告警中心", icon: Bell, path: null },
  { label: "设置", icon: Settings, path: null },
];

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
              className={`nav-item${item.path === location.pathname ? " is-active" : ""}`}
              onClick={() => { if (item.path) navigate(item.path); }}
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
        </Routes>
      </main>
    </div>
  );
}
