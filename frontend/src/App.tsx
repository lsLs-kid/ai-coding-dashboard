import { useState } from "react";
import { Bell, Box, Code2, Database, Home, LineChart, RefreshCcw, Settings, Users, WalletCards } from "lucide-react";
import { CodeMergePage } from "./pages/CodeMergePage";
import { OverviewPage } from "./pages/OverviewPage";

type Page = "overview" | "codemerge";

const navItems: { label: string; icon: React.ComponentType<{ size?: number }>; page: Page | null }[] = [
  { label: "概览", icon: Home, page: "overview" },
  { label: "运营分析", icon: LineChart, page: null },
  { label: "团队分析", icon: Users, page: null },
  { label: "用户分析", icon: Box, page: null },
  { label: "成本分析", icon: WalletCards, page: null },
  { label: "代码入库分析", icon: Database, page: "codemerge" },
  { label: "告警中心", icon: Bell, page: null },
  { label: "设置", icon: Settings, page: null },
];

export function App() {
  const [activePage, setActivePage] = useState<Page>("overview");
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
              className={`nav-item${activePage === item.page ? " is-active" : ""}`}
              onClick={() => {
                if (item.page) setActivePage(item.page);
              }}
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
        {activePage === "overview" && <OverviewPage onUpdatedAt={setUpdatedAt} />}
        {activePage === "codemerge" && <CodeMergePage onUpdatedAt={setUpdatedAt} />}
      </main>
    </div>
  );
}
