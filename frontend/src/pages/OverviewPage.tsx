import { useEffect, useState, type ReactNode } from "react";
import {
  BarChart3,
  ChevronDown,
  Code2,
  Database,
  Download,
  Loader2,
  Users,
} from "lucide-react";
import ReactECharts from "echarts-for-react";
import { defaultFilters, exportReport, getFilterOptions, getOverview } from "../api";
import type {
  DashboardFilters,
  DashboardOverview,
  FilterOptions,
  Insight,
  KpiMetric,
  MrDetail,
  RankingRow,
  TokenDetail,
  UserDetail,
} from "../types";

const kpiIcons = [Users, Users, Database, Code2, Code2, Database];

export function OverviewPage({ onUpdatedAt }: { onUpdatedAt: (t: string) => void }) {
  const [filters, setFilters] = useState<DashboardFilters>(defaultFilters);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    setIsLoading(true);
    setError(null);
    try {
      const [options, data] = await Promise.all([getFilterOptions(), getOverview(filters)]);
      setFilterOptions(options);
      setOverview(data);
      onUpdatedAt(data.updated_at);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function query(nextFilters = filters) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getOverview(nextFilters);
      setOverview(data);
      onUpdatedAt(data.updated_at);
    } catch (err) {
      setError(err instanceof Error ? err.message : "查询失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function onExport() {
    await exportReport(filters);
  }

  const activeFilters = overview?.filters ?? filters;

  return (
    <>
      <header className="page-header">
        <div>
          <h1>AI Coding 运营看板</h1>
          <p>面向无线 / PDU / LM 团队的 AI Coding 使用、成本与入库效果运营分析</p>
        </div>
        <button className="export-button" onClick={onExport}>
          <Download size={16} />
          导出报告
        </button>
      </header>

      <section className="filter-panel">
        {filterOptions ? (
          <FilterGrid
            options={filterOptions}
            filters={activeFilters}
            onChange={setFilters}
            onQuery={() => query(filters)}
          />
        ) : (
          <div className="filter-skeleton">筛选项加载中...</div>
        )}
      </section>

      {error ? <div className="error-banner">{error}</div> : null}

      {isLoading && !overview ? (
        <div className="loading-state">
          <Loader2 className="spin" size={28} />
          正在加载运营数据
        </div>
      ) : overview ? (
        <>
          <section className="kpi-grid">
            {overview.kpis.map((metric, index) => (
              <KpiCard key={metric.key} metric={metric} iconIndex={index} />
            ))}
          </section>

          <section className="chart-grid">
            <ChartPanel title="活跃用户趋势" action="按日">
              <ReactECharts option={activeUserOption(overview)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="Token 消耗趋势" action="按日">
              <ReactECharts option={tokenOption(overview)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="AI MR代码入库占比趋势" action="按日">
              <ReactECharts option={aiRatioOption(overview)} notMerge className="chart" />
            </ChartPanel>
          </section>

          <section className="analysis-grid">
            <RankingPanel rows={overview.rankings} />
            <ChartPanel title="成本-产出分析" action="按团队">
              <ReactECharts option={quadrantOption(overview)} notMerge className="chart" />
            </ChartPanel>
            <InsightsPanel insights={overview.insights} />
          </section>

          <DetailTabs users={overview.users} mrs={overview.mrs} tokens={overview.tokens} />
        </>
      ) : null}
    </>
  );
}

function FilterGrid({
  options,
  filters,
  onChange,
  onQuery,
}: {
  options: FilterOptions;
  filters: DashboardFilters;
  onChange: (filters: DashboardFilters) => void;
  onQuery: () => void;
}) {
  const fields = [
    ["时间范围", "date_range", options.date_ranges],
    ["统计粒度", "granularity", options.granularities],
    ["PDU", "pdu", options.pdus],
    ["LM团队", "lm_team", options.lm_teams],
    ["用户", "user", options.users],
    ["端类型", "terminal_type", options.terminal_types],
    ["客户端版本", "client_version", options.client_versions],
    ["IDE类型", "ide_type", options.ide_types],
    ["模型", "model", options.models],
  ] as const;

  return (
    <div className="filter-grid">
      {fields.map(([label, key, items]) => (
        <label key={key} className="filter-field">
          <span>{label}</span>
          <select
            value={filters[key]}
            onChange={(event) => onChange({ ...filters, [key]: event.target.value })}
          >
            {items.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
          <ChevronDown size={14} />
        </label>
      ))}
      <button className="query-button" onClick={onQuery}>
        查询
      </button>
    </div>
  );
}

function KpiCard({ metric, iconIndex }: { metric: KpiMetric; iconIndex: number }) {
  const Icon = kpiIcons[iconIndex] ?? BarChart3;
  return (
    <article className={`kpi-card accent-${metric.accent}`}>
      <div className="kpi-icon">
        <Icon size={28} />
      </div>
      <div>
        <h3>{metric.label}</h3>
        <div className="kpi-value">
          {metric.value}
          {metric.unit ? <span>{metric.unit}</span> : null}
        </div>
        <p className={`delta ${metric.direction}`}>
          {metric.previous_label}
          <span>
            {metric.direction === "down" ? "▼" : "▲"} {metric.change}
          </span>
        </p>
      </div>
    </article>
  );
}

function ChartPanel({
  title,
  action,
  children,
}: {
  title: string;
  action?: string;
  children: ReactNode;
}) {
  return (
    <article className="panel">
      <div className="panel-header">
        <h2>
          {title}
          <span className="info-dot">i</span>
        </h2>
        {action ? (
          <button className="small-select">
            {action}
            <ChevronDown size={14} />
          </button>
        ) : null}
      </div>
      {children}
    </article>
  );
}

function RankingPanel({ rows }: { rows: RankingRow[] }) {
  return (
    <article className="panel ranking-panel">
      <div className="panel-header">
        <h2>
          PDU / LM 团队运营排行<span className="info-dot">i</span>
        </h2>
      </div>
      <table className="ranking-table">
        <thead>
          <tr>
            <th>排名</th>
            <th>PDU</th>
            <th>LM团队</th>
            <th>活跃用户</th>
            <th>上量占比</th>
            <th>Token（亿）</th>
            <th>AI入库行数</th>
            <th>AI MR占比</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.rank}>
              <td>
                <span className={`rank rank-${row.rank}`}>{row.rank}</span>
              </td>
              <td>{row.pdu}</td>
              <td>{row.lm_team}</td>
              <td>{row.active_users}</td>
              <td>{row.rollout_ratio}%</td>
              <td>{row.token_cost}</td>
              <td>{row.ai_lines.toLocaleString()}</td>
              <td>{row.ai_mr_ratio}%</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="panel-footer">1 / 8</div>
    </article>
  );
}

function InsightsPanel({ insights }: { insights: Insight[] }) {
  return (
    <article className="panel insights-panel">
      <div className="panel-header">
        <h2>
          重点运营关注<span className="info-dot">i</span>
        </h2>
      </div>
      <div className="insight-list">
        {insights.map((item) => (
          <div key={item.title} className={`insight ${item.type}`}>
            <div className="insight-icon">
              {item.type === "risk" ? "!" : item.type === "warning" ? "?" : item.type === "success" ? "↗" : "i"}
            </div>
            <div>
              <strong>{item.title}</strong>
              <p>{item.description}</p>
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function DetailTabs({
  users,
  mrs,
  tokens,
}: {
  users: UserDetail[];
  mrs: MrDetail[];
  tokens: TokenDetail[];
}) {
  const [activeTab, setActiveTab] = useState<"users" | "mrs" | "tokens">("users");
  const tabs = [
    ["users", "用户明细"],
    ["mrs", "MR明细"],
    ["tokens", "Token明细"],
  ] as const;

  return (
    <section className="panel detail-panel">
      <div className="tabs">
        {tabs.map(([key, label]) => (
          <button
            key={key}
            className={activeTab === key ? "is-active" : ""}
            onClick={() => setActiveTab(key)}
          >
            {label}
          </button>
        ))}
      </div>
      {activeTab === "users" ? <UsersTable rows={users} /> : null}
      {activeTab === "mrs" ? <MrsTable rows={mrs} /> : null}
      {activeTab === "tokens" ? <TokensTable rows={tokens} /> : null}
      <div className="table-footer">
        <span>共 1,268 条</span>
        <button disabled>‹</button>
        <button className="is-active">1</button>
        <button>2</button>
        <button>3</button>
        <button>›</button>
        <span>每页 10 条</span>
      </div>
    </section>
  );
}

function UsersTable({ rows }: { rows: UserDetail[] }) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>用户</th>
          <th>PDU</th>
          <th>LM团队</th>
          <th>端类型</th>
          <th>客户端版本</th>
          <th>IDE类型</th>
          <th>最近活跃时间</th>
          <th>Prompt数</th>
          <th>Token（万）</th>
          <th>MR数</th>
          <th>AI入库行数</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            <td>{row.name}</td>
            <td>{row.pdu}</td>
            <td>{row.lm_team}</td>
            <td>{row.terminal_type}</td>
            <td>{row.client_version}</td>
            <td>{row.ide_type}</td>
            <td>{row.last_active_at ?? "-"}</td>
            <td>{row.prompt_count}</td>
            <td>{row.token_cost}</td>
            <td>{row.mr_count}</td>
            <td>{row.ai_lines.toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function MrsTable({ rows }: { rows: MrDetail[] }) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>MR</th>
          <th>仓库</th>
          <th>作者</th>
          <th>PDU</th>
          <th>LM团队</th>
          <th>合入时间</th>
          <th>有效代码行</th>
          <th>AI代码行</th>
          <th>AI MR占比</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.mr_id}>
            <td>{row.mr_id}</td>
            <td>{row.repository}</td>
            <td>{row.author}</td>
            <td>{row.pdu}</td>
            <td>{row.lm_team}</td>
            <td>{row.merged_at}</td>
            <td>{row.total_lines.toLocaleString()}</td>
            <td>{row.ai_lines.toLocaleString()}</td>
            <td>{row.ai_mr_ratio}%</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function TokensTable({ rows }: { rows: TokenDetail[] }) {
  return (
    <table className="data-table">
      <thead>
        <tr>
          <th>日期</th>
          <th>用户</th>
          <th>模型</th>
          <th>输入Token</th>
          <th>输出Token</th>
          <th>总Token</th>
          <th>Trace ID</th>
          <th>状态码</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.id}>
            <td>{row.date}</td>
            <td>{row.user}</td>
            <td>{row.model}</td>
            <td>{row.input_tokens.toLocaleString()}</td>
            <td>{row.output_tokens.toLocaleString()}</td>
            <td>{row.total_tokens.toLocaleString()}</td>
            <td>{row.trace_id}</td>
            <td>{row.status_code}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function baseGrid() {
  return {
    grid: { left: 48, right: 20, top: 36, bottom: 42 },
    tooltip: { trigger: "axis" },
    textStyle: { fontFamily: "Inter, Microsoft YaHei, system-ui", color: "#24324a" },
  };
}

function activeUserOption(data: DashboardOverview) {
  return {
    ...baseGrid(),
    xAxis: { type: "category", data: data.trends.map((d) => d.date), axisTick: { show: false } },
    yAxis: { type: "value", name: "活跃用户数（人）", splitLine: { lineStyle: { color: "#e8edf5" } } },
    series: [
      {
        data: data.trends.map((d) => d.active_users),
        type: "line",
        smooth: true,
        symbolSize: 7,
        areaStyle: { color: "rgba(37, 111, 246, .12)" },
        lineStyle: { width: 3, color: "#256ff6" },
        itemStyle: { color: "#256ff6" },
      },
    ],
  };
}

function tokenOption(data: DashboardOverview) {
  return {
    ...baseGrid(),
    xAxis: { type: "category", data: data.trends.map((d) => d.date), axisTick: { show: false } },
    yAxis: { type: "value", name: "Token 消耗（亿）", splitLine: { lineStyle: { color: "#e8edf5" } } },
    series: [
      {
        data: data.trends.map((d) => d.token_cost),
        type: "bar",
        barWidth: 10,
        itemStyle: { borderRadius: [4, 4, 0, 0], color: "#2f7df6" },
      },
    ],
  };
}

function aiRatioOption(data: DashboardOverview) {
  return {
    ...baseGrid(),
    xAxis: { type: "category", data: data.trends.map((d) => d.date), axisTick: { show: false } },
    yAxis: { type: "value", name: "%", min: 0, max: 50, splitLine: { lineStyle: { color: "#f0dada" } } },
    series: [
      {
        data: data.trends.map((d) => d.ai_mr_ratio),
        type: "line",
        smooth: true,
        symbolSize: 6,
        areaStyle: { color: "rgba(238, 51, 66, .10)" },
        lineStyle: { width: 3, color: "#ef3445" },
        itemStyle: { color: "#ef3445" },
      },
    ],
  };
}

function quadrantOption(data: DashboardOverview) {
  return {
    grid: { left: 58, right: 44, top: 34, bottom: 48 },
    tooltip: {
      formatter: (params: { data: [number, number, number, string] }) =>
        `${params.data[3]}<br/>Token: ${params.data[0]}亿<br/>AI MR占比: ${params.data[1]}%`,
    },
    xAxis: { name: "Token 消耗（亿）", splitLine: { lineStyle: { color: "#e7edf6" } } },
    yAxis: { name: "AI入库代码行数（万行）", splitLine: { lineStyle: { color: "#e7edf6" } } },
    series: [
      {
        type: "scatter",
        symbolSize: (value: number[]) => Math.max(16, Math.min(34, value[2] / 18000)),
        data: data.quadrant.map((d) => [d.token_cost, d.ai_mr_ratio, d.ai_lines, d.name]),
        itemStyle: {
          color: (params: { dataIndex: number }) =>
            ["#10b99a", "#17a48d", "#2c73f6", "#1f8cff", "#ef3445"][params.dataIndex % 5],
        },
        label: {
          show: true,
          formatter: (params: { data: [number, number, number, string] }) => params.data[3],
          position: "top",
          fontSize: 10,
          color: "#27344c",
        },
        labelLayout: { hideOverlap: true },
      },
    ],
  };
}
