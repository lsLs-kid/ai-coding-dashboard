import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  BarChart3,
  Bot,
  ChevronDown,
  Code2,
  Loader2,
  PhoneCall,
  Wrench,
} from "lucide-react";
import ReactECharts from "echarts-for-react";
import { defaultFilters, getFilterOptions, getOperationsOverview } from "../api";
import type {
  DashboardFilters,
  FilterOptions,
  OperationsOverview,
} from "../types";

const kpiIcons = [Bot, Code2, Wrench, PhoneCall];

export function OperationsPage({ onUpdatedAt }: { onUpdatedAt: (t: string) => void }) {
  const [filters, setFilters] = useState<DashboardFilters>(defaultFilters);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [overview, setOverview] = useState<OperationsOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isInitialMount = useRef(true);

  useEffect(() => {
    void bootstrap();
  }, []);

  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }
    void query(filters);
  }, [filters]);

  async function bootstrap() {
    setIsLoading(true);
    setError(null);
    try {
      const [options, data] = await Promise.all([
        getFilterOptions(),
        getOperationsOverview(filters),
      ]);
      setFilterOptions(options);
      setOverview(data);
      onUpdatedAt(new Date().toLocaleString("zh-CN", { hour12: false }).replace(/\//g, "-"));
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
      const data = await getOperationsOverview(nextFilters);
      setOverview(data);
      onUpdatedAt(new Date().toLocaleString("zh-CN", { hour12: false }).replace(/\//g, "-"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "查询失败");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <>
      <header className="page-header">
        <div>
          <h1>运营分析</h1>
          <p>工具调用、AI 采纳、代码生成与用户问题单运营分析</p>
        </div>
      </header>

      <section className="filter-panel">
        {filterOptions ? (
          <FilterGrid
            options={filterOptions}
            filters={filters}
            onChange={setFilters}
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
            <KpiCard
              label="AI 采纳率"
              value={`${overview.kpis.ai_adoption_rate.toFixed(1)}%`}
              change={overview.kpis.ai_adoption_rate_change}
              accent="blue"
              iconIdx={0}
            />
            <KpiCard
              label="AI 生成被采纳代码行数"
              value={overview.kpis.ai_accepted_lines.toLocaleString()}
              change={overview.kpis.ai_accepted_lines_change}
              accent="cyan"
              iconIdx={1}
            />
            <KpiCard
              label="总工具调用次数"
              value={overview.kpis.total_tool_calls.toLocaleString()}
              change={overview.kpis.total_tool_calls_change}
              accent="green"
              iconIdx={2}
            />
            <KpiCard
              label="用户问题单总数"
              value={overview.kpis.total_user_issues.toLocaleString()}
              change={overview.kpis.total_user_issues_change}
              accent="red"
              iconIdx={3}
            />
          </section>

          <section className="operations-chart-grid">
            <ChartPanel title="工具调用 Top 10">
              <ReactECharts option={toolCallTopOption(overview.top_tools)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="工具调用趋势">
              <ReactECharts option={toolCallTrendOption(overview.tool_call_trend)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="AI 采纳率趋势">
              <ReactECharts option={aiAdoptionTrendOption(overview.ai_adoption_trend)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="AI 生成代码行数趋势">
              <ReactECharts option={aiAcceptedLinesTrendOption(overview.ai_accepted_lines_trend)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="用户问题单趋势">
              <ReactECharts option={userIssueTrendOption(overview.user_issue_trend)} notMerge className="chart" />
            </ChartPanel>
            <ChartPanel title="不同类型用户问题单">
              <ReactECharts option={userIssuesByTypeOption(overview.user_issues_by_type)} notMerge className="chart" />
            </ChartPanel>
          </section>
        </>
      ) : null}
    </>
  );
}

function FilterGrid({
  options,
  filters,
  onChange,
}: {
  options: FilterOptions;
  filters: DashboardFilters;
  onChange: (filters: DashboardFilters) => void;
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
    </div>
  );
}

function KpiCard({
  label,
  value,
  change,
  accent,
  iconIdx,
}: {
  label: string;
  value: string;
  change: string;
  accent: "blue" | "cyan" | "green" | "red";
  iconIdx: number;
}) {
  const Icon = kpiIcons[iconIdx] ?? BarChart3;
  const direction = change.startsWith("-") ? "down" : "up";
  return (
    <article className={`kpi-card accent-${accent}`}>
      <div className="kpi-icon">
        <Icon size={28} />
      </div>
      <div>
        <h3>{label}</h3>
        <div className="kpi-value">{value}</div>
        <p className={`delta ${direction}`}>
          较上期
          <span>
            {direction === "down" ? "▼" : "▲"} {change}
          </span>
        </p>
      </div>
    </article>
  );
}

function ChartPanel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <article className="panel">
      <div className="panel-header">
        <h2>
          {title}
          <span className="info-dot">i</span>
        </h2>
      </div>
      {children}
    </article>
  );
}

function toolCallTopOption(items: { tool_name: string; call_count: number }[]) {
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: 16, right: 32, top: 16, bottom: 16, containLabel: true },
    xAxis: { type: "value" },
    yAxis: {
      type: "category",
      data: items.map((i) => i.tool_name).reverse(),
      axisLabel: { width: 90, overflow: "truncate" },
    },
    series: [
      {
        type: "bar",
        data: items.map((i) => i.call_count).reverse(),
        itemStyle: { color: "#3b82f6", borderRadius: [0, 4, 4, 0] },
      },
    ],
  };
}

function lineTrendOption(dates: string[], values: number[], color: string, unit?: string) {
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 16, right: 24, top: 24, bottom: 24, containLabel: true },
    xAxis: { type: "category", data: dates, boundaryGap: false },
    yAxis: { type: "value", axisLabel: { formatter: unit ? `{value}${unit}` : "{value}" } },
    series: [
      {
        type: "line",
        data: values,
        smooth: true,
        symbol: "none",
        lineStyle: { color, width: 2 },
        areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color }, { offset: 1, color: color.replace('rgb', 'rgba').replace(')', ', 0.05)') }] } },
      },
    ],
  };
}

function toolCallTrendOption(trend: { date: string; value: number }[]) {
  return lineTrendOption(
    trend.map((t) => t.date),
    trend.map((t) => t.value),
    "#10b981",
  );
}

function aiAdoptionTrendOption(trend: { date: string; value: number }[]) {
  return lineTrendOption(
    trend.map((t) => t.date),
    trend.map((t) => t.value),
    "#3b82f6",
    "%",
  );
}

function aiAcceptedLinesTrendOption(trend: { date: string; value: number }[]) {
  return lineTrendOption(
    trend.map((t) => t.date),
    trend.map((t) => t.value),
    "#06b6d4",
  );
}

function userIssueTrendOption(trend: { date: string; value: number }[]) {
  return lineTrendOption(
    trend.map((t) => t.date),
    trend.map((t) => t.value),
    "#ef4444",
  );
}

function userIssuesByTypeOption(items: { issue_type: string; count: number }[]) {
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: 16, right: 24, top: 24, bottom: 24, containLabel: true },
    xAxis: { type: "category", data: items.map((i) => i.issue_type) },
    yAxis: { type: "value" },
    series: [
      {
        type: "bar",
        data: items.map((i) => i.count),
        itemStyle: { color: "#f59e0b", borderRadius: [4, 4, 0, 0] },
      },
    ],
  };
}
