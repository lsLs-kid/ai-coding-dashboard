import { useEffect, useState } from "react";
import { BarChart3, Box, ChevronDown, Code2, Database, Loader2 } from "lucide-react";
import ReactECharts from "echarts-for-react";
import { defaultCodeMergeFilters, getCodeMergeMrs, getCodeMergeOverview, getFilterOptions } from "../api";
import type {
  CodeMergeFilters,
  CodeMergeOverview,
  MrRatioBucket,
  FilterOptions,
  MergeTrendPoint,
  MrPageResponse,
  RepoMergeStats,
} from "../types";

const cmKpiIcons = [Code2, BarChart3, Database, Database, Box];

export function CodeMergePage({ onUpdatedAt }: { onUpdatedAt: (t: string) => void }) {
  const [filters, setFilters] = useState<CodeMergeFilters>(defaultCodeMergeFilters);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [overview, setOverview] = useState<CodeMergeOverview | null>(null);
  const [mrs, setMrs] = useState<MrPageResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [tableLoading, setTableLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tableState, setTableState] = useState({
    page: 1,
    sort_by: "merged_at",
    sort_order: "desc" as "asc" | "desc",
  });

  useEffect(() => {
    void bootstrap();
  }, []);

  async function bootstrap() {
    setIsLoading(true);
    setError(null);
    try {
      const [options, ovData, mrData] = await Promise.all([
        getFilterOptions(),
        getCodeMergeOverview(filters),
        getCodeMergeMrs({ ...filters, ...tableState, page_size: 20 }),
      ]);
      setFilterOptions(options);
      setOverview(ovData);
      setMrs(mrData);
      onUpdatedAt(new Date().toLocaleString("zh-CN", { hour12: false }).replace(/\//g, "-"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function query(nextFilters: CodeMergeFilters) {
    setIsLoading(true);
    setError(null);
    const nextTable = { ...tableState, page: 1 };
    setTableState(nextTable);
    try {
      const [ovData, mrData] = await Promise.all([
        getCodeMergeOverview(nextFilters),
        getCodeMergeMrs({ ...nextFilters, ...nextTable, page_size: 20 }),
      ]);
      setOverview(ovData);
      setMrs(mrData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "查询失败");
    } finally {
      setIsLoading(false);
    }
  }

  async function fetchMrs(next: typeof tableState, currentFilters: CodeMergeFilters) {
    setTableLoading(true);
    try {
      const mrData = await getCodeMergeMrs({ ...currentFilters, ...next, page_size: 20 });
      setMrs(mrData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "加载失败");
    } finally {
      setTableLoading(false);
    }
  }

  function handleSort(col: string) {
    const nextOrder: "asc" | "desc" =
      tableState.sort_by === col && tableState.sort_order === "desc" ? "asc" : "desc";
    const next = { ...tableState, sort_by: col, sort_order: nextOrder, page: 1 };
    setTableState(next);
    void fetchMrs(next, filters);
  }

  function handlePage(page: number) {
    const next = { ...tableState, page };
    setTableState(next);
    void fetchMrs(next, filters);
  }

  function handleFilterChange(f: CodeMergeFilters) {
    setFilters(f);
    void query(f);
  }

  return (
    <>
      <header className="page-header">
        <div>
          <h1>代码入库分析</h1>
          <p>各 PDU 下 MR 入库中 AI 生成代码占比分析</p>
        </div>
      </header>

      <section className="filter-panel">
        {filterOptions ? (
          <CodeMergeFilterBar options={filterOptions} filters={filters} onChange={handleFilterChange} />
        ) : (
          <div className="filter-skeleton">筛选项加载中...</div>
        )}
      </section>

      {error ? <div className="error-banner">{error}</div> : null}

      {isLoading && !overview ? (
        <div className="loading-state">
          <Loader2 className="spin" size={28} />
          正在加载入库数据
        </div>
      ) : overview ? (
        <>
          <section className="codemerge-kpi-grid">
            <CmKpiCard
              label="AI 代码入库行数"
              value={overview.kpis.total_ai_lines.toLocaleString()}
              change={overview.kpis.ai_lines_change}
              accent="blue"
              iconIdx={0}
            />
            <CmKpiCard
              label="整体 AI 代码占比"
              value={`${overview.kpis.overall_ai_ratio}%`}
              change={overview.kpis.ai_ratio_change}
              accent="cyan"
              iconIdx={1}
            />
            <CmKpiCard
              label="入库 MR 总数"
              value={overview.kpis.total_mrs.toLocaleString()}
              change={overview.kpis.mr_count_change}
              accent="green"
              iconIdx={2}
            />
            <CmKpiCard
              label="AI 辅助 MR 占比"
              value={`${overview.kpis.ai_assisted_ratio}%`}
              change={overview.kpis.ai_assisted_ratio_change}
              accent="red"
              iconIdx={3}
            />
            <CmKpiCard
              label="涉及仓库数"
              value={overview.kpis.total_repos.toLocaleString()}
              change={null}
              accent="blue"
              iconIdx={4}
            />
          </section>

          <section className="codemerge-chart-grid">
            <article className="panel">
              <div className="panel-header">
                <h2>
                  AI MR代码入库占比趋势<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={aiMrRatioOption(overview.trend)} notMerge style={{ height: 220 }} />
            </article>
            <article className="panel">
              <div className="panel-header">
                <h2>
                  AI 代码占比趋势<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={trendOption(overview.trend)} notMerge style={{ height: 220 }} />
            </article>
            <article className="panel">
              <div className="panel-header">
                <h2>
                  仓库 AI 代码行 Top 10<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts option={repoBarOption(overview.top_repos)} notMerge style={{ height: 220 }} />
            </article>
            <article className="panel">
              <div className="panel-header">
                <h2>
                  MR AI 占比分布<span className="info-dot">i</span>
                </h2>
              </div>
              <ReactECharts
                option={mrRatioDistributionOption(overview.mr_ratio_distribution)}
                notMerge
                style={{ height: 220 }}
              />
            </article>
          </section>

          {mrs ? (
            <MrTable
              response={mrs}
              sortBy={tableState.sort_by}
              sortOrder={tableState.sort_order}
              onSort={handleSort}
              onPage={handlePage}
              loading={tableLoading}
            />
          ) : null}
        </>
      ) : null}
    </>
  );
}

// ── Filter bar ─────────────────────────────────────────────────────────────

const thresholdOptions = [
  { label: "AI辅助MR阈值 ≥30%", value: 30 as const },
  { label: "AI辅助MR阈值 ≥50%", value: 50 as const },
  { label: "AI辅助MR阈值 ≥70%", value: 70 as const },
];

function CodeMergeFilterBar({
  options,
  filters,
  onChange,
}: {
  options: FilterOptions;
  filters: CodeMergeFilters;
  onChange: (f: CodeMergeFilters) => void;
}) {
  return (
    <div className="codemerge-filter-grid">
      <label className="filter-field">
        <span>时间范围</span>
        <select
          value={filters.date_range}
          onChange={(e) => onChange({ ...filters, date_range: e.target.value })}
        >
          {options.date_ranges.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={14} />
      </label>
      <label className="filter-field">
        <span>统计粒度</span>
        <select
          value={filters.granularity}
          onChange={(e) =>
            onChange({ ...filters, granularity: e.target.value as CodeMergeFilters["granularity"] })
          }
        >
          {options.granularities.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={14} />
      </label>
      <label className="filter-field">
        <span>PDU</span>
        <select
          value={filters.pdu}
          onChange={(e) => onChange({ ...filters, pdu: e.target.value })}
        >
          {options.pdus.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={14} />
      </label>
      <label className="filter-field">
        <span>LM团队</span>
        <select
          value={filters.lm_team}
          onChange={(e) => onChange({ ...filters, lm_team: e.target.value })}
        >
          {options.lm_teams.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={14} />
      </label>
      <label className="filter-field">
        <span>AI辅助MR阈值</span>
        <select
          value={filters.ai_ratio_threshold}
          onChange={(e) =>
            onChange({
              ...filters,
              ai_ratio_threshold: Number(e.target.value) as 30 | 50 | 70,
            })
          }
        >
          {thresholdOptions.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={14} />
      </label>
    </div>
  );
}

// ── KPI card ───────────────────────────────────────────────────────────────

function CmKpiCard({
  label,
  value,
  change,
  accent,
  iconIdx,
}: {
  label: string;
  value: string;
  change: string | null;
  accent: "blue" | "red" | "green" | "cyan";
  iconIdx: number;
}) {
  const Icon = cmKpiIcons[iconIdx] ?? BarChart3;
  const direction =
    change == null ? "flat" : change.startsWith("+") ? "up" : change.startsWith("-") ? "down" : "flat";
  return (
    <article className={`kpi-card accent-${accent}`}>
      <div className="kpi-icon">
        <Icon size={28} />
      </div>
      <div>
        <h3>{label}</h3>
        <div className="kpi-value">{value}</div>
        {change ? (
          <p className={`delta ${direction}`}>
            较上期<span> {change}</span>
          </p>
        ) : null}
      </div>
    </article>
  );
}

// ── MR table ───────────────────────────────────────────────────────────────

function MrTable({
  response,
  sortBy,
  sortOrder,
  onSort,
  onPage,
  loading,
}: {
  response: MrPageResponse;
  sortBy: string;
  sortOrder: "asc" | "desc";
  onSort: (col: string) => void;
  onPage: (page: number) => void;
  loading: boolean;
}) {
  const totalPages = Math.ceil(response.total / response.page_size);
  const start = Math.max(1, response.page - 2);
  const end = Math.min(totalPages, start + 4);
  const pageNums: number[] = [];
  for (let p = start; p <= end; p++) pageNums.push(p);

  return (
    <section className="panel detail-panel" style={{ opacity: loading ? 0.6 : 1 }}>
      <div className="panel-header" style={{ padding: "14px 0 0" }}>
        <h2>
          MR 明细<span className="info-dot">i</span>
        </h2>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>MR</th>
            <th>仓库</th>
            <th>作者</th>
            <th>PDU</th>
            <th>团队</th>
            <SortTh label="入库时间" col="merged_at" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <SortTh label="总行数" col="total_lines" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <SortTh label="AI行数" col="ai_lines" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <SortTh label="AI占比" col="ai_mr_ratio" sortBy={sortBy} sortOrder={sortOrder} onSort={onSort} />
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          {response.items.map((row) => (
            <tr key={row.mr_id}>
              <td>{row.mr_id}</td>
              <td style={{ textAlign: "left" }}>{row.repository}</td>
              <td>{row.author}</td>
              <td>{row.pdu}</td>
              <td>{row.lm_team}</td>
              <td>{row.merged_at}</td>
              <td>{row.total_lines.toLocaleString()}</td>
              <td>{row.ai_lines.toLocaleString()}</td>
              <td>{row.ai_mr_ratio}%</td>
              <td>{row.status === "merged" ? "已合入" : "待合入"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="table-footer">
        <span>共 {response.total} 条</span>
        <button disabled={response.page <= 1} onClick={() => onPage(response.page - 1)}>
          ‹
        </button>
        {pageNums.map((p) => (
          <button
            key={p}
            className={response.page === p ? "is-active" : ""}
            onClick={() => onPage(p)}
          >
            {p}
          </button>
        ))}
        <button disabled={response.page >= totalPages} onClick={() => onPage(response.page + 1)}>
          ›
        </button>
        <span>每页 {response.page_size} 条</span>
      </div>
    </section>
  );
}

function SortTh({
  label,
  col,
  sortBy,
  sortOrder,
  onSort,
}: {
  label: string;
  col: string;
  sortBy: string;
  sortOrder: "asc" | "desc";
  onSort: (col: string) => void;
}) {
  const arrow = sortBy === col ? (sortOrder === "desc" ? " ↓" : " ↑") : " ↕";
  return (
    <th className="th-sortable" onClick={() => onSort(col)}>
      {label}
      {arrow}
    </th>
  );
}

// ── ECharts option builders ────────────────────────────────────────────────

function baseTextStyle() {
  return { fontFamily: "Inter, Microsoft YaHei, system-ui", color: "#24324a" };
}

function aiMrRatioOption(trend: MergeTrendPoint[]) {
  return {
    grid: { left: 48, right: 20, top: 36, bottom: 42 },
    tooltip: { trigger: "axis" },
    textStyle: baseTextStyle(),
    xAxis: { type: "category", data: trend.map((d) => d.date), axisTick: { show: false } },
    yAxis: { type: "value", name: "%", min: 0, max: 50, splitLine: { lineStyle: { color: "#f0dada" } } },
    series: [
      {
        data: trend.map((d) => d.ai_ratio),
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

function trendOption(trend: MergeTrendPoint[]) {
  return {
    grid: { left: 56, right: 20, top: 28, bottom: 42 },
    tooltip: { trigger: "axis" },
    textStyle: baseTextStyle(),
    xAxis: { type: "category", data: trend.map((d) => d.date), axisTick: { show: false } },
    yAxis: {
      type: "value",
      name: "%",
      min: 0,
      splitLine: { lineStyle: { color: "#e8edf5" } },
    },
    series: [
      {
        data: trend.map((d) => d.ai_ratio),
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

function repoBarOption(topRepos: RepoMergeStats[]) {
  const reversed = [...topRepos].reverse();
  return {
    tooltip: { trigger: "axis" },
    grid: { left: 140, right: 20, top: 16, bottom: 36 },
    textStyle: baseTextStyle(),
    xAxis: { type: "value", name: "AI代码行数" },
    yAxis: { type: "category", data: reversed.map((d) => d.repository) },
    series: [
      {
        type: "bar",
        data: reversed.map((d) => d.ai_lines),
        itemStyle: { color: "#10b99a", borderRadius: [0, 4, 4, 0] },
      },
    ],
  };
}

function mrRatioDistributionOption(distribution: MrRatioBucket[]) {
  const barColors = ["#c6d9fc", "#7aaaf5", "#4d85f5", "#1d5fdf", "#0a3fa8"];
  return {
    grid: { left: 48, right: 20, top: 36, bottom: 42 },
    tooltip: {
      trigger: "axis",
      formatter: (params: { name: string; value: number }[]) =>
        `AI占比 ${params[0].name}<br/>MR 数：${params[0].value}`,
    },
    textStyle: baseTextStyle(),
    xAxis: {
      type: "category",
      data: distribution.map((d) => d.label),
      axisTick: { show: false },
      name: "AI 代码占比区间",
      nameLocation: "middle",
      nameGap: 28,
    },
    yAxis: {
      type: "value",
      name: "MR 数",
      splitLine: { lineStyle: { color: "#e8edf5" } },
    },
    series: [
      {
        type: "bar",
        data: distribution.map((d, i) => ({
          value: d.count,
          itemStyle: { color: barColors[i % barColors.length], borderRadius: [4, 4, 0, 0] },
        })),
        barCategoryGap: "12%",
        label: {
          show: true,
          position: "top",
          formatter: (p: { value: number }) => (p.value > 0 ? String(p.value) : ""),
          fontSize: 12,
          color: "#44556a",
        },
      },
    ],
  };
}
